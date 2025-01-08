from django_hosts import patterns, host


host_patterns = patterns(
    '', 
    host('', 'property_manager.public_urls', name='app'), # main domain
    host('blog', 'blog.urls', name='blog'), # blog subdomain
    host('accounts', 'accounts.urls', name='account'), # accounts subdomain
    host(r'(?P<subdomain_name>(?!accounts|blog)\w+)', 'property_manager.tenant_urls', name='tenant') # tenants subdomain by checking if is NOT "accounts" or "blog"
)