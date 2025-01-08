from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("core.urls"))
    
]

if not settings.USE_SUBDOMAIN_ROUTING:
    urlpatterns += [path('accounts/', include('accounts.urls')), path('blog/', include('blog.urls')), path('', include('property_manager.tenant_urls'))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)