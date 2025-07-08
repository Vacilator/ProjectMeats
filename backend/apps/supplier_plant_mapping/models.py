"""
Supplier Plant Mapping models for ProjectMeats.
"""
from django.db import models
from apps.core.models import OwnedModel, StatusModel


class SupplierPlantMapping(OwnedModel, StatusModel):
    """Supplier Plant Mapping entity migrated from PowerApps pro_supplierplantmapping."""
    
    name = models.CharField(max_length=850, help_text="Mapping name")
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.PROTECT, related_name='plant_mappings')
    plant = models.ForeignKey('plants.Plant', on_delete=models.PROTECT, related_name='supplier_mappings')
    
    class Meta:
        db_table = 'supplier_plant_mapping_supplierplantmapping'
        verbose_name = 'Supplier Plant Mapping'
        verbose_name_plural = 'Supplier Plant Mappings'
        ordering = ['name']
        unique_together = ['supplier', 'plant']
    
    def __str__(self):
        return f"{self.supplier.name} - {self.plant.name}"
    
    @classmethod
    def get_powerapps_entity_name(cls):
        return "pro_supplierplantmapping"
