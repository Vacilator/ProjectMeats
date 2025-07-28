/**
 * MessageList Component
 * 
 * Displays a list of chat messages with different styles for user,
 * assistant, system, and document messages.
 */
import React from 'react';
import styled from 'styled-components';
import { ChatMessage } from '../../types';
import { aiUtils } from '../../services/aiService';

interface MessageListProps {
  messages: ChatMessage[];
  loading?: boolean;
  isTyping?: boolean;
  className?: string;
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  loading = false,
  isTyping = false,
  className
}) => {
  return (
    <MessageListContainer className={className}>
      {messages.map((message, index) => (
        <MessageBubble
          key={message.id}
          message={message}
          isLast={index === messages.length - 1}
        />
      ))}
      
      {isTyping && (
        <TypingIndicator>
          <TypingBubble>
            <TypingIcon>🤖</TypingIcon>
            <TypingText>
              <TypingDots>
                <TypingDot />
                <TypingDot />
                <TypingDot />
              </TypingDots>
            </TypingText>
          </TypingBubble>
        </TypingIndicator>
      )}
      
      {loading && !isTyping && (
        <LoadingIndicator>
          <LoadingSpinner />
          <LoadingText>Loading messages...</LoadingText>
        </LoadingIndicator>
      )}
    </MessageListContainer>
  );
};

interface MessageBubbleProps {
  message: ChatMessage;
  isLast: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isLast }) => {
  const isUser = message.message_type === 'user';
  const isSystem = message.message_type === 'system';
  const isDocument = message.message_type === 'document';
  
  return (
    <MessageContainer isUser={isUser} isLast={isLast}>
      <MessageWrapper isUser={isUser}>
        {!isUser && (
          <MessageIcon>
            {aiUtils.getMessageTypeIcon(message.message_type)}
          </MessageIcon>
        )}
        
        <MessageContent isUser={isUser} isSystem={isSystem}>
          <MessageHeader>
            <MessageType>
              {isUser ? 'You' : 
               isSystem ? 'System' : 
               isDocument ? 'Document' : 'AI Assistant'}
            </MessageType>
            <MessageTime>
              {aiUtils.formatRelativeTime(message.created_on)}
            </MessageTime>
          </MessageHeader>
          
          <MessageText isUser={isUser} isSystem={isSystem}>
            {message.content}
          </MessageText>
          
          {/* Document attachment */}
          {message.uploaded_document && (
            <DocumentAttachment>
              <DocumentIcon>📄</DocumentIcon>
              <DocumentInfo>
                <DocumentName>{message.uploaded_document.original_filename}</DocumentName>
                <DocumentMeta>
                  {aiUtils.formatFileSize(message.uploaded_document.file_size)} • 
                  {aiUtils.getDocumentTypeDisplay(message.uploaded_document.document_type)}
                  {message.uploaded_document.processing_status && (
                    <ProcessingStatus 
                      status={message.uploaded_document.processing_status}
                    >
                      {aiUtils.getProcessingStatusDisplay(message.uploaded_document.processing_status).name}
                    </ProcessingStatus>
                  )}
                </DocumentMeta>
              </DocumentInfo>
            </DocumentAttachment>
          )}
          
          {/* Processing error */}
          {message.processing_error && (
            <ErrorMessage>
              <ErrorIcon>⚠️</ErrorIcon>
              <ErrorText>{message.processing_error}</ErrorText>
            </ErrorMessage>
          )}
          
          {/* Metadata (for debugging - can be hidden in production) */}
          {message.metadata && Object.keys(message.metadata).length > 0 && (
            <MessageMetadata>
              {message.metadata.model && (
                <MetadataItem>Model: {message.metadata.model}</MetadataItem>
              )}
              {message.metadata.processing_time && (
                <MetadataItem>
                  Response time: {Math.round(message.metadata.processing_time * 1000)}ms
                </MetadataItem>
              )}
            </MessageMetadata>
          )}
        </MessageContent>
        
        {isUser && (
          <MessageIcon>
            👤
          </MessageIcon>
        )}
      </MessageWrapper>
    </MessageContainer>
  );
};

// Styled Components
const MessageListContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MessageContainer = styled.div<{isUser: boolean; isLast: boolean}>`
  display: flex;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: ${props => props.isLast ? 0 : '8px'};
`;

const MessageWrapper = styled.div<{isUser: boolean}>`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  max-width: 80%;
  flex-direction: ${props => props.isUser ? 'row-reverse' : 'row'};
`;

const MessageIcon = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  background: #f3f4f6;
  flex-shrink: 0;
  margin-top: 4px;
`;

const MessageContent = styled.div<{isUser: boolean; isSystem: boolean}>`
  background: ${props => 
    props.isUser ? '#667eea' :
    props.isSystem ? '#f59e0b' : '#f9fafb'
  };
  color: ${props => 
    props.isUser ? 'white' :
    props.isSystem ? 'white' : '#1f2937'
  };
  border-radius: 16px;
  padding: 12px 16px;
  border: ${props => props.isUser || props.isSystem ? 'none' : '1px solid #e5e7eb'};
  box-shadow: ${props => props.isUser || props.isSystem ? 'none' : '0 1px 3px rgba(0, 0, 0, 0.1)'};
`;

const MessageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  opacity: 0.8;
`;

const MessageType = styled.span`
  font-weight: 600;
`;

const MessageTime = styled.span`
  font-weight: 400;
`;

const MessageText = styled.div<{isUser: boolean; isSystem: boolean}>`
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
`;

const DocumentAttachment = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
`;

const DocumentIcon = styled.div`
  font-size: 20px;
`;

const DocumentInfo = styled.div`
  flex: 1;
`;

const DocumentName = styled.div`
  font-weight: 500;
  font-size: 13px;
  margin-bottom: 2px;
`;

const DocumentMeta = styled.div`
  font-size: 11px;
  opacity: 0.7;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const ProcessingStatus = styled.span<{status: string}>`
  background: ${props => aiUtils.getProcessingStatusDisplay(props.status).color};
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  margin-left: 4px;
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 6px 8px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(239, 68, 68, 0.2);
`;

const ErrorIcon = styled.span`
  font-size: 14px;
`;

const ErrorText = styled.span`
  font-size: 12px;
  color: #dc2626;
`;

const MessageMetadata = styled.div`
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 11px;
  opacity: 0.6;
`;

const MetadataItem = styled.div`
  margin-bottom: 2px;
`;

const TypingIndicator = styled.div`
  display: flex;
  justify-content: flex-start;
  margin-bottom: 8px;
`;

const TypingBubble = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 12px 16px;
  max-width: 80%;
`;

const TypingIcon = styled.div`
  font-size: 16px;
`;

const TypingText = styled.div`
  display: flex;
  align-items: center;
`;

const TypingDots = styled.div`
  display: flex;
  gap: 4px;
`;

const TypingDot = styled.div`
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #9ca3af;
  animation: typing 1.4s ease-in-out infinite;
  
  &:nth-child(1) {
    animation-delay: 0s;
  }
  
  &:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  &:nth-child(3) {
    animation-delay: 0.4s;
  }
  
  @keyframes typing {
    0%, 60%, 100% {
      transform: scale(1);
      opacity: 0.5;
    }
    30% {
      transform: scale(1.2);
      opacity: 1;
    }
  }
`;

const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #6b7280;
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingText = styled.span`
  font-size: 14px;
`;

export default MessageList;