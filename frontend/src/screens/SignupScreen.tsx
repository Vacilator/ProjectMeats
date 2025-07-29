/**
 * Signup Screen for ProjectMeats.
 * 
 * Provides user registration interface with form validation and automatic login.
 */
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { colors, typography, spacing, borderRadius, shadows } from '../components/DesignSystem';
import { useAuth } from '../contexts/AuthContext';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, ${colors.primary[50]} 0%, ${colors.surface} 100%);
  padding: ${spacing.lg};
`;

const SignupCard = styled.div`
  background: ${colors.background};
  border-radius: ${borderRadius.lg};
  box-shadow: ${shadows.xl};
  padding: ${spacing.xl};
  width: 100%;
  max-width: 500px;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: ${spacing.xl};
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${spacing.sm};
  margin-bottom: ${spacing.lg};
`;

const LogoIcon = styled.div`
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, ${colors.primary[600]} 0%, ${colors.primary[700]} 100%);
  border-radius: ${borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${colors.text.inverse};
  font-weight: 700;
  font-size: 24px;
`;

const Title = styled.h1`
  color: ${colors.text.primary};
  font-size: ${typography.fontSize['2xl']};
  font-weight: ${typography.fontWeight.bold};
  margin: 0 0 ${spacing.xs} 0;
`;

const Subtitle = styled.p`
  color: ${colors.text.secondary};
  font-size: ${typography.fontSize.base};
  margin: 0;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${spacing.lg};
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${spacing.md};
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing.xs};
`;

const Label = styled.label`
  color: ${colors.text.primary};
  font-size: ${typography.fontSize.sm};
  font-weight: ${typography.fontWeight.medium};
`;

const Input = styled.input<{ $hasError?: boolean }>`
  padding: ${spacing.md};
  border: 1px solid ${props => props.$hasError ? colors.error[300] : colors.neutral[300]};
  border-radius: ${borderRadius.md};
  font-size: ${typography.fontSize.base};
  color: ${colors.text.primary};
  background: ${colors.background};
  transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  
  &:focus {
    outline: none;
    border-color: ${props => props.$hasError ? colors.error[500] : colors.primary[500]};
    box-shadow: 0 0 0 3px ${props => props.$hasError ? colors.error[100] : colors.primary[100]};
  }
  
  &::placeholder {
    color: ${colors.text.muted};
  }
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  padding: ${spacing.md} ${spacing.lg};
  border: none;
  border-radius: ${borderRadius.md};
  font-size: ${typography.fontSize.base};
  font-weight: ${typography.fontWeight.medium};
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${spacing.xs};
  
  ${props => props.$variant === 'secondary' ? `
    background: ${colors.neutral[100]};
    color: ${colors.text.secondary};
    
    &:hover {
      background: ${colors.neutral[200]};
    }
  ` : `
    background: ${colors.primary[600]};
    color: ${colors.text.inverse};
    
    &:hover {
      background: ${colors.primary[700]};
    }
    
    &:active {
      background: ${colors.primary[800]};
    }
  `}
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  background: ${colors.error[50]};
  border: 1px solid ${colors.error[200]};
  border-radius: ${borderRadius.md};
  padding: ${spacing.md};
  color: ${colors.error[700]};
  font-size: ${typography.fontSize.sm};
  display: flex;
  align-items: center;
  gap: ${spacing.xs};
`;

const SuccessMessage = styled.div`
  background: ${colors.success[50]};
  border: 1px solid ${colors.success[200]};
  border-radius: ${borderRadius.md};
  padding: ${spacing.md};
  color: ${colors.success[700]};
  font-size: ${typography.fontSize.sm};
  display: flex;
  align-items: center;
  gap: ${spacing.xs};
`;

const InfoMessage = styled.div`
  background: ${colors.primary[50]};
  border: 1px solid ${colors.primary[200]};
  border-radius: ${borderRadius.md};
  padding: ${spacing.md};
  color: ${colors.primary[700]};
  font-size: ${typography.fontSize.sm};
  display: flex;
  align-items: center;
  gap: ${spacing.xs};
  margin-bottom: ${spacing.lg};
`;

const Footer = styled.div`
  text-align: center;
  margin-top: ${spacing.lg};
  padding-top: ${spacing.lg};
  border-top: 1px solid ${colors.neutral[200]};
`;

const FooterText = styled.p`
  color: ${colors.text.secondary};
  font-size: ${typography.fontSize.sm};
  margin: 0 0 ${spacing.sm} 0;
`;

const FooterLink = styled(Link)`
  color: ${colors.primary[600]};
  text-decoration: none;
  font-weight: ${typography.fontWeight.medium};
  
  &:hover {
    color: ${colors.primary[700]};
    text-decoration: underline;
  }
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const SignupScreen: React.FC = () => {
  const { signup, isLoading, error, clearError, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: '',
    department: '',
    job_title: ''
  });
  const [localLoading, setLocalLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // Clear errors when form data changes
  useEffect(() => {
    if (error) {
      clearError();
    }
  }, [formData, clearError, error]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.username || !formData.email || !formData.password) {
      return;
    }

    setLocalLoading(true);
    const success = await signup(formData);
    
    if (success) {
      setShowSuccess(true);
      setTimeout(() => {
        navigate('/dashboard', { replace: true });
      }, 1500);
    }
    
    setLocalLoading(false);
  };

  return (
    <Container>
      <SignupCard>
        <Header>
          <Logo>
            <LogoIcon>🥩</LogoIcon>
          </Logo>
          <Title>Create Account</Title>
          <Subtitle>Join ProjectMeats to manage your business</Subtitle>
        </Header>

        <InfoMessage>
          💡 In development mode, new accounts automatically get admin access!
        </InfoMessage>

        {showSuccess && (
          <SuccessMessage>
            ✅ Account created successfully! You've been automatically logged in. Redirecting...
          </SuccessMessage>
        )}

        {error && (
          <ErrorMessage>
            ⚠️ {error}
          </ErrorMessage>
        )}

        <Form onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="username">Username *</Label>
            <Input
              id="username"
              name="username"
              type="text"
              placeholder="Choose a username"
              value={formData.username}
              onChange={handleInputChange}
              required
              $hasError={!!error}
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="email">Email Address *</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleInputChange}
              required
              $hasError={!!error}
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="password">Password *</Label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder="Create a password"
              value={formData.password}
              onChange={handleInputChange}
              required
              $hasError={!!error}
            />
          </FormGroup>

          <FormRow>
            <FormGroup>
              <Label htmlFor="first_name">First Name</Label>
              <Input
                id="first_name"
                name="first_name"
                type="text"
                placeholder="First name"
                value={formData.first_name}
                onChange={handleInputChange}
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="last_name">Last Name</Label>
              <Input
                id="last_name"
                name="last_name"
                type="text"
                placeholder="Last name"
                value={formData.last_name}
                onChange={handleInputChange}
              />
            </FormGroup>
          </FormRow>

          <FormRow>
            <FormGroup>
              <Label htmlFor="department">Department</Label>
              <Input
                id="department"
                name="department"
                type="text"
                placeholder="Your department"
                value={formData.department}
                onChange={handleInputChange}
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="job_title">Job Title</Label>
              <Input
                id="job_title"
                name="job_title"
                type="text"
                placeholder="Your job title"
                value={formData.job_title}
                onChange={handleInputChange}
              />
            </FormGroup>
          </FormRow>

          <FormGroup>
            <Label htmlFor="phone">Phone Number</Label>
            <Input
              id="phone"
              name="phone"
              type="tel"
              placeholder="Your phone number"
              value={formData.phone}
              onChange={handleInputChange}
            />
          </FormGroup>

          <Button type="submit" disabled={isLoading || localLoading || showSuccess}>
            {(isLoading || localLoading) ? (
              <>
                <LoadingSpinner />
                Creating account...
              </>
            ) : (
              'Create Account'
            )}
          </Button>
        </Form>

        <Footer>
          <FooterText>Already have an account?</FooterText>
          <FooterLink to="/login">Sign in here</FooterLink>
        </Footer>
      </SignupCard>
    </Container>
  );
};

export default SignupScreen;