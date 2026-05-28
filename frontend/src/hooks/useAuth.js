// src/hooks/useAuth.js
import { useState, useEffect, useCallback } from 'react';
import api, { getMe } from '../services/api';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [authActionLoading, setAuthActionLoading] = useState(false);

  // Restore session on refresh
  const restoreSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMe();
      setUser(data);
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Login action
  const login = useCallback(async (username, password) => {
    setAuthActionLoading(true);
    setError(null);
    try {
      const res = await api.post('/auth/login', { username, password });
      setUser(res.data.user);
      return res.data.user;
    } catch (err) {
      const errMsg = err?.response?.data?.detail || 'Invalid username or password.';
      setError(errMsg);
      throw new Error(errMsg);
    } finally {
      setAuthActionLoading(false);
    }
  }, []);

  // Logout action
  const logout = useCallback(async () => {
    setAuthActionLoading(true);
    try {
      await api.post('/auth/logout');
    } catch (err) {
      console.error('API logout failed', err);
    } finally {
      setUser(null);
      setAuthActionLoading(false);
      // Trigger full page reload to clear state and redirect to login
      window.location.reload();
    }
  }, []);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  return {
    user,
    loading,
    error,
    authActionLoading,
    login,
    logout,
    restoreSession,
  };
};
