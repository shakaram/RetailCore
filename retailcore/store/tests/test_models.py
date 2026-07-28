# store/tests/test_models.py
from django.test import TestCase
from django.db import IntegrityError
from accounts.tests.factories import UserFactory
from products.tests.factories import ProductFactory
from store.models import (
    WarehouseModel, WasteModel, ReturnsModel, 
    TransfersModel, StoreModel, UpdatedInformationModel
)
from .factories import (
    WarehouseFactory, StoreFactory, WasteFactory,
    ReturnsFactory, TransfersFactory, UpdatedInformationFactory
)


class WarehouseModelTest(TestCase):
    """تست‌های مدل انبار"""
    
    def test_create_warehouse(self):
        """تست ایجاد موجودی انبار"""
        product = ProductFactory.create()
        warehouse = WarehouseFactory.create(product=product, quantity=10)
        
        self.assertEqual(warehouse.product, product)
        self.assertEqual(warehouse.quantity, 10)
        self.assertTrue(warehouse.is_available)
    
    def test_warehouse_is_available_auto_calc(self):
        """تست محاسبه خودکار وضعیت موجودی"""
        product = ProductFactory.create()
        
        # موجودی صفر
        warehouse = WarehouseFactory.create(product=product, quantity=0)
        self.assertFalse(warehouse.is_available)
        
        # موجودی مثبت
        warehouse = WarehouseFactory.create(product=product, quantity=5)
        self.assertTrue(warehouse.is_available)
    
    def test_warehouse_unique_product(self):
        """تست یکتایی محصول در انبار"""
        product = ProductFactory.create()
        # ✅ با get_or_create اولین رکورد را ایجاد کن
        WarehouseModel.objects.get_or_create(product=product, defaults={'quantity': 10})
        
        # ✅ دومین تلاش برای ایجاد باید خطا بدهد (اگر constraint وجود داشته باشد)
        # اما چون از get_or_create استفاده می‌کنیم، خطا نمی‌دهد
        # پس این تست را به روش دیگر انجام می‌دهیم
        with self.assertRaises(IntegrityError):
            WarehouseModel.objects.create(product=product, quantity=20)
    
    def test_warehouse_str_method(self):
        """تست متد __str__"""
        product = ProductFactory.create(name='محصول تست')
        warehouse = WarehouseFactory.create(product=product, quantity=10)
        self.assertEqual(str(warehouse), 'محصول تست - 10')


class StoreModelTest(TestCase):
    """تست‌های مدل فروشگاه"""
    
    def test_create_store(self):
        """تست ایجاد موجودی فروشگاه"""
        product = ProductFactory.create()
        store = StoreFactory.create(product=product, quantity=10)
        
        self.assertEqual(store.product, product)
        self.assertEqual(store.quantity, 10)
        self.assertTrue(store.is_available)
    
    def test_store_is_available_auto_calc(self):
        """تست محاسبه خودکار وضعیت موجودی"""
        product = ProductFactory.create()
        
        store = StoreFactory.create(product=product, quantity=0)
        self.assertFalse(store.is_available)
        
        store = StoreFactory.create(product=product, quantity=5)
        self.assertTrue(store.is_available)
    
    def test_store_unique_product(self):
        """تست یکتایی محصول در فروشگاه"""
        product = ProductFactory.create()
        StoreModel.objects.get_or_create(product=product, defaults={'quantity': 10})
        
        with self.assertRaises(IntegrityError):
            StoreModel.objects.create(product=product, quantity=20)
    
    def test_store_str_method(self):
        """تست متد __str__"""
        product = ProductFactory.create(name='محصول تست')
        store = StoreFactory.create(product=product, quantity=10)
        self.assertEqual(str(store), 'محصول تست - 10')
    
    def test_store_auto_timestamps(self):
        """تست ثبت خودکار زمان"""
        store = StoreFactory.create()
        self.assertIsNotNone(store.create_dt)
        self.assertIsNotNone(store.update_dt)


class WasteModelTest(TestCase):
    """تست‌های مدل ضایعات"""
    
    def test_create_waste(self):
        """تست ایجاد ضایعات"""
        product = ProductFactory.create()
        user = UserFactory.create()
        waste = WasteFactory.create(product=product, user=user, quantity=5)
        
        self.assertEqual(waste.product, product)
        self.assertEqual(waste.user, user)
        self.assertEqual(waste.quantity, 5)
    
    def test_waste_auto_timestamps(self):
        """تست ثبت خودکار زمان"""
        waste = WasteFactory.create()
        self.assertIsNotNone(waste.create_dt)
        self.assertIsNotNone(waste.update_dt)
    
    def test_waste_str_method(self):
        """تست متد __str__"""
        product = ProductFactory.create(name='محصول تست')
        user = UserFactory.create(username='testuser')
        waste = WasteFactory.create(product=product, user=user, quantity=3)
        self.assertEqual(str(waste), 'محصول تست - 3 - testuser')
    
    def test_waste_unique_product(self):
        """تست یکتایی محصول در ضایعات"""
        product = ProductFactory.create()
        user = UserFactory.create()
        WasteFactory.create(product=product, user=user)
        
        with self.assertRaises(IntegrityError):
            WasteFactory.create(product=product, user=user)


class ReturnsModelTest(TestCase):
    """تست‌های مدل مرجوعی"""
    def setUp(self):
        self.user = UserFactory.create()
        self.product = ProductFactory.create()

        StoreModel.objects.create(product=self.product, quantity=20)

        self.waste, _ = WasteModel.objects.get_or_create(
            product=self.product,
            user=self.user,
            defaults={'quantity': 10}
        )


    def test_returns_auto_timestamps(self):
        """تست ثبت خودکار زمان"""
        returns = ReturnsFactory.create()
        self.assertIsNotNone(returns.create_dt)
        self.assertIsNotNone(returns.update_dt)
    
    def test_returns_str_method(self):
        """تست متد __str__"""
        product = ProductFactory.create(name='محصول تست')
        # ✅ ایجاد ضایعات با get_or_create
        WasteModel.objects.get_or_create(
            product=product,
            user=self.user,
            defaults={'quantity': 10}
        )
        returns = ReturnsFactory.create(product=product, user=self.user, quantity=3)
        self.assertIn('محصول تست', str(returns))



class TransfersModelTest(TestCase):
    """تست‌های مدل انتقالات"""
    
    def test_create_transfers(self):
        """تست ایجاد انتقال"""
        product = ProductFactory.create()
        user = UserFactory.create()
        transfer = TransfersFactory.create(product=product, user=user, quantity=5)
        
        self.assertEqual(transfer.product, product)
        self.assertEqual(transfer.user, user)
        self.assertEqual(transfer.quantity, 5)
    
    def test_transfers_auto_timestamps(self):
        """تست ثبت خودکار زمان"""
        transfer = TransfersFactory.create()
        self.assertIsNotNone(transfer.create_dt)
        self.assertIsNotNone(transfer.update_dt)
    
    def test_transfers_str_method(self):
        """تست متد __str__"""
        product = ProductFactory.create(name='محصول تست')
        transfer = TransfersFactory.create(product=product)
        self.assertEqual(str(transfer), 'محصول تست')


class UpdatedInformationModelTest(TestCase):
    """تست‌های مدل تاریخچه تغییرات"""
    
    def test_create_updated_information(self):
        """تست ایجاد تاریخچه"""
        user = UserFactory.create()
        info = UpdatedInformationFactory.create(
            user=user,
            action_type='CREATE',
            text='تست ایجاد'
        )
        
        self.assertEqual(info.user, user)
        self.assertEqual(info.action_type, 'CREATE')
        self.assertEqual(info.text, 'تست ایجاد')
    
    def test_updated_information_str_method(self):
        """تست متد __str__"""
        user = UserFactory.create(username='testuser')
        info = UpdatedInformationFactory.create(
            user=user,
            action_type='UPDATE'
        )
        self.assertIn('testuser', str(info))
        self.assertIn('UPDATE', str(info))
    
    def test_updated_information_action_choices(self):
        """تست انتخاب‌های نوع عملیات"""
        valid_actions = ['CREATE', 'UPDATE', 'DELETE', 'TRANSFER', 'SOLD', 'WASTE', 'RETURN']
        
        for action in valid_actions:
            info = UpdatedInformationFactory.create(action_type=action)
            self.assertEqual(info.action_type, action)