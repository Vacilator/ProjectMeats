/**
 * Chat Interface Components
 * 
 * Exports all AI assistant chat interface components for easy importing.
 */

export { default as ChatWindow } from './ChatWindow';
export { default as MessageList } from './MessageList';
export { default as MessageInput } from './MessageInput';
export { default as DocumentUpload } from './DocumentUpload';
export { default as SessionsList } from './SessionsList';

// Re-export types for convenience
export type {
  ChatSession,
  ChatMessage,
  UploadedDocument,
  ChatRequest,
  ChatResponse,
  DocumentProcessingRequest,
  DocumentProcessingResponse
} from '../../types';