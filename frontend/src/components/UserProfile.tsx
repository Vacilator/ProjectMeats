/**
 * UserProfile component for header navigation.
 * 
 * Displays user avatar, name, and dropdown menu with profile options.
 */
import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { colors, typography, spacing, borderRadius, shadows } from './DesignSystem';
import { UserProfile as UserProfileType } from '../types';
import { UserProfilesService } from '../services/api';

// Default avatar when no profile image is available
const DEFAULT_AVATAR = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiNFNUU3RUIiLz4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxMiIgcj0iNSIgZmlsbD0iIzlDQTNBRiIvPgo8cGF0aCBkPSJNNiAyNmMwLTUuNTIzIDQuNDc3LTEwIDEwLTEwczEwIDQuNDc3IDEwIDEwdjFINnoiIGZpbGw9IiM5Q0EzQUYiLz4KPC9zdmc+";

interface UserProfileProps {
  className?: string;
}

const ProfileContainer = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`;

const ProfileButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  padding: ${spacing.sm};
  background: none;
  border: none;
  border-radius: ${borderRadius.md};
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  
  &:hover {
    background-color: ${colors.neutral[50]};
  }
  
  &:focus {
    outline: 2px solid ${colors.primary[500]};
    outline-offset: 2px;
  }
`;

const Avatar = styled.img`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid ${colors.neutral[200]};
`;

const UserInfo = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  
  @media (max-width: 768px) {
    display: none;
  }
`;

const UserName = styled.span`
  font-size: ${typography.fontSize.sm};
  font-weight: ${typography.fontWeight.medium};
  color: ${colors.text.primary};
  line-height: 1.2;
`;

const UserRole = styled.span`
  font-size: ${typography.fontSize.xs};
  color: ${colors.text.secondary};
  line-height: 1.2;
`;

const DropdownArrow = styled.span<{ $isOpen: boolean }>`
  display: inline-block;
  margin-left: ${spacing.xs};
  transform: ${props => props.$isOpen ? 'rotate(180deg)' : 'rotate(0deg)'};
  transition: transform 0.2s ease-in-out;
  color: ${colors.text.secondary};
  font-size: 12px;
`;

const DropdownMenu = styled.div<{ $isOpen: boolean }>`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: ${spacing.xs};
  background: ${colors.background};
  border: 1px solid ${colors.neutral[200]};
  border-radius: ${borderRadius.md};
  box-shadow: ${shadows.lg};
  min-width: 200px;
  z-index: 1000;
  opacity: ${props => props.$isOpen ? 1 : 0};
  visibility: ${props => props.$isOpen ? 'visible' : 'hidden'};
  transform: ${props => props.$isOpen ? 'translateY(0)' : 'translateY(-8px)'};
  transition: all 0.2s ease-in-out;
`;

const DropdownHeader = styled.div`
  padding: ${spacing.md};
  border-bottom: 1px solid ${colors.neutral[100]};
`;

const DropdownUserName = styled.div`
  font-size: ${typography.fontSize.sm};
  font-weight: ${typography.fontWeight.semibold};
  color: ${colors.text.primary};
  margin-bottom: 2px;
`;

const DropdownUserEmail = styled.div`
  font-size: ${typography.fontSize.xs};
  color: ${colors.text.secondary};
`;

const DropdownItem = styled.button`
  width: 100%;
  padding: ${spacing.sm} ${spacing.md};
  background: none;
  border: none;
  text-align: left;
  font-size: ${typography.fontSize.sm};
  color: ${colors.text.primary};
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
  
  &:hover {
    background-color: ${colors.neutral[50]};
  }
  
  &:focus {
    outline: none;
    background-color: ${colors.primary[50]};
    color: ${colors.primary[600]};
  }
`;

const DropdownDivider = styled.hr`
  margin: 0;
  border: none;
  border-top: 1px solid ${colors.neutral[100]};
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid ${colors.neutral[200]};
  border-top: 2px solid ${colors.primary[500]};
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const UserProfile: React.FC<UserProfileProps> = ({ className }) => {
  const { user, isAuthenticated, logout, isLoading } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // If not authenticated, show login button
  if (!isAuthenticated) {
    return (
      <ProfileContainer className={className}>
        <ProfileButton onClick={() => navigate('/login')}>
          Sign In
        </ProfileButton>
      </ProfileContainer>
    );
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close dropdown on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleMenuAction = async (action: string) => {
    console.log(`User selected: ${action}`);
    setIsOpen(false);
    
    // Implement actual navigation/actions
    switch (action) {
      case 'profile':
        // Navigate to profile page
        navigate('/profile');
        break;
      case 'settings':
        // Navigate to settings page - for now redirect to profile
        navigate('/profile');
        break;
      case 'admin':
        // Open admin portal in new tab
        const adminUrl = process.env.NODE_ENV === 'production' 
          ? `${window.location.origin}/admin/`
          : 'http://localhost:8000/admin/';
        window.open(adminUrl, '_blank');
        break;
      case 'logout':
        // Handle logout
        if (window.confirm('Are you sure you want to sign out?')) {
          await logout();
          navigate('/login');
        }
        break;
      default:
        break;
    }
  };

  if (isLoading) {
    return (
      <ProfileContainer className={className}>
        <LoadingSpinner />
      </ProfileContainer>
    );
  }

  if (!user) {
    return (
      <ProfileContainer className={className}>
        <ProfileButton onClick={() => navigate('/login')}>
          Sign In
        </ProfileButton>
      </ProfileContainer>
    );
  }

  const avatarSrc = user.profile_image_url || DEFAULT_AVATAR;
  const displayName = user.display_name || `${user.first_name} ${user.last_name}`.trim() || user.username;
  const jobTitle = user.job_title || user.department || 'User';

  return (
    <ProfileContainer className={className} ref={dropdownRef}>
      <ProfileButton onClick={toggleDropdown} aria-expanded={isOpen} aria-haspopup="true">
        <Avatar src={avatarSrc} alt={`${displayName}'s avatar`} />
        <UserInfo>
          <UserName>{displayName}</UserName>
          <UserRole>{jobTitle}</UserRole>
        </UserInfo>
        <DropdownArrow $isOpen={isOpen}>▼</DropdownArrow>
      </ProfileButton>

      <DropdownMenu $isOpen={isOpen} role="menu">
        <DropdownHeader>
          <DropdownUserName>{displayName}</DropdownUserName>
          <DropdownUserEmail>{user.email}</DropdownUserEmail>
        </DropdownHeader>

        <DropdownItem onClick={() => handleMenuAction('profile')} role="menuitem">
          👤 View Profile
        </DropdownItem>
        
        <DropdownItem onClick={() => handleMenuAction('settings')} role="menuitem">
          ⚙️ Settings
        </DropdownItem>
        
        {user.is_admin && (
          <DropdownItem onClick={() => handleMenuAction('admin')} role="menuitem">
            🔧 Admin Portal
          </DropdownItem>
        )}
        
        <DropdownDivider />
        
        <DropdownItem onClick={() => handleMenuAction('logout')} role="menuitem">
          🚪 Sign Out
        </DropdownItem>
      </DropdownMenu>
    </ProfileContainer>
  );
};

export default UserProfile;