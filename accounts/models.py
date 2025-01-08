from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from datetime import timedelta
import secrets
import importlib


paystack = importlib.import_module('payment_track.paystack')
# Create your models here.


class CustomUser(AbstractUser):
    ADMIN = 'client_admin'
    TENANT = 'tenant'
    
    USER_TYPE_CHOICES = (
        (ADMIN, 'Admin'),
        (TENANT, 'Tenant'),
    )
    email = models.EmailField("email address", unique=True, help_text="Required.",
        error_messages={
            "unique": "A user with that email already exists.",
        },)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default=TENANT)
    
    def is_admin(self):
        return self.user_type == self.ADMIN

    def is_client_user(self):
        return self.user_type == self.CLIENT_USER

    def is_tenant(self):
        return self.user_type == self.TENANT

    def __str__(self):
        return f"{self.username} ({self.email})"


class Token(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='auth_token')
    key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default= now() + timedelta(days=3)) 

    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return now() > self.expires_at

class ClientAccountProfile(models.Model):
    Account_Type = (
        ('Estate Management Company', 'Estate Management Company'),
        ('Property Management Company', 'Property Management Company'),
        ('LandLord', 'LandLord'),
        ('Property Manager', 'Property Manager'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="account_profile")
    account_type = models.CharField(("Account Type"),max_length=150, choices=Account_Type, blank=True, default='Estate Management Company')
    account_name = models.CharField(("Account Name"), max_length=150, blank=True)
    domain_name = models.CharField("Domain Name", help_text="realpro => realpro.duloft.com", max_length=150, blank=True, null=True)
    company_logo = models.FileField(upload_to='documents/company_logo/', null=True, blank=True)
    address = models.CharField(("Head Office Address"), max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    branch_address = models.CharField(("Branch Office Address"), max_length=200, blank=True, null=True)
    shared_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    recommended_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='client_referrals')
    is_deleted = models.BooleanField(("Delete"),default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.account_name} ({self.user.email})"
    
    def save(self, *args, **kwargs):
        if self.shared_id == "" or self.shared_id == None:
            shared_id = "DUA" + _generate_ref_code()
            length = len(shared_id)
            print(length)
            object_with_similar_ref = ClientAccountProfile.objects.filter(shared_id=shared_id)
            if object_with_similar_ref:
                shared_id = "DUA" + _generate_ref_code()
                length = len(shared_id)
                print(length)
            else:
                self.shared_id = shared_id
        super().save(*args, **kwargs)
    


def _generate_ref_code():
    import uuid
    ref_code = str(uuid.uuid4()).replace('-', '')[:16]
    return ref_code


class TenantProfile(models.Model):
    ID_Type = (
        ('nin', 'NIN'),
        ('vnin', 'vNIN'),
        ('voter\'s card', 'Voter\'s Card'),
        ('driver\'s license', 'Driver\'s License'),
        ('international passport', 'International Passport')
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="tenant_profile")
    shared_id = models.CharField(max_length=20, unique=True, blank=True, null=True) # SharedID or UniversalID
    recommended_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='tenant_referrals')
    id_type = models.CharField(max_length=50, choices=ID_Type, default='nin')
    valid_id_number = models.CharField(("Valid ID Number"), max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='documents/profilePhotos/', null=True, blank=True)
    marital_status = models.CharField("Marital Status", max_length=50, choices=(('single', 'Single'), ('married', 'Married')))
    job = models.CharField("Job Title", max_length=50, null=True, blank=True)
    monthly_income = models.CharField(max_length=50, null=True, blank=True)
    employer_name = models.CharField("Company Name/Employer Name", max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.user.username} ({self.user.email})"
    
    def save(self, *args, **kwargs):
        if self.shared_id == "" or self.shared_id == None:
            shared_id = "DUT" + _generate_ref_code()
            length = len(shared_id)
            print(length)
            object_with_similar_ref = TenantProfile.objects.filter(shared_id=shared_id)
            if object_with_similar_ref:
                shared_id = "DUT" + _generate_ref_code()
                length = len(shared_id)
                print(length)
            else:
                self.shared_id = shared_id
        super().save(*args, **kwargs)
    

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=25)
    no_users = models.CharField(max_length=10)
    amount = models.CharField(max_length=25, blank = True, null = True)
    no_properties = models.CharField(max_length=10, blank = True, null = True)
    duration_in_days = models.IntegerField(default=30)  # Subscription period in days
    no_units = models.CharField(max_length=20, blank=True, null=True)
    
    created_on = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return str(self.name)
    
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)


class Subscription(models.Model):
    """ training and data migration setup fee can be a separate service that is if there want their pay for it.
    Create a models for it and attach it the subscription models.
    """
    DurPlans = (
        ('1', '1 Month'),
        ('6', '6 Months'),
        ('12', '12 Months'),
        ('24', '24 Months')
    )
    company = models.OneToOneField(ClientAccountProfile, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    durations_plan = models.CharField("Durations Of Plan", max_length=10, choices=DurPlans)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True)
    verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('-start_date',)
    
    def __str__(self) -> str:
        return f"{self.plan}  X {self.durations_plan} month(s)."
    
    def save(self, *args, **kwargs):
        if self.start_date and not self.end_date:
            if hasattr(self.plan, 'duration_in_days') and self.plan.duration_in_days >= 30:
                subscription_duration = self.plan.duration_in_days * int(self.durations_plan)
            else:
                subscription_duration = 30 * int(self.durations_plan)  # Fallback to default 30 days
            self.end_date = self.start_date + timedelta(days=subscription_duration)
        super().save(*args, **kwargs)
    
    
    def is_active(self):
        try:
            return now().date() < self.end_date
        except:
            return True
    
    def validate_amount(self):
        return (float(self.amount)) * 100
        
    
    def verify_payment(self):
        print(settings.PAY_SECRET_KEY, "keys")
        print("======================================")
        paystack = paystack.PayStack(settings.PAY_SECRET_KEY)
        print(paystack.verify_payment(self.reference_id))
        try:
            status, result = paystack.verify_payment(self.reference_id)
            
        except:
            status, message, meta, type_, code = paystack.verify_payment(self.reference_id)
            
        
        if status is True:
            if result['amount'] / 100 == (float(self.amount)):
                self.verified = True
            else:
                self.verified = False
            self.save()
            
        if self.verified:
            return True
        return False


    