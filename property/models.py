import uuid
from django.db import models
from django.db import connection
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation


# Create your models here.


class AmenitiesModels(models.Model):
    feature = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.feature


def get_default_file():
    return "documents/TAs/DULOFT_TENANT_AGREEMENT.pdf"



class Image(models.Model):
    """ For all the images in the listing models both for properties and units

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"Image for {self.content_object}"
    
    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]



class PropertyType(models.Model):
    name = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class PropertyModel(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    unique_id = models.UUIDField(default=uuid.uuid4, unique=True)
    address = models.CharField(max_length=250)
    country = models.CharField(max_length=150, null=True, blank=True) # default=165
    state = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    no_of_total_units = models.PositiveIntegerField("Total Number Of Units", default=1)
    no_of_available_units = models.PositiveIntegerField("Total Number of Available Units", default=1)
    property_type = models.ForeignKey(PropertyType, related_name='property_type', on_delete=models.SET_NULL, null=True, blank=True)
    list_property = models.BooleanField(default=False, help_text="Do you want to list this property?")
    manager = models.ForeignKey("client_user.ClientUsers", on_delete=models.SET_NULL, null=True, blank=True, related_name='manager')
    is_verified = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.title}"
    
    
    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.property_type + ' located at ' + self.address
        super().save(*args, **kwargs)

    
    def property_unique_ID(self):
        """
        Generates a schema-aware unique identifier for a property.

        Returns:
            str: A string combining the schema name and the property's unique ID.
        """
        schema_name = connection.schema_name  # Get the current schema name
        uid = self.unique_id  # Assume 'unique_id' is a field in the model

        # Ensure both schema_name and uid are non-empty
        if not schema_name or not uid:
            raise ValueError("Schema name or unique_id is missing!")

        return f"{schema_name}:{uid}"
    
    def total_payments(self):
        # return "total payment"
        from payment_track.models import Payment
        return Payment.objects.filter(
            property_unique_id__in=self.units.values_list('unique_id', flat=True),verified=True,
            ).aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    

class PropertyListingModel(models.Model):
    property_model = models.OneToOneField("property.PropertyModel", on_delete=models.CASCADE, related_name="listing")
    on_sale = models.BooleanField('For Sale', default=False)
    collect_rent = models.BooleanField('Do you collect rent on the property or on behave of the property owner?', default=True)
    allow_online_payment = models.BooleanField(default=True)
    vid_file = models.FileField('Video File', upload_to="BuildingExterior/video/building/", blank=True, null=True)
    is_newly_built = models.BooleanField("Newly Built", default=False)
    description = models.TextField(null=True, blank=True)
    has_electricity = models.BooleanField(default=True)
    water = models.BooleanField(default=True)
    images = GenericRelation("Image", related_query_name="property_images")
    features = models.ManyToManyField(AmenitiesModels,  help_text='You can select more than one.')
    property_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True, default=0.00)
    tenant_agreement = models.FileField('Tenant Agreement', upload_to="documents/TAs/", null=True, blank=True, default=get_default_file)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    
    
    def __str__(self) -> str:
        return f"{self.property_model}"
    



# class UnitType(models.Model):
#     """What type of unit is it eg: residential or commercial
#     """
#     name = models.CharField(max_length=50)
#     timestamp = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self) -> str:
#         return self.name
    

class AccommodationType(models.Model):
    """ What type of accommodation is the unit. eg: 3 BedRooms or Office or Warehouse
    or Self Contain
    """
    name = models.CharField(max_length=50)
    # unit_type = models.ForeignKey(UnitType, related_name="accommodation_unit_type", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.name



class Unit(models.Model):
    
    property_id = models.ForeignKey("PropertyModel", related_name='units', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    # unit_type = models.ForeignKey(UnitType, related_name='unit_type', on_delete=models.SET_NULL, null=True, blank=True)
    unique_id = models.UUIDField(default=uuid.uuid4, unique=True)
    unit_number = models.CharField(max_length=50)
    taken = models.BooleanField(default=False)
    tenant_id = models.CharField(max_length=50, null=True, blank=True)
    price_per_year = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    accommodation_type = models.ForeignKey(AccommodationType, related_name='accommodation_type', on_delete=models.SET_NULL, null=True, blank=True)
    list_property = models.BooleanField(default=False, help_text="Do you want to list this unit?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.unit_number} ({self.unit_type})"
    
    def save(self, *args, **kwargs):
        # self.tenant_id = self.tenant_id if self.tenant_id else None
        if self.taken:
            self.list_property = False
        
        if self.list_property:
            self.taken = False
            
        super().save(*args, **kwargs)
       
        
    def unit_unique_ID(self):
        """
        Generates a schema-aware unique identifier for a unit.

        Returns:
            str: A string combining the schema name and the unit's unique ID.
        """
        schema_name = connection.schema_name  # Get the current schema name
        uid = self.unique_id  # Assume 'unique_id' is a field in the model

        # Ensure both schema_name and uid are non-empty
        if not schema_name or not uid:
            raise ValueError("Schema name or unique_id is missing!")

        return f"{schema_name}:{uid}"
    
    
    def unit_tenant_ID(self):
        """
        Generates a schema-aware tenant-specific identifier for a unit.

        Returns:
            str: A string combining the schema name and the unit's tenant ID.
        """
        schema_name = connection.schema_name  # Get the current schema name
        tenant_id = self.tenant_id  # Assume 'tenant_id' is a field in the model

        # Ensure both schema_name and tenant_id are non-empty
        if not schema_name or not tenant_id:
            raise ValueError("Schema name or tenant_id is missing!")

        return f"{schema_name}:{tenant_id}"

    def total_payments(self):
        # return "total payment"
        from payment_track.models import Payment
        return Payment.objects.filter(
            property_unique_id__in=self.apartments.values_list('unique_id', flat=True),verified=True,
            ).aggregate(models.Sum('amount'))['amount__sum'] or 0
    


class UnitListing(models.Model):
    unit_model = models.OneToOneField(Unit, on_delete=models.CASCADE, related_name="unit_listing")
    description = models.TextField('Description', max_length=320, blank=True, null=True)
    no_of_baths = models.IntegerField('No Of Baths', default=0)
    images = GenericRelation("property.Image", related_query_name="unit_images")
    vid_file = models.FileField('Video File', upload_to="BuildingInterior/video/flat", blank=True, null=True)
    features = models.ManyToManyField('property.AmenitiesModels', help_text='You can select more than one.')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return str(self.unit_model)
    
    


class InspectionModel(models.Model):
    tenant_id = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    unit_id = models.CharField(max_length=100)
    property_address = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.date}"
    

