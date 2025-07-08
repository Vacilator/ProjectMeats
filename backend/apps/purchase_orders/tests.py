"""
Tests for Purchase Orders API.

Tests the REST API endpoints for managing PurchaseOrder entities
migrated from PowerApps pro_purchaseorder.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from .models import PurchaseOrder
from apps.customers.models import Customer
from apps.suppliers.models import Supplier


class PurchaseOrderAPITest(APITestCase):
    """Test the PurchaseOrder API endpoints."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create related objects
        self.customer = Customer.objects.create(
            name='Test Customer',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        # Create a test purchase order
        self.purchase_order = PurchaseOrder.objects.create(
            po_number='PO-001',
            item='Test Item',
            quantity=10,
            price_per_unit=Decimal('25.99'),
            purchase_date=timezone.now(),
            fulfillment_date=timezone.now() + timedelta(days=7),
            customer=self.customer,
            supplier=self.supplier,
            customer_documents='customer_doc.pdf',
            supplier_documents='supplier_doc.pdf',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_list_purchase_orders(self):
        """Test retrieving list of purchase orders."""
        url = reverse('purchaseorder-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['po_number'], 'PO-001')
    
    def test_create_purchase_order(self):
        """Test creating a new purchase order."""
        url = reverse('purchaseorder-list')
        data = {
            'po_number': 'PO-002',
            'item': 'New Test Item',
            'quantity': 5,
            'price_per_unit': '15.50',
            'purchase_date': timezone.now().isoformat(),
            'fulfillment_date': (timezone.now() + timedelta(days=14)).isoformat(),
            'customer': self.customer.id,
            'supplier': self.supplier.id,
            'customer_documents': 'new_customer_doc.pdf',
            'supplier_documents': 'new_supplier_doc.pdf',
            'status': 'active'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseOrder.objects.count(), 2)
        self.assertEqual(response.data['po_number'], 'PO-002')
    
    def test_migration_info_endpoint(self):
        """Test the PowerApps migration info endpoint."""
        url = reverse('purchaseorder-migration-info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['powerapps_entity_name'], 'pro_purchaseorder')
        self.assertEqual(response.data['django_model_name'], 'PurchaseOrder')
        self.assertEqual(response.data['total_records'], 1)
        self.assertIn('field_mappings', response.data)
    
    def test_filtering_and_search(self):
        """Test API filtering and search capabilities."""
        url = reverse('purchaseorder-list')
        
        # Test search by PO number
        response = self.client.get(url, {'search': 'PO-001'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search by item
        response = self.client.get(url, {'search': 'Test Item'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filter by customer
        response = self.client.get(url, {'customer': self.customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filter by status
        response = self.client.get(url, {'status': 'active'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class PurchaseOrderModelTest(TestCase):
    """Test the PurchaseOrder model."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.customer = Customer.objects.create(
            name='Test Customer',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
    
    def test_purchase_order_creation(self):
        """Test creating a purchase order with required fields."""
        po = PurchaseOrder.objects.create(
            po_number='PO-TEST-001',
            item='Test Product',
            quantity=5,
            price_per_unit=Decimal('10.00'),
            purchase_date=timezone.now(),
            customer=self.customer,
            supplier=self.supplier,
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        self.assertEqual(po.po_number, 'PO-TEST-001')
        self.assertEqual(po.item, 'Test Product')
        self.assertEqual(po.quantity, 5)
        self.assertEqual(po.price_per_unit, Decimal('10.00'))
        self.assertEqual(po.total_amount, Decimal('50.00'))
        self.assertEqual(po.status, 'active')  # Default status
    
    def test_purchase_order_computed_properties(self):
        """Test purchase order computed properties."""
        po = PurchaseOrder.objects.create(
            po_number='PO-TEST-002',
            item='Test Product 2',
            quantity=3,
            price_per_unit=Decimal('25.99'),
            purchase_date=timezone.now(),
            fulfillment_date=timezone.now() - timedelta(days=1),  # Past date
            customer=self.customer,
            supplier=self.supplier,
            customer_documents='doc1.pdf',
            supplier_documents='doc2.pdf',
            created_by=self.user,
            modified_by=self.user,
            owner=self.user
        )
        
        # Test total_amount calculation
        expected_total = Decimal('3') * Decimal('25.99')
        self.assertEqual(po.total_amount, expected_total)
        
        # Test is_fulfilled (past fulfillment date)
        self.assertTrue(po.is_fulfilled)
        
        # Test has_documents
        self.assertTrue(po.has_documents)
