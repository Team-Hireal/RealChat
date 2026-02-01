import { useAppContext } from '../context/AppContext';
import { ACTIONS } from '../context/AppReducer';
import apiService from '../services/api';

export const useConfig = () => {
  const { state, dispatch } = useAppContext();

  const loadConfig = async () => {
    dispatch({ type: ACTIONS.SET_LOADING, payload: { config: true } });

    try {
      const response = await apiService.getConfig();
      dispatch({ type: ACTIONS.SET_CONFIG, payload: response.data });
    } catch (error) {
      console.error('Failed to load config:', error);
      dispatch({ type: ACTIONS.SET_ERROR, payload: 'Failed to load configuration' });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: { config: false } });
    }
  };

  const saveConfig = async (config) => {
    dispatch({ type: ACTIONS.SET_LOADING, payload: { config: true } });
    dispatch({ type: ACTIONS.CLEAR_ERROR });

    try {
      const response = await apiService.updateConfig(config);
      if (response.data.success) {
        dispatch({ type: ACTIONS.SET_CONFIG, payload: config });
        return { success: true };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      dispatch({ type: ACTIONS.SET_ERROR, payload: errorMessage });
      return { success: false, error: errorMessage };
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: { config: false } });
    }
  };

  return {
    config: state.config,
    loadConfig,
    saveConfig,
    isLoading: state.loading.config,
  };
};

export default useConfig;
