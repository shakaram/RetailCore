from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User
from .serializers import CustomUserSerializer
from .permissions import UserPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter , OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


class AccountsViewSet(ModelViewSet):
    """
    مدیریت کاربران سیستم
    
    ارائه دهنده عملیات CRUD برای کاربران با کنترل دسترسی بر اساس نقش
    """
    serializer_class=CustomUserSerializer
    queryset=User.objects.all()
    permission_classes=[IsAuthenticated,UserPermission]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields=['age']
    search_fields=['id', 'username', 'first_name', 'last_name']
    filterset_fields=['role','age']

    
    @extend_schema(
        summary="لیست کاربران",
        description="دریافت لیست تمام کاربران با قابلیت فیلتر و جستجو",
        tags=['کاربران'],
        responses={
            200: OpenApiResponse(
                response=CustomUserSerializer(many=True),
                description='لیست کاربران با موفقیت دریافت شد'
            ),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        },
        examples=[
            OpenApiExample(
                'مثال پاسخ',
                value=[
                    {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "role": "manager",
                        "first_name": "مدیر",
                        "last_name": "سیستم"
                    }
                ],
                response_only=True
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="ایجاد کاربر جدید",
        description="ایجاد یک کاربر جدید با اطلاعات کامل",
        tags=['کاربران'],
        request=CustomUserSerializer,
        responses={
            201: OpenApiResponse(
                response=CustomUserSerializer,
                description='کاربر با موفقیت ایجاد شد'
            ),
            400: OpenApiResponse(description='خطا در اعتبارسنجی'),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="دریافت اطلاعات کاربر",
        description="دریافت اطلاعات کامل یک کاربر با شناسه",
        tags=['کاربران'],
        responses={
            200: OpenApiResponse(
                response=CustomUserSerializer,
                description='اطلاعات کاربر دریافت شد'
            ),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
            404: OpenApiResponse(description='کاربر یافت نشد'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="بروزرسانی کامل کاربر",
        description="بروزرسانی تمام اطلاعات یک کاربر",
        tags=['کاربران'],
        request=CustomUserSerializer,
        responses={
            200: OpenApiResponse(
                response=CustomUserSerializer,
                description='کاربر با موفقیت بروزرسانی شد'
            ),
            400: OpenApiResponse(description='خطا در اعتبارسنجی'),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="بروزرسانی جزئی کاربر",
        description="بروزرسانی بخشی از اطلاعات یک کاربر",
        tags=['کاربران'],
        request=CustomUserSerializer,
        responses={
            200: OpenApiResponse(
                response=CustomUserSerializer,
                description='کاربر با موفقیت بروزرسانی شد'
            ),
            400: OpenApiResponse(description='خطا در اعتبارسنجی'),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="حذف کاربر",
        description="حذف یک کاربر از سیستم (فقط مدیر)",
        tags=['کاربران'],
        responses={
            204: OpenApiResponse(description='کاربر با موفقیت حذف شد'),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
            404: OpenApiResponse(description='کاربر یافت نشد'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="دریافت فروشندگان",
        description="دریافت لیست کاربران با نقش فروشنده (فقط سوپروایزر)",
        tags=['کاربران'],
        responses={
            200: OpenApiResponse(
                response=CustomUserSerializer(many=True),
                description='لیست فروشندگان دریافت شد'
            ),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        }
    )
    @action(detail=False, methods=['get'])
    def supervisor(self, request):
        """دریافت لیست فروشندگان (اکشن اختصاصی برای سوپروایزر)"""
        queryset = User.objects.filter(role='sales')
        serializer = CustomUserSerializer(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)