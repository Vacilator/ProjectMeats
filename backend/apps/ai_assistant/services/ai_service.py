"""
AI Service Layer for ProjectMeats AI Assistant.

This module provides a pluggable architecture for integrating with various
AI providers (OpenAI, Azure OpenAI, Anthropic, etc.) for chat responses
and document processing in the meat market business context.
"""
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
from django.conf import settings
from django.utils import timezone
from ..models import AIConfiguration, ChatMessage, MessageTypeChoices

logger = logging.getLogger(__name__)


class AIProviderInterface(ABC):
    """Abstract interface for AI providers."""
    
    @abstractmethod
    def generate_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate AI response for conversation."""
        pass
    
    @abstractmethod
    def extract_entities(self, text: str, **kwargs) -> Dict[str, Any]:
        """Extract business entities from text."""
        pass
    
    @abstractmethod
    def classify_document(self, text: str, **kwargs) -> Dict[str, Any]:
        """Classify document type and extract key information."""
        pass


class MockAIProvider(AIProviderInterface):
    """
    Mock AI provider for development and testing.
    
    Provides realistic responses without requiring external API keys.
    """
    
    def __init__(self, config: AIConfiguration):
        self.config = config
        self.model_name = config.model_name
    
    def generate_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate mock AI response."""
        user_message = messages[-1].get('content', '') if messages else ''
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Generate context-aware responses for meat industry
        response = self._generate_mock_response(user_message)
        
        return {
            'response': response,
            'usage': {
                'prompt_tokens': len(user_message.split()) * 2,
                'completion_tokens': len(response.split()),
                'total_tokens': len(user_message.split()) * 2 + len(response.split())
            },
            'model': self.model_name,
            'finish_reason': 'stop'
        }
    
    def extract_entities(self, text: str, **kwargs) -> Dict[str, Any]:
        """Extract mock entities from text."""
        entities = {
            'suppliers': [],
            'customers': [],
            'products': [],
            'dates': [],
            'amounts': [],
            'purchase_orders': [],
            'confidence': 0.85
        }
        
        # Simple keyword-based extraction for demo
        text_lower = text.lower()
        
        # Extract potential suppliers
        supplier_keywords = ['supplier', 'vendor', 'farm', 'ranch', 'meat co', 'processing']
        for keyword in supplier_keywords:
            if keyword in text_lower:
                entities['suppliers'].append({
                    'name': f"Mock {keyword.title()} Inc",
                    'confidence': 0.8
                })
        
        # Extract potential products
        meat_products = ['beef', 'pork', 'chicken', 'lamb', 'turkey', 'veal']
        for product in meat_products:
            if product in text_lower:
                entities['products'].append({
                    'name': product.title(),
                    'type': 'meat_product',
                    'confidence': 0.9
                })
        
        # Extract amounts (simple regex simulation)
        import re
        amounts = re.findall(r'\$[\d,]+\.?\d*', text)
        for amount in amounts:
            entities['amounts'].append({
                'value': amount,
                'currency': 'USD',
                'confidence': 0.95
            })
        
        return entities
    
    def classify_document(self, text: str, **kwargs) -> Dict[str, Any]:
        """Classify document type based on content."""
        text_lower = text.lower()
        
        # Simple classification logic
        if any(word in text_lower for word in ['purchase order', 'po number', 'order date']):
            return {
                'document_type': 'purchase_order',
                'confidence': 0.92,
                'key_fields': {
                    'po_number': 'PO-2025-001',
                    'order_date': '2025-01-28',
                    'supplier': 'Mock Supplier Inc'
                }
            }
        elif any(word in text_lower for word in ['invoice', 'bill', 'amount due']):
            return {
                'document_type': 'invoice',
                'confidence': 0.88,
                'key_fields': {
                    'invoice_number': 'INV-2025-001',
                    'total_amount': '$1,250.00',
                    'due_date': '2025-02-15'
                }
            }
        else:
            return {
                'document_type': 'unknown',
                'confidence': 0.60,
                'key_fields': {}
            }
    
    def _generate_mock_response(self, user_message: str) -> str:
        """Generate contextual mock responses."""
        message_lower = user_message.lower()
        
        # Greeting responses
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey']):
            return (
                "Hello! I'm your AI assistant for ProjectMeats. I can help you with:\n\n"
                "• Processing purchase orders and invoices\n"
                "• Managing supplier and customer information\n"
                "• Analyzing meat market data\n"
                "• Document classification and data extraction\n\n"
                "How can I assist you today?"
            )
        
        # Document processing queries
        elif any(word in message_lower for word in ['document', 'upload', 'process']):
            return (
                "I can help you process various business documents! Simply upload:\n\n"
                "📋 **Purchase Orders** - I'll extract supplier, product, and pricing information\n"
                "🧾 **Invoices** - I'll identify amounts, due dates, and payment terms\n"
                "📄 **Contracts** - I'll extract key terms and dates\n"
                "📊 **Supplier Documents** - I'll organize contact and capability information\n\n"
                "Just drag and drop your files or use the upload button, and I'll automatically "
                "identify the document type and extract relevant data to create records in your system."
            )
        
        # Purchase order queries
        elif any(word in message_lower for word in ['purchase order', 'po', 'order']):
            return (
                "I can help you manage purchase orders efficiently:\n\n"
                "• **Create POs** from uploaded documents\n"
                "• **Track order status** and fulfillment dates\n"
                "• **Manage supplier relationships** and pricing\n"
                "• **Generate reports** on order volumes and spending\n\n"
                "Would you like me to process a purchase order document or help you create a new order?"
            )
        
        # Supplier management
        elif any(word in message_lower for word in ['supplier', 'vendor']):
            return (
                "I can assist with comprehensive supplier management:\n\n"
                "🏢 **Supplier Profiles** - Contact info, capabilities, certifications\n"
                "📍 **Location Management** - Plants, warehouses, distribution centers\n"
                "💰 **Financial Tracking** - Credit applications, payment terms\n"
                "📊 **Performance Analytics** - Delivery times, quality metrics\n\n"
                "What specific supplier information do you need help with?"
            )
        
        # General help
        elif any(word in message_lower for word in ['help', 'what can you do']):
            return (
                "I'm your intelligent assistant for meat market operations! Here's what I can do:\n\n"
                "🤖 **Smart Document Processing**\n"
                "• Automatically identify document types (POs, invoices, contracts)\n"
                "• Extract key business data (dates, amounts, parties)\n"
                "• Create database records from documents\n\n"
                "📊 **Business Intelligence**\n"
                "• Answer questions about your data\n"
                "• Generate insights on suppliers, customers, and orders\n"
                "• Provide meat market industry guidance\n\n"
                "⚡ **Workflow Automation**\n"
                "• Streamline order processing\n"
                "• Manage supplier and customer relationships\n"
                "• Track plant operations and logistics\n\n"
                "Try uploading a document or ask me about your business operations!"
            )
        
        # Default response
        else:
            return (
                "I understand you're asking about meat market operations. I'm here to help with:\n\n"
                "• Document processing and data extraction\n"
                "• Purchase order and invoice management\n"
                "• Supplier and customer relationship management\n"
                "• Plant operations and logistics coordination\n\n"
                "Could you provide more specific details about what you'd like to accomplish? "
                "Or feel free to upload a document for me to process!"
            )


class OpenAIProvider(AIProviderInterface):
    """OpenAI provider implementation."""
    
    def __init__(self, config: AIConfiguration):
        self.config = config
        self.api_key = self._get_api_key()
        self.model_name = config.model_name
        
        # Import OpenAI client if available
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            logger.warning("OpenAI library not installed. Using mock responses.")
            self.client = None
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables."""
        if self.config.api_key_name:
            return getattr(settings, self.config.api_key_name, None)
        return getattr(settings, 'OPENAI_API_KEY', None)
    
    def generate_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        if not self.client:
            # Fallback to mock if OpenAI not available
            mock_provider = MockAIProvider(self.config)
            return mock_provider.generate_response(messages, **kwargs)
        
        try:
            # Add system message for meat industry context
            system_message = {
                "role": "system",
                "content": self._get_system_prompt()
            }
            
            # Prepare messages
            api_messages = [system_message] + messages
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=api_messages,
                **self.config.configuration
            )
            
            return {
                'response': response.choices[0].message.content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'model': response.model,
                'finish_reason': response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            # Fallback to mock on error
            mock_provider = MockAIProvider(self.config)
            return mock_provider.generate_response(messages, **kwargs)
    
    def extract_entities(self, text: str, **kwargs) -> Dict[str, Any]:
        """Extract entities using OpenAI."""
        if not self.client:
            mock_provider = MockAIProvider(self.config)
            return mock_provider.extract_entities(text, **kwargs)
        
        # Implementation would use OpenAI for entity extraction
        # For now, fallback to mock
        mock_provider = MockAIProvider(self.config)
        return mock_provider.extract_entities(text, **kwargs)
    
    def classify_document(self, text: str, **kwargs) -> Dict[str, Any]:
        """Classify document using OpenAI."""
        if not self.client:
            mock_provider = MockAIProvider(self.config)
            return mock_provider.classify_document(text, **kwargs)
        
        # Implementation would use OpenAI for document classification
        # For now, fallback to mock
        mock_provider = MockAIProvider(self.config)
        return mock_provider.classify_document(text, **kwargs)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for meat industry context."""
        return """
You are an AI assistant specialized in meat market operations and business management. 
You help with:

1. Document Processing: Purchase orders, invoices, contracts, supplier documents
2. Business Operations: Supplier management, customer relationships, plant operations
3. Data Analysis: Market trends, pricing, logistics, quality control
4. Regulatory Compliance: Food safety, traceability, certifications

Provide helpful, accurate responses focused on meat industry best practices. 
When processing documents, extract key business data like dates, amounts, parties, and product details.
Be professional and industry-appropriate in your responses.
"""


class AIService:
    """
    Main AI service class that provides a unified interface to different AI providers.
    
    Handles provider selection, configuration management, and response formatting.
    """
    
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider,
            'azure_openai': OpenAIProvider,  # Could be separate implementation
            'anthropic': MockAIProvider,      # Would be Anthropic implementation
            'local': MockAIProvider,          # Would be local model implementation
        }
    
    def get_default_config(self) -> Optional[AIConfiguration]:
        """Get the default AI configuration."""
        try:
            return AIConfiguration.objects.filter(
                is_active=True, 
                is_default=True
            ).first()
        except Exception as e:
            logger.error(f"Error getting default AI config: {str(e)}")
            return None
    
    def get_provider(self, config: Optional[AIConfiguration] = None) -> AIProviderInterface:
        """Get AI provider instance based on configuration."""
        if not config:
            config = self.get_default_config()
        
        if not config:
            # Create default mock configuration
            config = AIConfiguration(
                name="default_mock",
                provider="local",
                model_name="mock-model",
                configuration={}
            )
        
        provider_class = self.providers.get(config.provider, MockAIProvider)
        return provider_class(config)
    
    def generate_chat_response(
        self, 
        user_message: str, 
        session_messages: List[ChatMessage] = None,
        **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate AI response for chat conversation.
        
        Args:
            user_message: User's input message
            session_messages: Previous messages in the session
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (response_text, metadata)
        """
        start_time = time.time()
        
        try:
            # Get AI provider
            provider = self.get_provider()
            
            # Prepare conversation history
            messages = []
            if session_messages:
                for msg in session_messages[-10:]:  # Last 10 messages for context
                    if msg.message_type == MessageTypeChoices.USER:
                        messages.append({"role": "user", "content": msg.content})
                    elif msg.message_type == MessageTypeChoices.ASSISTANT:
                        messages.append({"role": "assistant", "content": msg.content})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            result = provider.generate_response(messages, **kwargs)
            
            processing_time = time.time() - start_time
            
            # Prepare metadata
            metadata = {
                'provider': provider.config.provider if hasattr(provider, 'config') else 'mock',
                'model': result.get('model', 'unknown'),
                'processing_time': processing_time,
                'usage': result.get('usage', {}),
                'finish_reason': result.get('finish_reason', 'unknown')
            }
            
            return result['response'], metadata
            
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            
            # Fallback response
            processing_time = time.time() - start_time
            fallback_response = (
                "I apologize, but I am experiencing technical difficulties right now. "
                "Please try again in a moment, or contact support if the issue persists."
            )
            
            metadata = {
                'provider': 'fallback',
                'model': 'error',
                'processing_time': processing_time,
                'error': str(e)
            }
            
            return fallback_response, metadata
    
    def extract_document_entities(self, text: str, **kwargs) -> Dict[str, Any]:
        """Extract business entities from document text."""
        try:
            provider = self.get_provider()
            return provider.extract_entities(text, **kwargs)
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {'error': str(e), 'entities': {}}
    
    def classify_document_type(self, text: str, **kwargs) -> Dict[str, Any]:
        """Classify document type and extract key information."""
        try:
            provider = self.get_provider()
            return provider.classify_document(text, **kwargs)
        except Exception as e:
            logger.error(f"Error classifying document: {str(e)}")
            return {
                'document_type': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }


# Global AI service instance
ai_service = AIService()