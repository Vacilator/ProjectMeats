"""
Django admin configuration for Customers.

Provides a user-friendly admin interface for managing Customer records
migrated from PowerApps pro_customer.
"""
from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Admin interface for Customer model.
    
    Configured to show PowerApps field mappings and provide
    efficient management of migrated data.
    """
    
    # List view configuration
    list_display = [
        'name',
        'status',
        'created_on',
        'owner'
    ]
    
    list_filter = [
        'status',
        'created_on',
        'modified_on',
        'owner'
    ]
    
    search_fields = [
        'name'
    ]
    
    # Detail view configuration
    fieldsets = (
        ('Basic Information (PowerApps: pro_customer)', {
            'fields': ('name', 'status'),
            'description': 'Core fields migrated from PowerApps pro_customer entity'
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
        self.message_user(request, f'{updated} customers marked as active.')
    mark_active.short_description = "Mark selected customers as active"
    
    def mark_inactive(self, request, queryset):
        """Bulk action to mark records as inactive (soft delete)."""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} customers marked as inactive.')
    mark_inactive.short_description = "Mark selected customers as inactive"
    
    def save_model(self, request, obj, form, change):
        """Auto-set ownership fields on save."""
        if not change:  # Creating new record
            obj.created_by = request.user
            obj.owner = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)
