// Action types
export const ACTIONS = {
  SET_BOT_STATUS: 'SET_BOT_STATUS',
  SET_CONFIG: 'SET_CONFIG',
  SET_LOGS: 'SET_LOGS',
  ADD_LOG: 'ADD_LOG',
  SET_TRACKING: 'SET_TRACKING',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Initial state
export const initialState = {
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
};

// Reducer
export const appReducer = (state, action) => {
  switch (action.type) {
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

    default:
      return state;
  }
};

