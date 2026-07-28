from rest_framework import permissions

class ProductPermission(permissions.BasePermission):
    """مدیریت دسترسی‌های محصولات"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        elif request.user.role == 'manager':
            return True
        
        elif request.user.role in ['supervisor'] and view.action in ['create', 'update', 'partial_update']:
            return True
        
        return False

class CompanyPermission(permissions.BasePermission):
    """مدیریت دسترسی‌های شرکت‌ها"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.role == 'manager':
            return True
        return False

class SoldPermission(permissions.BasePermission):
    """مدیریت دسترسی‌های فاکتورهای فروش"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['cashier', 'supervisor', 'manager']
        
        if view.action in ['create', 'update', 'partial_update']:
            return request.user.role in ['cashier', 'manager']
        
        if view.action == 'destroy':
            return request.user.role == 'manager'
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'manager':
            return True
        
        if request.user.role == 'cashier':
            return request.user == obj.cashier
        
        if request.user.role == 'supervisor':
            return True
        
        return False

class SoldItemPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'manager':
            return True
        
        elif request.method in permissions.SAFE_METHODS:
            return request.user.role in ['supervisor', 'cashier']
        
        elif request.user.role in ['cashier', 'manager'] and view.action == 'create':
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'manager':
            return True
        
        if request.user.role == 'cashier':
            return request.user == obj.sold.cashier
        
        if request.user.role == 'supervisor':
            return True
        
        return False

class CategoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.role in ['manager','supervisor']:
            return True
        return False

class ImageProductPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role in ['manager','supervisor']:
            return True
        return False
