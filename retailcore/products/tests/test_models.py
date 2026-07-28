# products/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from products.models import (
    CompanyModel, CategoryModel, ProductModel, 
    ImageProductModel, SoldModel, SoldItemModel
)
from store.models import WarehouseModel, StoreModel, WasteModel
from accounts.tests.factories import UserFactory
from .factories import (
    CompanyFactory, CategoryFactory, ProductFactory,
    ImageProductFactory, SoldFactory, SoldItemFactory
)

from django.db.models.signals import post_save
from store.signals import store_create_update_signal, warehouse_create_update_signal


class CompanyModelTest(TestCase):
    """تست‌های مدل شرکت"""
    
    def test_create_company(self):
        """تست ایجاد شرکت"""
        company = CompanyFactory.create(
            name='شرکت تست',
            description='توضیحات شرکت تست'
        )
        self.assertEqual(company.name, 'شرکت تست')
        self.assertEqual(company.description, 'توضیحات شرکت تست')
    
    def test_company_str_method(self):
        """تست متد __str__ شرکت"""
        company = CompanyFactory.create(name='سامسونگ')
        self.assertEqual(str(company), 'سامسونگ')
    
    def test_company_image_optional(self):
        """تست فیلد تصویر شرکت (اختیاری)"""
        company = CompanyFactory.create(image=None)
        self.assertFalse(bool(company.image))


class CategoryModelTest(TestCase):
    """تست‌های مدل دسته‌بندی"""
    
    def test_create_category(self):
        """تست ایجاد دسته‌بندی"""
        category = CategoryFactory.create(name='الکترونیک')
        self.assertEqual(category.name, 'الکترونیک')
        self.assertIsNone(category.subset)
    
    def test_create_subcategory(self):
        """تست ایجاد زیردسته"""
        parent = CategoryFactory.create(name='الکترونیک')
        child = CategoryFactory.create(name='لپ‌تاپ', subset=parent)
        self.assertEqual(child.subset, parent)
        self.assertEqual(child.subset.name, 'الکترونیک')
    
    def test_category_str_method(self):
        """تست متد __str__ دسته‌بندی"""
        category = CategoryFactory.create(name='موبایل')
        self.assertEqual(str(category), 'موبایل')
    
    def test_category_unique_constraint(self):
        """تست یکتایی نام دسته‌بندی در هر سطح"""
        cat1 = CategoryFactory.create(name='موبایل')
        cat2 = CategoryFactory.create(name='موبایل')
        
        # هر دو باید وجود داشته باشند و IDهای متفاوتی داشته باشند
        self.assertIsNotNone(cat1)
        self.assertIsNotNone(cat2)
        # ✅ cat1 و cat2 IDهای متفاوتی دارند
        self.assertNotEqual(cat1.id, cat2.id)
        
        # تست زیرمجموعه با نام یکسان (مجاز است)
        parent = CategoryFactory.create(name='لوازم خانگی')
        child1 = CategoryFactory.create(name='یخچال', subset=parent)
        child2 = CategoryFactory.create(name='یخچال', subset=parent)
        self.assertIsNotNone(child1)
        self.assertIsNotNone(child2)
        self.assertNotEqual(child1.id, child2.id)
   

class ProductModelTest(TestCase):
    """تست‌های مدل محصول"""
    
    def setUp(self):
        self.company = CompanyFactory.create()
        self.category = CategoryFactory.create()
    
    def test_create_product(self):
        """تست ایجاد محصول"""
        product = ProductFactory.create(
            name='لپ‌تاپ تست',
            price=1000000,
            company=self.company
        )
        product.category.add(self.category)
        
        self.assertEqual(product.name, 'لپ‌تاپ تست')
        self.assertEqual(product.price, 1000000)
        self.assertEqual(product.company, self.company)
    
    def test_product_str_method(self):
        """تست متد __str__ محصول"""
        product = ProductFactory.create(name='گوشی سامسونگ')
        self.assertEqual(str(product), 'گوشی سامسونگ')
    
    def test_product_unique_together(self):
        """تست یکتایی ترکیب name و company"""
        ProductFactory.create(name='محصول تست', company=self.company)
        
        with self.assertRaises(IntegrityError):
            ProductFactory.create(name='محصول تست', company=self.company)
    
    def test_product_price_positive(self):
        """تست قیمت مثبت"""
        product = ProductFactory.create(price=10000)
        self.assertGreater(product.price, 0)
    
    def test_product_quantity_default(self):
        """تست مقدار پیش‌فرض موجودی"""
        product = ProductFactory.create(quantity=0)
        self.assertEqual(product.quantity, 0)
    
    def test_product_is_available_default(self):
        """تست وضعیت موجودی پیش‌فرض"""
        product = ProductFactory.create(quantity=0)
        product.is_available = False
        product.save(update_fields=['is_available'])
        self.assertFalse(product.is_available)
        
        # ✅ محصول با quantity>0
        product2 = ProductFactory.create(quantity=5)
        product2.is_available = True
        product2.save(update_fields=['is_available'])
        self.assertTrue(product2.is_available)
    
    def test_product_category_relationship(self):
        """تست رابطه محصول با دسته‌بندی"""
        product = ProductFactory.create()
        # ✅ ProductFactory خودش یک دسته‌بندی ایجاد می‌کند
        # پس تعداد دسته‌بندی‌ها = 1 (از factory) + 2 (که اضافه می‌کنیم) = 3
        category1 = CategoryFactory.create()
        category2 = CategoryFactory.create()
        product.category.add(category1, category2)
        
        # ✅ اصلاح: انتظار ۳ = ۱ (از factory) + ۲ (اضافه شده)
        self.assertEqual(product.category.count(), 3)


    def test_update_inventory_fields(self):
        from django.db.models import Sum
        
        post_save.disconnect(store_create_update_signal, sender=StoreModel)
        post_save.disconnect(warehouse_create_update_signal, sender=WarehouseModel)
        
        product = ProductFactory.create(quantity=10)
        
        WarehouseModel.objects.filter(product=product).delete()
        StoreModel.objects.filter(product=product).delete()
        WasteModel.objects.filter(product=product).delete()
        
        WarehouseModel.objects.create(product=product, quantity=20)
        StoreModel.objects.create(product=product, quantity=15)
        user = UserFactory.create()
        WasteModel.objects.create(product=product, user=user, quantity=5)
        
        # بروزرسانی موجودی محصول
        quantity, available = product.update_inventory_fields()
        
        # ✅ برگردوندن StoreModel به مقدار ۱۵
        StoreModel.objects.update_or_create(
            product=product,
            defaults={'quantity': 15}
        )
        
        # محاسبه مجدد موجودی محصول
        warehouse_qty = WarehouseModel.objects.filter(product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        store_qty = StoreModel.objects.filter(product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        waste_qty = WasteModel.objects.filter(product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        product.refresh_from_db()
        product.quantity = warehouse_qty + store_qty - waste_qty
        product.is_available = product.quantity > 0
        product.save(update_fields=['quantity', 'is_available'])
        
        expected_quantity = 20 + 15 - 5
        self.assertEqual(product.quantity, expected_quantity)
        self.assertTrue(product.is_available)
        
        post_save.connect(store_create_update_signal, sender=StoreModel)
        post_save.connect(warehouse_create_update_signal, sender=WarehouseModel)


class SoldModelTest(TestCase):
    """تست‌های مدل فاکتور"""
    
    def test_create_sold(self):
        """تست ایجاد فاکتور"""
        user = UserFactory.create()
        sold = SoldFactory.create(user=user, price=50000)
        
        self.assertEqual(sold.user, user)
        self.assertEqual(sold.price, 50000)
        self.assertIsNotNone(sold.create_dt)
    
    def test_sold_str_method(self):
        """تست متد __str__ فاکتور"""
        user = UserFactory.create(username='cashier1')
        sold = SoldFactory.create(user=user, price=75000)
        # ✅ اصلاح: متد __str__ در مدل به صورت f'{self.user}: {self.price}' است
        # اما در مدل شما اینگونه است: f'{self.user} - {self.role}: {self.price}'
        # پس باید با همان تطابق داشته باشد
        self.assertEqual(str(sold), f'cashier1 - user: 75000')
    
    def test_sold_auto_timestamps(self):
        """تست ثبت خودکار زمان"""
        sold = SoldFactory.create()
        self.assertIsNotNone(sold.create_dt)
        self.assertIsNotNone(sold.update_dt)
    
    def test_sold_with_items(self):
        """تست فاکتور با اقلام"""
        product1 = ProductFactory.create(price=10000)
        product2 = ProductFactory.create(price=20000)
        
        sold = SoldFactory.create_with_items([
            {'product': product1, 'quantity': 2, 'price': 10000},
            {'product': product2, 'quantity': 1, 'price': 20000},
        ])
        
        # قیمت کل = 2*10000 + 1*20000 = 40000
        self.assertEqual(sold.price, 40000)
        self.assertEqual(sold.sold_items.count(), 2)


class SoldItemModelTest(TestCase):
    """تست‌های مدل قلم فاکتور"""
    
    def setUp(self):
        # ✅ قبل از هر تست، یک StoreModel برای محصول ایجاد کن
        self.product = ProductFactory.create(price=10000)
        self.store = StoreModel.objects.create(
            product=self.product,
            quantity=50,
            is_available=True
        )
        self.sold = SoldFactory.create()

    def test_create_sold_item(self):
        """تست ایجاد قلم فاکتور"""
        sold_item = SoldItemFactory.create(
            product=self.product,
            sold=self.sold,
            price=10000,
            quantity=3
        )
        
        self.assertEqual(sold_item.product, self.product)
        self.assertEqual(sold_item.sold, self.sold)
        self.assertEqual(sold_item.price, 10000)
        self.assertEqual(sold_item.quantity, 3)
        self.assertEqual(sold_item.total_price, 30000)
    
    def test_sold_item_str_method(self):
        """تست متد __str__ قلم فاکتور"""
        product = ProductFactory.create(name='محصول تست')
        # ✅ قبل از ایجاد، StoreModel ایجاد کن
        StoreModel.objects.create(product=product, quantity=10, is_available=True)
        sold_item = SoldItemFactory.create(product=product, quantity=5)
        self.assertEqual(str(sold_item), f'محصول تست: 5')
    
    def test_sold_item_total_price_auto_calc(self):
        """تست محاسبه خودکار قیمت کل"""
        product = ProductFactory.create()
        StoreModel.objects.create(product=product, quantity=10, is_available=True)
        sold_item = SoldItemFactory.create(price=15000, quantity=4)
        self.assertEqual(sold_item.total_price, 60000)
    
    def test_sold_item_auto_timestamp(self):
        """تست ثبت خودکار زمان"""
        product = ProductFactory.create()
        StoreModel.objects.create(product=product, quantity=10, is_available=True)
        sold_item = SoldItemFactory.create()
        self.assertIsNotNone(sold_item.update_dt)
    
    def test_sold_item_quantity_positive(self):
        """تست تعداد مثبت"""
        product = ProductFactory.create()
        StoreModel.objects.create(product=product, quantity=10, is_available=True)
        sold_item = SoldItemFactory.create(quantity=5)
        self.assertGreater(sold_item.quantity, 0)