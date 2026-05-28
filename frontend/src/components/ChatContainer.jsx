import React from 'react';
import { Header } from './Header';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { EmptyState } from './EmptyState';
import { SuggestedQueries } from './SuggestedQueries';
import { useChat } from '../hooks/useChat';
import { Trash2 } from 'lucide-react';

export const ChatContainer = () => {
  const { messages, isLoading, sendMessage, clearMessages, lastQueryMs } = useChat();

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 relative overflow-hidden select-none">
      {/* Background Matrix Grid Effect */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#022c22_1px,transparent_1px),linear-gradient(to_bottom,#022c22_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-[0.07] pointer-events-none" />

      {/* Main Header — full width */}
      <Header lastQueryMs={lastQueryMs} />

      {/* Body — sidebar + chat column */}
      <div className="flex flex-1 overflow-hidden relative">

        {/* ── Left Sidebar: always-visible query suggestions ── */}
        <SuggestedQueries onSelect={sendMessage} />

        {/* ── Main Chat Column ── */}
        <div className="flex flex-col flex-1 overflow-hidden relative">

          {/* Clear Terminal button — only when there are messages */}
          {messages.length > 0 && (
            <button
              type="button"
              onClick={clearMessages}
              title="Clear Console Screen"
              className="absolute top-4 right-6 p-2 bg-slate-900/90 border border-slate-800 text-slate-500 hover:text-red-400 hover:border-slate-700 rounded-xl transition-all cursor-pointer shadow-lg z-20 hover:scale-105 active:scale-95"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}

          {/* Empty welcome state OR message list */}
          {messages.length === 0 && !isLoading ? (
            <div className="flex-1 overflow-y-auto flex items-center justify-center">
              <EmptyState onSelectQuery={sendMessage} />
            </div>
          ) : (
            <MessageList messages={messages} isLoading={isLoading} />
          )}

          {/* Input bar — sticky to bottom of chat column */}
          <ChatInput sendMessage={sendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
};
