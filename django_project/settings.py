import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ow(!jkheczp!+n4j5^91p8cnyzwwqzr0lar6@i^kex54z$cqxk'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['.vercel.app', '.now.sh', '.circumeo-apps.net', '.duloft.com']

CSRF_TRUSTED_ORIGINS = [
    'https://*.d7k-adaptable-mendel.circumeo-apps.net'
    'https://*.property-manger.vercel.app',
    'https://*.duloft.com',
]

USE_SUBDOMAIN_ROUTING = True  

# Application Definition
SHARED_APPS = [
    'django_tenants',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-Party Apps
    'django_hosts',
    'honeypot',
    'froala_editor',
    'social_django',
    "django_celery_results",
    "django_celery_beat",
    "django_tenants_celery_beat",
    
    # Custom Apps
    'accounts.apps.AccountsConfig',
    'blog.apps.BlogConfig',
    'core.apps.CoreConfig',
    'client_user.apps.ClientUserConfig',
]

TENANT_APPS = [
    'dashboard.apps.DashboardConfig',
    'lease.apps.LeaseConfig',
    'property.apps.PropertyConfig',
    'maintenance_track.apps.MaintenanceTrackConfig',
    'payment_track.apps.PaymentTrackConfig',
    'visitor_track.apps.VisitorTrackConfig',
    'wallet_track.apps.WalletTrackConfig',
    
    "django_celery_results",
]

# Dynamically create INSTALLED_APPS
INSTALLED_APPS = SHARED_APPS + list(set(TENANT_APPS) - set(SHARED_APPS))

# Middleware Configuration
def _configure_middleware():
    """
    Dynamically configure middleware with special handling for subdomain routing.
    
    Ensures that django_hosts.middleware.HostsResponseMiddleware is the last middleware 
    when subdomain routing is enabled.
    """
    base_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'social_django.middleware.SocialAuthExceptionMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
    ]
    
    # Tenant-specific middleware
    if USE_SUBDOMAIN_ROUTING:
        tenant_middleware = [
            'django_project.middleware.CustomTenantMiddleware',
            'django_hosts.middleware.HostsRequestMiddleware',
        ] + base_middleware + [
            'django_hosts.middleware.HostsResponseMiddleware',
        ]
    else:
        tenant_middleware = [
            'django_project.middleware.SubfolderTenantMiddleware',
        ] + base_middleware
    
    return tenant_middleware

MIDDLEWARE = _configure_middleware()

# URL Configuration
ROOT_URLCONF = 'django_project.tenant_urls'
PUBLIC_SCHEMA_URLCONF = "django_project.public_urls"
AUTH_USER_MODEL = 'accounts.CustomUser'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # social auth 
                'social_django.context_processors.backends',
                # property manager
                'django_project.context_processors.routing_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_project.wsgi.application'



# kJ4qcna5OXHsUR91 <- db password

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTHENTICATION_BACKENDS = [
    
    # Added this for signing in with username or email
    'accounts.backends.EmailOrUsernameBackend',
    
    # social auth backend
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    
    # django's default auth backend
    'django.contrib.auth.backends.ModelBackend',
]

# Google auth credentials
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

# Facebook auth credentials
SOCIAL_AUTH_FACEBOOK_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_FACEBOOK_OAUTH2_KEY')
SOCIAL_AUTH_FACEBOOK_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_FACEBOOK_OAUTH2_SECRET')

SOCIAL_AUTH_FACEBOOK_SCOPE = [
    'email',
    'public_profile',
]


LOGIN_URL = 'signin'
LOGIN_REDIRECT_URL = 'signin'
LOGOUT_URL = 'signout'
LOGOUT_REDIRECT_URL = 'signin'


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

# storing static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static'),
]

# storing static files in the cloud
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

# Media files (Uploaded Images, Docs, Video)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR/"media"



# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Honeypot Configuration
HONEYPOT_FIELD_NAME = "dragon"

# Django Tenants Configuration
TENANT_MODEL = 'core.Client'
TENANT_DOMAIN_MODEL = 'core.Domain'
TENANT_SUBFOLDER_PREFIX = "clients"
PUBLIC_SCHEMA_NAME = 'public'
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

#paystack config
PAY_PUBLIC_KEY = os.getenv('PAYS_PUBLIC_KEY')
PAY_SECRET_KEY = os.getenv('PAYS_SECRET_KEY')




# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CELERY SETTINGS
CELERY_TIMEZONE = 'UTC'  # or your preferred timezone

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Required for django-tenants-celery-beat
DJANGO_TENANTS_CELERY_BEAT_SCHEDULER = 'django_tenants_celery_beat.schedulers:TenantAwareScheduler'
CELERY_BEAT_SCHEDULER = DJANGO_TENANTS_CELERY_BEAT_SCHEDULER
PERIODIC_TASK_TENANT_LINK_MODEL = "core.PeriodicTaskTenantLink"

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

TENANT_TIMEZONE_DISPLAY_GMT_OFFSET = False

CELERY_RESULT_BACKEND = "django-db"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default':{
        'ENGINE':'django_tenants.postgresql_backend',
        'HOST':os.getenv('DBHOST'),
        'NAME':os.getenv('DBNAME'),
        'PORT':os.getenv('DBPORT'),
        'USER':os.getenv('DBUSER'),
        'PASSWORD':os.getenv('DBPASSWORD')
    }
}



DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)



# Django Hosts Configuration
PARENT_HOST = 'duloft.com'
ROOT_HOSTCONF = 'django_project.hosts'
DEFAULT_HOST = 'app'

BASE_DOMAIN_NAME = 'duloft.com'


# Security Enhancements for Production

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
    
# Session and CSRF Cookie Configuration
SESSION_COOKIE_DOMAIN = 'duloft.com'
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN


# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '465'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
