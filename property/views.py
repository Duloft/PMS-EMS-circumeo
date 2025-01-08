from django.apps import apps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.contenttypes.models import ContentType
from .models import (PropertyModel, PropertyListingModel, PropertyType, Image, 
                     AmenitiesModels, AccommodationType, Unit, UnitListing)
from django_hosts.resolvers import reverse


# Create your views here.

ClientUsers = apps.get_model('client_user', 'ClientUsers')


# @login_required
# @login_required
def create_property_type(request):
    """Creates property type for the properties
    """
    template_name = 'properties/property_type_form.html'
    
    if request.method == "POST":
        property_type_name = request.POST.get('name')
        PropertyType.objects.create(
            name = property_type_name,
        )
        
        return redirect('property_list')
    
    return render(request, template_name)   
    

# @login_required
# @login_required
def update_property_type(request, pk):
    """ Updates property type for the properties

    Args:
        request (_type_): _description_
        id (_type_): _description_

    Returns:
        _type_: _description_
    """
    template_name = ''
    obj = get_object_or_404(PropertyType, pk=pk)
    
    
    if request.method == "POST":
        
        obj.save()
        return redirect('/')
    
    context = {
        'property_type':obj
    }
    return render(request, template_name, context)   
    

# @login_required
# @login_required
def get_property_type(request):
    """Returns a list of all the property type for the properties

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    template_name = ''
    prop_type_queryset = PropertyType.objects.all()
    context = {
        'property_types':prop_type_queryset
    }
    return render(request, template_name, context)   
    


# @login_required
# @login_required
def delete_property_type(request, pk):
    """Delete property type
    """
    template_name = ''
    property_type = get_object_or_404(PropertyType, pk=pk)
    if request.method == 'POST':
        property_type.delete
        return redirect('')
    
    context = {
        'property_type':property_type
    }
    
    return render(request, template_name, context)



# List all properties
def property_list(request):
    properties = PropertyModel.objects.all()
    return render(request, 'properties/property_list.html', {'properties': properties})
    return render(request, 'properties/property_list.html', {'properties': properties})

# sign_in_url = reverse('signin', host='account')
# @custom_login_required(login_url=sign_in_url, custom_login_url="/login/")
# @user_passes_test(get_subscription_plan_properties, login_url='subscription_limit', redirect_field_name=None)
def add_property_view(request):
    """Create and adds a property to the database
    """
    template_name = 'properties/property_form.html' 
    
    if request.method == "POST":
        title = request.POST['title']
        address = request.POST['address']
        country = request.POST['country']
        state = request.POST['state']
        city = request.POST['city']
        no_of_total_units = request.POST['no_of_total_units']
        no_of_available_units = request.POST['no_of_available_units']
        property_type_id = request.POST.get('property_type')
        list_property = bool(request.POST.get('list_property', False))
        manager_id = request.POST.get('manager')
        is_verified = bool(request.POST.get('is_verified', False))
        featured = bool(request.POST.get('featured', False))

        property_obj = PropertyModel.objects.create(
            title=title,
            address=address,
            country=country,
            state=state,
            city=city,
            no_of_total_units=no_of_total_units,
            no_of_available_units=no_of_available_units,
            property_type_id=property_type_id,
            list_property=list_property,
            manager_id=manager_id,
            is_verified=is_verified,
            featured=featured,
        )
        
        if property_obj.list_property:
            return redirect('add_property_listing', property_obj.id)
        else:
            return redirect('property_list')
            return redirect('property_list')

    property_types = PropertyType.objects.all()
    managers = ClientUsers.objects.all()
    context = {
        'property_types': property_types,
        'managers': managers
    }
    
    return render(request, template_name, context)


# @login_required
# @login_required
# @user_passes_test(is_approved, login_url='not_approved', redirect_field_name=None)  # can only be accessed by a user that is verified and approved
def update_property_view(request, pk):
    """updates a property in the database
    """
    template_name = 'properties/property_form.html'
    
    property_model = get_object_or_404(PropertyModel, pk=pk)
    if request.method == 'POST':
        property_model.title = request.POST['title']
        property_model.address = request.POST['address']
        property_model.country = request.POST['country']
        property_model.state = request.POST['state']
        property_model.city = request.POST['city']
        property_model.no_of_total_units = request.POST['no_of_total_units']
        property_model.no_of_available_units = request.POST['no_of_available_units']
        property_model.property_type_id = request.POST.get('property_type')
        property_model.list_property = bool(request.POST.get('list_property', False))
        property_model.manager_id = request.POST.get('manager')
        property_model.is_verified = bool(request.POST.get('is_verified', False))
        property_model.featured = bool(request.POST.get('featured', False))
        
        property_model.save()
        
        if not property_model.list_property:
            return redirect('property_list')
        else:
            return redirect('add_property_listing',pk)

    property_types = PropertyType.objects.all()
    managers = ClientUsers.objects.all()
    context = {
        'property_types': property_types,
        'managers': managers,
        'property_model': property_model,
    }
    return render(request, template_name, context)
    

def property_model_detail(request, pk):
    property = get_object_or_404(PropertyModel, pk=pk)
    template_name = 'properties/property_detail.html'
    return render(request, template_name, {'property': property})

def delete_property(request, pk):
    template_name = "properties/confirm_delete.html"
    property_obj = get_object_or_404(PropertyModel, pk=pk)
    if request.method == "POST":
        property_obj.delete()
        return redirect('property_list')
        property_obj.delete()
        return redirect('property_list')
    
    context = {
        'property':property_obj,
    }
    
    return render(request, template_name, context)    


# List all property listings
def property_listing_list(request):
    properties = PropertyListingModel.objects.all()
    
    context = {'properties': properties}
    return render(request, 'properties/property_listing.html', context)


# Create a new property listing
def add_property_listing(request, pk):
    property_model_id = get_object_or_404(PropertyModel, pk=pk)
    if request.method == 'POST':
        on_sale = bool(request.POST.get('on_sale', False))
        collect_rent = bool(request.POST.get('collect_rent', False))
        allow_online_payment = bool(request.POST.get('allow_online_payment', False))
        vid_file = request.FILES.get('vid_file')
        is_newly_built = bool(request.POST.get('is_newly_built', False))
        description = request.POST['description']
        has_electricity = bool(request.POST.get('has_electricity', False))
        water = bool(request.POST.get('water', False))
        features_ids = request.POST.getlist('features')
        property_price = request.POST['property_price']
        tenant_agreement = request.FILES.get('tenant_agreement')

        property_listing = PropertyListingModel.objects.create(
            property_model_id=property_model_id.id,
            on_sale=on_sale,
            collect_rent=collect_rent,
            allow_online_payment=allow_online_payment,
            vid_file=vid_file,
            is_newly_built=is_newly_built,
            description=description,
            has_electricity=has_electricity,
            water=water,
            property_price=property_price,
            tenant_agreement=tenant_agreement,
        )
        property_listing.features.set(features_ids)
        return redirect('property_listing')
    features = AmenitiesModels.objects.all()
    
    return render(request, 'properties/property_listing_form.html', {'features': features})


# Update a property listing
def update_property_listing(request, pk):
    property_listing = get_object_or_404(PropertyListingModel, pk=pk)
    if request.method == 'POST':
        property_listing.on_sale = bool(request.POST.get('on_sale', False))
        property_listing.collect_rent = bool(request.POST.get('collect_rent', False))
        property_listing.allow_online_payment = bool(request.POST.get('allow_online_payment', False))
        property_listing.vid_file = request.FILES.get('vid_file', property_listing.vid_file)
        property_listing.is_newly_built = bool(request.POST.get('is_newly_built', False))
        property_listing.description = request.POST['description']
        property_listing.has_electricity = bool(request.POST.get('has_electricity', False))
        property_listing.water = bool(request.POST.get('water', False))
        features_ids = request.POST.getlist('features')
        property_listing.property_price = request.POST['property_price']
        property_listing.tenant_agreement = request.FILES.get('tenant_agreement', property_listing.tenant_agreement)

        property_listing.features.set(features_ids)
        property_listing.save()
        # logger.info(f"Property listing with ID {pk} updated successfully.")   
        return redirect('property_listing')
    
    features = AmenitiesModels.objects.all()
    context = {'property_listing': property_listing, 'features': features}
    return render(request, 'properties/property_listing_form.html', context)


# Detail of a property listing
def property_listing_detail(request, pk):
    property_listing = get_object_or_404(PropertyListingModel, pk=pk)
    images = property_listing.images.all()
    
    context = {
        'property_listing':property_listing,
        'images':images
    }
    
    return render(request, 'properties/property_listing_detail.html', context)    

def property_listing_delete(request, pk):
    property_listing = get_object_or_404(PropertyListingModel, pk=pk)
    if request.method == 'POST':
        property_listing.delete()
        return redirect('property_listing')
    return render(request, 'properties/confirm_delete.html', {'property': property_listing})



# Manage images for a property listing
def property_images(request, pk):
    property_listing = get_object_or_404(PropertyListingModel, pk=pk)
    if request.method == 'POST':
        name = request.POST['name']
        image = request.FILES['image']
        Image.objects.create(
            name=name,
            image=image,
            content_type=ContentType.objects.get_for_model(PropertyListingModel),
            object_id=property_listing.id,
        )
        return redirect('property_images', pk=pk)
    images = property_listing.images.all()
    return render(request, 'property_images.html', {'property_listing': property_listing, 'images': images})


# Unit Function
# @login_required
# List all units
def unit_list(request):
    units = Unit.objects.select_related('property_id', 'accommodation_type').all()
    return render(request, 'unit_list.html', {'units': units})

# @login_required
# @user_passes_test(get_subscription_plan_properties, login_url='subscription_limit', redirect_field_name=None)
def create_unit(request):
    if request.method == 'POST':
        property_id = request.POST['property_id']
        title = request.POST['title']
        unit_number = request.POST['unit_number']
        taken = bool(request.POST.get('taken', False))
        tenant_id = request.POST.get('tenant_id')
        price_per_year = request.POST['price_per_year']
        accommodation_type_id = request.POST.get('accommodation_type')
        list_property = bool(request.POST.get('list_property', False))

        Unit.objects.create(
            property_id_id=property_id,
            title=title,
            unit_number=unit_number,
            taken=taken,
            tenant_id=tenant_id,
            price_per_year=price_per_year,
            accommodation_type_id=accommodation_type_id,
            list_property=list_property,
        )
        return redirect('unit_list')
    
    properties = PropertyModel.objects.all()
    accommodation_types = AccommodationType.objects.all()
    return render(request, 'unit_form.html', {'properties': properties, 'accommodation_types': accommodation_types})
   


# @login_required
# @user_passes_test(is_approved, login_url='not_approved', redirect_field_name=None) # can only be accessed by a user that is verified and approved
def update_unit_view(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        unit.property_id_id = request.POST['property_id']
        unit.title = request.POST['title']
        unit.unit_number = request.POST['unit_number']
        unit.taken = bool(request.POST.get('taken', False))
        unit.tenant_id = request.POST.get('tenant_id')
        unit.price_per_year = request.POST['price_per_year']
        unit.accommodation_type_id = request.POST.get('accommodation_type')
        unit.list_property = bool(request.POST.get('list_property', False))

        unit.save()
        return redirect('unit_list')
    
    properties = PropertyModel.objects.all()
    accommodation_types = AccommodationType.objects.all()
    context = {
        'unit': unit, 
        'properties': properties, 
        'accommodation_types': accommodation_types
    }
    return render(request, 'units/unit_form.html', context)

# @login_required
def unit_detail(request, pk):
    unit_instance = get_object_or_404(Unit, pk=pk)
    return render(request, 'units/unit_detail.html', {'unit': unit_instance})

# @login_required
def unit_delete(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        unit.delete()
        return redirect('unit_list')
    return render(request, 'units/unit_confirm_delete.html', {'unit': unit})

# List all unit listings
def unit_listing_list(request):
    unit_listings = UnitListing.objects.select_related('unit_model').prefetch_related('features', 'images').all()
    return render(request, 'unit_listing_list.html', {'unit_listings': unit_listings})

# @login_required
# @user_passes_test(get_subscription_plan_properties, login_url='subscription_limit', redirect_field_name=None)
def add_unit_listing(request):
    if request.method == 'POST':
        unit_id = request.POST['unit_model']
        description = request.POST.get('description')
        no_of_baths = int(request.POST['no_of_baths'])
        features = request.POST.getlist('features')
        vid_file = request.FILES.get('vid_file')

        unit_listing = UnitListing.objects.create(
            unit_model_id=unit_id,
            description=description,
            no_of_baths=no_of_baths,
            vid_file=vid_file,
        )
        unit_listing.features.set(features)
        return redirect('unit_listing_list')
    
    units = Unit.objects.all()
    amenities = AmenitiesModels.objects.all()
    return render(request, 'unit_listing_form.html', {'units': units, 'amenities': amenities})


# Update a unit listing
def update_unit_listing(request, pk):
    unit_listing = get_object_or_404(UnitListing, pk=pk)
    if request.method == 'POST':
        unit_listing.unit_model_id = request.POST['unit_model']
        unit_listing.description = request.POST.get('description')
        unit_listing.no_of_baths = int(request.POST['no_of_baths'])
        unit_listing.features.set(request.POST.getlist('features'))
        if 'vid_file' in request.FILES:
            unit_listing.vid_file = request.FILES['vid_file']
        unit_listing.save()
        return redirect('unit_listing_list')
    
    units = Unit.objects.all()
    amenities = AmenitiesModels.objects.all()
    return render(request, 'unit_listing_form.html', {'unit_listing': unit_listing, 'units': units, 'amenities': amenities})


# @login_required
def unit_listing_detail(request, pk):
    unit_instance = get_object_or_404(UnitListing, pk=pk)
    return render(request, 'units/unit_listing_detail.html', {'unit': unit_instance})


# @login_required
def unit_listing_delete(request, pk):
    unit_listing = get_object_or_404(UnitListing, pk=pk)
    if request.method == 'POST':
        unit_listing.delete()
        return redirect('unit_listing_list')
    return render(request, 'unit_listing_confirm_delete.html', {'unit_listing': unit_listing})