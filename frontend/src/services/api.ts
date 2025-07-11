/**
 * API service for communicating with Django REST Framework backend.
 * 
 * Handles all HTTP requests to the ProjectMeats API endpoints
 * migrated from PowerApps/Dataverse.
 */
import axios, { AxiosResponse } from 'axios';
import {
  AccountsReceivable,
  AccountsReceivableFormData,
  Supplier,
  SupplierFormData,
  Customer,
  CustomerFormData,
  ContactInfo,
  ContactInfoFormData,
  PurchaseOrder,
  PurchaseOrderFormData,
  SupplierPlantMapping,
  SupplierPlantMappingFormData,
  CarrierInfo,
  CarrierInfoFormData,
  Plant,
  PlantFormData,
  SupplierLocation,
  SupplierLocationFormData,
  ApiResponse, 
  MigrationInfo,
  FilterOptions 
} from '../types';

// Configure axios instance
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging in development
if (process.env.NODE_ENV === 'development') {
  apiClient.interceptors.request.use(
    (config) => {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('🚨 API Request Error:', error);
      return Promise.reject(error);
    }
  );
}

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('🚨 API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Accounts Receivables API service
 * Migrated from PowerApps cr7c4_accountsreceivables entity
 */
export class AccountsReceivablesService {
  private static baseEndpoint = '/accounts-receivables';

  /**
   * Get paginated list of accounts receivables
   */
  static async getList(
    page: number = 1, 
    filters: FilterOptions = {}
  ): Promise<ApiResponse<AccountsReceivable>> {
    const params = new URLSearchParams({
      page: page.toString(),
    });

    // Add filters
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    if (filters.has_contact) params.append('has_contact', 'true');

    const response: AxiosResponse<ApiResponse<AccountsReceivable>> = await apiClient.get(
      `${this.baseEndpoint}/?${params.toString()}`
    );
    return response.data;
  }

  /**
   * Get detailed information for a specific accounts receivable
   */
  static async getDetail(id: number): Promise<AccountsReceivable> {
    const response: AxiosResponse<AccountsReceivable> = await apiClient.get(
      `${this.baseEndpoint}/${id}/`
    );
    return response.data;
  }

  /**
   * Create new accounts receivable record
   */
  static async create(data: AccountsReceivableFormData): Promise<AccountsReceivable> {
    const response: AxiosResponse<AccountsReceivable> = await apiClient.post(
      `${this.baseEndpoint}/`,
      data
    );
    return response.data;
  }

  /**
   * Update existing accounts receivable record
   */
  static async update(id: number, data: Partial<AccountsReceivableFormData>): Promise<AccountsReceivable> {
    const response: AxiosResponse<AccountsReceivable> = await apiClient.patch(
      `${this.baseEndpoint}/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Delete accounts receivable record (soft delete to inactive)
   */
  static async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseEndpoint}/${id}/`);
  }

  /**
   * Get PowerApps migration information for this entity
   */
  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response: AxiosResponse<MigrationInfo> = await apiClient.get(
      `${this.baseEndpoint}/migration_info/`
    );
    return response.data;
  }
}

/**
 * Suppliers API service
 * Migrated from PowerApps cr7c4_supplier entity
 */
export class SuppliersService {
  private static baseEndpoint = '/suppliers';

  static async getList(page: number = 1, filters: FilterOptions = {}): Promise<ApiResponse<Supplier>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response: AxiosResponse<ApiResponse<Supplier>> = await apiClient.get(
      `${this.baseEndpoint}/?${params.toString()}`
    );
    return response.data;
  }

  static async getDetail(id: number): Promise<Supplier> {
    const response: AxiosResponse<Supplier> = await apiClient.get(`${this.baseEndpoint}/${id}/`);
    return response.data;
  }

  static async create(data: SupplierFormData): Promise<Supplier> {
    const response: AxiosResponse<Supplier> = await apiClient.post(`${this.baseEndpoint}/`, data);
    return response.data;
  }

  static async update(id: number, data: Partial<SupplierFormData>): Promise<Supplier> {
    const response: AxiosResponse<Supplier> = await apiClient.patch(`${this.baseEndpoint}/${id}/`, data);
    return response.data;
  }

  static async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseEndpoint}/${id}/`);
  }

  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response: AxiosResponse<MigrationInfo> = await apiClient.get(`${this.baseEndpoint}/migration_info/`);
    return response.data;
  }
}

/**
 * Customers API service
 * Migrated from PowerApps pro_customer entity
 */
export class CustomersService {
  private static baseEndpoint = '/customers';

  static async getList(page: number = 1, filters: FilterOptions = {}): Promise<ApiResponse<Customer>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response: AxiosResponse<ApiResponse<Customer>> = await apiClient.get(
      `${this.baseEndpoint}/?${params.toString()}`
    );
    return response.data;
  }

  static async getDetail(id: number): Promise<Customer> {
    const response: AxiosResponse<Customer> = await apiClient.get(`${this.baseEndpoint}/${id}/`);
    return response.data;
  }

  static async create(data: CustomerFormData): Promise<Customer> {
    const response: AxiosResponse<Customer> = await apiClient.post(`${this.baseEndpoint}/`, data);
    return response.data;
  }

  static async update(id: number, data: Partial<CustomerFormData>): Promise<Customer> {
    const response: AxiosResponse<Customer> = await apiClient.patch(`${this.baseEndpoint}/${id}/`, data);
    return response.data;
  }

  static async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseEndpoint}/${id}/`);
  }

  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response: AxiosResponse<MigrationInfo> = await apiClient.get(`${this.baseEndpoint}/migration_info/`);
    return response.data;
  }
}

/**
 * Contact Information API service
 * Migrated from PowerApps pro_contactinfo entity
 */
export class ContactsService {
  private static baseEndpoint = '/contacts';

  static async getList(page: number = 1, filters: FilterOptions = {}): Promise<ApiResponse<ContactInfo>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response: AxiosResponse<ApiResponse<ContactInfo>> = await apiClient.get(
      `${this.baseEndpoint}/?${params.toString()}`
    );
    return response.data;
  }

  static async getDetail(id: number): Promise<ContactInfo> {
    const response: AxiosResponse<ContactInfo> = await apiClient.get(`${this.baseEndpoint}/${id}/`);
    return response.data;
  }

  static async create(data: ContactInfoFormData): Promise<ContactInfo> {
    const response: AxiosResponse<ContactInfo> = await apiClient.post(`${this.baseEndpoint}/`, data);
    return response.data;
  }

  static async update(id: number, data: Partial<ContactInfoFormData>): Promise<ContactInfo> {
    const response: AxiosResponse<ContactInfo> = await apiClient.patch(`${this.baseEndpoint}/${id}/`, data);
    return response.data;
  }

  static async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseEndpoint}/${id}/`);
  }

  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response: AxiosResponse<MigrationInfo> = await apiClient.get(`${this.baseEndpoint}/migration_info/`);
    return response.data;
  }
}

/**
 * Purchase Orders API service
 * Migrated from PowerApps pro_purchaseorder entity
 */
export class PurchaseOrdersService {
  private static baseEndpoint = '/purchase-orders';

  static async getList(page: number = 1, filters: FilterOptions = {}): Promise<ApiResponse<PurchaseOrder>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response: AxiosResponse<ApiResponse<PurchaseOrder>> = await apiClient.get(
      `${this.baseEndpoint}/?${params.toString()}`
    );
    return response.data;
  }

  static async getDetail(id: number): Promise<PurchaseOrder> {
    const response: AxiosResponse<PurchaseOrder> = await apiClient.get(`${this.baseEndpoint}/${id}/`);
    return response.data;
  }

  static async create(data: PurchaseOrderFormData): Promise<PurchaseOrder> {
    const response: AxiosResponse<PurchaseOrder> = await apiClient.post(`${this.baseEndpoint}/`, data);
    return response.data;
  }

  static async update(id: number, data: Partial<PurchaseOrderFormData>): Promise<PurchaseOrder> {
    const response: AxiosResponse<PurchaseOrder> = await apiClient.patch(`${this.baseEndpoint}/${id}/`, data);
    return response.data;
  }

  static async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseEndpoint}/${id}/`);
  }

  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response: AxiosResponse<MigrationInfo> = await apiClient.get(`${this.baseEndpoint}/migration_info/`);
    return response.data;
  }
}

/**
 * Supplier Plant Mappings API service
 * Migrated from PowerApps pro_supplierplantmapping entity
 */
export class SupplierPlantMappingsService {
  private static baseEndpoint = '/supplier-plant-mappings';

  static async getList(page: number = 1, filters: FilterOptions = {}): Promise<ApiResponse<SupplierPlantMapping>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response: AxiosResponse<ApiResponse<SupplierPlantMapping>> = await apiClient.get(
      `${this.baseEndpoint}/?${params.toString()}`
    );
    return response.data;
  }

  static async getDetail(id: number): Promise<SupplierPlantMapping> {
    const response: AxiosResponse<SupplierPlantMapping> = await apiClient.get(`${this.baseEndpoint}/${id}/`);
    return response.data;
  }

  static async create(data: SupplierPlantMappingFormData): Promise<SupplierPlantMapping> {
    const response: AxiosResponse<SupplierPlantMapping> = await apiClient.post(`${this.baseEndpoint}/`, data);
    return response.data;
  }

  static async update(id: number, data: Partial<SupplierPlantMappingFormData>): Promise<SupplierPlantMapping> {
    const response: AxiosResponse<SupplierPlantMapping> = await apiClient.patch(`${this.baseEndpoint}/${id}/`, data);
    return response.data;
  }

  static async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseEndpoint}/${id}/`);
  }

  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response: AxiosResponse<MigrationInfo> = await apiClient.get(`${this.baseEndpoint}/migration_info/`);
    return response.data;
  }
}

/**
 * Carrier Info API service
 * Migrated from PowerApps cr7c4_carrierinfo entity
 */
export class CarrierInfoService {
  private static baseEndpoint = '/carrier-infos';

  static async getList(page: number = 1, filters: FilterOptions = {}): Promise<ApiResponse<CarrierInfo>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response: AxiosResponse<ApiResponse<CarrierInfo>> = await apiClient.get(
      `${this.baseEndpoint}/?${params.toString()}`
    );
    return response.data;
  }

  static async getDetail(id: number): Promise<CarrierInfo> {
    const response: AxiosResponse<CarrierInfo> = await apiClient.get(`${this.baseEndpoint}/${id}/`);
    return response.data;
  }

  static async create(data: CarrierInfoFormData): Promise<CarrierInfo> {
    const response: AxiosResponse<CarrierInfo> = await apiClient.post(`${this.baseEndpoint}/`, data);
    return response.data;
  }

  static async update(id: number, data: Partial<CarrierInfoFormData>): Promise<CarrierInfo> {
    const response: AxiosResponse<CarrierInfo> = await apiClient.patch(`${this.baseEndpoint}/${id}/`, data);
    return response.data;
  }

  static async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseEndpoint}/${id}/`);
  }

  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response: AxiosResponse<MigrationInfo> = await apiClient.get(`${this.baseEndpoint}/migration_info/`);
    return response.data;
  }
}

/**
 * Plants API service
 * Migrated from PowerApps cr7c4_plant entity
 */
export class PlantsService {
  private static baseEndpoint = '/plants';

  static async getList(page: number = 1, filters: FilterOptions = {}): Promise<ApiResponse<Plant>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response: AxiosResponse<ApiResponse<Plant>> = await apiClient.get(
      `${this.baseEndpoint}/?${params.toString()}`
    );
    return response.data;
  }

  static async getDetail(id: number): Promise<Plant> {
    const response: AxiosResponse<Plant> = await apiClient.get(`${this.baseEndpoint}/${id}/`);
    return response.data;
  }

  static async create(data: PlantFormData): Promise<Plant> {
    const response: AxiosResponse<Plant> = await apiClient.post(`${this.baseEndpoint}/`, data);
    return response.data;
  }

  static async update(id: number, data: Partial<PlantFormData>): Promise<Plant> {
    const response: AxiosResponse<Plant> = await apiClient.patch(`${this.baseEndpoint}/${id}/`, data);
    return response.data;
  }

  static async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseEndpoint}/${id}/`);
  }

  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response: AxiosResponse<MigrationInfo> = await apiClient.get(`${this.baseEndpoint}/migration_info/`);
    return response.data;
  }
}

/**
 * Supplier Locations API service
 * Migrated from PowerApps pro_supplier_locations entity
 */
export class SupplierLocationsService {
  private static baseEndpoint = '/supplier-locations';

  static async getList(page: number = 1, filters: FilterOptions = {}): Promise<ApiResponse<SupplierLocation>> {
    const params = new URLSearchParams({ page: page.toString() });
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response: AxiosResponse<ApiResponse<SupplierLocation>> = await apiClient.get(
      `${this.baseEndpoint}/?${params.toString()}`
    );
    return response.data;
  }

  static async getDetail(id: number): Promise<SupplierLocation> {
    const response: AxiosResponse<SupplierLocation> = await apiClient.get(`${this.baseEndpoint}/${id}/`);
    return response.data;
  }

  static async create(data: SupplierLocationFormData): Promise<SupplierLocation> {
    const response: AxiosResponse<SupplierLocation> = await apiClient.post(`${this.baseEndpoint}/`, data);
    return response.data;
  }

  static async update(id: number, data: Partial<SupplierLocationFormData>): Promise<SupplierLocation> {
    const response: AxiosResponse<SupplierLocation> = await apiClient.patch(`${this.baseEndpoint}/${id}/`, data);
    return response.data;
  }

  static async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseEndpoint}/${id}/`);
  }

  static async getMigrationInfo(): Promise<MigrationInfo> {
    const response: AxiosResponse<MigrationInfo> = await apiClient.get(`${this.baseEndpoint}/migration_info/`);
    return response.data;
  }
}

/**
 * Generic API service utilities
 */
export class ApiService {
  /**
   * Health check endpoint
   */
  static async healthCheck(): Promise<{ status: string }> {
    try {
      const response = await apiClient.get('/health/');
      return response.data;
    } catch (error) {
      return { status: 'error' };
    }
  }

  /**
   * Get API schema/documentation
   */
  static async getApiSchema(): Promise<any> {
    const response = await apiClient.get('/schema/');
    return response.data;
  }
}

// Export configured axios instance for custom requests
export { apiClient };
export default apiClient;