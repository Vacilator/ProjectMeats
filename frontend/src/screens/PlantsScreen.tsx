/**
 * Plants Screen Component
 * 
 * Main screen for managing plant records migrated from 
 * PowerApps cr7c4_plant entity.
 * 
 * Features:
 * - List view with search and filtering
 * - Display computed fields and storage information
 * - Relationship display (supplier names)
 * - PowerApps migration information display
 * - Responsive design for mobile and desktop
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plant, FilterOptions, MigrationInfo } from '../types';
import { PlantsService } from '../services/api';
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

const PlantTypeBadge = styled.span<{ type: string }>`
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

const StorageList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
`;

const StorageTag = styled.span`
  display: inline-block;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  background: #f1f3f4;
  color: #5f6368;
`;

interface PlantsScreenProps {}

const PlantsScreen: React.FC<PlantsScreenProps> = () => {
  // State management
  const [plants, setPlants] = useState<Plant[]>([]);
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
    const loadPlants = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const filters: FilterOptions = {};
        if (searchTerm) filters.search = searchTerm;
        if (statusFilter !== 'all') filters.status = statusFilter as 'active' | 'inactive';
        
        const response = await PlantsService.getList(currentPage, filters);
        
        setPlants(response.results);
        setTotalRecords(response.count);
        setTotalPages(Math.ceil(response.count / 20)); // Assuming 20 items per page
      } catch (err) {
        setError('Failed to load plant records. Please try again.');
        console.error('Error loading plants:', err);
      } finally {
        setLoading(false);
      }
    };

    loadPlants();
  }, [currentPage, searchTerm, statusFilter]);

  useEffect(() => {
    const loadMigrationInfo = async () => {
      try {
        const info = await PlantsService.getMigrationInfo();
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

  const formatPlantType = (type: string | undefined) => {
    if (!type) return 'Not specified';
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading && plants.length === 0) {
    return (
      <Container>
        <LoadingSpinner>Loading plants...</LoadingSpinner>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <div>
          <Title>Plants</Title>
          <Subtitle>
            Migrated from PowerApps cr7c4_plant • {totalRecords} total records
          </Subtitle>
        </div>
        <Controls>
          <SearchInput
            type="text"
            placeholder="Search by name, location, or plant type..."
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
            <Th>Plant Name</Th>
            <Th>Location</Th>
            <Th>Plant Type</Th>
            <Th>Storage Types</Th>
            <Th>Supplier</Th>
            <Th>Release Number</Th>
            <Th>Created</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody>
          {plants.map((plant) => (
            <tr key={plant.id}>
              <Td>
                <div>
                  <strong>{plant.name}</strong>
                  <InfoDetail>ID: {plant.id}</InfoDetail>
                </div>
              </Td>
              <Td>
                {plant.has_location ? (
                  <div>
                    <div>{plant.location}</div>
                    <InfoDetail>📍 Location specified</InfoDetail>
                  </div>
                ) : (
                  <span style={{ color: '#999' }}>No location</span>
                )}
              </Td>
              <Td>
                {plant.plant_type ? (
                  <PlantTypeBadge type={plant.plant_type}>
                    {formatPlantType(plant.plant_type)}
                  </PlantTypeBadge>
                ) : (
                  <span style={{ color: '#999' }}>Not specified</span>
                )}
              </Td>
              <Td>
                {plant.storage_list && plant.storage_list.length > 0 ? (
                  <StorageList>
                    {plant.storage_list.map((storage, index) => (
                      <StorageTag key={index}>{storage}</StorageTag>
                    ))}
                  </StorageList>
                ) : (
                  <span style={{ color: '#999' }}>No storage types</span>
                )}
              </Td>
              <Td>
                {plant.has_supplier ? (
                  <div>
                    <div>{plant.supplier_name}</div>
                    <InfoDetail>Supplier ID: {plant.supplier}</InfoDetail>
                  </div>
                ) : (
                  <span style={{ color: '#999' }}>No supplier</span>
                )}
              </Td>
              <Td>
                {plant.release_number ? (
                  <div>
                    <span style={{ fontFamily: 'monospace' }}>{plant.release_number}</span>
                  </div>
                ) : (
                  <span style={{ color: '#999' }}>Not set</span>
                )}
              </Td>
              <Td>{formatDate(plant.created_on)}</Td>
              <Td>
                <StatusBadge status={plant.status}>{plant.status}</StatusBadge>
              </Td>
            </tr>
          ))}
        </tbody>
      </Table>

      {plants.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          {searchTerm || statusFilter !== 'all' 
            ? 'No plant records found matching your filters.' 
            : 'No plant records available.'}
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

export default PlantsScreen;