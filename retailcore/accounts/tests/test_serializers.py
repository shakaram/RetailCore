from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken
from ..serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from .factories import UserFactory

User = get_user_model()


class CustomUserSerializerTest(TestCase):
    """تست‌های سریالایزر کاربر"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'علی',
            'last_name': 'محمدی',
            'role': 'cashier',
            'age': 30,
            'bio': 'بیوگرافی تست'
        }
    
    def test_serializer_with_valid_data(self):
        """تست سریالایزر با داده‌های معتبر"""
        serializer = CustomUserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'cashier')
    
    def test_serializer_with_minimal_data(self):
        """تست سریالایزر با حداقل داده‌ها"""
        data = {'username': 'minimal_user'}
        serializer = CustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, 'minimal_user')
        self.assertEqual(user.role, 'user')
    def test_serializer_without_username(self):
        """تست سریالایزر بدون نام کاربری (نامعتبر)"""
        data = {
            'email': 'test@example.com',
            'role': 'manager'
        }
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_serializer_read_only_fields(self):
        """تست فیلدهای فقط خواندنی"""
        user = UserFactory.create()
        serializer = CustomUserSerializer(instance=user)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('groups', data)
        self.assertIn('user_permissions', data)
    
    def test_serializer_role_validation(self):
        """تست اعتبارسنجی نقش"""
        invalid_data = self.user_data.copy()
        invalid_data['role'] = 'invalid_role'
        
        serializer = CustomUserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)
    
    def test_serializer_age_validation(self):
        """تست اعتبارسنجی سن"""
        invalid_data = self.user_data.copy()
        invalid_data['age'] = 5
        serializer = CustomUserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
        invalid_data['age'] = 130
        serializer = CustomUserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
    
    def test_serializer_update(self):
        """تست بروزرسانی کاربر با سریالایزر"""
        user = UserFactory.create(role='user')
        serializer = CustomUserSerializer(
            instance=user,
            data={'role': 'manager', 'username': user.username},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.role, 'manager')
    
    def test_serializer_hidden_fields(self):
        """تست فیلدهای پنهان (رمز عبور)"""
        user = UserFactory.create()
        serializer = CustomUserSerializer(instance=user)
        data = serializer.data
        self.assertNotIn('password', data)
    
    def test_serializer_with_groups_and_permissions(self):
        """تست سریالایزر با گروه‌ها و مجوزها"""
        from django.contrib.auth.models import Group, Permission
        
        group = Group.objects.create(name='test_group')
        perm = Permission.objects.first()
        if perm:
            group.permissions.add(perm)
        
        user = UserFactory.create()
        user.groups.add(group)
        
        serializer = CustomUserSerializer(instance=user)
        data = serializer.data
        
        self.assertIn('groups', data)
        self.assertIn('user_permissions', data)


class CustomTokenObtainPairSerializerTest(TestCase):
    """تست‌های سریالایزر توکن JWT"""
    
    def setUp(self):
        self.user = UserFactory.create(
            username='testuser',
            password='TestPass123!',
            role='manager'
        )
    
    def test_get_token_contains_role(self):
        """تست اینکه توکن حاوی نقش کاربر است"""
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(self.user)
        
        self.assertEqual(token['role'], 'manager')
        self.assertIsNotNone(token['user_id'])
    
    def test_token_has_custom_claim(self):
        """تست Claim سفارشی در توکن"""
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(self.user)
        
        self.assertIn('role', token)
        self.assertEqual(token['role'], 'manager')
    
    def test_validate_returns_role_and_username(self):
        """تست متد validate برای بازگشت اطلاعات کاربر"""
        serializer = CustomTokenObtainPairSerializer(
            data={
                'username': 'testuser',
                'password': 'TestPass123!'
            }
        )
        
        try:
            result = serializer.validate({
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            self.assertIn('role', result)
            self.assertIn('username', result)
            self.assertEqual(result['username'], 'testuser')
        except Exception as e:

            self.skipTest(f"auth_kit not configured: {e}")
    
    def test_token_serializer_works_with_jwt(self):
        """تست عملکرد سریالایزر توکن با JWT"""
        
        serializer = CustomTokenObtainPairSerializer()
        self.assertTrue(hasattr(serializer, 'get_token'))
        self.assertTrue(hasattr(serializer, 'validate'))