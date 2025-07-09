"""
Tests for Carrier Info functionality.

Tests for carrier information models, API endpoints, and business logic
migrated from PowerApps cr7c4_carrierinfo entity.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import CarrierInfo
from apps.suppliers.models import Supplier

User = get_user_model()


class CarrierInfoModelTest(TestCase):
    """Test cases for CarrierInfo model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )

    def test_create_carrier_info(self):
        """Test creating a carrier info record."""
        carrier = CarrierInfo.objects.create(
            name='Test Carrier',
            address='123 Test Street',
            contact_name='John Doe',
            release_number='REL-001',
            supplier=self.supplier,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(carrier.name, 'Test Carrier')
        self.assertEqual(carrier.address, '123 Test Street')
        self.assertEqual(carrier.contact_name, 'John Doe')
        self.assertEqual(carrier.release_number, 'REL-001')
        self.assertEqual(carrier.supplier, self.supplier)
        self.assertEqual(str(carrier), 'Test Carrier')

    def test_carrier_info_properties(self):
        """Test computed properties."""
        carrier = CarrierInfo.objects.create(
            name='Test Carrier',
            address='123 Test Street',
            contact_name='John Doe',
            supplier=self.supplier,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertTrue(carrier.has_address)
        self.assertTrue(carrier.has_contact_info)
        self.assertTrue(carrier.has_supplier)

    def test_carrier_info_without_optional_fields(self):
        """Test carrier with minimal required fields."""
        carrier = CarrierInfo.objects.create(
            name='Minimal Carrier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertFalse(carrier.has_address)
        self.assertFalse(carrier.has_contact_info)
        self.assertFalse(carrier.has_supplier)

    def test_powerapps_entity_name(self):
        """Test PowerApps entity name method."""
        self.assertEqual(CarrierInfo.get_powerapps_entity_name(), 'cr7c4_carrierinfo')


class CarrierInfoAPITest(APITestCase):
    """Test cases for CarrierInfo API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.carrier = CarrierInfo.objects.create(
            name='Test Carrier',
            address='123 Test Street',
            contact_name='John Doe',
            release_number='REL-001',
            supplier=self.supplier,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )

    def test_list_carrier_infos(self):
        """Test listing carrier infos."""
        response = self.client.get('/api/v1/carrier-infos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Carrier')

    def test_retrieve_carrier_info(self):
        """Test retrieving a specific carrier info."""
        response = self.client.get(f'/api/v1/carrier-infos/{self.carrier.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Carrier')
        self.assertTrue(response.data['has_address'])

    def test_migration_info_endpoint(self):
        """Test migration info endpoint."""
        response = self.client.get('/api/v1/carrier-infos/migration_info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['powerapps_entity_name'], 'cr7c4_carrierinfo')
        self.assertEqual(response.data['django_model_name'], 'CarrierInfo')
        self.assertEqual(response.data['total_records'], 1)
        self.assertEqual(response.data['active_records'], 1)
