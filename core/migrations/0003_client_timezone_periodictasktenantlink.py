# Generated by Django 5.1.4 on 2025-01-07 09:50

import django.db.models.deletion
import timezone_field.fields
from django.db import migrations, models
from django.conf import settings

def set_default_timezone(apps, schema_editor):
    Client = apps.get_model('core', 'Client')
    default_timezone = getattr(settings, 'TIME_ZONE', 'UTC')
    Client.objects.all().update(timezone=default_timezone)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_feedback'),
        ('django_celery_beat', '0019_alter_periodictasks_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default='UTC'),
        ),
        migrations.CreateModel(
            name='PeriodicTaskTenantLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('use_tenant_timezone', models.BooleanField(default=False)),
                ('periodic_task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='periodic_task_tenant_link', to='django_celery_beat.periodictask')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='periodic_task_tenant_links', to='core.client')),
            ],
            options={
                'abstract': False,
            },
        ),
        
        migrations.RunPython(set_default_timezone),
    ]
