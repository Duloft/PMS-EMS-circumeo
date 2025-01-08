import json
from django.apps import apps
from django.db import connection
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ClientUsers
from .utils import query_schema_all


Client = apps.get_model('core', 'Client')
CustomUser = apps.get_model('accounts', 'CustomUser')

# Create your views here.

@login_required
def client_users_list(request):
    """List view for all client users"""
    
    # Get search parameter from URL query string
    search_query = request.GET.get('search', '')
    
    # Start with all users
    users = ClientUsers.objects.all()
    
    # Apply search filter if search_query exists
    if search_query:
        users = users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(role__icontains=search_query) |
            Q(tenant__name__icontains=search_query)
        )
    
    # Order users by creation date (newest first)
    users = users.order_by('-created_at')
    
    # Paginate results
    items_per_page = 10
    paginator = Paginator(users, items_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Prepare context for template
    context = {
        'users': page_obj,  # Paginated user objects
        'total_users': users.count(),  # Total number of users
        'search_query': search_query,  # Current search term
        'title': 'Employee List',
        'page_obj': page_obj,  # Pagination object
    }
    
    return render(request, 'list.html', context)

@login_required
def client_user_detail(request, pk):
    """Detail view for a specific client user"""
    user = get_object_or_404(ClientUsers, pk=pk)
    context = {
        'user': user,
        'title': f'Employee Details - {user.user.username}'
    }
    return render(request, 'detail.html', context)

@login_required
def client_user_create(request):
    """Create view for new client user"""
    if request.method == 'POST':
        # Get form data
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        tenant = request.tenant
        phone_number = request.POST.get('phone_number')
        is_admin = request.POST.get('is_admin') == 'on'
        
        try:
            # Create CustomUser first
            custom_user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=firstname,
                last_name=lastname,
            )
            
            ClientUsers.objects.create(
                user=custom_user,
                tenant=tenant,
                role=role,
                phone_number=phone_number,
                is_admin=is_admin
            )
            
            messages.success(request, 'Employee created successfully!')
            return redirect('client_users_list')
            
        except Exception as e:
            messages.error(request, f'Error creating employee: {str(e)}')
    
    # GET request - display form
    # tenants = Client.objects.all()
    context = {
        # 'tenants': tenants,
        'roles': [
            ('property_manager', 'Property Manager'),
            ('accountant', 'Accountant'),
            ('leasing_agent', 'Leasing Agent'),
            ('maintenance_supervisor', 'Maintenance Supervisor'),
            ('maintenance_technician', 'Maintenance Technician'),
        ],
        'title': 'Create New Employee'
    }
    return render(request, 'create.html', context)

@login_required
def client_user_update(request, pk):
    """Update view for existing client user"""
    client_user = get_object_or_404(ClientUsers, pk=pk)
    
    if request.method == 'POST':
        # Get form data
        role = request.POST.get('role')
        # tenant_id = request.POST.get('tenant')
        phone_number = request.POST.get('phone_number')
        is_admin = request.POST.get('is_admin') == 'on'
        
        try:
            # Update ClientUser
            client_user.role = role
            # client_user.tenant = Client.objects.get(id=tenant_id) if tenant_id else None
            client_user.phone_number = phone_number
            client_user.is_admin = is_admin
            client_user.save()
            
            messages.success(request, 'Employee updated successfully!')
            return redirect('client_users_list')
            
        except Exception as e:
            messages.error(request, f'Error updating employee: {str(e)}')
    
    # GET request - display form
    # tenants = Client.objects.all()
    context = {
        'client_user': client_user,
        # 'tenants': tenants,
        'roles': [
            ('property_manager', 'Property Manager'),
            ('accountant', 'Accountant'),
            ('leasing_agent', 'Leasing Agent'),
            ('maintenance_supervisor', 'Maintenance Supervisor'),
            ('maintenance_technician', 'Maintenance Technician'),
        ],
        'title': f'Update Employee - {client_user.user.username}'
    }
    return render(request, 'update.html', context)

@login_required
def client_user_delete(request, pk):
    """Delete view for client user"""
    client_user = get_object_or_404(ClientUsers, pk=pk)
    
    if request.method == 'POST':
        try:
            # Delete associated CustomUser (will cascade delete ClientUser)
            client_user.user.delete()
            messages.success(request, 'Employee deleted successfully!')
            return redirect('client_users_list')
        except Exception as e:
            messages.error(request, f'Error deleting employee: {str(e)}')
            
    context = {
        'client_user': client_user,
        'title': f'Delete Employee - {client_user.user.username}'
    }
    return render(request, 'client_users/delete.html', context)