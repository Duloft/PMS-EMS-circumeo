from django.conf import settings

def routing_context(request):
    return {
        'USE_SUBDOMAIN_ROUTING': settings.USE_SUBDOMAIN_ROUTING
    }