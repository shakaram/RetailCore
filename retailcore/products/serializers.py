from rest_framework import serializers

from store.models import StoreModel
from . import models

class CompanySerializer(serializers.ModelSerializer):
    """
    سریالایزر شرکت‌های تولیدکننده
    """
    products=serializers.HyperlinkedRelatedField(view_name='products-detail',many=True,
                                 read_only=True,help_text='لیست محصولات این شرکت')
    class Meta:
        model=models.CompanyModel
        fields='__all__'
        extra_kwargs = {
            'name': {'help_text': 'نام شرکت (حداکثر ۵۰ کاراکتر)'},
            'description': {'help_text': 'توضیحات شرکت'},
            'image': {'help_text': 'لوگوی شرکت'},
        }

class CategorySerializer(serializers.ModelSerializer):
    """
    سریالایزر دسته‌بندی محصولات (سلسله‌مراتبی)
    """
    products=serializers.HyperlinkedRelatedField(view_name='products-detail',many=True,
                            read_only=True,help_text='لیست محصولات این دسته')
    subset = serializers.PrimaryKeyRelatedField(read_only=False,queryset=models.CategoryModel.objects.all(),
        allow_null=True,required=False,help_text='دسته والد (برای ایجاد زیردسته)')
    class Meta:
        model=models.CategoryModel
        fields='__all__'
        extra_kwargs = {
            'name': {'help_text': 'نام دسته‌بندی'},
            'subset': {'help_text': 'زیرمجموعه (دسته والد)'},
            }

class ProductSerializer(serializers.ModelSerializer):
    """
    سریالایزر اصلی محصولات با تمام جزئیات
    """
    images=serializers.HyperlinkedRelatedField(
        view_name='images-detail',many=True,
        read_only=True,help_text='لیست تصاویر محصول')
    company=serializers.HyperlinkedRelatedField(
        view_name='company-detail',queryset=models.CompanyModel.objects.all(),
        help_text='شرکت تولیدکننده')
    category=serializers.HyperlinkedRelatedField(
        view_name='category-detail',many=True,
        queryset=models.CategoryModel.objects.all(),
        help_text='دسته‌بندی‌های محصول (چندتایی)')
    class Meta:
        model=models.ProductModel
        fields='__all__'
        read_only_fields=['create_dt','quantity','is_available']
        extra_kwargs = {
            'name': {
                'help_text': 'نام محصول (حداکثر ۵۰ کاراکتر، یکتا با شرکت)',
                'max_length': 50
            },
            'description': {'help_text': 'توضیحات کامل محصول'},
            'price': {
                'help_text': 'قیمت محصول به تومان (عدد صحیح)',
                'min_value': 0
            },
            'quantity': {
                'help_text': 'موجودی کل (محاسبه خودکار از انبار + فروشگاه - ضایعات)',
                'read_only': True
            },
            'category': {'help_text': 'دسته‌بندی‌های محصول (حداقل یک دسته)'},
            'company': {'help_text': 'شرکت تولیدکننده محصول'},
            'create_dt': {'help_text': 'تاریخ و زمان ایجاد محصول', 'read_only': True},
            'is_available': {
                'help_text': 'آیا محصول موجود است؟ (محاسبه خودکار)',
                'read_only': True
            },
        }

class ImageProductSerializer(serializers.ModelSerializer):
    """
    سریالایزر تصاویر محصولات
    """
    product=serializers.HyperlinkedRelatedField(view_name='products-detail',
                                                queryset=models.ProductModel.objects.all(),
                                                help_text='محصول مربوطه')
    class Meta:
        model=models.ImageProductModel
        fields='__all__'
        extra_kwargs = {
            'image': {'help_text': 'فایل تصویر (jpg, png, etc.)'},
        }

class SoldSerializer(serializers.ModelSerializer):
    """
    سریالایزر فاکتورهای فروش
    """
    user=serializers.HiddenField(default=serializers.CurrentUserDefault())
    sold_items=serializers.HyperlinkedRelatedField(
        view_name='sold_item-detail',many=True,
        read_only=True,help_text='اقلام این فاکتور')
    class Meta:
        model = models.SoldModel
        fields = '__all__'
        read_only_fields = ['user','update_dt','create_dt']
        extra_kwargs = {
            'user': {'help_text': 'کاربر ثبت‌کننده (فروشنده)'},
            'price': {'help_text': 'قیمت کل فاکتور (محاسبه خودکار)'},
            'description': {'help_text': 'توضیحات اضافی برای فاکتور'},
            'update_dt': {'help_text': 'تاریخ آخرین ویرایش', 'read_only': True},
            'create_dt': {'help_text': 'تاریخ ایجاد فاکتور', 'read_only': True},
        }

class SoldItemSerializer(serializers.ModelSerializer):
    """
    سریالایزر اقلام هر فاکتور
    """
    product=serializers.HyperlinkedRelatedField(
        view_name='products-detail', queryset=models.ProductModel.objects.all(),
          help_text='محصول فروخته شده')
    sold=serializers.HyperlinkedRelatedField(
        view_name='sold-detail',queryset=models.SoldModel.objects.all(), help_text='فاکتور مربوطه')
    class Meta:
        model=models.SoldItemModel
        fields='__all__'
        read_only_fields = ['total_price','update_dt']
        extra_kwargs = {
            'product': {'help_text': 'محصول فروخته شده'},
            'sold': {'help_text': 'فاکتور مربوطه'},
            'price': {
                'help_text': 'قیمت واحد در لحظه فروش',
                'min_value': 0
            },
            'total_price': {
                'help_text': 'قیمت کل = قیمت واحد × تعداد (محاسبه خودکار)',
                'read_only': True
            },
            'quantity': {
                'help_text': 'تعداد خریداری شده (حداقل ۱)',
                'min_value': 1
            },
            'update_dt': {'help_text': 'تاریخ آخرین ویرایش', 'read_only': True},
        }
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("تعداد باید حداقل ۱ باشد")
        return value
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("قیمت نمی‌تواند منفی باشد")
        return value
    def validate(self, data):
        product = data['product']
        quantity = data['quantity']
        store = StoreModel.objects.filter(product=product).first()
        if not store or store.quantity < quantity:
            raise serializers.ValidationError("موجودی کافی نیست")
        return data

    def create(self, validated_data):
        validated_data['total_price'] = validated_data['price'] * validated_data['quantity']
        return super().create(validated_data)
