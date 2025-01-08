import csv
import logging
import importlib
from django.apps import apps
from django.contrib import messages
from django.db import connection
from django.db.models import Sum
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist

from django.apps import apps
from django_tenants.utils import schema_context
from django_hosts.resolvers import reverse

# Create your views here.


PropertyModel = apps.get_model("property", "PropertyModel")
PropertyListing = apps.get_model("property", "PropertyListingModel")
PropertyType = apps.get_model('property', 'PropertyType')
Unit  = apps.get_model("property", "Unit")
UnitListing = apps.get_model('property', 'UnitListing')
InspectionModel = apps.get_model('property', 'InspectionModel')
User, Subscription = apps.get_model('accounts', 'CustomUser'), apps.get_model('accounts', 'Subscription')
Client = apps.get_model('core', 'Client')
ClientUsers = apps.get_model('client_user', 'ClientUsers')
Payment = apps.get_model('payment_track', 'Payment')
Payout = apps.get_model('payment_track', 'Payout')
FeesRecord = apps.get_model('payment_track', 'FeesRecord')
ExpenseRecord = apps.get_model('payment_track', 'ExpenseRecord')
Lease = apps.get_model('lease', 'LeaseManagement')
MaintenanceRequest = apps.get_model('maintenance_track', 'MaintenanceRequest')
MaintenanceTask = apps.get_model('maintenance_track', 'MaintenanceTask')


AccountsUtils = importlib.import_module('accounts.utils')
check_active_subscription = AccountsUtils.check_active_subscription
query_schema_all = AccountsUtils.query_schema_all


logger = logging.getLogger(__name__)



def calculate_days_difference(datetime1, datetime2):
    """
    Calculate the difference in days between two Django datetime objects.

    Parameters:
    - datetime1: The first Django datetime object
    - datetime2: The second Django datetime object

    Returns:
    - The difference in days (integer)
    """
    
    # Adding One Year to the last rent date
    one_year_later = datetime1 + relativedelta(years=1)
    
    # Calculate the timedelta between the two datetimes
    time_difference = one_year_later - datetime2
    print(time_difference)
    # Extract the number of days from the timedelta
    days_difference = time_difference.days

    return days_difference

# @login_required(login_url=reverse('signin', host='account'))
def home_page(request, tenant_domain=None):
    # from django.contrib.auth.models import Permission
    # # Retrieve all permissions for the model
    # permissions = Permission.objects.all()

    # # Print the permissions
    # for perm in permissions:
    #     if perm.codename.startswith('add'):
    #         print(f"Codename: {perm.codename}, Name: {perm.name}")
    print("here  ...........")
    if tenant_domain:
        print(tenant_domain)
        request.tenant = Client.objects.get(schema_name = tenant_domain)
        # with schema_context(tenant_domain):
        
        return HttpResponse(
        f"""
            <h2> Welcome to {request.tenant}</h2>
            <br>
            <h4>Hello, {request.user}</h4>
            
            <a href="{reverse('signin', host='account')}">Register</a>
        """
    )

            
    return HttpResponse(
        f"""
            <h2> Welcome to {request.tenant}</h2>
            <br>
            <h4>Hello, {request.user}</h4>
            
            <a href="{reverse('signin', host='account')}">Register</a>
        """
    )

def main_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    properties = PropertyModel.objects.all()
    units = Unit.objects.all()
    vacant_units = units.filter(taken=False)
    active_units = units.filter(taken=True)
    
    # Use list comprehension instead of set for property payments
    list_property_payment = [
        {
            'property': prop.title,
            'total_payment': prop.total_payments(),
        }
        for prop in properties
    ]

    context = {
        'properties': properties,
        'units': units,
        'vacant_units': vacant_units,
        'active_units': active_units,
        'active_properties': len({unit.property_id for unit in active_units}),
        'list_property_payment': list_property_payment,
        'monthly_revenue': Payment.objects.monthly_revenue(),
        'yearly_revenue': Payment.objects.yearly_revenue(),
        'maintenance_request': MaintenanceRequest.objects.count(),
        'active_maintenance_request': MaintenanceRequest.objects.exclude(status='Completed').count(),
        'fees_record_income': FeesRecord.objects.monthly_total(),
        'expense_record_outgoing': ExpenseRecord.objects.monthly_total(),
    }
    
    return render(request, 'main_dashboard.html', context)
    


def tenant_dashboard(request):
    """Dashboard view for cross-tenant users showing all their leased units across different clients"""
    if not request.user.is_authenticated:
        return redirect('login')
        
    context = {}
    
    try:
        shared_id = request.user.tenant_profile.shared_id
        selected_client = request.GET.get('client', None)
        all_leased_units = []
        all_leases = []
        
        # Get all clients and their units/leases
        clients = Client.objects.all()
        clients_data = []
        
        for client in clients:
            try:
                # Query units and leases for this client
                leased_units = query_schema_all(client.schema_name, Unit).filter(tenant_id=shared_id)
                leases = query_schema_all(client.schema_name, Lease).filter(tenant_shared_id=shared_id)
                
                if leased_units.exists():  # Only add client if tenant has units
                    client_data = {
                        'client': client,
                        'units': [],
                        'leases': []
                    }
                    
                    # Process units
                    for unit in leased_units:
                        unit_data = {
                            'unit': unit,
                            'client_name': client.name,
                            'schema_name': client.schema_name
                        }
                        client_data['units'].append(unit_data)
                        all_leased_units.append(unit_data)
                    
                    # Process leases
                    for lease in leases:
                        lease_data = {
                            'lease': lease,
                            'client_name': client.name,
                            'schema_name': client.schema_name,
                            'days_remaining': calculate_days_difference(
                                lease.start_date,
                                now().date()
                            )
                        }
                        client_data['leases'].append(lease_data)
                        all_leases.append(lease_data)
                    
                    clients_data.append(client_data)
                    
            except Exception as e:
                logger.error(f"Error processing client {client.name}: {str(e)}")
                messages.error(
                    request, 
                    f"Unable to load data for {client.name}. Please try again later."
                )
                continue
        
        # Handle client selection
        if selected_client:
            selected_client_data = next(
                (cd for cd in clients_data if cd['client'].id == int(selected_client)), 
                None
            )
            if selected_client_data:
                context['selected_units'] = selected_client_data['units']
                context['selected_leases'] = selected_client_data['leases']
            else:
                messages.warning(request, "Selected client not found or no units available.")
        
        # Add all data to context
        context.update({
            'shared_id': shared_id,
            'clients_data': clients_data,
            'all_leased_units': all_leased_units,
            'all_leases': all_leases,
            'total_units': len(all_leased_units),
            'total_leases': len(all_leases),
            'selected_client': selected_client
        })
        
    except AttributeError:
        messages.error(
            request, 
            "No tenant profile found. Please contact support."
        )
        logger.error(f"No tenant profile found for user {request.user.id}")
    except Exception as e:
        messages.error(
            request, 
            "An error occurred while loading your dashboard."
        )
        logger.error(f"Unexpected error in tenant dashboard: {str(e)}")
    
    return render(request, 'tenant_dashboard.html', context)


