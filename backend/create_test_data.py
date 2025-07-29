#!/usr/bin/env python
"""
Comprehensive Test Data Creation Script

This script creates comprehensive test data for all ProjectMeats entities
to thoroughly test all forms and CRUD operations.
"""

import os
import sys
from datetime import timedelta

import django
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectmeats.settings")
django.setup()

from django.contrib.auth.models import User

from apps.accounts_receivables.models import AccountsReceivable
from apps.carriers.models import CarrierInfo
from apps.contacts.models import ContactInfo
from apps.customers.models import Customer
from apps.plants.models import Plant
from apps.purchase_orders.models import PurchaseOrder
from apps.suppliers.models import (Supplier, SupplierLocation,
                                   SupplierPlantMapping)


def create_users():
    """Create test users for ownership."""
    print("Creating test users...")

    users = []
    for i in range(1, 4):
        user, created = User.objects.get_or_create(
            username=f"testuser{i}",
            defaults={
                "email": f"testuser{i}@projectmeats.com",
                "first_name": f"Test{i}",
                "last_name": "User",
                "is_active": True,
            },
        )
        if created:
            user.set_password("testpass123")
            user.save()
        users.append(user)
        print(f"  ✓ Created user: {user.username}")

    return users


def create_accounts_receivables(users):
    """Create comprehensive test data for AccountsReceivable."""
    print("\nCreating AccountsReceivable test data...")

    test_data = [
        {
            "name": "AR-001 Premium Beef Sales",
            "email": "ar001@premiumbeef.com",
            "phone": "+1-555-0101",
            "terms": "30",
            "status": "active",
        },
        {
            "name": "AR-002 International Pork Export",
            "email": "ar002@intlmeat.com",
            "phone": "+1-555-0102",
            "terms": "45",
            "status": "active",
        },
        {
            "name": "AR-003 Local Poultry Distributor",
            "email": "ar003@localpoultry.com",
            "phone": "+1-555-0103",
            "terms": "60",
            "status": "inactive",
        },
        {
            "name": "AR-004 Specialty Meats LLC",
            "email": "ar004@specialtymeats.com",
            "phone": "+1-555-0104",
            "terms": "15",
            "status": "active",
        },
    ]

    for i, data in enumerate(test_data):
        ar, created = AccountsReceivable.objects.get_or_create(
            name=data["name"],
            defaults={
                **data,
                "created_by": users[i % len(users)],
                "modified_by": users[i % len(users)],
                "owner": users[i % len(users)],
            },
        )
        if created:
            print(f"  ✓ Created AccountsReceivable: {ar.name}")

    return AccountsReceivable.objects.all()


def create_suppliers(users, accounts_receivables):
    """Create comprehensive test data for Suppliers."""
    print("\nCreating Supplier test data...")

    test_data = [
        {
            "name": "Prime Beef Suppliers Inc",
            "delivery_type_profile": True,
            "credit_application_date": timezone.now() - timedelta(days=30),
            "accounts_receivable": accounts_receivables[0]
            if accounts_receivables
            else None,
            "status": "active",
        },
        {
            "name": "Global Pork Distributors",
            "delivery_type_profile": False,
            "credit_application_date": timezone.now() - timedelta(days=15),
            "accounts_receivable": accounts_receivables[1]
            if len(accounts_receivables) > 1
            else None,
            "status": "active",
        },
        {
            "name": "Local Farm Collective",
            "delivery_type_profile": True,
            "credit_application_date": None,
            "accounts_receivable": None,
            "status": "active",
        },
        {
            "name": "Inactive Meat Supplier",
            "delivery_type_profile": False,
            "credit_application_date": timezone.now() - timedelta(days=60),
            "accounts_receivable": accounts_receivables[2]
            if len(accounts_receivables) > 2
            else None,
            "status": "inactive",
        },
    ]

    for i, data in enumerate(test_data):
        supplier, created = Supplier.objects.get_or_create(
            name=data["name"],
            defaults={
                **data,
                "created_by": users[i % len(users)],
                "modified_by": users[i % len(users)],
                "owner": users[i % len(users)],
            },
        )
        if created:
            print(f"  ✓ Created Supplier: {supplier.name}")

    return Supplier.objects.all()


def create_customers(users):
    """Create comprehensive test data for Customers."""
    print("\nCreating Customer test data...")

    test_data = [
        {"name": "Restaurant Chain Holdings", "status": "active"},
        {"name": "Wholesale Food Distributors", "status": "active"},
        {"name": "Local Grocery Chain", "status": "active"},
        {"name": "Former Customer Corp", "status": "inactive"},
    ]

    for i, data in enumerate(test_data):
        customer, created = Customer.objects.get_or_create(
            name=data["name"],
            defaults={
                **data,
                "created_by": users[i % len(users)],
                "modified_by": users[i % len(users)],
                "owner": users[i % len(users)],
            },
        )
        if created:
            print(f"  ✓ Created Customer: {customer.name}")

    return Customer.objects.all()


def create_plants(users, suppliers):
    """Create comprehensive test data for Plants."""
    print("\nCreating Plant test data...")

    test_data = [
        {
            "name": "Primary Processing Plant A",
            "location": "Chicago, IL",
            "plant_type": "processing",
            "release_number": "REL-001",
            "load_pickup_requirements": "dock_loading, refrigerated_truck",
            "storage": "frozen, refrigerated",
            "supplier": suppliers[0] if suppliers else None,
            "status": "active",
        },
        {
            "name": "Distribution Center B",
            "location": "Dallas, TX",
            "plant_type": "distribution",
            "release_number": "REL-002",
            "load_pickup_requirements": "loading_dock",
            "storage": "dry, refrigerated",
            "supplier": suppliers[1] if len(suppliers) > 1 else None,
            "status": "active",
        },
        {
            "name": "Storage Facility C",
            "location": "Denver, CO",
            "plant_type": "storage",
            "release_number": "REL-003",
            "load_pickup_requirements": "ground_level_loading",
            "storage": "frozen",
            "supplier": suppliers[0] if suppliers else None,
            "status": "active",
        },
        {
            "name": "Inactive Plant D",
            "location": "Phoenix, AZ",
            "plant_type": "processing",
            "release_number": "REL-004",
            "load_pickup_requirements": "dock_loading",
            "storage": "ambient",
            "supplier": suppliers[2] if len(suppliers) > 2 else None,
            "status": "inactive",
        },
    ]

    for i, data in enumerate(test_data):
        plant, created = Plant.objects.get_or_create(
            name=data["name"],
            defaults={
                **data,
                "created_by": users[i % len(users)],
                "modified_by": users[i % len(users)],
                "owner": users[i % len(users)],
            },
        )
        if created:
            print(f"  ✓ Created Plant: {plant.name}")

    return Plant.objects.all()


def create_supplier_locations(users, suppliers):
    """Create comprehensive test data for SupplierLocations."""
    print("\nCreating SupplierLocation test data...")

    test_data = [
        {
            "name": "Headquarters",
            "address": "123 Main Street",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "country": "USA",
            "location_type": "headquarters",
            "contact_name": "John Smith",
            "contact_phone": "555-1001",
            "contact_email": "john.smith@supplier1.com",
            "supplier": suppliers[0] if suppliers else None,
            "notes": "Main corporate office with full facilities",
            "status": "active",
        },
        {
            "name": "Warehouse Alpha",
            "address": "456 Storage Avenue",
            "city": "Dallas",
            "state": "TX",
            "postal_code": "75201",
            "country": "USA",
            "location_type": "warehouse",
            "contact_name": "Jane Doe",
            "contact_phone": "555-2002",
            "contact_email": "jane.doe@supplier2.com",
            "supplier": suppliers[1] if len(suppliers) > 1 else None,
            "notes": "Primary distribution warehouse",
            "status": "active",
        },
        {
            "name": "Processing Plant Beta",
            "address": "789 Industrial Blvd",
            "city": "Kansas City",
            "state": "MO",
            "postal_code": "64108",
            "country": "USA",
            "location_type": "processing_plant",
            "contact_name": "Mike Johnson",
            "contact_phone": "555-3003",
            "contact_email": "mike.johnson@supplier1.com",
            "supplier": suppliers[0] if suppliers else None,
            "notes": "Meat processing facility",
            "status": "active",
        },
        {
            "name": "Closed Office",
            "address": "321 Old Street",
            "city": "Denver",
            "state": "CO",
            "postal_code": "80202",
            "country": "USA",
            "location_type": "office",
            "contact_name": "Sarah Wilson",
            "contact_phone": "555-4004",
            "contact_email": "sarah.wilson@supplier3.com",
            "supplier": suppliers[2] if len(suppliers) > 2 else None,
            "notes": "Former regional office",
            "status": "inactive",
        },
    ]

    for i, data in enumerate(test_data):
        location, created = SupplierLocation.objects.get_or_create(
            name=data["name"],
            supplier=data["supplier"],
            defaults={
                **{k: v for k, v in data.items() if k != "supplier"},
                "created_by": users[i % len(users)],
                "modified_by": users[i % len(users)],
                "owner": users[i % len(users)],
            },
        )
        if created:
            print(f"  ✓ Created SupplierLocation: {location.name}")

    return SupplierLocation.objects.all()


def create_contact_info(users, suppliers, customers):
    """Create comprehensive test data for ContactInfo."""
    print("\nCreating ContactInfo test data...")

    test_data = [
        {
            "name": "Sales Manager Contact",
            "email": "sales@supplier1.com",
            "phone": "555-7001",
            "position": "Sales Manager",
            "contact_type": "primary",
            "supplier": suppliers[0] if suppliers else None,
            "customer": None,
            "status": "active",
        },
        {
            "name": "Purchasing Director",
            "email": "purchasing@customer1.com",
            "phone": "555-8002",
            "position": "Purchasing Director",
            "contact_type": "primary",
            "supplier": None,
            "customer": customers[0] if customers else None,
            "status": "active",
        },
        {
            "name": "Operations Coordinator",
            "email": "ops@supplier2.com",
            "phone": "555-9003",
            "position": "Operations Coordinator",
            "contact_type": "secondary",
            "supplier": suppliers[1] if len(suppliers) > 1 else None,
            "customer": None,
            "status": "active",
        },
        {
            "name": "Former Contact",
            "email": "old@contact.com",
            "phone": "555-0004",
            "position": "Account Manager",
            "contact_type": "other",
            "supplier": suppliers[2] if len(suppliers) > 2 else None,
            "customer": None,
            "status": "inactive",
        },
    ]

    for i, data in enumerate(test_data):
        contact, created = ContactInfo.objects.get_or_create(
            name=data["name"],
            defaults={
                **data,
                "created_by": users[i % len(users)],
                "modified_by": users[i % len(users)],
                "owner": users[i % len(users)],
            },
        )
        if created:
            print(f"  ✓ Created ContactInfo: {contact.name}")

    return ContactInfo.objects.all()


def create_carrier_info(users, suppliers):
    """Create comprehensive test data for CarrierInfo."""
    print("\nCreating CarrierInfo test data...")

    test_data = [
        {
            "name": "Swift Transportation",
            "address": "123 Trucking Lane, Phoenix, AZ 85001",
            "contact_name": "Bob Carrier",
            "release_number": "CARR-001",
            "supplier": suppliers[0] if suppliers else None,
            "status": "active",
        },
        {
            "name": "Regional Freight Lines",
            "address": "456 Rail Road Ave, Kansas City, MO 64108",
            "contact_name": "Alice Rail",
            "release_number": "CARR-002",
            "supplier": suppliers[1] if len(suppliers) > 1 else None,
            "status": "active",
        },
    ]

    for i, data in enumerate(test_data):
        carrier, created = CarrierInfo.objects.get_or_create(
            name=data["name"],
            defaults={
                **data,
                "created_by": users[i % len(users)],
                "modified_by": users[i % len(users)],
                "owner": users[i % len(users)],
            },
        )
        if created:
            print(f"  ✓ Created CarrierInfo: {carrier.name}")

    return CarrierInfo.objects.all()


def create_purchase_orders(users, suppliers, customers):
    """Create comprehensive test data for PurchaseOrders."""
    print("\nCreating PurchaseOrder test data...")

    test_data = [
        {
            "po_number": "PO-2025-001",
            "item": "Premium ground beef, 80/20 blend",
            "quantity": 1000,
            "price_per_unit": "4.50",
            "purchase_date": timezone.now(),
            "fulfillment_date": timezone.now() + timedelta(days=7),
            "supplier": suppliers[0] if suppliers else None,
            "customer": customers[0] if customers else None,
            "customer_documents": "customer_specs.pdf",
            "supplier_documents": "shipping_manifest.pdf",
            "status": "active",
        },
        {
            "po_number": "PO-2025-002",
            "item": "Pork shoulder, bone-in",
            "quantity": 500,
            "price_per_unit": "3.75",
            "purchase_date": timezone.now() - timedelta(days=3),
            "fulfillment_date": timezone.now() + timedelta(days=2),
            "supplier": suppliers[1] if len(suppliers) > 1 else None,
            "customer": customers[1] if len(customers) > 1 else None,
            "customer_documents": "weekly_order.pdf",
            "supplier_documents": "invoice_123.pdf",
            "status": "active",
        },
        {
            "po_number": "PO-2025-003",
            "item": "Chicken breasts, boneless",
            "quantity": 750,
            "price_per_unit": "2.85",
            "purchase_date": timezone.now() - timedelta(days=10),
            "fulfillment_date": timezone.now() - timedelta(days=3),
            "supplier": suppliers[0] if suppliers else None,
            "customer": customers[2] if len(customers) > 2 else None,
            "customer_documents": "delivery_confirmation.pdf",
            "supplier_documents": "quality_cert.pdf",
            "status": "active",
        },
    ]

    for i, data in enumerate(test_data):
        po, created = PurchaseOrder.objects.get_or_create(
            po_number=data["po_number"],
            defaults={
                **data,
                "created_by": users[i % len(users)],
                "modified_by": users[i % len(users)],
                "owner": users[i % len(users)],
            },
        )
        if created:
            print(f"  ✓ Created PurchaseOrder: {po.po_number}")

    return PurchaseOrder.objects.all()


def create_supplier_plant_mappings(users, suppliers, plants, customers, contacts):
    """Create comprehensive test data for SupplierPlantMappings."""
    print("\nCreating SupplierPlantMapping test data...")

    test_data = [
        {
            "name": "Supplier 1 - Plant A Mapping",
            "supplier": suppliers[0] if suppliers else None,
            "plant": plants[0] if plants else None,
            "customer": customers[0] if customers else None,
            "contact_info": contacts[0] if contacts else None,
            "status": "active",
        },
        {
            "name": "Supplier 2 - Plant B Mapping",
            "supplier": suppliers[1] if len(suppliers) > 1 else None,
            "plant": plants[1] if len(plants) > 1 else None,
            "customer": customers[1] if len(customers) > 1 else None,
            "contact_info": contacts[1] if len(contacts) > 1 else None,
            "status": "active",
        },
    ]

    for i, data in enumerate(test_data):
        mapping, created = SupplierPlantMapping.objects.get_or_create(
            name=data["name"],
            defaults={
                **data,
                "created_by": users[i % len(users)],
                "modified_by": users[i % len(users)],
                "owner": users[i % len(users)],
            },
        )
        if created:
            print(f"  ✓ Created SupplierPlantMapping: {mapping.name}")

    return SupplierPlantMapping.objects.all()


def main():
    """Main function to create all test data."""
    print("🚀 Creating comprehensive test data for ProjectMeats...")
    print("=" * 60)

    # Create test users
    users = create_users()

    # Create entities in dependency order
    accounts_receivables = create_accounts_receivables(users)
    suppliers = create_suppliers(users, accounts_receivables)
    customers = create_customers(users)
    plants = create_plants(users, suppliers)
    # Create extended entities (currently not used in summary, but needed for relationships)
    create_supplier_locations(users, suppliers)
    contacts = create_contact_info(users, suppliers, customers)
    create_carrier_info(users, suppliers)
    create_purchase_orders(users, suppliers, customers)
    create_supplier_plant_mappings(users, suppliers, plants, customers, contacts)

    print("\n" + "=" * 60)
    print("✅ Test data creation completed successfully!")
    print("📊 Summary:")
    print(f"   Users: {User.objects.count()}")
    print(f"   AccountsReceivables: {AccountsReceivable.objects.count()}")
    print(f"   Suppliers: {Supplier.objects.count()}")
    print(f"   Customers: {Customer.objects.count()}")
    print(f"   Plants: {Plant.objects.count()}")
    print(f"   SupplierLocations: {SupplierLocation.objects.count()}")
    print(f"   ContactInfo: {ContactInfo.objects.count()}")
    print(f"   CarrierInfo: {CarrierInfo.objects.count()}")
    print(f"   PurchaseOrders: {PurchaseOrder.objects.count()}")
    print(f"   SupplierPlantMappings: {SupplierPlantMapping.objects.count()}")
    print("\n🎯 Ready for comprehensive frontend testing!")


if __name__ == "__main__":
    main()
