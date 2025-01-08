from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from froala_editor.fields import FroalaField

# Create your models here.

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, editable=False)  

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        
        self.slug = f"{slugify(self.name)}-{self.pk}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, editable=False)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    image_copyright = models.CharField(max_length=155, null=True, blank=True)
    content = FroalaField()
    category = models.ManyToManyField(Category, related_name='posts')
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        
        self.slug = f"{slugify(self.title)}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = FroalaField()
    date_added = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f'Comment by {self.user} on {self.post.title}'


