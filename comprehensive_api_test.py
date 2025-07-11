#!/usr/bin/env python
"""
Comprehensive Frontend/Backend Integration Testing Script

This script tests all CRUD operations for every ProjectMeats entity
to ensure the frontend forms work correctly with the backend API.
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta

# API configuration
API_BASE_URL = "http://localhost:8001/api/v1"

class ProjectMeatsAPITester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.test_results = []
        self.created_records = {}  # Track created records for cleanup
        
    def log_test(self, test_name, success, details=""):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"    {details}")
        
    def test_list_endpoint(self, endpoint, entity_name):
        """Test listing entities."""
        try:
            response = requests.get(f"{self.base_url}/{endpoint}/")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                self.log_test(f"{entity_name} - List", True, f"Found {count} records")
                return data['results']
            else:
                self.log_test(f"{entity_name} - List", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test(f"{entity_name} - List", False, str(e))
            return []
    
    def test_create_endpoint(self, endpoint, entity_name, test_data):
        """Test creating a new entity."""
        try:
            response = requests.post(f"{self.base_url}/{endpoint}/", json=test_data)
            if response.status_code == 201:
                created_record = response.json()
                record_id = created_record.get('id')
                if record_id:
                    if endpoint not in self.created_records:
                        self.created_records[endpoint] = []
                    self.created_records[endpoint].append(record_id)
                    self.log_test(f"{entity_name} - Create", True, f"Created with ID {record_id}")
                    return created_record
                else:
                    # If no ID in response, check if record was created by listing and finding it
                    self.log_test(f"{entity_name} - Create", True, f"Created (ID not returned in response)")
                    return created_record
            else:
                self.log_test(f"{entity_name} - Create", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test(f"{entity_name} - Create", False, str(e))
            return None
    
    def test_detail_endpoint(self, endpoint, entity_name, record_id):
        """Test retrieving entity details."""
        try:
            response = requests.get(f"{self.base_url}/{endpoint}/{record_id}/")
            if response.status_code == 200:
                self.log_test(f"{entity_name} - Retrieve", True, f"Retrieved record {record_id}")
                return response.json()
            else:
                self.log_test(f"{entity_name} - Retrieve", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test(f"{entity_name} - Retrieve", False, str(e))
            return None
    
    def test_update_endpoint(self, endpoint, entity_name, record_id, update_data):
        """Test updating an entity."""
        try:
            response = requests.patch(f"{self.base_url}/{endpoint}/{record_id}/", json=update_data)
            if response.status_code == 200:
                self.log_test(f"{entity_name} - Update", True, f"Updated record {record_id}")
                return response.json()
            else:
                self.log_test(f"{entity_name} - Update", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test(f"{entity_name} - Update", False, str(e))
            return None
    
    def test_delete_endpoint(self, endpoint, entity_name, record_id):
        """Test deleting an entity (usually soft delete)."""
        try:
            response = requests.delete(f"{self.base_url}/{endpoint}/{record_id}/")
            if response.status_code in [204, 200]:
                self.log_test(f"{entity_name} - Delete", True, f"Deleted record {record_id}")
                return True
            else:
                self.log_test(f"{entity_name} - Delete", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"{entity_name} - Delete", False, str(e))
            return False
    
    def test_search_endpoint(self, endpoint, entity_name, search_term):
        """Test search functionality."""
        try:
            response = requests.get(f"{self.base_url}/{endpoint}/", params={'search': search_term})
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                self.log_test(f"{entity_name} - Search", True, f"Search '{search_term}' returned {count} results")
                return data['results']
            else:
                self.log_test(f"{entity_name} - Search", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test(f"{entity_name} - Search", False, str(e))
            return []
    
    def test_filter_endpoint(self, endpoint, entity_name, filter_params):
        """Test filtering functionality."""
        try:
            response = requests.get(f"{self.base_url}/{endpoint}/", params=filter_params)
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                filter_str = ", ".join([f"{k}={v}" for k, v in filter_params.items()])
                self.log_test(f"{entity_name} - Filter", True, f"Filter '{filter_str}' returned {count} results")
                return data['results']
            else:
                self.log_test(f"{entity_name} - Filter", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test(f"{entity_name} - Filter", False, str(e))
            return []
    
    def test_migration_info_endpoint(self, endpoint, entity_name):
        """Test migration info endpoint."""
        try:
            response = requests.get(f"{self.base_url}/{endpoint}/migration_info/")
            if response.status_code == 200:
                data = response.json()
                powerapps_name = data.get('powerapps_entity_name', 'Unknown')
                self.log_test(f"{entity_name} - Migration Info", True, f"PowerApps: {powerapps_name}")
                return data
            else:
                self.log_test(f"{entity_name} - Migration Info", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test(f"{entity_name} - Migration Info", False, str(e))
            return None
    
    def test_accounts_receivables(self):
        """Comprehensive test for AccountsReceivable entity."""
        print(f"\n🧪 Testing Accounts Receivables...")
        endpoint = "accounts-receivables"
        entity_name = "AccountsReceivable"
        
        # Test list
        existing = self.test_list_endpoint(endpoint, entity_name)
        
        # Test create
        test_data = {
            "name": "Test AR for CRUD",
            "email": "test.crud@example.com",
            "phone": "+1-555-TEST",
            "terms": "Net 30",
            "status": "active"
        }
        created = self.test_create_endpoint(endpoint, entity_name, test_data)
        
        if created:
            record_id = created['id']
            
            # Test retrieve
            self.test_detail_endpoint(endpoint, entity_name, record_id)
            
            # Test update
            update_data = {"email": "updated.crud@example.com", "terms": "Net 45"}
            self.test_update_endpoint(endpoint, entity_name, record_id, update_data)
            
            # Test search
            self.test_search_endpoint(endpoint, entity_name, "Test AR")
            
            # Test filter
            self.test_filter_endpoint(endpoint, entity_name, {"status": "active"})
            
            # Test delete
            self.test_delete_endpoint(endpoint, entity_name, record_id)
        
        # Test migration info
        self.test_migration_info_endpoint(endpoint, entity_name)
    
    def test_suppliers(self):
        """Comprehensive test for Supplier entity."""
        print(f"\n🧪 Testing Suppliers...")
        endpoint = "suppliers"
        entity_name = "Supplier"
        
        # Test list
        existing = self.test_list_endpoint(endpoint, entity_name)
        
        # Test create
        test_data = {
            "name": "Test Supplier for CRUD",
            "delivery_type_profile": True,
            "status": "active"
        }
        created = self.test_create_endpoint(endpoint, entity_name, test_data)
        
        if created:
            record_id = created['id']
            
            # Test retrieve
            self.test_detail_endpoint(endpoint, entity_name, record_id)
            
            # Test update
            update_data = {"delivery_type_profile": False}
            self.test_update_endpoint(endpoint, entity_name, record_id, update_data)
            
            # Test search
            self.test_search_endpoint(endpoint, entity_name, "Test Supplier")
            
            # Test filter
            self.test_filter_endpoint(endpoint, entity_name, {"status": "active"})
            
            # Test delete
            self.test_delete_endpoint(endpoint, entity_name, record_id)
        
        # Test migration info
        self.test_migration_info_endpoint(endpoint, entity_name)
    
    def test_customers(self):
        """Comprehensive test for Customer entity."""
        print(f"\n🧪 Testing Customers...")
        endpoint = "customers"
        entity_name = "Customer"
        
        # Test list
        existing = self.test_list_endpoint(endpoint, entity_name)
        
        # Test create
        test_data = {
            "name": "Test Customer for CRUD",
            "status": "active"
        }
        created = self.test_create_endpoint(endpoint, entity_name, test_data)
        
        if created:
            record_id = created['id']
            
            # Test retrieve
            self.test_detail_endpoint(endpoint, entity_name, record_id)
            
            # Test update
            update_data = {"name": "Updated Test Customer"}
            self.test_update_endpoint(endpoint, entity_name, record_id, update_data)
            
            # Test search
            self.test_search_endpoint(endpoint, entity_name, "Test Customer")
            
            # Test filter
            self.test_filter_endpoint(endpoint, entity_name, {"status": "active"})
            
            # Test delete
            self.test_delete_endpoint(endpoint, entity_name, record_id)
        
        # Test migration info
        self.test_migration_info_endpoint(endpoint, entity_name)
    
    def test_plants(self):
        """Comprehensive test for Plant entity."""
        print(f"\n🧪 Testing Plants...")
        endpoint = "plants"
        entity_name = "Plant"
        
        # Test list
        existing = self.test_list_endpoint(endpoint, entity_name)
        
        # Test create
        test_data = {
            "name": "Test Plant for CRUD",
            "location": "Test City, TS",
            "plant_type": "processing",
            "status": "active"
        }
        created = self.test_create_endpoint(endpoint, entity_name, test_data)
        
        if created:
            record_id = created['id']
            
            # Test retrieve
            self.test_detail_endpoint(endpoint, entity_name, record_id)
            
            # Test update
            update_data = {"location": "Updated City, TS", "plant_type": "distribution"}
            self.test_update_endpoint(endpoint, entity_name, record_id, update_data)
            
            # Test search
            self.test_search_endpoint(endpoint, entity_name, "Test Plant")
            
            # Test filter
            self.test_filter_endpoint(endpoint, entity_name, {"status": "active"})
            
            # Test delete
            self.test_delete_endpoint(endpoint, entity_name, record_id)
        
        # Test migration info
        self.test_migration_info_endpoint(endpoint, entity_name)
    
    def test_supplier_locations(self):
        """Comprehensive test for SupplierLocation entity."""
        print(f"\n🧪 Testing Supplier Locations...")
        endpoint = "supplier-locations"
        entity_name = "SupplierLocation"
        
        # Get a supplier for the foreign key
        suppliers = self.test_list_endpoint("suppliers", "Supplier")
        supplier_id = suppliers[0]['id'] if suppliers else None
        
        if not supplier_id:
            self.log_test(f"{entity_name} - Prerequisites", False, "No suppliers available")
            return
        
        # Test list
        existing = self.test_list_endpoint(endpoint, entity_name)
        
        # Test create
        test_data = {
            "name": "Test Location for CRUD",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "TS",
            "postal_code": "12345",
            "location_type": "office",
            "contact_name": "Test Contact",
            "contact_phone": "555-TEST",
            "contact_email": "test@location.com",
            "supplier": supplier_id,
            "status": "active"
        }
        created = self.test_create_endpoint(endpoint, entity_name, test_data)
        
        if created:
            record_id = created['id']
            
            # Test retrieve
            self.test_detail_endpoint(endpoint, entity_name, record_id)
            
            # Test update
            update_data = {"city": "Updated City", "location_type": "warehouse"}
            self.test_update_endpoint(endpoint, entity_name, record_id, update_data)
            
            # Test search
            self.test_search_endpoint(endpoint, entity_name, "Test Location")
            
            # Test filter
            self.test_filter_endpoint(endpoint, entity_name, {"status": "active"})
            
            # Test delete
            self.test_delete_endpoint(endpoint, entity_name, record_id)
        
        # Test migration info
        self.test_migration_info_endpoint(endpoint, entity_name)
    
    def test_contact_info(self):
        """Comprehensive test for ContactInfo entity."""
        print(f"\n🧪 Testing Contact Info...")
        endpoint = "contacts"
        entity_name = "ContactInfo"
        
        # Test list
        existing = self.test_list_endpoint(endpoint, entity_name)
        
        # Test create
        test_data = {
            "name": "Test Contact for CRUD",
            "email": "test.contact@example.com",
            "phone": "555-CONTACT",
            "position": "Test Manager",
            "contact_type": "primary",
            "status": "active"
        }
        created = self.test_create_endpoint(endpoint, entity_name, test_data)
        
        if created:
            record_id = created['id']
            
            # Test retrieve
            self.test_detail_endpoint(endpoint, entity_name, record_id)
            
            # Test update
            update_data = {"position": "Updated Manager", "contact_type": "secondary"}
            self.test_update_endpoint(endpoint, entity_name, record_id, update_data)
            
            # Test search
            self.test_search_endpoint(endpoint, entity_name, "Test Contact")
            
            # Test filter
            self.test_filter_endpoint(endpoint, entity_name, {"status": "active"})
            
            # Test delete
            self.test_delete_endpoint(endpoint, entity_name, record_id)
        
        # Test migration info
        self.test_migration_info_endpoint(endpoint, entity_name)
    
    def test_carrier_info(self):
        """Comprehensive test for CarrierInfo entity."""
        print(f"\n🧪 Testing Carrier Info...")
        endpoint = "carriers"
        entity_name = "CarrierInfo"
        
        # Test list
        existing = self.test_list_endpoint(endpoint, entity_name)
        
        # Test create
        test_data = {
            "name": "Test Carrier for CRUD",
            "address": "456 Carrier Road",
            "contact_name": "Test Carrier Contact",
            "release_number": "TEST-001",
            "status": "active"
        }
        created = self.test_create_endpoint(endpoint, entity_name, test_data)
        
        if created:
            record_id = created['id']
            
            # Test retrieve
            self.test_detail_endpoint(endpoint, entity_name, record_id)
            
            # Test update
            update_data = {"contact_name": "Updated Carrier Contact"}
            self.test_update_endpoint(endpoint, entity_name, record_id, update_data)
            
            # Test search
            self.test_search_endpoint(endpoint, entity_name, "Test Carrier")
            
            # Test filter
            self.test_filter_endpoint(endpoint, entity_name, {"status": "active"})
            
            # Test delete
            self.test_delete_endpoint(endpoint, entity_name, record_id)
        
        # Test migration info
        self.test_migration_info_endpoint(endpoint, entity_name)
    
    def test_purchase_orders(self):
        """Comprehensive test for PurchaseOrder entity."""
        print(f"\n🧪 Testing Purchase Orders...")
        endpoint = "purchase-orders"
        entity_name = "PurchaseOrder"
        
        # Get suppliers and customers for foreign keys
        suppliers = self.test_list_endpoint("suppliers", "Supplier")
        customers = self.test_list_endpoint("customers", "Customer")
        
        supplier_id = suppliers[0]['id'] if suppliers else None
        customer_id = customers[0]['id'] if customers else None
        
        if not supplier_id or not customer_id:
            self.log_test(f"{entity_name} - Prerequisites", False, "Missing suppliers or customers")
            return
        
        # Test list
        existing = self.test_list_endpoint(endpoint, entity_name)
        
        # Test create
        test_data = {
            "po_number": "TEST-PO-001",
            "item": "Test Product for CRUD",
            "quantity": 100,
            "price_per_unit": "5.99",
            "purchase_date": datetime.now().isoformat(),
            "supplier": supplier_id,
            "customer": customer_id,
            "status": "active"
        }
        created = self.test_create_endpoint(endpoint, entity_name, test_data)
        
        if created:
            record_id = created['id']
            
            # Test retrieve
            self.test_detail_endpoint(endpoint, entity_name, record_id)
            
            # Test update
            update_data = {"quantity": 150, "price_per_unit": "6.99"}
            self.test_update_endpoint(endpoint, entity_name, record_id, update_data)
            
            # Test search
            self.test_search_endpoint(endpoint, entity_name, "TEST-PO")
            
            # Test filter
            self.test_filter_endpoint(endpoint, entity_name, {"status": "active"})
            
            # Test delete
            self.test_delete_endpoint(endpoint, entity_name, record_id)
        
        # Test migration info
        self.test_migration_info_endpoint(endpoint, entity_name)
    
    def run_all_tests(self):
        """Run comprehensive tests for all entities."""
        print("🚀 Starting Comprehensive ProjectMeats API Testing...")
        print("=" * 60)
        
        # Test all entities
        self.test_accounts_receivables()
        self.test_suppliers()
        self.test_customers()
        self.test_plants()
        self.test_supplier_locations()
        self.test_contact_info()
        self.test_carrier_info()
        self.test_purchase_orders()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary:")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to test_results.json")
        return failed_tests == 0


def main():
    """Main function to run all tests."""
    tester = ProjectMeatsAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the results above.")
        return 1


if __name__ == '__main__':
    exit(main())