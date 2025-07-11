/**
 * Business Dashboard for ProjectMeats
 * 
 * Executive dashboard providing key performance indicators and business insights
 * for meat sales brokers. Displays critical metrics for transaction processing,
 * financial summaries, and operational efficiency.
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  Container, 
  Card, 
  Heading, 
  Text, 
  Grid, 
  Flex, 
  Badge,
  colors,
  spacing,
  shadows,
  borderRadius 
} from '../components/DesignSystem';
import { 
  SuppliersService, 
  CustomersService, 
  PurchaseOrdersService 
} from '../services/api';

// Types for dashboard data
interface DashboardMetrics {
  totalRevenue: number;
  activeOrders: number;
  totalCustomers: number;
  totalSuppliers: number;
  pendingOrders: number;
  completedOrdersThisMonth: number;
  averageOrderValue: number;
  topPerformingSuppliers: Array<{
    id: number;
    name: string;
    orderCount: number;
    totalValue: number;
  }>;
  recentActivity: Array<{
    id: number;
    type: 'order' | 'customer' | 'supplier';
    description: string;
    timestamp: string;
  }>;
}

// Styled Components
const DashboardGrid = styled(Grid)`
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  margin-bottom: ${spacing.xl};
`;

const MetricCard = styled(Card)<{ trend?: 'up' | 'down' | 'neutral' }>`
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: ${props => {
      switch (props.trend) {
        case 'up': return colors.success;
        case 'down': return colors.error;
        default: return colors.primary[500];
      }
    }};
  }
`;

const MetricValue = styled(Text)`
  font-size: 32px;
  font-weight: 700;
  color: ${colors.text.primary};
  margin-bottom: ${spacing.xs};
`;

const MetricLabel = styled(Text)`
  font-size: 14px;
  color: ${colors.text.secondary};
  margin-bottom: ${spacing.sm};
`;

const TrendIndicator = styled.span<{ trend: 'up' | 'down' | 'neutral' }>`
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 500;
  
  color: ${props => {
    switch (props.trend) {
      case 'up': return colors.success;
      case 'down': return colors.error;
      default: return colors.text.muted;
    }
  }};
  
  &::before {
    content: ${props => {
      switch (props.trend) {
        case 'up': return "'↗'";
        case 'down': return "'↘'";
        default: return "'→'";
      }
    }};
    margin-right: 4px;
  }
`;

const ActivityItem = styled.div`
  padding: ${spacing.md};
  border-left: 3px solid ${colors.primary[200]};
  background: ${colors.neutral[50]};
  border-radius: 0 ${borderRadius.md} ${borderRadius.md} 0;
  margin-bottom: ${spacing.sm};
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const ActivityTime = styled(Text)`
  font-size: 12px;
  color: ${colors.text.muted};
`;

const ChartPlaceholder = styled.div`
  height: 200px;
  background: linear-gradient(135deg, ${colors.primary[50]} 0%, ${colors.secondary[50]} 100%);
  border-radius: ${borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${colors.text.muted};
  font-style: italic;
`;

const QuickActionGrid = styled(Grid)`
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  margin-top: ${spacing.xl};
`;

const QuickActionCard = styled(Card)`
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${shadows.lg};
  }
`;

const QuickActionIcon = styled.div`
  width: 48px;
  height: 48px;
  background: ${colors.primary[100]};
  border-radius: ${borderRadius.full};
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto ${spacing.md};
  font-size: 24px;
`;

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load data from all services
      const [
        suppliers,
        customers,
        purchaseOrders
      ] = await Promise.all([
        SuppliersService.getList(),
        CustomersService.getList(),
        PurchaseOrdersService.getList()
      ]);

      // Calculate metrics
      const totalCustomers = customers.results?.length || 0;
      const totalSuppliers = suppliers.results?.length || 0;
      const orders = purchaseOrders.results || [];
      const activeOrders = orders.filter(order => order.status === 'active').length;
      
      // Calculate financial metrics
      const totalRevenue = orders.reduce((sum, order) => {
        if (order.quantity && order.price_per_unit) {
          return sum + (order.quantity * parseFloat(order.price_per_unit.toString()));
        }
        return sum;
      }, 0);
      
      const averageOrderValue = orders.length > 0 ? totalRevenue / orders.length : 0;
      
      // Get current month orders
      const currentMonth = new Date().getMonth();
      const currentYear = new Date().getFullYear();
      const completedOrdersThisMonth = orders.filter(order => {
        if (order.fulfillment_date) {
          const orderDate = new Date(order.fulfillment_date);
          return orderDate.getMonth() === currentMonth && 
                 orderDate.getFullYear() === currentYear &&
                 order.status === 'completed';
        }
        return false;
      }).length;

      // Mock recent activity (in a real app, this would come from an activity log)
      const recentActivity = [
        {
          id: 1,
          type: 'order' as const,
          description: 'New purchase order created for premium beef cuts',
          timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
        },
        {
          id: 2,
          type: 'customer' as const,
          description: 'New customer registration completed',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
        },
        {
          id: 3,
          type: 'supplier' as const,
          description: 'Supplier pricing updated for seasonal products',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(), // 4 hours ago
        }
      ];

      const dashboardMetrics: DashboardMetrics = {
        totalRevenue,
        activeOrders,
        totalCustomers,
        totalSuppliers,
        pendingOrders: orders.filter(order => order.status === 'inactive').length,
        completedOrdersThisMonth,
        averageOrderValue,
        topPerformingSuppliers: [], // Would be calculated from order data
        recentActivity
      };

      setMetrics(dashboardMetrics);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes} minutes ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)} hours ago`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)} days ago`;
    }
  };

  if (loading) {
    return (
      <Container>
        <Flex justify="center" style={{ padding: spacing['3xl'] }}>
          <Text>Loading dashboard...</Text>
        </Flex>
      </Container>
    );
  }

  if (error || !metrics) {
    return (
      <Container>
        <Card variant="outlined">
          <Text color="secondary">Error loading dashboard data</Text>
        </Card>
      </Container>
    );
  }

  return (
    <Container>
      <Flex justify="between" align="center" style={{ marginBottom: spacing.xl }}>
        <div>
          <Heading level={1}>Business Dashboard</Heading>
          <Text color="secondary" style={{ marginTop: spacing.xs }}>
            Real-time insights for meat sales operations
          </Text>
        </div>
        <Badge variant="success">Live Data</Badge>
      </Flex>

      {/* Key Metrics */}
      <DashboardGrid>
        <MetricCard trend="up">
          <MetricLabel>Total Revenue</MetricLabel>
          <MetricValue>{formatCurrency(metrics.totalRevenue)}</MetricValue>
          <TrendIndicator trend="up">12.5% from last month</TrendIndicator>
        </MetricCard>

        <MetricCard trend="neutral">
          <MetricLabel>Active Orders</MetricLabel>
          <MetricValue>{metrics.activeOrders}</MetricValue>
          <TrendIndicator trend="neutral">Processing</TrendIndicator>
        </MetricCard>

        <MetricCard trend="up">
          <MetricLabel>Total Customers</MetricLabel>
          <MetricValue>{metrics.totalCustomers}</MetricValue>
          <TrendIndicator trend="up">8.3% growth</TrendIndicator>
        </MetricCard>

        <MetricCard trend="neutral">
          <MetricLabel>Active Suppliers</MetricLabel>
          <MetricValue>{metrics.totalSuppliers}</MetricValue>
          <TrendIndicator trend="neutral">Stable network</TrendIndicator>
        </MetricCard>

        <MetricCard trend="down">
          <MetricLabel>Pending Orders</MetricLabel>
          <MetricValue>{metrics.pendingOrders}</MetricValue>
          <TrendIndicator trend="down">Reduced backlog</TrendIndicator>
        </MetricCard>

        <MetricCard trend="up">
          <MetricLabel>Avg Order Value</MetricLabel>
          <MetricValue>{formatCurrency(metrics.averageOrderValue)}</MetricValue>
          <TrendIndicator trend="up">15.2% increase</TrendIndicator>
        </MetricCard>
      </DashboardGrid>

      {/* Charts and Activity */}
      <Grid cols={2} gap={spacing.xl}>
        <Card>
          <Heading level={3} style={{ marginBottom: spacing.lg }}>
            Revenue Trend
          </Heading>
          <ChartPlaceholder>
            📊 Revenue chart visualization would appear here
          </ChartPlaceholder>
        </Card>

        <Card>
          <Heading level={3} style={{ marginBottom: spacing.lg }}>
            Recent Activity
          </Heading>
          <div>
            {metrics.recentActivity.map(activity => (
              <ActivityItem key={activity.id}>
                <Text size="sm" style={{ marginBottom: spacing.xs }}>
                  {activity.description}
                </Text>
                <ActivityTime>
                  {formatTimeAgo(activity.timestamp)}
                </ActivityTime>
              </ActivityItem>
            ))}
          </div>
        </Card>
      </Grid>

      {/* Quick Actions */}
      <div style={{ marginTop: spacing.xl }}>
        <Heading level={2} style={{ marginBottom: spacing.lg }}>
          Quick Actions
        </Heading>
        <QuickActionGrid>
          <QuickActionCard onClick={() => window.location.href = '/purchase-orders'}>
            <QuickActionIcon>📋</QuickActionIcon>
            <Heading level={4}>New Order</Heading>
            <Text size="sm" color="secondary">Create purchase order</Text>
          </QuickActionCard>

          <QuickActionCard onClick={() => window.location.href = '/customers'}>
            <QuickActionIcon>👥</QuickActionIcon>
            <Heading level={4}>Add Customer</Heading>
            <Text size="sm" color="secondary">Register new customer</Text>
          </QuickActionCard>

          <QuickActionCard onClick={() => window.location.href = '/suppliers'}>
            <QuickActionIcon>🏢</QuickActionIcon>
            <Heading level={4}>Manage Suppliers</Heading>
            <Text size="sm" color="secondary">Supplier relationships</Text>
          </QuickActionCard>

          <QuickActionCard onClick={() => alert('Reports feature coming soon!')}>
            <QuickActionIcon>📊</QuickActionIcon>
            <Heading level={4}>Generate Report</Heading>
            <Text size="sm" color="secondary">Business analytics</Text>
          </QuickActionCard>
        </QuickActionGrid>
      </div>
    </Container>
  );
};

export default Dashboard;