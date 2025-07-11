/**
 * Enhanced Reusable Entity Form Component
 * 
 * Professional modal form with modern design system integration.
 * Features:
 * - Real-time draft saving as fields are entered
 * - Create, Save Draft, and Close options
 * - Generic form field handling with validation
 * - Modern modal overlay with accessibility
 * - Responsive design for mobile and desktop
 */
import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { 
  Button, 
  Input, 
  Label, 
  Card,
  Heading,
  Flex,
  colors,
  spacing,
  borderRadius,
  typography
} from './DesignSystem';

// Enhanced Styled Components
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease-out;
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
`;

const ModalContent = styled(Card)`
  min-width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-20px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }
  
  @media (max-width: 768px) {
    min-width: 90vw;
    margin: ${spacing.md};
  }
`;

const FormHeader = styled(Flex)`
  border-bottom: 1px solid ${colors.neutral[200]};
  padding-bottom: ${spacing.md};
  margin-bottom: ${spacing.lg};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  color: ${colors.text.muted};
  cursor: pointer;
  padding: ${spacing.xs};
  border-radius: ${borderRadius.sm};
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${colors.neutral[100]};
    color: ${colors.text.primary};
  }
`;

const DraftStatus = styled.div<{ isDraft: boolean }>`
  padding: ${spacing.xs} ${spacing.sm};
  border-radius: ${borderRadius.sm};
  font-size: ${typography.fontSize.xs};
  font-weight: ${typography.fontWeight.medium};
  
  ${props => props.isDraft ? `
    background-color: ${colors.warning}20;
    color: ${colors.warning};
    border: 1px solid ${colors.warning}40;
  ` : `
    background-color: ${colors.success}20;
    color: ${colors.success};
    border: 1px solid ${colors.success}40;
  `}
`;

const FormRow = styled.div`
  margin-bottom: ${spacing.md};
`;

const Select = styled.select`
  width: 100%;
  padding: ${spacing.sm} ${spacing.md};
  border: 1px solid ${colors.neutral[300]};
  border-radius: ${borderRadius.md};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.base};
  background: ${colors.background};
  transition: border-color 0.2s ease-in-out;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary[500]};
    box-shadow: 0 0 0 3px ${colors.primary[200]};
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: ${spacing.sm} ${spacing.md};
  border: 1px solid ${colors.neutral[300]};
  border-radius: ${borderRadius.md};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.base};
  min-height: 80px;
  resize: vertical;
  transition: border-color 0.2s ease-in-out;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary[500]};
    box-shadow: 0 0 0 3px ${colors.primary[200]};
  }
  
  &::placeholder {
    color: ${colors.text.muted};
  }
`;

const FileInput = styled.input`
  width: 100%;
  padding: ${spacing.sm} ${spacing.md};
  border: 1px solid ${colors.neutral[300]};
  border-radius: ${borderRadius.md};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.base};
  background: ${colors.background};
  transition: border-color 0.2s ease-in-out;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary[500]};
    box-shadow: 0 0 0 3px ${colors.primary[200]};
  }
  
  &::file-selector-button {
    background-color: ${colors.primary[600]};
    color: ${colors.text.inverse};
    border: none;
    padding: ${spacing.xs} ${spacing.sm};
    border-radius: ${borderRadius.sm};
    margin-right: ${spacing.sm};
    cursor: pointer;
    font-size: ${typography.fontSize.sm};
    transition: background-color 0.2s ease;
    
    &:hover {
      background-color: ${colors.primary[700]};
    }
  }
`;

const FormActions = styled(Flex)`
  margin-top: ${spacing.xl};
  padding-top: ${spacing.md};
  border-top: 1px solid ${colors.neutral[200]};
  justify-content: flex-end;
  gap: ${spacing.md};
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

// Form field interface
export interface FormField {
  key: string;
  label: string;
  type: 'text' | 'email' | 'tel' | 'textarea' | 'select' | 'checkbox' | 'date' | 'file';
  required?: boolean;
  placeholder?: string;
  options?: { value: string | number; label: string }[];
  accept?: string; // For file inputs
  multiple?: boolean; // For multiple file uploads
}

// Props interface
interface EntityFormProps {
  title: string;
  fields: FormField[];
  initialData?: Record<string, any>;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Record<string, any>) => Promise<void>;
  onSaveDraft?: (data: Record<string, any>) => Promise<void>;
  isSubmitting?: boolean;
}

const EntityForm: React.FC<EntityFormProps> = ({
  title,
  fields,
  initialData = {},
  isOpen,
  onClose,
  onSubmit,
  onSaveDraft,
  isSubmitting = false
}) => {
  const [formData, setFormData] = useState<Record<string, any>>(initialData);
  const [isDraft, setIsDraft] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Manual save draft functionality (auto-save removed to prevent typing interference)
  const saveDraft = useCallback(async () => {
    if (onSaveDraft && hasChanges) {
      try {
        await onSaveDraft(formData);
        setIsDraft(true);
        setHasChanges(false);
      } catch (error) {
        console.error('Error saving draft:', error);
      }
    }
  }, [formData, hasChanges, onSaveDraft]);

  // Reset form when opened/closed
  useEffect(() => {
    if (isOpen) {
      setFormData(initialData);
      setIsDraft(false);
      setHasChanges(false);
    }
  }, [isOpen, initialData]);

  const handleFieldChange = (key: string, value: any) => {
    setFormData(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
    setIsDraft(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  const handleSaveDraft = async () => {
    await saveDraft();
  };

  const renderField = (field: FormField) => {
    const value = formData[field.key] || '';

    switch (field.type) {
      case 'textarea':
        return (
          <TextArea
            value={value}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
          />
        );

      case 'select':
        return (
          <Select
            value={value}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            required={field.required}
          >
            <option value="">Select {field.label}</option>
            {field.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        );

      case 'checkbox':
        return (
          <Input
            type="checkbox"
            checked={value}
            onChange={(e) => handleFieldChange(field.key, e.target.checked)}
            style={{ width: 'auto', marginRight: '8px' }}
          />
        );

      case 'file':
        return (
          <FileInput
            type="file"
            onChange={(e) => {
              const files = e.target.files;
              if (field.multiple) {
                handleFieldChange(field.key, files);
              } else {
                handleFieldChange(field.key, files?.[0] || null);
              }
            }}
            accept={field.accept}
            multiple={field.multiple}
            required={field.required}
          />
        );

      default:
        return (
          <Input
            type={field.type}
            value={value}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
          />
        );
    }
  };

  if (!isOpen) return null;

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  return (
    <ModalOverlay 
      role="dialog" 
      aria-modal="true" 
      onClick={onClose}
    >
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <FormHeader justify="between" align="center">
          <div>
            <Heading level={2}>{title}</Heading>
            <DraftStatus isDraft={isDraft}>
              {isDraft ? '💾 Draft Saved' : hasChanges ? '✏️ Editing' : '✅ Ready'}
            </DraftStatus>
          </div>
          <CloseButton onClick={onClose} aria-label="Close form">
            ×
          </CloseButton>
        </FormHeader>

        <form onSubmit={handleSubmit}>
          {fields.map(field => (
            <FormRow key={field.key}>
              <Label required={field.required}>
                {field.label}
              </Label>
              {renderField(field)}
            </FormRow>
          ))}

          <FormActions>
            <Button type="button" variant="outline" onClick={onClose}>
              Close
            </Button>
            {onSaveDraft && (
              <Button
                type="button"
                variant="secondary"
                onClick={handleSaveDraft}
                disabled={!hasChanges}
              >
                Save Draft
              </Button>
            )}
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save'}
            </Button>
          </FormActions>
        </form>
      </ModalContent>
    </ModalOverlay>
  );
};

export default EntityForm;