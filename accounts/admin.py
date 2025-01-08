from django.contrib import admin
from .models import CustomUser,ClientAccountProfile,TenantProfile, Subscription, SubscriptionPlan
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(ClientAccountProfile)
admin.site.register(TenantProfile)
admin.site.register(SubscriptionPlan)
admin.site.register(Subscription)