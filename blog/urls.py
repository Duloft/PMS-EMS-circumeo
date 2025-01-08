from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.blog_posts, name="posts"),
    path('post/<slug:slug>/', views.post_details, name="details"),  
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)