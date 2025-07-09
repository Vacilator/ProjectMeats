from django.contrib import admin

"""
Django admin configuration for Plants app.

Provides admin interface for managing Plant entities
migrated from PowerApps cr7c4_plant.
"""
from django.contrib import admin
from .models import Plant


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    """
    Admin interface for Plant model.
    
    Provides comprehensive management interface with PowerApps field mappings
    and helpful actions for the migrated Plant entity.
    """
    
    # List view configuration
    list_display = [
        'name',
        'location',
        'plant_type',
        'supplier',
        'status',
        'created_on',
        'modified_on',
        'owner'
    ]
    
    list_filter = [
        'status',
        'plant_type',
        'supplier',
        'created_on',
        'modified_on'
    ]
    
    search_fields = [
        'name',
        'location',
        'release_number',
        'supplier__name'
    ]
    
    # Detail view configuration
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'plant_type', 'release_number'),
            'description': 'Primary plant information from PowerApps cr7c4_plant'
        }),
        ('Operational Details', {
            'fields': ('load_pickup_requirements', 'storage'),
            'description': 'Operational requirements and storage capabilities'
        }),
        ('Relationships', {
            'fields': ('supplier',),
            'description': 'Related entities from PowerApps lookups'
        }),
        ('Status & Ownership', {
            'fields': ('status', 'owner'),
            'description': 'PowerApps status and ownership fields'
        }),
        ('Audit Information', {
            'fields': ('created_by', 'modified_by', 'created_on', 'modified_on'),
            'classes': ('collapse',),
            'description': 'PowerApps audit trail fields (read-only)'
        })
    )
    
    readonly_fields = ['created_on', 'modified_on']
    
    # Ordering and pagination
    ordering = ['name']
    list_per_page = 25
    
    # Actions
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def mark_as_active(self, request, queryset):
        """Mark selected plants as active (PowerApps Active status)."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} plant(s) marked as active.')
    mark_as_active.short_description = 'Mark selected plants as active'
    
    def mark_as_inactive(self, request, queryset):
        """Mark selected plants as inactive (PowerApps Inactive status)."""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} plant(s) marked as inactive.')
    mark_as_inactive.short_description = 'Mark selected plants as inactive'
    
    def get_queryset(self, request):
        """Optimize queryset with related object selections."""
        return super().get_queryset(request).select_related('supplier', 'owner', 'created_by', 'modified_by')
    
    class Meta:
        verbose_name = "Plant (PowerApps cr7c4_plant)"
        verbose_name_plural = "Plants (PowerApps cr7c4_plant)"
