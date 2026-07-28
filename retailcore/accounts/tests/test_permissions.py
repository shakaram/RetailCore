from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient
from rest_framework.viewsets import ViewSet
from rest_framework import status
from ..permissions import UserPermission
from ..views import AccountsViewSet as Accounts
from .factories import UserFactory

User = get_user_model()


class UserPermissionTest(TestCase):
    """تست‌های مجوزهای کاربر"""
    
    def setUp(self):
        """تنظیمات اولیه"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.permission = UserPermission()
        
        self.manager = UserFactory.create_manager()
        self.supervisor = UserFactory.create_supervisor()
        self.cashier = UserFactory.create_cashier()
        self.sales = UserFactory.create_sales()
        self.user = UserFactory.create_user()
    
    def create_view(self, action):
        """ایجاد یک ویو ساختگی برای تست"""
        view = ViewSet()
        view.action = action
        view.detail = False
        return view
    
    def create_authenticated_request(self, user, method='get', path='/'):
        """ایجاد درخواست احراز هویت شده"""
        request = getattr(self.factory, method)(path)
        request.user = user
        return request
    
    def test_manager_has_permission_all_actions(self):
        """تست مدیر: دسترسی به همه اکشن‌ها"""
        for action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            view = self.create_view(action)
            request = self.create_authenticated_request(self.manager)
            self.assertTrue(
                self.permission.has_permission(request, view),
                f'مدیر باید به اکشن {action} دسترسی داشته باشد'
            )
    
    def test_supervisor_only_supervisor_action(self):
        """تست سوپروایزر: فقط به اکشن supervisor دسترسی دارد"""
        view = self.create_view('supervisor')
        request = self.create_authenticated_request(self.supervisor)
        self.assertTrue(self.permission.has_permission(request, view))
        
        for action in ['list', 'create', 'update', 'partial_update', 'destroy']:
            view = self.create_view(action)
            request = self.create_authenticated_request(self.supervisor)
            self.assertFalse(
                self.permission.has_permission(request, view),
                f'سوپروایزر نباید به اکشن {action} دسترسی داشته باشد'
            )
    
    def test_user_has_permission_retrieve_update_partial(self):
        """تست کاربر عادی: دسترسی به retrieve, update, partial_update"""
        for action in ['retrieve', 'update', 'partial_update']:
            view = self.create_view(action)
            request = self.create_authenticated_request(self.user)
            self.assertTrue(
                self.permission.has_permission(request, view),
                f'کاربر عادی باید به اکشن {action} دسترسی داشته باشد'
            )
    
    def test_user_no_permission_list_create_destroy(self):
        """تست کاربر عادی: دسترسی ندارد به list, create, destroy"""
        for action in ['list', 'create', 'destroy']:
            view = self.create_view(action)
            request = self.create_authenticated_request(self.user)
            self.assertFalse(
                self.permission.has_permission(request, view),
                f'کاربر عادی نباید به اکشن {action} دسترسی داشته باشد'
            )
    
    def test_object_permission_manager_all_objects(self):
        """تست مدیر: دسترسی به همه اشیاء"""
        target_user = UserFactory.create()
        view = self.create_view('retrieve')
        request = self.create_authenticated_request(self.manager)
        
        self.assertTrue(
            self.permission.has_object_permission(request, view, target_user)
        )
    
    def test_object_permission_supervisor_only_sales(self):
        """تست سوپروایزر: فقط به فروشندگان دسترسی دارد"""
        sales_user = UserFactory.create_sales()
        other_user = UserFactory.create_user()
        
        view = self.create_view('retrieve')
        
        request = self.create_authenticated_request(self.supervisor)
        self.assertTrue(
            self.permission.has_object_permission(request, view, sales_user)
        )
        
        request = self.create_authenticated_request(self.supervisor)
        self.assertFalse(
            self.permission.has_object_permission(request, view, other_user)
        )
    
    def test_object_permission_user_own_object(self):
        """تست کاربر عادی: فقط به خودش دسترسی دارد"""
        target_user = UserFactory.create()
        view = self.create_view('retrieve')
        
        request = self.create_authenticated_request(target_user)
        self.assertTrue(
            self.permission.has_object_permission(request, view, target_user)
        )
        
        other_user = UserFactory.create()
        request = self.create_authenticated_request(target_user)
        self.assertFalse(
            self.permission.has_object_permission(request, view, other_user)
        )
    
    def test_object_permission_cashier_no_extra_access(self):
        """تست صندوقدار: به اشیاء دیگر دسترسی ندارد (مگر خودش)"""
        cashier_user = UserFactory.create_cashier()
        target_user = UserFactory.create()
        view = self.create_view('retrieve')
        
        request = self.create_authenticated_request(cashier_user)
        self.assertFalse(
            self.permission.has_object_permission(request, view, target_user)
        )
        
        request = self.create_authenticated_request(cashier_user)
        self.assertTrue(
            self.permission.has_object_permission(request, view, cashier_user)
        )
    
    def test_authenticated_but_no_permission(self):
        """تست کاربر احراز هویت شده بدون مجوز مناسب"""
        view = self.create_view('list')
        request = self.create_authenticated_request(self.user)
        self.assertFalse(self.permission.has_permission(request, view))
    
    def test_unauthenticated_access(self):
        """تست کاربر بدون احراز هویت"""
        view = self.create_view('list')
        request = self.factory.get('/')
        self.assertFalse(self.permission.has_permission(request, view))