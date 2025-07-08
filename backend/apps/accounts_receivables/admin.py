"""
Django admin configuration for Accounts Receivables.

Provides a user-friendly admin interface for managing AccountsReceivable records
migrated from PowerApps cr7c4_accountsreceivables.
"""
from django.contrib import admin
from .models import AccountsReceivable


@admin.register(AccountsReceivable)
class AccountsReceivableAdmin(admin.ModelAdmin):
    """
    Admin interface for AccountsReceivable model.
    
    Configured to show PowerApps field mappings and provide
    efficient management of migrated data.
    """
    
    # List view configuration
    list_display = [
        'name',
        'email', 
        'phone',
        'status',
        'has_contact_info',
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
        'name',
        'email',
        'phone',
        'terms'
    ]
    
    # Detail view configuration
    fieldsets = (
        ('Basic Information (PowerApps: cr7c4_accountsreceivables)', {
            'fields': ('name', 'email', 'phone', 'terms', 'status'),
            'description': 'Core fields migrated from PowerApps cr7c4_accountsreceivables entity'
        }),
        ('Ownership (PowerApps: Owner/Created/Modified)', {
            'fields': ('owner', 'created_by', 'modified_by'),
            'classes': ('collapse',),
            'description': 'PowerApps ownership fields mapped to Django User model'
        }),
        ('Timestamps (PowerApps: CreatedOn/ModifiedOn)', {
            'fields': ('created_on', 'modified_on'),
            'classes': ('collapse',),
            'description': 'Automatic timestamp fields from PowerApps'
        }),
    )
    
    readonly_fields = ['created_on', 'modified_on']
    
    # Ordering and pagination
    ordering = ['name']
    list_per_page = 25
    
    # Actions
    actions = ['mark_active', 'mark_inactive']
    
    def mark_active(self, request, queryset):
        """Bulk action to mark records as active."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} records marked as active.')
    mark_active.short_description = "Mark selected accounts receivable as active"
    
    def mark_inactive(self, request, queryset):
        """Bulk action to mark records as inactive (soft delete)."""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} records marked as inactive.')
    mark_inactive.short_description = "Mark selected accounts receivable as inactive"
    
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
