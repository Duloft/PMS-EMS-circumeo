from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_page, name='home'),
    path('main-dashboard/', views.main_dashboard, name='main_dashboard'),
    path('tenant-dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    
]
