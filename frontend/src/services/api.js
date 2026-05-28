// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
});

// Add dev API key header
if (import.meta.env.DEV) {
  api.interceptors.request.use((config) => {
    config.headers['X-API-Key'] = 'dev-key-123';
    return config;
  });
}

// Response interceptors for common error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error;
    if (!response) {
      return Promise.reject(new Error('Network connection failed. Please check your connection.'));
    }
    
    switch (response.status) {
      case 401:
        // For unauthorized requests, let the caller handle it (e.g. useAuth will clear user state)
        // If a request fails with 401 when the page is active, we reload to drop back to login
        if (window.location.pathname !== '/' || response.config.url !== '/me') {
          window.location.reload();
        }
        return Promise.reject(new Error('Session expired or unauthorized. Please log in again.'));
      case 429:
        return Promise.reject(new Error('Rate limit reached (10 queries/min). Please wait a moment.'));
      case 504:
        return Promise.reject(new Error('Database query timed out (exceeded 5s SLA). Try a more specific question.'));
      case 501:
        return Promise.reject(new Error('Endpoint not implemented yet.'));
      default:
        const errMsg = response.data?.detail || response.data?.error || 'Internal Server Error.';
        return Promise.reject(new Error(errMsg));
    }
  }
);

export const sendQuery = async (message) => {
  try {
    const res = await api.post('/query', { message });
    return res.data;
  } catch (error) {
    const response = error.response;
    if (!response) {
      throw new Error("Connection lost. Please check your network.");
    }
    
    const status = response.status;
    const detail = response.data?.detail;
    
    if (status === 400) {
      const code = response.data?.code || (detail && typeof detail === 'object' ? detail.code : null);
      const detailStr = detail && typeof detail === 'object' ? detail.error : detail;
      if (code === 'SECURITY_BLOCKED' || String(detailStr).includes('SECURITY_BLOCKED') || String(detail).includes('SECURITY_BLOCKED')) {
        throw new Error("That query was blocked by the security policy.");
      }
    }
    
    if (status === 401) {
      throw new Error("Your session has expired. Please log in again.");
    }
    if (status === 403) {
      throw new Error("You don't have permission to run this query.");
    }
    if (status === 429) {
      throw new Error("Too many requests. Please wait a moment before trying again.");
    }
    if (status === 503) {
      throw new Error("The AI service is temporarily unavailable. Please try again in a few seconds.");
    }
    
    throw new Error("Something went wrong. Please try again.");
  }
};

export const getIntents = async () => {
  const res = await api.get('/intents');
  return res.data;
};

export const getHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const getMe = async () => {
  const res = await api.get('/me');
  return res.data;
};

export default api;
