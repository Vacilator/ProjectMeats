/**
 * SessionsList Component
 * 
 * Displays a list of chat sessions for the current user,
 * allowing them to switch between conversations or start new ones.
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ChatSession } from '../../types';
import { chatSessionsApi, aiUtils } from '../../services/aiService';

interface SessionsListProps {
  currentSessionId?: string;
  onSessionSelect: (session: ChatSession) => void;
  onNewSession: () => void;
  className?: string;
}

const SessionsList: React.FC<SessionsListProps> = ({
  currentSessionId,
  onSessionSelect,
  onNewSession,
  className
}) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load sessions
  const loadSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await chatSessionsApi.list({
        page: 1
      });
      
      setSessions(response.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
      console.error('Error loading sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  // Delete session
  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!window.confirm('Are you sure you want to delete this session?')) {
      return;
    }

    try {
      await chatSessionsApi.delete(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      
      // If current session was deleted, clear it
      if (sessionId === currentSessionId) {
        onNewSession();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete session');
      console.error('Error deleting session:', err);
    }
  };

  return (
    <SessionsContainer className={className}>
      {/* Header */}
      <SessionsHeader>
        <HeaderTitle>
          <HeaderIcon>💬</HeaderIcon>
          Chat Sessions
        </HeaderTitle>
        <NewSessionButton onClick={onNewSession}>
          <NewSessionIcon>+</NewSessionIcon>
          New Chat
        </NewSessionButton>
      </SessionsHeader>

      {/* Error display */}
      {error && (
        <ErrorMessage>
          <ErrorIcon>⚠️</ErrorIcon>
          <ErrorText>{error}</ErrorText>
          <RetryButton onClick={loadSessions}>Retry</RetryButton>
        </ErrorMessage>
      )}

      {/* Sessions list */}
      <SessionsListContainer>
        {loading ? (
          <LoadingState>
            <LoadingSpinner />
            <LoadingText>Loading sessions...</LoadingText>
          </LoadingState>
        ) : sessions.length === 0 ? (
          <EmptyState>
            <EmptyIcon>💭</EmptyIcon>
            <EmptyTitle>No chat sessions yet</EmptyTitle>
            <EmptyText>Start a new conversation to begin</EmptyText>
          </EmptyState>
        ) : (
          sessions.map(session => (
            <SessionItem
              key={session.id}
              isActive={session.id === currentSessionId}
              onClick={() => onSessionSelect(session)}
            >
              <SessionContent>
                <SessionTitle>
                  {session.title || `Session ${session.id.slice(0, 8)}`}
                </SessionTitle>
                <SessionMeta>
                  <SessionTime>
                    {aiUtils.formatRelativeTime(session.last_activity)}
                  </SessionTime>
                  <SessionStats>
                    {session.message_count} messages
                    {session.has_documents && ' • 📄'}
                  </SessionStats>
                </SessionMeta>
              </SessionContent>
              
              <SessionActions>
                <DeleteButton
                  onClick={(e) => handleDeleteSession(session.id, e)}
                  title="Delete session"
                >
                  🗑️
                </DeleteButton>
              </SessionActions>
            </SessionItem>
          ))
        )}
      </SessionsListContainer>

      {/* Refresh button */}
      <RefreshContainer>
        <RefreshButton onClick={loadSessions} disabled={loading}>
          <RefreshIcon>🔄</RefreshIcon>
          Refresh
        </RefreshButton>
      </RefreshContainer>
    </SessionsContainer>
  );
};

// Styled Components
const SessionsContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
`;

const SessionsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
`;

const HeaderTitle = styled.h3`
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
`;

const HeaderIcon = styled.span`
  font-size: 18px;
`;

const NewSessionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const NewSessionIcon = styled.span`
  font-size: 14px;
  font-weight: bold;
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: #fef2f2;
  border-bottom: 1px solid #fecaca;
  color: #dc2626;
  font-size: 12px;
`;

const ErrorIcon = styled.span`
  font-size: 14px;
`;

const ErrorText = styled.span`
  flex: 1;
`;

const RetryButton = styled.button`
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  font-size: 12px;
  text-decoration: underline;
  
  &:hover {
    opacity: 0.7;
  }
`;

const SessionsListContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
`;

const LoadingState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 12px;
`;

const LoadingSpinner = styled.div`
  width: 24px;
  height: 24px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingText = styled.div`
  font-size: 14px;
  color: #6b7280;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
`;

const EmptyIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
`;

const EmptyTitle = styled.h4`
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
`;

const EmptyText = styled.p`
  margin: 0;
  font-size: 14px;
  color: #6b7280;
`;

const SessionItem = styled.div<{isActive: boolean}>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  margin: 0 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: ${props => props.isActive ? '#f0f4ff' : 'transparent'};
  border: ${props => props.isActive ? '1px solid #c7d2fe' : '1px solid transparent'};
  
  &:hover {
    background: ${props => props.isActive ? '#f0f4ff' : '#f9fafb'};
  }
`;

const SessionContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const SessionTitle = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const SessionMeta = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #6b7280;
`;

const SessionTime = styled.span``;

const SessionStats = styled.span``;

const SessionActions = styled.div`
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
  
  ${SessionItem}:hover & {
    opacity: 1;
  }
`;

const DeleteButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.2s ease;
  
  &:hover {
    background: #fef2f2;
  }
`;

const RefreshContainer = styled.div`
  padding: 12px 20px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
`;

const RefreshButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 8px 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 12px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    background: #f3f4f6;
    border-color: #9ca3af;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const RefreshIcon = styled.span`
  font-size: 14px;
`;

export default SessionsList;