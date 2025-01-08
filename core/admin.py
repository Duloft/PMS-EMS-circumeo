from django.contrib import admin
from .models import Client, Domain

from .models import Client, Domain

# Register your models here.

class ClientAdminSite(admin.AdminSite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register(Client)
        self.register(Domain)
    
    
client_admin_site = ClientAdminSite(name="client_admin_site")

