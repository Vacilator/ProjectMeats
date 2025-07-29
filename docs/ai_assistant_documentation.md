# ProjectMeats AI Assistant - Comprehensive Documentation

## 🤖 Overview

The ProjectMeats AI Assistant is an intelligent chatbot feature similar to Microsoft Copilot, specifically designed for meat market operations. It provides intuitive document processing, business intelligence, and workflow automation capabilities.

## ✨ Key Features

### 🗣️ **Conversational AI Interface**
- **Microsoft Copilot-style Chat Experience**: Modern, intuitive chat interface with message bubbles and real-time interactions
- **Context-Aware Responses**: AI understands meat industry terminology and business processes
- **Session Management**: Multiple conversation threads with persistent history
- **Real-time Typing Indicators**: Visual feedback during AI response generation

### 📄 **Intelligent Document Processing**
- **Drag-and-Drop Upload**: Easy file upload with validation and progress tracking
- **Multi-Format Support**: PDF, Word, Excel, images (JPG, PNG), and text files
- **Automatic Classification**: AI identifies document types (purchase orders, invoices, contracts, etc.)
- **Data Extraction**: Intelligent extraction of key business information

### 🔧 **Business Automation**
- **Entity Creation**: Automatically create suppliers, customers, purchase orders from documents
- **Document Analysis**: Extract dates, amounts, parties, and product details
- **Workflow Integration**: Seamless integration with existing business processes
- **Audit Trail**: Complete tracking of AI actions and entity creation

## 🏗️ Architecture

### Backend Components

#### 1. **Django AI Assistant App** (`apps/ai_assistant/`)
```
apps/ai_assistant/
├── models.py              # Core data models
├── serializers.py         # API serialization
├── views.py              # REST API endpoints
├── admin.py              # Django admin interface
├── services/
│   ├── ai_service.py     # AI provider integration
│   ├── document_processor.py # Document processing
│   └── entity_extractor.py   # Business entity extraction
├── tests.py              # Comprehensive test suite
└── urls.py               # API routing
```

#### 2. **Core Models**
- **ChatSession**: Conversation management with context tracking
- **ChatMessage**: Individual messages with type classification (user/assistant/system/document)
- **UploadedDocument**: File storage with processing status and extracted data
- **AIConfiguration**: Flexible AI provider configuration (OpenAI, Azure, Anthropic)
- **ProcessingTask**: Background task tracking for document processing

#### 3. **AI Service Layer**
- **Pluggable Architecture**: Support for multiple AI providers
- **Mock Provider**: Development-friendly testing without API keys
- **OpenAI Integration**: Production-ready OpenAI API integration
- **Custom Prompts**: Meat industry-specific prompt engineering

### Frontend Components

#### 1. **React Chat Interface** (`src/components/ChatInterface/`)
```
ChatInterface/
├── ChatWindow.tsx        # Main chat container
├── MessageList.tsx       # Message display with types
├── MessageInput.tsx      # Input with suggestions
├── DocumentUpload.tsx    # Drag-drop file upload
├── SessionsList.tsx      # Conversation history
└── index.ts             # Component exports
```

#### 2. **Services & Types**
- **aiService.ts**: API communication layer with error handling
- **Type Definitions**: Comprehensive TypeScript interfaces
- **Utility Functions**: File formatting, time display, status indicators

#### 3. **Screen Integration**
- **AIAssistantScreen.tsx**: Split-pane layout with sidebar toggle
- **Navigation Integration**: Added to main application menu
- **Responsive Design**: Mobile-friendly interface

## 📚 API Reference

### Chat Endpoints

#### Start New Chat Session
```http
POST /api/v1/ai-assistant/sessions/start_session/
Content-Type: application/json

{
  "message": "Hello, I need help with purchase orders",
  "title": "Purchase Order Help"
}
```

**Response:**
```json
{
  "session": {
    "id": "uuid",
    "title": "Purchase Order Help",
    "session_status": "active",
    "message_count": 2,
    "has_documents": false
  },
  "user_message": { /* ChatMessage object */ },
  "ai_response": { /* ChatMessage object */ }
}
```

#### Send Message
```http
POST /api/v1/ai-assistant/chat/chat/
Content-Type: application/json

{
  "message": "Can you help me process this invoice?",
  "session_id": "existing-session-uuid"
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you process that invoice...",
  "session_id": "session-uuid",
  "message_id": "message-uuid",
  "processing_time": 1.23,
  "metadata": {
    "model": "mock-gpt-3.5",
    "usage": { "prompt_tokens": 50, "completion_tokens": 100 }
  }
}
```

### Document Processing

#### Upload Document
```http
POST /api/v1/ai-assistant/documents/
Content-Type: multipart/form-data

file: [binary file data]
original_filename: "purchase_order_123.pdf"
```

**Response:**
```json
{
  "id": "doc-uuid",
  "original_filename": "purchase_order_123.pdf",
  "file_size": 1048576,
  "file_size_mb": 1.0,
  "document_type": "purchase_order",
  "processing_status": "processing",
  "confidence_score": 0.92
}
```

#### Process Document
```http
POST /api/v1/ai-assistant/chat/process_document/
Content-Type: application/json

{
  "document_id": "doc-uuid",
  "session_id": "session-uuid"
}
```

### Session Management

#### List Sessions
```http
GET /api/v1/ai-assistant/sessions/
```

#### Get Session Messages
```http
GET /api/v1/ai-assistant/sessions/{session_id}/messages/
```

## 🛠️ Configuration

### AI Provider Setup

#### 1. **Mock Provider** (Default - No API Key Required)
```python
# Settings already configured for development
AI_CONFIG = "default_mock"
```

#### 2. **OpenAI Provider**
```bash
# Environment variables
export OPENAI_API_KEY="your-api-key-here"
```

```python
# Create configuration via Django admin or shell
from apps.ai_assistant.models import AIConfiguration

AIConfiguration.objects.create(
    name="OpenAI GPT-4",
    provider="openai",
    model_name="gpt-4",
    api_key_name="OPENAI_API_KEY",
    configuration={
        "temperature": 0.7,
        "max_tokens": 2000
    },
    is_default=True
)
```

#### 3. **Azure OpenAI Provider**
```bash
# Environment variables
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

### File Upload Configuration

#### Supported File Types
- **Documents**: PDF, Word (.doc, .docx), Excel (.xls, .xlsx), Text (.txt)
- **Images**: JPG, JPEG, PNG
- **Maximum Size**: 10MB (configurable)

#### Security Settings
```python
# File validation in DocumentUpload component
ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'txt', 'doc', 'docx', 'xls', 'xlsx']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

## 🚀 Getting Started

### 1. **Access the AI Assistant**
- Navigate to the AI Assistant from the main navigation menu (🤖 AI Assistant)
- The interface will open with a welcome screen and suggested prompts

### 2. **Start a Conversation**
- Click on a suggested prompt or type your own message
- Example: "Help me process a purchase order"
- The AI will respond with industry-specific guidance

### 3. **Upload Documents**
- Use the drag-and-drop area or click to browse
- Supported formats: PDF, Word, Excel, images, text files
- AI will automatically analyze and classify the document

### 4. **Document Processing Workflow**
1. **Upload** → Document is uploaded and validated
2. **Analysis** → AI classifies document type and extracts text
3. **Processing** → Key business data is identified and structured
4. **Entity Creation** → Suppliers, customers, orders can be automatically created
5. **Review** → User can review and approve extracted information

## 📋 Use Cases

### 1. **Purchase Order Processing**
```
User: "I have a purchase order from ABC Meat Suppliers"
Assistant: "I can help you process that purchase order. Please upload 
the document and I'll extract the supplier information, product details, 
quantities, and pricing to create the order in your system."
```

### 2. **Invoice Analysis**
```
User: [Uploads invoice PDF]
Assistant: "I've identified this as an invoice from XYZ Processing Plant. 
Here's what I found:
- Invoice Number: INV-2025-001
- Total Amount: $2,450.00
- Due Date: February 15, 2025
- Products: Ground Beef (500 lbs), Ribeye Steaks (100 lbs)

Would you like me to create an accounts receivable record?"
```

### 3. **Supplier Information Management**
```
User: "Tell me about our relationship with Premium Beef Co"
Assistant: "Based on your records, Premium Beef Co is an active supplier with:
- 15 purchase orders in the last 6 months
- Average order value: $3,200
- Last delivery: January 20, 2025
- Contact: Mike Johnson (mike@premiumbeef.com)

They have excellent delivery performance and competitive pricing on ribeye cuts."
```

### 4. **Business Intelligence Queries**
```
User: "What are our top performing suppliers this quarter?"
Assistant: "Here are your top 5 suppliers by volume this quarter:

1. Midwest Cattle Ranch - $125,000 (45 orders)
2. Premium Beef Co - $98,000 (32 orders)  
3. Local Farm Collective - $67,000 (28 orders)
4. Regional Processing - $54,000 (19 orders)
5. Quality Meats LLC - $43,000 (15 orders)

Midwest Cattle Ranch has shown 15% growth compared to last quarter."
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test apps.ai_assistant
```

**Test Coverage Includes:**
- Model creation and validation
- API endpoint functionality
- AI service integration
- Document processing workflow
- Error handling scenarios

### Frontend Testing
```bash
cd frontend
npm test
```

## 🔒 Security Considerations

### 1. **File Upload Security**
- File type validation (whitelist approach)
- File size limits (10MB default)
- Virus scanning (recommended for production)
- Secure file storage with access controls

### 2. **Data Privacy**
- User-scoped access (users only see their own sessions)
- No sensitive data logged in AI requests
- Optional data encryption for stored documents
- GDPR compliance considerations

### 3. **AI Provider Security**
- API key rotation support
- Request rate limiting
- Error message sanitization
- Audit logging for AI interactions

## 📈 Performance Optimization

### 1. **Database Optimization**
- Strategic indexes on frequently queried fields
- Pagination for large datasets
- Efficient query patterns with select_related/prefetch_related

### 2. **Frontend Performance**
- Code splitting for AI components
- Lazy loading of chat history
- Optimized image processing for documents
- Debounced search and filtering

### 3. **AI Response Optimization**
- Response caching for common queries
- Streaming responses for long AI outputs
- Background processing for document analysis
- Connection pooling for API requests

## 🔧 Troubleshooting

### Common Issues

#### 1. **AI Not Responding**
- Check AI configuration in Django admin
- Verify API keys in environment variables
- Ensure mock provider is configured for development
- Check backend logs for API errors

#### 2. **File Upload Failures**
- Verify file type is supported
- Check file size (10MB limit)
- Ensure sufficient disk space
- Review upload permissions

#### 3. **Session Loading Issues**
- Clear browser cache/localStorage
- Check network connectivity
- Verify user authentication
- Review backend API status

### Debug Mode
```bash
# Enable debug logging
export DEBUG=True
export LOG_LEVEL=DEBUG

# Backend logs
tail -f backend/debug.log

# Frontend console
# Open browser dev tools → Console tab
```

## 🔮 Future Enhancements

### Phase 3: Enhanced Document Processing
- [ ] Advanced OCR for scanned documents
- [ ] Multi-language document support
- [ ] Custom document templates
- [ ] Batch document processing

### Phase 4: Advanced AI Features
- [ ] Voice interaction support
- [ ] Predictive analytics and recommendations
- [ ] Custom AI model training
- [ ] Integration with external market data

### Phase 5: Enterprise Features
- [ ] Multi-tenant support
- [ ] Advanced audit and compliance
- [ ] Workflow automation builder
- [ ] Custom integration APIs

## 📞 Support

### For Users
- Use the built-in help system in the AI Assistant
- Check the suggested prompts for common tasks
- Review error messages for specific guidance

### For Developers
- Comprehensive API documentation at `/api/docs/`
- TypeScript definitions for all interfaces
- Example code in component documentation
- Test cases for reference implementations

### For Administrators
- Django admin interface for configuration
- Monitoring dashboards for usage analytics
- Performance metrics and optimization guides
- Security best practices documentation

---

**Ready to revolutionize your meat market operations with AI?** Start by navigating to the AI Assistant in your ProjectMeats application and try uploading a business document or asking about your suppliers!