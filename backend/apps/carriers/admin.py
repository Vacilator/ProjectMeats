"""
Carriers admin configuration for ProjectMeats.

Django admin interface for CarrierInfo entity
migrated from PowerApps cr7c4_carrierinfo.
"""
from django.contrib import admin
from .models import CarrierInfo


@admin.register(CarrierInfo)
class CarrierInfoAdmin(admin.ModelAdmin):
    """
    Admin interface for CarrierInfo model.
    
    Provides comprehensive management interface with PowerApps field documentation
    and bulk actions for status management.
    """
    
    list_display = [
        'name',
        'contact_name',
        'phone',
        'email',
        'has_address',
        'has_contact_details',
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
        'address',
        'contact_name',
        'phone',
        'email',
        'owner__username',
        'created_by__username'
    ]
    
    fieldsets = (
        ('Carrier Information (PowerApps: cr7c4_carrierinfo)', {
            'fields': ('name', 'address', 'status'),
            'description': 'Core carrier information migrated from PowerApps cr7c4_carrierinfo entity'
        }),
        ('Contact Details (PowerApps: Contact Fields)', {
            'fields': ('contact_name', 'phone', 'email'),
            'description': 'Contact information fields from PowerApps'
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
        self.message_user(request, f'{updated} carrier infos marked as active.')
    mark_active.short_description = "Mark selected carrier infos as active"
    
    def mark_inactive(self, request, queryset):
        """Bulk action to mark records as inactive (soft delete)."""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} carrier infos marked as inactive.')
    mark_inactive.short_description = "Mark selected carrier infos as inactive"
    
    def has_address(self, obj):
        """Display whether the record has address information."""
        return obj.has_address
    has_address.boolean = True
    has_address.short_description = "Has Address"
    
    def has_contact_details(self, obj):
        """Display whether the record has contact details."""
        return obj.has_contact_details
    has_contact_details.boolean = True
    has_contact_details.short_description = "Has Contact Details"
    
    def save_model(self, request, obj, form, change):
        """Auto-set ownership fields on save."""
        if not change:  # Creating new record
            obj.created_by = request.user
            obj.owner = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)