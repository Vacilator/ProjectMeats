"""
Django admin configuration for Carriers.
"""
from django.contrib import admin
from .models import CarrierInfo


@admin.register(CarrierInfo)
class CarrierInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'status', 'created_on', 'owner']
    list_filter = ['status', 'created_on', 'modified_on', 'owner']
    search_fields = ['name', 'address', 'phone']
    readonly_fields = ['created_on', 'modified_on']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information (PowerApps: cr7c4_carrierinfo)', {
            'fields': ('name', 'address', 'phone', 'status'),
        }),
        ('Ownership (PowerApps: Owner/Created/Modified)', {
            'fields': ('owner', 'created_by', 'modified_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps (PowerApps: CreatedOn/ModifiedOn)', {
            'fields': ('created_on', 'modified_on'),
            'classes': ('collapse',)
        })
    )
