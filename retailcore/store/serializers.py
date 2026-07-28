from rest_framework import serializers
from .models import *
from products.models import ProductModel
class WarehouseSerializer(serializers.ModelSerializer):
    """
    سریالایزر موجودی انبار
    """
    product=serializers.HyperlinkedRelatedField(
        view_name='products-detail',queryset=ProductModel.objects.all(), help_text='محصول')
    class Meta:
        model=WarehouseModel
        fields='__all__'
        read_only_fields=['is_available']
        extra_kwargs = {
            'product': {'help_text': 'محصول در انبار'},
            'quantity': {'help_text': 'تعداد موجود در انبار'},
            'is_available': {
                'help_text': 'آیا موجود است؟ (محاسبه خودکار)',
                'read_only': True
            },
        }

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        
        if not product or not quantity:
            return data
        
        # ✅ فقط اعتبارسنجی موجودی
        # (برای Warehouse نیازی به بررسی موجودی نیست چون موجودی را خودش تعیین می‌کند)
        return data
    
    def create(self, validated_data):
        """ایجاد یا بروزرسانی موجودی انبار با استفاده از update_or_create"""
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        
        # ✅ استفاده از update_or_create برای جلوگیری از UniqueConstraint
        warehouse, created = WarehouseModel.objects.update_or_create(
            product=product,
            defaults={'quantity': quantity}
        )
        return warehouse
    
    def update(self, instance, validated_data):
        """بروزرسانی موجودی انبار"""
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance
    

# store/serializers.py

class WasteSerializer(serializers.ModelSerializer):
    """
    سریالایزر ضایعات محصولات
    """
    product = serializers.HyperlinkedRelatedField(
        view_name='products-detail',
        queryset=ProductModel.objects.all(),
        help_text='محصول ضایعاتی (فقط URL)'
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = WasteModel
        fields = '__all__'
        read_only_fields = ['update_dt', 'create_dt']
    

    def validate(self, data):
        product = data.get('product')
        quantity = int(data.get('quantity', 0))  # ✅ این خط رو اضافه کن
        
        if not product:
            raise serializers.ValidationError({
                'product': 'محصول باید مشخص شود'
            })
        
        warehouse = WarehouseModel.objects.filter(product=product).first()
        store = StoreModel.objects.filter(product=product).first()
        total = (warehouse.quantity if warehouse else 0) + (store.quantity if store else 0)
        
        if total < quantity:
            raise serializers.ValidationError({
                'non_field_errors': [
                    f"موجودی کافی نیست. موجودی کل: {total}, درخواستی: {quantity}"
                ]
            })
        
        return data


    def create(self, validated_data):
        product = validated_data.get('product')
        user = validated_data.get('user')
        quantity = validated_data.get('quantity')
        description = validated_data.get('description', '')
        
        if not user:
            raise serializers.ValidationError("کاربر مشخص نشده است")
        
        waste, created = WasteModel.objects.get_or_create(
            product=product,
            user=user,
            defaults={
                'quantity': quantity,
                'description': description
            }
        )
        
        if not created:
            waste.quantity += quantity
            if description:
                waste.description = (waste.description or '') + f"\n{description}"
            waste.save()
            
            UpdatedInformationModel.objects.create(
                user=user,
                action_type='WASTE',
                text=f"افزایش ضایعات {product.name} به مقدار {quantity} (مجموع: {waste.quantity})"
            )
        else:
            UpdatedInformationModel.objects.create(
                user=user,
                action_type='WASTE',
                text=f"ثبت ضایعات جدید برای {product.name} به مقدار {quantity}"
            )
        
        return waste


class ReturnsSerializer(serializers.ModelSerializer):
    """
    سریالایزر مرجوعی محصولات
    """
    product=serializers.HyperlinkedRelatedField(view_name='products-detail',read_only=True)
    user=serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model=ReturnsModel
        fields='__all__'
        read_only_fields=['user','update_dt','create_dt']
    
    def validate(self, data):
        """بررسی موجودی فروشگاه برای مرجوعی"""
        product = data.get('product')
        quantity = data.get('quantity')
        store = StoreModel.objects.filter(product=product).first()
        
        if not store or store.quantity < quantity:
            raise serializers.ValidationError(
                f"موجودی فروشگاه کافی نیست. موجودی: {store.quantity if store else 0}"
            )
        return data

class TransfersSerializer(serializers.ModelSerializer):
    """
    سریالایزر انتقال محصولات از انبار به فروشگاه
    """
    product=serializers.HyperlinkedRelatedField(
        view_name='products-detail',read_only=True)
    user=serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model=TransfersModel
        fields='__all__'
        read_only_fields=['user','update_dt','create_dt']
        extra_kwargs = {
            'product': {'help_text': 'محصول انتقالی'},
            'user': {'help_text': 'کاربر ثبت‌کننده (خودکار)'},
            'quantity': {'help_text': 'تعداد انتقالی'},
            'update_dt': {'help_text': 'تاریخ آخرین ویرایش', 'read_only': True},
            'create_dt': {'help_text': 'تاریخ ثبت', 'read_only': True},
        }
    
    def validate(self, data):
        """بررسی موجودی کافی در انبار"""
        product = data.get('product')
        quantity = data.get('quantity')
        warehouse = WarehouseModel.objects.filter(product=product).first()
        
        if not warehouse or warehouse.quantity < quantity:
            raise serializers.ValidationError(
                f"موجودی انبار کافی نیست. موجودی: {warehouse.quantity if warehouse else 0}"
            )
        return data

class StoreSerializer(serializers.ModelSerializer):
    """
    سریالایزر موجودی فروشگاه
    """
    product=serializers.HyperlinkedRelatedField(
        view_name='products-detail',read_only=True,)
    class Meta:
        model=StoreModel
        fields='__all__'
        read_only_fields=['product','update_dt','create_dt','is_available']
        extra_kwargs = {
            'product': {'help_text': 'محصول در فروشگاه'},
            'quantity': {'help_text': 'تعداد موجود در فروشگاه'},
            'is_available': {
                'help_text': 'آیا موجود است؟ (محاسبه خودکار)',
                'read_only': True
            },
            'update_dt': {'help_text': 'تاریخ آخرین ویرایش', 'read_only': True},
            'create_dt': {'help_text': 'تاریخ ایجاد', 'read_only': True},
        }

class UpdatedInformationSerializer(serializers.ModelSerializer):
    """
    سریالایزر تاریخچه تغییرات
    """

    user=serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model=UpdatedInformationModel
        fields='__all__'
        read_only_fields=['user','create_dt']
        extra_kwargs = {
            'user': {'help_text': 'کاربر انجام‌دهنده تغییر (خودکار)'},
            'action_type': {
                'help_text': 'نوع عملیات (CREATE, UPDATE, DELETE, SOLD, WASTE, RETURN, TRANSFER)'
            },
            'text': {'help_text': 'شرح تغییرات'},
            'create_dt': {'help_text': 'تاریخ و زمان تغییر', 'read_only': True},
        }
