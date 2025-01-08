import re
from django.apps import apps
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth import ( login, authenticate, logout, get_user_model )
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from datetime import datetime 
from django.core.exceptions import ObjectDoesNotExist


from honeypot.decorators import check_honeypot
from django_hosts.resolvers import reverse
from django_tenants.utils import schema_context, tenant_context

from .models import CustomUser, SubscriptionPlan, Subscription
from .models import ClientAccountProfile,TenantProfile, Token
from .tasks import send_email

User = get_user_model()

Unit = apps.get_model('property', 'Unit')
Client = apps.get_model('core', 'Client')
Domain = apps.get_model('core', 'Domain')

def test_home(request):
    return render(request, 'accounts/new-email.html')

# Password validation
def is_password_complex(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<br>\/?]", password):
        return "Password must contain at least one special character."
    return None  


def user_signin(request):
    # redirect to homepage if the user is authenticated
    if request.user.is_authenticated:

        next_url = request.GET.get('next')  # ('next', 'home')
        if next_url:
            return redirect(next_url)
        return HttpResponse(
            f"""
            <p>You are signed in as {request.user.first_name}.</p>
            <br>
            <a href="/profile/">Update Your Profile</a>
            <a href="/sign-out/">Sign-out</a>
            """
        )# for testing
    
    # get signin data
    if request.method == 'POST':
        signin_id = request.POST.get('signin_id')
        password = request.POST.get('signin_password')
        
        # check if all fields are provided
        if not (signin_id and password):
            messages.error(request, 'Please fill in your credentials to signin.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        

        # authenticate for email or username
        user = authenticate(request, username=signin_id, password=password)
        
        # check if authentication is successful
        if user: 
            # login the user and redirect to homepage if email is verified
            if user.is_active:
                request.user.backend = 'accounts.backends.EmailOrUsernameBackend'
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                request.tokens = token.key
                print(request.tokens, 'tokens')
                return HttpResponse(
                    f"""
                    <p>Sign in successful!</p>
                    <p>You are signed in as {request.user.first_name}.</p>
                    <br>
                    <a href="/profile/">Update Your Profile</a>
                    <a href="/sign-out/">Sign-out</a>
                    """
                )# for testing
                # return redirect('home')
            else:
                messages.error(request, 'Email not verified. Please check your email for verification link.')
        else:
            messages.error (request, 'Invalid email or password. Please try again.')
    
    template = "accounts/signin.html"
    return render(request, template)


def account_type(request):
    # Render a template for choosing account type
    return render(request, 'accounts/account-type.html')


def set_tenant_unit(request):
    from django.db import connection
    if request.method == 'POST':
        # Get the unique unit ID from the requestN
        unit_unique_id = request.POST.get('unit_unique_id')
        user = request.user
        
        if not user.is_tenant():
            return HttpResponseBadRequest("Only Tenant can be placed in a unit")

        if not unit_unique_id:
            # If no unit_unique_id, redirect to tenant registration
            return  HttpResponseBadRequest("Unit Unique ID required.")  

        try:
            # Split unit_unique_id into schema_name and unit_id
            schema_name, unit_id = unit_unique_id.split(':')
            
            user_profile = user.tenant_profile

            print(f"Current schema: {connection.schema_name}")
            print(f"Switching to schema: {schema_name}")  # Debugging log
            # Query the schema for the unit
            unit_obj = query_schema_filter(schema_name, 'Unit', unique_id=unit_id)
            print(f"Current schema: {connection.schema_name}")
            unit_obj.tenant_id = user_profile.shared_id
            unit_obj.save()
            # Redirect with unit details in the URL or session (depending on your design)
            return redirect('tenant_dashboard')  # Add appropriate handling for `unit_obj`
        except ValueError:
            # If the format of unit_unique_id is invalid
            return HttpResponseBadRequest("Invalid unit unique ID format.")
        except Unit.DoesNotExist:
            # Handle case where the unit is not found in the tenant schema
            return HttpResponseBadRequest("Unit not found.")
        except Exception as e:
            # Handle unexpected errors
            return HttpResponseBadRequest(f"An error occurred: {str(e)}")

    # Render a template to ask or determine tenant stage
    return render(request, 'tenant_stage.html')  # Replace with your actual template


def query_schema_filter(schema_name, model_name, **filters):
    """
    Query data within a specific schema using schema_context.
    """
    from django.apps import apps

    model = apps.get_model('Properties', model_name)  # Dynamically load the tenant-specific model

    with schema_context(schema_name):  # Switch to the tenant's schema
        # Query the model with optional filters
        return get_object_or_404(model, **filters)



def user_signup(request):
    page = "signup"
    
    # get account type
    account_type = request.GET.get('type')

    # get signup data 
    if request.method == "POST":
        firstname = request.POST.get('signup_firstname')
        lastname = request.POST.get('signup_lastname')
        username = request.POST.get('signup_username').lower()
        email = request.POST.get('signup_email').lower()
        # phone_number = request.POST.get('signup_phone_number')
        password = request.POST.get('signup_password')
        confirm_password = request.POST.get('signup_confirm_password')
        
        # check if all fields are provided
        if not (firstname and lastname and username and email and password and confirm_password):
                messages.error(request, 'Please complete all required fields.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        # validate email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'The email address provided is not valid.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        # check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'An account with this username already exists.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        # check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email address already exists.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        # check password strength
        complexity_error = is_password_complex(password)
        if complexity_error:
            messages.error(request, complexity_error)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match. Please re-enter to confirm.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        if account_type == "tenant":
            # tenant's account creation 

            # create the user model with user_type as tenant
            new_user = User.objects.create_user(
                user_type = CustomUser.TENANT,
                username=username,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=password,
                is_active = False
            )
            
            # create profile
            
        else:
            # property manager's account creation
            
            # create the user model with user_type as admin
            new_user = User.objects.create_user(
                user_type = CustomUser.ADMIN,
                username=username,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=password,
                is_active = False
            )
            
            # create profile
            
        new_user.save()
        
        # send verification email
        user = new_user
        send_verification_email(request, user)
        context = {
            'user_email': user.email
        }

        return render(request, 'accounts/email_verification_notification.html', context)
    
    template = "accounts/signup.html"
    context = {'page': page, 'type': account_type}
    return render(request, template, context)


def signout_user(request):
    
    logout(request)
    return redirect('signin')




token_generator = PasswordResetTokenGenerator()

# Send verification email
def send_verification_email(request, user):
    # reverse('blog_post', kwargs={'id': post_id}, host='blog') 
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    verification_link = f"/activate-account/{uid}/{token}/"
    activation_url = f"http://{domain}{verification_link}"
    user_fullname = f"{user.first_name} {user.last_name}".title()  
    subject = "Verify your email"
    send_email.delay(subject, template_mail_name='accounts/email_verification_mail.html', template_mail_context={
        'user_fullname': user_fullname,
        'activation_url': activation_url,
    }, email_list=[user.email])
    

# Activate account
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64).decode())
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='accounts.backends.EmailOrUsernameBackend')
        messages.success(request, "Your account has been verified!")
        # if user.user_type == CustomUser.ADMIN:
        #     return redirect('client_profile')
        # else:
        #     return redirect('tenant_profile')
        return HttpResponse(
            f"""
            <p>Sign in successful!</p>
            <p>{request.user.first_name} {request.user.last_name}</p>
            <br>
            <a href="/sign-out/">Sign-out</a>
            """
        )# for testing
        
    else:
        messages.error(request, "The activation link is invalid!")
        return redirect('signup')

def password_reset_view(request):
    """This function is for resetting the password of any user, that can't access their accounts

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == "POST":
        email = request.POST.get('password_reset_email')
        
        # email_objects = CustomUser.objects.filter(email=email, is_active=True)
        # if email_objects.exists():
        #     email_object = email_objects.first()
        #     user = email_object.username
        
        
        try:
            user = CustomUser.objects.get(email=email)
            
            if user.is_active:
                first_name = user.first_name
                token = token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                protocol = 'https' if request.is_secure() else 'http'
                verification_link = f"reset/{uid}/{token}" # reverse('password_reset_confirm', args=[uid, token]) # this doent usually work # i dont know why shaa.
                #  reverse('blog_post', kwargs={'id': post_id}, host='blog')
                activation_url = f"{protocol}://{domain}/{verification_link}/"
                subject = 'Password Reset Requested'
                
                template_mail_name = 'accounts/password_reset_mail.html'
                template_mail_context = {
                    'first_name':first_name,
                    'rest_link':activation_url
                }
                email_list=[user.email]
                send_email.delay(subject, template_mail_name=template_mail_name, template_mail_context=template_mail_context, email_list=email_list)
                return redirect('password_reset_done')
            else:
                messages.error(request, 'User not verified.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return render(request, 'accounts/password_reset_form.html')

def password_reset_done(request):
    """send a template to the user when the password reset form is filled.

    Args:
        request (_type_): _description_
    """
    return render(request, 'accounts/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    """Requests the user for a new password if the link is valid and sets it to user account.

    Args:
        request (_type_): _description_
        uidb64 (_type_): _description_
        token (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            # check if password and confirm password match
            if new_password == confirm_password:
                # check password strength
                complexity_error = is_password_complex(new_password)
                if complexity_error:
                    messages.error(request, complexity_error)
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
                user.set_password(new_password)
                user.save()
                return redirect('password_reset_complete')
            else:
                messages.error(request, "Passwors do not match, please try again.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return render(request, 'accounts/password_reset_comfirm.html', {"validlink":True})
    else:
        return render(request, 'accounts/password_reset_confirm.html', {"validlink":False})

def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')



def update_client_profile(request):
    page = "update_client_profile"
    user = request.user
    if hasattr(user, 'account_profile'):
        client_profile = ClientAccountProfile.objects.get(user = user)
    else:
        client_profile =''
    if request.method == "POST":
        account_type = request.POST.get('account_type')
        account_name = request.POST.get('account_name')
        domain_name = str(request.POST.get('domain_name')).lower()
        head_office_address = request.POST.get('head_office_address')
        branch_office_address = request.POST.get('branch_office_address') 
        if account_type and account_name and domain_name and head_office_address and branch_office_address:
            if user.user_type == "client_admin":
                client_profile.account_type = account_type
                client_profile.account_name = account_name
                client_profile.domain_name = domain_name
                client_profile.address = head_office_address
                client_profile.branch_address = branch_office_address
                client_profile.save()
                messages.success(request, "Profile has been updated successfully.")
                return redirect('client_profile')
            else:
                messages.error(request, "Access denied.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, "Please fill all the required fields")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
    context = {
        'page': page,
        'user': user,
        'profile': client_profile,
    }
    return render(request, "accounts/update_client_profile.html", context)

def update_tenant_profile(request):
    page = "update_tenant_profile"
    user = request.user
    if hasattr(user, 'tenant_profile'):
        tenant_profile = TenantProfile.objects.get(user = user)
    else:
        tenant_profile =''
    if request.method == "POST":
        id_type = request.POST.get('id_type') 
        valid_id_number = request.POST.get('valid_id_number')  
        date_of_birth = request.POST.get('date_of_birth') 
        profile_photo = request.FILES.get('profile_photo') 
        marital_status = request.POST.get('marital_status') 
        job = request.POST.get('job')
        monthly_income = request.POST.get('monthly_income') 
        employer_name = request.POST.get('employer_name') 
    
        if id_type and valid_id_number and date_of_birth and marital_status and job and monthly_income and employer_name:
            if user.user_type == "tenant":
                tenant_profile.id_type = id_type
                tenant_profile.valid_id_number = valid_id_number
                tenant_profile.date_of_birth = date_of_birth
                tenant_profile.profile_photo = profile_photo
                tenant_profile.marital_status = marital_status
                tenant_profile.job = job
                tenant_profile.monthly_income = monthly_income
                tenant_profile.employer_name = employer_name
                tenant_profile.save()
                messages.success(request, "Profile has been updated successfully.")
                return redirect('tenant_profile')
            else:
                messages.error(request, "Access denied.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, "Please fill all the required fields")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
    context = {
        'pagee': page,
        'user': user,
        'profile': tenant_profile,
    }
    return render(request, "accounts/update_tenant_profile.html", context)


def client_profile_page(request):
    # reverse('repo', args=('jezdez',), host='www', scheme='git', port=1337) f"{protocol}://{subdomain}.{settings.PARENT_HOST}"
    # reverse('home', host='tenant', kwargs={'subdomain_name':'value'})
    protocol = request.scheme  # This will be 'http' or 'https'
    
    if  request.user.is_authenticated:
        user = request.user
        print(user)
        if hasattr(user, 'account_profile'):
            subdomain = user.account_profile.domain_name
        else:
            subdomain = None
        subdomain_str = str(subdomain).lower()
        subdomain_url =  f"{protocol}://{settings.PARENT_HOST}/{settings.TENANT_SUBFOLDER_PREFIX}/{subdomain_str}/"
        

        context = {
            'user':user,
            'subdomain_url': subdomain_url,
        }
        if subdomain != None:
            context.update({
                'subdomain':subdomain_str
            })
    else:
        context = {
            'user':'',
            'subdomain_url':''
        }
    
    return render(request, 'accounts/profile_client_page.html', context)
    

def tenant_profile_page(request):
    user = ''
    if  request.user.is_authenticated:
        user = request.user
    
    context = {
        'user':user
    }
    
    return render(request, 'accounts/profile_tenant_page.html', context)


def profile_update_sso(request):
    option_user_type = CustomUser.USER_TYPE_CHOICES
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        
        if first_name and last_name and email and user_type:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.user_type = user_type
            user.save()
            messages.success(request, "Profile updated successfully.")
            if user.user_type == CustomUser.ADMIN:
                return redirect('client_profile')
            else:
                return redirect('tenant_profile')
        else:
            messages.error(request, "Please fill all the required fields.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return render(request, 'accounts/profile_update_sso.html', context={'user':user, 'option_user_type':option_user_type})


def profile_page(request):
    
    if request.user.is_admin():
        return redirect('client_profile')
    
    elif request.user.is_tenant():
        return redirect('tenant_profile')
    
    else:
        return redirect('tenant_profile')

def display_subscription_plan(request):
    sub_plan = SubscriptionPlan.objects.all()
    plan_duration = Subscription.DurPlans
    
    context = {
        "sub_plan":sub_plan,
        'plan_duration':plan_duration,           
    }
    
    return render(request, 'subscriptions/subscription_plan.html', context)

def initiate_subscription_payment(request,id):
    subscribed_plan = SubscriptionPlan.objects.get(id=id)
    durations_plan = request.POST.get('duration', '12')
    print(subscribed_plan, 'view', durations_plan)
    if subscribed_plan.name != 'freemium':
        # try:
            if request.user.is_authenticated and request.user.account_profile:
                subscriber = request.user.account_profile
                email = request.user.email
                # multiply the amount by 12 for yearly subscription or get the durations_plan from the Subscription
                try:
                    subscribed_obj = Subscription.objects.get(company=subscriber)
                except ObjectDoesNotExist:
                    # Handle case where subscription does not exist
                    init_pay = Subscription.objects.get_or_create(
                        company=subscriber, 
                        plan=subscribed_plan, 
                        amount=(float(subscribed_plan.amount) * int(durations_plan)), 
                        durations_plan=durations_plan
                    )
                    context = {'data': init_pay, 'Public_key': settings.PAY_PUBLIC_KEY}
                    return render(request, 'subscription/subscription_payment.html', context)
                else:
                    if not subscribed_obj.is_active():
                        subscribed_obj.amount = (float(subscribed_plan.amount) * int(durations_plan))
                        subscribed_obj.plan = subscribed_plan
                        subscribed_obj.durations_plan = durations_plan
                        subscribed_obj.start_date = datetime.now()
                        subscribed_obj.save()
                    else:
                        context = {'Public_key': settings.PAY_PUBLIC_KEY}
                        return render(request, 'subscription/subscription_payment.html', context)
            else:
                return HttpResponse("User is not authenticated or don't have a company profile.")
        # except:
            # return render(request, 'access_denied.html')
    else:
        try:
            if request.user.is_authenticated and request.user.account_profile:
                subscriber = request.user.account_profile
                email = request.user.email
                
                # multiply the amount by 12 for yearly subscription
                try:
                    subscribed_obj = Subscription.objects.get(company=subscriber)
                except ObjectDoesNotExist:
                    # Handle case where subscription does not exist
                    init_pay = Subscription.objects.get_or_create(
                        company=subscriber, 
                        plan=subscribed_plan, 
                        amount=(float(subscribed_plan.amount) * int(durations_plan)), 
                        durations_plan=durations_plan
                    )
                    return render(request, 'thank_you_subscriber.html')
                else:
                    if not subscribed_obj.is_active():
                        subscribed_obj.amount = (float(subscribed_plan.amount) * int(durations_plan))
                        subscribed_obj.plan = subscribed_plan
                        subscribed_obj.durations_plan = durations_plan
                        subscribed_obj.start_date = datetime.now()
                        subscribed_obj.save()
                    else:
                        return render(request, 'thank_you_subscriber.html')
            else:
                return HttpResponse("User is not authenticated or don't have a company profile.")
        except:
            return render(request, 'access_denied.html')