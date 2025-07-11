/**
 * Supplier Locations Screen Component
 * 
 * Main screen for managing supplier location records migrated from 
 * PowerApps pro_supplier_locations entity.
 * 
 * Features:
 * - List view with search and filtering
 * - Display address and contact information
 * - Relationship display (supplier names)
 * - PowerApps migration information display
 * - Responsive design for mobile and desktop
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { SupplierLocation, FilterOptions, MigrationInfo } from '../types';
import { SupplierLocationsService } from '../services/api';
import { Container, MigrationInfo as SharedMigrationInfo, ErrorMessage } from '../components/SharedComponents';

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

const LocationTypeBadge = styled.span<{ type: string }>`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: #e9ecef;
  color: #495057;
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

const InfoDetail = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 2px;
`;

const ContactInfo = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 2px;
  
  > div {
    margin: 1px 0;
  }
`;

interface SupplierLocationsScreenProps {}

const SupplierLocationsScreen: React.FC<SupplierLocationsScreenProps> = () => {
  // State management
  const [locations, setLocations] = useState<SupplierLocation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [migrationInfo, setMigrationInfo] = useState<MigrationInfo | null>(null);
  const [showMigrationInfo, setShowMigrationInfo] = useState(false);

  // Load data on component mount and when filters change
  useEffect(() => {
    const loadLocations = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const filters: FilterOptions = {};
        if (searchTerm) filters.search = searchTerm;
        if (statusFilter !== 'all') filters.status = statusFilter as 'active' | 'inactive';
        
        const response = await SupplierLocationsService.getList(currentPage, filters);
        
        setLocations(response.results);
        setTotalRecords(response.count);
        setTotalPages(Math.ceil(response.count / 20)); // Assuming 20 items per page
      } catch (err) {
        setError('Failed to load supplier location records. Please try again.');
        console.error('Error loading supplier locations:', err);
      } finally {
        setLoading(false);
      }
    };

    loadLocations();
  }, [currentPage, searchTerm, statusFilter]);

  useEffect(() => {
    const loadMigrationInfo = async () => {
      try {
        const info = await SupplierLocationsService.getMigrationInfo();
        setMigrationInfo(info);
      } catch (err) {
        console.error('Error loading migration info:', err);
      }
    };

    loadMigrationInfo();
  }, []);

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

  const formatLocationType = (type: string | undefined) => {
    if (!type) return 'Not specified';
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading && locations.length === 0) {
    return (
      <Container>
        <LoadingSpinner>Loading supplier locations...</LoadingSpinner>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <div>
          <Title>Supplier Locations</Title>
          <Subtitle>
            Migrated from PowerApps pro_supplier_locations • {totalRecords} total records
          </Subtitle>
        </div>
        <Controls>
          <SearchInput
            type="text"
            placeholder="Search by name, address, city, or supplier..."
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
            <Th>Location Name</Th>
            <Th>Supplier</Th>
            <Th>Address</Th>
            <Th>Contact Info</Th>
            <Th>Location Type</Th>
            <Th>Created</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody>
          {locations.map((location) => (
            <tr key={location.id}>
              <Td>
                <div>
                  <strong>{location.name}</strong>
                  <InfoDetail>ID: {location.id}</InfoDetail>
                </div>
              </Td>
              <Td>
                <div>
                  <strong>{location.supplier_name}</strong>
                  <InfoDetail>Supplier ID: {location.supplier}</InfoDetail>
                </div>
              </Td>
              <Td>
                {location.has_address ? (
                  <div>
                    <div>{location.full_address || location.address}</div>
                    <InfoDetail>
                      {location.city && location.state && `${location.city}, ${location.state}`}
                      {location.postal_code && ` ${location.postal_code}`}
                    </InfoDetail>
                    <InfoDetail>📍 Full address available</InfoDetail>
                  </div>
                ) : (
                  <span style={{ color: '#999' }}>No address</span>
                )}
              </Td>
              <Td>
                {location.has_contact_info ? (
                  <ContactInfo>
                    {location.contact_name && <div><strong>{location.contact_name}</strong></div>}
                    {location.contact_phone && <div>📞 {location.contact_phone}</div>}
                    {location.contact_email && <div>📧 {location.contact_email}</div>}
                  </ContactInfo>
                ) : (
                  <span style={{ color: '#999' }}>No contact info</span>
                )}
              </Td>
              <Td>
                {location.location_type ? (
                  <LocationTypeBadge type={location.location_type}>
                    {formatLocationType(location.location_type)}
                  </LocationTypeBadge>
                ) : (
                  <span style={{ color: '#999' }}>Not specified</span>
                )}
              </Td>
              <Td>{formatDate(location.created_on)}</Td>
              <Td>
                <StatusBadge status={location.status}>{location.status}</StatusBadge>
              </Td>
            </tr>
          ))}
        </tbody>
      </Table>

      {locations.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          {searchTerm || statusFilter !== 'all' 
            ? 'No supplier location records found matching your filters.' 
            : 'No supplier location records available.'}
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

export default SupplierLocationsScreen;