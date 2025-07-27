import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import '../styles/Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('Connecting...');
  const [ws, setWs] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const initializeChat = async () => {
      console.log('🚀 Starting chat initialization...');
      
      try {
        // Step 1: Check backend health
        console.log('📡 Checking backend health at port 8001...');
        const healthResponse = await fetch('http://localhost:8001/health');
        
        if (!healthResponse.ok) {
          throw new Error(`Health check failed: ${healthResponse.status}`);
        }
        
        const healthData = await healthResponse.json();
        console.log('✅ Backend health response:', healthData);
        
        if (!healthData.vector_store_ready) {
          console.error('❌ Vector store not ready!');
          setConnectionStatus('Vector store not initialized');
          setIsConnected(false);
          
          // Add welcome message about initialization
          setMessages([{
            text: "⚠️ The AI system is initializing. Please wait a moment and refresh the page.",
            isUser: false,
            isSystem: true
          }]);
          return;
        }

        // Step 2: Create WebSocket connection
        console.log('🔌 Creating WebSocket connection to port 8001...');
        const websocket = new WebSocket('ws://localhost:8001/ws');
        
        websocket.onopen = () => {
          console.log('✅ WebSocket connected successfully!');
          setIsConnected(true);
          setConnectionStatus('Connected');
          
          // Add welcome message
          setMessages([{
            text: "👋 Hello! I'm your AI assistant. I'm ready to help you with questions about the curriculum and computer science topics. How can I assist you today?",
            isUser: false,
            isSystem: true
          }]);
        };

        websocket.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          setIsConnected(false);
          setConnectionStatus('Connection error');
        };

        websocket.onclose = (event) => {
          console.log('🔌 WebSocket closed:', event.code, event.reason);
          setIsConnected(false);
          setConnectionStatus('Disconnected');
          
          // Try to reconnect after 3 seconds
          setTimeout(() => {
            console.log('🔄 Attempting to reconnect...');
            initializeChat();
          }, 3000);
        };

        websocket.onmessage = (event) => {
          console.log('📨 Received message:', event.data);
          setIsLoading(false);
          
          try {
            const data = JSON.parse(event.data);
            
            setMessages(prev => [...prev, {
              text: data.response || data.message || "No response received",
              isUser: false,
              sources: data.sources || [],
              error: data.error || null
            }]);
          } catch (e) {
            console.error('Error parsing message:', e);
            setMessages(prev => [...prev, {
              text: "Error: Could not parse server response",
              isUser: false,
              error: true
            }]);
          }
        };

        setWs(websocket);
      } catch (error) {
        console.error('❌ Failed to initialize chat:', error);
        setConnectionStatus(`Failed to connect: ${error.message}`);
        setIsConnected(false);
        
        setMessages([{
          text: `❌ Failed to connect to the server: ${error.message}. Make sure the backend is running on port 8001.`,
          isUser: false,
          isSystem: true,
          error: true
        }]);
      }
    };

    initializeChat();

    // Cleanup function
    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('🧹 Cleaning up WebSocket connection...');
        ws.close();
      }
    };
  }, []); // Empty dependency array - only run once on mount

  // Debug info logger
  useEffect(() => {
    console.log('📊 Connection state changed:', {
      isConnected,
      connectionStatus,
      wsState: ws?.readyState,
      wsStateText: ws ? ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][ws.readyState] : 'NO_WS'
    });
  }, [isConnected, connectionStatus, ws]);

  const sendMessage = () => {
    if (inputMessage.trim() && ws && ws.readyState === WebSocket.OPEN) {
      console.log('📤 Sending message:', inputMessage);
      
      // Add user message to chat
      setMessages(prev => [...prev, { text: inputMessage, isUser: true }]);
      setIsLoading(true);
      
      // Send message through WebSocket
      try {
        ws.send(JSON.stringify({
          message: inputMessage,
          session_id: 'default-session',
          timestamp: new Date().toISOString()
        }));
        
        setInputMessage('');
      } catch (error) {
        console.error('Failed to send message:', error);
        setIsLoading(false);
        setMessages(prev => [...prev, {
          text: "Failed to send message. Please try again.",
          isUser: false,
          error: true
        }]);
      }
    } else {
      console.warn('⚠️ Cannot send message:', {
        hasInput: !!inputMessage.trim(),
        hasWs: !!ws,
        wsState: ws?.readyState
      });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Debug Panel Component
  const DebugPanel = () => (
    <div style={{
      position: 'fixed',
      bottom: 20,
      right: 20,
      background: 'rgba(0, 0, 0, 0.85)',
      color: '#fff',
      padding: '15px',
      borderRadius: '8px',
      fontSize: '12px',
      fontFamily: 'monospace',
      boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
      maxWidth: '300px',
      zIndex: 1000
    }}>
      <div style={{ marginBottom: '10px', fontWeight: 'bold', borderBottom: '1px solid #444', paddingBottom: '5px' }}>
        🔧 Debug Panel
      </div>
      <div>🔌 Connected: {isConnected ? '✅ Yes' : '❌ No'}</div>
      <div>📡 Status: {connectionStatus}</div>
      <div>🌐 WebSocket: {ws ? ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][ws.readyState] : 'Not initialized'}</div>
      <div>🔗 Backend: http://localhost:8001</div>
      <div>📬 Messages: {messages.length}</div>
      <div style={{ marginTop: '10px', display: 'flex', gap: '5px' }}>
        <button 
          onClick={() => window.location.reload()} 
          style={{
            padding: '5px 10px',
            background: '#4CAF50',
            border: 'none',
            borderRadius: '4px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '11px'
          }}
        >
          🔄 Reload
        </button>
        <button 
          onClick={() => {
            if (ws) ws.close();
            window.location.reload();
          }} 
          style={{
            padding: '5px 10px',
            background: '#ff5722',
            border: 'none',
            borderRadius: '4px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '11px'
          }}
        >
          🔌 Reconnect
        </button>
      </div>
    </div>
  );

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>AI Assistant</h1>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          <span className="status-dot"></span>
          {connectionStatus}
        </div>
      </div>
      
      <div className="messages-container">
        {messages.length === 0 && !isConnected && (
          <div className="loading-message">
            <div className="spinner"></div>
            <p>Connecting to AI assistant...</p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.isUser ? 'user-message' : 'assistant-message'} ${message.isSystem ? 'system-message' : ''} ${message.error ? 'error-message' : ''}`}
          >
            {message.isUser ? (
              <div className="message-content">
                <div className="message-text">{message.text}</div>
              </div>
            ) : (
              <div className="message-content">
                <ReactMarkdown className="message-text">{message.text}</ReactMarkdown>
                {message.sources && message.sources.length > 0 && (
                  <div className="sources">
                    <div className="sources-header">📚 Sources:</div>
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="source">
                        <span className="source-icon">📄</span>
                        {source.metadata?.source || source.page_content?.substring(0, 100) || 'Unknown source'}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant-message">
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
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            isConnected 
              ? "Type your message here... (Press Enter to send, Shift+Enter for new line)" 
              : "Connecting to server..."
          }
          disabled={!isConnected}
          className="message-input"
          rows="3"
        />
        <button 
          onClick={sendMessage} 
          disabled={!isConnected || !inputMessage.trim() || isLoading}
          className={`send-button ${(!isConnected || !inputMessage.trim() || isLoading) ? 'disabled' : ''}`}
        >
          {isLoading ? (
            <span className="button-loading">⏳</span>
          ) : (
            <span>Send 📤</span>
          )}
        </button>
      </div>
      
      {/* Debug panel - remove or comment out in production */}
      <DebugPanel />
    </div>
  );
};

export default Chat;