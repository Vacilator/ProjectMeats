/**
 * Accounts Receivables Screen Component
 * 
 * Main screen for managing accounts receivable records migrated from 
 * PowerApps cr7c4_accountsreceivables entity.
 * 
 * Features:
 * - List view with search and filtering
 * - Create/Edit/Delete operations
 * - PowerApps migration information display
 * - Responsive design for mobile and desktop
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { AccountsReceivable, FilterOptions, MigrationInfo } from '../types';
import { AccountsReceivablesService } from '../services/api';
import { Container, MigrationInfo as SharedMigrationInfo, ErrorMessage } from '../components/SharedComponents';
import EntityForm, { FormField } from '../components/EntityForm';

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

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 16px;
  color: #666;
`;

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
`;

interface AccountsReceivablesScreenProps {}

const AccountsReceivablesScreen: React.FC<AccountsReceivablesScreenProps> = () => {
  // State management
  const [accounts, setAccounts] = useState<AccountsReceivable[]>([]);
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
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load data on component mount and when filters change
  useEffect(() => {
    loadAccounts();
  }, [currentPage, searchTerm, statusFilter]);

  useEffect(() => {
    loadMigrationInfo();
  }, []);

  // Form field definitions for Accounts Receivables
  const formFields: FormField[] = [
    {
      key: 'name',
      label: 'Name',
      type: 'text',
      required: true,
      placeholder: 'Enter account name'
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
      key: 'terms',
      label: 'Terms',
      type: 'textarea',
      placeholder: 'Enter payment terms or notes'
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

  const loadAccounts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filters: FilterOptions = {};
      if (searchTerm) filters.search = searchTerm;
      if (statusFilter !== 'all') filters.status = statusFilter as 'active' | 'inactive';
      
      const response = await AccountsReceivablesService.getList(currentPage, filters);
      
      setAccounts(response.results);
      setTotalRecords(response.count);
      setTotalPages(Math.ceil(response.count / 20)); // Assuming 20 items per page
    } catch (err) {
      setError('Failed to load accounts receivables. Please try again.');
      console.error('Error loading accounts:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMigrationInfo = async () => {
    try {
      const info = await AccountsReceivablesService.getMigrationInfo();
      setMigrationInfo(info);
    } catch (err) {
      console.error('Error loading migration info:', err);
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
  const handleCreateAccount = async (formData: Record<string, any>) => {
    try {
      setIsSubmitting(true);
      // Type-safe conversion
      const accountData = {
        name: formData.name as string,
        email: formData.email as string || undefined,
        phone: formData.phone as string || undefined,
        terms: formData.terms as string || undefined,
        status: formData.status as 'active' | 'inactive'
      };
      await AccountsReceivablesService.create(accountData);
      setShowCreateForm(false);
      loadAccounts(); // Reload the list to show new account
      setError(null);
    } catch (err) {
      setError('Failed to create account. Please try again.');
      console.error('Error creating account:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveDraft = async (formData: Record<string, any>) => {
    // For now, just log the draft - in a real app this might save to localStorage
    // or a dedicated draft API endpoint
    console.log('Saving draft:', formData);
    // You could save to localStorage here:
    localStorage.setItem('accountsReceivableDraft', JSON.stringify(formData));
  };

  const handleDeleteAccount = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this account receivable?')) {
      try {
        await AccountsReceivablesService.delete(id);
        loadAccounts(); // Reload the list
      } catch (err) {
        setError('Failed to delete account. Please try again.');
        console.error('Error deleting account:', err);
      }
    }
  };

  if (loading && accounts.length === 0) {
    return (
      <Container>
        <LoadingSpinner>Loading accounts receivables...</LoadingSpinner>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <div>
          <Title>Accounts Receivables</Title>
          <Subtitle>
            Migrated from PowerApps cr7c4_accountsreceivables • {totalRecords} total records
          </Subtitle>
        </div>
        <Controls>
          <SearchInput
            type="text"
            placeholder="Search by name or email..."
            value={searchTerm}
            onChange={handleSearch}
          />
          <FilterSelect value={statusFilter} onChange={handleStatusFilter}>
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </FilterSelect>
          <Button variant="secondary" onClick={() => setShowMigrationInfo(!showMigrationInfo)}>
            {showMigrationInfo ? 'Hide' : 'Show'} Migration Info
          </Button>
          <Button variant="primary" onClick={() => setShowCreateForm(true)}>Add New</Button>
        </Controls>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {showMigrationInfo && migrationInfo && (
        <SharedMigrationInfo>
          <strong>PowerApps Migration Information:</strong><br />
          Original Entity: {migrationInfo.powerapps_entity_name}<br />
          Django Model: {migrationInfo.django_model_name}<br />
          Total Records: {migrationInfo.total_records} ({migrationInfo.active_records} active)<br />
          API Endpoint: {migrationInfo.api_endpoints.list}
        </SharedMigrationInfo>
      )}

      <Table>
        <thead>
          <tr>
            <Th>Name</Th>
            <Th>Email</Th>
            <Th>Phone</Th>
            <Th>Terms</Th>
            <Th>Status</Th>
            <Th>Created</Th>
            <Th>Actions</Th>
          </tr>
        </thead>
        <tbody>
          {accounts.map((account) => (
            <tr key={account.id}>
              <Td>{account.name}</Td>
              <Td>{account.email || '-'}</Td>
              <Td>{account.phone || '-'}</Td>
              <Td>{account.terms || '-'}</Td>
              <Td>
                <StatusBadge status={account.status}>
                  {account.status}
                </StatusBadge>
              </Td>
              <Td>{formatDate(account.created_on)}</Td>
              <Td>
                <Button variant="secondary" style={{ marginRight: '8px' }}>
                  Edit
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={() => handleDeleteAccount(account.id)}
                >
                  Delete
                </Button>
              </Td>
            </tr>
          ))}
        </tbody>
      </Table>

      {accounts.length === 0 && !loading && (
        <LoadingSpinner>
          {searchTerm || statusFilter !== 'all' 
            ? 'No accounts receivables found matching your criteria.' 
            : 'No accounts receivables found. Click "Add New" to create the first record.'
          }
        </LoadingSpinner>
      )}

      {totalPages > 1 && (
        <Pagination>
          <Button
            variant="secondary"
            disabled={currentPage <= 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Previous
          </Button>
          <span>Page {currentPage} of {totalPages}</span>
          <Button
            variant="secondary"
            disabled={currentPage >= totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
          </Button>
        </Pagination>
      )}

      <EntityForm
        title="Create New Accounts Receivable"
        fields={formFields}
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSubmit={handleCreateAccount}
        onSaveDraft={handleSaveDraft}
        isSubmitting={isSubmitting}
      />
    </Container>
  );
};

export default AccountsReceivablesScreen;