"""
Suppliers models for ProjectMeats.

Migrated from PowerApps entity: cr7c4_supplier
Original description: "This table contains records of supplier information"

PowerApps Entity Name: cr7c4_Supplier
Django Model Name: Supplier
"""
from django.db import models
from django.core.validators import EmailValidator
from apps.core.models import OwnedModel, StatusModel


class Supplier(OwnedModel, StatusModel):
    """
    Supplier entity migrated from PowerApps cr7c4_supplier.
    
    PowerApps Field Mappings:
    - cr7c4_nameofsupplier -> name (Primary field, required)
    - cr7c4_datewhencreditapplicationwassent -> credit_application_date
    - cr7c4_profileofsupplierdeliverytype -> delivery_type_profile (boolean)
    - cr7c4_accountsreceivablesid -> accounts_receivable (foreign key, optional)
    - cr7c4_plant -> plant (foreign key, will be implemented when Plant entity is migrated)
    + Standard PowerApps audit fields via OwnedModel base class
    """
    
    # Primary field - equivalent to cr7c4_nameofsupplier (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=850,  # PowerApps MaxLength was 850
        help_text="Equivalent to PowerApps cr7c4_nameofsupplier field (Primary Name)"
    )
    
    # Credit application date - equivalent to cr7c4_datewhencreditapplicationwassent
    credit_application_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_datewhencreditapplicationwassent field"
    )
    
    # Delivery type profile - equivalent to cr7c4_profileofsupplierdeliverytype
    delivery_type_profile = models.BooleanField(
        default=False,
        help_text="Equivalent to PowerApps cr7c4_profileofsupplierdeliverytype field"
    )
    
    # Foreign key to Accounts Receivable - equivalent to cr7c4_accountsreceivablesid
    accounts_receivable = models.ForeignKey(
        'accounts_receivables.AccountsReceivable',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='suppliers',
        help_text="Equivalent to PowerApps cr7c4_accountsreceivablesid field"
    )
    
    # Note: Plant foreign key will be added when Plant entity is migrated
    # plant = models.ForeignKey('plants.Plant', ...)
    
    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        db_table = "suppliers"
        ordering = ['name']
        
    def __str__(self):
        """String representation using the primary name field."""
        return self.name
    
    def clean(self):
        """Model validation - ensure name is provided."""
        from django.core.exceptions import ValidationError
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Name is required and cannot be empty.'})
    
    @property
    def has_credit_application(self):
        """Helper property to check if credit application date is set."""
        return self.credit_application_date is not None
    
    @property
    def has_accounts_receivable(self):
        """Helper property to check if linked to accounts receivable."""
        return self.accounts_receivable is not None
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "cr7c4_supplier"


class SupplierPlantMapping(OwnedModel, StatusModel):
    """
    Supplier Plant Mapping entity migrated from PowerApps pro_supplierplantmapping.
    
    PowerApps Field Mappings:
    - pro_supplierplantmapping1 -> name (Primary field, required)
    - pro_supplierplantmappingid -> id (Django auto-generated)
    - Supplier relationship -> supplier (foreign key)
    - Customer relationship -> customer (foreign key)  
    - Contact relationship -> contact_info (foreign key)
    - Plant relationship -> plant (foreign key, placeholder for future Plant entity)
    + Standard PowerApps audit fields via OwnedModel base class
    + Standard PowerApps status fields via StatusModel base class
    
    PowerApps Description: "This table contains a mapping relationship between suppliers, customers, contacts, plants, and documents."
    """
    
    # Primary field - equivalent to pro_supplierplantmapping1 (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=850,  # PowerApps MaxLength was 850
        help_text="Equivalent to PowerApps pro_supplierplantmapping1 field (Primary Name)"
    )
    
    # Foreign key relationships - equivalent to PowerApps lookup fields
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.PROTECT,
        related_name='plant_mappings',
        help_text="Equivalent to PowerApps Supplier lookup field"
    )
    
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='supplier_plant_mappings',
        help_text="Equivalent to PowerApps Customer lookup field"
    )
    
    contact_info = models.ForeignKey(
        'contacts.ContactInfo',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='supplier_plant_mappings',
        help_text="Equivalent to PowerApps Contact Info lookup field"
    )
    
    # Plant relationship - placeholder for future Plant entity implementation
    # plant = models.ForeignKey(
    #     'plants.Plant',
    #     on_delete=models.PROTECT,
    #     blank=True,
    #     null=True,
    #     related_name='supplier_mappings',
    #     help_text="Equivalent to PowerApps Plant lookup field (placeholder)"
    # )
    
    # Document-related fields (based on PowerApps description mentioning documents)
    documents_reference = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Document references related to this supplier-plant mapping"
    )
    
    class Meta:
        verbose_name = "Supplier Plant Mapping"
        verbose_name_plural = "Supplier Plant Mappings"
        db_table = "supplier_plant_mappings"
        ordering = ['name']
        
    def __str__(self):
        """String representation using the primary name field."""
        return self.name
    
    def clean(self):
        """Model validation - ensure name is provided."""
        from django.core.exceptions import ValidationError
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Name is required and cannot be empty.'})
    
    @property
    def has_contact_info(self):
        """Helper property to check if contact info is linked."""
        return bool(self.contact_info)
    
    @property
    def has_documents(self):
        """Helper property to check if documents reference is set."""
        return bool(self.documents_reference)
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "pro_supplierplantmapping"


class SupplierLocation(OwnedModel, StatusModel):
    """
    Supplier Location entity migrated from PowerApps pro_supplier_locations.
    
    PowerApps Field Mappings:
    - pro_locationname -> name (Primary field, required)
    - pro_supplier_locationsid -> id (Django auto-generated)
    - pro_address -> address (Location address)
    - pro_city -> city (City name)
    - pro_state -> state (State/province)
    - pro_zipcode -> zip_code (Postal/ZIP code)
    - pro_country -> country (Country name)
    - pro_supplier_lookup -> supplier (Foreign key to Supplier)
    + Standard PowerApps audit fields via OwnedModel base class
    + Standard PowerApps status fields via StatusModel base class
    
    PowerApps Description: "Supplier location and address management"
    """
    
    # Primary field - equivalent to pro_locationname (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=850,  # Standard PowerApps text field length
        help_text="Equivalent to PowerApps pro_locationname field (Primary Name)"
    )
    
    # Address fields - equivalent to PowerApps address fields
    address = models.CharField(
        max_length=500,  # Street address
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_address field"
    )
    
    city = models.CharField(
        max_length=100,  # City name
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_city field"
    )
    
    state = models.CharField(
        max_length=100,  # State/province
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_state field"
    )
    
    zip_code = models.CharField(
        max_length=20,  # ZIP/postal code
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_zipcode field"
    )
    
    country = models.CharField(
        max_length=100,  # Country name
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_country field"
    )
    
    # Foreign key relationship - equivalent to PowerApps lookup field
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.PROTECT,
        related_name='locations',
        help_text="Equivalent to PowerApps pro_supplier_lookup field"
    )
    
    class Meta:
        verbose_name = "Supplier Location"
        verbose_name_plural = "Supplier Locations"
        db_table = "supplier_locations"
        ordering = ['supplier__name', 'name']
        
    def __str__(self):
        """String representation using the primary name field and supplier."""
        return f"{self.supplier.name} - {self.name}"
    
    def clean(self):
        """Model validation - ensure name is provided."""
        from django.core.exceptions import ValidationError
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Name is required and cannot be empty.'})
    
    @property
    def has_address(self):
        """Helper property to check if address information is provided."""
        return bool(self.address and self.address.strip())
    
    @property
    def has_complete_address(self):
        """Helper property to check if complete address is provided."""
        return bool(
            self.address and self.address.strip() and
            self.city and self.city.strip() and
            self.state and self.state.strip() and
            self.zip_code and self.zip_code.strip()
        )
    
    @property
    def formatted_address(self):
        """Helper property to get formatted address string."""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts) if parts else ""
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "pro_supplier_locations"
