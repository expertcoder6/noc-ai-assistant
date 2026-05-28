import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal } from 'lucide-react';

export const ChatInput = ({ sendMessage, isLoading }) => {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea to fit content height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (text.trim() && !isLoading) {
        sendMessage(text.trim());
        setText('');
      }
    }
  };

  const handleSend = () => {
    if (text.trim() && !isLoading) {
      sendMessage(text.trim());
      setText('');
    }
  };

  return (
    <div className="bg-gradient-to-t from-slate-950 via-slate-950/95 to-transparent border-t border-slate-900/60 p-4 pb-6 sticky bottom-0 z-30">
      <div className="max-w-4xl mx-auto flex flex-col gap-2">
        <div className="relative flex items-center bg-slate-900/90 border border-slate-800 focus-within:border-emerald-500/50 rounded-2xl p-2 transition-all shadow-xl backdrop-blur-md">
          {/* Prefix Console Icon */}
          <div className="pl-3 pr-2 text-slate-500 shrink-0 self-center">
            <Terminal className="w-4 h-4" />
          </div>

          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-0 resize-none py-2 pr-12 min-h-[38px] max-h-[120px] font-mono leading-relaxed"
            placeholder="Query device status, interfaces, metric thresholds, alerts..."
          />

          {/* Send Button */}
          <button
            type="button"
            onClick={handleSend}
            disabled={isLoading || !text.trim()}
            className="absolute right-3.5 bottom-3 p-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer shadow-md active:scale-95"
            title="Execute Command"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        {/* Shortcut Legend */}
        <div className="flex items-center justify-between text-[9px] font-mono text-slate-500 px-3 uppercase tracking-wider font-bold">
          <span>Target Response SLA: &lt;3000ms</span>
          <span>Press Enter to send · Shift+Enter for newline</span>
        </div>
      </div>
    </div>
  );
};
