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