# Frontend Setup Guide

This guide helps you set up the React frontend for ProjectMeats, providing a modern web interface for the business management system migrated from PowerApps.

## Prerequisites

- Node.js 16+ (LTS recommended)
- npm or yarn package manager
- Running Django backend (see [Backend Setup Guide](backend_setup.md))

## Quick Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or with yarn:
   yarn install
   ```

3. **Configure environment:**
   ```bash
   # Create environment file
   echo "REACT_APP_API_BASE_URL=http://localhost:8000/api/v1" > .env.local
   ```

4. **Start development server:**
   ```bash
   npm start
   # or with yarn:
   yarn start
   ```

5. **Open browser:**
   - Application: http://localhost:3000
   - API Documentation: http://localhost:8000/api/docs/

## Project Structure

```
frontend/
├── public/                    # Static assets
│   └── index.html            # HTML template
├── src/
│   ├── components/           # Reusable React components
│   ├── screens/             # Main application screens
│   │   └── AccountsReceivablesScreen.tsx
│   ├── services/            # API communication layer
│   │   └── api.ts           # Django REST API client
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # Entity types from PowerApps
│   ├── utils/               # Utility functions
│   ├── App.tsx              # Main application component
│   └── index.tsx            # React DOM entry point
├── package.json             # Dependencies and scripts
└── tsconfig.json           # TypeScript configuration
```

## Development Workflow

### Component Development

#### Screen Components
Screen components represent full pages and handle:
- Data fetching from API
- State management
- Layout and navigation
- Error handling

Example pattern:
```typescript
// screens/EntityScreen.tsx
import React, { useState, useEffect } from 'react';
import { EntityService } from '../services/api';

const EntityScreen: React.FC = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    try {
      const response = await EntityService.getList();
      setData(response.results);
    } catch (error) {
      // Handle error
    } finally {
      setLoading(false);
    }
  };
  
  return (
    // Component JSX
  );
};
```

#### Reusable Components
Create reusable components in `src/components/`:
- `Table.tsx` - Generic data table
- `SearchInput.tsx` - Search with debouncing
- `StatusBadge.tsx` - Status indicator
- `LoadingSpinner.tsx` - Loading indicator

### API Integration

#### Service Layer Pattern
All API communication goes through service classes:

```typescript
// services/api.ts
export class EntityService {
  static async getList(filters?) {
    return apiClient.get('/entities/', { params: filters });
  }
  
  static async create(data) {
    return apiClient.post('/entities/', data);
  }
  
  // ... other CRUD operations
}
```

#### Error Handling
Standardized error handling across the application:

```typescript
try {
  const data = await EntityService.getList();
  // Handle success
} catch (error) {
  if (error.response?.status === 404) {
    // Handle not found
  } else if (error.response?.status >= 500) {
    // Handle server error
  } else {
    // Handle other errors
  }
}
```

### TypeScript Integration

#### Entity Types
Define TypeScript interfaces that match Django serializers:

```typescript
// types/index.ts
export interface AccountsReceivable extends OwnedEntity, StatusEntity {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  terms?: string;
}
```

#### Props and State
Use TypeScript for component props and state:

```typescript
interface ScreenProps {
  entityId?: number;
  onClose?: () => void;
}

const Screen: React.FC<ScreenProps> = ({ entityId, onClose }) => {
  const [entity, setEntity] = useState<AccountsReceivable | null>(null);
  // ...
};
```

### Styling with Styled Components

#### Component Styling
Use styled-components for component-specific styles:

```typescript
import styled from 'styled-components';

const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 8px 16px;
  background: ${props => props.variant === 'primary' ? '#007bff' : 'white'};
  color: ${props => props.variant === 'primary' ? 'white' : '#333'};
`;
```

#### Global Styles
Define global styles in the main App component:

```typescript
const GlobalStyle = createGlobalStyle`
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background-color: #f5f5f5;
  }
`;
```

## Testing

### Running Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage --watchAll=false
```

### Writing Tests
Create test files alongside components:

```typescript
// __tests__/AccountsReceivablesScreen.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import AccountsReceivablesScreen from '../AccountsReceivablesScreen';

test('renders accounts receivables list', async () => {
  render(<AccountsReceivablesScreen />);
  
  await waitFor(() => {
    expect(screen.getByText('Accounts Receivables')).toBeInTheDocument();
  });
});
```

## Building for Production

### Environment Configuration
Create production environment file:

```bash
# .env.production
REACT_APP_API_BASE_URL=https://api.yourproductiondomain.com/api/v1
REACT_APP_ENVIRONMENT=production
```

### Build Commands
```bash
# Create production build
npm run build

# Serve build locally for testing
npx serve -s build

# Analyze bundle size
npm install --save-dev @typescript-eslint/parser
npm run build -- --analyze
```

### Deployment Options

#### Static Hosting (Netlify, Vercel, S3)
```bash
npm run build
# Upload build/ folder to hosting service
```

#### Docker Deployment
```dockerfile
# Dockerfile (in frontend directory)
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## PowerApps Migration Notes

### UI/UX Migration Strategy

1. **Preserve Business Logic**: Maintain the same workflows and data relationships from PowerApps
2. **Improve User Experience**: Enhance with modern React patterns and responsive design
3. **Progressive Enhancement**: Start with basic CRUD operations, add advanced features incrementally

### Component Mapping

| PowerApps Element | React Implementation |
|-------------------|---------------------|
| Gallery/List View | Table component with search/filter |
| Form | Controlled form components |
| Lookup fields | Select/Autocomplete components |
| Status choices | Badge/Chip components |
| Navigation | React Router routes |

### Data Flow

```
PowerApps Canvas App → React Screens
↓                      ↓
Dataverse            Django REST API
↓                      ↓
Direct queries       HTTP requests via services
```

## Development Best Practices

### Code Organization
- Group related components together
- Use index files for clean imports
- Separate business logic from UI components
- Create custom hooks for reusable logic

### Performance
- Use React.memo for expensive components
- Implement virtual scrolling for large lists
- Lazy load screens with React.lazy
- Optimize API requests with caching

### Accessibility
- Use semantic HTML elements
- Add ARIA labels for screen readers
- Ensure keyboard navigation support
- Maintain proper color contrast

### Error Handling
- Implement error boundaries for component errors
- Show user-friendly error messages
- Log errors for debugging
- Provide retry mechanisms

## Troubleshooting

### Common Issues

1. **CORS errors with Django backend:**
   ```bash
   # Ensure CORS_ALLOWED_ORIGINS includes frontend URL
   # Check Django settings.py
   ```

2. **TypeScript compilation errors:**
   ```bash
   # Check tsconfig.json configuration
   # Ensure all imports have proper types
   npm run type-check
   ```

3. **API connection issues:**
   ```bash
   # Verify backend is running on port 8000
   # Check REACT_APP_API_BASE_URL in .env.local
   curl http://localhost:8000/api/v1/accounts-receivables/
   ```

4. **Styling issues:**
   ```bash
   # Clear browser cache
   # Check styled-components version compatibility
   ```

### Development Tools

#### Browser Extensions
- React Developer Tools
- Redux DevTools (if using Redux)
- Axe accessibility checker

#### VS Code Extensions
- ES7+ React/Redux/React-Native snippets
- TypeScript Importer
- Auto Rename Tag
- Prettier - Code formatter

## Next Steps

1. **Add remaining entity screens** (Suppliers, Customers, etc.)
2. **Implement authentication** with Django backend
3. **Add comprehensive testing** with Jest and React Testing Library
4. **Optimize performance** with React Query or SWR
5. **Enhance UX** with loading states and optimistic updates
6. **Add offline support** with service workers

For more information, see the main [README.md](../README.md) and [API Reference](api_reference.md).