/**
 * Modern Design System for ProjectMeats
 * 
 * Professional UI components and styling system for meat sales broker application.
 * Provides consistent, accessible, and industry-leading design patterns.
 */
import styled from 'styled-components';

// Design Tokens
export const colors = {
  // Primary Palette (Professional meat industry colors)
  primary: {
    50: '#fdf2f2',
    100: '#fde6e6',
    200: '#fbcdcd',
    300: '#f7a6a6',
    400: '#f27676',
    500: '#e94646',
    600: '#d32929',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
  },
  // Secondary Palette (Warm browns/earth tones)
  secondary: {
    50: '#fafaf9',
    100: '#f5f5f4',
    200: '#e7e5e4',
    300: '#d6d3d1',
    400: '#a8a29e',
    500: '#78716c',
    600: '#57534e',
    700: '#44403c',
    800: '#292524',
    900: '#1c1917',
  },
  // Neutral Palette
  neutral: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  // Status Colors
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    700: '#15803d'
  },
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    700: '#a16207'
  },
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    500: '#ef4444',
    700: '#b91c1c'
  },
  info: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    700: '#1d4ed8'
  },
  
  // Background
  background: '#ffffff',
  surface: '#f8fafc',
  
  // Text
  text: {
    primary: '#1f2937',
    secondary: '#4b5563',
    muted: '#9ca3af',
    inverse: '#ffffff',
  }
};

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
  '3xl': '64px',
};

export const typography = {
  fontFamily: {
    sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
    mono: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
  },
  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
    '4xl': '36px',
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  }
};

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
};

export const borderRadius = {
  sm: '4px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  full: '9999px',
};

// Enhanced Components

export const Card = styled.div<{ variant?: 'default' | 'elevated' | 'outlined' }>`
  background: ${colors.background};
  border-radius: ${borderRadius.lg};
  padding: ${spacing.lg};
  
  ${props => {
    switch (props.variant) {
      case 'elevated':
        return `box-shadow: ${shadows.lg};`;
      case 'outlined':
        return `border: 1px solid ${colors.neutral[200]};`;
      default:
        return `box-shadow: ${shadows.md};`;
    }
  }}
`;

export const Button = styled.button<{ 
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: ${borderRadius.md};
  font-family: ${typography.fontFamily.sans};
  font-weight: ${typography.fontWeight.medium};
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  text-decoration: none;
  
  ${props => {
    const size = props.size || 'md';
    switch (size) {
      case 'sm':
        return `
          padding: ${spacing.sm} ${spacing.md};
          font-size: ${typography.fontSize.sm};
        `;
      case 'lg':
        return `
          padding: ${spacing.md} ${spacing.xl};
          font-size: ${typography.fontSize.lg};
        `;
      default:
        return `
          padding: ${spacing.sm} ${spacing.lg};
          font-size: ${typography.fontSize.base};
        `;
    }
  }}
  
  ${props => props.fullWidth && 'width: 100%;'}
  
  ${props => {
    const variant = props.variant || 'primary';
    switch (variant) {
      case 'secondary':
        return `
          background-color: ${colors.secondary[600]};
          color: ${colors.text.inverse};
          &:hover:not(:disabled) {
            background-color: ${colors.secondary[700]};
          }
        `;
      case 'outline':
        return `
          background-color: transparent;
          color: ${colors.primary[600]};
          border: 1px solid ${colors.primary[600]};
          &:hover:not(:disabled) {
            background-color: ${colors.primary[50]};
          }
        `;
      case 'ghost':
        return `
          background-color: transparent;
          color: ${colors.primary[600]};
          &:hover:not(:disabled) {
            background-color: ${colors.primary[50]};
          }
        `;
      case 'danger':
        return `
          background-color: ${colors.error};
          color: ${colors.text.inverse};
          &:hover:not(:disabled) {
            background-color: #dc2626;
          }
        `;
      default: // primary
        return `
          background-color: ${colors.primary[600]};
          color: ${colors.text.inverse};
          &:hover:not(:disabled) {
            background-color: ${colors.primary[700]};
          }
        `;
    }
  }}
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px ${colors.primary[200]};
  }
`;

export const Input = styled.input<{ error?: boolean; fullWidth?: boolean }>`
  padding: ${spacing.sm} ${spacing.md};
  border: 1px solid ${props => props.error ? colors.error : colors.neutral[300]};
  border-radius: ${borderRadius.md};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.base};
  transition: border-color 0.2s ease-in-out;
  
  ${props => props.fullWidth && 'width: 100%;'}
  
  &:focus {
    outline: none;
    border-color: ${colors.primary[500]};
    box-shadow: 0 0 0 3px ${colors.primary[200]};
  }
  
  &::placeholder {
    color: ${colors.text.muted};
  }
`;

export const Label = styled.label<{ required?: boolean }>`
  display: block;
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.sm};
  font-weight: ${typography.fontWeight.medium};
  color: ${colors.text.primary};
  margin-bottom: ${spacing.xs};
  
  ${props => props.required && `
    &::after {
      content: ' *';
      color: ${colors.error};
    }
  `}
`;

export const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: ${colors.background};
  border-radius: ${borderRadius.lg};
  overflow: hidden;
  box-shadow: ${shadows.md};
`;

export const TableHeader = styled.th`
  background-color: ${colors.neutral[50]};
  padding: ${spacing.md};
  text-align: left;
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.sm};
  font-weight: ${typography.fontWeight.semibold};
  color: ${colors.text.primary};
  border-bottom: 1px solid ${colors.neutral[200]};
`;

export const TableRow = styled.tr`
  &:nth-child(even) {
    background-color: ${colors.neutral[50]};
  }
  
  &:hover {
    background-color: ${colors.primary[50]};
  }
  
  transition: background-color 0.15s ease-in-out;
`;

export const TableCell = styled.td`
  padding: ${spacing.md};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.sm};
  color: ${colors.text.primary};
  border-bottom: 1px solid ${colors.neutral[200]};
`;

export const Badge = styled.span<{ variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral' }>`
  display: inline-flex;
  align-items: center;
  padding: ${spacing.xs} ${spacing.sm};
  border-radius: ${borderRadius.full};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.xs};
  font-weight: ${typography.fontWeight.medium};
  
  ${props => {
    const variant = props.variant || 'neutral';
    switch (variant) {
      case 'success':
        return `
          background-color: #dcfce7;
          color: #166534;
        `;
      case 'warning':
        return `
          background-color: #fef3c7;
          color: #92400e;
        `;
      case 'error':
        return `
          background-color: #fee2e2;
          color: #991b1b;
        `;
      case 'info':
        return `
          background-color: #dbeafe;
          color: #1e40af;
        `;
      default:
        return `
          background-color: ${colors.neutral[100]};
          color: ${colors.neutral[700]};
        `;
    }
  }}
`;

export const Container = styled.div<{ maxWidth?: string }>`
  width: 100%;
  max-width: ${props => props.maxWidth || '1200px'};
  margin: 0 auto;
  padding: 0 ${spacing.lg};
  
  @media (max-width: 768px) {
    padding: 0 ${spacing.md};
  }
`;

export const Grid = styled.div<{ cols?: number; gap?: string }>`
  display: grid;
  grid-template-columns: repeat(${props => props.cols || 1}, 1fr);
  gap: ${props => props.gap || spacing.lg};
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

export const Flex = styled.div<{ 
  direction?: 'row' | 'column';
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around';
  gap?: string;
  wrap?: boolean;
}>`
  display: flex;
  flex-direction: ${props => props.direction || 'row'};
  align-items: ${props => {
    switch (props.align) {
      case 'start': return 'flex-start';
      case 'end': return 'flex-end';
      case 'stretch': return 'stretch';
      default: return 'center';
    }
  }};
  justify-content: ${props => {
    switch (props.justify) {
      case 'start': return 'flex-start';
      case 'end': return 'flex-end';
      case 'between': return 'space-between';
      case 'around': return 'space-around';
      default: return 'center';
    }
  }};
  gap: ${props => props.gap || spacing.md};
  
  ${props => props.wrap && 'flex-wrap: wrap;'}
`;

export const Text = styled.p<{ 
  size?: 'xs' | 'sm' | 'base' | 'lg' | 'xl';
  weight?: 'normal' | 'medium' | 'semibold' | 'bold';
  color?: 'primary' | 'secondary' | 'muted' | 'inverse';
}>`
  font-family: ${typography.fontFamily.sans};
  font-size: ${props => typography.fontSize[props.size || 'base']};
  font-weight: ${props => typography.fontWeight[props.weight || 'normal']};
  color: ${props => {
    switch (props.color) {
      case 'secondary': return colors.text.secondary;
      case 'muted': return colors.text.muted;
      case 'inverse': return colors.text.inverse;
      default: return colors.text.primary;
    }
  }};
  line-height: ${typography.lineHeight.normal};
  margin: 0;
`;

export const Heading = styled.h1<{ 
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  color?: 'primary' | 'secondary' | 'muted';
}>`
  font-family: ${typography.fontFamily.sans};
  font-weight: ${typography.fontWeight.bold};
  color: ${props => {
    switch (props.color) {
      case 'secondary': return colors.text.secondary;
      case 'muted': return colors.text.muted;
      default: return colors.text.primary;
    }
  }};
  line-height: ${typography.lineHeight.tight};
  margin: 0;
  
  ${props => {
    const level = props.level || 1;
    switch (level) {
      case 1: return `font-size: ${typography.fontSize['4xl']};`;
      case 2: return `font-size: ${typography.fontSize['3xl']};`;
      case 3: return `font-size: ${typography.fontSize['2xl']};`;
      case 4: return `font-size: ${typography.fontSize.xl};`;
      case 5: return `font-size: ${typography.fontSize.lg};`;
      case 6: return `font-size: ${typography.fontSize.base};`;
    }
  }}
`;

export const LoadingSpinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid ${colors.neutral[200]};
  border-top: 2px solid ${colors.primary[600]};
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

export const Alert = styled.div<{ variant?: 'success' | 'warning' | 'error' | 'info' }>`
  padding: ${spacing.md};
  border-radius: ${borderRadius.md};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.sm};
  
  ${props => {
    const variant = props.variant || 'info';
    switch (variant) {
      case 'success':
        return `
          background-color: #f0fdf4;
          color: #166534;
          border: 1px solid #bbf7d0;
        `;
      case 'warning':
        return `
          background-color: #fffbeb;
          color: #92400e;
          border: 1px solid #fde68a;
        `;
      case 'error':
        return `
          background-color: #fef2f2;
          color: #991b1b;
          border: 1px solid #fecaca;
        `;
      default: // info
        return `
          background-color: #eff6ff;
          color: #1e40af;
          border: 1px solid #bfdbfe;
        `;
    }
  }}
`;