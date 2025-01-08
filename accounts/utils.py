from django_tenants.utils import schema_context
from .models import Subscription

def check_active_subscription(user):
    account = None
    try:
        account = user.account_profile
        if account:
            print(account, 'check active subscription')
        else:
            print("No associated account found for the user.")
    except:
        print("User does not have the required attributes.")
        return False
    else:
        plan = Subscription.objects.get(company=account)
        try:
            if plan.is_active:
                return True
            else:
                return False
        except:
            return False




def query_schema_all(schema_name, models):
    """
    Query data within a specific schema using schema_context.
    """
    with schema_context(schema_name):
        # Query data within the schema
        results = models.objects.all()
        return results
