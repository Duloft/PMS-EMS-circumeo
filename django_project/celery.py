from tenant_schemas_celery.app import CeleryApp as TenantAwareCeleryApp
from celery.schedules import crontab
import os

from django.conf import settings

# Initialize the Celery app
app = TenantAwareCeleryApp('django_project')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

# Load settings from Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

# Debug task (optional)
@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


# Set beat schedule after ensuring settings are loaded
if settings.configured:
    from django_tenants_celery_beat.utils import generate_beat_schedule
    # Define beat schedule
    app.conf.beat_schedule = generate_beat_schedule({   
        "tenant_task": {
            "task": "your_app.tasks.some_task",  # Replace 'your_app' with your actual app name
            "schedule": crontab(minute=0, hour=12),
            # "schedule":60.0, # every 60 seconds
            "tenancy_options": {
                "public": False,
                "all_tenants": True,
                # "use_tenant_timezone": True,
            },
        },
        "public_task": {
            "task": "your_app.tasks.public_task",  # Replace 'your_app' with your actual app name
            "schedule": crontab(minute=0, hour=0),
            "tenancy_options": {
                "public": True,
                "all_tenants": False,
            },
        },
        "celery.backend_cleanup": {
            "task": "celery.backend_cleanup",
            "schedule": crontab(hour=4, minute=0),
            "options": {"expire_seconds": 12 * 3600},
            "tenancy_options": {
                "public": False,
                "all_tenants": True,
                "use_tenant_timezone": True,
            }
        },
    })
