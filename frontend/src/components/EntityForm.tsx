/**
 * Reusable Entity Form Component
 * 
 * Provides a modal form with draft functionality for creating/editing entities.
 * Features:
 * - Real-time draft saving as fields are entered
 * - Create, Save Draft, and Close options
 * - Generic form field handling
 * - Modal overlay for clean UX
 */
import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';

// Styled Components
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  min-width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
`;

const FormHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 16px;
`;

const FormTitle = styled.h2`
  margin: 0;
  color: #333;
  font-size: 20px;
`;

const DraftStatus = styled.div<{ isDraft: boolean }>`
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  
  ${props => props.isDraft ? `
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
  ` : `
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  `}
`;

const FormRow = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #555;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-height: 80px;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
`;

const FormActions = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e5e5;
`;

const Button = styled.button<{ variant: 'primary' | 'secondary' | 'danger' }>`
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
  min-width: 80px;
  
  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background-color: #007bff;
          color: white;
          &:hover { background-color: #0056b3; }
          &:disabled { background-color: #6c757d; cursor: not-allowed; }
        `;
      case 'danger':
        return `
          background-color: #dc3545;
          color: white;
          &:hover { background-color: #c82333; }
        `;
      default:
        return `
          background-color: #f8f9fa;
          color: #333;
          border: 1px solid #dee2e6;
          &:hover { background-color: #e9ecef; }
        `;
    }
  }}
`;

// Form field interface
export interface FormField {
  key: string;
  label: string;
  type: 'text' | 'email' | 'tel' | 'textarea' | 'select' | 'checkbox' | 'date';
  required?: boolean;
  placeholder?: string;
  options?: { value: string | number; label: string }[];
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

  // Auto-save draft functionality
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

  // Auto-save draft after 2 seconds of inactivity
  useEffect(() => {
    if (hasChanges) {
      const timer = setTimeout(saveDraft, 2000);
      return () => clearTimeout(timer);
    }
  }, [hasChanges, saveDraft]);

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

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <FormHeader>
          <FormTitle>{title}</FormTitle>
          <DraftStatus isDraft={isDraft}>
            {isDraft ? '💾 Draft Saved' : hasChanges ? '✏️ Editing' : '✅ Ready'}
          </DraftStatus>
        </FormHeader>

        <form onSubmit={handleSubmit}>
          {fields.map(field => (
            <FormRow key={field.key}>
              <Label>
                {field.label}
                {field.required && <span style={{ color: '#dc3545' }}>*</span>}
              </Label>
              {renderField(field)}
            </FormRow>
          ))}

          <FormActions>
            <Button type="button" variant="secondary" onClick={onClose}>
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
              {isSubmitting ? 'Creating...' : 'Create'}
            </Button>
          </FormActions>
        </form>
      </ModalContent>
    </ModalOverlay>
  );
};

export default EntityForm;