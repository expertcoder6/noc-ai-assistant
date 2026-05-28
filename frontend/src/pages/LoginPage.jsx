import React, { useState } from 'react';
import { Shield, Key, User, Activity, AlertCircle } from 'lucide-react';

export const LoginPage = ({ login, authActionLoading, error }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidationError('');
    if (!username.trim() || !password.trim()) {
      setValidationError('Username and password are required.');
      return;
    }
    try {
      await login(username, password);
    } catch (err) {
      // Error handled by hook state
    }
  };

  const handleQuickSelect = (u, p) => {
    setUsername(u);
    setPassword(p);
    setValidationError('');
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-950 text-slate-100 relative overflow-hidden">
      {/* Background Grid Effects */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#022c22_1px,transparent_1px),linear-gradient(to_bottom,#022c22_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30"></div>
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="relative w-full max-w-md p-8 bg-slate-900/80 border border-slate-800 rounded-2xl shadow-2xl backdrop-blur-md">
        {/* Logo and Header */}
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl mb-4 text-emerald-400">
            <Shield className="w-8 h-8 animate-pulse" />
          </div>
          <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
            NOC AI OPERATIONS
          </h1>
          <p className="text-xs text-slate-400 uppercase tracking-widest mt-1 flex items-center gap-1 font-mono">
            <Activity className="w-3.5 h-3.5 text-emerald-500" /> Secure Terminal Session
          </p>
        </div>

        {/* Errors */}
        {(error || validationError) && (
          <div className="flex items-start gap-2.5 p-3.5 mb-6 text-sm bg-red-950/40 border border-red-800/50 text-red-300 rounded-lg">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{validationError || error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2 font-mono">
              Operator Username
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500/50 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-emerald-500/30 transition-all font-mono"
                placeholder="operator_id"
                disabled={authActionLoading}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2 font-mono">
              Access Password
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500/50 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-emerald-500/30 transition-all font-mono"
                placeholder="••••••••"
                disabled={authActionLoading}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={authActionLoading}
            className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500/40 shadow-lg shadow-emerald-950/50 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {authActionLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <>Authenticate Access</>
            )}
          </button>
        </form>

        {/* Quick Credentials Panel for Demos */}
        <div className="mt-8 pt-6 border-t border-slate-800/80">
          <div className="text-xs font-semibold tracking-wider uppercase text-slate-500 mb-3 text-center font-mono">
            Demo Operator Credentials
          </div>
          <div className="grid grid-cols-2 gap-3.5">
            <button
              type="button"
              onClick={() => handleQuickSelect('admin', 'admin123')}
              className="flex flex-col items-center p-2.5 bg-slate-950 border border-slate-800 hover:border-slate-700/85 hover:bg-slate-900 rounded-xl text-left transition-all cursor-pointer group"
            >
              <span className="text-[11px] font-mono text-emerald-400 font-bold group-hover:text-emerald-300">
                admin
              </span>
              <span className="text-[9px] text-slate-500 mt-0.5">
                Role: Administrator
              </span>
            </button>

            <button
              type="button"
              onClick={() => handleQuickSelect('nocuser', 'noc123')}
              className="flex flex-col items-center p-2.5 bg-slate-950 border border-slate-800 hover:border-slate-700/85 hover:bg-slate-900 rounded-xl text-left transition-all cursor-pointer group"
            >
              <span className="text-[11px] font-mono text-cyan-400 font-bold group-hover:text-cyan-300">
                nocuser
              </span>
              <span className="text-[9px] text-slate-500 mt-0.5">
                Role: NOC Operator
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
