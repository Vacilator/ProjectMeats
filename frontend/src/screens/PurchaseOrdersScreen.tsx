/**
 * Purchase Orders Screen Component
 * 
 * Main screen for managing purchase order records migrated from 
 * PowerApps pro_purchaseorder entity.
 * 
 * Features:
 * - List view with search and filtering
 * - Create/Edit/Delete operations
 * - PowerApps migration information display
 * - Customer and Supplier relationships
 * - Responsive design for mobile and desktop
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { PurchaseOrder, FilterOptions, MigrationInfo } from '../types';
import { PurchaseOrdersService } from '../services/api';

// Reuse styled components from other screens for consistency
const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

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
  width: 250px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
`;

const Button = styled.button<{ variant: 'primary' | 'secondary' | 'danger' }>`
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  
  ${props => props.variant === 'primary' && `
    background: #007bff;
    color: white;
    
    &:hover {
      background: #0056b3;
    }
  `}
  
  ${props => props.variant === 'secondary' && `
    background: #6c757d;
    color: white;
    
    &:hover {
      background: #545b62;
    }
  `}
  
  ${props => props.variant === 'danger' && `
    background: #dc3545;
    color: white;
    
    &:hover {
      background: #c82333;
    }
  `}
`;

const ErrorMessage = styled.div`
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  border: 1px solid #f5c6cb;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
`;

const MigrationInfo = styled.div`
  background: #d1ecf1;
  color: #0c5460;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  border: 1px solid #bee5eb;
  font-size: 14px;
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
  color: #495057;
  border-bottom: 2px solid #dee2e6;
`;

const TableCell = styled.td`
  padding: 12px;
  border-bottom: 1px solid #dee2e6;
  vertical-align: top;
`;

const StatusBadge = styled.span<{ status: string }>`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  
  ${props => props.status === 'active' ? `
    background: #d4edda;
    color: #155724;
  ` : `
    background: #f8d7da;
    color: #721c24;
  `}
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 14px;
  margin-right: 8px;
  
  &:hover {
    text-decoration: underline;
  }
  
  &:last-child {
    margin-right: 0;
  }
`;

const ComputedFields = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 4px;
`;

const PurchaseOrdersScreen: React.FC = () => {
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [migrationInfo, setMigrationInfo] = useState<MigrationInfo | null>(null);

  useEffect(() => {
    loadPurchaseOrders();
    loadMigrationInfo();
  }, []);

  const loadPurchaseOrders = async () => {
    try {
      setLoading(true);
      const response = await PurchaseOrdersService.getList(1, { search: searchTerm });
      setPurchaseOrders(response.results);
      setError(null);
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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadPurchaseOrders();
  };

  const handleDeletePurchaseOrder = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this purchase order?')) {
      try {
        await PurchaseOrdersService.delete(id);
        loadPurchaseOrders(); // Reload the list
      } catch (err) {
        setError('Failed to delete purchase order. Please try again.');
        console.error('Error deleting purchase order:', err);
      }
    }
  };

  const formatCurrency = (amount: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(parseFloat(amount));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
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
            Manage purchase order records migrated from PowerApps pro_purchaseorder
            {migrationInfo && ` • ${migrationInfo.total_records} total records`}
          </Subtitle>
        </div>
        <Controls>
          <form onSubmit={handleSearch}>
            <SearchInput
              type="text"
              placeholder="Search purchase orders..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </form>
          <Button variant="primary">Add Purchase Order</Button>
          <Button variant="secondary">Export</Button>
        </Controls>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {migrationInfo && (
        <MigrationInfo>
          📦 PowerApps Migration Status: {migrationInfo.active_records} active purchase orders 
          from {migrationInfo.powerapps_entity_name} entity
        </MigrationInfo>
      )}

      <Table>
        <thead>
          <tr>
            <TableHeader>PO Number</TableHeader>
            <TableHeader>Item</TableHeader>
            <TableHeader>Customer</TableHeader>
            <TableHeader>Supplier</TableHeader>
            <TableHeader>Quantity</TableHeader>
            <TableHeader>Unit Price</TableHeader>
            <TableHeader>Total</TableHeader>
            <TableHeader>Purchase Date</TableHeader>
            <TableHeader>Status</TableHeader>
            <TableHeader>Actions</TableHeader>
          </tr>
        </thead>
        <tbody>
          {purchaseOrders.map((po) => (
            <tr key={po.id}>
              <TableCell>
                <strong>{po.po_number}</strong>
                <ComputedFields>
                  {po.is_fulfilled ? '✅ Fulfilled' : '⏳ Pending'}
                  {po.has_documents && ' • 📎 Has Docs'}
                </ComputedFields>
              </TableCell>
              <TableCell>
                {po.item}
              </TableCell>
              <TableCell>
                {po.customer_name}
              </TableCell>
              <TableCell>
                {po.supplier_name}
              </TableCell>
              <TableCell>
                {po.quantity}
              </TableCell>
              <TableCell>
                {formatCurrency(po.price_per_unit)}
              </TableCell>
              <TableCell>
                <strong>{formatCurrency(po.total_amount)}</strong>
              </TableCell>
              <TableCell>
                {formatDate(po.purchase_date)}
                {po.fulfillment_date && (
                  <ComputedFields>
                    Expected: {formatDate(po.fulfillment_date)}
                  </ComputedFields>
                )}
              </TableCell>
              <TableCell>
                <StatusBadge status={po.status}>
                  {po.status}
                </StatusBadge>
              </TableCell>
              <TableCell>
                <ActionButton>Edit</ActionButton>
                <ActionButton>View</ActionButton>
                <ActionButton 
                  onClick={() => handleDeletePurchaseOrder(po.id)}
                  style={{ color: '#dc3545' }}
                >
                  Delete
                </ActionButton>
              </TableCell>
            </tr>
          ))}
        </tbody>
      </Table>

      {purchaseOrders.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          {searchTerm ? 'No purchase orders found matching your search.' : 'No purchase orders found.'}
        </div>
      )}
    </Container>
  );
};

export default PurchaseOrdersScreen;