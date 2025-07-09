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

// Supplier types (migrated from cr7c4_supplier)
export interface Supplier extends OwnedEntity, StatusEntity {
  id: number;
  name: string;
  credit_application_date?: string;
  delivery_type_profile: boolean;
  accounts_receivable?: number;
  accounts_receivable_name?: string;
  has_credit_application: boolean;
  has_accounts_receivable: boolean;
  powerapps_entity_name?: string;
}

// Customer types (migrated from pro_customer)
export interface Customer extends OwnedEntity, StatusEntity {
  id: number;
  name: string;
  powerapps_entity_name?: string;
}

// ContactInfo types (migrated from pro_contactinfo)
export interface ContactInfo extends OwnedEntity, StatusEntity {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  position?: string;
  contact_type?: string;
  customer?: number;
  customer_name?: string;
  supplier?: number;
  supplier_name?: string;
  has_contact_details: boolean;
  has_relationships: boolean;
  powerapps_entity_name?: string;
}

// Purchase Order types (migrated from pro_purchaseorder)
export interface PurchaseOrder extends OwnedEntity, StatusEntity {
  id: number;
  po_number: string;
  item: string;
  quantity: number;
  price_per_unit: string;
  total_amount: string;
  purchase_date: string;
  fulfillment_date?: string;
  customer: number;
  customer_name?: string;
  supplier: number;
  supplier_name?: string;
  customer_documents?: string;
  supplier_documents?: string;
  is_fulfilled: boolean;
  has_documents: boolean;
  powerapps_entity_name?: string;
}

// Supplier Plant Mapping types (migrated from pro_supplierplantmapping)
export interface SupplierPlantMapping extends OwnedEntity, StatusEntity {
  id: number;
  name: string;
  supplier: number;
  supplier_name?: string;
  customer: number;
  customer_name?: string;
  contact_info?: number;
  contact_info_name?: string;
  documents_reference?: string;
  has_contact_info: boolean;
  has_documents: boolean;
  powerapps_entity_name?: string;
}

// Carrier Info types (migrated from cr7c4_carrierinfo)
export interface CarrierInfo extends OwnedEntity, StatusEntity {
  id: number;
  name: string;
  address?: string;
  contact_name?: string;
  release_number?: string;
  supplier?: number;
  supplier_name?: string;
  has_contact_info: boolean;
  has_address: boolean;
  has_supplier: boolean;
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

export interface SupplierFormData {
  name: string;
  credit_application_date?: string;
  delivery_type_profile: boolean;
  accounts_receivable?: number;
  status: 'active' | 'inactive';
}

export interface CustomerFormData {
  name: string;
  status: 'active' | 'inactive';
}

export interface ContactInfoFormData {
  name: string;
  email?: string;
  phone?: string;
  position?: string;
  contact_type?: string;
  customer?: number;
  supplier?: number;
  status: 'active' | 'inactive';
}

export interface PurchaseOrderFormData {
  po_number: string;
  item: string;
  quantity: number;
  price_per_unit: string;
  purchase_date: string;
  fulfillment_date?: string;
  customer: number;
  supplier: number;
  customer_documents?: string;
  supplier_documents?: string;
  status: 'active' | 'inactive';
}

export interface SupplierPlantMappingFormData {
  name: string;
  supplier: number;
  customer: number;
  contact_info?: number;
  documents_reference?: string;
  status: 'active' | 'inactive';
}

export interface CarrierInfoFormData {
  name: string;
  address?: string;
  contact_name?: string;
  release_number?: string;
  supplier?: number;
  status: 'active' | 'inactive';
}