/**
 * Bug Report Button Component
 * 
 * A floating action button that allows users to quickly report bugs
 * from anywhere in the application.
 */
import React, { useState } from 'react';
import styled from 'styled-components';
import { colors, spacing, borderRadius, shadows } from './DesignSystem';
import BugReportModal from './BugReportModal';

interface BugReportButtonProps {
  position?: 'bottom-right' | 'bottom-left' | 'header';
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
}

const BugReportButton: React.FC<BugReportButtonProps> = ({ 
  position = 'bottom-right', 
  size = 'medium',
  showText = false 
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [recentSubmission, setRecentSubmission] = useState(false);

  const handleSuccess = (bugReport: any) => {
    setRecentSubmission(true);
    // Reset success state after a few seconds
    setTimeout(() => {
      setRecentSubmission(false);
    }, 5000);
  };

  const buttonTitle = recentSubmission 
    ? 'Bug report submitted successfully!' 
    : 'Report a bug or issue';

  return (
    <>
      <ButtonContainer $position={position} $size={size}>
        <StyledButton
          onClick={() => setIsModalOpen(true)}
          $size={size}
          $showText={showText}
          $success={recentSubmission}
          title={buttonTitle}
          disabled={recentSubmission}
        >
          <ButtonIcon $size={size}>
            {recentSubmission ? '✅' : '🐛'}
          </ButtonIcon>
          {showText && (
            <ButtonText $size={size}>
              {recentSubmission ? 'Submitted!' : 'Report Bug'}
            </ButtonText>
          )}
        </StyledButton>
      </ButtonContainer>

      <BugReportModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={handleSuccess}
      />
    </>
  );
};

// Styled Components
const ButtonContainer = styled.div<{ $position: string; $size: string }>`
  ${({ $position }) => {
    switch ($position) {
      case 'bottom-right':
        return `
          position: fixed;
          bottom: ${spacing.lg};
          right: ${spacing.lg};
          z-index: 999;
        `;
      case 'bottom-left':
        return `
          position: fixed;
          bottom: ${spacing.lg};
          left: ${spacing.lg};
          z-index: 999;
        `;
      case 'header':
        return `
          position: relative;
          display: inline-block;
        `;
      default:
        return '';
    }
  }}

  @media (max-width: 768px) {
    ${({ $position }) => $position === 'bottom-right' && `
      bottom: ${spacing.md};
      right: ${spacing.md};
    `}
    ${({ $position }) => $position === 'bottom-left' && `
      bottom: ${spacing.md};
      left: ${spacing.md};
    `}
  }
`;

const StyledButton = styled.button<{ 
  $size: string; 
  $showText: boolean; 
  $success: boolean;
}>`
  background: ${({ $success }) => $success ? colors.success[700] : colors.primary[600]};
  color: ${colors.text.inverse};
  border: none;
  border-radius: ${({ $showText }) => $showText ? borderRadius.lg : '50%'};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${spacing.xs};
  transition: all 0.2s ease-in-out;
  box-shadow: ${shadows.lg};
  
  ${({ $size, $showText }) => {
    const sizes = {
      small: $showText ? 'padding: 8px 12px;' : 'width: 40px; height: 40px;',
      medium: $showText ? 'padding: 12px 16px;' : 'width: 56px; height: 56px;',
      large: $showText ? 'padding: 16px 20px;' : 'width: 64px; height: 64px;',
    };
    return sizes[$size as keyof typeof sizes];
  }}

  &:hover:not(:disabled) {
    background: ${({ $success }) => $success ? colors.success[700] : colors.primary[700]};
    transform: translateY(-2px);
    box-shadow: ${shadows.xl};
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    cursor: default;
    transform: none;
  }

  &:focus {
    outline: none;
    box-shadow: ${shadows.lg}, 0 0 0 3px ${colors.primary[100]};
  }
`;

const ButtonIcon = styled.span<{ $size: string }>`
  font-size: ${({ $size }) => {
    const sizes = {
      small: '16px',
      medium: '20px', 
      large: '24px',
    };
    return sizes[$size as keyof typeof sizes];
  }};
  
  line-height: 1;
`;

const ButtonText = styled.span<{ $size: string }>`
  font-weight: 600;
  font-size: ${({ $size }) => {
    const sizes = {
      small: '12px',
      medium: '14px',
      large: '16px',
    };
    return sizes[$size as keyof typeof sizes];
  }};
  
  white-space: nowrap;
`;

export default BugReportButton;