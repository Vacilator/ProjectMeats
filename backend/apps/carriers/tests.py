"""
Tests for Carriers API.

Tests the REST API endpoints for managing CarrierInfo entities
migrated from PowerApps cr7c4_carrierinfo.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from .models import CarrierInfo


class CarrierInfoModelTest(TestCase):
    """Test the CarrierInfo model."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
    def test_carrier_info_creation(self):
        """Test creating a carrier info."""
        carrier = CarrierInfo.objects.create(
            name='Test Carrier',
            address='Test Address',
            contact_name='John Doe',
            phone='123-456-7890',
            email='test@carrier.com',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(carrier.name, 'Test Carrier')
        self.assertEqual(carrier.address, 'Test Address')
        self.assertEqual(carrier.status, 'active')  # Default status
        self.assertTrue(carrier.has_address)
        self.assertTrue(carrier.has_contact_details)
        self.assertTrue(carrier.has_complete_contact)
        
    def test_carrier_info_str_representation(self):
        """Test the string representation."""
        carrier = CarrierInfo.objects.create(
            name='Test Carrier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        self.assertEqual(str(carrier), 'Test Carrier')
        
    def test_carrier_info_without_details(self):
        """Test carrier info without optional details."""
        carrier = CarrierInfo.objects.create(
            name='Test Carrier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        self.assertFalse(carrier.has_address)
        self.assertFalse(carrier.has_contact_details)
        self.assertFalse(carrier.has_complete_contact)
        
    def test_partial_contact_details(self):
        """Test carrier info with partial contact details."""
        carrier = CarrierInfo.objects.create(
            name='Test Carrier',
            phone='123-456-7890',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        self.assertTrue(carrier.has_contact_details)
        self.assertFalse(carrier.has_complete_contact)
        
    def test_powerapps_entity_name(self):
        """Test PowerApps entity name method."""
        self.assertEqual(CarrierInfo.get_powerapps_entity_name(), 'cr7c4_carrierinfo')


class CarrierInfoAPITest(APITestCase):
    """Test the CarrierInfo API endpoints."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
        self.carrier = CarrierInfo.objects.create(
            name='Test Carrier',
            address='Test Address',
            contact_name='John Doe',
            phone='123-456-7890',
            email='test@carrier.com',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_list_carrier_infos(self):
        """Test retrieving list of carrier infos."""
        url = reverse('carrierinfo-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Carrier')
        
    def test_create_carrier_info(self):
        """Test creating a new carrier info."""
        url = reverse('carrierinfo-list')
        data = {
            'name': 'New Carrier',
            'address': 'New Address',
            'contact_name': 'Jane Doe',
            'phone': '987-654-3210',
            'email': 'new@carrier.com',
            'status': 'active'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CarrierInfo.objects.count(), 2)
        self.assertEqual(CarrierInfo.objects.latest('id').name, 'New Carrier')
        
    def test_get_carrier_info_detail(self):
        """Test retrieving a specific carrier info."""
        url = reverse('carrierinfo-detail', kwargs={'pk': self.carrier.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Carrier')
        self.assertEqual(response.data['powerapps_entity_name'], 'cr7c4_carrierinfo')
        
    def test_update_carrier_info(self):
        """Test updating a carrier info."""
        url = reverse('carrierinfo-detail', kwargs={'pk': self.carrier.pk})
        data = {
            'name': 'Updated Carrier',
            'address': 'Updated Address',
            'contact_name': 'Updated Contact',
            'phone': '555-555-5555',
            'email': 'updated@carrier.com',
            'status': 'active'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.carrier.refresh_from_db()
        self.assertEqual(self.carrier.name, 'Updated Carrier')
        
    def test_migration_info_endpoint(self):
        """Test the PowerApps migration info endpoint."""
        url = reverse('carrierinfo-migration-info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['powerapps_entity_name'], 'cr7c4_carrierinfo')
        self.assertEqual(response.data['django_model_name'], 'CarrierInfo')
        self.assertEqual(response.data['total_records'], 1)
        self.assertIn('field_mappings', response.data)
        
    def test_filtering_and_search(self):
        """Test API filtering and search capabilities."""
        # Create additional carrier for testing
        CarrierInfo.objects.create(
            name='Search Carrier',
            address='Search Address',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user,
            status='inactive'
        )
        
        # Test status filtering
        url = reverse('carrierinfo-list') + '?status=active'
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search
        url = reverse('carrierinfo-list') + '?search=Search'
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)