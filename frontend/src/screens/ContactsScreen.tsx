/**
 * Contact Inf// Styled components with unique color scheme for contacts
const Header = styled.div` Screen Component
 * 
 * Main screen for managing contact information records migrated from 
 * PowerApps pro_contactinfo entity.
 * 
 * Features:
 * - List view with search and filtering
 * - Create/Edit/Delete operations
 * - PowerApps migration information display
 * - Customer and supplier relationship management
 * - Contact details tracking
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ContactInfo, FilterOptions } from '../types';
import type { MigrationInfo } from '../types';
import { ContactsService } from '../services/api';
import { Container, MigrationInfo as SharedMigrationInfo, ErrorMessage, LoadingMessage } from '../components/SharedComponents';

// Styled components with unique color scheme for contacts
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
    background-color: #6f42c1;
    color: white;
    &:hover { background-color: #5a32a3; }
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
  font-size: 13px;
`;

const TableCell = styled.td`
  padding: 12px;
  border-bottom: 1px solid #f1f1f1;
  font-size: 14px;
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

const ContactBadge = styled.span<{ type: string }>`
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  margin-right: 4px;
  
  ${props => props.type === 'email' ? `
    background-color: #cce5ff;
    color: #0066cc;
  ` : `
    background-color: #e6f3ff;
    color: #0080ff;
  `}
`;

const RelationshipTag = styled.span<{ type: 'customer' | 'supplier' }>`
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  
  ${props => props.type === 'customer' ? `
    background-color: #d4edda;
    color: #155724;
  ` : `
    background-color: #d1ecf1;
    color: #0c5460;
  `}
`;

const ContactsScreen: React.FC = () => {
  const [contacts, setContacts] = useState<ContactInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [migrationInfo, setMigrationInfo] = useState<MigrationInfo | null>(null);

  useEffect(() => {
    loadContacts();
    loadMigrationInfo();
  }, []);

  const loadContacts = async () => {
    try {
      setLoading(true);
      const response = await ContactsService.getList(1, { search: searchTerm });
      setContacts(response.results);
      setError(null);
    } catch (err) {
      setError('Failed to load contact information. Please try again.');
      console.error('Error loading contacts:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMigrationInfo = async () => {
    try {
      const info = await ContactsService.getMigrationInfo();
      setMigrationInfo(info);
    } catch (err) {
      console.error('Error loading migration info:', err);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadContacts();
  };

  const handleDeleteContact = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      try {
        await ContactsService.delete(id);
        loadContacts(); // Reload the list
      } catch (err) {
        setError('Failed to delete contact. Please try again.');
        console.error('Error deleting contact:', err);
      }
    }
  };

  if (loading) {
    return (
      <Container>
        <LoadingMessage>Loading contact information...</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <div>
          <Title>Contact Information</Title>
          <Subtitle>
            Manage contact records migrated from PowerApps pro_contactinfo
            {migrationInfo && ` • ${migrationInfo.total_records} total records`}
          </Subtitle>
        </div>
        <Controls>
          <form onSubmit={handleSearch}>
            <SearchInput
              type="text"
              placeholder="Search contacts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </form>
          <Button variant="primary">Add Contact</Button>
          <Button variant="secondary">Export</Button>
        </Controls>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {migrationInfo && (
        <SharedMigrationInfo>
          📞 PowerApps Migration Status: {migrationInfo.active_records} active contacts 
          from {migrationInfo.powerapps_entity_name} entity
        </SharedMigrationInfo>
      )}

      <Table>
        <thead>
          <tr>
            <TableHeader>Name</TableHeader>
            <TableHeader>Contact Details</TableHeader>
            <TableHeader>Position</TableHeader>
            <TableHeader>Type</TableHeader>
            <TableHeader>Relationships</TableHeader>
            <TableHeader>Status</TableHeader>
            <TableHeader>Created</TableHeader>
            <TableHeader>Actions</TableHeader>
          </tr>
        </thead>
        <tbody>
          {contacts.map((contact) => (
            <tr key={contact.id}>
              <TableCell>
                <strong>{contact.name}</strong>
              </TableCell>
              <TableCell>
                <div>
                  {contact.email && (
                    <div>
                      <ContactBadge type="email">📧</ContactBadge>
                      {contact.email}
                    </div>
                  )}
                  {contact.phone && (
                    <div>
                      <ContactBadge type="phone">📞</ContactBadge>
                      {contact.phone}
                    </div>
                  )}
                  {!contact.has_contact_details && (
                    <span style={{ color: '#999', fontStyle: 'italic' }}>
                      No contact details
                    </span>
                  )}
                </div>
              </TableCell>
              <TableCell>
                {contact.position || '-'}
              </TableCell>
              <TableCell>
                {contact.contact_type || '-'}
              </TableCell>
              <TableCell>
                <div>
                  {contact.customer_name && (
                    <div>
                      <RelationshipTag type="customer">Customer</RelationshipTag>
                      {contact.customer_name}
                    </div>
                  )}
                  {contact.supplier_name && (
                    <div>
                      <RelationshipTag type="supplier">Supplier</RelationshipTag>
                      {contact.supplier_name}
                    </div>
                  )}
                  {!contact.has_relationships && (
                    <span style={{ color: '#999', fontStyle: 'italic' }}>
                      No relationships
                    </span>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <StatusBadge status={contact.status}>
                  {contact.status}
                </StatusBadge>
              </TableCell>
              <TableCell>
                {new Date(contact.created_on).toLocaleDateString()}
              </TableCell>
              <TableCell>
                <Button 
                  variant="secondary" 
                  onClick={() => console.log('Edit contact:', contact.id)}
                  style={{ marginRight: '8px' }}
                >
                  Edit
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={() => handleDeleteContact(contact.id)}
                >
                  Delete
                </Button>
              </TableCell>
            </tr>
          ))}
        </tbody>
      </Table>

      {contacts.length === 0 && !loading && (
        <LoadingMessage>No contacts found. Create your first contact to get started.</LoadingMessage>
      )}
    </Container>
  );
};

export default ContactsScreen;