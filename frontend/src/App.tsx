/**
 * Main App component for ProjectMeats frontend.
 * 
 * Provides routing and layout for the React application
 * migrated from PowerApps.
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import styled, { createGlobalStyle } from 'styled-components';
import AccountsReceivablesScreen from './screens/AccountsReceivablesScreen';
import SuppliersScreen from './screens/SuppliersScreen';
import CustomersScreen from './screens/CustomersScreen';
import PurchaseOrdersScreen from './screens/PurchaseOrdersScreen';
import PlantsScreen from './screens/PlantsScreen';
import SupplierLocationsScreen from './screens/SupplierLocationsScreen';
// Hidden screens as requested: ContactsScreen, SupplierPlantMappingsScreen, CarrierInfoScreen

// Global styles
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #f5f5f5;
    color: #333;
  }

  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
      monospace;
  }
`;

const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const Header = styled.header`
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 16px 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const HeaderContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.h1`
  color: #007bff;
  font-size: 24px;
  font-weight: 600;
`;

const Navigation = styled.nav`
  display: flex;
  gap: 24px;
`;

const NavLink = styled.a`
  color: #666;
  text-decoration: none;
  font-weight: 500;
  
  &:hover {
    color: #007bff;
  }
  
  &.active {
    color: #007bff;
    border-bottom: 2px solid #007bff;
    padding-bottom: 2px;
  }
`;

const Main = styled.main`
  flex: 1;
  padding: 0;
`;

const Footer = styled.footer`
  background: #fff;
  border-top: 1px solid #e0e0e0;
  padding: 16px 24px;
  text-align: center;
  color: #666;
  font-size: 14px;
`;

const App: React.FC = () => {
  return (
    <Router>
      <GlobalStyle />
      <AppContainer>
        <Header>
          <HeaderContent>
            <Logo>ProjectMeats</Logo>
            <Navigation>
              <NavLink href="/accounts-receivables" className="active">
                Accounts Receivables
              </NavLink>
              <NavLink href="/suppliers">Suppliers</NavLink>
              <NavLink href="/customers">Customers</NavLink>
              <NavLink href="/purchase-orders">Purchase Orders</NavLink>
              <NavLink href="/plants">Plants</NavLink>
              <NavLink href="/supplier-locations">Supplier Locations</NavLink>
            </Navigation>
          </HeaderContent>
        </Header>
        
        <Main>
          <Routes>
            <Route path="/" element={<Navigate to="/accounts-receivables" replace />} />
            <Route path="/accounts-receivables" element={<AccountsReceivablesScreen />} />
            <Route path="/suppliers" element={<SuppliersScreen />} />
            <Route path="/customers" element={<CustomersScreen />} />
            <Route path="/purchase-orders" element={<PurchaseOrdersScreen />} />
            <Route path="/plants" element={<PlantsScreen />} />
            <Route path="/supplier-locations" element={<SupplierLocationsScreen />} />
          </Routes>
        </Main>
        
        <Footer>
          ProjectMeats © 2024 | Migrated from PowerApps/Dataverse to Django + React
        </Footer>
      </AppContainer>
    </Router>
  );
};

export default App;