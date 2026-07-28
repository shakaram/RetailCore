# products/tests/factories.py
from django.contrib.auth import get_user_model
from factory import django, Faker, SubFactory, post_generation
from factory.django import DjangoModelFactory
from accounts.tests.factories import UserFactory
from products.models import (
    CompanyModel, CategoryModel, ProductModel, 
    ImageProductModel, SoldModel, SoldItemModel
)

User = get_user_model()


class CompanyFactory(DjangoModelFactory):
    """کارخانه تولید شرکت"""
    
    class Meta:
        model = CompanyModel
        django_get_or_create = ('name',)
    
    name = Faker('company')
    description = Faker('text', max_nb_chars=200)
    image = None  # برای تست بدون تصویر


class CategoryFactory(DjangoModelFactory):
    """کارخانه تولید دسته‌بندی"""
    
    class Meta:
        model = CategoryModel
    
    name = Faker('word')
    subset = None  # دسته والد (اختیاری)
    
    @classmethod
    def create_with_subset(cls, **kwargs):
        """ایجاد دسته‌بندی با زیرمجموعه"""
        parent = cls.create()
        return cls.create(subset=parent, **kwargs)


class ProductFactory(DjangoModelFactory):
    """کارخانه تولید محصول"""
    
    class Meta:
        model = ProductModel
    
    name = Faker('word')
    description = Faker('text', max_nb_chars=300)
    price = Faker('random_int', min=1000, max=10000000)
    quantity = Faker('random_int', min=0, max=1000)
    company = SubFactory(CompanyFactory)
    is_available = True
    
    @post_generation
    def categories(self, create, extracted, **kwargs):
        """اضافه کردن دسته‌بندی‌ها به محصول"""
        if not create:
            return
        if extracted:
            for category in extracted:
                self.category.add(category)
        else:
            # اگر دسته‌بندی مشخص نشده، یک دسته جدید ایجاد کن
            category = CategoryFactory.create()
            self.category.add(category)
    
    @classmethod
    def create_with_company(cls, company=None, **kwargs):
        """ایجاد محصول با شرکت مشخص"""
        if not company:
            company = CompanyFactory.create()
        return cls.create(company=company, **kwargs)
    
    @classmethod
    def create_with_categories(cls, categories=None, **kwargs):
        """ایجاد محصول با دسته‌بندی‌های مشخص"""
        product = cls.create(**kwargs)
        if categories:
            for category in categories:
                product.category.add(category)
        return product


class ImageProductFactory(DjangoModelFactory):
    """کارخانه تولید تصویر محصول"""
    
    class Meta:
        model = ImageProductModel
    
    product = SubFactory(ProductFactory)
    image = None  # برای تست بدون تصویر


class SoldFactory(DjangoModelFactory):
    """کارخانه تولید فاکتور"""
    
    class Meta:
        model = SoldModel
    
    user = SubFactory(UserFactory)
    price = 0  # ابتدا صفر، بعداً محاسبه می‌شود
    description = Faker('text', max_nb_chars=100)
    
    @classmethod
    def create_with_items(cls, items_data=None, **kwargs):
        """ایجاد فاکتور با اقلام"""
        sold = cls.create(**kwargs)
        if items_data:
            total_price = 0
            for item_data in items_data:
                product = item_data.get('product')
                quantity = item_data.get('quantity', 1)
                price = item_data.get('price', product.price if product else 1000)
                sold_item = SoldItemFactory.create(
                    sold=sold,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                total_price += sold_item.total_price
            sold.price = total_price
            sold.save()
        return sold


class SoldItemFactory(DjangoModelFactory):
    """کارخانه تولید قلم فاکتور"""
    
    class Meta:
        model = SoldItemModel
    
    product = SubFactory(ProductFactory)
    sold = SubFactory(SoldFactory)
    price = Faker('random_int', min=1000, max=1000000)
    quantity = Faker('random_int', min=1, max=10)
    total_price = 0  # محاسبه خودکار در create
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """ایجاد با محاسبه خودکار total_price"""
        price = kwargs.get('price', 1000)
        quantity = kwargs.get('quantity', 1)
        kwargs['total_price'] = price * quantity
        
        # ✅ قبل از ایجاد SoldItem، اطمینان از وجود StoreModel
        product = kwargs.get('product')
        if product:
            from store.models import StoreModel
            store, created = StoreModel.objects.get_or_create(
                product=product,
                defaults={'quantity': 100, 'is_available': True}  # موجودی کافی برای تست
            )
            if not created and store.quantity < quantity:
                store.quantity = quantity + 10
                store.save()
        
        return super()._create(model_class, *args, **kwargs)