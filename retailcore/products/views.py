from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import *
from .permissions import *
from .filters import PriceFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter , OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, OpenApiParameter, OpenApiTypes

class ProductViewSet(ModelViewSet):
    """
    مدیریت محصولات
    
    عملیات CRUD کامل برای محصولات با قابلیت‌های پیشرفته فیلتر و جستجو
    """
    serializer_class=ProductSerializer
    queryset=ProductModel.objects.all().select_related('company').prefetch_related('category')
    permission_classes=[IsAuthenticatedOrReadOnly,ProductPermission]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter,PriceFilterBackend]
    ordering_fields=['price','is_available','create_dt']
    search_fields=['name', 'description']
    filterset_fields=['price','is_available']

    @extend_schema(
        summary="دریافت لیست محصولات",
        description="""
        دریافت لیست کامل محصولات با قابلیت‌های:
        - **فیلتر بر اساس قیمت** (price_min و price_max)
        - **فیلتر بر اساس موجودی** (is_available)
        - **فیلتر بر اساس دسته‌بندی** (category)
        - **فیلتر بر اساس شرکت** (company)
        - **جستجو** در نام و توضیحات
        - **مرتب‌سازی** بر اساس قیمت، موجودی و تاریخ
        """,
        tags=['محصولات'],
        parameters=[
            OpenApiParameter(
                name='price_min',
                description='حداقل قیمت (عدد صحیح)',
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name='price_max',
                description='حداکثر قیمت (عدد صحیح)',
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name='is_available',
                description='فقط محصولات موجود (true/false)',
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name='search',
                description='جستجو در نام و توضیحات محصول',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='ordering',
                description='مرتب‌سازی (price, -price, create_dt, -create_dt)',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='limit',
                description='تعداد آیتم در هر صفحه',
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name='offset',
                description='شروع از ردیف چندم',
                required=False,
                type=int,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=ProductSerializer(many=True),
                description='لیست محصولات با موفقیت دریافت شد'
            ),
            400: OpenApiResponse(description='پارامترهای نامعتبر'),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="ایجاد محصول جدید",
        description="ایجاد یک محصول جدید با تمام اطلاعات (فقط مدیر و سوپروایزر)",
        tags=['محصولات'],
        request=ProductSerializer,
        responses={
            201: OpenApiResponse(
                response=ProductSerializer,
                description='محصول با موفقیت ایجاد شد'
            ),
            400: OpenApiResponse(description='خطا در اعتبارسنجی'),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        },
        examples=[
            OpenApiExample(
                'مثال درخواست',
                value={
                    "name": "لپ تاپ ایسوس",
                    "description": "لپ تاپ با پردازنده i7 و ۱۶ گیگ رم",
                    "price": 25000000,
                    "category": [1, 2],
                    "company": 1
                },
                request_only=True
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="دریافت اطلاعات محصول",
        description="دریافت اطلاعات کامل یک محصول با شناسه",
        tags=['محصولات'],
        responses={
            200: OpenApiResponse(
                response=ProductSerializer,
                description='اطلاعات محصول دریافت شد'
            ),
            404: OpenApiResponse(description='محصول یافت نشد'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="بروزرسانی کامل محصول",
        description="بروزرسانی تمام اطلاعات یک محصول (فقط مدیر و سوپروایزر)",
        tags=['محصولات'],
        request=ProductSerializer,
        responses={
            200: OpenApiResponse(
                response=ProductSerializer,
                description='محصول با موفقیت بروزرسانی شد'
            ),
            400: OpenApiResponse(description='خطا در اعتبارسنجی'),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="بروزرسانی جزئی محصول",
        description="بروزرسانی بخشی از اطلاعات محصول (فقط مدیر و سوپروایزر)",
        tags=['محصولات'],
        request=ProductSerializer,
        responses={
            200: OpenApiResponse(
                response=ProductSerializer,
                description='محصول با موفقیت بروزرسانی شد'
            ),
            400: OpenApiResponse(description='خطا در اعتبارسنجی'),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="حذف محصول",
        description="حذف یک محصول از سیستم (فقط مدیر)",
        tags=['محصولات'],
        responses={
            204: OpenApiResponse(description='محصول با موفقیت حذف شد'),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
            404: OpenApiResponse(description='محصول یافت نشد'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class CompanyViewSet(ModelViewSet):
    """مدیریت شرکت‌های تولیدکننده
    
    این ViewSet عملیات CRUD کامل برای شرکت‌های تولیدکننده محصولات را ارائه می‌دهد."""
    queryset=CompanyModel.objects.all()
    serializer_class=CompanySerializer
    permission_classes=[CompanyPermission]
    
    filter_backends = [ SearchFilter]
    search_fields=['name', 'description']

class SoldViewSet(ModelViewSet):
    """مدیریت فاکتورهای فروش
    
    این ViewSet عملیات CRUD کامل برای فاکتورهای فروش را ارائه می‌دهد."""
    queryset=SoldModel.objects.all().select_related('user')
    serializer_class=SoldSerializer
    permission_classes=[SoldPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields=['user__username', 'user__first_name', 'user__last_name','price','description']
    ordering_fields=['price','create_dt','date']
    filterset_fields=['user__username', 'user__role', 'price']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'manager':
            return queryset
        elif user.role == 'supervisor':
            return queryset
        elif user.role == 'sales':
            return queryset.filter(user=user)
        return queryset.none()

class SoldItemViewSet(ModelViewSet):
    """مدیریت اقلام فاکتورهای فروش
    
    این ViewSet عملیات CRUD کامل برای اقلام هر فاکتور فروش را ارائه می‌دهد."""
    queryset=SoldItemModel.objects.all().select_related('product__company','sold__user')
    serializer_class=SoldItemSerializer
    permission_classes=[SoldItemPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields=['product__name','sold__id','sold__user__username']
    filterset_fields=['product__name','sold__id','price','date']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'manager':
            return queryset
        elif user.role == 'supervisor':
            return queryset
        elif user.role == 'sales':
            return queryset.filter(sold__user=user)
        return queryset.none()

class CategoryViewSet(ModelViewSet):
    """مدیریت دسته‌بندی محصولات
    
    این ViewSet عملیات CRUD کامل برای دسته‌بندی‌های سلسله‌مراتبی محصولات را ارائه می‌دهد."""
    queryset=CategoryModel.objects.all().select_related('subset')
    serializer_class=CategorySerializer
    permission_classes=[CategoryPermission]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name'] 
    filterset_fields = ['name', 'subset__name']

class ImageProductViewSet(ModelViewSet):
    """مدیریت تصاویر محصولات
    
    این ViewSet عملیات CRUD کامل برای تصاویر محصولات را ارائه می‌دهد."""
    queryset=ImageProductModel.objects.all().select_related('product__company')
    serializer_class=ImageProductSerializer
    permission_classes=[ImageProductPermission]

    filter_backends = [DjangoFilterBackend]
    filterset_fields=['product__id']
