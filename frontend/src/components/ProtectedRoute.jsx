import React from 'react';
import { LoginPage } from '../pages/LoginPage';

export const ProtectedRoute = ({ user, loading, login, authActionLoading, error, children }) => {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-slate-950 text-slate-300">
        <div className="relative flex items-center justify-center mb-4">
          {/* NOC Radar spin */}
          <div className="w-16 h-16 border border-emerald-500/20 rounded-full animate-ping absolute"></div>
          <div className="w-12 h-12 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <div className="font-mono text-xs uppercase tracking-widest text-emerald-500 animate-pulse">
          Initializing NOC Security Protocol...
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <LoginPage
        login={login}
        authActionLoading={authActionLoading}
        error={error}
      />
    );
  }

  return children;
};
