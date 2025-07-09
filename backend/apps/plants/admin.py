"""
Plants admin configuration for ProjectMeats.

Django admin interface for Plants entity
migrated from PowerApps cr7c4_plant.
"""
from django.contrib import admin
from .models import Plant


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    """
    Admin interface for Plant model.
    
    Provides comprehensive management interface with PowerApps field documentation
    and bulk actions for status management.
    """
    
    list_display = [
        'name',
        'location',
        'has_location',
        'has_contact_info',
        'status',
        'owner',
        'created_on',
        'modified_on'
    ]
    
    list_filter = [
        'status',
        'created_on',
        'modified_on',
        'owner',
        'created_by'
    ]
    
    search_fields = [
        'name',
        'location',
        'contact_info',
        'owner__username',
        'created_by__username'
    ]
    
    fieldsets = (
        ('Plant Information (PowerApps: cr7c4_plant)', {
            'fields': ('name', 'location', 'contact_info', 'status'),
            'description': 'Core plant information migrated from PowerApps cr7c4_plant entity'
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
    
    def has_location(self, obj):
        """Display whether the record has location information."""
        return obj.has_location
    has_location.boolean = True
    has_location.short_description = "Has Location"
    
    def has_contact_info(self, obj):
        """Display whether the record has contact information."""
        return obj.has_contact_info
    has_contact_info.boolean = True
    has_contact_info.short_description = "Has Contact Info"
    
    def save_model(self, request, obj, form, change):
        """Auto-set ownership fields on save."""
        if not change:  # Creating new record
            obj.created_by = request.user
            obj.owner = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)