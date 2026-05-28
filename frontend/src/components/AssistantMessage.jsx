import React from 'react';
import { DataTable } from './DataTable';
import { TimingBadge } from './TimingBadge';
import { Terminal, Network } from 'lucide-react';

export const AssistantMessage = ({ message }) => {
  const { content, data, intent, timing } = message;

  return (
    <div className="flex gap-4 max-w-3xl self-start w-full group animate-in fade-in slide-in-from-left-4 duration-200">
      {/* Bot Avatar Icon */}
      <div className="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center shrink-0 text-emerald-400 shadow-md">
        <Terminal className="w-4 h-4" />
      </div>

      <div className="flex flex-col gap-1.5 flex-1">
        {/* Main Content Bubble */}
        <div className="bg-slate-900 border border-slate-850 p-4 rounded-2xl rounded-tl-none text-slate-100 text-sm whitespace-pre-wrap leading-relaxed shadow-lg shadow-slate-950/20">
          {content}

          {/* DataTable section */}
          {data && data.length > 0 && <DataTable data={data} />}
        </div>

        {/* Footer timing telemetry and metadata */}
        <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500 font-mono mt-0.5 ml-1">
          {intent && (intent.intent || typeof intent === 'string') && (
            <span className="px-2 py-0.5 bg-slate-900 border border-slate-850 rounded text-slate-400 font-bold uppercase tracking-wider text-[9px]">
              INTENT: {intent.intent || String(intent)}
            </span>
          )}
          
          {timing && (
            <TimingBadge
              intent_ms={timing.intent_extraction_ms}
              db_ms={timing.db_query_ms ?? timing.query_execution_ms}
              formatter_ms={timing.formatting_ms ?? timing.response_formatting_ms}
              total_ms={timing.total_ms}
              cache_hit={timing.cache_hit ?? false}
            />
          )}
        </div>
      </div>
    </div>
  );
};
