from django.urls import reverse
from django.http import HttpResponseRedirect
from django_tenants.utils import schema_context
from django.shortcuts import render, redirect

# Home view to render the homepage template
def home(request):
    
    context = {
        # Add any context data if needed (for example, posts, categories, etc.)
    }
    return render(request, "core/homepage.html", context)

def landing_page(request):
    return render(request, 'core/landing.html')


def landing_page_2(request):
    return render(request, 'core/testing_page.html')

# Create your views here.
def switch_tenant(request, tenant_name):
    with schema_context(tenant_name):
        # Redirect to the admin homepage within the selected schema
        return redirect('/admin/')
