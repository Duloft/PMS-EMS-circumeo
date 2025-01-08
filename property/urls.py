from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('create/', views.add_property_view, name='add_property'),
    path('<int:pk>/update/', views.update_property_view, name='update_property'),
    path('<int:pk>/delete/', views.delete_property, name='delete_property'),
    
    path('type/', views.get_property_type, name='property_type_list'),
    path('type/create/', views.create_property_type, name='add_property_type'),
    path('type/<int:pk>/update/', views.update_property_type, name='update_property_type'),
    path('type/<int:pk>/delete/', views.delete_property_type, name='delete_property_type'),
    
    path('listing/', views.property_listing_list, name='property_listing'),
    path('listing/<int:pk>/create/', views.add_property_listing, name='add_property_listing'),
    path('listing/<int:pk>/update/', views.update_property_listing, name='update_property_listing'),
    path('listing/<int:pk>/delete/', views.property_listing_delete, name='property_listing_delete'),
    path('listing/<int:pk>/images/', views.property_images, name='property_listing_images'),
    
    path('units/', views.unit_list, name='unit_list'),
    path('units/create/', views.create_unit, name='add_unit'),
    path('units/<int:pk>/update/', views.update_unit_view, name='unit_update'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),
    
    path('unit-listings/', views.unit_listing_list, name='unit_listing_list'),
    path('unit-listings/create/', views.add_unit_listing, name='add_unit_listing'),
    path('unit-listings/<int:pk>/update/', views.update_unit_listing, name='update_unit_listing'),
    path('unit-listings/<int:pk>/delete/', views.unit_listing_delete, name='unit_listing_delete'),
]
