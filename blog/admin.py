from django.contrib import admin
from .models import (Post, Comment, Category)

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_modified', 'date_added')
    list_filter = ('last_modified', 'date_added')
    def __str__(self):
        self.title
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'post_id', 'date_added')
    list_filter = ('post', 'user', 'date_added')
    def __str__(self):
        f'Comment by {self.user} on {self.post.title}'

admin.site.register(Category)