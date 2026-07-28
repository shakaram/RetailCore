from rest_framework.permissions import BasePermission
class UserPermission(BasePermission):
    """مدیریت دسترسی‌های کاربران"""
    
    def has_permission(self, request, view):

        if not hasattr(request, 'user') or not request.user or not request.user.is_authenticated:
            return False

        if request.user.role == 'manager':
            return True
        
        if request.user.role == 'supervisor':
            return view.action in ['supervisor', 'retrieve']
        
        if view.action in ['retrieve', 'update', 'partial_update']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):

        if not hasattr(request, 'user') or not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'manager':
            return True
        
        if request.user.role == 'supervisor' and obj.role == 'sales':
            return True
        
        if request.user.id == obj.id:
            return True
        
        return False
