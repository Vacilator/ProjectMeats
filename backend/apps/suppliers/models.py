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
    
    # Plant relationship - now available with Plant entity implementation
    plant = models.ForeignKey(
        'plants.Plant',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='supplier_mappings',
        help_text="Equivalent to PowerApps Plant lookup field"
    )
    
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
