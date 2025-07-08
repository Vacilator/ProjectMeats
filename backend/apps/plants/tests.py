"""
Tests for Plants app.

Tests for the Plant model and API endpoints migrated from PowerApps cr7c4_plant.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Plant


class PlantModelTest(TestCase):
    """Test cases for Plant model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_plant(self):
        """Test creating a plant."""
        plant = Plant.objects.create(
            name='Test Plant',
            plant_type='manufacturing',
            status='active',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(plant.name, 'Test Plant')
        self.assertEqual(plant.plant_type, 'manufacturing')
        self.assertEqual(plant.status, 'active')
        self.assertEqual(str(plant), 'Test Plant')
    
    def test_plant_name_required(self):
        """Test that plant name is required."""
        plant = Plant(
            name='',  # Empty name should fail validation
            plant_type='warehouse',
            status='active',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        with self.assertRaises(ValidationError):
            plant.clean()
    
    def test_plant_type_choices(self):
        """Test plant type choices."""
        plant = Plant.objects.create(
            name='Warehouse Plant',
            plant_type='warehouse',
            status='active',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(plant.plant_type, 'warehouse')
    
    def test_powerapps_entity_name(self):
        """Test PowerApps entity name method."""
        self.assertEqual(Plant.get_powerapps_entity_name(), 'cr7c4_plant')


class PlantAPITest(APITestCase):
    """Test cases for Plant API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.plant = Plant.objects.create(
            name='Test Plant',
            plant_type='manufacturing',
            status='active',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_get_plants_list(self):
        """Test retrieving plants list."""
        response = self.client.get('/api/v1/plants/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Plant')
    
    def test_get_plant_detail(self):
        """Test retrieving plant detail."""
        response = self.client.get(f'/api/v1/plants/{self.plant.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Plant')
        self.assertEqual(response.data['plant_type'], 'manufacturing')
    
    def test_create_plant(self):
        """Test creating a plant via API."""
        data = {
            'name': 'New Plant',
            'plant_type': 'warehouse',
            'status': 'active'
        }
        response = self.client.post('/api/v1/plants/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Plant')
        
        # Verify plant was created in database
        plant = Plant.objects.get(name='New Plant')
        self.assertEqual(plant.plant_type, 'warehouse')
    
    def test_update_plant(self):
        """Test updating a plant via API."""
        data = {
            'name': 'Updated Plant Name',
            'plant_type': 'distribution'
        }
        response = self.client.patch(f'/api/v1/plants/{self.plant.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Plant Name')
        
        # Verify plant was updated in database
        self.plant.refresh_from_db()
        self.assertEqual(self.plant.name, 'Updated Plant Name')
        self.assertEqual(self.plant.plant_type, 'distribution')
    
    def test_delete_plant(self):
        """Test deleting a plant via API (soft delete)."""
        response = self.client.delete(f'/api/v1/plants/{self.plant.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify plant was soft deleted (status changed to inactive)
        self.plant.refresh_from_db()
        self.assertEqual(self.plant.status, 'inactive')
    
    def test_migration_info_endpoint(self):
        """Test migration info endpoint."""
        response = self.client.get('/api/v1/plants/migration_info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['powerapps_entity_name'], 'cr7c4_plant')
        self.assertEqual(data['django_model_name'], 'Plant')
        self.assertEqual(data['django_app_name'], 'plants')
        self.assertEqual(data['total_records'], 1)
        self.assertEqual(data['active_records'], 1)
        self.assertIn('field_mappings', data)
        self.assertIn('api_endpoints', data)
    
    def test_search_plants(self):
        """Test searching plants."""
        # Create another plant for search testing
        Plant.objects.create(
            name='Another Plant',
            plant_type='processing',
            status='active',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        response = self.client.get('/api/v1/plants/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Plant')
    
    def test_filter_plants_by_type(self):
        """Test filtering plants by type."""
        # Create plants with different types
        Plant.objects.create(
            name='Warehouse Plant',
            plant_type='warehouse',
            status='active',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        response = self.client.get('/api/v1/plants/?plant_type=warehouse')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['plant_type'], 'warehouse')
