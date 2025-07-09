"""
Tests for Plants API.

Tests the REST API endpoints for managing Plant entities
migrated from PowerApps cr7c4_plant.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from .models import Plant


class PlantModelTest(TestCase):
    """Test the Plant model."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
    def test_plant_creation(self):
        """Test creating a plant."""
        plant = Plant.objects.create(
            name='Test Plant',
            location='Test Location',
            contact_info='Contact Info',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(plant.name, 'Test Plant')
        self.assertEqual(plant.location, 'Test Location')
        self.assertEqual(plant.status, 'active')  # Default status
        self.assertTrue(plant.has_location)
        self.assertTrue(plant.has_contact_info)
        
    def test_plant_str_representation(self):
        """Test the string representation."""
        plant = Plant.objects.create(
            name='Test Plant',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        self.assertEqual(str(plant), 'Test Plant')
        
    def test_plant_without_location(self):
        """Test plant without location."""
        plant = Plant.objects.create(
            name='Test Plant',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        self.assertFalse(plant.has_location)
        self.assertFalse(plant.has_contact_info)
        
    def test_powerapps_entity_name(self):
        """Test PowerApps entity name method."""
        self.assertEqual(Plant.get_powerapps_entity_name(), 'cr7c4_plant')


class PlantAPITest(APITestCase):
    """Test the Plant API endpoints."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
        self.plant = Plant.objects.create(
            name='Test Plant',
            location='Test Location',
            contact_info='Contact Info',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_list_plants(self):
        """Test retrieving list of plants."""
        url = reverse('plant-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Plant')
        
    def test_create_plant(self):
        """Test creating a new plant."""
        url = reverse('plant-list')
        data = {
            'name': 'New Plant',
            'location': 'New Location',
            'contact_info': 'New Contact Info',
            'status': 'active'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plant.objects.count(), 2)
        self.assertEqual(Plant.objects.latest('id').name, 'New Plant')
        
    def test_get_plant_detail(self):
        """Test retrieving a specific plant."""
        url = reverse('plant-detail', kwargs={'pk': self.plant.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Plant')
        self.assertEqual(response.data['powerapps_entity_name'], 'cr7c4_plant')
        
    def test_update_plant(self):
        """Test updating a plant."""
        url = reverse('plant-detail', kwargs={'pk': self.plant.pk})
        data = {
            'name': 'Updated Plant',
            'location': 'Updated Location',
            'contact_info': 'Updated Contact Info',
            'status': 'active'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plant.refresh_from_db()
        self.assertEqual(self.plant.name, 'Updated Plant')
        
    def test_migration_info_endpoint(self):
        """Test the PowerApps migration info endpoint."""
        url = reverse('plant-migration-info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['powerapps_entity_name'], 'cr7c4_plant')
        self.assertEqual(response.data['django_model_name'], 'Plant')
        self.assertEqual(response.data['total_records'], 1)
        self.assertIn('field_mappings', response.data)
        
    def test_filtering_and_search(self):
        """Test API filtering and search capabilities."""
        # Create additional plant for testing
        Plant.objects.create(
            name='Search Plant',
            location='Search Location',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user,
            status='inactive'
        )
        
        # Test status filtering
        url = reverse('plant-list') + '?status=active'
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search
        url = reverse('plant-list') + '?search=Search'
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)