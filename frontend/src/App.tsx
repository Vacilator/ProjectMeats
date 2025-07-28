/**
 * Main App component for ProjectMeats frontend.
 * 
 * Professional meat sales broker application with modern UI/UX.
 * Provides comprehensive business management tools for end-to-end
 * transaction processing, supplier/customer relationships, and financial tracking.
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import styled, { createGlobalStyle } from 'styled-components';
import { colors, typography, spacing, borderRadius, shadows } from './components/DesignSystem';
import UserProfile from './components/UserProfile';
import DashboardScreen from './screens/DashboardScreen';
import AccountsReceivablesScreen from './screens/AccountsReceivablesScreen';
import SuppliersScreen from './screens/SuppliersScreen';
import CustomersScreen from './screens/CustomersScreen';
import PurchaseOrdersScreen from './screens/PurchaseOrdersScreen';
import PlantsScreen from './screens/PlantsScreen';
import SupplierLocationsScreen from './screens/SupplierLocationsScreen';
// Additional screens for complete functionality:
import ContactsScreen from './screens/ContactsScreen';
import SupplierPlantMappingsScreen from './screens/SupplierPlantMappingsScreen';
import CarrierInfoScreen from './screens/CarrierInfoScreen';
import UserProfileScreen from './screens/UserProfileScreen';
import AIAssistantScreen from './screens/AIAssistantScreen';

// Enhanced global styles with design system
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: ${typography.fontFamily.sans};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: ${colors.surface};
    color: ${colors.text.primary};
    line-height: ${typography.lineHeight.normal};
  }

  code {
    font-family: ${typography.fontFamily.mono};
  }

  /* Accessibility improvements */
  *:focus {
    outline: 2px solid ${colors.primary[500]};
    outline-offset: 2px;
  }

  /* Smooth scrolling */
  html {
    scroll-behavior: smooth;
  }
`;

const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: ${colors.surface};
`;

const Header = styled.header`
  background: ${colors.background};
  border-bottom: 1px solid ${colors.neutral[200]};
  box-shadow: ${shadows.sm};
  position: sticky;
  top: 0;
  z-index: 100;
`;

const HeaderContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 ${spacing.lg};
  height: 70px;
  
  @media (max-width: 768px) {
    padding: 0 ${spacing.md};
    height: 60px;
  }
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.lg};
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
`;

const LogoIcon = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, ${colors.primary[600]} 0%, ${colors.primary[700]} 100%);
  border-radius: ${borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${colors.text.inverse};
  font-weight: 700;
  font-size: 18px;
`;

const LogoText = styled.div`
  display: flex;
  flex-direction: column;
`;

const LogoTitle = styled.h1`
  color: ${colors.text.primary};
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  line-height: 1;
`;

const LogoSubtitle = styled.span`
  color: ${colors.text.secondary};
  font-size: 12px;
  font-weight: 500;
  margin-top: 2px;
`;

const Navigation = styled.nav`
  display: flex;
  gap: ${spacing.xs};
  
  @media (max-width: 768px) {
    display: none; /* Could implement mobile menu here */
  }
`;

const NavItem = ({ to, children, icon }: { to: string; children: React.ReactNode; icon?: string }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <NavLinkStyled as={Link} to={to} $isActive={isActive}>
      {icon && <span style={{ marginRight: spacing.xs }}>{icon}</span>}
      {children}
    </NavLinkStyled>
  );
};

const NavLinkStyled = styled.div<{ $isActive?: boolean }>`
  color: ${props => props.$isActive ? colors.primary[600] : colors.text.secondary};
  text-decoration: none;
  font-weight: ${props => props.$isActive ? typography.fontWeight.semibold : typography.fontWeight.medium};
  font-size: ${typography.fontSize.sm};
  padding: ${spacing.sm} ${spacing.md};
  border-radius: ${borderRadius.md};
  transition: all 0.2s ease-in-out;
  display: flex;
  align-items: center;
  
  &:hover {
    color: ${colors.primary[600]};
    background-color: ${colors.primary[50]};
  }
  
  ${props => props.$isActive && `
    background-color: ${colors.primary[50]};
    box-shadow: inset 0 0 0 1px ${colors.primary[200]};
  `}
`;

const Main = styled.main`
  flex: 1;
  padding: ${spacing.lg} 0;
  min-height: calc(100vh - 70px - 60px); /* minus header and footer */
`;

const Footer = styled.footer`
  background: ${colors.background};
  border-top: 1px solid ${colors.neutral[200]};
  padding: ${spacing.lg};
  text-align: center;
  
  @media (max-width: 768px) {
    padding: ${spacing.md};
  }
`;

const FooterContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: ${spacing.md};
  
  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
  }
`;

const FooterText = styled.p`
  color: ${colors.text.secondary};
  font-size: ${typography.fontSize.sm};
  margin: 0;
`;

const FooterLinks = styled.div`
  display: flex;
  gap: ${spacing.lg};
  
  @media (max-width: 768px) {
    gap: ${spacing.md};
  }
`;

const FooterLink = styled.a`
  color: ${colors.text.muted};
  text-decoration: none;
  font-size: ${typography.fontSize.sm};
  
  &:hover {
    color: ${colors.primary[600]};
  }
`;

// Navigation component with location awareness
const NavigationWithLocation: React.FC = () => {
  return (
    <Navigation>
      <NavItem to="/dashboard" icon="📊">Dashboard</NavItem>
      <NavItem to="/ai-assistant" icon="🤖">AI Assistant</NavItem>
      <NavItem to="/accounts-receivables" icon="📋">Accounts</NavItem>
      <NavItem to="/suppliers" icon="🏢">Suppliers</NavItem>
      <NavItem to="/customers" icon="👥">Customers</NavItem>
      <NavItem to="/purchase-orders" icon="📦">Orders</NavItem>
      <NavItem to="/contacts" icon="📞">Contacts</NavItem>
    </Navigation>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <GlobalStyle />
      <AppContainer>
        <Header>
          <HeaderContent>
            <HeaderLeft>
              <Logo>
                <LogoIcon>🥩</LogoIcon>
                <LogoText>
                  <LogoTitle>ProjectMeats</LogoTitle>
                  <LogoSubtitle>Sales Management</LogoSubtitle>
                </LogoText>
              </Logo>
              <NavigationWithLocation />
            </HeaderLeft>
            <HeaderRight>
              <UserProfile />
            </HeaderRight>
          </HeaderContent>
        </Header>
        
        <Main>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardScreen />} />
            <Route path="/ai-assistant" element={<AIAssistantScreen />} />
            <Route path="/accounts-receivables" element={<AccountsReceivablesScreen />} />
            <Route path="/suppliers" element={<SuppliersScreen />} />
            <Route path="/customers" element={<CustomersScreen />} />
            <Route path="/purchase-orders" element={<PurchaseOrdersScreen />} />
            <Route path="/plants" element={<PlantsScreen />} />
            <Route path="/supplier-locations" element={<SupplierLocationsScreen />} />
            <Route path="/contacts" element={<ContactsScreen />} />
            <Route path="/supplier-plant-mappings" element={<SupplierPlantMappingsScreen />} />
            <Route path="/carriers" element={<CarrierInfoScreen />} />
            <Route path="/profile" element={<UserProfileScreen />} />
          </Routes>
        </Main>
        
        <Footer>
          <FooterContent>
            <FooterText>
              ProjectMeats © 2024 | Professional Meat Sales Management Platform
            </FooterText>
            <FooterLinks>
              <FooterLink href="#support">Support</FooterLink>
              <FooterLink href="#documentation">Documentation</FooterLink>
              <FooterLink href="#api">API</FooterLink>
            </FooterLinks>
          </FooterContent>
        </Footer>
      </AppContainer>
    </Router>
  );
};

export default App;