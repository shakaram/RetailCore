# store/tests/test_serializers.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError
from accounts.tests.factories import UserFactory
from products.tests.factories import ProductFactory
from store.serializers import (
    WarehouseSerializer, StoreSerializer, WasteSerializer,
    ReturnsSerializer, TransfersSerializer, UpdatedInformationSerializer
)
from store.models import WarehouseModel, StoreModel, WasteModel
from .factories import (
    WarehouseFactory, StoreFactory, WasteFactory,
    ReturnsFactory, TransfersFactory, UpdatedInformationFactory
)
from products.models import ProductModel

class WarehouseSerializerTest(TestCase):
    """تست‌های سریالایزر انبار"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.product = ProductFactory.create()
        self.warehouse, _ = WarehouseModel.objects.update_or_create(
            product=self.product,
            defaults={'quantity': 10}
        )

    def test_serialize_warehouse(self):
        """تست سریالایز کردن انبار"""
        request = self.factory.get('/api/store/warehouse/')
        serializer = WarehouseSerializer(
            instance=self.warehouse,
            context={'request': request}
        )
        data = serializer.data
        
        self.assertEqual(data['quantity'], 10)
        self.assertEqual(data['product'], f'http://testserver/api/products/{self.product.id}/')
        self.assertTrue(data['is_available'])
    
    def test_deserialize_warehouse(self):
        """تست دیسریالایز کردن انبار"""
        request = self.factory.get('/api/store/warehouse/')
        
        data = {
            'quantity': 20
        }
        serializer = WarehouseSerializer(
            instance=self.warehouse,
            data=data,
            context={'request': request},
            partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        warehouse = serializer.save()
        
        self.assertEqual(warehouse.quantity, 20)


class StoreSerializerTest(TestCase):
    """تست‌های سریالایزر فروشگاه"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.product = ProductFactory.create()
        self.store, _ = StoreModel.objects.update_or_create(
            product=self.product,
            defaults={'quantity': 10}
        )
    
    def test_serialize_store(self):
        """تست سریالایز کردن فروشگاه"""
        request = self.factory.get('/api/store/')
        serializer = StoreSerializer(
            instance=self.store,
            context={'request': request}
        )
        data = serializer.data
        
        self.assertEqual(data['quantity'], 10)
        self.assertEqual(data['product'], f'http://testserver/api/products/{self.product.id}/')
        self.assertTrue(data['is_available'])


class WasteSerializerTest(TestCase):
    """تست‌های سریالایزر ضایعات"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory.create()
        self.product = ProductFactory.create()
        
        self.store, _ = StoreModel.objects.update_or_create(
            product=self.product,
            defaults={'quantity': 20, 'is_available': True}
        )
        self.waste = WasteFactory.create(product=self.product, user=self.user, quantity=5)
    
    def test_serialize_waste(self):
        """تست سریالایز کردن ضایعات"""
        request = self.factory.get('/api/store/waste/')
        request.user = self.user
        serializer = WasteSerializer(
            instance=self.waste,
            context={'request': request}
        )
        data = serializer.data
        
        self.assertEqual(data['quantity'], 5)
        self.assertEqual(data['product'], f'http://testserver/api/products/{self.product.id}/')
    
    def test_deserialize_waste(self):
        """تست دیسریالایز کردن ضایعات"""
        request = self.factory.get('/api/store/waste/')
        request.user = self.user
        
        new_product = ProductFactory.create()
        StoreModel.objects.create(product=new_product, quantity=20)
        
        # ✅ ارسال URL
        product_url = reverse('products-detail', kwargs={'pk': new_product.pk})
        
        data = {
            'product': product_url,
            'quantity': 3,
            'description': 'تست ضایعات'
        }
        serializer = WasteSerializer(
            data=data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        waste = serializer.save()
        
        self.assertEqual(waste.quantity, 3)
        self.assertEqual(waste.user.id, self.user.id)
        self.assertEqual(waste.product.id, new_product.id)



    def test_waste_validate_insufficient_stock(self):
        request = self.factory.get('/api/store/waste/')
        request.user = self.user
        
        new_product = ProductFactory.create()
        
        # ✅ پاک کردن همه موجودی‌های قبلی برای این محصول
        WarehouseModel.objects.filter(product=new_product).delete()
        StoreModel.objects.filter(product=new_product).delete()
        
        # ✅ فقط یک موجودی فروشگاه با مقدار ۵ ایجاد کن
        StoreModel.objects.create(product=new_product, quantity=5)
        
        product_url = reverse('products-detail', kwargs={'pk': new_product.pk})
        
        data = {
            'product': product_url,
            'quantity': 100,
            'description': 'تست'
        }
        
        serializer = WasteSerializer(data=data, context={'request': request})
        is_valid = serializer.is_valid()
        
        # ✅ حالا باید False باشه
        self.assertFalse(is_valid)
        self.assertIn('non_field_errors', serializer.errors)



class TransfersSerializerTest(TestCase):
    """تست‌های سریالایزر انتقالات"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory.create()
        self.product = ProductFactory.create()
        
        self.warehouse, _ = WarehouseModel.objects.update_or_create(
            product=self.product,
            defaults={'quantity': 20}
        )
        self.transfer = TransfersFactory.create(product=self.product, user=self.user, quantity=5)
    
    def test_serialize_transfers(self):
        """تست سریالایز کردن انتقال"""
        request = self.factory.get('/api/store/transfers/')
        request.user = self.user
        serializer = TransfersSerializer(
            instance=self.transfer,
            context={'request': request}
        )
        data = serializer.data
        
        self.assertEqual(data['quantity'], 5)
        self.assertEqual(data['product'], f'http://testserver/api/products/{self.product.id}/')
    
    def test_transfers_validate_insufficient_stock(self):
        """تست اعتبارسنجی موجودی ناکافی انبار"""
        request = self.factory.get('/api/store/transfers/')
        request.user = self.user
        
        data = {
            'product': f'http://testserver/api/products/{self.product.id}/',
            'quantity': 100
        }
        serializer = TransfersSerializer(
            data=data,
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)