import React from 'react';
import { User, LogOut, Shield, ShieldCheck } from 'lucide-react';

export const UserBadge = ({ user, onLogout }) => {
  if (!user) return null;

  const isAdmin = user.role === 'admin';

  return (
    <div className="flex items-center gap-3 pl-3 py-1 bg-slate-900 border border-slate-800 rounded-xl max-w-xs transition-all shadow-inner">
      <div className="relative">
        <div className="p-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-slate-300">
          {isAdmin ? (
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          ) : (
            <Shield className="w-4 h-4 text-cyan-400" />
          )}
        </div>
        {/* Pulse online indicator */}
        <span className="absolute bottom-0 right-0 block h-2 w-2 rounded-full bg-emerald-500 ring-2 ring-slate-900 animate-pulse"></span>
      </div>

      <div className="flex flex-col shrink-0 pr-1">
        <span className="text-xs font-semibold font-mono text-slate-200">
          {user.username}
        </span>
        <span className="text-[9px] uppercase tracking-wider text-slate-500 font-bold font-mono">
          {isAdmin ? 'SYS_ADMIN' : 'NOC_OPERATOR'}
        </span>
      </div>

      <button
        onClick={onLogout}
        title="Terminate Session"
        className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-950/20 border-l border-slate-800 hover:border-red-950/40 rounded-r-xl transition-all cursor-pointer grow-0 h-full flex items-center justify-center shrink-0 self-stretch"
      >
        <LogOut className="w-4 h-4" />
      </button>
    </div>
  );
};
