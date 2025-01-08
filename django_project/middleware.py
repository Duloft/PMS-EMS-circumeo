from django.db import connection
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
from django_tenants.middleware.main import TenantMainMiddleware
from core.models import Client, Domain
from accounts.models import Token
from django.http import Http404
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

class CustomTenantMiddleware(TenantMainMiddleware):
    def process_request(self, request):
        # Getting the host or domain
        host = request.get_host().lower()
        base_domain = host.split(':')[0]  # Strip out any port number

        print(f"Processing request for host: {host}")
        print(f"Processing request for base domain: {base_domain}")

        # Skip tenant processing for accounts and blog subdomains
        if base_domain.startswith(('accounts.', 'blog.')):
            print(f"Skipping tenant processing for {base_domain}")
            return self.get_response(request)

        try:
            # Get the public schema (should always exist)
            public_tenant = Client.objects.get(schema_name='public')
            print(f"Public tenant domain: {public_tenant.domains.first().domain}")

            # Extract the subdomain
            request_subdomain = base_domain.split('.')[0]
            print(f"Request subdomain: {request_subdomain}")

            # Find the matching tenant
            try:
                tenant = Client.objects.get(schema_name=request_subdomain)
                print(f"Tenant found: {tenant.schema_name}")

                # Explicitly set the tenant on the request
                request.tenant = tenant
                request.urlconf = 'property_manager.tenant_urls'  # Set tenant-specific URLconf if needed

                # Call the parent method to complete tenant processing
                return super().process_request(request)

            except Client.DoesNotExist:
                # Handle main domain or default case
                if base_domain.startswith(('app.', '')):
                    print(f"Setting public tenant for {base_domain}")
                    request.tenant = public_tenant
                    request.urlconf = 'property_manager.public_urls'
                    return super().process_request(request)

                print(f"Subdomain '{request_subdomain}' not matched. Raising Http404.")
                raise Http404("No tenant for this subdomain")

        except Client.DoesNotExist:
            print("Public tenant not found in the database.")
            raise Http404("Public tenant not found")

        except Exception as e:
            # Catch any other exceptions that occur and log them
            print(f"Unexpected error during tenant processing for {base_domain}: {e}")
            raise Http404("Error during tenant processing")

class SubfolderTenantMiddleware(TenantMainMiddleware):
    """
    Custom middleware to handle tenant routing via subfolders with prefix validation.
    
    This middleware extends the default django-tenants middleware to support
    tenant routing through URL subfolders with a specific prefix.
    
    Example URL structure:
    - https://example.com/t/tenant1/admin/
    - https://example.com/t/tenant2/dashboard/
    """
    
    def determine_tenant_from_request(self, request):
        """
        Determine the tenant based on the URL segment after the tenant prefix.
        
        :param request: The incoming HTTP request
        :return: Tenant object or None
        """
        # Get the tenant subfolder prefix from settings (default to 't' if not set)
        TENANT_SUBFOLDER_PREFIX = getattr(settings, 'TENANT_SUBFOLDER_PREFIX', 't')
        
        # Split the path and remove empty segments
        path_parts = [part for part in request.path.strip('/').split('/') if part]
        
        # Validate the path starts with the tenant prefix
        if not path_parts or path_parts[0] != TENANT_SUBFOLDER_PREFIX:
            return None
        
        # Ensure there's a tenant identifier after the prefix
        if len(path_parts) < 2:
            return None
        
        # Get the tenant identifier (second segment)
        tenant_identifier = path_parts[1]
        
        try:
            # Attempt to find tenant by schema name
            Tenant = get_tenant_model()
            tenant = Tenant.objects.get(schema_name=tenant_identifier)
            return tenant
        except Tenant.DoesNotExist:
            return None
    
    def process_request(self, request):
        """
        Process the incoming request and set the tenant context.
        
        :param request: The incoming HTTP request
        """
        print('connection:', connection.schema_name)
        # Get the tenant subfolder prefix from settings (default to 't' if not set)
        TENANT_SUBFOLDER_PREFIX = getattr(settings, 'TENANT_SUBFOLDER_PREFIX', 't')
        PUBLIC_SCHEMA_NAME = getattr(settings, 'PUBLIC_SCHEMA_NAME', 'public')
        
        # Determine the tenant from the request
        tenant = self.determine_tenant_from_request(request)
        print(tenant)
        if not tenant:
            # If no tenant is found and it's a tenant-prefixed route, raise 404
            path_parts = [part for part in request.path.strip('/').split('/') if part]
            if path_parts and path_parts[0] == TENANT_SUBFOLDER_PREFIX:
                raise Http404("No tenant found for this subdomain")
            else:
                # If not a tenant route, ensure public schema is set
                connection.set_schema_to_public()
                return super().process_request(request)
        
        if tenant:
            # Set the tenant on the request
            request.tenant = tenant
            connection.set_tenant(request.tenant)
            
            # Set the schema
            connection.set_schema(tenant.schema_name)
            print('connection:', connection.schema_name)
            
            # Continue with standard tenant middleware processing
            return super().process_request(request)




# Optional: Middleware to modify URLs to include tenant subfolder
class TenantSubfolderURLRewriteMiddleware:
    """
    Middleware to rewrite URLs to include the tenant subfolder.
    
    This middleware helps generate URLs that include the tenant's schema name
    as a subfolder.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Attach a method to the request to generate tenant-aware URLs
        def tenant_url(viewname, *args, **kwargs):
            from django.urls import reverse
            
            # Get the current tenant's schema name
            tenant_prefix = request.tenant.schema_name if hasattr(request, 'tenant') else ''
            
            # Generate the base URL
            base_url = reverse(viewname, *args, **kwargs)
            
            # Prepend the tenant subfolder if exists
            if tenant_prefix:
                base_url = f'/{tenant_prefix}{base_url}'
            
            return base_url
        
        # Add the method to the request
        request.tenant_url = tenant_url
        
        response = self.get_response(request)
        return response

class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token_key = request.META.get('HTTP_AUTHORIZATION')
        if token_key:
            try:
                token = Token.objects.get(key=token_key)
                request.user = token.user
            except Token.DoesNotExist:
                request.user = None
        else:
            request.user = None
