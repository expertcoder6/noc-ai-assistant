import React from 'react';
import { Terminal } from 'lucide-react';

export const TypingIndicator = () => (
  <div className="flex gap-4 max-w-xs self-start w-full animate-in fade-in duration-200">
    {/* Bot Avatar Icon */}
    <div className="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center shrink-0 text-emerald-400 shadow-md">
      <Terminal className="w-4 h-4" />
    </div>

    <div className="flex flex-col gap-1 flex-1">
      <div className="bg-slate-900 border border-slate-850 px-4 py-3 rounded-2xl rounded-tl-none flex items-center gap-1.5 shadow-lg shadow-slate-950/20 w-fit">
        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0ms', animationDuration: '0.8s' }} />
        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '150ms', animationDuration: '0.8s' }} />
        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '300ms', animationDuration: '0.8s' }} />
        
        <span className="text-[10px] font-mono text-slate-500 ml-1.5 uppercase tracking-wider font-bold">
          Running inference...
        </span>
      </div>
    </div>
  </div>
);
