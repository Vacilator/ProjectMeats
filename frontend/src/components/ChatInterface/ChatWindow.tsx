/**
 * ChatWindow Component
 * 
 * Main chat interface component that provides an intuitive AI assistant
 * experience similar to Microsoft Copilot for meat market operations.
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled from 'styled-components';
import { ChatSession, ChatMessage } from '../../types';
import { chatApi, chatSessionsApi, documentsApi, aiUtils } from '../../services/aiService';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import DocumentUpload from './DocumentUpload';

interface ChatWindowProps {
  sessionId?: string;
  onSessionChange?: (session: ChatSession | null) => void;
  className?: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  sessionId,
  onSessionChange,
  className
}) => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load session and messages
  const loadSession = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);

      const [sessionData, messagesData] = await Promise.all([
        chatSessionsApi.get(id),
        chatSessionsApi.getMessages(id)
      ]);

      setSession(sessionData);
      setMessages(messagesData.results);
      onSessionChange?.(sessionData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load session');
      console.error('Error loading session:', err);
    } finally {
      setLoading(false);
    }
  }, [onSessionChange]);

  // Start new session
  const startNewSession = useCallback(async (initialMessage: string) => {
    try {
      setLoading(true);
      setError(null);
      setIsTyping(true);

      const result = await chatSessionsApi.startSession({
        message: initialMessage,
        title: `Chat ${new Date().toLocaleString()}`
      });

      setSession(result.session);
      setMessages([result.user_message, result.ai_response]);
      onSessionChange?.(result.session);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start session');
      console.error('Error starting session:', err);
    } finally {
      setLoading(false);
      setIsTyping(false);
    }
  }, [onSessionChange]);

  // Send message to existing session
  const sendMessage = useCallback(async (message: string) => {
    if (!session) {
      await startNewSession(message);
      return;
    }

    try {
      setError(null);
      setIsTyping(true);

      // Add user message immediately for better UX
      const userMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        session: session.id,
        message_type: 'user',
        content: message,
        metadata: {},
        is_processed: true,
        owner: session.owner,
        created_by: session.created_by,
        modified_by: session.modified_by,
        created_on: new Date().toISOString(),
        modified_on: new Date().toISOString(),
      };

      setMessages(prev => [...prev, userMessage]);

      // Send to API
      await chatApi.sendMessage({
        message,
        session_id: session.id
      });

      // Update messages with real data
      const updatedMessages = await chatSessionsApi.getMessages(session.id);
      setMessages(updatedMessages.results);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      console.error('Error sending message:', err);
      
      // Remove the temporary user message on error
      setMessages(prev => prev.filter(m => !m.id.startsWith('temp-')));
    } finally {
      setIsTyping(false);
    }
  }, [session, startNewSession]);

  // Upload document
  const uploadDocument = useCallback(async (file: File) => {
    try {
      setLoading(true);
      setError(null);

      // Upload the document
      const document = await documentsApi.upload({
        file,
        original_filename: file.name
      });

      // Create a document message if we have a session
      if (session) {
        const documentMessage = `📄 I've uploaded "${file.name}" for processing. Let me analyze this ${aiUtils.getDocumentTypeDisplay(document.document_type).toLowerCase()} for you.`;
        
        // Send a message about the document
        await sendMessage(documentMessage);
      } else {
        // Start new session with document processing message
        await startNewSession(`Please analyze this uploaded document: ${file.name}`);
      }

      return document;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload document');
      console.error('Error uploading document:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session, sendMessage, startNewSession]);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Load session on mount or session ID change
  useEffect(() => {
    if (sessionId) {
      loadSession(sessionId);
    } else {
      setSession(null);
      setMessages([]);
      onSessionChange?.(null);
    }
  }, [sessionId, loadSession, onSessionChange]);

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return (
    <ChatWindowContainer className={className}>
      {/* Header */}
      <ChatHeader>
        <HeaderInfo>
          <AssistantIcon>🤖</AssistantIcon>
          <HeaderText>
            <AssistantName>ProjectMeats AI Assistant</AssistantName>
            <SessionTitle>
              {session ? (session.title || `Session ${session.id.slice(0, 8)}`) : 'Start a new conversation'}
            </SessionTitle>
          </HeaderText>
        </HeaderInfo>
        <HeaderActions>
          {session && (
            <SessionInfo>
              {session.message_count} messages
              {session.has_documents && ' • 📄 Has documents'}
            </SessionInfo>
          )}
        </HeaderActions>
      </ChatHeader>

      {/* Error Display */}
      {error && (
        <ErrorBar>
          <ErrorIcon>⚠️</ErrorIcon>
          <ErrorText>{error}</ErrorText>
          <ErrorClose onClick={() => setError(null)}>×</ErrorClose>
        </ErrorBar>
      )}

      {/* Messages */}
      <MessagesContainer>
        {!session && messages.length === 0 ? (
          <WelcomeMessage>
            <WelcomeIcon>🥩</WelcomeIcon>
            <WelcomeTitle>Welcome to ProjectMeats AI Assistant</WelcomeTitle>
            <WelcomeText>
              I am here to help you with meat market operations including:
            </WelcomeText>
            <FeaturesList>
              <FeatureItem>📋 Processing purchase orders and invoices</FeatureItem>
              <FeatureItem>🏢 Managing supplier and customer information</FeatureItem>
              <FeatureItem>📊 Analyzing business documents</FeatureItem>
              <FeatureItem>📄 Document classification and data extraction</FeatureItem>
            </FeaturesList>
            <WelcomeText>
              Send me a message or upload a document to get started!
            </WelcomeText>
          </WelcomeMessage>
        ) : (
          <>
            <MessageList 
              messages={messages}
              loading={loading}
              isTyping={isTyping}
            />
            <div ref={messagesEndRef} />
          </>
        )}
      </MessagesContainer>

      {/* Input Area */}
      <InputArea>
        <DocumentUpload
          onFileUpload={uploadDocument}
          disabled={loading}
        />
        <MessageInput
          onSendMessage={sendMessage}
          disabled={loading}
          placeholder={
            !session 
              ? "Ask me anything about meat market operations..." 
              : "Continue the conversation..."
          }
        />
      </InputArea>
    </ChatWindowContainer>
  );
};

// Styled Components
const ChatWindowContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const ChatHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const HeaderInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const AssistantIcon = styled.div`
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
`;

const HeaderText = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const AssistantName = styled.div`
  font-size: 16px;
  font-weight: 600;
`;

const SessionTitle = styled.div`
  font-size: 14px;
  opacity: 0.9;
  font-weight: 400;
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const SessionInfo = styled.div`
  font-size: 12px;
  opacity: 0.8;
  text-align: right;
`;

const ErrorBar = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: #fef2f2;
  border-bottom: 1px solid #fecaca;
  color: #dc2626;
`;

const ErrorIcon = styled.span`
  font-size: 16px;
`;

const ErrorText = styled.span`
  flex: 1;
  font-size: 14px;
`;

const ErrorClose = styled.button`
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  font-size: 18px;
  padding: 0;
  
  &:hover {
    opacity: 0.7;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  max-width: 500px;
  margin: 0 auto;
  padding: 40px 20px;
`;

const WelcomeIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
`;

const WelcomeTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
`;

const WelcomeText = styled.p`
  font-size: 16px;
  color: #6b7280;
  line-height: 1.6;
  margin-bottom: 20px;
`;

const FeaturesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 20px 0;
  text-align: left;
`;

const FeatureItem = styled.div`
  font-size: 14px;
  color: #4b5563;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
  border-left: 3px solid #667eea;
`;

const InputArea = styled.div`
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
`;

export default ChatWindow;