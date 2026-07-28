# products/tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.tests.factories import UserFactory, setup_groups_and_permissions
from store.models import StoreModel, WarehouseModel
from .factories import (
    CompanyFactory, CategoryFactory, ProductFactory,
    ImageProductFactory, SoldFactory, SoldItemFactory
)


class ProductViewSetTest(APITestCase):
    """تست‌های ویوی محصولات"""
    
    def setUp(self):
        self.client = APIClient()
        setup_groups_and_permissions()
        
        self.manager = UserFactory.create_manager(password='pass123')
        self.supervisor = UserFactory.create_supervisor(password='pass123')
        self.user = UserFactory.create_user(password='pass123')
        
        self.company = CompanyFactory.create()
        self.category = CategoryFactory.create()
        
        # ✅ ایجاد محصول در setUp
        self.product = ProductFactory.create(
            name='محصول اولیه',
            price=100000,
            company=self.company
        )
        self.product.category.add(self.category)
        
        self.list_url = reverse('products-list')
        self.detail_url = reverse('products-detail', kwargs={'pk': self.product.id})
    
    def test_list_products_unauthenticated(self):
        """تست دریافت لیست محصولات بدون احراز هویت"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_products_authenticated(self):
        """تست دریافت لیست محصولات با احراز هویت"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_product_as_manager(self):
        """تست ایجاد محصول توسط مدیر"""
        self.client.force_authenticate(user=self.manager)
        
        # ✅ داده‌های کامل برای ایجاد محصول
        data = {
            'name': 'محصول جدید',
            'description': 'توضیحات محصول جدید',
            'price': 150000,
            'company': f'http://testserver/api/company/{self.company.id}/',  # ✅ URL
            'category': [f'http://testserver/api/category/{self.category.id}/']  # ✅ URL
        }
        response = self.client.post(self.list_url, data, format='json')
        
        # ✅ اگر 400 گرفت، خطا را نشان بده
        if response.status_code == 400:
            print("Error:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'محصول جدید')
    
    def test_create_product_as_supervisor(self):
        """تست ایجاد محصول توسط سوپروایزر"""
        self.client.force_authenticate(user=self.supervisor)
        
        data = {
            'name': 'محصول سوپروایزر',
            'description': 'توضیحات',
            'price': 200000,
            'company': f'http://testserver/api/company/{self.company.id}/',
            'category': [f'http://testserver/api/category/{self.category.id}/']
        }
        response = self.client.post(self.list_url, data, format='json')
        
        if response.status_code == 400:
            print("Error:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_product_as_normal_user(self):
        """تست ایجاد محصول توسط کاربر عادی (دسترسی ندارد)"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'محصول غیرمجاز',
            'description': 'توضیحات',
            'price': 100000,
            'company': self.company.id,
            'category': [self.category.id]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_product(self):
        """تست دریافت اطلاعات محصول"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)
    
    def test_update_product_as_manager(self):
        """تست بروزرسانی محصول توسط مدیر"""
        self.client.force_authenticate(user=self.manager)
        
        data = {
            'name': 'محصول بروزرسانی شده',
            'description': 'توضیحات جدید',
            'price': 300000,
            'company': f'http://testserver/api/company/{self.company.id}/',
            'category': [f'http://testserver/api/category/{self.category.id}/']
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        if response.status_code == 400:
            print("Error:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'محصول بروزرسانی شده')
    
    def test_delete_product_as_manager(self):
        """تست حذف محصول توسط مدیر"""
        self.client.force_authenticate(user=self.manager)
        
        # ✅ ابتدا یک محصول جدید برای حذف ایجاد می‌کنیم
        new_product = ProductFactory.create(
            name='محصول برای حذف',
            price=50000,
            company=self.company
        )
        new_product.category.add(self.category)
        
        delete_url = reverse('products-detail', kwargs={'pk': new_product.id})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    
    def test_filter_products_by_price(self):
        """تست فیلتر محصولات بر اساس قیمت"""
        ProductFactory.create(price=50000)
        ProductFactory.create(price=200000)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'price_min': 100000, 'price_max': 250000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for product in response.data['results']:
            self.assertGreaterEqual(product['price'], 100000)
            self.assertLessEqual(product['price'], 250000)
    
    def test_search_products(self):
        """تست جستجو در محصولات"""
        ProductFactory.create(name='لپ‌تاپ ایسوس')
        ProductFactory.create(name='گوشی سامسونگ')
        
        response = self.client.get(self.list_url, {'search': 'لپ‌تاپ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for product in response.data['results']:
            self.assertIn('لپ‌تاپ', product['name'])


class CompanyViewSetTest(APITestCase):
    """تست‌های ویوی شرکت‌ها"""
    
    def setUp(self):
        self.client = APIClient()
        setup_groups_and_permissions()
        
        self.manager = UserFactory.create_manager(password='pass123')
        self.user = UserFactory.create_user(password='pass123')
        self.company = CompanyFactory.create()
        
        self.list_url = reverse('company-list')
        self.detail_url = reverse('company-detail', kwargs={'pk': self.company.id})
    
    def test_list_companies(self):
        """تست دریافت لیست شرکت‌ها"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_company_as_manager(self):
        """تست ایجاد شرکت توسط مدیر"""
        self.client.force_authenticate(user=self.manager)
        data = {
            'name': 'شرکت جدید',
            'description': 'توضیحات شرکت جدید'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_company_as_normal_user(self):
        """تست ایجاد شرکت توسط کاربر عادی (دسترسی ندارد)"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'شرکت غیرمجاز',
            'description': 'توضیحات'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SoldViewSetTest(APITestCase):
    """تست‌های ویوی فاکتورها"""
    
    def setUp(self):
        self.client = APIClient()
        setup_groups_and_permissions()
        
        self.manager = UserFactory.create_manager(password='pass123')
        self.cashier = UserFactory.create_cashier(password='pass123')
        self.supervisor = UserFactory.create_supervisor(password='pass123')
        self.user = UserFactory.create_user(password='pass123')
        
        self.product = ProductFactory.create(quantity=10)
        self.sold = SoldFactory.create(user=self.cashier, price=100000)
        
        self.list_url = reverse('sold-list')
        self.detail_url = reverse('sold-detail', kwargs={'pk': self.sold.id})
    
    def test_list_solds_as_cashier(self):
        """تست دریافت لیست فاکتورها توسط صندوقدار"""
        self.client.force_authenticate(user=self.cashier)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_solds_as_user(self):
        """تست دریافت لیست فاکتورها توسط کاربر عادی (دسترسی ندارد)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_sold_as_cashier(self):
        """تست ایجاد فاکتور توسط صندوقدار"""
        self.client.force_authenticate(user=self.cashier)
        data = {
            'description': 'فاکتور تست',
            'price': 0
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], 'فاکتور تست')


class SoldItemViewSetTest(APITestCase):
    """تست‌های ویوی اقلام فاکتور"""
    
    def setUp(self):
        self.client = APIClient()
        setup_groups_and_permissions()
        
        self.manager = UserFactory.create_manager(password='pass123')
        self.cashier = UserFactory.create_cashier(password='pass123')
        
        self.product = ProductFactory.create(quantity=10)
        self.sold = SoldFactory.create(user=self.cashier)
        
        # ✅ استفاده از get_or_create به جای create
        StoreModel.objects.get_or_create(
            product=self.product,
            defaults={'quantity': 10}
        )
        
        self.sold_item = SoldItemFactory.create(
            sold=self.sold,
            product=self.product,
            price=10000,
            quantity=2
        )
        
        self.list_url = reverse('sold_item-list')
        self.detail_url = reverse('sold_item-detail', kwargs={'pk': self.sold_item.id})
    
    def test_create_sold_item(self):
        """تست ایجاد قلم فاکتور"""
        self.client.force_authenticate(user=self.cashier)
        
        # ✅ استفاده از get_or_create
        StoreModel.objects.get_or_create(
            product=self.product,
            defaults={'quantity': 10}
        )
        
        data = {
            'product': f'http://testserver/api/products/{self.product.id}/',
            'sold': f'http://testserver/api/sold/{self.sold.id}/',
            'price': 15000,
            'quantity': 3
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_price'], 45000)