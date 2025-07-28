/**
 * AI Assistant API Service
 * 
 * Handles communication with the AI Assistant backend endpoints
 * for chat functionality, document processing, and AI operations.
 */
import {
  ChatSession,
  ChatMessage,
  UploadedDocument,
  AIConfiguration,
  ProcessingTask,
  ChatRequest,
  ChatResponse,
  DocumentProcessingRequest,
  DocumentProcessingResponse,
  DocumentUploadFormData,
  ApiResponse,
  ChatSessionFormData
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Generic fetch wrapper with error handling
 */
async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const config: RequestInit = {
    ...options,
    headers: defaultHeaders,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    } else {
      return {} as T;
    }
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Upload file with multipart form data
 */
async function uploadFile<T>(
  endpoint: string,
  file: File,
  additionalData: Record<string, any> = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const formData = new FormData();
  formData.append('file', file);
  
  // Add additional form fields
  Object.entries(additionalData).forEach(([key, value]) => {
    formData.append(key, value);
  });

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`File upload failed for ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Chat Sessions API
 */
export const chatSessionsApi = {
  /**
   * List all chat sessions for the current user
   */
  list: async (params?: {
    page?: number;
    search?: string;
    session_status?: string;
    status?: string;
  }): Promise<ApiResponse<ChatSession>> => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.search) searchParams.append('search', params.search);
    if (params?.session_status) searchParams.append('session_status', params.session_status);
    if (params?.status) searchParams.append('status', params.status);
    
    const endpoint = `/ai-assistant/sessions/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    return apiRequest<ApiResponse<ChatSession>>(endpoint);
  },

  /**
   * Get a specific chat session
   */
  get: async (id: string): Promise<ChatSession> => {
    return apiRequest<ChatSession>(`/ai-assistant/sessions/${id}/`);
  },

  /**
   * Create a new chat session
   */
  create: async (data: ChatSessionFormData): Promise<ChatSession> => {
    return apiRequest<ChatSession>('/ai-assistant/sessions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update a chat session
   */
  update: async (id: string, data: Partial<ChatSessionFormData>): Promise<ChatSession> => {
    return apiRequest<ChatSession>(`/ai-assistant/sessions/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a chat session
   */
  delete: async (id: string): Promise<void> => {
    return apiRequest<void>(`/ai-assistant/sessions/${id}/`, {
      method: 'DELETE',
    });
  },

  /**
   * Get messages for a specific session
   */
  getMessages: async (id: string, page?: number): Promise<ApiResponse<ChatMessage>> => {
    const params = page ? `?page=${page}` : '';
    return apiRequest<ApiResponse<ChatMessage>>(`/ai-assistant/sessions/${id}/messages/${params}`);
  },

  /**
   * Start a new session with an initial message
   */
  startSession: async (data: {
    message: string;
    title?: string;
  }): Promise<{
    session: ChatSession;
    user_message: ChatMessage;
    ai_response: ChatMessage;
  }> => {
    return apiRequest('/ai-assistant/sessions/start_session/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

/**
 * Chat Messages API
 */
export const chatMessagesApi = {
  /**
   * List messages (filtered by user's sessions)
   */
  list: async (params?: {
    page?: number;
    session?: string;
    message_type?: string;
  }): Promise<ApiResponse<ChatMessage>> => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.session) searchParams.append('session', params.session);
    if (params?.message_type) searchParams.append('message_type', params.message_type);
    
    const endpoint = `/ai-assistant/messages/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    return apiRequest<ApiResponse<ChatMessage>>(endpoint);
  },

  /**
   * Create a new message (will trigger AI response for user messages)
   */
  create: async (data: {
    session: string;
    message_type: 'user' | 'system';
    content: string;
    metadata?: Record<string, any>;
  }): Promise<ChatMessage> => {
    return apiRequest<ChatMessage>('/ai-assistant/messages/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get a specific message
   */
  get: async (id: string): Promise<ChatMessage> => {
    return apiRequest<ChatMessage>(`/ai-assistant/messages/${id}/`);
  },
};

/**
 * Document Upload and Processing API
 */
export const documentsApi = {
  /**
   * List uploaded documents
   */
  list: async (params?: {
    page?: number;
    search?: string;
    document_type?: string;
    processing_status?: string;
  }): Promise<ApiResponse<UploadedDocument>> => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.search) searchParams.append('search', params.search);
    if (params?.document_type) searchParams.append('document_type', params.document_type);
    if (params?.processing_status) searchParams.append('processing_status', params.processing_status);
    
    const endpoint = `/ai-assistant/documents/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    return apiRequest<ApiResponse<UploadedDocument>>(endpoint);
  },

  /**
   * Upload a new document
   */
  upload: async (data: DocumentUploadFormData): Promise<UploadedDocument> => {
    return uploadFile<UploadedDocument>('/ai-assistant/documents/', data.file, {
      original_filename: data.original_filename || data.file.name,
    });
  },

  /**
   * Get a specific document
   */
  get: async (id: string): Promise<UploadedDocument> => {
    return apiRequest<UploadedDocument>(`/ai-assistant/documents/${id}/`);
  },

  /**
   * Reprocess a document
   */
  reprocess: async (id: string): Promise<UploadedDocument> => {
    return apiRequest<UploadedDocument>(`/ai-assistant/documents/${id}/reprocess/`, {
      method: 'POST',
    });
  },

  /**
   * Create entities from processed document
   */
  createEntities: async (id: string): Promise<{
    message: string;
    created_entities: Array<{type: string; id: number; name?: string}>;
  }> => {
    return apiRequest(`/ai-assistant/documents/${id}/create_entities/`, {
      method: 'POST',
    });
  },
};

/**
 * Simplified Chat API (recommended for frontend)
 */
export const chatApi = {
  /**
   * Send a message and get AI response
   */
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    return apiRequest<ChatResponse>('/ai-assistant/chat/chat/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Process a document with AI
   */
  processDocument: async (data: DocumentProcessingRequest): Promise<DocumentProcessingResponse> => {
    return apiRequest<DocumentProcessingResponse>('/ai-assistant/chat/process_document/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

/**
 * Processing Tasks API
 */
export const processingTasksApi = {
  /**
   * List processing tasks for current user
   */
  list: async (params?: {
    page?: number;
    task_type?: string;
    status?: string;
  }): Promise<ApiResponse<ProcessingTask>> => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.task_type) searchParams.append('task_type', params.task_type);
    if (params?.status) searchParams.append('status', params.status);
    
    const endpoint = `/ai-assistant/tasks/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    return apiRequest<ApiResponse<ProcessingTask>>(endpoint);
  },

  /**
   * Get a specific processing task
   */
  get: async (id: string): Promise<ProcessingTask> => {
    return apiRequest<ProcessingTask>(`/ai-assistant/tasks/${id}/`);
  },
};

/**
 * AI Configurations API (admin only)
 */
export const aiConfigurationsApi = {
  /**
   * List available AI configurations
   */
  list: async (): Promise<ApiResponse<AIConfiguration>> => {
    return apiRequest<ApiResponse<AIConfiguration>>('/ai-assistant/configurations/');
  },

  /**
   * Get a specific AI configuration
   */
  get: async (id: number): Promise<AIConfiguration> => {
    return apiRequest<AIConfiguration>(`/ai-assistant/configurations/${id}/`);
  },
};

/**
 * Utility functions
 */
export const aiUtils = {
  /**
   * Format file size for display
   */
  formatFileSize: (bytes: number): string => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  },

  /**
   * Get document type display name
   */
  getDocumentTypeDisplay: (type: string): string => {
    const types: Record<string, string> = {
      'purchase_order': 'Purchase Order',
      'invoice': 'Invoice',
      'supplier_document': 'Supplier Document',
      'customer_document': 'Customer Document',
      'contract': 'Contract',
      'receipt': 'Receipt',
      'unknown': 'Unknown',
    };
    return types[type] || type;
  },

  /**
   * Get processing status display name and color
   */
  getProcessingStatusDisplay: (status: string): {name: string; color: string} => {
    const statuses: Record<string, {name: string; color: string}> = {
      'pending': {name: 'Pending', color: '#ffa500'},
      'processing': {name: 'Processing', color: '#0066cc'},
      'completed': {name: 'Completed', color: '#28a745'},
      'failed': {name: 'Failed', color: '#dc3545'},
      'manual_review': {name: 'Manual Review', color: '#6f42c1'},
    };
    return statuses[status] || {name: status, color: '#6c757d'};
  },

  /**
   * Get message type icon
   */
  getMessageTypeIcon: (type: string): string => {
    const icons: Record<string, string> = {
      'user': '👤',
      'assistant': '🤖',
      'system': '⚙️',
      'document': '📄',
    };
    return icons[type] || '💬';
  },

  /**
   * Format relative time
   */
  formatRelativeTime: (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  },
};