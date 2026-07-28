from django.urls import path , include
from . import views
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('warehouse',views.WarehouseViewSet,'warehouse')
router.register('waste',views.WasteViewSet, 'waste')
router.register('returns',views.ReturnsViewSet, 'returns')
router.register('transfers',views.TransfersViewSet, 'transfers')
router.register('',views.StoreViewSet, 'store')
router.register('updated_information',views.UpdatedInformationViewSet, 'updated_information')
urlpatterns = [
    path('',include(router.urls)),
]
