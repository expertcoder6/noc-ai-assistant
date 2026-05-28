import React from 'react';
import { useAuth } from './hooks/useAuth';
import { ProtectedRoute } from './components/ProtectedRoute';
import { ChatContainer } from './components/ChatContainer';

export const App = () => {
  const { user, loading, error, authActionLoading, login } = useAuth();

  return (
    <ProtectedRoute
      user={user}
      loading={loading}
      login={login}
      authActionLoading={authActionLoading}
      error={error}
    >
      <ChatContainer />
    </ProtectedRoute>
  );
};
