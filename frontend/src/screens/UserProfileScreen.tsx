/**
 * User Profile Screen for ProjectMeats.
 * 
 * Allows users to view and edit their profile information.
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { colors, typography, spacing, borderRadius, shadows } from '../components/DesignSystem';
import { UserProfile as UserProfileType } from '../types';
import { UserProfilesService } from '../services/api';

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
  const [userProfile, setUserProfile] = useState<UserProfileType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        setLoading(true);
        setError(null);
        const profile = await UserProfilesService.getCurrentUserProfile();
        setUserProfile(profile);
      } catch (err) {
        console.error('Failed to fetch user profile:', err);
        setError('Failed to load user profile');
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, []);

  if (loading) {
    return (
      <Container>
        <LoadingContainer>
          <LoadingSpinner />
        </LoadingContainer>
      </Container>
    );
  }

  if (error || !userProfile) {
    return (
      <Container>
        <ErrorContainer>
          <ErrorText>{error || 'User profile not found'}</ErrorText>
        </ErrorContainer>
      </Container>
    );
  }

  const avatarSrc = userProfile.profile_image_url || DEFAULT_AVATAR;

  return (
    <Container>
      <Header>
        <Title>User Profile</Title>
        <Subtitle>View and manage your profile information</Subtitle>
      </Header>

      <ProfileCard>
        <ProfileHeader>
          <Avatar src={avatarSrc} alt={`${userProfile.display_name}'s avatar`} />
          <ProfileInfo>
            <DisplayName>{userProfile.display_name}</DisplayName>
            {userProfile.job_title && <JobTitle>{userProfile.job_title}</JobTitle>}
            {userProfile.department && <Department>{userProfile.department}</Department>}
            <div style={{ marginTop: spacing.sm }}>
              {userProfile.is_admin && <Badge $variant="admin">Administrator</Badge>}
              {userProfile.is_active ? (
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
              <InfoValue>{userProfile.email}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Phone</InfoLabel>
              <InfoValue>{userProfile.phone || 'Not provided'}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Username</InfoLabel>
              <InfoValue>{userProfile.username}</InfoValue>
            </InfoItem>
          </InfoSection>

          <InfoSection>
            <SectionTitle>Work Information</SectionTitle>
            <InfoItem>
              <InfoLabel>Department</InfoLabel>
              <InfoValue>{userProfile.department || 'Not specified'}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Job Title</InfoLabel>
              <InfoValue>{userProfile.job_title || 'Not specified'}</InfoValue>
            </InfoItem>
          </InfoSection>

          <InfoSection>
            <SectionTitle>Preferences</SectionTitle>
            <InfoItem>
              <InfoLabel>Timezone</InfoLabel>
              <InfoValue>{userProfile.timezone}</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Email Notifications</InfoLabel>
              <InfoValue>{userProfile.email_notifications ? 'Enabled' : 'Disabled'}</InfoValue>
            </InfoItem>
          </InfoSection>

          <InfoSection>
            <SectionTitle>Account Status</SectionTitle>
            <InfoItem>
              <InfoLabel>Account Type</InfoLabel>
              <InfoValue>
                {userProfile.is_superuser ? 'Super Administrator' : 
                 userProfile.is_staff ? 'Administrator' : 'Standard User'}
              </InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Profile Completion</InfoLabel>
              <InfoValue>
                {userProfile.has_complete_profile ? 'Complete' : 'Incomplete'}
              </InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>Member Since</InfoLabel>
              <InfoValue>
                {new Date(userProfile.created_on).toLocaleDateString()}
              </InfoValue>
            </InfoItem>
          </InfoSection>
        </InfoGrid>

        {userProfile.bio && (
          <InfoSection style={{ marginTop: spacing.lg }}>
            <SectionTitle>Bio</SectionTitle>
            <InfoValue>{userProfile.bio}</InfoValue>
          </InfoSection>
        )}
      </ProfileCard>
    </Container>
  );
};

export default UserProfileScreen;