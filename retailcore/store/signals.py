from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from crum import get_current_request, get_current_user
from .models import *
from django.db import transaction


def updated_information_local(instance, action_type):
    """ثبت لاگ با دریافت user از request"""
    from .models import UpdatedInformationModel

    request = get_current_request()
    user = request.user if request and hasattr(request, 'user') else None
    
    if user is None:
        user = get_current_user()
    
    # ✅ اگر user وجود نداشت، یک کاربر پیش‌فرض ایجاد کن (برای تست)
    if user is None:
        from accounts.models import User
        user, _ = User.objects.get_or_create(
            username='system',
            defaults={'password': '123456'}
        )
    
    # ✅ همیشه لاگ ایجاد کن (حتی اگر user None باشد)
    UpdatedInformationModel.objects.create(
        user=user,
        action_type=action_type,
        text=str(instance)
    )


@receiver(post_save, sender=WarehouseModel)
@transaction.atomic
def warehouse_create_update_signal(sender, instance, created, **kwargs):
    instance.product.update_inventory_fields()
    if created:
        updated_information_local(instance, 'CREATE')
    else:
        updated_information_local(instance, 'UPDATE')

@receiver(post_delete, sender=WarehouseModel)
@transaction.atomic
def warehouse_delete_signal(sender, instance, **kwargs):
    instance.product.update_inventory_fields()
    updated_information_local(instance, 'DELETE')

@receiver(post_save, sender=WasteModel)
@transaction.atomic
def waste_create_update_signal(sender, instance, created, **kwargs):
    if created:
        if instance.quantity <= 0:
            raise ValueError('تعداد ضایعات باید بیشتر از صفر باشد')
        
        store_inventory = StoreModel.objects.select_for_update().filter(product=instance.product).first()
        if store_inventory and store_inventory.quantity >= instance.quantity:
            store_inventory.quantity -= instance.quantity
            store_inventory.save(update_fields=['quantity'])
            updated_information_local(instance, 'WASTE')
        else:
            warehouse = WarehouseModel.objects.select_for_update().filter(product=instance.product).first()
            needed = instance.quantity - (store_inventory.quantity if store_inventory else 0)
            if warehouse and warehouse.quantity >= needed:
                if store_inventory and store_inventory.quantity > 0:
                    store_inventory.quantity = 0
                    store_inventory.save(update_fields=['quantity'])
                if warehouse.quantity >= needed:
                    warehouse.quantity -= needed
                    warehouse.save(update_fields=['quantity'])
                    updated_information_local(instance, 'WASTE')
                else:
                    raise ValueError(f'موجودی انبار کافی نیست. موجودی: {warehouse.quantity}')
            else:
                raise ValueError(f'موجودی کافی نیست. موجودی کل: {instance.product.quantity}')
        instance.product.update_inventory_fields()
    else:
        updated_information_local(instance, 'UPDATE')


@receiver(post_delete, sender=WasteModel)
@transaction.atomic
def waste_delete_signal(sender, instance, **kwargs):
    instance.product.update_inventory_fields()
    updated_information_local(instance, 'DELETE')

@receiver(post_save, sender=ReturnsModel)
@transaction.atomic
def returns_create_update_signal(sender, instance, created, **kwargs):
    if created:

        waste = WasteModel.objects.select_for_update().filter(product=instance.product).first()
        
        if not waste:
            raise ValueError('ضایعاتی برای این محصول ثبت نشده است')
        
        if waste.quantity < instance.quantity:
            raise ValueError(f'مقدار ضایعات کافی نیست. موجودی: {waste.quantity}')
        
        waste.quantity -= instance.quantity
        if waste.quantity == 0:
            waste.delete()
            updated_information_local(instance, 'DELETE')
        else:
            waste.save()
            updated_information_local(instance, 'RETURN')
            
        instance.product.update_inventory_fields()
    else:
        updated_information_local(instance, 'UPDATE')

@receiver(post_delete, sender=ReturnsModel)
@transaction.atomic
def returns_delete_signal(sender, instance, **kwargs):
    instance.product.update_inventory_fields()
    updated_information_local(instance, 'DELETE')

@receiver(post_save, sender=TransfersModel)
@transaction.atomic
def transfers_create_update_signal(sender, instance, created, **kwargs):
    if created:
        warehouse = WarehouseModel.objects.select_for_update().get(product=instance.product)
        store, _ = StoreModel.objects.get_or_create(
            product=instance.product,
            defaults={'quantity': 0})
        
        if instance.quantity > warehouse.quantity:
            raise ValueError(f'موجودی انبار کافی نیست. موجودی: {warehouse.quantity}')
        
        warehouse.quantity -= instance.quantity
        store.quantity += instance.quantity

        warehouse.save(update_fields=['quantity'])
        store.save(update_fields=['quantity'])

        instance.product.update_inventory_fields()
        updated_information_local(instance, 'TRANSFER') 

    else:
        updated_information_local(instance, 'UPDATE')

@receiver(post_delete, sender=TransfersModel)
@transaction.atomic
def transfers_delete_signal(sender, instance, **kwargs):
    warehouse = WarehouseModel.objects.select_for_update().filter(product=instance.product).first()
    store = StoreModel.objects.select_for_update().filter(product=instance.product).first()
    
    warehouse.quantity += instance.quantity
    store.quantity -= instance.quantity
    
    warehouse.save(update_fields=['quantity'])
    store.save(update_fields=['quantity'])
    
    instance.product.update_inventory_fields()
    updated_information_local(instance, 'DELETE')

@receiver(post_save, sender=StoreModel)
@transaction.atomic
def store_create_update_signal(sender, instance, created, **kwargs):
    instance.product.update_inventory_fields()
    
    if created:
        updated_information_local(instance, 'STORE')
    else:
        updated_information_local(instance, 'UPDATE')

@receiver(post_delete, sender=StoreModel)
@transaction.atomic
def store_delete_signal(sender, instance, **kwargs):
    
    instance.product.update_inventory_fields()
    updated_information_local(instance, 'DELETE')
