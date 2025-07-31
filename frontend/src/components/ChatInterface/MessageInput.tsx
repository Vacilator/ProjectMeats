/**
 * MessageInput Component
 * 
 * Enhanced input field for typing and sending messages to the AI assistant.
 * Includes integrated file upload, auto-resize, keyboard shortcuts, and suggested prompts.
 * Designed similar to Microsoft Copilot interface.
 */
import React, { useState, useRef, useEffect, KeyboardEvent, useCallback } from 'react';
import styled from 'styled-components';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  onFileUpload?: (file: File) => Promise<any>;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

// Supported file types for upload
const SUPPORTED_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/jpg', 
  'image/png',
  'text/plain',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
];

const SUPPORTED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'txt', 'doc', 'docx', 'xls', 'xlsx'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  onFileUpload,
  disabled = false,
  placeholder = "Type your message...",
  className
}) => {
  const [message, setMessage] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Suggested prompts for meat market operations
  const suggestedPrompts = [
    "Help me process a purchase order",
    "How do I manage supplier information?",
    "What are the current market trends?",
    "Analyze my recent invoices",
    "Create a new customer record",
    "Track delivery schedules",
  ];

  // Validate file
  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return `File size too large. Maximum size is ${(MAX_FILE_SIZE / (1024 * 1024)).toFixed(1)}MB.`;
    }

    // Check file type
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    if (!fileExtension || !SUPPORTED_EXTENSIONS.includes(fileExtension)) {
      return `File type not supported. Supported types: ${SUPPORTED_EXTENSIONS.join(', ')}`;
    }

    return null;
  }, []);

  // Handle file upload
  const handleFileUpload = useCallback(async (file: File) => {
    setError(null);
    
    // Validate file
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    if (!onFileUpload) {
      setError('File upload not available');
      return;
    }

    try {
      setUploading(true);
      await onFileUpload(file);
      
      // Add a message about the uploaded file
      const fileMessage = `📄 I've uploaded "${file.name}" for processing.`;
      setMessage(fileMessage);
      textareaRef.current?.focus();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [onFileUpload, validateFile]);

  // Handle drag events
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled && !uploading) {
      setIsDragOver(true);
    }
  }, [disabled, uploading]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    // Only set dragOver to false if we're leaving the main container
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragOver(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    if (disabled || uploading) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, [disabled, uploading, handleFileUpload]);

  // Handle file input change
  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0] as File);
    }
    // Reset input value to allow same file upload
    e.target.value = '';
  }, [handleFileUpload]);

  // Handle attachment button click
  const handleAttachmentClick = useCallback(() => {
    if (!disabled && !uploading) {
      fileInputRef.current?.click();
    }
  }, [disabled, uploading]);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  // Handle form submission
  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    
    if (message.trim() && !disabled && !uploading) {
      onSendMessage(message.trim());
      setMessage('');
      setShowSuggestions(false);
      setError(null);
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    setError(null); // Clear error when user starts typing
    
    // Show suggestions if input is empty and user starts typing
    if (e.target.value === '' && !showSuggestions) {
      setShowSuggestions(true);
    } else if (e.target.value !== '' && showSuggestions) {
      setShowSuggestions(false);
    }
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: string) => {
    setMessage(suggestion);
    setShowSuggestions(false);
    textareaRef.current?.focus();
  };

  // Focus input on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  return (
    <InputContainer 
      className={className}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      isDragOver={isDragOver}
    >
      {/* Hidden file input */}
      <HiddenFileInput
        ref={fileInputRef}
        type="file"
        accept={SUPPORTED_EXTENSIONS.map(ext => `.${ext}`).join(',')}
        onChange={handleFileInputChange}
        disabled={disabled || uploading}
      />

      {/* Error display */}
      {error && (
        <ErrorBanner>
          <ErrorIcon>⚠️</ErrorIcon>
          <ErrorText>{error}</ErrorText>
          <ErrorClose onClick={() => setError(null)}>×</ErrorClose>
        </ErrorBanner>
      )}

      {/* Drag overlay */}
      {isDragOver && (
        <DragOverlay>
          <DragIcon>📄</DragIcon>
          <DragText>Drop your document here</DragText>
        </DragOverlay>
      )}

      {/* Suggested prompts */}
      {showSuggestions && (
        <SuggestionsContainer>
          <SuggestionsTitle>💡 Suggested prompts:</SuggestionsTitle>
          <SuggestionsList>
            {suggestedPrompts.map((prompt, index) => (
              <SuggestionItem
                key={index}
                onClick={() => handleSuggestionClick(prompt)}
              >
                {prompt}
              </SuggestionItem>
            ))}
          </SuggestionsList>
        </SuggestionsContainer>
      )}

      {/* Main input form */}
      <InputForm onSubmit={handleSubmit}>
        <InputWrapper isDragOver={isDragOver}>
          <AttachmentButton
            type="button"
            onClick={handleAttachmentClick}
            disabled={disabled || uploading}
            title="Upload a document"
          >
            {uploading ? (
              <LoadingSpinner />
            ) : (
              <AttachmentIcon>📎</AttachmentIcon>
            )}
          </AttachmentButton>
          
          <TextArea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || uploading}
            rows={1}
            maxLength={5000}
          />
          
          <InputActions>
            <CharacterCount isNearLimit={message.length > 4500}>
              {message.length}/5000
            </CharacterCount>
            
            <SendButton
              type="submit"
              disabled={!message.trim() || disabled || uploading}
              title="Send message (Enter)"
            >
              {disabled || uploading ? (
                <LoadingSpinner />
              ) : (
                <SendIcon>🚀</SendIcon>
              )}
            </SendButton>
          </InputActions>
        </InputWrapper>
        
        <InputHint>
          Press <Kbd>Enter</Kbd> to send, <Kbd>Shift + Enter</Kbd> for new line • Drag & drop files to upload
        </InputHint>
      </InputForm>
    </InputContainer>
  );
};

// Styled Components
const InputContainer = styled.div<{isDragOver?: boolean}>`
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  ${props => props.isDragOver && `
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border-radius: 12px;
  `}
`;

const HiddenFileInput = styled.input`
  display: none;
`;

const ErrorBanner = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 12px;
  animation: slideDown 0.2s ease-out;
  
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const ErrorIcon = styled.span`
  font-size: 14px;
`;

const ErrorText = styled.span`
  flex: 1;
`;

const ErrorClose = styled.button`
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  
  &:hover {
    opacity: 0.7;
  }
`;

const DragOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 10;
  animation: fadeIn 0.2s ease-out;
  
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
`;

const DragIcon = styled.div`
  font-size: 48px;
  margin-bottom: 8px;
`;

const DragText = styled.div`
  font-size: 18px;
  font-weight: 600;
`;

const SuggestionsContainer = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.2s ease-out;
  
  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const SuggestionsTitle = styled.div`
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 8px;
`;

const SuggestionsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
`;

const SuggestionItem = styled.button`
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 12px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e5e7eb;
    border-color: #d1d5db;
    transform: translateY(-1px);
  }
  
  &:active {
    transform: scale(0.98);
  }
`;

const InputForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const InputWrapper = styled.div<{isDragOver?: boolean}>`
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 2px solid ${props => props.isDragOver ? '#667eea' : '#e5e7eb'};
  border-radius: 12px;
  transition: all 0.2s ease;
  position: relative;
  
  &:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  ${props => props.isDragOver && `
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  `}
`;

const AttachmentButton = styled.button`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
  
  &:hover:not(:disabled) {
    background: #e5e7eb;
    color: #374151;
    transform: translateY(-1px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0) scale(0.95);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const AttachmentIcon = styled.span`
  font-size: 16px;
`;

const TextArea = styled.textarea`
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  color: #1f2937;
  background: transparent;
  min-height: 20px;
  max-height: 120px;
  
  &::placeholder {
    color: #9ca3af;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const InputActions = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
`;

const CharacterCount = styled.div<{isNearLimit: boolean}>`
  font-size: 10px;
  color: ${props => props.isNearLimit ? '#dc2626' : '#9ca3af'};
  font-weight: ${props => props.isNearLimit ? '600' : '400'};
`;

const SendButton = styled.button`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const SendIcon = styled.span`
  font-size: 16px;
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const InputHint = styled.div`
  font-size: 11px;
  color: #9ca3af;
  text-align: center;
  padding: 0 12px;
`;

const Kbd = styled.kbd`
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 1px 4px;
  font-size: 10px;
  font-family: monospace;
`;

export default MessageInput;