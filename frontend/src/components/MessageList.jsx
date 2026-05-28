import React, { useEffect, useRef } from 'react';
import { AssistantMessage } from './AssistantMessage';
import { TypingIndicator } from './TypingIndicator';
import { User, AlertOctagon } from 'lucide-react';

export const MessageList = ({ messages, isLoading }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages.length]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-800">
      <div className="max-w-4xl mx-auto space-y-6">
        {messages.map((msg) => {
          if (msg.role === 'user') {
            return (
              <div
                key={msg.id}
                className="flex gap-4 max-w-2xl ml-auto justify-end group animate-in fade-in slide-in-from-right-4 duration-200"
              >
                <div className="flex flex-col gap-1 items-end">
                  <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-4 py-3 rounded-2xl rounded-tr-none text-sm whitespace-pre-wrap leading-relaxed shadow-lg shadow-emerald-950/20 font-sans">
                    {msg.content}
                  </div>
                  <span className="text-[9px] font-mono text-slate-500 mr-1 mt-0.5 uppercase tracking-wider font-bold">
                    User Session
                  </span>
                </div>
                {/* User Avatar */}
                <div className="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center shrink-0 text-slate-400 shadow-md">
                  <User className="w-4 h-4" />
                </div>
              </div>
            );
          }
          
          if (msg.role === 'assistant') {
            return (
              <div key={msg.id} className="flex justify-start">
                <AssistantMessage message={msg} />
              </div>
            );
          }
          
          // error role
          return (
            <div
              key={msg.id}
              className="flex gap-4 max-w-xl self-start w-full group animate-in fade-in duration-200"
            >
              <div className="w-9 h-9 rounded-xl bg-red-950/30 border border-red-900/40 flex items-center justify-center shrink-0 text-red-400 shadow-md">
                <AlertOctagon className="w-4 h-4" />
              </div>
              <div className="flex flex-col gap-1">
                <div className="bg-red-950/25 border border-red-900/35 px-4 py-3 rounded-2xl rounded-tl-none text-red-300 text-xs font-mono leading-relaxed shadow-lg">
                  {msg.content}
                </div>
                <span className="text-[9px] font-mono text-red-500/80 ml-1 mt-0.5 uppercase tracking-wider font-bold">
                  Telemetry Alert // API Error
                </span>
              </div>
            </div>
          );
        })}
        
        {isLoading && (
          <div className="flex justify-start">
            <TypingIndicator />
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
