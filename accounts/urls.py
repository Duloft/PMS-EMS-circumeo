from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .import views

urlpatterns = [
    path('', views.test_home),
    path('account-type/', views.account_type, name="account_type"),
    path('sign-up/', views.user_signup, name="signup"),
    path('sign-in/', views.user_signin, name="signin"),
    path('sign-out/', views.signout_user, name="signout"),
    # url for account activation
    path('activate-account/<uidb64>/<token>/', views.activate, name='activate'),
    # social auth url
    path('social-auth/', include('social_django.urls', namespace='social')),
    
    path('password-reset/', views.password_reset_view, name="password_reset"),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_cofirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    
    path('update-sso-profile/', views.profile_update_sso, name="profile_update_sso" ),
    path('update-client-profile/', views.update_client_profile, name="update_client_profile" ),
    path('update-tenant-profile/', views.update_tenant_profile, name="update_tenant_profile" ),
    path('client-profile/', views.client_profile_page, name="client_profile"),
    path('tenant-profile/', views.tenant_profile_page, name='tenant_profile'),
    path('profile/', views.profile_page, name="profile_page"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)