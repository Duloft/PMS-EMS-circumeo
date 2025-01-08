from django.core.management import call_command
from django.db.models.signals import post_save
from django.http import HttpRequest
from django.dispatch import receiver
from .models import CustomUser, ClientAccountProfile, TenantProfile
from .tasks import create_schema_migrate



@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created,*args, **kwargs):
    """creates a profile for either the client or tenant that just registered.

    Args:
        sender (_type_): _description_
        instance (_type_): _description_
        created (_type_): _description_
    """
    if created:
        print('profile created...')
        if not instance.is_active:
            user = instance
            
            if user.user_type == CustomUser.ADMIN:
                ClientAccountProfile.objects.create(user=user)
            elif user.user_type == CustomUser.TENANT:
                TenantProfile.objects.create(user=user)

@receiver(post_save, sender=ClientAccountProfile)
def create_domain(sender, instance, created,*args, **kwargs):
    """create the domain name and schema name for the client, that just registered.

    Args:
        sender (_type_): _description_
        instance (_type_): _description_
        created (_type_): _description_
    """
    if not created:  # Runs when ClientAccountProfile is updated
        create_schema_migrate.delay(instance.id)