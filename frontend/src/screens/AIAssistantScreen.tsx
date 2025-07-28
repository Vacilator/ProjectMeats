/**
 * AI Assistant Screen
 * 
 * Main screen for the AI assistant that combines the chat interface
 * with session management in a split-pane layout similar to Microsoft Copilot.
 */
import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import { ChatWindow, SessionsList } from '../components/ChatInterface';
import { ChatSession } from '../types';

const AIAssistantScreen: React.FC = () => {
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);

  // Handle session selection
  const handleSessionSelect = useCallback((session: ChatSession) => {
    setCurrentSession(session);
  }, []);

  // Handle new session
  const handleNewSession = useCallback(() => {
    setCurrentSession(null);
  }, []);

  // Handle session change from chat window
  const handleSessionChange = useCallback((session: ChatSession | null) => {
    setCurrentSession(session);
  }, []);

  // Toggle sidebar
  const toggleSidebar = useCallback(() => {
    setShowSidebar(prev => !prev);
  }, []);

  return (
    <ScreenContainer>
      {/* Header */}
      <ScreenHeader>
        <HeaderLeft>
          <SidebarToggle onClick={toggleSidebar}>
            {showSidebar ? '◀' : '▶'}
          </SidebarToggle>
          <HeaderTitle>
            <TitleIcon>🤖</TitleIcon>
            ProjectMeats AI Assistant
          </HeaderTitle>
        </HeaderLeft>
        
        <HeaderRight>
          <HeaderSubtitle>
            Intelligent document processing and business assistance
          </HeaderSubtitle>
        </HeaderRight>
      </ScreenHeader>

      {/* Main content */}
      <ScreenContent>
        {/* Sessions sidebar */}
        {showSidebar && (
          <Sidebar>
            <SessionsList
              currentSessionId={currentSession?.id}
              onSessionSelect={handleSessionSelect}
              onNewSession={handleNewSession}
            />
          </Sidebar>
        )}

        {/* Chat area */}
        <ChatArea showSidebar={showSidebar}>
          <ChatWindow
            sessionId={currentSession?.id}
            onSessionChange={handleSessionChange}
          />
        </ChatArea>
      </ScreenContent>
    </ScreenContainer>
  );
};

// Styled Components
const ScreenContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8fafc;
`;

const ScreenHeader = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const SidebarToggle = styled.button`
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  color: #64748b;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e2e8f0;
    color: #334155;
  }
`;

const HeaderTitle = styled.h1`
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
`;

const TitleIcon = styled.span`
  font-size: 28px;
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
`;

const HeaderSubtitle = styled.p`
  margin: 0;
  font-size: 14px;
  color: #64748b;
  font-style: italic;
`;

const ScreenContent = styled.div`
  flex: 1;
  display: flex;
  overflow: hidden;
  gap: 1px;
  background: #e2e8f0;
`;

const Sidebar = styled.aside`
  width: 320px;
  background: white;
  overflow: hidden;
  flex-shrink: 0;
`;

const ChatArea = styled.main<{showSidebar: boolean}>`
  flex: 1;
  background: white;
  overflow: hidden;
  border-radius: ${props => props.showSidebar ? '0' : '8px 0 0 0'};
`;

export default AIAssistantScreen;