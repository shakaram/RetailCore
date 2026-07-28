# store/tests/test_permissions.py
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ViewSet
from accounts.tests.factories import UserFactory
from store.permissions import (
    WarehousePermission, WastePermission, ReturnsPermission,
    TransfersPermission, StorePermission, UpdatedInformationPermission
)


class WarehousePermissionTest(TestCase):
    """تست‌های مجوز انبار"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = WarehousePermission()
        
        self.manager = UserFactory.create_manager()
        self.supervisor = UserFactory.create_supervisor()
        self.sales = UserFactory.create_sales()
        self.user = UserFactory.create_user()
    
    def create_request(self, user, method='GET'):
        request = getattr(self.factory, method.lower())('/')
        request.user = user
        request.method = method
        return request
    
    def test_safe_methods_for_supervisor_sales(self):
        """تست روش‌های امن برای سوپروایزر و فروشنده مجاز است"""
        view = ViewSet()
        view.action = 'list'
        
        for role_user in [self.supervisor, self.sales]:
            request = self.create_request(role_user, 'GET')
            self.assertTrue(self.permission.has_permission(request, view))
    
    def test_manager_full_access(self):
        """تست مدیر دسترسی کامل دارد"""
        view = ViewSet()
        view.action = 'create'
        request = self.create_request(self.manager, 'POST')
        self.assertTrue(self.permission.has_permission(request, view))
    
    def test_user_no_access(self):
        """تست کاربر عادی دسترسی ندارد"""
        view = ViewSet()
        view.action = 'list'
        request = self.create_request(self.user, 'GET')
        self.assertFalse(self.permission.has_permission(request, view))


class WastePermissionTest(TestCase):
    """تست‌های مجوز ضایعات"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = WastePermission()
        
        self.manager = UserFactory.create_manager()
        self.supervisor = UserFactory.create_supervisor()
        self.sales = UserFactory.create_sales()
        self.user = UserFactory.create_user()
    
    def create_request(self, user, method='GET'):
        request = getattr(self.factory, method.lower())('/')
        request.user = user
        request.method = method
        return request
    
    def test_manager_supervisor_access(self):
        """تست مدیر و سوپروایزر دسترسی دارند"""
        view = ViewSet()
        view.action = 'create'
        
        for role_user in [self.manager, self.supervisor]:
            request = self.create_request(role_user, 'POST')
            self.assertTrue(self.permission.has_permission(request, view))
    
    def test_sales_no_create_access(self):
        """تست فروشنده دسترسی ایجاد ندارد"""
        view = ViewSet()
        view.action = 'create'
        request = self.create_request(self.sales, 'POST')
        self.assertFalse(self.permission.has_permission(request, view))