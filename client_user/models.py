from django.db import models


class ClientUsers(models.Model):
    MANAGER = 'property_manager'
    AGENT = 'leasing_agent'
    ACCOUNTANT = 'accountant'
    SUPERVISOR = 'maintenance_supervisor'
    TECHNICIAN = 'maintenance_technician'
    
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, null=True, related_name='client_users')
    tenant = models.ForeignKey('core.Client', on_delete=models.CASCADE, help_text="The tenants this user belongs to.", related_name="clientusers_set", null=True)
    role = models.CharField(
        max_length=50,
        choices=(
            (MANAGER, 'Property Manager'),
            (ACCOUNTANT, 'Accountant'),
            (AGENT, 'Leasing Agent'),
            (SUPERVISOR, 'Maintenance Supervisor'),
            (TECHNICIAN, 'Maintenance Technician'),
        ),
        default=""
    )
    # uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}  ({self.role.name if self.role else 'No Role'})"

    def get_tenants(self):
        """Return all tenants this employee belongs to."""
        return self.tenant
    
    def has_permission(self, permission_codename):
        if self.role:
            return self.role.permissions.filter(codename=permission_codename).exists()
        else:
            return False
    
    class Meta:
        verbose_name = "ClientUsers"
        verbose_name_plural = "ClientUsers"