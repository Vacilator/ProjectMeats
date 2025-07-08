"""
Django admin configuration for Plants.

Provides a user-friendly admin interface for managing Plant records
migrated from PowerApps cr7c4_plant.
"""
from django.contrib import admin
from .models import Plant


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    """
    Admin interface for Plant model.
    
    Configured to show PowerApps field mappings and provide
    efficient management of migrated data.
    """
    
    # List view configuration
    list_display = [
        'name',
        'plant_type',
        'status',
        'created_on',
        'modified_on',
        'owner'
    ]
    
    list_filter = [
        'status',
        'plant_type',
        'created_on',
        'modified_on',
        'owner'
    ]
    
    search_fields = [
        'name',
        'plant_type'
    ]
    
    # Detail view configuration
    fieldsets = (
        ('Basic Information (PowerApps: cr7c4_plant)', {
            'fields': ('name', 'plant_type', 'status'),
            'description': 'Core plant fields migrated from PowerApps cr7c4_plant entity'
        }),
        ('Ownership (PowerApps: Owner/Created/Modified)', {
            'fields': ('owner', 'created_by', 'modified_by'),
            'description': 'PowerApps ownership and audit fields mapped to Django User model',
            'classes': ('collapse',)
        }),
        ('Timestamps (PowerApps: CreatedOn/ModifiedOn)', {
            'fields': ('created_on', 'modified_on'),
            'description': 'Auto-managed timestamp fields from PowerApps',
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_on', 'modified_on']
    
    # Ordering
    ordering = ['name']
    
    # Actions
    actions = ['mark_active', 'mark_inactive']
    
    def mark_active(self, request, queryset):
        """Bulk action to mark records as active."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} plants marked as active.')
    mark_active.short_description = "Mark selected plants as active"
    
    def mark_inactive(self, request, queryset):
        """Bulk action to mark records as inactive (soft delete)."""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} plants marked as inactive.')
    mark_inactive.short_description = "Mark selected plants as inactive"
    
    def save_model(self, request, obj, form, change):
        """Auto-set ownership fields on save."""
        if not change:  # Creating new object
            obj.created_by = request.user
            obj.owner = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)
