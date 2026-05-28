// src/hooks/useChat.js
import { useState, useCallback } from 'react';
import { sendQuery } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastQueryMs, setLastQueryMs] = useState(null);

  const addMessage = useCallback((msg) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  const sendMessage = useCallback(async (text) => {
    // 1. add user message
    const userMsg = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      data: null,
      intent: null,
      timing: null,
      timestamp: new Date(),
    };
    addMessage(userMsg);
    setIsLoading(true);
    try {
      const response = await sendQuery(text);
      if (response && response.timing && response.timing.total_ms !== undefined) {
        setLastQueryMs(response.timing.total_ms);
      }
      const assistantMsg = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.answer,
        data: response.data ?? [],
        intent: response.intent ?? {},
        timing: response.timing ?? {},
        timestamp: new Date(),
      };
      addMessage(assistantMsg);
    } catch (err) {
      const errorMsg = {
        id: crypto.randomUUID(),
        role: 'error',
        content: err?.message || 'Something went wrong. Please try again.',
        data: null,
        intent: null,
        timing: null,
        timestamp: new Date(),
      };
      addMessage(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [addMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, isLoading, sendMessage, clearMessages, lastQueryMs };
};
