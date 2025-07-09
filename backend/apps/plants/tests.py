from django.test import TestCase

"""
Tests for Plants app.

Test suite for Plant model, serializers, and API endpoints
migrated from PowerApps cr7c4_plant entity.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from apps.suppliers.models import Supplier
from .models import Plant


class PlantModelTest(TestCase):
    """Test cases for Plant model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_plant_creation(self):
        """Test creating a Plant instance."""
        plant = Plant.objects.create(
            name='Test Plant',
            location='Test Location',
            plant_type='processing',
            supplier=self.supplier,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(plant.name, 'Test Plant')
        self.assertEqual(plant.location, 'Test Location')
        self.assertEqual(plant.plant_type, 'processing')
        self.assertEqual(plant.supplier, self.supplier)
        self.assertEqual(str(plant), 'Test Plant')
    
    def test_plant_properties(self):
        """Test Plant model properties."""
        plant = Plant.objects.create(
            name='Test Plant',
            location='Test Location',
            supplier=self.supplier,
            load_pickup_requirements='forklift_required,dock_access',
            storage='refrigerated,frozen',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertTrue(plant.has_location)
        self.assertTrue(plant.has_supplier)
        self.assertEqual(plant.load_pickup_requirements_list, ['forklift_required', 'dock_access'])
        self.assertEqual(plant.storage_list, ['refrigerated', 'frozen'])
    
    def test_get_powerapps_entity_name(self):
        """Test PowerApps entity name method."""
        self.assertEqual(Plant.get_powerapps_entity_name(), 'cr7c4_plant')


class PlantAPITest(APITestCase):
    """Test cases for Plant API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        self.plant = Plant.objects.create(
            name='Test Plant',
            location='Test Location',
            plant_type='processing',
            supplier=self.supplier,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_plant_list_endpoint(self):
        """Test GET /api/v1/plants/ endpoint."""
        response = self.client.get('/api/v1/plants/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Plant')
    
    def test_plant_detail_endpoint(self):
        """Test GET /api/v1/plants/{id}/ endpoint."""
        response = self.client.get(f'/api/v1/plants/{self.plant.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Plant')
        self.assertEqual(response.data['powerapps_entity_name'], 'cr7c4_plant')
    
    def test_plant_creation_endpoint(self):
        """Test POST /api/v1/plants/ endpoint."""
        data = {
            'name': 'New Plant',
            'location': 'New Location',
            'plant_type': 'warehouse',
            'supplier': self.supplier.id
        }
        response = self.client.post('/api/v1/plants/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Plant')
    
    def test_migration_info_endpoint(self):
        """Test GET /api/v1/plants/migration_info/ endpoint."""
        response = self.client.get('/api/v1/plants/migration_info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['powerapps_entity_name'], 'cr7c4_plant')
        self.assertEqual(response.data['django_model_name'], 'Plant')
        self.assertEqual(response.data['total_records'], 1)
        self.assertEqual(response.data['active_records'], 1)
        self.assertIn('field_mappings', response.data)
        self.assertIn('api_endpoints', response.data)


# Placeholder test classes for future implementation
class PlantSerializerTest(TestCase):
    """Test cases for Plant serializers."""
    
    def test_placeholder(self):
        """Placeholder test for serializers."""
        # TODO: Implement serializer tests
        pass


class PlantFilteringTest(APITestCase):
    """Test cases for Plant API filtering and search."""
    
    def test_placeholder(self):
        """Placeholder test for filtering."""
        # TODO: Implement filtering tests
        pass


class PlantPermissionsTest(APITestCase):
    """Test cases for Plant API permissions."""
    
    def test_placeholder(self):
        """Placeholder test for permissions."""
        # TODO: Implement permission tests
        pass
