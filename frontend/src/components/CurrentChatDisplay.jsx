import { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import './CurrentChatDisplay.css';

const CurrentChatDisplay = () => {
  const [currentChat, setCurrentChat] = useState('No active chat');
  const [isDetected, setIsDetected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';
    const socket = io(API_BASE, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    socket.on('connect', () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setIsLoading(false);
    });

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    });

    socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      setIsConnected(false);
      setIsLoading(false);
    });

    // Listen for current chat updates
    socket.on('current_chat_update', (data) => {
      setCurrentChat(data.chat);
      setIsDetected(data.detected);
      setIsLoading(false);
    });

    // Cleanup on unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="current-chat-display">
      <div className="current-chat-row">
        <div className="current-chat-left">
          <span className="current-chat-icon">💬</span>
          <div className="current-chat-info">
            <span className="current-chat-label">Current Chat:</span>
            {isLoading ? (
              <span className="current-chat-name loading">Detecting...</span>
            ) : (
              <span className="current-chat-name">{currentChat}</span>
            )}
          </div>
        </div>
        <div className="current-chat-badges">
          {isDetected && <span className="badge live">Live</span>}
          <span className={`badge connection ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '● WS' : '○ WS'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default CurrentChatDisplay;
