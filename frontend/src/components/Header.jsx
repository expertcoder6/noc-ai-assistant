import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { UserBadge } from './UserBadge';
import { Network, Activity, Cpu, Database } from 'lucide-react';

export const Header = ({ lastQueryMs }) => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-slate-950/80 border-b border-slate-900 h-16 flex items-center justify-between px-6 shadow-lg backdrop-blur-md sticky top-0 z-40">
      {/* Brand Logo & Name */}
      <div className="flex items-center gap-2.5 shrink-0">
        <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
          <Network className="w-5 h-5 animate-pulse" />
        </div>
        <div className="flex flex-col">
          <span className="font-bold tracking-tight text-slate-100 text-sm">
            NOC AI OPERATIONS
          </span>
          <span className="text-[9px] uppercase tracking-wider text-emerald-500 font-bold font-mono flex items-center gap-1">
            <Activity className="w-2.5 h-2.5 shrink-0" /> Systems Operational
          </span>
        </div>
      </div>

      {/* Observability Live Badges Panel */}
      {user && (
        <div className="hidden md:flex items-center gap-3.5">
          {/* AI Status */}
          <div className="border-slate-800 bg-slate-900 text-slate-300 text-xs font-mono px-2 py-1 rounded-full border flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse shrink-0"></span>
            <span>AI ONLINE</span>
          </div>

          {/* DB Status */}
          <div className="border-slate-800 bg-slate-900 text-slate-300 text-xs font-mono px-2 py-1 rounded-full border flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-cyan-500 shrink-0"></span>
            <span>DB CONNECTED</span>
          </div>

          {/* Role Badge */}
          {(() => {
            const getRoleDetails = (role) => {
              const r = String(role || '').toLowerCase();
              if (r === 'network_operator') return { text: 'NOC_OPERATOR', classes: 'border-blue-500/30 bg-blue-500/10 text-blue-400' };
              if (r === 'network_engineer') return { text: 'NETWORK_ENGINEER', classes: 'border-purple-500/30 bg-purple-500/10 text-purple-400' };
              if (r === 'security_team') return { text: 'SECURITY_TEAM', classes: 'border-orange-500/30 bg-orange-500/10 text-orange-400' };
              if (r === 'admin') return { text: 'ADMIN', classes: 'border-red-500/30 bg-red-500/10 text-red-400' };
              return { text: String(role || '').toUpperCase(), classes: 'border-slate-800 bg-slate-900 text-slate-400' };
            };
            const details = getRoleDetails(user.role);
            return (
              <div className={`text-xs font-mono px-2 py-1 rounded-full border flex items-center shrink-0 ${details.classes}`}>
                {details.text}
              </div>
            );
          })()}

          {/* Latency Badge */}
          {(() => {
            const getLatencyClasses = (ms) => {
              if (ms === null || ms === undefined) return 'border-slate-800 bg-slate-900 text-slate-500';
              if (ms < 1000) return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400';
              if (ms <= 3000) return 'border-amber-500/30 bg-amber-500/10 text-amber-400';
              return 'border-rose-500/30 bg-rose-500/10 text-rose-400';
            };
            const classes = getLatencyClasses(lastQueryMs);
            const text = lastQueryMs !== null && lastQueryMs !== undefined ? `${lastQueryMs}ms` : '—';
            return (
              <div className={`text-xs font-mono px-2 py-1 rounded-full border flex items-center shrink-0 ${classes}`}>
                {text}
              </div>
            );
          })()}
        </div>
      )}

      {/* User Badge Component */}
      {user && <UserBadge user={user} onLogout={logout} />}
    </header>
  );
};
