# products/tests/test_permissions.py
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ViewSet
from accounts.tests.factories import UserFactory
from products.permissions import (
    ProductPermission, CompanyPermission, 
    SoldPermission, SoldItemPermission
)


class ProductPermissionTest(TestCase):
    """تست‌های مجوز محصول"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = ProductPermission()
        
        self.manager = UserFactory.create_manager()
        self.supervisor = UserFactory.create_supervisor()
        self.cashier = UserFactory.create_cashier()
        self.user = UserFactory.create_user()
    
    def create_request(self, user, method='GET'):
        """ایجاد درخواست با کاربر مشخص"""
        request = getattr(self.factory, method.lower())('/')
        request.user = user
        request.method = method
        return request
    
    def test_safe_methods_allowed_for_all(self):
        """تست روش‌های امن (GET) برای همه مجاز است"""
        view = ViewSet()
        view.action = 'list'
        
        # ✅ کاربر عادی با GET
        request = self.create_request(self.user, 'GET')
        self.assertTrue(self.permission.has_permission(request, view))
        
        # ✅ بدون احراز هویت با GET
        request = self.factory.get('/')
        self.assertTrue(self.permission.has_permission(request, view))
        
        # ❌ کاربر عادی با POST (غیرامن) مجاز نیست
        request = self.create_request(self.user, 'POST')
        view.action = 'create'
        self.assertFalse(self.permission.has_permission(request, view))
    
    def test_create_update_for_supervisor(self):
        """تست ایجاد و ویرایش برای سوپروایزر مجاز است"""
        view = ViewSet()
        view.action = 'create'
        request = self.create_request(self.supervisor)
        self.assertTrue(self.permission.has_permission(request, view))
        
        view.action = 'update'
        self.assertTrue(self.permission.has_permission(request, view))
    
    def test_create_update_for_manager(self):
        """تست ایجاد و ویرایش برای مدیر مجاز است"""
        view = ViewSet()
        view.action = 'create'
        request = self.create_request(self.manager)
        self.assertTrue(self.permission.has_permission(request, view))
    
    def test_create_update_for_cashier_not_allowed(self):
        """تست ایجاد و ویرایش برای صندوقدار مجاز نیست"""
        view = ViewSet()
        view.action = 'create'
        request = self.create_request(self.cashier, 'POST')
        # ✅ صندوقدار نباید دسترسی داشته باشد
        self.assertFalse(self.permission.has_permission(request, view))
        
        view.action = 'update'
        request = self.create_request(self.cashier, 'PUT')
        self.assertFalse(self.permission.has_permission(request, view))

    def test_create_update_for_supervisor_allowed(self):
        """تست ایجاد و ویرایش برای سوپروایزر مجاز است"""
        view = ViewSet()
        view.action = 'create'
        request = self.create_request(self.supervisor, 'POST')
        self.assertTrue(self.permission.has_permission(request, view))
        
        view.action = 'update'
        request = self.create_request(self.supervisor, 'PUT')
        self.assertTrue(self.permission.has_permission(request, view))
    

class CompanyPermissionTest(TestCase):
    """تست‌های مجوز شرکت"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = CompanyPermission()
        
        self.manager = UserFactory.create_manager()
        self.supervisor = UserFactory.create_supervisor()
        self.cashier = UserFactory.create_cashier()
        self.user = UserFactory.create_user()
    
    def create_request(self, user, method='GET'):
        request = getattr(self.factory, method.lower())('/')  # ✅ تغییر
        request.user = user
        request.method = method  # ✅ تغییر
        return request
    
    def test_safe_methods_allowed(self):
        """تست روش‌های امن برای همه مجاز است"""
        view = ViewSet()
        view.action = 'list'
        
        # ✅ کاربر عادی با GET
        request = self.create_request(self.user, 'GET')
        self.assertTrue(self.permission.has_permission(request, view))
        
        # ✅ بدون احراز هویت با GET
        request = self.factory.get('/')
        self.assertTrue(self.permission.has_permission(request, view))
    
    def test_create_only_manager(self):
        """تست ایجاد فقط برای مدیر مجاز است"""
        view = ViewSet()
        view.action = 'create'
        
        # ✅ مدیر دسترسی دارد
        request = self.create_request(self.manager, 'POST')
        self.assertTrue(self.permission.has_permission(request, view))
        
        # ❌ سوپروایزر دسترسی ندارد
        request = self.create_request(self.supervisor, 'POST')
        self.assertFalse(self.permission.has_permission(request, view))


class SoldPermissionTest(TestCase):
    """تست‌های مجوز فاکتور"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = SoldPermission()
        
        self.manager = UserFactory.create_manager()
        self.supervisor = UserFactory.create_supervisor()
        self.cashier = UserFactory.create_cashier()
        self.user = UserFactory.create_user()
    
    def create_request(self, user, method='GET'):
        request = getattr(self.factory, method.lower())('/')
        request.user = user
        request.method = method
        return request
    
    def test_safe_methods_for_cashier_supervisor_manager(self):
        """تست روش‌های امن برای صندوقدار، سوپروایزر، مدیر مجاز است"""
        view = ViewSet()
        view.action = 'list'
        
        for role_user in [self.cashier, self.supervisor, self.manager]:
            request = self.create_request(role_user, 'GET')
            self.assertTrue(self.permission.has_permission(request, view))
    
    def test_safe_methods_for_user_not_allowed(self):
        """تست روش‌های امن برای کاربر عادی مجاز نیست"""
        view = ViewSet()
        view.action = 'list'
        request = self.create_request(self.user, 'GET')
        self.assertFalse(self.permission.has_permission(request, view))
    
    def test_create_for_cashier_manager(self):
        """تست ایجاد برای صندوقدار و مدیر مجاز است"""
        view = ViewSet()
        view.action = 'create'
        
        # ✅ صندوقدار دسترسی دارد
        request = self.create_request(self.cashier, 'POST')
        self.assertTrue(self.permission.has_permission(request, view))
        
        # ✅ مدیر دسترسی دارد
        request = self.create_request(self.manager, 'POST')
        self.assertTrue(self.permission.has_permission(request, view))
        
        # ❌ سوپروایزر دسترسی ندارد
        request = self.create_request(self.supervisor, 'POST')
        self.assertFalse(self.permission.has_permission(request, view))