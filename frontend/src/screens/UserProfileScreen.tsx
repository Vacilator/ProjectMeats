/**
 * User Profile Screen for ProjectMeats.
 * 
 * Allows users to view and edit their profile information.
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, typography, spacing, borderRadius, shadows } from '../components/DesignSystem';
import { useAuth } from '../contexts/AuthContext';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: ${spacing.lg};
`;

const Header = styled.div`
  margin-bottom: ${spacing.xl};
`;

const Title = styled.h1`
  color: ${colors.text.primary};
  font-size: ${typography.fontSize['2xl']};
  font-weight: ${typography.fontWeight.bold};
  margin: 0 0 ${spacing.sm} 0;
`;

const Subtitle = styled.p`
  color: ${colors.text.secondary};
  font-size: ${typography.fontSize.lg};
  margin: 0;
`;

const ProfileCard = styled.div`
  background: ${colors.background};
  border-radius: ${borderRadius.lg};
  box-shadow: ${shadows.md};
  padding: ${spacing.xl};
  margin-bottom: ${spacing.xl};
`;

const ProfileHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.lg};
  margin-bottom: ${spacing.xl};
`;

const Avatar = styled.img`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid ${colors.neutral[200]};
`;

const ProfileInfo = styled.div`
  flex: 1;
`;

const DisplayName = styled.h2`
  color: ${colors.text.primary};
  font-size: ${typography.fontSize.xl};
  font-weight: ${typography.fontWeight.semibold};
  margin: 0 0 ${spacing.xs} 0;
`;

const JobTitle = styled.p`
  color: ${colors.text.secondary};
  font-size: ${typography.fontSize.base};
  margin: 0 0 ${spacing.sm} 0;
`;

const Department = styled.p`
  color: ${colors.text.muted};
  font-size: ${typography.fontSize.sm};
  margin: 0;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${spacing.lg};
`;

const InfoSection = styled.div`
  border: 1px solid ${colors.neutral[200]};
  border-radius: ${borderRadius.md};
  padding: ${spacing.lg};
`;

const SectionTitle = styled.h3`
  color: ${colors.text.primary};
  font-size: ${typography.fontSize.lg};
  font-weight: ${typography.fontWeight.semibold};
  margin: 0 0 ${spacing.md} 0;
`;

const InfoItem = styled.div`
  margin-bottom: ${spacing.md};
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const InfoLabel = styled.div`
  color: ${colors.text.secondary};
  font-size: ${typography.fontSize.sm};
  font-weight: ${typography.fontWeight.medium};
  margin-bottom: ${spacing.xs};
`;

const InfoValue = styled.div`
  color: ${colors.text.primary};
  font-size: ${typography.fontSize.base};
`;

const Badge = styled.span<{ $variant: 'admin' | 'user' | 'active' | 'inactive' }>`
  display: inline-block;
  padding: ${spacing.xs} ${spacing.sm};
  border-radius: ${borderRadius.sm};
  font-size: ${typography.fontSize.xs};
  font-weight: ${typography.fontWeight.medium};
  
  ${props => {
    switch (props.$variant) {
      case 'admin':
        return `
          background-color: ${colors.primary[100]};
          color: ${colors.primary[700]};
        `;
      case 'user':
        return `
          background-color: ${colors.neutral[100]};
          color: ${colors.neutral[700]};
        `;
      case 'active':
        return `
          background-color: ${colors.success[100]};
          color: ${colors.success[700]};
        `;
      case 'inactive':
        return `
          background-color: ${colors.error[100]};
          color: ${colors.error[700]};
        `;
      default:
        return `
          background-color: ${colors.neutral[100]};
          color: ${colors.neutral[700]};
        `;
    }
  }}
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
`;

const LoadingSpinner = styled.div`
  width: 32px;
  height: 32px;
  border: 3px solid ${colors.neutral[200]};
  border-top: 3px solid ${colors.primary[500]};
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorContainer = styled.div`
  background: ${colors.error[100]};
  border: 1px solid ${colors.error[100]};
  border-radius: ${borderRadius.md};
  padding: ${spacing.lg};
  text-align: center;
`;

const ErrorText = styled.p`
  color: ${colors.error[700]};
  font-size: ${typography.fontSize.base};
  margin: 0;
`;

// Default avatar when no profile image is available
const DEFAULT_AVATAR = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9IiNFNUU3RUIiLz4KPGNpcmNsZSBjeD0iNDAiIGN5PSIzMCIgcj0iMTIiIGZpbGw9IiM5Q0EzQUYiLz4KPHBhdGggZD0iTTE2IDY0YzAtMTMuMjU1IDEwLjc0NS0yNCAyNC0yNHMyNCAxMC43NDUgMjQgMjR2MkgxNnoiIGZpbGw9IiM5Q0EzQUYiLz4KPC9zdmc+";

const UserProfileScreen: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Container>
        <LoadingContainer>
          <LoadingSpinner />
        </LoadingContainer>
      </Container>
    );
  }

  if (!user) {
    return (
      <Container>
        <ErrorContainer>
          <ErrorText>User profile not found</ErrorText>
        </ErrorContainer>
      </Container>
    );
  }

  const avatarSrc = user.profile_image_url || DEFAULT_AVATAR;

  return (
    <Container>
      <Header>
        <Title>User Profile</Title>
        <Subtitle>View and manage your profile information</Subtitle>
      </Header>

      <ProfileCard>
        <ProfileHeader>
          <Avatar src={avatarSrc} alt={`${user.display_name}'s avatar`} />
          <ProfileInfo>
            <DisplayName>{user.display_name}</DisplayName>
            {user.job_title && <JobTitle>{user.job_title}</JobTitle>}
            {user.department && <Department>{user.department}</Department>}
            <div style={{ marginTop: spacing.sm }}>
              {user.is_admin && <Badge $variant="admin">Administrator</Badge>}
              {user.is_active ? (
                <Badge $variant="active" style={{ marginLeft: spacing.xs }}>Active</Badge>
              ) : (
                <Badge $variant="inactive" style={{ marginLeft: spacing.xs }}>Inactive</Badge>
              )}
            </div>
          </ProfileInfo>
        </ProfileHeader>

        <InfoGrid>
          <InfoSection>
            <SectionTitle>Contact Information</SectionTitle>
            <InfoItem>
              <InfoLabel>Email</InfoLabel>
              <InfoValue>{user.email}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Phone</InfoLabel>
              <InfoValue>{user.phone || 'Not provided'}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Username</InfoLabel>
              <InfoValue>{user.username}</InfoValue>
            </InfoItem>
          </InfoSection>

          <InfoSection>
            <SectionTitle>Work Information</SectionTitle>
            <InfoItem>
              <InfoLabel>Department</InfoLabel>
              <InfoValue>{user.department || 'Not specified'}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Job Title</InfoLabel>
              <InfoValue>{user.job_title || 'Not specified'}</InfoValue>
            </InfoItem>
          </InfoSection>

          <InfoSection>
            <SectionTitle>Preferences</SectionTitle>
            <InfoItem>
              <InfoLabel>Timezone</InfoLabel>
              <InfoValue>{user.timezone}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Email Notifications</InfoLabel>
              <InfoValue>{user.email_notifications ? 'Enabled' : 'Disabled'}</InfoValue>
            </InfoItem>
          </InfoSection>

          <InfoSection>
            <SectionTitle>Account Status</SectionTitle>
            <InfoItem>
              <InfoLabel>Account Type</InfoLabel>
              <InfoValue>
                {user.is_superuser ? 'Super Administrator' : 
                 user.is_staff ? 'Administrator' : 'Standard User'}
              </InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Profile Completion</InfoLabel>
              <InfoValue>
                {user.has_complete_profile ? 'Complete' : 'Incomplete'}
              </InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Member Since</InfoLabel>
              <InfoValue>
                {new Date(user.created_on).toLocaleDateString()}
              </InfoValue>
            </InfoItem>
          </InfoSection>
        </InfoGrid>

        {user.bio && (
          <InfoSection style={{ marginTop: spacing.lg }}>
            <SectionTitle>Bio</SectionTitle>
            <InfoValue>{user.bio}</InfoValue>
          </InfoSection>
        )}
      </ProfileCard>
    </Container>
  );
};

export default UserProfileScreen;