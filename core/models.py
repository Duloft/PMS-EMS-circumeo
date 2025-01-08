from django.db import models

from django_tenants.models import TenantMixin, DomainMixin
from django_tenants_celery_beat.models import TenantTimezoneMixin, PeriodicTaskTenantLinkMixin


class Client(TenantTimezoneMixin, TenantMixin):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField()
    created_on = models.DateTimeField(auto_now_add=True)
    
    auto_create_schema = True
    auto_drop_schema = True
    

class Domain(DomainMixin):
    pass

class PeriodicTaskTenantLink(PeriodicTaskTenantLinkMixin):
    pass

class FeedBack(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_no = models.CharField("Phone Number", max_length=20)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    
    def __str__(self):
        return f"{self.name} {self.subject} ({self.email})"
