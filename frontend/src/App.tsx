import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
}

interface ChatResponse {
  response: string;
  sources: string[];
  session_id: string;
}

const API_URL = 'http://localhost:8001';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => {
    // Generate session ID
    setSessionId(`session-${Date.now()}`);
    
    // Check API connection
    checkConnection();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkConnection = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`);
      setIsConnected(response.data.status === 'healthy');
    } catch (error) {
      setIsConnected(false);
      console.error('API connection error:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post<ChatResponse>(`${API_URL}/api/chat/`, {
        message: userMessage.content,
        session_id: sessionId,
      });

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        sources: response.data.sources,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(`session-${Date.now()}`);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 AI Chatbot</h1>
        <div className="connection-status">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to AI Chatbot!</h2>
              <p>Ask me anything about the computer science curriculum.</p>
              <div className="sample-questions">
                <h3>Try asking:</h3>
                <ul>
                  <li>"What courses are available?"</li>
                  <li>"What is object-oriented programming?"</li>
                  <li>"Tell me about the xv6 operating system"</li>
                  <li>"What are the prerequisites for Machine Learning?"</li>
                </ul>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-header">
                <span className="message-role">
                  {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
                </span>
                <span className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
              {message.sources && message.sources.length > 0 && (
                <div className="message-sources">
                  <span>Sources: </span>
                  {message.sources.map((source, index) => (
                    <span key={index} className="source-tag">{source}</span>
                  ))}
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="message assistant loading">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <button className="clear-button" onClick={clearChat} title="Clear chat">
            🗑️
          </button>
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            disabled={!isConnected || isLoading}
            rows={1}
          />
          <button 
            onClick={sendMessage} 
            disabled={!isConnected || isLoading || !inputValue.trim()}
            className="send-button"
          >
            {isLoading ? '⏳' : '📤'} Send
          </button>
        </div>
      </div>

      <footer className="App-footer">
        <p>Session ID: {sessionId}</p>
      </footer>
    </div>
  );
}

export default App;