/**
 * Supplier Plant Mappings Screen Component
 * 
 * Main screen for managing supplier plant mapping records migrated from 
 * PowerApps pro_supplierplantmapping entity.
 * 
 * Features:
 * - List view with search and filtering
 * - Display relationship information (supplier, customer, contact info)
 * - Document reference indicators
 * - PowerApps migration information display
 * - Responsive design for mobile and desktop
 */
import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { SupplierPlantMapping, FilterOptions } from '../types';
import { SupplierPlantMappingsService } from '../services/api';
import { Container, ErrorMessage, LoadingMessage } from '../components/SharedComponents';

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

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
`;

const RelationshipInfo = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 2px;
`;

interface SupplierPlantMappingsScreenProps {}

const SupplierPlantMappingsScreen: React.FC<SupplierPlantMappingsScreenProps> = () => {
  // State management
  const [mappings, setMappings] = useState<SupplierPlantMapping[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  const loadMappings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filters: FilterOptions = {};
      if (searchTerm) filters.search = searchTerm;
      if (statusFilter !== 'all') filters.status = statusFilter as 'active' | 'inactive';
      
      const response = await SupplierPlantMappingsService.getList(currentPage, filters);
      
      setMappings(response.results);
      setTotalRecords(response.count);
      setTotalPages(Math.ceil(response.count / 20)); // Assuming 20 items per page
    } catch (err) {
      setError('Failed to load supplier plant mappings. Please try again.');
      console.error('Error loading mappings:', err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, statusFilter]);

  // Load data on component mount and when filters change
  useEffect(() => {
    loadMappings();
  }, [loadMappings]);

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

  if (loading && mappings.length === 0) {
    return (
      <Container>
        <LoadingMessage>Loading supplier plant mappings...</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <div>
          <Title>Supplier Plant Mappings</Title>
          <Subtitle>
            Migrated from PowerApps pro_supplierplantmapping • {totalRecords} total records
          </Subtitle>
        </div>
        <Controls>
          <SearchInput
            type="text"
            placeholder="Search by mapping name..."
            value={searchTerm}
            onChange={handleSearch}
          />
          <FilterSelect value={statusFilter} onChange={handleStatusFilter}>
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </FilterSelect>
        </Controls>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}


      <Table>
        <thead>
          <tr>
            <Th>Mapping Name</Th>
            <Th>Supplier</Th>
            <Th>Customer</Th>
            <Th>Contact Info</Th>
            <Th>Documents</Th>
            <Th>Created</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody>
          {mappings.map((mapping) => (
            <tr key={mapping.id}>
              <Td>
                <div>
                  <strong>{mapping.name}</strong>
                  <RelationshipInfo>
                    ID: {mapping.id}
                  </RelationshipInfo>
                </div>
              </Td>
              <Td>
                <div>{mapping.supplier_name}</div>
                <RelationshipInfo>Supplier ID: {mapping.supplier}</RelationshipInfo>
              </Td>
              <Td>
                <div>{mapping.customer_name}</div>
                <RelationshipInfo>Customer ID: {mapping.customer}</RelationshipInfo>
              </Td>
              <Td>
                {mapping.has_contact_info ? (
                  <div>
                    <div>{mapping.contact_info_name || 'Contact Info'}</div>
                    <RelationshipInfo>Contact ID: {mapping.contact_info}</RelationshipInfo>
                  </div>
                ) : (
                  <span style={{ color: '#999' }}>No contact</span>
                )}
              </Td>
              <Td>
                {mapping.has_documents ? (
                  <div>
                    <span style={{ color: '#007bff' }}>📎 Has Documents</span>
                    {mapping.documents_reference && (
                      <RelationshipInfo>
                        Ref: {mapping.documents_reference.substring(0, 30)}
                        {mapping.documents_reference.length > 30 && '...'}
                      </RelationshipInfo>
                    )}
                  </div>
                ) : (
                  <span style={{ color: '#999' }}>No documents</span>
                )}
              </Td>
              <Td>{formatDate(mapping.created_on)}</Td>
              <Td>
                <StatusBadge status={mapping.status}>{mapping.status}</StatusBadge>
              </Td>
            </tr>
          ))}
        </tbody>
      </Table>

      {mappings.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          {searchTerm || statusFilter !== 'all' 
            ? 'No supplier plant mappings found matching your filters.' 
            : 'No supplier plant mappings available.'}
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
    </Container>
  );
};

export default SupplierPlantMappingsScreen;