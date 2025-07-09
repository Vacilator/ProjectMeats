/**
 * Customers Screen Component
 * 
 * Main screen for managing customer records migrated from 
 * PowerApps pro_customer entity.
 * 
 * Features:
 * - List view with search and filtering
 * - Create/Edit/Delete operations
 * - PowerApps migration information display
 * - Responsive design for mobile and desktop
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Customer, ContactInfo } from '../types';
import type { MigrationInfo } from '../types';
import { CustomersService, ContactsService } from '../services/api';
import { Container, MigrationInfo as SharedMigrationInfo, ErrorMessage, LoadingMessage } from '../components/SharedComponents';
import EntityForm, { FormField } from '../components/EntityForm';
import ConfirmationModal from '../components/ConfirmationModal';

// Reuse styled components from SuppliersScreen for consistency
const Header = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
`;

const Title = styled.h1`
  margin: 0;
  color: #333;
  font-size: 28px;
`;

const Subtitle = styled.p`
  margin: 4px 0 0 0;
  color: #666;
  font-size: 14px;
`;

const Controls = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
  
  ${props => props.variant === 'primary' ? `
    background-color: #28a745;
    color: white;
    &:hover { background-color: #218838; }
  ` : `
    background-color: #f8f9fa;
    color: #333;
    border: 1px solid #dee2e6;
    &:hover { background-color: #e9ecef; }
  `}
`;

const SearchInput = styled.input`
  padding: 8px 12px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const TableHeader = styled.th`
  background: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid #dee2e6;
`;

const TableCell = styled.td`
  padding: 12px;
  border-bottom: 1px solid #f1f1f1;
`;

const StatusBadge = styled.span<{ status: string }>`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  
  ${props => props.status === 'active' ? `
    background-color: #d4edda;
    color: #155724;
  ` : `
    background-color: #f8d7da;
    color: #721c24;
  `}
`;

const CustomersScreen: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [migrationInfo, setMigrationInfo] = useState<MigrationInfo | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingCustomerId, setDeletingCustomerId] = useState<number | null>(null);
  const [showContactForm, setShowContactForm] = useState(false);
  const [selectedCustomerId, setSelectedCustomerId] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [customerContacts, setCustomerContacts] = useState<Record<number, ContactInfo[]>>({});

  useEffect(() => {
    loadCustomers();
    loadMigrationInfo();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load contacts for all customers
  useEffect(() => {
    if (customers.length > 0) {
      loadCustomerContacts();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [customers]);

  // Form field definitions for Customers
  const customerFormFields: FormField[] = [
    {
      key: 'name',
      label: 'Customer Name',
      type: 'text',
      required: true,
      placeholder: 'Enter customer name'
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select',
      required: true,
      options: [
        { value: 'active', label: 'Active' },
        { value: 'inactive', label: 'Inactive' }
      ]
    }
  ];

  // Form field definitions for Contact Info (for customers)
  const contactFormFields: FormField[] = [
    {
      key: 'name',
      label: 'Contact Name',
      type: 'text',
      required: true,
      placeholder: 'Enter contact person name'
    },
    {
      key: 'email',
      label: 'Email',
      type: 'email',
      placeholder: 'Enter email address'
    },
    {
      key: 'phone',
      label: 'Phone',
      type: 'tel',
      placeholder: 'Enter phone number'
    },
    {
      key: 'position',
      label: 'Position',
      type: 'text',
      placeholder: 'Enter job title/position'
    },
    {
      key: 'contact_type',
      label: 'Contact Type',
      type: 'select',
      options: [
        { value: 'primary', label: 'Primary Contact' },
        { value: 'billing', label: 'Billing Contact' },
        { value: 'technical', label: 'Technical Contact' },
        { value: 'sales', label: 'Sales Contact' }
      ]
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select',
      required: true,
      options: [
        { value: 'active', label: 'Active' },
        { value: 'inactive', label: 'Inactive' }
      ]
    }
  ];

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const response = await CustomersService.getList(1, { search: searchTerm });
      setCustomers(response.results);
      setError(null);
    } catch (err) {
      setError('Failed to load customers. Please try again.');
      console.error('Error loading customers:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMigrationInfo = async () => {
    try {
      const info = await CustomersService.getMigrationInfo();
      setMigrationInfo(info);
    } catch (err) {
      console.error('Error loading migration info:', err);
    }
  };

  const loadCustomerContacts = async () => {
    try {
      // Load all contacts and filter by customer ID
      const response = await ContactsService.getList(1, {});
      const contactsMap: Record<number, ContactInfo[]> = {};
      
      // Initialize empty arrays for all customers
      customers.forEach(customer => {
        contactsMap[customer.id] = [];
      });
      
      // Group contacts by customer ID
      response.results.forEach(contact => {
        if (contact.customer) {
          if (!contactsMap[contact.customer]) {
            contactsMap[contact.customer] = [];
          }
          contactsMap[contact.customer].push(contact);
        }
      });
      
      setCustomerContacts(contactsMap);
    } catch (err) {
      console.error('Error loading customer contacts:', err);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadCustomers();
  };

  const handleEditCustomer = (id: number) => {
    const customer = customers.find(c => c.id === id);
    if (customer) {
      setEditingCustomer(customer);
      setShowEditForm(true);
    }
  };

  const handleUpdateCustomer = async (formData: Record<string, any>) => {
    if (!editingCustomer) return;
    
    try {
      setIsSubmitting(true);
      const customerData = {
        name: formData.name as string,
        status: formData.status as 'active' | 'inactive'
      };
      await CustomersService.update(editingCustomer.id, customerData);
      setShowEditForm(false);
      setEditingCustomer(null);
      loadCustomers(); // Reload the list
      setError(null);
    } catch (err) {
      setError('Failed to update customer. Please try again.');
      console.error('Error updating customer:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteCustomer = async (id: number) => {
    setDeletingCustomerId(id);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!deletingCustomerId) return;
    
    try {
      await CustomersService.delete(deletingCustomerId);
      loadCustomers(); // Reload the list
      setError(null);
    } catch (err) {
      setError('Failed to delete customer. Please try again.');
      console.error('Error deleting customer:', err);
    } finally {
      setShowDeleteConfirm(false);
      setDeletingCustomerId(null);
    }
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setDeletingCustomerId(null);
  };

  // Form handling functions
  const handleCreateCustomer = async (formData: Record<string, any>) => {
    try {
      setIsSubmitting(true);
      // Type-safe conversion
      const customerData = {
        name: formData.name as string,
        status: formData.status as 'active' | 'inactive'
      };
      await CustomersService.create(customerData);
      setShowCreateForm(false);
      loadCustomers(); // Reload the list to show new customer
      setError(null);
    } catch (err) {
      setError('Failed to create customer. Please try again.');
      console.error('Error creating customer:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateContact = async (formData: Record<string, any>) => {
    try {
      setIsSubmitting(true);
      // Type-safe conversion with customer ID
      const contactData = {
        name: formData.name as string,
        email: formData.email as string || undefined,
        phone: formData.phone as string || undefined,
        position: formData.position as string || undefined,
        contact_type: formData.contact_type as string || undefined,
        customer: selectedCustomerId as number,
        status: formData.status as 'active' | 'inactive'
      };
      await ContactsService.create(contactData);
      setShowContactForm(false);
      setSelectedCustomerId(null);
      loadCustomerContacts(); // Reload contacts to show new contact
      setError(null);
    } catch (err) {
      setError('Failed to create contact. Please try again.');
      console.error('Error creating contact:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveDraft = async (formData: Record<string, any>) => {
    console.log('Saving customer draft:', formData);
    localStorage.setItem('customerDraft', JSON.stringify(formData));
  };

  const handleSaveContactDraft = async (formData: Record<string, any>) => {
    console.log('Saving contact draft:', formData);
    localStorage.setItem('contactDraft', JSON.stringify(formData));
  };

  const handleAddContact = (customerId: number) => {
    setSelectedCustomerId(customerId);
    setShowContactForm(true);
  };

  if (loading) {
    return (
      <Container>
        <LoadingMessage>Loading customers...</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <div>
          <Title>Customers</Title>
          <Subtitle>
            Manage customer records migrated from PowerApps pro_customer
            {migrationInfo && ` • ${migrationInfo.total_records} total records`}
          </Subtitle>
        </div>
        <Controls>
          <form onSubmit={handleSearch}>
            <SearchInput
              type="text"
              placeholder="Search customers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </form>
          <Button variant="primary" onClick={() => setShowCreateForm(true)}>Add Customer</Button>
          <Button variant="secondary">Export</Button>
        </Controls>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {migrationInfo && (
        <SharedMigrationInfo>
          🏢 PowerApps Migration Status: {migrationInfo.active_records} active customers 
          from {migrationInfo.powerapps_entity_name} entity
        </SharedMigrationInfo>
      )}

      <Table>
        <thead>
          <tr>
            <TableHeader>Name</TableHeader>
            <TableHeader>Status</TableHeader>
            <TableHeader>Contacts</TableHeader>
            <TableHeader>Created</TableHeader>
            <TableHeader>Owner</TableHeader>
            <TableHeader>Actions</TableHeader>
          </tr>
        </thead>
        <tbody>
          {customers.map((customer) => (
            <tr key={customer.id}>
              <TableCell>
                <strong>{customer.name}</strong>
              </TableCell>
              <TableCell>
                <StatusBadge status={customer.status}>
                  {customer.status}
                </StatusBadge>
              </TableCell>
              <TableCell>
                {customerContacts[customer.id]?.length || 0} contacts
                <br />
                <Button 
                  variant="secondary" 
                  onClick={() => handleAddContact(customer.id)}
                  style={{ fontSize: '12px', padding: '4px 8px', marginTop: '4px' }}
                >
                  Add Contact
                </Button>
              </TableCell>
              <TableCell>
                {new Date(customer.created_on).toLocaleDateString()}
              </TableCell>
              <TableCell>
                {customer.owner_username}
              </TableCell>
              <TableCell>
                <Button 
                  variant="secondary" 
                  onClick={() => handleEditCustomer(customer.id)}
                  style={{ marginRight: '8px' }}
                >
                  Edit
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={() => handleDeleteCustomer(customer.id)}
                >
                  Delete
                </Button>
              </TableCell>
            </tr>
          ))}
        </tbody>
      </Table>

      {customers.length === 0 && !loading && (
        <LoadingMessage>No customers found. Create your first customer to get started.</LoadingMessage>
      )}

      <EntityForm
        title="Create New Customer"
        fields={customerFormFields}
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSubmit={handleCreateCustomer}
        onSaveDraft={handleSaveDraft}
        isSubmitting={isSubmitting}
      />

      <EntityForm
        title="Edit Customer"
        fields={customerFormFields}
        initialData={editingCustomer ? {
          name: editingCustomer.name,
          status: editingCustomer.status
        } : {}}
        isOpen={showEditForm}
        onClose={() => {
          setShowEditForm(false);
          setEditingCustomer(null);
        }}
        onSubmit={handleUpdateCustomer}
        onSaveDraft={handleSaveDraft}
        isSubmitting={isSubmitting}
      />

      <EntityForm
        title="Add Contact to Customer"
        fields={contactFormFields}
        isOpen={showContactForm}
        onClose={() => {
          setShowContactForm(false);
          setSelectedCustomerId(null);
        }}
        onSubmit={handleCreateContact}
        onSaveDraft={handleSaveContactDraft}
        isSubmitting={isSubmitting}
      />

      <ConfirmationModal
        isOpen={showDeleteConfirm}
        title="Delete Customer"
        message="Are you sure you want to delete this customer? This action cannot be undone and will permanently remove all associated data."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </Container>
  );
};

export default CustomersScreen;