import secrets
from django.conf import settings
from django.db import models

# Create your models here.
User = settings.AUTH_USER_MODEL


class MaintenanceRequest(models.Model):
    STATE = (
        ('Pending', 'Pending'), 
        ('Denied', 'Denied'), 
        ('Approved', 'Approved')
    )
    PRIORITY = (
        ('Low', 'Low'), 
        ('Medium', 'Medium'), 
        ('High', 'High')
    )
    STATUS = (
        ('Open', 'Open'), 
        ('In Progress', 'In Progress'), 
        ('Completed', 'Completed')
    )
    
    request_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    property_unique_id = models.UUIDField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    state = models.CharField(max_length=50, choices=STATE, default="Pending")  # E.g., Low, Medium, High
    priority = models.CharField(max_length=50, choices=PRIORITY, default='Medium')  # E.g., Low, Medium, High
    status = models.CharField(max_length=50, choices=STATUS, default='Open')  # E.g., Open, In Progress, Completed
    request_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        while not self.request_id:
            request_id = secrets.token_hex(8)
            if not MaintenanceRequest.objects.filter(request_id=request_id).exists():
                self.request_id = request_id

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Maintenance Request"
        verbose_name_plural = "Maintenance Requests"
        indexes = [
            models.Index(fields=['property_unique_id']),
            models.Index(fields=['request_by']),
        ]



class MaintenanceTask(models.Model):
    task_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    completion_status = models.CharField(max_length=50, choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')])  # E.g., Not Started, In Progress, Completed
    assigned_technician = models.ForeignKey('client_user.ClientUsers', on_delete=models.SET_NULL , null=True)
    costs = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_assigned = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    materials_used = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        while not self.task_id:
            task_id = secrets.token_hex(8)
            if not MaintenanceTask.objects.filter(task_id=task_id).exists():
                self.task_id = task_id

        super().save(*args, **kwargs)