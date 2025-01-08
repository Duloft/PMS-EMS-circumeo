from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
import secrets

# Create your models here.


class LeaseManagement(models.Model):
    LEASE_FREQUENCY = (
        ('yearly', 'Yearly'),
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
    )
    transaction_id = models.CharField(max_length=50, unique=True, blank=True)
    tenant_name = models.CharField(max_length=150)
    tenant_shared_id = models.CharField(max_length=20)
    unit_address = models.CharField(max_length=100)
    unit_unique_id = models.CharField(max_length=50)
    rent_amount = models.DecimalField(max_digits=15, decimal_places=2)
    lease_frequency = models.CharField(max_length=50, choices=LEASE_FREQUENCY,default='yearly')
    term_lease = models.IntegerField(default=3)
    start_date = models.DateField()
    end_date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.start_date:
            self.end_date = self.start_date + relativedelta(years=self.term_lease)
        while not self.transaction_id:
            transaction_id = secrets.token_hex(12)
            object_with_similar_ref = LeaseManagement.objects.filter(transaction_id=transaction_id)
            if object_with_similar_ref:
                self.transaction_id = secrets.token_hex(12)
            else:
                self.transaction_id = transaction_id        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tenant_name} {self.start_date} {self.end_date}"

    def is_active(self):
        return now().date() < self.end_date
    

class LeaseSpecificationSettings(models.Model):
    term_lease = models.IntegerField(default=3)
    state_lease = models.CharField(max_length=50)
    caution_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    
    def __str__(self) -> str:
        return self.state_lease


class LeaseDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('LEASE_AGREEMENT', 'Lease Agreement'),
        ('ADDENDUM', 'Lease Addendum'),
        ('INSPECTION', 'Property Inspection'),
        ('TERMINATION', 'Lease Termination'),
        ('OTHER', 'Other Document'),
    ]

    lease = models.ForeignKey(LeaseManagement, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='lease_documents/')
    uploaded_by = models.ForeignKey("client_user.ClientUsers", on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    is_signed = models.BooleanField(default=False)
    signature_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.lease}"

class LeaseTerms(models.Model):
    lease = models.OneToOneField(LeaseManagement, on_delete=models.CASCADE, related_name='terms')
    pets_allowed = models.BooleanField(default=False)
    pet_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    utilities_included = models.BooleanField(default=False)
    maintenance_terms = models.TextField()
    parking_spots = models.IntegerField(default=0)
    special_conditions = models.TextField(blank=True)
    notice_period_days = models.IntegerField(default=30)
    late_fee_percentage = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Terms for {self.lease}"

class LeaseRenewal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]

    lease = models.ForeignKey(LeaseManagement, on_delete=models.CASCADE, related_name='renewals')
    new_start_date = models.DateField()
    new_end_date = models.DateField()
    new_monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name='requested_renewals')
    approved_by = models.ForeignKey("client_user.ClientUsers", on_delete=models.SET_NULL, null=True, related_name='approved_renewals')
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Renewal for {self.lease} - {self.status}"