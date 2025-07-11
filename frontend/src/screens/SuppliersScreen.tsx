/**
 * Suppliers Screen Component
 * 
 * Main screen for managing supplier records migrated from 
 * PowerApps cr7c4_supplier entity.
 * 
 * Features:
 * - List view with search and filtering
 * - Create/Edit/Delete operations
 * - PowerApps migration information display
 * - Credit application tracking
 * - Delivery type management
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Supplier, ContactInfo, Plant } from '../types';
import type { MigrationInfo } from '../types';
import { SuppliersService, ContactsService, PlantsService } from '../services/api';
import { Container, MigrationInfo as SharedMigrationInfo, ErrorMessage, LoadingMessage } from '../components/SharedComponents';
import EntityForm, { FormField } from '../components/EntityForm';
import ConfirmationModal from '../components/ConfirmationModal';

// Styled components
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
    background-color: #007bff;
    color: white;
    &:hover { background-color: #0056b3; }
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

const ClickableContactCount = styled.span`
  color: #007bff;
  cursor: pointer;
  text-decoration: underline;
  
  &:hover {
    color: #0056b3;
  }
`;

const ContactModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ContactModalContent = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  min-width: 500px;
  max-width: 80vw;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const ContactList = styled.div`
  margin-top: 16px;
`;

const ContactItem = styled.div`
  padding: 12px;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const ContactHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  margin-bottom: 8px;
`;

const ContactDetails = styled.div`
  font-size: 14px;
  color: #666;
  
  & > div {
    margin-bottom: 4px;
  }
`;

const SuppliersScreen: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [migrationInfo, setMigrationInfo] = useState<MigrationInfo | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingSupplierId, setDeletingSupplierId] = useState<number | null>(null);
  const [showContactForm, setShowContactForm] = useState(false);
  const [selectedSupplierId, setSelectedSupplierId] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [supplierContacts, setSupplierContacts] = useState<Record<number, ContactInfo[]>>({});
  const [supplierPlants, setSupplierPlants] = useState<Record<number, Plant[]>>({});
  const [showContactsModal, setShowContactsModal] = useState(false);
  const [selectedSupplierForContacts, setSelectedSupplierForContacts] = useState<Supplier | null>(null);
  const [showPlantsModal, setShowPlantsModal] = useState(false);
  const [selectedSupplierForPlants, setSelectedSupplierForPlants] = useState<Supplier | null>(null);

  useEffect(() => {
    loadSuppliers();
    loadMigrationInfo();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load contacts for all suppliers
  useEffect(() => {
    if (suppliers.length > 0) {
      loadSupplierContacts();
      loadSupplierPlants();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [suppliers]);

  // Form field definitions for Suppliers
  const formFields: FormField[] = [
    {
      key: 'name',
      label: 'Supplier Name',
      type: 'text',
      required: true,
      placeholder: 'Enter supplier name'
    },
    {
      key: 'credit_application_date',
      label: 'Credit Application Date',
      type: 'date',
      placeholder: 'Select credit application date'
    },
    {
      key: 'delivery_type_profile',
      label: 'Delivery Type Profile',
      type: 'checkbox'
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

  // Form field definitions for Contact Info (for suppliers)
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
        { value: 'procurement', label: 'Procurement Contact' }
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

  const loadSuppliers = async () => {
    try {
      setLoading(true);
      const response = await SuppliersService.getList(1, { search: searchTerm });
      setSuppliers(response.results);
      setError(null);
    } catch (err) {
      setError('Failed to load suppliers. Please try again.');
      console.error('Error loading suppliers:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMigrationInfo = async () => {
    try {
      const info = await SuppliersService.getMigrationInfo();
      setMigrationInfo(info);
    } catch (err) {
      console.error('Error loading migration info:', err);
    }
  };

  const loadSupplierContacts = async () => {
    try {
      // Load all contacts and filter by supplier ID
      const response = await ContactsService.getList(1, {});
      const contactsMap: Record<number, ContactInfo[]> = {};
      
      // Initialize empty arrays for all suppliers
      suppliers.forEach(supplier => {
        contactsMap[supplier.id] = [];
      });
      
      // Group contacts by supplier ID
      response.results.forEach(contact => {
        if (contact.supplier) {
          if (!contactsMap[contact.supplier]) {
            contactsMap[contact.supplier] = [];
          }
          contactsMap[contact.supplier].push(contact);
        }
      });
      
      // Force state update
      setSupplierContacts({ ...contactsMap });
    } catch (err) {
      console.error('Error loading supplier contacts:', err);
    }
  };

  const loadSupplierPlants = async () => {
    try {
      // Load all plants and filter by supplier ID
      const response = await PlantsService.getList(1, {});
      const plantsMap: Record<number, Plant[]> = {};
      
      // Initialize empty arrays for all suppliers
      suppliers.forEach(supplier => {
        plantsMap[supplier.id] = [];
      });
      
      // Group plants by supplier ID
      response.results.forEach(plant => {
        if (plant.supplier) {
          if (!plantsMap[plant.supplier]) {
            plantsMap[plant.supplier] = [];
          }
          plantsMap[plant.supplier].push(plant);
        }
      });
      
      // Force state update
      setSupplierPlants({ ...plantsMap });
    } catch (err) {
      console.error('Error loading supplier plants:', err);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadSuppliers();
  };

  const handleEditSupplier = (id: number) => {
    const supplier = suppliers.find(s => s.id === id);
    if (supplier) {
      setEditingSupplier(supplier);
      setShowEditForm(true);
    }
  };

  const handleUpdateSupplier = async (formData: Record<string, any>) => {
    if (!editingSupplier) return;
    
    try {
      setIsSubmitting(true);
      const supplierData = {
        name: formData.name as string,
        credit_application_date: formData.credit_application_date as string || undefined,
        delivery_type_profile: Boolean(formData.delivery_type_profile),
        status: formData.status as 'active' | 'inactive'
      };
      await SuppliersService.update(editingSupplier.id, supplierData);
      setShowEditForm(false);
      setEditingSupplier(null);
      loadSuppliers(); // Reload the list
      setError(null);
    } catch (err) {
      setError('Failed to update supplier. Please try again.');
      console.error('Error updating supplier:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteSupplier = async (id: number) => {
    setDeletingSupplierId(id);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!deletingSupplierId) return;
    
    try {
      await SuppliersService.delete(deletingSupplierId);
      loadSuppliers(); // Reload the list
      setError(null);
    } catch (err) {
      setError('Failed to delete supplier. Please try again.');
      console.error('Error deleting supplier:', err);
    } finally {
      setShowDeleteConfirm(false);
      setDeletingSupplierId(null);
    }
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setDeletingSupplierId(null);
  };

  // Form handling functions
  const handleCreateSupplier = async (formData: Record<string, any>) => {
    try {
      setIsSubmitting(true);
      // Type-safe conversion
      const supplierData = {
        name: formData.name as string,
        credit_application_date: formData.credit_application_date as string || undefined,
        delivery_type_profile: Boolean(formData.delivery_type_profile),
        status: formData.status as 'active' | 'inactive'
      };
      await SuppliersService.create(supplierData);
      setShowCreateForm(false);
      loadSuppliers(); // Reload the list to show new supplier
      setError(null);
    } catch (err) {
      setError('Failed to create supplier. Please try again.');
      console.error('Error creating supplier:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveDraft = async (formData: Record<string, any>) => {
    console.log('Saving supplier draft:', formData);
    localStorage.setItem('supplierDraft', JSON.stringify(formData));
  };

  const handleCreateContact = async (formData: Record<string, any>) => {
    try {
      setIsSubmitting(true);
      // Type-safe conversion with supplier ID
      const contactData = {
        name: formData.name as string,
        email: formData.email as string || undefined,
        phone: formData.phone as string || undefined,
        position: formData.position as string || undefined,
        contact_type: formData.contact_type as string || undefined,
        supplier: selectedSupplierId as number,
        status: formData.status as 'active' | 'inactive'
      };
      await ContactsService.create(contactData);
      setShowContactForm(false);
      setSelectedSupplierId(null);
      
      // Reload supplier contacts after backend update is confirmed
      await loadSupplierContacts();
      
      setError(null);
    } catch (err) {
      setError('Failed to create contact. Please try again.');
      console.error('Error creating contact:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveContactDraft = async (formData: Record<string, any>) => {
    console.log('Saving supplier contact draft:', formData);
    localStorage.setItem('supplierContactDraft', JSON.stringify(formData));
  };

  const handleAddContact = (supplierId: number) => {
    setSelectedSupplierId(supplierId);
    setShowContactForm(true);
  };

  const handleShowContacts = (supplier: Supplier) => {
    setSelectedSupplierForContacts(supplier);
    setShowContactsModal(true);
  };

  const handleShowPlants = (supplier: Supplier) => {
    setSelectedSupplierForPlants(supplier);
    setShowPlantsModal(true);
  };

  if (loading) {
    return (
      <Container>
        <LoadingMessage>Loading suppliers...</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <div>
          <Title>Suppliers</Title>
          <Subtitle>
            Manage supplier records migrated from PowerApps cr7c4_supplier
            {migrationInfo && ` • ${migrationInfo.total_records} total records`}
          </Subtitle>
        </div>
        <Controls>
          <form onSubmit={handleSearch}>
            <SearchInput
              type="text"
              placeholder="Search suppliers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </form>
          <Button variant="primary" onClick={() => setShowCreateForm(true)}>Add Supplier</Button>
          <Button variant="secondary">Export</Button>
        </Controls>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {migrationInfo && (
        <SharedMigrationInfo>
          📊 PowerApps Migration Status: {migrationInfo.active_records} active suppliers 
          from {migrationInfo.powerapps_entity_name} entity
        </SharedMigrationInfo>
      )}

      <Table>
        <thead>
          <tr>
            <TableHeader>Name</TableHeader>
            <TableHeader>Status</TableHeader>
            <TableHeader>Contacts</TableHeader>
            <TableHeader>Plants</TableHeader>
            <TableHeader>Delivery Type</TableHeader>
            <TableHeader>Credit Application</TableHeader>
            <TableHeader>A/R Link</TableHeader>
            <TableHeader>Created</TableHeader>
            <TableHeader>Actions</TableHeader>
          </tr>
        </thead>
        <tbody>
          {suppliers.map((supplier) => (
            <tr key={supplier.id}>
              <TableCell>
                <strong>{supplier.name}</strong>
              </TableCell>
              <TableCell>
                <StatusBadge status={supplier.status}>
                  {supplier.status}
                </StatusBadge>
              </TableCell>
              <TableCell>
                <ClickableContactCount onClick={() => handleShowContacts(supplier)}>
                  {supplierContacts[supplier.id]?.length || 0} contacts
                </ClickableContactCount>
                <br />
                <Button 
                  variant="secondary" 
                  onClick={() => handleAddContact(supplier.id)}
                  style={{ fontSize: '12px', padding: '4px 8px', marginTop: '4px' }}
                >
                  Add Contact
                </Button>
              </TableCell>
              <TableCell>
                <ClickableContactCount onClick={() => handleShowPlants(supplier)}>
                  {supplierPlants[supplier.id]?.length || 0} plants
                </ClickableContactCount>
                <br />
                <Button 
                  variant="secondary" 
                  onClick={() => alert('Plant management feature coming soon!')}
                  style={{ fontSize: '12px', padding: '4px 8px', marginTop: '4px' }}
                >
                  Manage Plants
                </Button>
              </TableCell>
              <TableCell>
                {supplier.delivery_type_profile ? '✅ Yes' : '❌ No'}
              </TableCell>
              <TableCell>
                {supplier.has_credit_application ? '📋 Applied' : '⏳ Pending'}
              </TableCell>
              <TableCell>
                {supplier.has_accounts_receivable ? supplier.accounts_receivable_name : 'None'}
              </TableCell>
              <TableCell>
                {new Date(supplier.created_on).toLocaleDateString()}
              </TableCell>
              <TableCell>
                <Button 
                  variant="secondary" 
                  onClick={() => handleEditSupplier(supplier.id)}
                  style={{ marginRight: '8px' }}
                >
                  Edit
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={() => handleDeleteSupplier(supplier.id)}
                >
                  Delete
                </Button>
              </TableCell>
            </tr>
          ))}
        </tbody>
      </Table>

      {suppliers.length === 0 && !loading && (
        <LoadingMessage>No suppliers found. Create your first supplier to get started.</LoadingMessage>
      )}

      <EntityForm
        title="Create New Supplier"
        fields={formFields}
        initialData={{}}
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSubmit={handleCreateSupplier}
        onSaveDraft={handleSaveDraft}
        isSubmitting={isSubmitting}
      />

      <EntityForm
        title="Edit Supplier"
        fields={formFields}
        initialData={editingSupplier ? {
          name: editingSupplier.name,
          credit_application_date: editingSupplier.credit_application_date || '',
          delivery_type_profile: editingSupplier.delivery_type_profile,
          status: editingSupplier.status
        } : {}}
        isOpen={showEditForm}
        onClose={() => {
          setShowEditForm(false);
          setEditingSupplier(null);
        }}
        onSubmit={handleUpdateSupplier}
        onSaveDraft={handleSaveDraft}
        isSubmitting={isSubmitting}
      />

      <EntityForm
        title="Add Contact to Supplier"
        fields={contactFormFields}
        initialData={{}}
        isOpen={showContactForm}
        onClose={() => {
          setShowContactForm(false);
          setSelectedSupplierId(null);
        }}
        onSubmit={handleCreateContact}
        onSaveDraft={handleSaveContactDraft}
        isSubmitting={isSubmitting}
      />

      <ConfirmationModal
        isOpen={showDeleteConfirm}
        title="Delete Supplier"
        message="Are you sure you want to delete this supplier? This action cannot be undone and will permanently remove all associated data."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />

      {showContactsModal && selectedSupplierForContacts && (
        <ContactModal onClick={() => setShowContactsModal(false)}>
          <ContactModalContent onClick={(e) => e.stopPropagation()}>
            <ContactHeader>
              <h3>Contacts for {selectedSupplierForContacts.name}</h3>
              <Button 
                variant="secondary" 
                onClick={() => setShowContactsModal(false)}
                style={{ padding: '4px 8px' }}
              >
                ✕
              </Button>
            </ContactHeader>
            
            {supplierContacts[selectedSupplierForContacts.id]?.length > 0 ? (
              <ContactList>
                {supplierContacts[selectedSupplierForContacts.id].map((contact) => (
                  <ContactItem key={contact.id}>
                    <ContactHeader>
                      <span>{contact.name}</span>
                      <StatusBadge status={contact.status}>
                        {contact.status}
                      </StatusBadge>
                    </ContactHeader>
                    <ContactDetails>
                      {contact.email && <div>📧 {contact.email}</div>}
                      {contact.phone && <div>📞 {contact.phone}</div>}
                      {contact.position && <div>💼 {contact.position}</div>}
                      {contact.contact_type && <div>🏷️ {contact.contact_type}</div>}
                    </ContactDetails>
                  </ContactItem>
                ))}
              </ContactList>
            ) : (
              <div style={{ textAlign: 'center', padding: '32px', color: '#666' }}>
                No contacts found for this supplier.
                <br />
                <Button 
                  variant="primary" 
                  onClick={() => {
                    setShowContactsModal(false);
                    handleAddContact(selectedSupplierForContacts.id);
                  }}
                  style={{ marginTop: '16px' }}
                >
                  Add First Contact
                </Button>
              </div>
            )}
          </ContactModalContent>
        </ContactModal>
      )}

      {showPlantsModal && selectedSupplierForPlants && (
        <ContactModal onClick={() => setShowPlantsModal(false)}>
          <ContactModalContent onClick={(e) => e.stopPropagation()}>
            <ContactHeader>
              <h3>Plants for {selectedSupplierForPlants.name}</h3>
              <Button 
                variant="secondary" 
                onClick={() => setShowPlantsModal(false)}
                style={{ padding: '4px 8px' }}
              >
                ✕
              </Button>
            </ContactHeader>
            
            {supplierPlants[selectedSupplierForPlants.id]?.length > 0 ? (
              <ContactList>
                {supplierPlants[selectedSupplierForPlants.id].map((plant) => (
                  <ContactItem key={plant.id}>
                    <ContactHeader>
                      <span>{plant.name}</span>
                      <StatusBadge status={plant.status}>
                        {plant.status}
                      </StatusBadge>
                    </ContactHeader>
                    <ContactDetails>
                      {plant.location && <div>📍 {plant.location}</div>}
                      {plant.plant_type && <div>🏭 {plant.plant_type}</div>}
                      {plant.release_number && <div>🔢 Release: {plant.release_number}</div>}
                    </ContactDetails>
                  </ContactItem>
                ))}
              </ContactList>
            ) : (
              <div style={{ textAlign: 'center', padding: '32px', color: '#666' }}>
                No plants found for this supplier.
                <br />
                <Button 
                  variant="primary" 
                  onClick={() => {
                    setShowPlantsModal(false);
                    alert('Plant creation feature coming soon!');
                  }}
                  style={{ marginTop: '16px' }}
                >
                  Add First Plant
                </Button>
              </div>
            )}
          </ContactModalContent>
        </ContactModal>
      )}
    </Container>
  );
};

export default SuppliersScreen;