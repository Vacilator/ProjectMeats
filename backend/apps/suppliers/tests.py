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
from .models import Supplier, SupplierPlantMapping
from apps.accounts_receivables.models import AccountsReceivable
from apps.customers.models import Customer
from apps.contacts.models import ContactInfo


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


class SupplierPlantMappingModelTest(TestCase):
    """Test the SupplierPlantMapping model."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create related objects
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.customer = Customer.objects.create(
            name='Test Customer',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.contact_info = ContactInfo.objects.create(
            name='Test Contact',
            email='contact@example.com',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_supplier_plant_mapping_creation(self):
        """Test creating a supplier plant mapping with required fields."""
        mapping = SupplierPlantMapping.objects.create(
            name='Test Mapping',
            supplier=self.supplier,
            customer=self.customer,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(mapping.name, 'Test Mapping')
        self.assertEqual(mapping.supplier, self.supplier)
        self.assertEqual(mapping.customer, self.customer)
        self.assertEqual(mapping.status, 'active')  # Default status
        self.assertEqual(str(mapping), 'Test Mapping')
        self.assertEqual(mapping.get_powerapps_entity_name(), 'pro_supplierplantmapping')
    
    def test_supplier_plant_mapping_with_contact_info(self):
        """Test supplier plant mapping with contact info relationship."""
        mapping = SupplierPlantMapping.objects.create(
            name='Test Mapping with Contact',
            supplier=self.supplier,
            customer=self.customer,
            contact_info=self.contact_info,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(mapping.contact_info, self.contact_info)
        self.assertTrue(mapping.has_contact_info)
    
    def test_supplier_plant_mapping_properties(self):
        """Test supplier plant mapping computed properties."""
        mapping = SupplierPlantMapping.objects.create(
            name='Test Mapping',
            supplier=self.supplier,
            customer=self.customer,
            documents_reference='Document123, Document456',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertTrue(mapping.has_documents)
        self.assertFalse(mapping.has_contact_info)


class SupplierPlantMappingAPITest(APITestCase):
    """Test the SupplierPlantMapping API endpoints."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create related objects
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.customer = Customer.objects.create(
            name='Test Customer',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.contact_info = ContactInfo.objects.create(
            name='Test Contact',
            email='contact@example.com',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        # Create a test mapping
        self.mapping = SupplierPlantMapping.objects.create(
            name='Test Mapping',
            supplier=self.supplier,
            customer=self.customer,
            contact_info=self.contact_info,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_list_supplier_plant_mappings(self):
        """Test retrieving list of supplier plant mappings."""
        url = reverse('supplier-plant-mapping-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Mapping')
    
    def test_create_supplier_plant_mapping(self):
        """Test creating a new supplier plant mapping."""
        url = reverse('supplier-plant-mapping-list')
        data = {
            'name': 'New Mapping',
            'supplier': self.supplier.id,
            'customer': self.customer.id,
            'status': 'active'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SupplierPlantMapping.objects.count(), 2)
        
        new_mapping = SupplierPlantMapping.objects.get(name='New Mapping')
        self.assertEqual(new_mapping.created_by, self.user)
        self.assertEqual(new_mapping.owner, self.user)
    
    def test_create_supplier_plant_mapping_validation(self):
        """Test supplier plant mapping creation validation."""
        url = reverse('supplier-plant-mapping-list')
        data = {}  # Missing required fields
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_retrieve_supplier_plant_mapping(self):
        """Test retrieving a specific supplier plant mapping."""
        url = reverse('supplier-plant-mapping-detail', kwargs={'pk': self.mapping.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Mapping')
        self.assertEqual(response.data['powerapps_entity_name'], 'pro_supplierplantmapping')
    
    def test_update_supplier_plant_mapping(self):
        """Test updating a supplier plant mapping."""
        url = reverse('supplier-plant-mapping-detail', kwargs={'pk': self.mapping.pk})
        data = {
            'name': 'Updated Mapping',
            'documents_reference': 'Updated docs'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mapping.refresh_from_db()
        self.assertEqual(self.mapping.name, 'Updated Mapping')
        self.assertEqual(self.mapping.documents_reference, 'Updated docs')
    
    def test_delete_supplier_plant_mapping_soft_delete(self):
        """Test soft delete of supplier plant mapping (sets status to inactive)."""
        url = reverse('supplier-plant-mapping-detail', kwargs={'pk': self.mapping.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.mapping.refresh_from_db()
        self.assertEqual(self.mapping.status, 'inactive')
    
    def test_migration_info_endpoint(self):
        """Test the PowerApps migration info endpoint."""
        url = reverse('supplier-plant-mapping-migration-info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['powerapps_entity_name'], 'pro_supplierplantmapping')
        self.assertEqual(response.data['django_model_name'], 'SupplierPlantMapping')
        self.assertEqual(response.data['total_records'], 1)
        self.assertEqual(response.data['active_records'], 1)
        self.assertIn('field_mappings', response.data)
    
    def test_filtering(self):
        """Test API filtering capabilities."""
        # Create another mapping with different attributes
        SupplierPlantMapping.objects.create(
            name='Inactive Mapping',
            supplier=self.supplier,
            customer=self.customer,
            status='inactive',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        # Test filtering by status
        url = reverse('supplier-plant-mapping-list')
        response = self.client.get(url, {'status': 'active'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtering by supplier
        response = self.client.get(url, {'supplier': self.supplier.id})
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search(self):
        """Test API search functionality."""
        url = reverse('supplier-plant-mapping-list')
        response = self.client.get(url, {'search': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
