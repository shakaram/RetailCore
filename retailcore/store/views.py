from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import *
from .permissions import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter , OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

# Create your views here.
class WarehouseViewSet(ModelViewSet):
    """
    مدیریت موجودی انبار
    
    مشاهده و مدیریت موجودی کالاها در انبار
    """
    serializer_class=WarehouseSerializer
    queryset=WarehouseModel.objects.all().select_related('product__company')
    permission_classes=[IsAuthenticated,WarehousePermission]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields=['product__price','is_available']
    search_fields=['product__name', 'product__id','product__description']
    filterset_fields=['product__price','is_available','product__company__name']

    @extend_schema(
        summary="دریافت موجودی انبار",
        description="دریافت لیست موجودی انبار با قابلیت فیلتر و جستجو",
        tags=['انبار'],
        parameters=[
            OpenApiParameter(
                name='is_available',
                description='فقط کالاهای موجود',
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name='search',
                description='جستجو در نام و شناسه محصول',
                required=False,
                type=str
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=WarehouseSerializer(many=True),
                description='لیست موجودی انبار دریافت شد'
            ),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class WasteViewSet(ModelViewSet):
    """
    مدیریت ضایعات
    
    ثبت و مدیریت کالاهای ضایعاتی
    """
    serializer_class=WasteSerializer
    queryset=WasteModel.objects.all().select_related('product__company')
    permission_classes=[IsAuthenticated,WastePermission]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields=['product__price','is_available','create_dt']
    search_fields=['product__name', 'product__id','product__description']
    filterset_fields=['product__price','is_available','create_dt']

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
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @extend_schema(
        summary="ثبت ضایعات جدید",
        description="ثبت یک کالا به عنوان ضایعات (فقط مدیر و سوپروایزر)",
        tags=['ضایعات'],
        request=WasteSerializer,
        responses={
            201: OpenApiResponse(
                response=WasteSerializer,
                description='ضایعات با موفقیت ثبت شد'
            ),
            400: OpenApiResponse(description='خطا در اعتبارسنجی'),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class ReturnsViewSet(ModelViewSet):
    """مدیریت مرجوعی محصولات
    
    این ViewSet عملیات CRUD کامل برای مرجوعی محصولات را ارائه می‌دهد."""
    serializer_class=ReturnsSerializer
    queryset=ReturnsModel.objects.all().select_related('product__company')
    permission_classes=[IsAuthenticated,ReturnsPermission]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields=['product__price','is_available','create_dt','user__username']
    search_fields=['product__name', 'product__id','product__description']
    filterset_fields=['product__price','is_available','create_dt','user__username','product__company__name']

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
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransfersViewSet(ModelViewSet):
    """مدیریت انتقالات از انبار به فروشگاه
    
    این ViewSet عملیات CRUD کامل برای انتقال محصولات از انبار به فروشگاه را ارائه می‌دهد."""
    serializer_class=TransfersSerializer
    queryset=TransfersModel.objects.all().select_related('product__company')
    permission_classes=[IsAuthenticated,TransfersPermission]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields=['product__price','is_available']
    search_fields=['product__name', 'product__id','product__description']
    filterset_fields=['product__price','is_available']

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
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StoreViewSet(ModelViewSet):
    """
    مدیریت موجودی فروشگاه
    
    مشاهده موجودی کالاها در فروشگاه (فقط خواندنی)
    """
    serializer_class=StoreSerializer
    queryset=StoreModel.objects.all().select_related('product__company')
    permission_classes=[IsAuthenticated,StorePermission]
    http_method_names = ['get']

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields=['product__price','is_available']
    search_fields=['product__name', 'product__id','product__description']
    filterset_fields=['product__price','is_available','product__company__name']

    @extend_schema(
        summary="دریافت موجودی فروشگاه",
        description="دریافت لیست موجودی فروشگاه با قابلیت فیلتر و جستجو",
        tags=['فروشگاه'],
        parameters=[
            OpenApiParameter(
                name='is_available',
                description='فقط کالاهای موجود',
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name='search',
                description='جستجو در نام محصول',
                required=False,
                type=str
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=StoreSerializer(many=True),
                description='لیست موجودی فروشگاه دریافت شد'
            ),
            401: OpenApiResponse(description='احراز هویت نشده'),
            403: OpenApiResponse(description='دسترسی غیرمجاز'),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class UpdatedInformationViewSet(ModelViewSet):
    """مدیریت تاریخچه تغییرات سیستم
    
    این ViewSet فقط عملیات مشاهده (GET) را برای تاریخچه تغییرات ارائه می‌دهد."""
    serializer_class=UpdatedInformationSerializer
    queryset=UpdatedInformationModel.objects.all().select_related('user')
    permission_classes=[IsAuthenticated,UpdatedInformationPermission]
    http_method_names = ['get']
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields=['create_dt']
    search_fields=['text']
    filterset_fields=['user__username', 'action_type', 'create_dt']
