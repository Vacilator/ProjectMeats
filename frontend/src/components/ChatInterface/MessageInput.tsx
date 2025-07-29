/**
 * MessageInput Component
 * 
 * Input field for typing and sending messages to the AI assistant.
 * Includes features like auto-resize, keyboard shortcuts, and suggested prompts.
 */
import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import styled from 'styled-components';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message...",
  className
}) => {
  const [message, setMessage] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Suggested prompts for meat market operations
  const suggestedPrompts = [
    "Help me process a purchase order",
    "How do I manage supplier information?",
    "What are the current market trends?",
    "Analyze my recent invoices",
    "Create a new customer record",
    "Track delivery schedules",
  ];

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  // Handle form submission
  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      setShowSuggestions(false);
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Show suggestions if input is empty and user starts typing
    if (e.target.value === '' && !showSuggestions) {
      setShowSuggestions(true);
    } else if (e.target.value !== '' && showSuggestions) {
      setShowSuggestions(false);
    }
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: string) => {
    setMessage(suggestion);
    setShowSuggestions(false);
    textareaRef.current?.focus();
  };

  // Focus input on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  return (
    <InputContainer className={className}>
      {/* Suggested prompts */}
      {showSuggestions && (
        <SuggestionsContainer>
          <SuggestionsTitle>💡 Suggested prompts:</SuggestionsTitle>
          <SuggestionsList>
            {suggestedPrompts.map((prompt, index) => (
              <SuggestionItem
                key={index}
                onClick={() => handleSuggestionClick(prompt)}
              >
                {prompt}
              </SuggestionItem>
            ))}
          </SuggestionsList>
        </SuggestionsContainer>
      )}

      {/* Main input form */}
      <InputForm onSubmit={handleSubmit}>
        <InputWrapper>
          <TextArea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            maxLength={5000}
          />
          
          <InputActions>
            <CharacterCount isNearLimit={message.length > 4500}>
              {message.length}/5000
            </CharacterCount>
            
            <SendButton
              type="submit"
              disabled={!message.trim() || disabled}
              title="Send message (Enter)"
            >
              {disabled ? (
                <LoadingSpinner />
              ) : (
                <SendIcon>🚀</SendIcon>
              )}
            </SendButton>
          </InputActions>
        </InputWrapper>
        
        <InputHint>
          Press <Kbd>Enter</Kbd> to send, <Kbd>Shift + Enter</Kbd> for new line
        </InputHint>
      </InputForm>
    </InputContainer>
  );
};

// Styled Components
const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const SuggestionsContainer = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const SuggestionsTitle = styled.div`
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 8px;
`;

const SuggestionsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
`;

const SuggestionItem = styled.button`
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 12px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e5e7eb;
    border-color: #d1d5db;
  }
  
  &:active {
    transform: scale(0.98);
  }
`;

const InputForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const InputWrapper = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  transition: border-color 0.2s ease;
  
  &:focus-within {
    border-color: #667eea;
  }
`;

const TextArea = styled.textarea`
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  color: #1f2937;
  background: transparent;
  min-height: 20px;
  max-height: 120px;
  
  &::placeholder {
    color: #9ca3af;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const InputActions = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
`;

const CharacterCount = styled.div<{isNearLimit: boolean}>`
  font-size: 10px;
  color: ${props => props.isNearLimit ? '#dc2626' : '#9ca3af'};
  font-weight: ${props => props.isNearLimit ? '600' : '400'};
`;

const SendButton = styled.button`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const SendIcon = styled.span`
  font-size: 16px;
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const InputHint = styled.div`
  font-size: 11px;
  color: #9ca3af;
  text-align: center;
  padding: 0 12px;
`;

const Kbd = styled.kbd`
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 1px 4px;
  font-size: 10px;
  font-family: monospace;
`;

export default MessageInput;