from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from factory import django, Faker, post_generation
from factory.django import DjangoModelFactory

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = Faker('user_name')
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    raw_password = Faker('password', length=12)  
    role = 'user'
    age = Faker('random_int', min=18, max=60)
    bio = Faker('text', max_nb_chars=100)
    is_active = True
    profile = None  
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        raw_password = kwargs.pop('raw_password', None)
        user = super()._create(model_class, *args, **kwargs)
        if raw_password:
            user.set_password(raw_password)
            user._raw_password = raw_password  
            user.save()
        return user
    
    @post_generation
    def set_role(self, create, extracted, **kwargs):
        """تنظیم نقش کاربر"""
        if extracted:
            self.role = extracted
            self.save()
    
    @classmethod
    def create_manager(cls, **kwargs):
        return cls.create(role='manager', **kwargs)
    
    @classmethod
    def create_supervisor(cls, **kwargs):
        return cls.create(role='supervisor', **kwargs)
    
    @classmethod
    def create_cashier(cls, **kwargs):
        return cls.create(role='cashier', **kwargs)
    
    @classmethod
    def create_sales(cls, **kwargs):
        return cls.create(role='sales', **kwargs)
    
    @classmethod
    def create_user(cls, **kwargs):
        return cls.create(role='user', **kwargs)



class GroupFactory(DjangoModelFactory):
    """کارخانه تولید گروه‌ها"""
    
    class Meta:
        model = Group
        django_get_or_create = ('name',)
    
    name = Faker('word')


def setup_groups_and_permissions():
    """
    ایجاد گروه‌ها و مجوزهای مورد نیاز برای تست
    
    این تابع مشابه سیگنال create_groups در signals.py است
    """
    groups_permissions = {
        'supervisor': [
            'view_companymodel', 'add_companymodel', 'change_companymodel',
            'view_categorymodel', 'add_categorymodel', 'change_categorymodel',
            'view_productmodel', 'add_productmodel', 'change_productmodel',
            'view_imageproductmodel', 'add_imageproductmodel', 'change_imageproductmodel', 'delete_imageproductmodel',
            'view_soldmodel', 'view_solditemmodel',
            'view_warehousemodel', 'change_warehousemodel',
            'view_wastemodel', 'add_wastemodel', 'change_wastemodel', 'delete_wastemodel',
            'view_returnsmodel', 'add_returnsmodel', 'change_returnsmodel',
            'view_transfersmodel', 'add_transfersmodel', 'change_transfersmodel',
            'view_storemodel',
        ],
        'cashier': [
            'view_companymodel', 'view_categorymodel', 'view_productmodel',
            'view_soldmodel', 'add_soldmodel', 'change_soldmodel',
            'view_solditemmodel', 'add_solditemmodel', 'change_solditemmodel', 'delete_solditemmodel',
            'view_storemodel',
        ],
        'sales': [
            'view_companymodel', 'view_categorymodel', 'view_productmodel',
            'view_warehousemodel',
            'view_wastemodel', 'add_wastemodel', 'change_wastemodel',
        ],
        'user': [
            'view_companymodel', 'view_categorymodel', 'view_productmodel',
            'view_storemodel',
        ]
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