import { useAppContext } from '../context/AppContext';
import './CurrentChatDisplay.css';

const CurrentChatDisplay = () => {
  const { state } = useAppContext();
  const { currentChat, socketConnected } = state;

  return (
    <div className="current-chat-display">
      <div className="current-chat-row">
        <div className="current-chat-left">
          <span className="current-chat-icon">💬</span>
          <div className="current-chat-info">
            <span className="current-chat-label">Current Chat:</span>
            <span className="current-chat-name">{currentChat.chat}</span>
          </div>
        </div>
        <div className="current-chat-badges">
          {currentChat.detected && <span className="badge live">Live</span>}
          <span className={`badge connection ${socketConnected ? 'connected' : 'disconnected'}`}>
            {socketConnected ? '● WS' : '○ WS'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default CurrentChatDisplay;
