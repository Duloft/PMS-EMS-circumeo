from django.contrib import admin
from .models import PropertyModel, PropertyType
# Register your models here.
admin.site.register((PropertyModel,
                    PropertyType))
