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
import { Supplier, FilterOptions, MigrationInfo } from '../types';
import { SuppliersService } from '../services/api';

// Styled components
const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

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

const LoadingMessage = styled.div`
  text-align: center;
  padding: 40px;
  color: #666;
`;

const ErrorMessage = styled.div`
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
`;

const MigrationInfo = styled.div`
  background-color: #d1ecf1;
  color: #0c5460;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
`;

const SuppliersScreen: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [migrationInfo, setMigrationInfo] = useState<MigrationInfo | null>(null);

  useEffect(() => {
    loadSuppliers();
    loadMigrationInfo();
  }, []);

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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadSuppliers();
  };

  const handleDeleteSupplier = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this supplier?')) {
      try {
        await SuppliersService.delete(id);
        loadSuppliers(); // Reload the list
      } catch (err) {
        setError('Failed to delete supplier. Please try again.');
        console.error('Error deleting supplier:', err);
      }
    }
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
          <Button variant="primary">Add Supplier</Button>
          <Button variant="secondary">Export</Button>
        </Controls>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {migrationInfo && (
        <MigrationInfo>
          📊 PowerApps Migration Status: {migrationInfo.active_records} active suppliers 
          from {migrationInfo.powerapps_entity_name} entity
        </MigrationInfo>
      )}

      <Table>
        <thead>
          <tr>
            <TableHeader>Name</TableHeader>
            <TableHeader>Status</TableHeader>
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
                  onClick={() => console.log('Edit supplier:', supplier.id)}
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
    </Container>
  );
};

export default SuppliersScreen;