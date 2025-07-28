# GitHub Copilot Setup and Usage Guide for ProjectMeats

## Overview
This guide explains how to effectively use GitHub Copilot with the ProjectMeats application. The project has been configured with custom instructions, VS Code settings, and MCP (Model Context Protocol) servers to make Copilot smarter and more context-aware.

## 🚀 Quick Setup

### 1. Prerequisites
- **VS Code** with GitHub Copilot extension installed
- **GitHub Copilot subscription** (individual or business)
- **Node.js 16+** for MCP servers
- **Python 3.9+** and **Django** environment

### 2. Open the Project
```bash
# Open with VS Code workspace (recommended)
code ProjectMeats.code-workspace

# Or open the folder directly
code .
```

### 3. Install Recommended Extensions
VS Code will prompt you to install recommended extensions. Click "Install All" for the best experience:
- GitHub Copilot
- GitHub Copilot Chat
- Python extensions
- TypeScript/React extensions
- Django extensions

## 📋 Configuration Files

### GitHub Copilot Instructions
- **Location**: `.github/copilot-instructions.md`
- **Purpose**: Provides project context, coding patterns, and best practices to Copilot
- **Content**: Django/React patterns, PowerApps migration guidelines, security considerations

### VS Code Workspace
- **Location**: `ProjectMeats.code-workspace`
- **Purpose**: Multi-folder workspace with optimized settings for backend/frontend development
- **Features**: 
  - Separate Python interpreter configuration
  - Integrated debugging configurations
  - Build and test tasks
  - Code formatting on save

### MCP Configuration
- **Location**: `.mcp-config.json`
- **Purpose**: Configures Model Context Protocol servers for enhanced AI context
- **Servers**:
  - **Filesystem**: Provides file system access
  - **SQLite**: Database query capabilities
  - **Git**: Repository history and branch information

## 🛠️ Using Copilot Effectively

### 1. Copilot Chat Commands

#### Project-Specific Prompts
```
@workspace How do I migrate a new PowerApps entity to Django?
@workspace Show me the pattern for creating a new React component
@workspace What's the current migration status?
@workspace How do I add a new API endpoint following the project patterns?
```

#### Code Generation
```
# Generate a Django model
Create a Django model for Supplier entity following the ProjectMeats patterns with PowerApps field mappings

# Generate a React component
Create a React TypeScript component for managing suppliers with CRUD operations

# Generate API tests
Create pytest tests for the AccountsReceivable ViewSet following existing patterns
```

### 2. Context-Aware Development

#### Django Backend
When working in the backend folder, Copilot will understand:
- Django REST Framework patterns
- PowerApps migration context
- Existing model inheritance (`OwnedModel`, `StatusModel`)
- API serialization patterns
- Testing patterns with pytest

#### React Frontend
When working in the frontend folder, Copilot will understand:
- TypeScript React patterns
- Styled-components usage
- API service integration
- Component structure and organization
- Testing with Jest/React Testing Library

### 3. Code Completion Examples

#### Django Model Generation
```python
# Type this comment and let Copilot generate:
# Create a Supplier model migrated from PowerApps cr7c4_supplier
```

#### React Component Generation
```tsx
// Type this comment and let Copilot generate:
// Create a SuppliersScreen component with CRUD operations
```

#### API Service Generation
```typescript
// Type this comment and let Copilot generate:
// Create supplierService with CRUD operations following existing patterns
```

## 🔍 Advanced Features

### 1. MCP Server Integration

#### Database Queries
```
@workspace Query the database to show me all accounts receivables
@workspace What's the structure of the AccountsReceivable table?
```

#### File System Operations
```
@workspace Find all Python files with 'supplier' in the name
@workspace Show me the migration files for accounts_receivables app
```

#### Git History
```
@workspace What recent changes were made to the frontend components?
@workspace Show me the commit history for the accounts_receivables models
```

### 2. Debugging with Copilot

#### Error Analysis
```
@workspace I'm getting a Django migration error, help me fix it
@workspace This React component isn't rendering correctly, what's wrong?
@workspace The API is returning 500 errors, help me debug
```

#### Performance Optimization
```
@workspace How can I optimize this Django query?
@workspace This React component is re-rendering too much, how to fix?
@workspace Suggest performance improvements for this API endpoint
```

### 3. Testing Assistance

#### Test Generation
```
@workspace Generate unit tests for the AccountsReceivable model
@workspace Create integration tests for the supplier API endpoints
@workspace Generate React component tests using Testing Library
```

#### Test Debugging
```
@workspace This test is failing, help me understand why
@workspace How do I mock this API call in my React test?
@workspace Suggest test cases I might be missing for this component
```

## 📚 Best Practices

### 1. Provide Context
- Always mention you're working on ProjectMeats
- Specify if you're migrating from PowerApps
- Mention the specific entity or component you're working on

### 2. Use Project Terminology
- **Entities**: Refer to business objects (Supplier, Customer, etc.)
- **Migration**: PowerApps to Django/React conversion
- **ViewSets**: Django REST Framework API endpoints
- **Screens**: React components that represent full pages

### 3. Follow Existing Patterns
- Always ask Copilot to follow existing patterns
- Reference the accounts_receivables app as an example
- Maintain consistency with PowerApps field mappings

### 4. Security Considerations
- Always ask for input validation
- Request proper authentication checks
- Ensure sensitive data protection

## 🐛 Troubleshooting

### Common Issues

#### Copilot Not Understanding Project Context
```bash
# Reload VS Code window
Ctrl+Shift+P -> "Developer: Reload Window"

# Check if custom instructions are loaded
Ctrl+Shift+P -> "GitHub Copilot: Check Status"
```

#### MCP Servers Not Working
```bash
# Install MCP servers if needed
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-sqlite
npm install -g @modelcontextprotocol/server-git
```

#### VS Code Extensions Issues
```bash
# Reinstall GitHub Copilot
Ctrl+Shift+X -> Search "GitHub Copilot" -> Reinstall
```

### Getting Better Suggestions

#### Be Specific
```
# Instead of: "Create a model"
# Use: "Create a Django model for Supplier entity following ProjectMeats patterns with PowerApps field mappings"
```

#### Provide Examples
```
# Use: "Create a React component similar to AccountsReceivablesScreen but for suppliers"
```

#### Reference Documentation
```
# Use: "Following the patterns in docs/migration_mapping.md, create..."
```

## 📖 Additional Resources

### Project Documentation
- [Setup Overview](../SETUP_OVERVIEW.md) - Complete project setup guide
- [Migration Mapping](migration_mapping.md) - PowerApps to Django mappings
- [API Reference](api_reference.md) - Complete API documentation
- [Agent Quick Start](agent_quick_start.md) - Development workflow guide

### GitHub Copilot Resources
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [VS Code Copilot Guide](https://code.visualstudio.com/docs/editor/github-copilot)
- [Copilot Chat Commands](https://docs.github.com/en/copilot/github-copilot-chat/using-github-copilot-chat-in-your-ide)

### Model Context Protocol
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)

## 🔄 Updates and Maintenance

### Keeping Configurations Updated
1. **Custom Instructions**: Update `.github/copilot-instructions.md` when adding new patterns or entities
2. **VS Code Settings**: Modify `.vscode/settings.json` for new development tools or preferences
3. **MCP Configuration**: Update `.mcp-config.json` when adding new data sources or servers

### Regular Tasks
- Review and update Copilot instructions monthly
- Test MCP server connections after major updates
- Update VS Code extensions regularly
- Share effective prompts with the team

---

**Need Help?** Check the project documentation or create an issue for questions about using Copilot with ProjectMeats.