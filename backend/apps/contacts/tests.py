"""
Tests for Contact Information API.

Tests the REST API endpoints for managing ContactInfo entities
migrated from PowerApps pro_contactinfo.
"""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.customers.models import Customer
from apps.suppliers.models import Supplier

from .models import ContactInfo


class ContactInfoAPITest(APITestCase):
    """Test the ContactInfo API endpoints."""

    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        # Create related objects
        self.customer = Customer.objects.create(
            name="Test Customer",
            created_by=self.user,
            modified_by=self.user,
            owner=self.user,
        )

        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            created_by=self.user,
            modified_by=self.user,
            owner=self.user,
        )

        # Create a test contact info
        self.contact_info = ContactInfo.objects.create(
            name="Test Contact",
            email="test@contact.com",
            phone="+1-555-0123",
            position="Manager",
            contact_type="Primary",
            customer=self.customer,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user,
        )

    def test_list_contact_info(self):
        """Test retrieving list of contact information."""
        url = reverse("contactinfo-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Contact")

    def test_create_contact_info(self):
        """Test creating a new contact info."""
        url = reverse("contactinfo-list")
        data = {
            "name": "New Contact",
            "email": "new@contact.com",
            "phone": "+1-555-9999",
            "position": "Director",
            "contact_type": "Secondary",
            "supplier": self.supplier.id,
            "status": "active",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactInfo.objects.count(), 2)

        new_contact = ContactInfo.objects.get(name="New Contact")
        self.assertEqual(new_contact.supplier, self.supplier)
        self.assertEqual(new_contact.created_by, self.user)

    def test_migration_info_endpoint(self):
        """Test the PowerApps migration info endpoint."""
        url = reverse("contactinfo-migration-info")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["powerapps_entity_name"], "pro_contactinfo"
        )
        self.assertEqual(response.data["django_model_name"], "ContactInfo")
        self.assertEqual(response.data["total_records"], 1)
        self.assertEqual(response.data["active_records"], 1)
        self.assertIn("field_mappings", response.data)

    def test_filtering_and_search(self):
        """Test API filtering and search capabilities."""
        url = reverse("contactinfo-list")

        # Test search
        response = self.client.get(url, {"search": "Test"})
        self.assertEqual(len(response.data["results"]), 1)

        # Test filtering by customer
        response = self.client.get(url, {"customer": self.customer.id})
        self.assertEqual(len(response.data["results"]), 1)

        # Test custom filters
        response = self.client.get(url, {"has_contact_details": "true"})
        self.assertEqual(len(response.data["results"]), 1)

        response = self.client.get(url, {"has_relationships": "true"})
        self.assertEqual(len(response.data["results"]), 1)
