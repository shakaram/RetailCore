from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient, force_authenticate
from rest_framework import status
from ..models import User
from .factories import UserFactory, setup_groups_and_permissions

User = get_user_model()


class AccountsViewSetTest(APITestCase):
    """تست‌های ویوی Accounts"""
    
    def setUp(self):
        """تنظیمات اولیه قبل از هر تست"""
        self.client = APIClient()
        
        setup_groups_and_permissions()
        
        self.manager = UserFactory.create_manager(
            username='manager_user',
            password='Manager123!'
        )
        self.supervisor = UserFactory.create_supervisor(
            username='supervisor_user',
            password='Super123!'
        )
        self.cashier = UserFactory.create_cashier(
            username='cashier_user',
            password='Cash123!'
        )
        self.sales = UserFactory.create_sales(
            username='sales_user',
            password='Sales123!'
        )
        self.user = UserFactory.create_user(
            username='normal_user',
            password='User123!'
        )
        
        self.list_url = reverse('user-list')
    
    def test_list_users_as_manager(self):
        """تست دریافت لیست کاربران توسط مدیر"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 5)
    
    def test_list_users_as_supervisor(self):
        """تست دریافت لیست کاربران توسط سوپروایزر (دسترسی ندارد)"""
        self.client.force_authenticate(user=self.supervisor)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_users_as_normal_user(self):
        """تست دریافت لیست کاربران توسط کاربر عادی (دسترسی ندارد)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_users_unauthenticated(self):
        """تست دریافت لیست کاربران بدون احراز هویت"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_user_as_manager(self):
        """تست ایجاد کاربر جدید توسط مدیر"""
        self.client.force_authenticate(user=self.manager)
        
        data = {
            'username': 'new_user',
            'password': 'NewPass123!',
            'email': 'new@example.com',
            'role': 'cashier',
            'first_name': 'رضا',
            'last_name': 'کریمی',
            'age': 28
        }
        
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'new_user')
        self.assertEqual(response.data['role'], 'cashier')
        
        user = User.objects.get(username='new_user')
        self.assertEqual(user.email, 'new@example.com')
    
    def test_create_user_as_normal_user(self):
        """تست ایجاد کاربر توسط کاربر عادی (دسترسی ندارد)"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'username': 'unauthorized_user',
            'password': 'Pass123!',
            'role': 'user'
        }
        
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_user_as_manager(self):
        """تست دریافت اطلاعات کاربر توسط مدیر"""
        target_user = UserFactory.create(username='target_user')
        url = reverse('user-detail', kwargs={'pk': target_user.id})
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'target_user')
    
    def test_retrieve_user_as_supervisor_to_sales(self):
        """تست سوپروایزر به فروشنده دسترسی دارد"""
        sales_user = UserFactory.create_sales(username='sales_for_supervisor')
        url = reverse('user-detail', kwargs={'pk': sales_user.id})
        
        self.client.force_authenticate(user=self.supervisor)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'sales_for_supervisor')
    
    def test_retrieve_user_as_supervisor_to_other(self):
        """تست سوپروایزر به غیر فروشنده دسترسی ندارد"""
        other_user = UserFactory.create_user(username='other_user')
        url = reverse('user-detail', kwargs={'pk': other_user.id})
        
        self.client.force_authenticate(user=self.supervisor)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_own_user(self):
        """تست کاربر عادی به خودش دسترسی دارد"""
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
    
    def test_retrieve_other_user_as_normal_user(self):
        """تست کاربر عادی به کاربر دیگر دسترسی ندارد"""
        other_user = UserFactory.create_user(username='other_normal')
        url = reverse('user-detail', kwargs={'pk': other_user.id})
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_user_as_manager(self):
        """تست بروزرسانی کاربر توسط مدیر"""
        target_user = UserFactory.create_user(username='update_target')
        url = reverse('user-detail', kwargs={'pk': target_user.id})
        
        self.client.force_authenticate(user=self.manager)
        data = {
            'username': 'updated_username',
            'role': 'supervisor',
            'first_name': 'علی',
            'last_name': 'رضایی'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'updated_username')
        self.assertEqual(response.data['role'], 'supervisor')
    
    def test_partial_update_user_as_manager(self):
        """تست بروزرسانی جزئی کاربر توسط مدیر"""
        target_user = UserFactory.create_user(username='partial_update_target')
        url = reverse('user-detail', kwargs={'pk': target_user.id})
        
        self.client.force_authenticate(user=self.manager)
        data = {'role': 'cashier'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'cashier')
        self.assertEqual(response.data['username'], 'partial_update_target')
    
    def test_update_own_user_as_normal(self):
        """تست کاربر عادی اطلاعات خودش را بروزرسانی کند"""
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        
        self.client.force_authenticate(user=self.user)
        data = {
            'username': self.user.username,
            'first_name': 'نام جدید',
            'last_name': 'نام خانوادگی جدید'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'نام جدید')
    
    def test_update_other_user_as_normal(self):
        """تست کاربر عادی کاربر دیگر را بروزرسانی کند (دسترسی ندارد)"""
        other_user = UserFactory.create_user(username='other_update')
        url = reverse('user-detail', kwargs={'pk': other_user.id})
        
        self.client.force_authenticate(user=self.user)
        data = {'first_name': 'تغییر غیرمجاز'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_user_as_manager(self):
        """تست حذف کاربر توسط مدیر"""
        target_user = UserFactory.create_user(username='delete_target')
        url = reverse('user-detail', kwargs={'pk': target_user.id})
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=target_user.id).exists())
    
    def test_delete_user_as_normal(self):
        """تست حذف کاربر توسط کاربر عادی (دسترسی ندارد)"""
        target_user = UserFactory.create_user(username='delete_other')
        url = reverse('user-detail', kwargs={'pk': target_user.id})
        
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_supervisor_action(self):
        """تست اکشن supervisor (دریافت فروشندگان)"""
        UserFactory.create_sales(username='sales1')
        UserFactory.create_sales(username='sales2')
        UserFactory.create_sales(username='sales3')
        
        url = reverse('user-supervisor')
        
        self.client.force_authenticate(user=self.supervisor)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user_data in response.data:
            self.assertEqual(user_data['role'], 'sales')
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_filter_users_by_role(self):
        """تست فیلتر کردن کاربران بر اساس نقش"""
        self.client.force_authenticate(user=self.manager)
        
        response = self.client.get(self.list_url, {'role': 'manager'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user_data in response.data['results']:
            self.assertEqual(user_data['role'], 'manager')
        
        response = self.client.get(self.list_url, {'role': 'cashier'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user_data in response.data['results']:
            self.assertEqual(user_data['role'], 'cashier')
    
    def test_search_users(self):
        """تست جستجو در کاربران"""
        UserFactory.create(username='reza_ahmadi', first_name='رضا', last_name='احمدی')
        UserFactory.create(username='ali_karimi', first_name='علی', last_name='کریمی')
        
        self.client.force_authenticate(user=self.manager)
        
        response = self.client.get(self.list_url, {'search': 'رضا'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        response = self.client.get(self.list_url, {'search': 'ali_karimi'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_order_users_by_age(self):
        """تست مرتب‌سازی کاربران بر اساس سن"""
        UserFactory.create(age=20)
        UserFactory.create(age=30)
        UserFactory.create(age=25)
        
        self.client.force_authenticate(user=self.manager)
        
        response = self.client.get(self.list_url, {'ordering': 'age'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ages = [user['age'] for user in response.data['results'] if user['age'] is not None]
        if ages:
            self.assertEqual(ages, sorted(ages))
        
        response = self.client.get(self.list_url, {'ordering': '-age'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ages = [user['age'] for user in response.data['results'] if user['age'] is not None]
        if ages:
            self.assertEqual(ages, sorted(ages, reverse=True))
    
    def test_pagination(self):
        for i in range(25):
            UserFactory.create(username=f'user_{i}')
        self.client.force_authenticate(user=self.manager)
        total_users = User.objects.count()
        response = self.client.get(self.list_url, {'limit': 10, 'offset': 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], total_users)
    
    def test_invalid_age_filter(self):
        """تست فیلتر سن نامعتبر"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.list_url, {'age': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_rate_limiting(self):
        """تست محدودیت نرخ (اگر پیاده‌سازی شده باشد)"""
        
        self.skipTest("Rate limiting not implemented in this version")