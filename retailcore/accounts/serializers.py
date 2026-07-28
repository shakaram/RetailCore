from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class CustomUserSerializer(serializers.ModelSerializer):
    """سریالایزر کاربر با اطلاعات کامل"""
    groups = serializers.StringRelatedField(many=True, read_only=True)
    user_permissions = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model=User
        fields=['id','username','email','profile','bio','age',
                'role','first_name','last_name', 'groups', 'user_permissions']
        extra_kwargs = {
            'username': {'help_text': 'نام کاربری (حداکثر ۱۵۰ کاراکتر)'},
            'email': {'help_text': 'ایمیل کاربر', 'required': False},
            'profile': {'help_text': 'تصویر پروفایل کاربر'},
            'bio': {'help_text': 'بیوگرافی کاربر'},
            'age': {'help_text': 'سن کاربر (بین ۱۰ تا ۱۲۰ سال)'},
            'role': {'help_text': 'نقش کاربر در سیستم'},
            'first_name': {'help_text': 'نام'},
            'last_name': {'help_text': 'نام خانوادگی'},
        }

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """سریالایزر دریافت توکن JWT با اطلاعات اضافی
    این سریالایزر علاوه بر توکن‌های استاندارد، اطلاعات نقش کاربر را نیز برمی‌گرداند."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role']=user.role
        token['username'] = user.username
        return token
