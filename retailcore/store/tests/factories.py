# store/tests/factories.py
from factory import django, Faker, SubFactory
from factory.django import DjangoModelFactory
from accounts.tests.factories import UserFactory
from products.tests.factories import ProductFactory
from store.models import (
    WarehouseModel, WasteModel, ReturnsModel, 
    TransfersModel, StoreModel, UpdatedInformationModel
)


class WarehouseFactory(DjangoModelFactory):
    """کارخانه تولید موجودی انبار"""
    
    class Meta:
        model = WarehouseModel
    
    product = SubFactory(ProductFactory)
    quantity = Faker('random_int', min=0, max=1000)
    is_available = True
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """ایجاد با استفاده از update_or_create برای به‌روزرسانی quantity"""
        product = kwargs.get('product')
        quantity = kwargs.get('quantity', 0)
        
        # ✅ استفاده از update_or_create
        warehouse, created = WarehouseModel.objects.update_or_create(
            product=product,
            defaults={
                'quantity': quantity,
                'is_available': quantity > 0
            }
        )
        return warehouse


class StoreFactory(DjangoModelFactory):
    """کارخانه تولید موجودی فروشگاه"""
    
    class Meta:
        model = StoreModel
    
    product = SubFactory(ProductFactory)
    quantity = Faker('random_int', min=0, max=1000)
    is_available = True
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """ایجاد با استفاده از update_or_create"""
        product = kwargs.get('product')
        quantity = kwargs.get('quantity', 0)
        
        store, created = StoreModel.objects.update_or_create(
            product=product,
            defaults={
                'quantity': quantity,
                'is_available': quantity > 0
            }
        )
        return store


class WasteFactory(DjangoModelFactory):
    """کارخانه تولید ضایعات"""
    
    class Meta:
        model = WasteModel
    
    product = SubFactory(ProductFactory)
    user = SubFactory(UserFactory)
    quantity = Faker('random_int', min=1, max=50)
    description = Faker('text', max_nb_chars=100)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """ایجاد با بررسی quantity مثبت"""
        quantity = kwargs.get('quantity', 1)
        # ✅ اگر quantity کمتر از 1 بود، به 1 تغییر بده
        if quantity < 1:
            quantity = 1
            kwargs['quantity'] = quantity
        return super()._create(model_class, *args, **kwargs)


class ReturnsFactory(DjangoModelFactory):
    """کارخانه تولید مرجوعی"""
    
    class Meta:
        model = ReturnsModel
    
    product = SubFactory(ProductFactory)
    user = SubFactory(UserFactory)
    quantity = Faker('random_int', min=1, max=10)
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """ایجاد مرجوعی با بررسی وجود ضایعات"""
        product = kwargs.get('product')
        user = kwargs.get('user')
        quantity = kwargs.get('quantity', 1)
        
        # ✅ بررسی وجود ضایعات برای محصول
        waste = WasteModel.objects.filter(product=product).first()
        if not waste:
            # اگر ضایعات وجود نداشت، ابتدا ضایعات ایجاد کن
            waste = WasteModel.objects.create(
                product=product,
                user=user,
                quantity=quantity + 5  # موجودی کافی برای مرجوعی
            )
        
        # ✅ اگر موجودی ضایعات کافی نیست، افزایش بده
        if waste.quantity < quantity:
            waste.quantity = quantity + 5
            waste.save()
        
        return super()._create(model_class, *args, **kwargs)


class TransfersFactory(DjangoModelFactory):
    """کارخانه تولید انتقالات"""
    
    class Meta:
        model = TransfersModel
    
    product = SubFactory(ProductFactory)
    user = SubFactory(UserFactory)
    quantity = Faker('random_int', min=1, max=50)


class UpdatedInformationFactory(DjangoModelFactory):
    """کارخانه تولید تاریخچه تغییرات"""
    
    class Meta:
        model = UpdatedInformationModel
    
    user = SubFactory(UserFactory)
    action_type = 'CREATE'
    text = Faker('text', max_nb_chars=200)