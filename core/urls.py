from django.urls import path
from . import views, admin as core_admin


urlpatterns = [
    path("home/", views.home, name="home"),
    path("", views.landing_page, name='landing'),
    path("testing/", views.landing_page_2, name='testing_landing'),
    path('client-back-in/', core_admin.client_admin_site.urls)
    
]

