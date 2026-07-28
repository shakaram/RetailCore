
from django.contrib import admin
from django.urls import path , include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf.urls.static import static
from . import settings


urlpatterns = [
    #admin
    path('admin/', admin.site.urls),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    #auth
    path('api/auth/', include('auth_kit.urls')),
    #my urls
    path('api/AccountsViewSet/', include('accounts.urls')),
    #path('api/store/', include('store.urls')),
    path('api/', include('products.urls')),
    path('api/store/', include('store.urls')),
]+ static(settings.MEDIA_URL ,document_root = settings.MEDIA_ROOT )
