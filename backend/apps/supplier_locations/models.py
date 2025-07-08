"""
Supplier Locations models for ProjectMeats.
"""
from django.db import models
from apps.core.models import OwnedModel, StatusModel


class SupplierLocation(OwnedModel, StatusModel):
    """Supplier Location entity migrated from PowerApps pro_supplier_locations."""
    
    name = models.CharField(max_length=850, help_text="Location name")
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.PROTECT, related_name='locations')
    address = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        db_table = 'supplier_locations_supplierlocation'
        verbose_name = 'Supplier Location'
        verbose_name_plural = 'Supplier Locations'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.supplier.name} - {self.name}"
    
    @classmethod
    def get_powerapps_entity_name(cls):
        return "pro_supplier_locations"
