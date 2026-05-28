import React, { useState } from 'react';
import { Timer, Zap, Cpu, Database, Eye, ChevronDown, ChevronUp, Layers } from 'lucide-react';

export const TimingBadge = (props) => {
  // Build a consistent timing map from direct props if timing object is absent
  const actualTiming = props.timing || {
    intent_extraction_ms: props.intent_ms,
    validation_ms: 0,
    db_query_ms: props.db_ms,
    formatting_ms: props.formatter_ms,
    total_ms: props.total_ms,
    cache_hit: props.cache_hit
  };

  if (!actualTiming || !actualTiming.total_ms) return null;

  const [isExpanded, setIsExpanded] = useState(false);

  const {
    intent_extraction_ms = 0,
    validation_ms = 0,
    db_query_ms = 0,
    formatting_ms = 0,
    total_ms = 0,
    cache_hit = false
  } = actualTiming;

  // SLAs
  const SLA_TARGET = 3000;
  const isSlaExceeded = total_ms > SLA_TARGET;

  // Color mapping
  let badgeColor = 'border-emerald-500/20 text-emerald-400 bg-emerald-500/5';
  let badgeText = 'PASS';
  if (total_ms >= 1000 && total_ms <= 3000) {
    badgeColor = 'border-amber-500/20 text-amber-400 bg-amber-500/5';
    badgeText = 'PASS';
  } else if (total_ms > 3000) {
    badgeColor = 'border-rose-500/20 text-rose-400 bg-rose-500/5';
    badgeText = 'SLA EXCEEDED';
  }

  // Override if cache hit
  if (cache_hit) {
    badgeColor = 'border-cyan-500/25 text-cyan-400 bg-cyan-500/5';
    badgeText = 'CACHE PASS';
  }

  return (
    <div className="flex flex-col self-start max-w-sm mt-2">
      {/* SLA Trigger Bar */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className={`flex items-center gap-1.5 px-3 py-1.5 border rounded-xl font-mono text-[10px] tracking-wider font-bold transition-all shadow-md focus:outline-none focus:ring-1 cursor-pointer select-none ${badgeColor}`}
      >
        <Timer className="w-3.5 h-3.5" />
        <span>{total_ms}ms total</span>
        {cache_hit && (
          <>
            <span className="opacity-45">|</span>
            <span className="flex items-center gap-0.5 text-cyan-400">
              <Layers className="w-3 h-3 animate-pulse" /> CACHE HIT
            </span>
          </>
        )}
        <span className="opacity-45">|</span>
        <span>Target: &lt;3s</span>
        <span className="opacity-45">|</span>
        <span className="underline font-sans font-semibold tracking-normal flex items-center gap-0.5">
          {badgeText} {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </span>
      </button>

      {/* Expanded Timing Details Panel */}
      {isExpanded && (
        <div className="mt-1.5 p-3 bg-slate-950 border border-slate-850 rounded-xl space-y-2 text-[10px] font-mono text-slate-400 shadow-xl animate-in fade-in slide-in-from-top-1 duration-200">
          <div className="text-[9px] uppercase tracking-wider text-slate-500 font-bold font-sans border-b border-slate-900 pb-1.5 mb-1.5 flex items-center justify-between">
            <span>Query Telemetry</span>
            {cache_hit ? (
              <span className="text-cyan-400">Cache Active</span>
            ) : (
              <span className={isSlaExceeded ? 'text-rose-400' : 'text-emerald-400'}>
                {isSlaExceeded ? 'SLA Alert' : 'SLA Compliant'}
              </span>
            )}
          </div>

          <div className="flex items-center justify-between gap-8">
            <span className="flex items-center gap-1 text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span>Intent Extraction</span>
            </span>
            <span className="font-bold text-slate-200">{intent_extraction_ms}ms</span>
          </div>

          <div className="flex items-center justify-between gap-8">
            <span className="flex items-center gap-1 text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-purple-400 shrink-0" />
              <span>Security Validation</span>
            </span>
            <span className="font-bold text-slate-200">{validation_ms}ms</span>
          </div>

          <div className="flex items-center justify-between gap-8">
            <span className="flex items-center gap-1 text-slate-300">
              <Database className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span>Database Query</span>
            </span>
            <span className="font-bold text-slate-200">{db_query_ms}ms</span>
          </div>

          <div className="flex items-center justify-between gap-8">
            <span className="flex items-center gap-1 text-slate-300">
              <Eye className="w-3.5 h-3.5 text-pink-400 shrink-0" />
              <span>Deterministic Format</span>
            </span>
            <span className="font-bold text-slate-200">{formatting_ms}ms</span>
          </div>

          <div className="pt-1.5 border-t border-slate-900 flex items-center justify-between font-bold text-slate-200">
            <span className="flex items-center gap-1 text-slate-300">
              <Zap className="w-3.5 h-3.5 text-amber-400 shrink-0 animate-pulse" style={{ animationDuration: '2s' }} />
              <span>Total Delay</span>
            </span>
            <span className={cache_hit ? 'text-cyan-400' : isSlaExceeded ? 'text-rose-400' : 'text-emerald-400'}>
              {total_ms}ms
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
