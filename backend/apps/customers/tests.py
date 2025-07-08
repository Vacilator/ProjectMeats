"""
Tests for Customers API.

Tests the REST API endpoints for managing Customer entities
migrated from PowerApps pro_customer.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Customer


class CustomerModelTest(TestCase):
    """Test the Customer model."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_customer_creation(self):
        """Test creating a customer with required fields."""
        customer = Customer.objects.create(
            name='Test Customer',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(customer.name, 'Test Customer')
        self.assertEqual(customer.status, 'active')  # Default status
        self.assertEqual(str(customer), 'Test Customer')
        self.assertEqual(customer.get_powerapps_entity_name(), 'pro_customer')
    
    def test_customer_validation(self):
        """Test customer model validation."""
        customer = Customer(
            name='',  # Empty name should fail validation
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        with self.assertRaises(Exception):
            customer.full_clean()


class CustomerAPITest(APITestCase):
    """Test the Customer API endpoints."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_list_customers(self):
        """Test retrieving list of customers."""
        url = reverse('customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Customer')
    
    def test_create_customer(self):
        """Test creating a new customer."""
        url = reverse('customer-list')
        data = {
            'name': 'New Customer',
            'status': 'active'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)
        
        new_customer = Customer.objects.get(name='New Customer')
        self.assertEqual(new_customer.created_by, self.user)
        self.assertEqual(new_customer.owner, self.user)
    
    def test_create_customer_validation(self):
        """Test customer creation validation."""
        url = reverse('customer-list')
        data = {}  # Missing required name field
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_retrieve_customer(self):
        """Test retrieving a specific customer."""
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Customer')
        self.assertEqual(response.data['powerapps_entity_name'], 'pro_customer')
    
    def test_update_customer(self):
        """Test updating a customer."""
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        data = {
            'name': 'Updated Customer'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'Updated Customer')
    
    def test_delete_customer_soft_delete(self):
        """Test soft delete of customer (sets status to inactive)."""
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.status, 'inactive')
    
    def test_migration_info_endpoint(self):
        """Test the PowerApps migration info endpoint."""
        url = reverse('customer-migration-info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['powerapps_entity_name'], 'pro_customer')
        self.assertEqual(response.data['django_model_name'], 'Customer')
        self.assertEqual(response.data['total_records'], 1)
        self.assertEqual(response.data['active_records'], 1)
        self.assertIn('field_mappings', response.data)
    
    def test_filtering(self):
        """Test API filtering capabilities."""
        # Create another customer with different status
        Customer.objects.create(
            name='Inactive Customer',
            status='inactive',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        # Test filtering by status
        url = reverse('customer-list')
        response = self.client.get(url, {'active': 'true'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtering by status field directly
        response = self.client.get(url, {'status': 'active'})
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search(self):
        """Test API search functionality."""
        url = reverse('customer-list')
        response = self.client.get(url, {'search': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
