from django.urls import path
from . import views

urlpatterns = [
    path('client-users/', views.client_users_list, name='client_users_list'),
    path('client-users/create/', views.client_user_create, name='client_user_create'),
    path('client-users/<int:pk>/', views.client_user_detail, name='client_user_detail'),
    path('client-users/<int:pk>/update/', views.client_user_update, name='client_user_update'),
    path('client-users/<int:pk>/delete/', views.client_user_delete, name='client_user_delete'),
]