# store/tests/test_views.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.tests.factories import UserFactory, setup_groups_and_permissions
from products.tests.factories import ProductFactory
from store.models import WarehouseModel, StoreModel, WasteModel
from .factories import (
    WarehouseFactory, StoreFactory, WasteFactory,
    ReturnsFactory, TransfersFactory
)


class WarehouseViewSetTest(APITestCase):
    """تست‌های ویوی انبار"""
    
    def setUp(self):
        self.client = APIClient()
        setup_groups_and_permissions()
        
        self.manager = UserFactory.create_manager(password='pass123')
        self.supervisor = UserFactory.create_supervisor(password='pass123')
        self.sales = UserFactory.create_sales(password='pass123')
        self.user = UserFactory.create_user(password='pass123')
        
        self.product = ProductFactory.create()
    # ✅ استفاده از get_or_create
        self.warehouse, _ = WarehouseModel.objects.get_or_create(
            product=self.product,
            defaults={'quantity': 10}
        )
        
        self.list_url = reverse('warehouse-list')
        self.detail_url = reverse('warehouse-detail', kwargs={'pk': self.warehouse.id})
    
    def test_list_warehouse_as_manager(self):
        """تست دریافت لیست انبار توسط مدیر"""
        self.client.force_authenticate(user=self.manager)
        # ✅ اصلاح: GET به جای POST
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_warehouse_as_sales(self):
        """تست دریافت لیست انبار توسط فروشنده"""
        self.client.force_authenticate(user=self.sales)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_warehouse_as_user(self):
        """تست دریافت لیست انبار توسط کاربر عادی (دسترسی ندارد)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_warehouse_as_manager(self):
        """تست ایجاد موجودی انبار توسط مدیر"""
        self.client.force_authenticate(user=self.manager)
        # ✅ برای ایجاد، یک محصول جدید بساز
        new_product = ProductFactory.create()
        data = {
            'product': f'http://testserver/api/products/{new_product.id}/',
            'quantity': 20
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_warehouse_as_sales(self):
        """تست ایجاد موجودی انبار توسط فروشنده (دسترسی ندارد)"""
        self.client.force_authenticate(user=self.sales)
        data = {
            'product': f'http://testserver/api/products/{self.product.id}/',
            'quantity': 20
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StoreViewSetTest(APITestCase):
    """تست‌های ویوی فروشگاه"""
    
    def setUp(self):
        self.client = APIClient()
        setup_groups_and_permissions()
        
        self.manager = UserFactory.create_manager(password='pass123')
        self.user = UserFactory.create_user(password='pass123')
        
        self.product = ProductFactory.create()
        self.store = StoreFactory.create(product=self.product, quantity=10)
        
        self.list_url = reverse('store-list')
    
    def test_list_store_as_user(self):
        """تست دریافت لیست فروشگاه توسط کاربر عادی"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_store_unauthenticated(self):
        """تست دریافت لیست فروشگاه بدون احراز هویت"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_store_not_allowed(self):
        """تست ایجاد موجودی فروشگاه (مجاز نیست)"""
        self.client.force_authenticate(user=self.manager)
        product_url = f'http://testserver/api/products/{self.product.id}/'
        data = {
            'product': product_url,
            'quantity': 20
        }
        response = self.client.post(self.list_url, data, format='json')
        # ✅ انتظار 403 به جای 405 (چون StorePermission اجازه create نمی‌دهد)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WasteViewSetTest(APITestCase):
    """تست‌های ویوی ضایعات"""
    
    def setUp(self):
        self.client = APIClient()
        setup_groups_and_permissions()
        
        self.manager = UserFactory.create_manager(password='pass123')
        self.supervisor = UserFactory.create_supervisor(password='pass123')
        self.sales = UserFactory.create_sales(password='pass123')
        
        self.product = ProductFactory.create()
        self.store, _ = StoreModel.objects.update_or_create(
            product=self.product,
            defaults={'quantity': 20}
        )
        
        self.list_url = reverse('waste-list')
    
    def test_create_waste_as_manager(self):
        """تست ایجاد ضایعات توسط مدیر"""
        self.client.force_authenticate(user=self.manager)
        
        # ✅ استفاده از URL
        product_url = f'http://testserver/api/products/{self.product.id}/'
        
        data = {
            'product': product_url,  # ✅ URL
            'quantity': 3,
            'description': 'تست ضایعات'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        if response.status_code == 400:
            print("Error:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_waste_as_sales(self):
        """تست ایجاد ضایعات توسط فروشنده (دسترسی ندارد)"""
        self.client.force_authenticate(user=self.sales)
        data = {
            'product': f'http://testserver/api/products/{self.product.id}/',
            'quantity': 3,
            'description': 'تست ضایعات'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)