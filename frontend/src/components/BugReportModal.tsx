/**
 * Bug Report Modal Component
 * 
 * Provides a user-friendly interface for reporting bugs that automatically
 * creates GitHub issues assigned to copilot agents.
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, typography, spacing, borderRadius, shadows } from './DesignSystem';
import { BugReportFormData } from '../types';
import { BugReportsService } from '../services/api';

interface BugReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (bugReport: any) => void;
}

const BugReportModal: React.FC<BugReportModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState<BugReportFormData>({
    title: '',
    description: '',
    steps_to_reproduce: '',
    expected_behavior: '',
    actual_behavior: '',
    priority: 'medium',
    current_url: '',
    page_title: '',
    browser_info: {},
    user_agent: '',
    application_state: {},
    reporter_email: '',
  });

  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState(false);

  // Auto-populate context information when modal opens
  useEffect(() => {
    if (isOpen) {
      const browserInfo = {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
        cookieEnabled: navigator.cookieEnabled,
        onLine: navigator.onLine,
        screenResolution: `${window.screen.width}x${window.screen.height}`,
        windowSize: `${window.innerWidth}x${window.innerHeight}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      };

      setFormData(prev => ({
        ...prev,
        current_url: window.location.href,
        page_title: document.title,
        browser_info: browserInfo,
        user_agent: navigator.userAgent,
        application_state: {
          pathname: window.location.pathname,
          search: window.location.search,
          hash: window.location.hash,
          timestamp: new Date().toISOString(),
        },
      }));

      // Reset form state
      setError('');
      setSuccess(false);
      setScreenshot(null);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      // Prepare form data with screenshot if provided
      const submitData: BugReportFormData = {
        ...formData,
        screenshot: screenshot || undefined,
      };

      // Submit bug report
      const result = await BugReportsService.create(submitData);
      
      setSuccess(true);
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess(result);
      }

      // Auto-close after short delay
      setTimeout(() => {
        onClose();
      }, 2000);

    } catch (err: any) {
      console.error('Error submitting bug report:', err);
      setError(err.response?.data?.error || err.message || 'Failed to submit bug report');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('Screenshot file size must be less than 10MB');
        return;
      }
      
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file for the screenshot');
        return;
      }
      
      setScreenshot(file);
      setError('');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      steps_to_reproduce: '',
      expected_behavior: '',
      actual_behavior: '',
      priority: 'medium',
      current_url: window.location.href,
      page_title: document.title,
      browser_info: {},
      user_agent: navigator.userAgent,
      application_state: {},
      reporter_email: '',
    });
    setScreenshot(null);
    setError('');
    setSuccess(false);
  };

  if (!isOpen) return null;

  return (
    <Overlay onClick={onClose}>
      <ModalContainer onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>🐛 Report a Bug</ModalTitle>
          <CloseButton onClick={onClose}>&times;</CloseButton>
        </ModalHeader>

        {success ? (
          <SuccessMessage>
            <SuccessIcon>✅</SuccessIcon>
            <SuccessText>
              <strong>Bug report submitted successfully!</strong>
              <br />
              A GitHub issue has been created and assigned to our support team.
              <br />
              <small>This modal will close automatically...</small>
            </SuccessText>
          </SuccessMessage>
        ) : (
          <form onSubmit={handleSubmit}>
            <ModalContent>
              <FormSection>
                <FormGroup>
                  <Label htmlFor="title">Bug Title *</Label>
                  <Input
                    id="title"
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Brief summary of the bug"
                    required
                    maxLength={200}
                  />
                </FormGroup>

                <FormGroup>
                  <Label htmlFor="description">Description *</Label>
                  <TextArea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Detailed description of what happened"
                    required
                    rows={4}
                  />
                </FormGroup>

                <FormGroup>
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    id="priority"
                    value={formData.priority}
                    onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as any }))}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </Select>
                </FormGroup>
              </FormSection>

              <FormSection>
                <SectionTitle>Additional Details (Optional)</SectionTitle>
                
                <FormGroup>
                  <Label htmlFor="steps">Steps to Reproduce</Label>
                  <TextArea
                    id="steps"
                    value={formData.steps_to_reproduce}
                    onChange={(e) => setFormData(prev => ({ ...prev, steps_to_reproduce: e.target.value }))}
                    placeholder="1. First step&#10;2. Second step&#10;3. ..."
                    rows={3}
                  />
                </FormGroup>

                <FormRow>
                  <FormGroup>
                    <Label htmlFor="expected">Expected Behavior</Label>
                    <TextArea
                      id="expected"
                      value={formData.expected_behavior}
                      onChange={(e) => setFormData(prev => ({ ...prev, expected_behavior: e.target.value }))}
                      placeholder="What should have happened"
                      rows={2}
                    />
                  </FormGroup>

                  <FormGroup>
                    <Label htmlFor="actual">Actual Behavior</Label>
                    <TextArea
                      id="actual"
                      value={formData.actual_behavior}
                      onChange={(e) => setFormData(prev => ({ ...prev, actual_behavior: e.target.value }))}
                      placeholder="What actually happened"
                      rows={2}
                    />
                  </FormGroup>
                </FormRow>

                <FormGroup>
                  <Label htmlFor="screenshot">Screenshot</Label>
                  <FileInput
                    id="screenshot"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                  />
                  {screenshot && (
                    <FileInfo>
                      Selected: {screenshot.name} ({(screenshot.size / 1024).toFixed(1)} KB)
                    </FileInfo>
                  )}
                </FormGroup>

                <FormGroup>
                  <Label htmlFor="email">Email (Optional)</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.reporter_email}
                    onChange={(e) => setFormData(prev => ({ ...prev, reporter_email: e.target.value }))}
                    placeholder="For updates on this bug report"
                  />
                </FormGroup>
              </FormSection>

              <ContextInfo>
                <small>
                  <strong>Context Information:</strong><br />
                  Page: {formData.page_title}<br />
                  URL: {formData.current_url}
                </small>
              </ContextInfo>

              {error && <ErrorMessage>{error}</ErrorMessage>}
            </ModalContent>

            <ModalFooter>
              <SecondaryButton type="button" onClick={resetForm}>
                Reset Form
              </SecondaryButton>
              <SecondaryButton type="button" onClick={onClose}>
                Cancel
              </SecondaryButton>
              <PrimaryButton type="submit" disabled={isSubmitting || !formData.title || !formData.description}>
                {isSubmitting ? 'Submitting...' : 'Submit Bug Report'}
              </PrimaryButton>
            </ModalFooter>
          </form>
        )}
      </ModalContainer>
    </Overlay>
  );
};

// Styled Components
const Overlay = styled.div`
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
  padding: ${spacing.md};
`;

const ModalContainer = styled.div`
  background: ${colors.background};
  border-radius: ${borderRadius.lg};
  box-shadow: ${shadows.xl};
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${spacing.lg};
  border-bottom: 1px solid ${colors.neutral[200]};
`;

const ModalTitle = styled.h2`
  margin: 0;
  color: ${colors.text.primary};
  font-size: ${typography.fontSize.xl};
  font-weight: ${typography.fontWeight.semibold};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: ${spacing.xs};
  color: ${colors.text.secondary};
  
  &:hover {
    color: ${colors.text.primary};
  }
`;

const ModalContent = styled.div`
  padding: ${spacing.lg};
`;

const ModalFooter = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${spacing.sm};
  padding: ${spacing.lg};
  border-top: 1px solid ${colors.neutral[200]};
`;

const FormSection = styled.div`
  margin-bottom: ${spacing.lg};
`;

const SectionTitle = styled.h3`
  margin: 0 0 ${spacing.md} 0;
  color: ${colors.text.primary};
  font-size: ${typography.fontSize.lg};
  font-weight: ${typography.fontWeight.medium};
`;

const FormGroup = styled.div`
  margin-bottom: ${spacing.md};
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${spacing.md};
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Label = styled.label`
  display: block;
  margin-bottom: ${spacing.xs};
  color: ${colors.text.primary};
  font-weight: ${typography.fontWeight.medium};
  font-size: ${typography.fontSize.sm};
`;

const Input = styled.input`
  width: 100%;
  padding: ${spacing.sm};
  border: 1px solid ${colors.neutral[300]};
  border-radius: ${borderRadius.md};
  font-size: ${typography.fontSize.sm};
  
  &:focus {
    outline: none;
    border-color: ${colors.primary[500]};
    box-shadow: 0 0 0 3px ${colors.primary[100]};
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: ${spacing.sm};
  border: 1px solid ${colors.neutral[300]};
  border-radius: ${borderRadius.md};
  font-size: ${typography.fontSize.sm};
  font-family: ${typography.fontFamily.sans};
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary[500]};
    box-shadow: 0 0 0 3px ${colors.primary[100]};
  }
`;

const Select = styled.select`
  width: 100%;
  padding: ${spacing.sm};
  border: 1px solid ${colors.neutral[300]};
  border-radius: ${borderRadius.md};
  font-size: ${typography.fontSize.sm};
  background: ${colors.background};
  
  &:focus {
    outline: none;
    border-color: ${colors.primary[500]};
    box-shadow: 0 0 0 3px ${colors.primary[100]};
  }
`;

const FileInput = styled.input`
  width: 100%;
  padding: ${spacing.sm};
  border: 1px solid ${colors.neutral[300]};
  border-radius: ${borderRadius.md};
  font-size: ${typography.fontSize.sm};
`;

const FileInfo = styled.div`
  margin-top: ${spacing.xs};
  font-size: ${typography.fontSize.xs};
  color: ${colors.text.secondary};
`;

const ContextInfo = styled.div`
  background: ${colors.neutral[50]};
  padding: ${spacing.sm};
  border-radius: ${borderRadius.md};
  border: 1px solid ${colors.neutral[200]};
  margin-bottom: ${spacing.md};
  
  small {
    color: ${colors.text.secondary};
    word-break: break-all;
  }
`;

const ErrorMessage = styled.div`
  background: ${colors.error[100]};
  border: 1px solid ${colors.error[100]};
  color: ${colors.error[700]};
  padding: ${spacing.sm};
  border-radius: ${borderRadius.md};
  margin-top: ${spacing.md};
`;

const SuccessMessage = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.md};
  padding: ${spacing.xl};
  text-align: center;
`;

const SuccessIcon = styled.div`
  font-size: 48px;
`;

const SuccessText = styled.div`
  color: ${colors.success[700]};
  font-size: ${typography.fontSize.base};
`;

const PrimaryButton = styled.button`
  background: ${colors.primary[600]};
  color: ${colors.text.inverse};
  border: none;
  padding: ${spacing.sm} ${spacing.lg};
  border-radius: ${borderRadius.md};
  font-weight: ${typography.fontWeight.medium};
  cursor: pointer;
  
  &:hover:not(:disabled) {
    background: ${colors.primary[700]};
  }
  
  &:disabled {
    background: ${colors.neutral[300]};
    cursor: not-allowed;
  }
`;

const SecondaryButton = styled.button`
  background: ${colors.background};
  color: ${colors.text.primary};
  border: 1px solid ${colors.neutral[300]};
  padding: ${spacing.sm} ${spacing.lg};
  border-radius: ${borderRadius.md};
  font-weight: ${typography.fontWeight.medium};
  cursor: pointer;
  
  &:hover {
    background: ${colors.neutral[50]};
  }
`;

export default BugReportModal;