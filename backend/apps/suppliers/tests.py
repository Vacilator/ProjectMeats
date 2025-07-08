"""
Tests for Suppliers API.

Tests the REST API endpoints for managing Supplier entities
migrated from PowerApps cr7c4_supplier.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Supplier
from apps.accounts_receivables.models import AccountsReceivable


class SupplierModelTest(TestCase):
    """Test the Supplier model."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_supplier_creation(self):
        """Test creating a supplier with required fields."""
        supplier = Supplier.objects.create(
            name='Test Supplier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(supplier.name, 'Test Supplier')
        self.assertEqual(supplier.status, 'active')  # Default status
        self.assertFalse(supplier.delivery_type_profile)  # Default value
        self.assertEqual(str(supplier), 'Test Supplier')
        self.assertEqual(supplier.get_powerapps_entity_name(), 'cr7c4_supplier')
    
    def test_supplier_with_relationships(self):
        """Test supplier with foreign key relationships."""
        # Create an accounts receivable record
        ar = AccountsReceivable.objects.create(
            name='Test AR',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        supplier = Supplier.objects.create(
            name='Test Supplier with AR',
            accounts_receivable=ar,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(supplier.accounts_receivable, ar)
        self.assertTrue(supplier.has_accounts_receivable)
    
    def test_supplier_properties(self):
        """Test supplier computed properties."""
        from django.utils import timezone
        
        supplier = Supplier.objects.create(
            name='Test Supplier',
            credit_application_date=timezone.now(),
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertTrue(supplier.has_credit_application)
        self.assertFalse(supplier.has_accounts_receivable)


class SupplierAPITest(APITestCase):
    """Test the Supplier API endpoints."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            delivery_type_profile=True,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_list_suppliers(self):
        """Test retrieving list of suppliers."""
        url = reverse('supplier-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Supplier')
    
    def test_create_supplier(self):
        """Test creating a new supplier."""
        url = reverse('supplier-list')
        data = {
            'name': 'New Supplier',
            'delivery_type_profile': False,
            'status': 'active'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 2)
        
        new_supplier = Supplier.objects.get(name='New Supplier')
        self.assertEqual(new_supplier.created_by, self.user)
        self.assertEqual(new_supplier.owner, self.user)
    
    def test_create_supplier_validation(self):
        """Test supplier creation validation."""
        url = reverse('supplier-list')
        data = {}  # Missing required name field
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_retrieve_supplier(self):
        """Test retrieving a specific supplier."""
        url = reverse('supplier-detail', kwargs={'pk': self.supplier.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Supplier')
        self.assertEqual(response.data['powerapps_entity_name'], 'cr7c4_supplier')
    
    def test_update_supplier(self):
        """Test updating a supplier."""
        url = reverse('supplier-detail', kwargs={'pk': self.supplier.pk})
        data = {
            'name': 'Updated Supplier',
            'delivery_type_profile': False
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, 'Updated Supplier')
        self.assertFalse(self.supplier.delivery_type_profile)
    
    def test_delete_supplier_soft_delete(self):
        """Test soft delete of supplier (sets status to inactive)."""
        url = reverse('supplier-detail', kwargs={'pk': self.supplier.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.status, 'inactive')
    
    def test_migration_info_endpoint(self):
        """Test the PowerApps migration info endpoint."""
        url = reverse('supplier-migration-info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['powerapps_entity_name'], 'cr7c4_supplier')
        self.assertEqual(response.data['django_model_name'], 'Supplier')
        self.assertEqual(response.data['total_records'], 1)
        self.assertEqual(response.data['active_records'], 1)
        self.assertIn('field_mappings', response.data)
    
    def test_filtering(self):
        """Test API filtering capabilities."""
        # Create another supplier with different attributes
        Supplier.objects.create(
            name='Inactive Supplier',
            status='inactive',
            delivery_type_profile=False,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        # Test filtering by status
        url = reverse('supplier-list')
        response = self.client.get(url, {'active': 'true'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtering by delivery type
        response = self.client.get(url, {'delivery_type_profile': 'true'})
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search(self):
        """Test API search functionality."""
        url = reverse('supplier-list')
        response = self.client.get(url, {'search': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
