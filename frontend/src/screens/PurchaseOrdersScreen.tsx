/**
 * Purchase Orders Screen Component
 * 
 * Main screen for managing purchase order records migrated from 
 * PowerApps pro_purchaseorder entity.
 * 
 * Features:
 * - List view with search and filtering
 * - Display computed fields (total_amount, is_fulfilled, has_documents)
 * - Relationship display (customer and supplier names)
 * - PowerApps migration information display
 * - Responsive design for mobile and desktop
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { PurchaseOrder, Customer, Supplier } from '../types';
import type { MigrationInfo } from '../types';
import { PurchaseOrdersService, CustomersService, SuppliersService } from '../services/api';
import { Container, MigrationInfo as SharedMigrationInfo, ErrorMessage, LoadingMessage } from '../components/SharedComponents';
import EntityForm, { FormField } from '../components/EntityForm';
import ConfirmationModal from '../components/ConfirmationModal';

// Styled components (reusing consistent patterns)
const Header = styled.div`
  display: flex;
  justify-content: space-between;
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

const SearchInput = styled.input`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
`;

const FilterSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 8px 16px;
  border: 1px solid ${props => props.variant === 'primary' ? '#007bff' : '#ddd'};
  background: ${props => props.variant === 'primary' ? '#007bff' : 'white'};
  color: ${props => props.variant === 'primary' ? 'white' : '#333'};
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    opacity: 0.9;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Th = styled.th`
  background: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #ddd;
`;

const Td = styled.td`
  padding: 12px;
  border-bottom: 1px solid #eee;
  
  &:last-child {
    text-align: right;
  }
`;

const StatusBadge = styled.span<{ status: 'active' | 'inactive' }>`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => props.status === 'active' ? '#d4edda' : '#f8d7da'};
  color: ${props => props.status === 'active' ? '#155724' : '#721c24'};
`;

const FulfillmentBadge = styled.span<{ fulfilled: boolean }>`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => props.fulfilled ? '#fff3cd' : '#d1ecf1'};
  color: ${props => props.fulfilled ? '#856404' : '#0c5460'};
`;

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
`;

interface PurchaseOrdersScreenProps {}

const PurchaseOrdersScreen: React.FC<PurchaseOrdersScreenProps> = () => {
  // State management
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [migrationInfo, setMigrationInfo] = useState<MigrationInfo | null>(null);
  const [showMigrationInfo, setShowMigrationInfo] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingPurchaseOrder, setEditingPurchaseOrder] = useState<PurchaseOrder | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingPurchaseOrderId, setDeletingPurchaseOrderId] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);

  // Load data on component mount and when filters change
  useEffect(() => {
    loadPurchaseOrders();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, searchTerm, statusFilter]);

  useEffect(() => {
    loadMigrationInfo();
    loadCustomersAndSuppliers();
  }, []);

  // Form field definitions for Purchase Orders
  const formFields: FormField[] = [
    {
      key: 'po_number',
      label: 'PO Number',
      type: 'text',
      required: true,
      placeholder: 'Enter purchase order number'
    },
    {
      key: 'item',
      label: 'Item',
      type: 'text',
      required: true,
      placeholder: 'Enter item description'
    },
    {
      key: 'quantity',
      label: 'Quantity',
      type: 'text',
      required: true,
      placeholder: 'Enter quantity'
    },
    {
      key: 'price_per_unit',
      label: 'Price per Unit',
      type: 'text',
      required: true,
      placeholder: 'Enter price per unit'
    },
    {
      key: 'purchase_date',
      label: 'Purchase Date',
      type: 'date',
      required: true
    },
    {
      key: 'fulfillment_date',
      label: 'Fulfillment Date',
      type: 'date'
    },
    {
      key: 'customer',
      label: 'Customer',
      type: 'select',
      required: true,
      options: customers.map(customer => ({ value: customer.id, label: customer.name }))
    },
    {
      key: 'supplier',
      label: 'Supplier',
      type: 'select',
      required: true,
      options: suppliers.map(supplier => ({ value: supplier.id, label: supplier.name }))
    },
    {
      key: 'customer_documents',
      label: 'Customer Documents',
      type: 'file',
      accept: '.pdf,.doc,.docx,.txt,.jpg,.png',
      multiple: true,
      placeholder: 'Upload customer documents'
    },
    {
      key: 'supplier_documents',
      label: 'Supplier Documents',
      type: 'file',
      accept: '.pdf,.doc,.docx,.txt,.jpg,.png',
      multiple: true,
      placeholder: 'Upload supplier documents'
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

  const loadPurchaseOrders = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filters: any = {};
      if (searchTerm) filters.search = searchTerm;
      if (statusFilter !== 'all') filters.status = statusFilter as 'active' | 'inactive';
      
      const response = await PurchaseOrdersService.getList(currentPage, filters);
      
      setPurchaseOrders(response.results);
      setTotalRecords(response.count);
      setTotalPages(Math.ceil(response.count / 20)); // Assuming 20 items per page
    } catch (err) {
      setError('Failed to load purchase orders. Please try again.');
      console.error('Error loading purchase orders:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMigrationInfo = async () => {
    try {
      const info = await PurchaseOrdersService.getMigrationInfo();
      setMigrationInfo(info);
    } catch (err) {
      console.error('Error loading migration info:', err);
    }
  };

  const loadCustomersAndSuppliers = async () => {
    try {
      const [customersResponse, suppliersResponse] = await Promise.all([
        CustomersService.getList(1, {}),
        SuppliersService.getList(1, {})
      ]);
      setCustomers(customersResponse.results);
      setSuppliers(suppliersResponse.results);
    } catch (err) {
      console.error('Error loading customers and suppliers:', err);
    }
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1); // Reset to first page
  };

  const handleStatusFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value as 'all' | 'active' | 'inactive');
    setCurrentPage(1); // Reset to first page
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Form handling functions
  const handleCreatePurchaseOrder = async (formData: Record<string, any>) => {
    try {
      setIsSubmitting(true);
      // Type-safe conversion
      const purchaseOrderData = {
        po_number: formData.po_number as string,
        item: formData.item as string,
        quantity: Number(formData.quantity),
        price_per_unit: formData.price_per_unit as string,
        purchase_date: formData.purchase_date as string,
        fulfillment_date: formData.fulfillment_date as string || undefined,
        customer: Number(formData.customer),
        supplier: Number(formData.supplier),
        customer_documents: formData.customer_documents as string || undefined,
        supplier_documents: formData.supplier_documents as string || undefined,
        status: formData.status as 'active' | 'inactive'
      };
      await PurchaseOrdersService.create(purchaseOrderData);
      setShowCreateForm(false);
      loadPurchaseOrders(); // Reload the list to show new purchase order
      setError(null);
    } catch (err) {
      setError('Failed to create purchase order. Please try again.');
      console.error('Error creating purchase order:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveDraft = async (formData: Record<string, any>) => {
    console.log('Saving purchase order draft:', formData);
    localStorage.setItem('purchaseOrderDraft', JSON.stringify(formData));
  };

  const handleEditPurchaseOrder = async (id: number) => {
    const order = purchaseOrders.find(po => po.id === id);
    if (order) {
      setEditingPurchaseOrder(order);
      setShowEditForm(true);
    }
  };

  const handleUpdatePurchaseOrder = async (formData: Record<string, any>) => {
    if (!editingPurchaseOrder) return;
    
    try {
      setIsSubmitting(true);
      // Type-safe conversion for update
      const updateData = {
        po_number: formData.po_number as string,
        item: formData.item as string,
        quantity: Number(formData.quantity),
        price_per_unit: formData.price_per_unit as string,
        purchase_date: formData.purchase_date as string,
        fulfillment_date: formData.fulfillment_date as string || undefined,
        customer: Number(formData.customer),
        supplier: Number(formData.supplier),
        customer_documents: formData.customer_documents || undefined,
        supplier_documents: formData.supplier_documents || undefined,
        status: formData.status as 'active' | 'inactive'
      };
      
      await PurchaseOrdersService.update(editingPurchaseOrder.id, updateData);
      setShowEditForm(false);
      setEditingPurchaseOrder(null);
      loadPurchaseOrders(); // Reload the list
      setError(null);
    } catch (err) {
      setError('Failed to update purchase order. Please try again.');
      console.error('Error updating purchase order:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeletePurchaseOrder = (id: number) => {
    setDeletingPurchaseOrderId(id);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!deletingPurchaseOrderId) return;
    
    try {
      await PurchaseOrdersService.delete(deletingPurchaseOrderId);
      loadPurchaseOrders(); // Reload the list
      setError(null);
    } catch (err) {
      setError('Failed to delete purchase order. Please try again.');
      console.error('Error deleting purchase order:', err);
    } finally {
      setShowDeleteConfirm(false);
      setDeletingPurchaseOrderId(null);
    }
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setDeletingPurchaseOrderId(null);
  };

  const formatCurrency = (amount: string) => {
    return `$${parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  };

  if (loading && purchaseOrders.length === 0) {
    return (
      <Container>
        <LoadingMessage>Loading purchase orders...</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <div>
          <Title>Purchase Orders</Title>
          <Subtitle>
            Migrated from PowerApps pro_purchaseorder • {totalRecords} total records
          </Subtitle>
        </div>
        <Controls>
          <SearchInput
            type="text"
            placeholder="Search by PO number or item..."
            value={searchTerm}
            onChange={handleSearch}
          />
          <FilterSelect value={statusFilter} onChange={handleStatusFilter}>
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </FilterSelect>
          <Button
            variant="secondary"
            onClick={() => setShowMigrationInfo(!showMigrationInfo)}
          >
            {showMigrationInfo ? 'Hide' : 'Show'} Migration Info
          </Button>
          <Button
            variant="primary"
            onClick={() => setShowCreateForm(true)}
          >
            Add Purchase Order
          </Button>
        </Controls>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {showMigrationInfo && migrationInfo && (
        <SharedMigrationInfo>
          <strong>PowerApps Migration Info:</strong><br />
          Entity: {migrationInfo.powerapps_entity_name} → {migrationInfo.django_model_name}<br />
          Records: {migrationInfo.active_records} active / {migrationInfo.total_records} total<br />
          <details style={{ marginTop: '8px' }}>
            <summary>Field Mappings</summary>
            <pre style={{ fontSize: '12px', marginTop: '8px' }}>
              {JSON.stringify(migrationInfo.field_mappings, null, 2)}
            </pre>
          </details>
        </SharedMigrationInfo>
      )}

      <Table>
        <thead>
          <tr>
            <Th>PO Number</Th>
            <Th>Item</Th>
            <Th>Quantity</Th>
            <Th>Unit Price</Th>
            <Th>Total</Th>
            <Th>Customer</Th>
            <Th>Supplier</Th>
            <Th>Purchase Date</Th>
            <Th>Fulfillment</Th>
            <Th>Status</Th>
            <Th>Actions</Th>
          </tr>
        </thead>
        <tbody>
          {purchaseOrders.map((order) => (
            <tr key={order.id}>
              <Td>
                <strong>{order.po_number}</strong>
                {order.has_documents && (
                  <div style={{ fontSize: '12px', color: '#666' }}>📎 Has Documents</div>
                )}
              </Td>
              <Td>
                <div>{order.item}</div>
              </Td>
              <Td>{order.quantity}</Td>
              <Td>{formatCurrency(order.price_per_unit)}</Td>
              <Td><strong>{formatCurrency(order.total_amount)}</strong></Td>
              <Td>{order.customer_name}</Td>
              <Td>{order.supplier_name}</Td>
              <Td>{formatDate(order.purchase_date)}</Td>
              <Td>
                {order.fulfillment_date ? (
                  <div>
                    <div>{formatDate(order.fulfillment_date)}</div>
                    <FulfillmentBadge fulfilled={order.is_fulfilled}>
                      {order.is_fulfilled ? 'Fulfilled' : 'Pending'}
                    </FulfillmentBadge>
                  </div>
                ) : (
                  <span style={{ color: '#999' }}>Not set</span>
                )}
              </Td>
              <Td>
                <StatusBadge status={order.status}>{order.status}</StatusBadge>
              </Td>
              <Td>
                <Button 
                  variant="secondary" 
                  style={{ marginRight: '8px' }}
                  onClick={() => handleEditPurchaseOrder(order.id)}
                >
                  Edit
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={() => handleDeletePurchaseOrder(order.id)}
                >
                  Delete
                </Button>
              </Td>
            </tr>
          ))}
        </tbody>
      </Table>

      {purchaseOrders.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          {searchTerm || statusFilter !== 'all' 
            ? 'No purchase orders found matching your filters.' 
            : 'No purchase orders available.'}
        </div>
      )}

      {totalPages > 1 && (
        <Pagination>
          <Button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
          >
            Previous
          </Button>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <Button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
          >
            Next
          </Button>
        </Pagination>
      )}

      <EntityForm
        title="Create New Purchase Order"
        fields={formFields}
        initialData={{}}
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSubmit={handleCreatePurchaseOrder}
        onSaveDraft={handleSaveDraft}
        isSubmitting={isSubmitting}
      />

      <EntityForm
        title="Edit Purchase Order"
        fields={formFields}
        initialData={editingPurchaseOrder ? {
          po_number: editingPurchaseOrder.po_number,
          item: editingPurchaseOrder.item,
          quantity: editingPurchaseOrder.quantity,
          price_per_unit: editingPurchaseOrder.price_per_unit,
          purchase_date: editingPurchaseOrder.purchase_date,
          fulfillment_date: editingPurchaseOrder.fulfillment_date || '',
          customer: editingPurchaseOrder.customer,
          supplier: editingPurchaseOrder.supplier,
          customer_documents: editingPurchaseOrder.customer_documents || '',
          supplier_documents: editingPurchaseOrder.supplier_documents || '',
          status: editingPurchaseOrder.status
        } : {}}
        isOpen={showEditForm}
        onClose={() => {
          setShowEditForm(false);
          setEditingPurchaseOrder(null);
        }}
        onSubmit={handleUpdatePurchaseOrder}
        onSaveDraft={handleSaveDraft}
        isSubmitting={isSubmitting}
      />

      <ConfirmationModal
        isOpen={showDeleteConfirm}
        title="Delete Purchase Order"
        message="Are you sure you want to delete this purchase order? This action cannot be undone and will permanently remove all associated data."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </Container>
  );
};

export default PurchaseOrdersScreen;