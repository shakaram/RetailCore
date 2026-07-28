from django.urls import path , include
from . import views
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('products',views.ProductViewSet,'products')
router.register('company',views.CompanyViewSet, 'company')
router.register('sold',views.SoldViewSet, 'sold')
router.register('sold_item',views.SoldItemViewSet, 'sold_item')
router.register('category',views.CategoryViewSet, 'category')
router.register('images',views.ImageProductViewSet, 'images')
urlpatterns = [
    path('',include(router.urls)),
]
