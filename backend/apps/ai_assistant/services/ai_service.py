"""
AI Service Layer for ProjectMeats AI Assistant.

This module provides a pluggable architecture for integrating with various
AI providers (OpenAI, Azure OpenAI, Anthropic, etc.) for chat responses
and document processing in the meat market business context.
"""
import json
import time
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
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
        """Extract enhanced entities from text with meat industry focus."""
        entities = {
            'suppliers': [],
            'customers': [],
            'products': [],
            'quantities': [],
            'prices': [],
            'dates': [],
            'locations': [],
            'certifications': [],
            'purchase_orders': [],
            'invoice_numbers': [],
            'contact_info': [],
            'quality_metrics': [],
            'confidence': 0.85
        }
        
        # Simple keyword-based extraction for demo with enhanced patterns
        text_lower = text.lower()
        
        # Extract potential suppliers with more sophisticated patterns
        supplier_patterns = [
            r'([A-Z][a-z]+ (?:Beef|Pork|Meat|Farm|Ranch|Processing|Suppliers?|Inc|LLC|Corp|Co\.?))',
            r'([A-Z][a-z]+ [A-Z][a-z]+ (?:Farms?|Ranches?|Meat|Processing))',
            r'((?:Prime|Quality|Fresh|Local|Regional|Global) [A-Z][a-z]+ (?:Suppliers?|Distributors?))',
        ]
        
        import re
        for pattern in supplier_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entities['suppliers'].append({
                    'name': match,
                    'confidence': 0.85,
                    'extracted_from': 'pattern_matching'
                })
        
        # Extract meat products with quantities and grades
        meat_products = {
            'beef': ['ground beef', 'ribeye', 'sirloin', 'chuck', 'brisket', 'prime rib'],
            'pork': ['pork chops', 'bacon', 'ham', 'sausage', 'pork belly', 'tenderloin'],
            'chicken': ['whole chicken', 'chicken breast', 'chicken thighs', 'wings'],
            'lamb': ['lamb chops', 'leg of lamb', 'lamb shoulder'],
            'turkey': ['whole turkey', 'turkey breast', 'ground turkey'],
            'seafood': ['salmon', 'shrimp', 'lobster', 'crab', 'tuna']
        }
        
        for category, products in meat_products.items():
            for product in products:
                if product in text_lower:
                    # Look for quantities nearby
                    quantity_pattern = rf'(\d+(?:\.\d+)?)\s*(?:lbs?|pounds?|kg|kilograms?|tons?)?\s*(?:of\s+)?{re.escape(product)}'
                    quantity_matches = re.findall(quantity_pattern, text_lower)
                    
                    for qty in quantity_matches:
                        entities['quantities'].append({
                            'product': product.title(),
                            'quantity': qty,
                            'category': category,
                            'confidence': 0.90
                        })
                    
                    entities['products'].append({
                        'name': product.title(),
                        'category': category,
                        'confidence': 0.90
                    })
        
        # Extract prices with currency
        price_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,234.56
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD)',  # 1,234.56 dollars
            r'(\d+(?:\.\d{2})?)\s*/\s*(?:lb|pound|kg)',  # 5.99/lb
        ]
        
        for pattern in price_patterns:
            amounts = re.findall(pattern, text, re.IGNORECASE)
            for amount in amounts:
                entities['prices'].append({
                    'amount': amount,
                    'currency': 'USD',
                    'confidence': 0.95
                })
        
        # Extract dates with multiple formats
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY-MM-DD
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',  # January 15, 2024
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            for date in dates:
                entities['dates'].append({
                    'date': date,
                    'format': 'detected',
                    'confidence': 0.90
                })
        
        # Extract purchase order numbers
        po_patterns = [
            r'(?:PO|Purchase Order|Order)\s*#?\s*([A-Z0-9-]+)',
            r'(\d{4,}-\d{3,})',  # Pattern like 2024-001
        ]
        
        for pattern in po_patterns:
            pos = re.findall(pattern, text, re.IGNORECASE)
            for po in pos:
                entities['purchase_orders'].append({
                    'po_number': po,
                    'confidence': 0.85
                })
        
        # Extract invoice numbers
        invoice_patterns = [
            r'(?:Invoice|INV)\s*#?\s*([A-Z0-9-]+)',
            r'(?:Bill|Receipt)\s*#?\s*([A-Z0-9-]+)',
        ]
        
        for pattern in invoice_patterns:
            invoices = re.findall(pattern, text, re.IGNORECASE)
            for inv in invoices:
                entities['invoice_numbers'].append({
                    'invoice_number': inv,
                    'confidence': 0.85
                })
        
        # Extract locations (cities, states, addresses)
        location_patterns = [
            r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road))',  # Street addresses
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, ST
            r'([A-Z][a-z]+\s+[A-Z][a-z]+,\s*[A-Z]{2})',  # City Name, ST
        ]
        
        for pattern in location_patterns:
            locations = re.findall(pattern, text)
            for location in locations:
                entities['locations'].append({
                    'location': location,
                    'type': 'address',
                    'confidence': 0.80
                })
        
        # Extract certifications and compliance info
        certification_keywords = [
            'USDA', 'FDA', 'HACCP', 'SQF', 'BRC', 'ISO', 'Organic', 'Halal', 'Kosher',
            'SSOP', 'GMP', 'FSIS', 'Non-GMO', 'Grass-fed', 'Free-range', 'Cage-free'
        ]
        
        for cert in certification_keywords:
            if cert.lower() in text_lower:
                entities['certifications'].append({
                    'certification': cert,
                    'type': 'food_safety' if cert in ['USDA', 'FDA', 'HACCP', 'FSIS'] else 'quality',
                    'confidence': 0.95
                })
        
        # Extract contact information
        contact_patterns = [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Email
            r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})',  # Phone numbers
            r'(\d{3}-\d{2}-\d{4})',  # SSN or Tax ID format
        ]
        
        contact_types = ['email', 'phone', 'tax_id']
        for i, pattern in enumerate(contact_patterns):
            contacts = re.findall(pattern, text)
            for contact in contacts:
                entities['contact_info'].append({
                    'value': contact,
                    'type': contact_types[i],
                    'confidence': 0.90
                })
        
        # Extract quality metrics
        quality_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:°F|degrees?|fahrenheit)',  # Temperature
            r'(\d+(?:\.\d+)?)\s*(?:%|percent)',  # Percentages
            r'(?:pH|acidity)\s*:?\s*(\d+(?:\.\d+)?)',  # pH levels
            r'(?:moisture|fat|protein)\s*:?\s*(\d+(?:\.\d+)?)',  # Composition
        ]
        
        quality_types = ['temperature', 'percentage', 'ph_level', 'composition']
        for i, pattern in enumerate(quality_patterns):
            metrics = re.findall(pattern, text_lower)
            for metric in metrics:
                entities['quality_metrics'].append({
                    'value': metric,
                    'type': quality_types[i],
                    'confidence': 0.85
                })
        
        return entities
    
    def classify_document(self, text: str, **kwargs) -> Dict[str, Any]:
        """Classify document type with enhanced meat industry intelligence."""
        text_lower = text.lower()
        
        # Enhanced classification logic with confidence scoring
        if any(word in text_lower for word in ['purchase order', 'po number', 'order date', 'ship to', 'bill to']):
            confidence = 0.95 if 'purchase order' in text_lower else 0.85
            return {
                'document_type': 'purchase_order',
                'confidence': confidence,
                'key_fields': {
                    'po_number': self._extract_po_number(text),
                    'order_date': self._extract_date(text, 'order'),
                    'supplier': self._extract_supplier_name(text),
                    'delivery_date': self._extract_date(text, 'delivery'),
                    'total_amount': self._extract_total_amount(text)
                },
                'metadata': {
                    'urgency': self._assess_urgency(text),
                    'approval_required': self._check_approval_needed(text),
                    'special_instructions': self._extract_special_instructions(text)
                }
            }
        elif any(word in text_lower for word in ['invoice', 'bill', 'amount due', 'payment terms', 'remit to']):
            confidence = 0.92 if 'invoice' in text_lower else 0.80
            return {
                'document_type': 'invoice',
                'confidence': confidence,
                'key_fields': {
                    'invoice_number': self._extract_invoice_number(text),
                    'invoice_date': self._extract_date(text, 'invoice'),
                    'due_date': self._extract_date(text, 'due'),
                    'total_amount': self._extract_total_amount(text),
                    'tax_amount': self._extract_tax_amount(text),
                    'payment_terms': self._extract_payment_terms(text)
                },
                'metadata': {
                    'payment_status': self._assess_payment_status(text),
                    'late_fees': self._check_late_fees(text),
                    'discount_available': self._check_early_payment_discount(text)
                }
            }
        elif any(word in text_lower for word in ['contract', 'agreement', 'terms and conditions', 'whereas']):
            confidence = 0.88
            return {
                'document_type': 'contract',
                'confidence': confidence,
                'key_fields': {
                    'contract_number': self._extract_contract_number(text),
                    'effective_date': self._extract_date(text, 'effective'),
                    'expiration_date': self._extract_date(text, 'expiration'),
                    'parties': self._extract_contract_parties(text),
                    'contract_value': self._extract_total_amount(text)
                },
                'metadata': {
                    'contract_type': self._classify_contract_type(text),
                    'renewal_terms': self._extract_renewal_terms(text),
                    'termination_clause': self._check_termination_clause(text)
                }
            }
        elif any(word in text_lower for word in ['certificate', 'inspection', 'usda', 'haccp', 'organic']):
            confidence = 0.90
            return {
                'document_type': 'certificate',
                'confidence': confidence,
                'key_fields': {
                    'certificate_number': self._extract_certificate_number(text),
                    'issue_date': self._extract_date(text, 'issue'),
                    'expiration_date': self._extract_date(text, 'expiration'),
                    'certifying_body': self._extract_certifying_body(text),
                    'scope': self._extract_certification_scope(text)
                },
                'metadata': {
                    'certification_type': self._classify_certification_type(text),
                    'compliance_level': self._assess_compliance_level(text),
                    'renewal_required': self._check_renewal_required(text)
                }
            }
        elif any(word in text_lower for word in ['delivery', 'receipt', 'shipment', 'bol', 'bill of lading']):
            confidence = 0.85
            return {
                'document_type': 'delivery_receipt',
                'confidence': confidence,
                'key_fields': {
                    'delivery_number': self._extract_delivery_number(text),
                    'delivery_date': self._extract_date(text, 'delivery'),
                    'carrier': self._extract_carrier_info(text),
                    'origin': self._extract_location(text, 'origin'),
                    'destination': self._extract_location(text, 'destination'),
                    'weight': self._extract_weight(text)
                },
                'metadata': {
                    'delivery_condition': self._assess_delivery_condition(text),
                    'temperature_compliance': self._check_temperature_compliance(text),
                    'signature_required': self._check_signature_required(text)
                }
            }
        elif any(word in text_lower for word in ['quality', 'test', 'lab', 'analysis', 'results']):
            confidence = 0.87
            return {
                'document_type': 'quality_report',
                'confidence': confidence,
                'key_fields': {
                    'report_number': self._extract_report_number(text),
                    'test_date': self._extract_date(text, 'test'),
                    'sample_id': self._extract_sample_id(text),
                    'test_results': self._extract_test_results(text),
                    'pass_fail': self._determine_pass_fail(text)
                },
                'metadata': {
                    'test_type': self._classify_test_type(text),
                    'accreditation': self._check_lab_accreditation(text),
                    'critical_violations': self._check_critical_violations(text)
                }
            }
        else:
            return {
                'document_type': 'unknown',
                'confidence': 0.60,
                'key_fields': {
                    'detected_entities': self._extract_any_entities(text),
                    'potential_type': self._guess_document_type(text)
                },
                'metadata': {
                    'suggestions': self._suggest_classification_improvements(text),
                    'manual_review_required': True
                }
            }
    
    def _extract_po_number(self, text: str) -> str:
        """Extract purchase order number."""
        import re
        patterns = [
            r'(?:PO|Purchase Order|Order)\s*#?\s*([A-Z0-9-]+)',
            r'(\d{4,}-\d{3,})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return 'Not found'
    
    def _extract_date(self, text: str, date_type: str) -> str:
        """Extract dates based on type context."""
        import re
        # Look for dates near specific keywords
        if date_type == 'order':
            pattern = rf'(?:order\s+date|date\s+ordered)[:\s]*(\d{{1,2}}[-/]\d{{1,2}}[-/]\d{{4}})'
        elif date_type == 'delivery':
            pattern = rf'(?:delivery\s+date|ship\s+date|due\s+date)[:\s]*(\d{{1,2}}[-/]\d{{1,2}}[-/]\d{{4}})'
        else:
            pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
        
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else 'Not found'
    
    def _extract_supplier_name(self, text: str) -> str:
        """Extract supplier name from document."""
        import re
        # Look for company names after specific keywords
        patterns = [
            r'(?:supplier|vendor|from)[:\s]*([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)* (?:Inc|LLC|Corp|Co\.?))',
            r'([A-Z][a-z]+ (?:Meat|Beef|Pork|Processing|Suppliers?) (?:Inc|LLC|Corp|Co\.?))',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return 'Not found'
    
    def _extract_total_amount(self, text: str) -> str:
        """Extract total amount from document."""
        import re
        patterns = [
            r'(?:total|amount|grand total)[:\s]*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s+total)?'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}"
        return 'Not found'
    
    def _assess_urgency(self, text: str) -> str:
        """Assess urgency level of document."""
        urgent_keywords = ['urgent', 'rush', 'asap', 'priority', 'immediate']
        if any(keyword in text.lower() for keyword in urgent_keywords):
            return 'high'
        return 'normal'
    
    def _check_approval_needed(self, text: str) -> bool:
        """Check if approval is needed based on amount or terms."""
        import re
        # Check for high amounts that might need approval
        amount_pattern = r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        matches = re.findall(amount_pattern, text)
        if matches:
            amounts = [float(amount.replace(',', '')) for amount in matches]
            return max(amounts) > 10000  # Threshold for approval
        return False
    
    def _extract_special_instructions(self, text: str) -> str:
        """Extract special delivery or handling instructions."""
        import re
        instruction_patterns = [
            r'(?:special instructions?|notes?|comments?)[:\s]*([^\n\r]+)',
            r'(?:deliver|shipping instructions?)[:\s]*([^\n\r]+)'
        ]
        for pattern in instruction_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return 'None'
    
    # Add more helper methods for other extraction functions
    def _extract_invoice_number(self, text: str) -> str:
        """Extract invoice number."""
        import re
        pattern = r'(?:invoice|inv)\s*#?\s*([A-Z0-9-]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else 'Not found'
    
    def _extract_tax_amount(self, text: str) -> str:
        """Extract tax amount."""
        import re
        pattern = r'(?:tax|sales tax)[:\s]*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        match = re.search(pattern, text, re.IGNORECASE)
        return f"${match.group(1)}" if match else 'Not found'
    
    def _extract_payment_terms(self, text: str) -> str:
        """Extract payment terms."""
        import re
        pattern = r'(?:terms?|payment terms?)[:\s]*([^\n\r]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else 'Not specified'
    
    def _assess_payment_status(self, text: str) -> str:
        """Assess payment status from invoice."""
        if any(word in text.lower() for word in ['paid', 'payment received']):
            return 'paid'
        elif any(word in text.lower() for word in ['overdue', 'past due']):
            return 'overdue'
        return 'pending'
    
    def _check_late_fees(self, text: str) -> bool:
        """Check if late fees are mentioned."""
        return any(word in text.lower() for word in ['late fee', 'penalty', 'interest charge'])
    
    def _check_early_payment_discount(self, text: str) -> bool:
        """Check if early payment discount is available."""
        return any(word in text.lower() for word in ['early payment', 'discount', '2/10 net 30'])
    
    # Placeholder methods for other document types
    def _extract_contract_number(self, text: str) -> str:
        return 'Contract-2025-001'
    
    def _extract_contract_parties(self, text: str) -> str:
        return 'Party A, Party B'
    
    def _classify_contract_type(self, text: str) -> str:
        return 'supply_agreement'
    
    def _extract_renewal_terms(self, text: str) -> str:
        return 'Annual renewal'
    
    def _check_termination_clause(self, text: str) -> bool:
        return True
    
    def _extract_certificate_number(self, text: str) -> str:
        return 'CERT-2025-001'
    
    def _extract_certifying_body(self, text: str) -> str:
        return 'USDA FSIS'
    
    def _extract_certification_scope(self, text: str) -> str:
        return 'Meat processing facility'
    
    def _classify_certification_type(self, text: str) -> str:
        return 'food_safety'
    
    def _assess_compliance_level(self, text: str) -> str:
        return 'compliant'
    
    def _check_renewal_required(self, text: str) -> bool:
        return False
    
    def _extract_delivery_number(self, text: str) -> str:
        return 'DEL-2025-001'
    
    def _extract_carrier_info(self, text: str) -> str:
        return 'Swift Transportation'
    
    def _extract_location(self, text: str, location_type: str) -> str:
        return 'Location details'
    
    def _extract_weight(self, text: str) -> str:
        return '2,500 lbs'
    
    def _assess_delivery_condition(self, text: str) -> str:
        return 'good'
    
    def _check_temperature_compliance(self, text: str) -> bool:
        return True
    
    def _check_signature_required(self, text: str) -> bool:
        return True
    
    def _extract_report_number(self, text: str) -> str:
        return 'QR-2025-001'
    
    def _extract_sample_id(self, text: str) -> str:
        return 'SAMPLE-001'
    
    def _extract_test_results(self, text: str) -> dict:
        return {'pH': '5.8', 'temperature': '38°F', 'bacteria_count': '<10 CFU/g'}
    
    def _determine_pass_fail(self, text: str) -> str:
        return 'pass'
    
    def _classify_test_type(self, text: str) -> str:
        return 'microbiological'
    
    def _check_lab_accreditation(self, text: str) -> bool:
        return True
    
    def _check_critical_violations(self, text: str) -> bool:
        return False
    
    def _extract_any_entities(self, text: str) -> dict:
        return {'text_length': len(text), 'word_count': len(text.split())}
    
    def _guess_document_type(self, text: str) -> str:
        return 'business_document'
    
    def _suggest_classification_improvements(self, text: str) -> list:
        return ['Consider adding more context keywords', 'Check document formatting']
    
    def _generate_mock_response(self, user_message: str) -> str:
        """Generate contextual mock responses with enhanced meat industry focus."""
        message_lower = user_message.lower()
        
        # Greeting responses
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return (
                "Hello! Welcome to your ProjectMeats AI Assistant! 🥩\n\n"
                "I'm here to streamline your meat market operations with:\n\n"
                "🔍 **Smart Document Processing**\n"
                "• Purchase orders, invoices, contracts, and receipts\n"
                "• Automatic data extraction and entity recognition\n"
                "• Document classification with 90%+ accuracy\n\n"
                "📊 **Business Intelligence**\n"
                "• Supplier performance analytics\n"
                "• Purchase trend analysis\n"
                "• Quality control insights\n"
                "• Cost optimization recommendations\n\n"
                "⚡ **Workflow Automation**\n"
                "• Supplier and customer management\n"
                "• Plant operations coordination\n"
                "• Regulatory compliance tracking\n\n"
                "What would you like to accomplish today?"
            )
        
        # Document processing queries
        elif any(word in message_lower for word in ['document', 'upload', 'process', 'file', 'scan']):
            return (
                "I excel at processing meat industry documents! 📄\n\n"
                "**Supported Document Types:**\n"
                "📋 **Purchase Orders** - Extract supplier, quantities, pricing, delivery dates\n"
                "🧾 **Invoices** - Capture amounts, due dates, payment terms, line items\n"
                "📄 **Supplier Contracts** - Identify key terms, pricing agreements, quality specs\n"
                "🏪 **Vendor Certificates** - USDA, HACCP, organic certifications\n"
                "📊 **Quality Reports** - Temperature logs, inspection results, compliance data\n"
                "🚚 **Delivery Receipts** - Track shipments, weights, condition reports\n\n"
                "**Processing Features:**\n"
                "• OCR for scanned documents and images\n"
                "• Automatic data validation against your database\n"
                "• Duplicate detection and conflict resolution\n"
                "• Batch processing for multiple documents\n\n"
                "Simply drag and drop your files, and I'll extract all relevant data to create or update records automatically!"
            )
        
        # Purchase order queries
        elif any(word in message_lower for word in ['purchase order', 'po', 'order', 'ordering', 'procurement']):
            return (
                "I'll help optimize your purchase order management! 📦\n\n"
                "**Purchase Order Capabilities:**\n"
                "🎯 **Smart Order Creation**\n"
                "• Extract data from supplier catalogs and quotes\n"
                "• Auto-populate based on historical orders\n"
                "• Suggest optimal quantities based on demand forecasting\n\n"
                "📈 **Order Intelligence**\n"
                "• Track order status and delivery performance\n"
                "• Monitor supplier reliability metrics\n"
                "• Identify cost-saving opportunities\n"
                "• Flag potential supply chain risks\n\n"
                "🔄 **Workflow Automation**\n"
                "• Automatic approval routing based on amount thresholds\n"
                "• Email notifications for status changes\n"
                "• Integration with accounting systems\n"
                "• Compliance checking for regulatory requirements\n\n"
                "Would you like me to process a purchase order document or help you analyze existing orders?"
            )
        
        # Supplier management
        elif any(word in message_lower for word in ['supplier', 'vendor', 'partnership', 'sourcing']):
            return (
                "I provide comprehensive supplier intelligence! 🏢\n\n"
                "**Supplier Management Features:**\n"
                "📊 **Performance Analytics**\n"
                "• On-time delivery rates and trends\n"
                "• Quality metrics and defect tracking\n"
                "• Price competitiveness analysis\n"
                "• Risk assessment and scoring\n\n"
                "📋 **Compliance Monitoring**\n"
                "• USDA certification status tracking\n"
                "• Food safety audit results\n"
                "• Insurance and bonding verification\n"
                "• Regulatory compliance alerts\n\n"
                "💡 **Strategic Insights**\n"
                "• Supplier diversification recommendations\n"
                "• Cost optimization opportunities\n"
                "• Market trend analysis\n"
                "• Alternative supplier suggestions\n\n"
                "🔄 **Relationship Management**\n"
                "• Contact management and communication history\n"
                "• Contract renewal tracking\n"
                "• Performance review scheduling\n"
                "• Supplier scorecard generation\n\n"
                "What specific supplier information or analysis would you like me to provide?"
            )
        
        # Quality and safety queries
        elif any(word in message_lower for word in ['quality', 'safety', 'inspection', 'compliance', 'haccp', 'usda']):
            return (
                "Quality and food safety are paramount in meat operations! 🛡️\n\n"
                "**Quality Management Support:**\n"
                "🔬 **Inspection & Testing**\n"
                "• Track temperature logs and cold chain compliance\n"
                "• Monitor microbiological test results\n"
                "• Document HACCP critical control points\n"
                "• Generate quality assurance reports\n\n"
                "📋 **Regulatory Compliance**\n"
                "• USDA/FSIS regulation tracking\n"
                "• FDA food safety requirements\n"
                "• State and local health department compliance\n"
                "• International export certification\n\n"
                "⚠️ **Risk Management**\n"
                "• Early warning systems for quality issues\n"
                "• Recall preparation and traceability\n"
                "• Supplier audit scheduling and tracking\n"
                "• Non-conformance reporting and CAPA\n\n"
                "📊 **Analytics & Insights**\n"
                "• Quality trend analysis across suppliers\n"
                "• Cost of quality calculations\n"
                "• Customer complaint pattern analysis\n"
                "• Continuous improvement recommendations\n\n"
                "How can I assist with your quality or compliance needs today?"
            )
        
        # Inventory and logistics
        elif any(word in message_lower for word in ['inventory', 'stock', 'warehouse', 'logistics', 'shipping', 'cold chain']):
            return (
                "I'll help optimize your inventory and logistics operations! 🚚\n\n"
                "**Inventory Intelligence:**\n"
                "📦 **Stock Management**\n"
                "• Real-time inventory tracking across facilities\n"
                "• Automated reorder point calculations\n"
                "• Expiration date monitoring and FIFO compliance\n"
                "• Lot/batch traceability throughout the supply chain\n\n"
                "🌡️ **Cold Chain Monitoring**\n"
                "• Temperature compliance tracking\n"
                "• Cold storage capacity optimization\n"
                "• Energy efficiency recommendations\n"
                "• Equipment maintenance scheduling\n\n"
                "🚛 **Logistics Optimization**\n"
                "• Route planning for delivery efficiency\n"
                "• Carrier performance evaluation\n"
                "• Freight cost analysis and optimization\n"
                "• Delivery scheduling coordination\n\n"
                "📈 **Predictive Analytics**\n"
                "• Demand forecasting based on seasonal trends\n"
                "• Optimal safety stock calculations\n"
                "• Waste reduction opportunities\n"
                "• Cost per unit delivered analysis\n\n"
                "What inventory or logistics challenge can I help you solve?"
            )
        
        # Financial and accounting
        elif any(word in message_lower for word in ['finance', 'accounting', 'cost', 'profit', 'price', 'margin', 'budget']):
            return (
                "I provide powerful financial insights for your meat business! 💰\n\n"
                "**Financial Analytics:**\n"
                "📊 **Cost Analysis**\n"
                "• Product cost breakdowns (materials, labor, overhead)\n"
                "• Supplier price trend analysis\n"
                "• Transportation and logistics cost tracking\n"
                "• Yield and shrinkage impact calculations\n\n"
                "💹 **Profitability Insights**\n"
                "• Margin analysis by product and customer\n"
                "• Price optimization recommendations\n"
                "• Customer profitability ranking\n"
                "• Market pricing competitive analysis\n\n"
                "📋 **Accounts Management**\n"
                "• Accounts receivable aging analysis\n"
                "• Payment pattern tracking\n"
                "• Credit risk assessment\n"
                "• Cash flow forecasting\n\n"
                "🎯 **Performance Metrics**\n"
                "• KPI dashboards and scorecards\n"
                "• Budget vs. actual variance analysis\n"
                "• ROI calculations for investments\n"
                "• Industry benchmark comparisons\n\n"
                "What financial analysis or insights would you like me to provide?"
            )
        
        # Analytics and reporting
        elif any(word in message_lower for word in ['analytics', 'report', 'dashboard', 'insights', 'data', 'trends']):
            return (
                "I'll generate powerful analytics and insights for your business! 📊\n\n"
                "**Advanced Analytics Capabilities:**\n"
                "📈 **Business Intelligence**\n"
                "• Sales trend analysis and forecasting\n"
                "• Customer behavior pattern recognition\n"
                "• Seasonal demand predictions\n"
                "• Market opportunity identification\n\n"
                "🎯 **Operational Insights**\n"
                "• Production efficiency metrics\n"
                "• Equipment utilization analysis\n"
                "• Labor productivity tracking\n"
                "• Energy consumption optimization\n\n"
                "📋 **Custom Reporting**\n"
                "• Executive summary dashboards\n"
                "• Regulatory compliance reports\n"
                "• Customer-specific analytics\n"
                "• Supplier performance scorecards\n\n"
                "🔮 **Predictive Models**\n"
                "• Demand forecasting algorithms\n"
                "• Risk prediction models\n"
                "• Quality issue early detection\n"
                "• Maintenance scheduling optimization\n\n"
                "What type of analysis or report would you like me to create?"
            )
        
        # General help
        elif any(word in message_lower for word in ['help', 'what can you do', 'capabilities', 'features']):
            return (
                "I'm your comprehensive AI assistant for meat market operations! 🤖\n\n"
                "**Core Capabilities:**\n"
                "🔍 **Document Intelligence**\n"
                "• OCR and text extraction from any document format\n"
                "• Automatic classification and data extraction\n"
                "• Entity recognition and database integration\n"
                "• Duplicate detection and data validation\n\n"
                "💬 **Business Intelligence Chat**\n"
                "• Natural language queries about your data\n"
                "• Real-time analytics and insights\n"
                "• Trend analysis and forecasting\n"
                "• Custom report generation\n\n"
                "⚡ **Process Automation**\n"
                "• Workflow optimization recommendations\n"
                "• Automated data entry and updates\n"
                "• Alert systems for critical events\n"
                "• Integration with existing systems\n\n"
                "🎯 **Industry Expertise**\n"
                "• Deep knowledge of meat industry regulations\n"
                "• Best practices for food safety and quality\n"
                "• Supply chain optimization strategies\n"
                "• Market intelligence and trends\n\n"
                "**Quick Start Tips:**\n"
                "• Upload documents for instant processing\n"
                "• Ask questions about your suppliers, customers, or orders\n"
                "• Request specific reports or analytics\n"
                "• Get recommendations for process improvements\n\n"
                "Try saying something like: 'Analyze my top suppliers' or 'Process this invoice'"
            )
        
        # Specific product queries
        elif any(word in message_lower for word in ['beef', 'pork', 'chicken', 'lamb', 'turkey', 'veal', 'meat']):
            detected_products = []
            meat_products = ['beef', 'pork', 'chicken', 'lamb', 'turkey', 'veal']
            for product in meat_products:
                if product in message_lower:
                    detected_products.append(product.title())
            
            products_text = ", ".join(detected_products) if detected_products else "meat products"
            
            return (
                f"I can provide comprehensive insights about {products_text}! 🥩\n\n"
                "**Product Intelligence:**\n"
                "📊 **Market Analysis**\n"
                f"• Current {products_text.lower()} pricing trends and forecasts\n"
                "• Seasonal demand patterns and planning\n"
                "• Competitive pricing analysis\n"
                "• Margin optimization opportunities\n\n"
                "🏭 **Supply Chain Insights**\n"
                "• Supplier quality ratings and certifications\n"
                "• Alternative sourcing recommendations\n"
                "• Geographic sourcing optimization\n"
                "• Risk assessment and mitigation strategies\n\n"
                "📋 **Quality & Compliance**\n"
                "• Grade standards and specifications\n"
                "• Inspection requirements and scheduling\n"
                "• Traceability and lot tracking\n"
                "• Regulatory compliance monitoring\n\n"
                "💡 **Optimization Recommendations**\n"
                "• Inventory turnover improvements\n"
                "• Yield optimization strategies\n"
                "• Waste reduction opportunities\n"
                "• Customer preference analysis\n\n"
                f"What specific information about {products_text.lower()} would you like me to analyze?"
            )
        
        # Default response with suggestions
        else:
            return (
                "I'm here to assist with your meat market operations! 🎯\n\n"
                "I can help you with various tasks. Here are some suggestions:\n\n"
                "📄 **Document Processing:**\n"
                "• \"Process this purchase order\"\n"
                "• \"Extract data from this invoice\"\n"
                "• \"Classify this supplier document\"\n\n"
                "📊 **Business Analytics:**\n"
                "• \"Show me my top suppliers\"\n"
                "• \"Analyze purchase trends\"\n"
                "• \"Generate a quality report\"\n\n"
                "🔍 **Data Insights:**\n"
                "• \"Which customers are most profitable?\"\n"
                "• \"What are my inventory levels?\"\n"
                "• \"Show delivery performance metrics\"\n\n"
                "⚙️ **Operations:**\n"
                "• \"Help me optimize my supply chain\"\n"
                "• \"Review quality compliance\"\n"
                "• \"Analyze cost reduction opportunities\"\n\n"
                "Just describe what you'd like to accomplish, or upload a document for me to process!"
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
        """Get the default AI configuration with caching."""
        cache_key = 'ai_assistant:default_config'
        config = cache.get(cache_key)
        
        if config is None:
            try:
                config = AIConfiguration.objects.filter(
                    is_active=True, 
                    is_default=True
                ).first()
                # Cache for 5 minutes
                cache.set(cache_key, config, 300)
            except Exception as e:
                logger.error(f"Error getting default AI config: {str(e)}")
                return None
        
        return config
    
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
        Generate AI response for chat conversation with caching.
        
        Args:
            user_message: User's input message
            session_messages: Previous messages in the session
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (response_text, metadata)
        """
        start_time = time.time()
        
        # Create cache key for similar queries
        cache_key = self._create_cache_key(user_message, session_messages)
        cached_response = cache.get(cache_key)
        
        if cached_response and not kwargs.get('force_refresh', False):
            logger.info(f"Using cached response for query: {user_message[:50]}...")
            cached_response['metadata']['cached'] = True
            cached_response['metadata']['processing_time'] = time.time() - start_time
            return cached_response['response'], cached_response['metadata']
        
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
                'finish_reason': result.get('finish_reason', 'unknown'),
                'cached': False,
                'timestamp': timezone.now().isoformat()
            }
            
            # Cache the response for 1 hour for similar queries
            cache_data = {
                'response': result['response'],
                'metadata': metadata.copy()
            }
            cache.set(cache_key, cache_data, 3600)
            
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
                'error': str(e),
                'cached': False,
                'timestamp': timezone.now().isoformat()
            }
            
            return fallback_response, metadata
    
    def _create_cache_key(self, user_message: str, session_messages: List[ChatMessage] = None) -> str:
        """Create a cache key for the conversation context."""
        # Create a hash of the user message and recent context
        content_to_hash = user_message.lower().strip()
        
        # Add recent context if available
        if session_messages:
            recent_messages = session_messages[-3:]  # Last 3 messages for context
            context = " ".join([msg.content for msg in recent_messages])
            content_to_hash += " " + context.lower().strip()
        
        # Create hash
        hash_object = hashlib.md5(content_to_hash.encode())
        cache_key = f"ai_assistant:response:{hash_object.hexdigest()}"
        
        return cache_key
    
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