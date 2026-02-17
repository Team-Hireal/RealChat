// Action types
export const ACTIONS = {
  SET_BOT_STATUS: 'SET_BOT_STATUS',
  SET_CONFIG: 'SET_CONFIG',
  SET_LOGS: 'SET_LOGS',
  ADD_LOG: 'ADD_LOG',
  CLEAR_LOGS: 'CLEAR_LOGS',
  SET_TRACKING: 'SET_TRACKING',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_CURRENT_CHAT: 'SET_CURRENT_CHAT',
  SET_SOCKET_CONNECTED: 'SET_SOCKET_CONNECTED',
  SET_CHAT_SESSIONS: 'SET_CHAT_SESSIONS',
  SET_ACTIVE_CHAT: 'SET_ACTIVE_CHAT',
  ENSURE_CHAT_SESSION: 'ENSURE_CHAT_SESSION',
  ADD_MESSAGE_TO_SESSION: 'ADD_MESSAGE_TO_SESSION',
  REPLACE_SESSION_MESSAGES: 'REPLACE_SESSION_MESSAGES',
  SET_MODE: 'SET_MODE',
};

// Initial state
export const initialState = {
  mode: typeof window !== 'undefined'
    ? (localStorage.getItem('realchat_mode') || 'consumer')
    : 'consumer',
  botStatus: {
    running: false,
    pid: null,
  },
  config: {
    chat_name: '',
    user_name: '',
    user_title: '',
    intro_template: "Hi! I'm {{NAME}}, {{TITLE}}. It was great meeting you! Let's stay in touch.",
    default_reply: 'Thanks for your message!',
    reply_mode: 'c',
    dry_run: 'yes',
  },
  logs: [],
  tracking: [],
  loading: {
    config: false,
    status: false,
    logs: false,
    tracking: false,
    starting: false,
    stopping: false,
  },
  error: null,
  currentChat: {
    chat: 'No active chat',
    detected: false,
  },
  socketConnected: false,
  chatSessions: {},   // { chatName: messages[] }
  activeChat: null,
};

// Reducer
export const appReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.SET_MODE:
      localStorage.setItem('realchat_mode', action.payload);
      return {
        ...state,
        mode: action.payload,
      };

    case ACTIONS.SET_BOT_STATUS:
      return {
        ...state,
        botStatus: action.payload,
      };

    case ACTIONS.SET_CONFIG:
      return {
        ...state,
        config: action.payload,
      };

    case ACTIONS.SET_LOGS:
      return {
        ...state,
        logs: action.payload,
      };

    case ACTIONS.ADD_LOG:
      return {
        ...state,
        logs: [...state.logs, action.payload],
      };

    case ACTIONS.CLEAR_LOGS:
      return {
        ...state,
        logs: [],
      };

    case ACTIONS.SET_TRACKING:
      return {
        ...state,
        tracking: action.payload,
      };

    case ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: {
          ...state.loading,
          ...action.payload,
        },
      };

    case ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
      };

    case ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    case ACTIONS.SET_CURRENT_CHAT:
      return {
        ...state,
        currentChat: action.payload,
      };

    case ACTIONS.SET_SOCKET_CONNECTED:
      return {
        ...state,
        socketConnected: action.payload,
      };

    case ACTIONS.SET_CHAT_SESSIONS:
      return {
        ...state,
        chatSessions: action.payload,
      };

    case ACTIONS.SET_ACTIVE_CHAT:
      return {
        ...state,
        activeChat: action.payload,
      };

    case ACTIONS.ENSURE_CHAT_SESSION:
      if (state.chatSessions[action.payload]) return state;
      return {
        ...state,
        chatSessions: { ...state.chatSessions, [action.payload]: [] },
      };

    case ACTIONS.ADD_MESSAGE_TO_SESSION: {
      const { chatName, message } = action.payload;
      return {
        ...state,
        chatSessions: {
          ...state.chatSessions,
          [chatName]: [...(state.chatSessions[chatName] || []), message],
        },
      };
    }

    case ACTIONS.REPLACE_SESSION_MESSAGES: {
      const { chatName: cn, messages: msgs } = action.payload;
      return {
        ...state,
        chatSessions: { ...state.chatSessions, [cn]: msgs },
      };
    }

    default:
      return state;
  }
};

