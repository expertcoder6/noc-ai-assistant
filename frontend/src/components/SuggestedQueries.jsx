import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Zap, Server, Activity, Cpu, GitCommit, Bell, Clock, ChevronLeft, ChevronRight } from 'lucide-react';

const CATEGORIES = [
  {
    label: 'Device Status',
    icon: Server,
    color: 'text-emerald-400',
    borderColor: 'border-emerald-500/20',
    queries: [
      'Which routers are down?',
      'Show degraded switches',
      'List all devices that are up',
    ],
  },
  {
    label: 'Interfaces',
    icon: Activity,
    color: 'text-cyan-400',
    borderColor: 'border-cyan-500/20',
    queries: [
      'Show interfaces with packet loss above 5%',
      'List highly utilized interfaces',
      'Are there any interfaces with errors?',
    ],
  },
  {
    label: 'CPU / Memory',
    icon: Cpu,
    color: 'text-violet-400',
    borderColor: 'border-violet-500/20',
    queries: [
      'Show devices with CPU above 80%',
      'List switches with high memory',
      'Show temperature above 60°C',
    ],
  },
  {
    label: 'Config Changes',
    icon: GitCommit,
    color: 'text-amber-400',
    borderColor: 'border-amber-500/20',
    queries: [
      'Who changed configs today?',
      'Show config changes last 48 hours',
      'Show changes on dal-rtr-core-01',
    ],
  },
  {
    label: 'Alerts',
    icon: Bell,
    color: 'text-rose-400',
    borderColor: 'border-rose-500/20',
    queries: [
      'Show critical alerts',
      'Are there any warning alerts?',
      'Give me an alert summary',
    ],
  },
  {
    label: 'Uptime',
    icon: Clock,
    color: 'text-sky-400',
    borderColor: 'border-sky-500/20',
    queries: [
      'What is the uptime of dal-rtr-core-01?',
      'Show device uptimes in Chicago',
      'List uptime for all routers',
    ],
  },
];

// Role-based category filtering
const ROLE_CATEGORIES = {
  admin: [0, 1, 2, 3, 4, 5],
  network_engineer: [0, 1, 2, 3, 5],
  security_team: [0, 4],
  network_operator: [0, 1, 2, 3, 4, 5],
};

export const SuggestedQueries = ({ onSelect }) => {
  const { user } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  if (!user) return null;

  const role = (user.role || 'network_operator').toLowerCase();
  const allowedIdxs = ROLE_CATEGORIES[role] ?? ROLE_CATEGORIES['network_operator'];
  const visibleCategories = CATEGORIES.filter((_, i) => allowedIdxs.includes(i));

  return (
    <aside
      className={`
        relative flex-shrink-0 flex flex-col
        bg-slate-950/80 border-r border-slate-900
        transition-all duration-300 ease-in-out
        ${collapsed ? 'w-10' : 'w-56'}
        overflow-hidden
      `}
    >
      {/* Collapse toggle button */}
      <button
        type="button"
        onClick={() => setCollapsed(c => !c)}
        title={collapsed ? 'Expand query panel' : 'Collapse query panel'}
        className="
          absolute top-3 right-2 z-10
          p-1 rounded-lg
          text-slate-500 hover:text-slate-300
          hover:bg-slate-800/60
          transition-all duration-200
          cursor-pointer
        "
      >
        {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>

      {/* Panel content — hidden when collapsed */}
      <div
        className={`
          flex flex-col h-full overflow-y-auto
          transition-opacity duration-200
          ${collapsed ? 'opacity-0 pointer-events-none' : 'opacity-100'}
          scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-800
        `}
      >
        {/* Panel Header */}
        <div className="px-3 pt-4 pb-3 border-b border-slate-900 shrink-0">
          <div className="flex items-center gap-1.5">
            <Zap className="w-3 h-3 text-emerald-500 shrink-0" />
            <span className="text-[9px] font-mono font-bold uppercase tracking-widest text-emerald-500">
              Quick Queries
            </span>
          </div>
          <p className="text-[9px] text-slate-600 font-mono mt-0.5 uppercase tracking-wider">
            {role.replace('_', ' ')}
          </p>
        </div>

        {/* Categories + chips */}
        <div className="flex flex-col gap-0 py-2 px-2">
          {visibleCategories.map((cat) => {
            const Icon = cat.icon;
            return (
              <div key={cat.label} className="mb-3">
                {/* Category label */}
                <div className={`flex items-center gap-1.5 mb-1.5 px-1`}>
                  <Icon className={`w-3 h-3 shrink-0 ${cat.color}`} />
                  <span className={`text-[9px] font-mono font-bold uppercase tracking-wider ${cat.color}`}>
                    {cat.label}
                  </span>
                </div>

                {/* Query chips */}
                <div className="flex flex-col gap-1">
                  {cat.queries.map((q, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => onSelect(q)}
                      title={q}
                      className={`
                        w-full text-left
                        bg-slate-900/50 hover:bg-slate-800/80
                        border ${cat.borderColor} hover:border-slate-700
                        text-slate-400 hover:text-slate-200
                        rounded-lg px-2.5 py-1.5
                        text-[10px] font-mono leading-snug
                        transition-all duration-150
                        cursor-pointer
                        active:scale-[0.98]
                        truncate
                      `}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Collapsed state — show only icons */}
      {collapsed && (
        <div className="flex flex-col items-center gap-3 pt-12 px-1">
          {visibleCategories.map((cat) => {
            const Icon = cat.icon;
            return (
              <div key={cat.label} title={cat.label}>
                <Icon className={`w-4 h-4 ${cat.color} opacity-60`} />
              </div>
            );
          })}
        </div>
      )}
    </aside>
  );
};
