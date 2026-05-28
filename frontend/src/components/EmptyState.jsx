import React from 'react';
import { SuggestedQueries } from './SuggestedQueries';

export const EmptyState = ({ onSelectQuery }) => {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12 flex flex-col items-center select-none animate-in fade-in duration-300">
      {/* Title */}
      <h2 className="text-3xl font-bold tracking-tight text-slate-100 mb-2 font-mono">
        NetOps AI Assistant
      </h2>
      {/* Subtitle */}
      <p className="text-slate-400 text-sm mb-8 text-center max-w-md leading-relaxed">
        Ask anything about your network infrastructure
      </p>

      {/* Two Static Info Cards Side by Side */}
      <div className="grid grid-cols-2 gap-4 w-full max-w-md mb-8">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center justify-center gap-2.5 shadow-md">
          <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse shrink-0"></span>
          <span className="text-xs font-mono font-bold text-slate-300">AI Ready</span>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center justify-center gap-2.5 shadow-md">
          <span className="h-2 w-2 rounded-full bg-cyan-500 shrink-0"></span>
          <span className="text-xs font-mono font-bold text-slate-300">DB Connected</span>
        </div>
      </div>

      {/* Suggested Queries */}
      <SuggestedQueries onSelect={onSelectQuery} />
    </div>
  );
};
