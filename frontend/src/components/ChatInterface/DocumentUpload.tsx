/**
 * DocumentUpload Component
 * 
 * Drag-and-drop file upload interface for processing business documents
 * with the AI assistant. Supports various file formats and provides
 * upload progress and validation feedback.
 */
import React, { useState, useRef, useCallback } from 'react';
import styled from 'styled-components';
import { UploadedDocument } from '../../types';
import { aiUtils } from '../../services/aiService';

// Supported file types - defined outside component to avoid dependencies
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

interface DocumentUploadProps {
  onFileUpload: (file: File) => Promise<UploadedDocument>;
  disabled?: boolean;
  className?: string;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onFileUpload,
  disabled = false,
  className
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Validate file
  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return `File size too large. Maximum size is ${aiUtils.formatFileSize(MAX_FILE_SIZE)}.`;
    }

    // Check file type
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    if (!fileExtension || !SUPPORTED_EXTENSIONS.includes(fileExtension)) {
      return `File type not supported. Supported types: ${SUPPORTED_EXTENSIONS.join(', ')}`;
    }

    // Check MIME type if available
    if (file.type && !SUPPORTED_TYPES.includes(file.type)) {
      return `File format not supported. Please upload a document or image file.`;
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

    try {
      setUploading(true);
      setUploadProgress(0);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      await onFileUpload(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Reset after success
      setTimeout(() => {
        setUploading(false);
        setUploadProgress(0);
      }, 1000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setUploading(false);
      setUploadProgress(0);
    }
  }, [onFileUpload, validateFile]);

  // Handle drag events
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
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
      handleFileUpload(files[0]);
    }
    // Reset input value to allow same file upload
    e.target.value = '';
  }, [handleFileUpload]);

  // Handle click to browse
  const handleBrowseClick = useCallback(() => {
    if (!disabled && !uploading) {
      fileInputRef.current?.click();
    }
  }, [disabled, uploading]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return (
    <UploadContainer className={className}>
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
          <ErrorClose onClick={clearError}>×</ErrorClose>
        </ErrorBanner>
      )}

      {/* Upload area */}
      <UploadArea
        isDragOver={isDragOver}
        isUploading={uploading}
        isDisabled={disabled}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleBrowseClick}
      >
        {uploading ? (
          <UploadingContent>
            <UploadIcon>📤</UploadIcon>
            <UploadText>Uploading document...</UploadText>
            <ProgressBar>
              <ProgressFill progress={uploadProgress} />
            </ProgressBar>
            <ProgressText>{uploadProgress}%</ProgressText>
          </UploadingContent>
        ) : (
          <UploadContent>
            <UploadIcon>
              {isDragOver ? '📥' : '📄'}
            </UploadIcon>
            <UploadText>
              {isDragOver 
                ? 'Drop your document here' 
                : 'Drag & drop a document or click to browse'
              }
            </UploadText>
            <UploadSubtext>
              Supports: PDF, Images (JPG, PNG), Word, Excel, Text files
            </UploadSubtext>
            <UploadSubtext>
              Maximum file size: {aiUtils.formatFileSize(MAX_FILE_SIZE)}
            </UploadSubtext>
          </UploadContent>
        )}
      </UploadArea>

      {/* Supported formats info */}
      <SupportedFormats>
        <FormatTitle>📋 Document types I can process:</FormatTitle>
        <FormatList>
          <FormatItem>📋 Purchase Orders</FormatItem>
          <FormatItem>🧾 Invoices</FormatItem>
          <FormatItem>📄 Contracts</FormatItem>
          <FormatItem>🏢 Supplier Documents</FormatItem>
          <FormatItem>👥 Customer Documents</FormatItem>
          <FormatItem>🧾 Receipts</FormatItem>
        </FormatList>
      </SupportedFormats>
    </UploadContainer>
  );
};

// Styled Components
const UploadContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
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

const UploadArea = styled.div<{
  isDragOver: boolean;
  isUploading: boolean;
  isDisabled: boolean;
}>`
  border: 2px dashed ${props => 
    props.isDragOver ? '#667eea' :
    props.isUploading ? '#10b981' : '#d1d5db'
  };
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: ${props => 
    props.isDisabled || props.isUploading ? 'not-allowed' : 'pointer'
  };
  background: ${props => 
    props.isDragOver ? '#f0f4ff' :
    props.isUploading ? '#f0fdf4' : '#fafafa'
  };
  transition: all 0.2s ease;
  opacity: ${props => props.isDisabled ? 0.5 : 1};
  
  &:hover:not(:disabled) {
    border-color: ${props => 
      props.isUploading ? '#10b981' : '#9ca3af'
    };
    background: ${props => 
      props.isUploading ? '#f0fdf4' : '#f5f5f5'
    };
  }
`;

const UploadContent = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
`;

const UploadingContent = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
`;

const UploadIcon = styled.div`
  font-size: 32px;
  margin-bottom: 4px;
`;

const UploadText = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: #374151;
`;

const UploadSubtext = styled.div`
  font-size: 12px;
  color: #6b7280;
`;

const ProgressBar = styled.div`
  width: 200px;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  margin: 8px 0 4px 0;
`;

const ProgressFill = styled.div<{progress: number}>`
  width: ${props => props.progress}%;
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  transition: width 0.3s ease;
`;

const ProgressText = styled.div`
  font-size: 12px;
  color: #059669;
  font-weight: 600;
`;

const SupportedFormats = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
`;

const FormatTitle = styled.div`
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
`;

const FormatList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 4px;
`;

const FormatItem = styled.div`
  font-size: 11px;
  color: #64748b;
  padding: 2px 4px;
`;

export default DocumentUpload;