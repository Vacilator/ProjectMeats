"""
Django admin configuration for Suppliers.

Provides a user-friendly admin interface for managing Supplier records
migrated from PowerApps cr7c4_supplier.
"""
from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """
    Admin interface for Supplier model.
    
    Configured to show PowerApps field mappings and provide
    efficient management of migrated data.
    """
    
    # List view configuration
    list_display = [
        'name',
        'status',
        'delivery_type_profile',
        'has_credit_application',
        'has_accounts_receivable',
        'accounts_receivable',
        'created_on',
        'owner'
    ]
    
    list_filter = [
        'status',
        'delivery_type_profile',
        'created_on',
        'modified_on',
        'owner',
        'accounts_receivable'
    ]
    
    search_fields = [
        'name',
        'accounts_receivable__name'
    ]
    
    # Detail view configuration
    fieldsets = (
        ('Basic Information (PowerApps: cr7c4_supplier)', {
            'fields': ('name', 'status', 'delivery_type_profile'),
            'description': 'Core fields migrated from PowerApps cr7c4_supplier entity'
        }),
        ('Credit Information (PowerApps: Credit Fields)', {
            'fields': ('credit_application_date',),
            'description': 'Credit application tracking information'
        }),
        ('Relationships (PowerApps: Lookup Fields)', {
            'fields': ('accounts_receivable',),
            'description': 'Relationships to other entities'
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
        self.message_user(request, f'{updated} suppliers marked as active.')
    mark_active.short_description = "Mark selected suppliers as active"
    
    def mark_inactive(self, request, queryset):
        """Bulk action to mark records as inactive (soft delete)."""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} suppliers marked as inactive.')
    mark_inactive.short_description = "Mark selected suppliers as inactive"
    
    def has_credit_application(self, obj):
        """Display whether the record has credit application date set."""
        return obj.has_credit_application
    has_credit_application.boolean = True
    has_credit_application.short_description = "Has Credit Application"
    
    def has_accounts_receivable(self, obj):
        """Display whether the record is linked to accounts receivable."""
        return obj.has_accounts_receivable
    has_accounts_receivable.boolean = True
    has_accounts_receivable.short_description = "Linked to A/R"
    
    def save_model(self, request, obj, form, change):
        """Auto-set ownership fields on save."""
        if not change:  # Creating new record
            obj.created_by = request.user
            obj.owner = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)
