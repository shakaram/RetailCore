# store/tests/test_signals.py
from django.test import TestCase
from django.db import transaction
from django.db.utils import IntegrityError
from accounts.tests.factories import UserFactory
from products.tests.factories import ProductFactory
from store.models import (
    WarehouseModel, StoreModel, WasteModel, 
    ReturnsModel, TransfersModel, UpdatedInformationModel
)
from .factories import (
    WarehouseFactory, StoreFactory, WasteFactory,
    ReturnsFactory, TransfersFactory
)


class WarehouseSignalTest(TestCase):
    """تست‌های سیگنال‌های انبار"""
    
    def setUp(self):
        self.user = UserFactory.create()
        self.product = ProductFactory.create()
    
    def test_warehouse_create_updates_product_inventory(self):
        """تست ایجاد انبار -> بروزرسانی موجودی محصول"""
        product = ProductFactory.create()
        warehouse = WarehouseFactory.create(product=product, quantity=20)
        
        product.refresh_from_db()
        self.assertEqual(product.quantity, 20)
    
    def test_warehouse_update_updates_product_inventory(self):
        """تست بروزرسانی انبار -> بروزرسانی موجودی محصول"""
        product = ProductFactory.create()
        warehouse = WarehouseFactory.create(product=product, quantity=10)
        
        warehouse.quantity = 30
        warehouse.save()
        
        product.refresh_from_db()
        self.assertEqual(product.quantity, 30)
    
    def test_warehouse_delete_updates_product_inventory(self):
        """تست حذف انبار -> بروزرسانی موجودی محصول"""
        product = ProductFactory.create()
        warehouse = WarehouseFactory.create(product=product, quantity=15)
        
        warehouse.delete()
        
        product.refresh_from_db()
        self.assertEqual(product.quantity, 0)
    
    def test_warehouse_create_creates_log(self):
        """تست ایجاد انبار -> ایجاد لاگ"""
        product = ProductFactory.create()
        warehouse = WarehouseFactory.create(product=product, quantity=10)
        
        log = UpdatedInformationModel.objects.filter(
            action_type='CREATE'
        ).first()
        
        self.assertIsNotNone(log)
    
    def test_warehouse_update_creates_log(self):
        """تست بروزرسانی انبار -> ایجاد لاگ"""
        warehouse = WarehouseFactory.create(product=self.product, quantity=10)
        warehouse.quantity = 20
        warehouse.save()
        
        log = UpdatedInformationModel.objects.filter(
            action_type='UPDATE',
            text__icontains=str(warehouse)
        ).first()
        
        self.assertIsNotNone(log)
    
    def test_warehouse_delete_creates_log(self):
        """تست حذف انبار -> ایجاد لاگ"""
        warehouse = WarehouseFactory.create(product=self.product, quantity=10)
        warehouse.delete()
        
        log = UpdatedInformationModel.objects.filter(
            action_type='DELETE'
        ).first()
        
        self.assertIsNotNone(log)


class StoreSignalTest(TestCase):
    """تست‌های سیگنال‌های فروشگاه"""
    
    def setUp(self):
        self.user = UserFactory.create()
        self.product = ProductFactory.create()
    
    def test_store_create_updates_product_inventory(self):
        """تست ایجاد فروشگاه -> بروزرسانی موجودی محصول"""
        initial_quantity = self.product.quantity
        
        store = StoreFactory.create(product=self.product, quantity=20)
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity + 20)
    
    def test_store_update_updates_product_inventory(self):
        """تست بروزرسانی فروشگاه -> بروزرسانی موجودی محصول"""
        store = StoreFactory.create(product=self.product, quantity=10)
        initial_quantity = self.product.quantity
        
        store.quantity = 30
        store.save()
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity + 20)
    
    def test_store_delete_updates_product_inventory(self):
        """تست حذف فروشگاه -> بروزرسانی موجودی محصول"""
        store = StoreFactory.create(product=self.product, quantity=15)
        initial_quantity = self.product.quantity
        
        store.delete()
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity - 15)
    
    def test_store_create_creates_log(self):
        """تست ایجاد فروشگاه -> ایجاد لاگ"""
        store = StoreFactory.create(product=self.product, quantity=10)
        
        log = UpdatedInformationModel.objects.filter(
            action_type='STORE',
            text__icontains=str(store)
        ).first()
        
        self.assertIsNotNone(log)
    
    def test_store_update_creates_log(self):
        """تست بروزرسانی فروشگاه -> ایجاد لاگ"""
        store = StoreFactory.create(product=self.product, quantity=10)
        store.quantity = 20
        store.save()
        
        log = UpdatedInformationModel.objects.filter(
            action_type='UPDATE',
            text__icontains=str(store)
        ).first()
        
        self.assertIsNotNone(log)
    
    def test_store_delete_creates_log(self):
        """تست حذف فروشگاه -> ایجاد لاگ"""
        store = StoreFactory.create(product=self.product, quantity=10)
        store.delete()
        
        log = UpdatedInformationModel.objects.filter(
            action_type='DELETE'
        ).first()
        
        self.assertIsNotNone(log)


class WasteSignalTest(TestCase):
    """تست‌های سیگنال‌های ضایعات"""
    
    def setUp(self):
        self.user = UserFactory.create()
        self.product = ProductFactory.create()
        
        # ایجاد موجودی برای تست
        self.store = StoreFactory.create(product=self.product, quantity=20)
        self.warehouse = WarehouseFactory.create(product=self.product, quantity=10)
    
    def test_waste_create_decreases_store_first(self):
        """تست ایجاد ضایعات -> کاهش از فروشگاه (اولویت با فروشگاه)"""
        initial_store = self.store.quantity
        initial_warehouse = self.warehouse.quantity
        
        waste = WasteFactory.create(product=self.product, user=self.user, quantity=5)
        
        self.store.refresh_from_db()
        self.warehouse.refresh_from_db()
        
        self.assertEqual(self.store.quantity, initial_store - 5)
        self.assertEqual(self.warehouse.quantity, initial_warehouse)
    
    def test_waste_create_decreases_warehouse_when_store_insufficient(self):
        """تست ایجاد ضایعات -> کاهش از انبار وقتی فروشگاه کافی نیست"""
        self.store.quantity = 2
        self.store.save()
        
        # ✅ موجودی انبار 10
        initial_warehouse = self.warehouse.quantity
        
        # ✅ ایجاد ضایعات 5 عدد (2 تا از فروشگاه، 3 تا از انبار)
        waste = WasteFactory.create(product=self.product, user=self.user, quantity=5)
        
        self.store.refresh_from_db()
        self.warehouse.refresh_from_db()
        
        # ✅ فروشگاه باید 0 شود
        self.assertEqual(self.store.quantity, 0)
        # ✅ انبار باید 3 تا کم شود (10 - 3 = 7)
        self.assertEqual(self.warehouse.quantity, initial_warehouse - 3)
    
    def test_waste_create_insufficient_stock(self):
        """تست ایجاد ضایعات با موجودی ناکافی -> خطا"""
        self.store.quantity = 2
        self.store.save()
        self.warehouse.quantity = 1
        self.warehouse.save()
        
        with self.assertRaises(ValueError):
            WasteFactory.create(product=self.product, user=self.user, quantity=10)
    
    def test_waste_create_creates_log(self):
        """تست ایجاد ضایعات -> ایجاد لاگ"""
        waste = WasteFactory.create(product=self.product, user=self.user, quantity=3)
        
        log = UpdatedInformationModel.objects.filter(
            action_type='WASTE',
            text__icontains=str(waste)
        ).first()
        
        self.assertIsNotNone(log)
    
    def test_waste_update_creates_log(self):
        """تست بروزرسانی ضایعات -> ایجاد لاگ"""
        waste = WasteFactory.create(product=self.product, user=self.user, quantity=3)
        waste.quantity = 5
        waste.save()
        
        log = UpdatedInformationModel.objects.filter(
            action_type='UPDATE',
            text__icontains=str(waste)
        ).first()
        
        self.assertIsNotNone(log)
    
    def test_waste_delete_creates_log(self):
        """تست حذف ضایعات -> ایجاد لاگ"""
        waste = WasteFactory.create(product=self.product, user=self.user, quantity=3)
        waste.delete()
        
        log = UpdatedInformationModel.objects.filter(
            action_type='DELETE'
        ).first()
        
        self.assertIsNotNone(log)


class ReturnsSignalTest(TestCase):
    """تست‌های سیگنال‌های مرجوعی"""
    
    def setUp(self):
        self.user = UserFactory.create()
        self.product = ProductFactory.create()
        
        # ✅ ایجاد موجودی کافی برای ضایعات (مثلاً ۲۰ تا در فروشگاه)
        StoreModel.objects.create(product=self.product, quantity=20)
        
        self.waste, _ = WasteModel.objects.update_or_create(
            product=self.product,
            user=self.user,
            defaults={'quantity': 10}
        )
    
    def test_returns_create_decreases_waste(self):
        """تست ایجاد مرجوعی -> کاهش ضایعات"""
        initial_waste = self.waste.quantity
        
        returns = ReturnsFactory.create(product=self.product, user=self.user, quantity=3)
        
        self.waste.refresh_from_db()
        self.assertEqual(self.waste.quantity, initial_waste - 3)
    
    def test_returns_create_deletes_waste_when_zero(self):
        """تست ایجاد مرجوعی -> حذف ضایعات وقتی به صفر می‌رسد"""
        returns = ReturnsFactory.create(product=self.product, user=self.user, quantity=10)
        
        with self.assertRaises(WasteModel.DoesNotExist):
            self.waste.refresh_from_db()
    

    def test_returns_create_insufficient_waste(self):
        """تست ایجاد مرجوعی با ضایعات ناکافی -> خطا"""
        WasteModel.objects.filter(product=self.product, user=self.user).delete()
        
        # ایجاد ضایعات با موجودی ۳
        WasteModel.objects.create(
            product=self.product,
            user=self.user,
            quantity=3,
            description='تست ضایعات'
        )
        
        # تلاش برای ایجاد مرجوعی با مقدار ۱۰
        with self.assertRaises(ValueError) as context:
            ReturnsModel.objects.create(
                product=self.product,
                user=self.user,
                quantity=10
            )
        
        self.assertIn('مقدار ضایعات کافی نیست', str(context.exception))

    
    def test_returns_create_creates_log(self):
        """تست ایجاد مرجوعی -> ایجاد لاگ"""
        returns = ReturnsFactory.create(product=self.product, user=self.user, quantity=3)
        
        log = UpdatedInformationModel.objects.filter(
            action_type='RETURN'
        ).first()
        
        self.assertIsNotNone(log)
    
    def test_returns_delete_creates_log(self):
        """تست حذف مرجوعی -> ایجاد لاگ"""
        returns = ReturnsFactory.create(product=self.product, user=self.user, quantity=3)
        returns.delete()
        
        log = UpdatedInformationModel.objects.filter(
            action_type='DELETE'
        ).first()
        
        self.assertIsNotNone(log)


class TransfersSignalTest(TestCase):
    """تست‌های سیگنال‌های انتقالات"""
    
    def setUp(self):
        self.user = UserFactory.create()
        self.product = ProductFactory.create()
        
        self.warehouse = WarehouseFactory.create(product=self.product, quantity=20)
        self.store, _ = StoreModel.objects.get_or_create(
            product=self.product,
            defaults={'quantity': 0}
        )
    
    def test_transfers_create_decreases_warehouse_increases_store(self):
        """تست ایجاد انتقال -> کاهش انبار و افزایش فروشگاه"""
        initial_warehouse = self.warehouse.quantity
        initial_store = self.store.quantity
        
        transfer = TransfersFactory.create(product=self.product, user=self.user, quantity=5)
        
        self.warehouse.refresh_from_db()
        self.store.refresh_from_db()
        
        self.assertEqual(self.warehouse.quantity, initial_warehouse - 5)
        self.assertEqual(self.store.quantity, initial_store + 5)
    
    def test_transfers_create_insufficient_warehouse(self):
        """تست ایجاد انتقال با موجودی ناکافی انبار -> خطا"""
        with self.assertRaises(ValueError):
            TransfersFactory.create(product=self.product, user=self.user, quantity=100)
    
    def test_transfers_create_creates_log(self):
        """تست ایجاد انتقال -> ایجاد لاگ"""
        transfer = TransfersFactory.create(product=self.product, user=self.user, quantity=5)
        
        log = UpdatedInformationModel.objects.filter(
            action_type='TRANSFER',
            text__icontains=str(transfer)
        ).first()
        
        self.assertIsNotNone(log)
    
    def test_transfers_update_creates_log(self):
        """تست بروزرسانی انتقال -> ایجاد لاگ"""
        transfer = TransfersFactory.create(product=self.product, user=self.user, quantity=5)
        transfer.quantity = 10
        transfer.save()
        
        log = UpdatedInformationModel.objects.filter(
            action_type='UPDATE',
            text__icontains=str(transfer)
        ).first()
        
        self.assertIsNotNone(log)
    
    def test_transfers_delete_restores_inventory(self):
        """تست حذف انتقال -> بازگرداندن موجودی"""
        product = ProductFactory.create()
        warehouse = WarehouseFactory.create(product=product, quantity=20)
        store, _ = StoreModel.objects.get_or_create(
            product=product,
            defaults={'quantity': 10}
        )
        
        transfer = TransfersFactory.create(product=product, user=self.user, quantity=5)
        
        # بعد از انتقال: انبار 15، فروشگاه 15
        warehouse.refresh_from_db()
        store.refresh_from_db()
        
        initial_warehouse = warehouse.quantity  # 15
        initial_store = store.quantity          # 15
        
        transfer.delete()
        
        warehouse.refresh_from_db()
        store.refresh_from_db()
        
        # ✅ بررسی: انبار باید به 20 برگردد (15 + 5)
        self.assertEqual(warehouse.quantity, initial_warehouse + 5)  # 15 + 5 = 20
        self.assertEqual(store.quantity, initial_store - 5)
        
    def test_transfers_delete_creates_log(self):
        """تست حذف انتقال -> ایجاد لاگ"""
        transfer = TransfersFactory.create(product=self.product, user=self.user, quantity=5)
        transfer.delete()
        
        log = UpdatedInformationModel.objects.filter(
            action_type='DELETE'
        ).first()
        
        self.assertIsNotNone(log)

