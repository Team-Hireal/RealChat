import { useState } from 'react';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const callApi = async (apiFunction, ...args) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiFunction(...args);
      setLoading(false);
      return { data: response.data, error: null };
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'An error occurred';
      setError(errorMessage);
      setLoading(false);
      return { data: null, error: errorMessage };
    }
  };

  return { loading, error, callApi };
};

export default useApi;
