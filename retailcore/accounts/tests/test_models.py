from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import User
from .factories import UserFactory

User = get_user_model()


class UserModelTest(TestCase):
    """تست‌های مدل کاربر"""
    
    def setUp(self):
        """تنظیمات اولیه قبل از هر تست"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'علی',
            'last_name': 'محمدی',
            'role': 'user',
            'age': 25,
            'bio': 'این یک بیوگرافی تست است'
        }
    
    def test_create_user_with_minimum_fields(self):
        """تست ایجاد کاربر با حداقل فیلدها"""
        user = User.objects.create_user(
            username='minimal_user',
            password='pass123'
        )
        
        self.assertEqual(user.username, 'minimal_user')
        self.assertEqual(user.role, 'user')
        self.assertTrue(user.check_password('pass123'))
        self.assertIsNone(user.age)
        self.assertIsNone(user.bio)
    
    def test_create_user_with_all_fields(self):
        """تست ایجاد کاربر با تمام فیلدها"""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            role=self.user_data['role'],
            age=self.user_data['age'],
            bio=self.user_data['bio']
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'علی')
        self.assertEqual(user.last_name, 'محمدی')
        self.assertEqual(user.role, 'user')
        self.assertEqual(user.age, 25)
        self.assertEqual(user.bio, 'این یک بیوگرافی تست است')
    
    def test_age_validation_min_value(self):
        """تست اعتبارسنجی سن - مقدار کمتر از حد مجاز"""
        with self.assertRaises(ValidationError):
            user = User(
                username='young_user',
                age=5
            )
            user.full_clean()  
    
    def test_age_validation_max_value(self):
        """تست اعتبارسنجی سن - مقدار بیشتر از حد مجاز"""
        with self.assertRaises(ValidationError):
            user = User(
                username='old_user',
                age=130
            )
            user.full_clean()
    
    def test_age_validation_allowed_values(self):
        """تست اعتبارسنجی سن - مقادیر مجاز"""
        allowed_ages = [10, 25, 60, 120]
        for age in allowed_ages:
            user = User(
                username=f'user_age_{age}',
                password='TestPass123!',
                age=age
            )
            try:
                user.full_clean()
            except ValidationError:
                self.fail(f'سن {age} باید مجاز باشد')
    
    def test_role_choices(self):
        """تست انتخاب نقش‌های معتبر"""
        valid_roles = ['user', 'sales', 'cashier', 'supervisor', 'manager']
        
        for role in valid_roles:
            user = User(
                username=f'user_{role}',
                password='TestPass123!',
                role=role
            )
            try:
                user.full_clean()
            except ValidationError:
                self.fail(f'نقش {role} باید معتبر باشد')
    
    def test_role_choices_invalid(self):
        """تست نقش نامعتبر"""
        user = User(
            username='invalid_role_user',
            role='invalid_role'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_unique_username(self):
        """تست یکتایی نام کاربری"""
        User.objects.create_user(username='unique_user', password='pass123')
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='unique_user', password='pass456')
    
    def test_str_method(self):
        """تست متد __str__"""
        user = UserFactory.create(username='test_str', role='manager')
        self.assertEqual(str(user), 'test_str - manager')
    
    def test_user_factory_creation(self):
        """تست ایجاد کاربر با factory-boy"""
        user = UserFactory.create()
        self.assertIsNotNone(user.id)
        self.assertTrue(user.check_password(user._raw_password))
    
    def test_factory_with_specific_role(self):
        """تست ایجاد کاربر با نقش مشخص"""
        manager = UserFactory.create_manager()
        supervisor = UserFactory.create_supervisor()
        cashier = UserFactory.create_cashier()
        sales = UserFactory.create_sales()
        user = UserFactory.create_user()
        
        self.assertEqual(manager.role, 'manager')
        self.assertEqual(supervisor.role, 'supervisor')
        self.assertEqual(cashier.role, 'cashier')
        self.assertEqual(sales.role, 'sales')
        self.assertEqual(user.role, 'user')
    
    def test_profile_image_optional(self):
        """تست فیلد تصویر پروفایل (اختیاری)"""
        user = UserFactory.create()
        user.profile = None
        user.save()
        self.assertEqual(user.profile.name, None)
    
    def test_bio_optional(self):
        """تست فیلد بیوگرافی (اختیاری)"""
        user_without_bio = UserFactory.create(bio=None)
        self.assertIsNone(user_without_bio.bio)
        
        user_with_bio = UserFactory.create(bio='این یک بیوگرافی تست است')
        self.assertEqual(user_with_bio.bio, 'این یک بیوگرافی تست است')
    
    def test_email_optional(self):
        """تست فیلد ایمیل (اختیاری)"""
        user_without_email = UserFactory.create(email='')
        self.assertEqual(user_without_email.email, '')
        
        user_with_email = UserFactory.create(email='test@example.com')
        self.assertEqual(user_with_email.email, 'test@example.com')
    
    def test_is_active_default(self):
        """تست وضعیت فعال بودن کاربر (پیش‌فرض)"""
        user = UserFactory.create()
        self.assertTrue(user.is_active)
    
    def test_is_staff_default(self):
        """تست وضعیت کارمند بودن (پیش‌فرض)"""
        user = UserFactory.create()
        self.assertFalse(user.is_staff)
    
    def test_is_superuser_default(self):
        """تست وضعیت سوپریوزر بودن (پیش‌فرض)"""
        user = UserFactory.create()
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """تست ایجاد سوپریوزر"""
        superuser = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)
        self.assertEqual(superuser.username, 'admin')
    
    def test_user_permissions_relationship(self):
        """تست رابطه کاربر با مجوزها"""
        user = UserFactory.create()
        self.assertEqual(user.user_permissions.count(), 0)
        
        from django.contrib.auth.models import Permission
        perm = Permission.objects.first()
        if perm:
            user.user_permissions.add(perm)
            self.assertEqual(user.user_permissions.count(), 1)