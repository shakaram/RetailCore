from rest_framework.permissions import BasePermission , SAFE_METHODS

class WarehousePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.role in ['supervisor','sales'] and request.method in SAFE_METHODS:
            return True
        elif request.user.role in ['manager']:
            return True
        return False

class WastePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.role in ['manager','supervisor']:
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'manager':
            return True
        if request.user.role == 'supervisor':
            return True
        if request.user == obj.user:
            return True
        return False

class ReturnsPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.role in ['supervisor', 'manager']
        
        if view.action == 'create':
            return request.user.role in ['supervisor', 'manager']
        
        if view.action in ['update', 'partial_update', 'destroy']:
            return request.user.role == 'manager'
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'manager':
            return True
        
        if request.user.role == 'supervisor':
            return obj.user == request.user
        
        return False

class TransfersPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.role in ['sales', 'supervisor', 'manager']
        
        if view.action == 'create':
            return request.user.role in ['supervisor', 'manager']
        
        if view.action in ['update', 'partial_update']:
            return request.user.role == 'manager'
        
        if view.action == 'destroy':
            return request.user.role == 'manager'
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'manager':
            return True
        
        if request.user.role == 'supervisor':
            return obj.user == request.user
        
        return False

class StorePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        if view.action == 'create':
            return False
        
        if view.action in ['update', 'partial_update']:
            return request.user.role == 'manager'
        
        if view.action == 'destroy':
            return False
        
        return False

class UpdatedInformationPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.role in ['manager']:
            return True
        return False
