from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from .models import (Post, Comment)
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your views here.

def blog_posts(request):
    # get all the posts with pagination of 20
    p = Paginator(Post.objects.all(), 20)
    page = request.GET.get('page')
    posts = p.get_page(page)
    
    template = 'blog/home.html'
    context = {'posts': posts}
    return render (request, template, context)

def post_details(request, slug):
    # get a particular post by slug
    post = Post.objects.get(slug=slug)
    
    # get all the comments on that particular post
    post_comments = Comment.objects.filter(post = post)
    
    template = 'blog/post_detail.html'
    context = {'post': post, 'post_comments': post_comments}
    return render (request, template, context)

def add_comment(request, post_id):
    if request.method == "POST":
        comment_content = request.POST.get('comment')
        # if the comment box is not empty create a comment
        if comment_content:
            post = Post.objects.get(id=post_id)
            user = request.user
            Comment.objects.create(
                user = user,
                post = post,
                content = comment_content
            )

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))