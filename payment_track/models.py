import secrets
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.db.models import Sum

from .paystack import PayStack

# Create your models here.

User = settings.AUTH_USER_MODEL


from django.db.models import Sum
from django.utils.timezone import now

class PaymentManager(models.Manager):
    def monthly_revenue(self):
        return self.filter(verified=True, payment_date__month=now().month).aggregate(Sum('amount'))['amount__sum'] or 0

    def yearly_revenue(self):
        return self.filter(verified=True, payment_date__year=now().year).aggregate(Sum('amount'))['amount__sum'] or 0

    def total_revenue(self):
        return self.filter(verified=True).aggregate(Sum('amount'))['amount__sum'] or 0

    def total_commission(self):
        return self.filter(verified=True).aggregate(Sum('commission'))['commission__sum'] or 0



class RecordManager(models.Manager):
    def monthly_total(self):
        return self.filter(date_created__month=now().month, payment_status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0

    def yearly_total(self):
        return self.filter(date_created__year=now().year, payment_status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0

    def total(self):
        return self.filter(payment_status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    def total_revenue_record_fees_type(self, fees_type='Sanitation'):
        return self.filter(payment_status='Paid', fees_type=fees_type).aggregate(Sum('amount'))['amount__sum'] or 0
        


class Payment(models.Model):
    "The payout uses the same ref id as payment"
    reference_id =  models.CharField(max_length=100, unique=True, blank=True)
    property_unique_id = models.UUIDField()
    depositor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_depositors") # use tenant
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_recipients") # use account
    email = models.EmailField()
    description = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    objects = PaymentManager()
    class Meta:
        ordering = ('-payment_date',)

    def __str__(self):
        return f"Payment: {self.amount}"
    
    
    def save(self, *args, **kwargs):
        while not self.reference_id:
            reference_id = 'd'+ secrets.token_urlsafe(25)
            object_with_similar_ref = Payment.objects.filter(reference_id=reference_id)
            if object_with_similar_ref:
                self.reference_id = 'd'+ secrets.token_urlsafe(25)
            else:
                self.reference_id = reference_id        
        if not self.property_unique_id:
            print('You are not allowed to leave property_unique_id empty')
        super().save(*args, **kwargs)
       
    
    def final_amount(self):
        return float(self.amount) + float(self.commission)
    
    def commission_charge(self):
        return float(self.amount) * 0.05
    
    def legal_fee(self):
        return float(self.amount) * 0.1
    
    
    def transaction_charge(self):
        charge = float(self.amount) * 0.017
        if charge > 3000:
            charge = 3000
        else:
            charge = charge
        return float(charge)
    
    
    def validate_amount(self):
        return (float(self.amount) + float(self.commission)) * 100
    
    def verify_payment(self):
        paystack = PayStack(settings.PAY_SECRET_KEY)
        try:
            status, result = paystack.verify_payment(self.reference_id)
        except:
            status, message, meta, type_, code =  paystack.verify_payment(self.reference_id)
        
        if status is True:
            if result['amount'] / 100 == (float(self.amount) + float(self.commission)):
                self.verified = True
            else:
                self.verified = False
            self.save()
            
        if self.verified:
            return True
        return False
    
    def paid_amount(self):
        return float(self.amount) * 0.99


class Payout(models.Model):
    "The payout uses the same ref id as payment"
    reference_id =  models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payout_recipients")# use accounts
    bank_detail = models.ForeignKey('BankDetail', on_delete=models.SET_NULL, null=True, blank=True)
    # recipient_code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    objects = PaymentManager()
    
    class Meta:
        ordering = ('-payment_date',)
    
    def __str__(self):
        return f"Payment: {self.amount}"
    
    
class ExpenseRecord(models.Model):
    """is designed to track outflows for the PMS owner

    Args:
        models (_type_): _description_
    """
    FeesType = [
        ('Insurance', 'Insurance'),
        ('Legal', 'Legal'),
        ('Security', 'Security'),
        ('Sanitation', 'Sanitation'),
        ('Taxes', 'Taxes'),
        ('Water', 'Water'),
        ('Waste Disposal', 'Waste Disposal'),
        ('Utilities', 'Utilities'),
    ]
    transaction_id = models.CharField(max_length=50, unique=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payee = models.CharField(max_length=50, help_text="The one who receives money from the payer")
    fees_type = models.CharField(max_length=25, choices=FeesType, default='Sanitation')
    payment_status = models.CharField(max_length=25, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Paid')
    date = models.DateField()
    date_created = models.DateTimeField(auto_now_add=True)

    objects = RecordManager()
    
    def save(self, *args, **kwargs):
        while not self.transaction_id:
            transaction_id = secrets.token_hex(15)
            object_with_similar_ref = ExpenseRecord.objects.filter(transaction_id=transaction_id)
            if object_with_similar_ref:
                self.transaction_id = secrets.token_hex(15)
            else:
                self.transaction_id = transaction_id        
        super().save(*args, **kwargs)




class FeesRecord(models.Model):
    """tracks inflows from tenants to PMS owner.
    """
    FeesType = [
        ('General', 'General'),
        ('Security', 'Security'),
        ('Sanitation', 'Sanitation'),
        ('Water', 'Water'),
        ('Waste Disposal', 'Waste Disposal'),
        ('Utilities', 'Utilities'),
    ]
    
    transaction_id = models.CharField(max_length=50, unique=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payer = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, help_text="The name of the one who pays money to the payee")
    fees_type = models.CharField(max_length=25, choices=FeesType, default='Sanitation')
    property_name = models.ForeignKey("property.PropertyModel", on_delete=models.CASCADE, blank=True,  null=True)
    unit_name = models.CharField(max_length=50, blank=True, null=True)
    property_unique_id = models.UUIDField()
    payment_status = models.CharField(max_length=25, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')
    date = models.DateField("Date Due")
    date_created = models.DateTimeField(auto_now_add=True)

    objects = RecordManager()
    
    def save(self, *args, **kwargs):
        while not self.transaction_id:
            transaction_id = secrets.token_hex(15)
            object_with_similar_ref = FeesRecord.objects.filter(transaction_id=transaction_id)
            if object_with_similar_ref:
                self.transaction_id = secrets.token_hex(15)
            else:
                self.transaction_id = transaction_id        
        super().save(*args, **kwargs)
        
    
    def validate_amount(self):
        return (float(self.amount)) * 100

    def verify_payment(self):
        paystack = PayStack(settings.PAY_SECRET_KEY)
        try:
            status, result = paystack.verify_payment(self.transaction_id)
            
        except:
            status, message, meta, type_, code = paystack.verify_payment(self.transaction_id)
        
        
        if status is not False:
            if result['amount'] / 100 == (float(self.amount)):
                self.verified = True
            else:
                self.verified = False
            self.save()
        
        if self.verified:
            return True
        return False


class BankDetail(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="bank_details"
    )
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    swift_code = models.CharField(max_length=11, blank=True, null=True)  # For international transfers
    iban = models.CharField(max_length=34, blank=True, null=True)       # For international transfers
    currency = models.CharField(max_length=10, default="USD")           # Default currency
    is_primary = models.BooleanField(default=False)                     # Mark the primary withdrawal account
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_name} - {self.bank_name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure no other bank details for the user are marked as primary
            BankDetail.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)