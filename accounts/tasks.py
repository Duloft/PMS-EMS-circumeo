from django.core.management import call_command
from .models import CustomUser, ClientAccountProfile, TenantProfile
from django.apps import apps
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# from property_manager.celery import app  # Not needed now create a new tasks file for it.
from celery import shared_task


domain_model = apps.get_model('core', 'Domain')
client_model = apps.get_model('core', 'Client')

@shared_task
def send_email(subject: str, template_mail_name: str, template_mail_context: dict, email_list: list):
    """For sending mail to our users

    Args:
        subject (str): subject of the mail
        template_mail_name (str): the template for sending the mail
        template_mail_context (dict): the context for the mail template
        email_list (list): receiver email addresses
    """
    html_content = render_to_string(template_mail_name,template_mail_context)
    plain_message = strip_tags(html_content)  
    
    email = EmailMultiAlternatives(subject, plain_message, settings.EMAIL_HOST_USER, email_list)
    email.attach_alternative(html_content, "text/html")
    email.send()


@shared_task
def create_schema_migrate(instance_id):
    instance = ClientAccountProfile.objects.get(id=instance_id)
    if instance.domain_name:
        print('domain created...')
        schema_name = ''.join(instance.account_name.lower().split())
        domain_name = f"{instance.domain_name.lower()}.{settings.BASE_DOMAIN_NAME}" 
        if not client_model.objects.filter(schema_name=schema_name).exists() and not domain_model.objects.filter(domain=domain_name).exists():
            client = client_model(
                schema_name=schema_name,
                name=instance.account_name,
                is_active=True
            )
            client.save()
            
            domain = domain_model()
            domain.domain = domain_name 
            domain.tenant = client
            domain.is_primary = True
            domain.save()   
            

            # runs manage.py migrate_schemas
            call_command('migrate_schemas', schema_name=client.schema_name)