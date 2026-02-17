import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { axiosInstance as api, setAuthToken } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount, check for stored token and validate it
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setAuthToken(token);
      api.get('/auth/me')
        .then(res => setUser(res.data.user))
        .catch(() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          setAuthToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    console.log('[Auth] login called with:', { email });
    console.log('[Auth] API baseURL:', api.defaults.baseURL);
    try {
      const res = await api.post('/auth/login', { email, password });
      console.log('[Auth] login response:', res.status, res.data);
      const { user: u, access_token, refresh_token } = res.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setAuthToken(access_token);
      setUser(u);
      return u;
    } catch (err) {
      console.error('[Auth] login error:', {
        message: err.message,
        code: err.code,
        status: err.response?.status,
        data: err.response?.data,
        config: { url: err.config?.url, baseURL: err.config?.baseURL, method: err.config?.method },
      });
      throw err;
    }
  }, []);

  const signup = useCallback(async (email, password, name) => {
    console.log('[Auth] signup called with:', { email, name, passwordLength: password.length });
    console.log('[Auth] API baseURL:', api.defaults.baseURL);
    try {
      const res = await api.post('/auth/signup', { email, password, name });
      console.log('[Auth] signup response:', res.status, res.data);
      const { user: u, access_token, refresh_token } = res.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setAuthToken(access_token);
      setUser(u);
      return u;
    } catch (err) {
      console.error('[Auth] signup error:', {
        message: err.message,
        code: err.code,
        status: err.response?.status,
        data: err.response?.data,
        config: { url: err.config?.url, baseURL: err.config?.baseURL, method: err.config?.method },
      });
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setAuthToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
