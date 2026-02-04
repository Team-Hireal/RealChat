import { useAppContext } from '../context/AppContext';
import { ACTIONS } from '../context/AppReducer';
import apiService from '../services/api';

export const useBotControl = () => {
  const { state, dispatch } = useAppContext();

  const startBot = async (chat = 'File Transfer') => {
    dispatch({ type: ACTIONS.SET_LOADING, payload: { starting: true } });
    dispatch({ type: ACTIONS.CLEAR_ERROR });

    try {
      const response = await apiService.startAgent(chat);
      if (response.data.success) {
        dispatch({ type: ACTIONS.SET_BOT_STATUS, payload: { running: true, agent_running: true } });
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      dispatch({ type: ACTIONS.SET_ERROR, payload: errorMessage });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: { starting: false } });
    }
  };

  const stopBot = async () => {
    dispatch({ type: ACTIONS.SET_LOADING, payload: { stopping: true } });
    dispatch({ type: ACTIONS.CLEAR_ERROR });

    try {
      const response = await apiService.stopAgent();
      if (response.data.success) {
        dispatch({ type: ACTIONS.SET_BOT_STATUS, payload: { running: false, agent_running: false, pid: null } });
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      dispatch({ type: ACTIONS.SET_ERROR, payload: errorMessage });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: { stopping: false } });
    }
  };

  const refreshStatus = async () => {
    try {
      const response = await apiService.getStatus();
      dispatch({ type: ACTIONS.SET_BOT_STATUS, payload: response.data });
    } catch (error) {
      console.error('Failed to refresh status:', error);
    }
  };

  return {
    startBot,
    stopBot,
    refreshStatus,
    isStarting: state.loading.starting,
    isStopping: state.loading.stopping,
  };
};

export default useBotControl;
