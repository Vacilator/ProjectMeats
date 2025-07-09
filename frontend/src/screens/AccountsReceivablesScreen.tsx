/**
 * Enhanced Accounts Receivables Screen Component
 * 
 * Professional screen for managing accounts receivable records migrated from 
 * PowerApps cr7c4_accountsreceivables entity. Features modern UI/UX with
 * business-focused workflows for meat sales brokers.
 * 
 * Features:
 * - Modern design system integration
 * - Advanced search and filtering capabilities
 * - Create/Edit/Delete operations with enhanced UX
 * - PowerApps migration information display
 * - Responsive design for mobile and desktop
 * - Business-focused data presentation
 */
import React, { useState, useEffect } from 'react';
import { AccountsReceivable, FilterOptions, MigrationInfo } from '../types';
import { AccountsReceivablesService } from '../services/api';
import { 
  Container, 
  Card,
  Heading,
  Text,
  Button,
  Input,
  Table,
  TableHeader,
  TableRow,
  TableCell,
  Badge,
  Flex,
  Alert,
  MigrationInfo as MigrationAlert,
  LoadingSpinner
} from '../components/DesignSystem';
import EntityForm, { FormField } from '../components/EntityForm';
import ConfirmationModal from '../components/ConfirmationModal';

// Form field definitions for accounts receivables
const accountsReceivableFields: FormField[] = [
  {
    key: 'name',
    label: 'Company Name',
    type: 'text',
    required: true,
    placeholder: 'Enter company name...'
  },
  {
    key: 'email',
    label: 'Email Address',
    type: 'email',
    placeholder: 'contact@company.com'
  },
  {
    key: 'phone',
    label: 'Phone Number',
    type: 'tel',
    placeholder: '+1 (555) 123-4567'
  },
  {
    key: 'terms',
    label: 'Payment Terms',
    type: 'select',
    options: [
      { value: 'net-30', label: 'Net 30 Days' },
      { value: 'net-15', label: 'Net 15 Days' },
      { value: 'net-60', label: 'Net 60 Days' },
      { value: 'due-on-receipt', label: 'Due on Receipt' },
      { value: 'custom', label: 'Custom Terms' }
    ]
  }
];

const AccountsReceivablesScreen: React.FC = () => {
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
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingAccount, setEditingAccount] = useState<AccountsReceivable | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingAccountId, setDeletingAccountId] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load data on component mount and when filters change
  useEffect(() => {
    loadAccounts();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, searchTerm, statusFilter]);

  useEffect(() => {
    loadMigrationInfo();
  }, []);

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
    setDeletingAccountId(id);
    setShowDeleteConfirm(true);
  };

  const handleEditAccount = (id: number) => {
    const account = accounts.find(acc => acc.id === id);
    if (account) {
      setEditingAccount(account);
      setShowEditForm(true);
    }
  };

  const handleUpdateAccount = async (formData: Record<string, any>) => {
    if (!editingAccount) return;
    
    try {
      setIsSubmitting(true);
      const accountData = {
        name: formData.name as string,
        email: formData.email as string || undefined,
        phone: formData.phone as string || undefined,
        terms: formData.terms as string || undefined,
        status: formData.status as 'active' | 'inactive'
      };
      await AccountsReceivablesService.update(editingAccount.id, accountData);
      setShowEditForm(false);
      setEditingAccount(null);
      loadAccounts(); // Reload the list
      setError(null);
    } catch (err) {
      setError('Failed to update account. Please try again.');
      console.error('Error updating account:', err);
      throw err; // Re-throw to prevent form from closing
    } finally {
      setIsSubmitting(false);
    }
  };

  const confirmDelete = async () => {
    if (!deletingAccountId) return;
    
    try {
      await AccountsReceivablesService.delete(deletingAccountId);
      loadAccounts(); // Reload the list
      setError(null);
    } catch (err) {
      setError('Failed to delete account. Please try again.');
      console.error('Error deleting account:', err);
    } finally {
      setShowDeleteConfirm(false);
      setDeletingAccountId(null);
    }
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setDeletingAccountId(null);
  };

  if (loading && accounts.length === 0) {
    return (
      <Container>
        <Flex justify="center" style={{ padding: '3rem 0' }}>
          <LoadingSpinner />
          <Text style={{ marginLeft: '1rem' }}>Loading accounts receivables...</Text>
        </Flex>
      </Container>
    );
  }

  return (
    <Container>
      <Card>
        <Flex justify="between" align="start" wrap style={{ marginBottom: '2rem' }}>
          <div>
            <Heading level={1}>Accounts Receivables</Heading>
            <Text color="secondary" style={{ marginTop: '0.5rem' }}>
              Migrated from PowerApps cr7c4_accountsreceivables • {totalRecords} total records
            </Text>
          </div>
          <Flex gap="0.75rem" wrap>
            <Input
              type="text"
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={handleSearch}
              style={{ minWidth: '200px' }}
            />
            <select 
              value={statusFilter} 
              onChange={handleStatusFilter}
              style={{ 
                padding: '0.5rem 0.75rem',
                border: '1px solid #d1d5db',
                borderRadius: '0.5rem',
                fontSize: '14px'
              }}
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            <Button variant="outline" onClick={() => setShowMigrationInfo(!showMigrationInfo)}>
              {showMigrationInfo ? 'Hide' : 'Show'} Migration Info
            </Button>
            <Button variant="primary" onClick={() => setShowCreateForm(true)}>
              Add New Account
            </Button>
          </Flex>
        </Flex>

        {error && (
          <Alert variant="error" style={{ marginBottom: '1.5rem' }}>
            {error}
          </Alert>
        )}

        {showMigrationInfo && migrationInfo && (
          <MigrationAlert style={{ marginBottom: '1.5rem' }}>
            <strong>🏢 PowerApps Migration Information:</strong><br />
            Original Entity: {migrationInfo.powerapps_entity_name}<br />
            Django Model: {migrationInfo.django_model_name}<br />
            Total Records: {migrationInfo.total_records} ({migrationInfo.active_records} active)<br />
            API Endpoint: {migrationInfo.api_endpoints.list}
          </MigrationAlert>
        )}

        <Table>
          <thead>
            <tr>
              <TableHeader>Name</TableHeader>
              <TableHeader>Email</TableHeader>
              <TableHeader>Phone</TableHeader>
              <TableHeader>Terms</TableHeader>
              <TableHeader>Status</TableHeader>
              <TableHeader>Created</TableHeader>
              <TableHeader>Actions</TableHeader>
            </tr>
          </thead>
          <tbody>
            {accounts.map((account) => (
              <TableRow key={account.id}>
                <TableCell>
                  <Text weight="semibold">{account.name}</Text>
                </TableCell>
                <TableCell>{account.email || '-'}</TableCell>
                <TableCell>{account.phone || '-'}</TableCell>
                <TableCell>{account.terms || '-'}</TableCell>
                <TableCell>
                  <Badge variant={account.status === 'active' ? 'success' : 'neutral'}>
                    {account.status}
                  </Badge>
                </TableCell>
                <TableCell>{formatDate(account.created_on)}</TableCell>
                <TableCell>
                  <Flex gap="0.5rem">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleEditAccount(account.id)}
                    >
                      Edit
                    </Button>
                    <Button 
                      variant="danger" 
                      size="sm"
                      onClick={() => handleDeleteAccount(account.id)}
                    >
                      Delete
                    </Button>
                  </Flex>
                </TableCell>
              </TableRow>
            ))}
          </tbody>
        </Table>

        {accounts.length === 0 && !loading && (
          <div style={{ textAlign: 'center', padding: '3rem 0' }}>
            <Text color="secondary">
              {searchTerm || statusFilter !== 'all' 
                ? 'No accounts receivables found matching your criteria.' 
                : 'No accounts receivables found. Click "Add New Account" to create the first record.'
              }
            </Text>
          </div>
        )}

        {totalPages > 1 && (
          <Flex justify="center" align="center" gap="1rem" style={{ marginTop: '2rem' }}>
            <Button
              variant="outline"
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage(currentPage - 1)}
            >
              Previous
            </Button>
            <Text>Page {currentPage} of {totalPages}</Text>
            <Button
              variant="outline"
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage(currentPage + 1)}
            >
              Next
            </Button>
          </Flex>
        )}
      </Card>

      <EntityForm
        title="Create New Accounts Receivable"
        fields={accountsReceivableFields}
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSubmit={handleCreateAccount}
        onSaveDraft={handleSaveDraft}
        isSubmitting={isSubmitting}
      />

      <EntityForm
        title="Edit Account"
        fields={accountsReceivableFields}
        initialData={editingAccount ? {
          name: editingAccount.name,
          email: editingAccount.email || '',
          phone: editingAccount.phone || '',
          terms: editingAccount.terms || '',
          status: editingAccount.status
        } : {}}
        isOpen={showEditForm}
        onClose={() => {
          setShowEditForm(false);
          setEditingAccount(null);
        }}
        onSubmit={handleUpdateAccount}
        onSaveDraft={handleSaveDraft}
        isSubmitting={isSubmitting}
      />

      <ConfirmationModal
        isOpen={showDeleteConfirm}
        title="Delete Account"
        message="Are you sure you want to delete this account receivable? This action cannot be undone and will permanently remove all associated data."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </Container>
  );
};

export default AccountsReceivablesScreen;