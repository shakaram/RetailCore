from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    groups_permissions = {
        'supervisor': ['view_companymodel','add_companymodel','change_companymodel',
                       'view_categorymodel','add_categorymodel','change_categorymodel',
                       'view_productmodel','add_productmodel','change_productmodel',
                       'view_imageproductmodel','add_imageproductmodel','change_imageproductmodel','delete_imageproductmodel',
                       'view_soldmodel','view_solditemmodel',
                       'view_warehousemodel','change_warehousemodel',
                       'view_wastemodel','add_wastemodel','change_wastemodel','delete_wastemodel',
                       'view_returnsmodel','add_returnsmodel','change_returnsmodel',
                       'view_transfersmodel','add_transfersmodel','change_transfersmodel',
                       'view_storemodel',],

        'cashier': ['view_companymodel','view_categorymodel','view_productmodel',
                    'view_soldmodel','add_soldmodel','change_soldmodel',
                    'view_solditemmodel','add_SoldItemModel','change_SoldItemModel','delete_SoldItemModel',
                    'view_storemodel'],

        'sales':['view_companymodel','view_categorymodel','view_productmodel',
                 'view_warehousemodel',
                 'view_wastemodel','add_wastemodel','change_wastemodel',],

        'user':['view_companymodel','view_categorymodel','view_productmodel',
                'view_storemodel']


    }
    
    manager_group, _ = Group.objects.get_or_create(name='manager')
    
    all_permissions = Permission.objects.all()
    manager_group.permissions.set(all_permissions)
    

    for group_name, perms in groups_permissions.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        for perm in perms:
            try:
                permission = Permission.objects.get(codename=perm)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                pass

