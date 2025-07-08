/**
 * TypeScript type definitions for ProjectMeats application.
 * 
 * Defines interfaces that match the Django REST API responses
 * for entities migrated from PowerApps.
 */

// Base interfaces for common PowerApps patterns
export interface TimestampedEntity {
  created_on: string;
  modified_on: string;
}

export interface OwnedEntity extends TimestampedEntity {
  created_by: number;
  modified_by: number;
  owner: number;
  created_by_username?: string;
  modified_by_username?: string;
  owner_username?: string;
}

export interface StatusEntity {
  status: 'active' | 'inactive';
}

// Accounts Receivable types (migrated from cr7c4_accountsreceivables)
export interface AccountsReceivable extends OwnedEntity, StatusEntity {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  terms?: string;
  has_contact_info: boolean;
  powerapps_entity_name?: string;
}

// API Response types
export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  non_field_errors?: string[];
  [field: string]: string | string[] | undefined;
}

// Migration info response
export interface MigrationInfo {
  powerapps_entity_name: string;
  django_model_name: string;
  django_app_name: string;
  total_records: number;
  active_records: number;
  field_mappings: Record<string, string>;
  api_endpoints: Record<string, string>;
}

// Component props
export interface TableColumn<T> {
  key: keyof T;
  title: string;
  render?: (value: any, record: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

export interface FilterOptions {
  status?: 'active' | 'inactive';
  search?: string;
  has_contact?: boolean;
}

// Form data types
export interface AccountsReceivableFormData {
  name: string;
  email?: string;
  phone?: string;
  terms?: string;
  status: 'active' | 'inactive';
}