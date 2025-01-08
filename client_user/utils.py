from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django_tenants.utils import schema_context
from django.db import connection


# Define role-permission mappings
ROLE_PERMISSIONS = {
    "property_manager": ["add_propertymodel", "add_unit", "add_leasemanagement", "add_unitlisting", "add_propertylistingmodel", "change_propertymodel", "add_image", "delete_propertymodel"],
    "leasing_agent": ["add_lease", "change_lease"],
    "accountant": ["add_record", "change_record"],
    "maintenance_supervisor": ["view_unit", "change_unit"],
    "maintenance_technician": ["view_unit"],
}

# def assign_permissions():
#     for role_name, perm_codenames in ROLE_PERMISSIONS.items():
#         role, created = Role.objects.get_or_create(name=role_name)
#         for codename in perm_codenames:
#             permission = Permission.objects.get(codename=codename)
#             role.permissions.add(permission)



# Retrieve all permissions for the model
# permissions = Permission.objects.all()

# # Print the permissions
# for perm in permissions:
#     print(f"Codename: {perm.codename}, Name: {perm.name}")




def query_schema_all(schema_name, models, set_schema_connection=False):
    """
    Query data within a specific schema using schema_context.
    """
    if set_schema_connection:
        connection.set_schema(schema_name)
        
    with schema_context(schema_name):
        # Query data within the schema
        results = models.objects.all()
        return results

