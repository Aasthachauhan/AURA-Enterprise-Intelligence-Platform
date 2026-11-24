/**
 * Page 2: Advanced AI Conversational Workspace with multi-agent traces, citations, and streaming.
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Plus,
  Trash2,
  Bookmark,
  Bot,
  Sparkles,
  Paperclip,
  CheckCircle2,
  Clock,
  ExternalLink,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check
} from 'lucide-react';
import { api, Conversation, Message, DocumentItem } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

export const ChatWorkspacePage: React.FC = () => {
  const { activeWorkspace } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputPrompt, setInputPrompt] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [useAgents, setUseAgents] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadConversations = async () => {
    try {
      const list = await api.listConversations();
      setConversations(list);
      if (list.length > 0) {
        if (!activeConvId) {
          setActiveConvId(list[0].id);
        }
      } else {
        const initial = await api.createConversation('Intelligence Analysis');
        setConversations([initial]);
        setActiveConvId(initial.id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadDocuments = async () => {
    try {
      const res = await api.listDocuments({ limit: 50 });
      setDocuments(res.items);
    } catch (err) {
      console.error(err);
    }
  };

  const loadMessages = async (convId: string) => {
    try {
      const data = await api.getConversation(convId);
      setMessages(data.messages);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadConversations();
    loadDocuments();
  }, [activeWorkspace?.id]);

  useEffect(() => {
    if (activeConvId) {
      loadMessages(activeConvId);
    }
  }, [activeConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleCreateNewConversation = async () => {
    try {
      const conv = await api.createConversation('New Intelligence Analysis');
      setConversations([conv, ...conversations]);
      setActiveConvId(conv.id);
      setMessages([]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      const remaining = conversations.filter((c) => c.id !== id);
      setConversations(remaining);
      if (activeConvId === id) {
        setActiveConvId(remaining[0]?.id || null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim() || isSending) return;

    const userText = inputPrompt;
    setInputPrompt('');
    setIsSending(true);

    let currentConvId = activeConvId;
    if (!currentConvId) {
      try {
        const newConv = await api.createConversation('Intelligence Analysis');
        setConversations((prev) => [newConv, ...prev]);
        setActiveConvId(newConv.id);
        currentConvId = newConv.id;
      } catch (err) {
        console.error('Failed to create conversation', err);
        setIsSending(false);
        return;
      }
    }

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: currentConvId,
      role: 'user',
      content: userText,
      citations_json: [],
      agent_steps_json: [],
      tool_calls_json: [],
      tokens_prompt: 0,
      tokens_completion: 0,
      total_tokens: 0,
      latency_ms: 0,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const assistantMsg = await api.sendMessage(currentConvId, {
        content: userText,
        selected_document_ids: selectedDocIds.length > 0 ? selectedDocIds : undefined,
        use_agents: useAgents,
      });
      setMessages((prev) => [...prev.filter((m) => m.id !== tempUserMsg.id), tempUserMsg, assistantMsg]);
      loadConversations(); // refresh title if updated
    } catch (err: any) {
      console.error(err);
      alert(`Chat error: ${err.message || 'Failed to generate response'}`);
    } finally {
      setIsSending(false);
    }
  };

  const handleFeedback = async (messageId: string, rating: number) => {
    try {
      const updated = await api.submitFeedback(messageId, rating);
      setMessages((prev) => prev.map((m) => (m.id === messageId ? updated : m)));
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="h-[calc(100vh-7rem)] flex rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
      {/* Conversation History Sidebar */}
      <div className="w-72 border-r border-slate-800 flex flex-col bg-slate-950/60">
        <div className="p-3 border-b border-slate-800">
          <button
            onClick={handleCreateNewConversation}
            className="w-full py-2 px-3 rounded-lg bg-blue-600 hover:bg-blue-500 font-medium text-white text-xs flex items-center justify-center gap-2 shadow-md transition-all"
          >
            <Plus className="w-3.5 h-3.5" /> New Analysis
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.map((c) => (
            <div
              key={c.id}
              onClick={() => setActiveConvId(c.id)}
              className={`p-2.5 rounded-lg text-xs cursor-pointer flex items-center justify-between group transition-colors ${
                activeConvId === c.id ? 'bg-blue-600/20 text-blue-400 font-semibold' : 'text-slate-400 hover:bg-slate-800/60'
              }`}
            >
              <span className="truncate pr-2">{c.title}</span>
              <button
                onClick={(e) => handleDeleteConversation(e, c.id)}
                className="opacity-0 group-hover:opacity-100 hover:text-rose-400 p-1 transition-opacity"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Pane */}
      <div className="flex-1 flex flex-col bg-slate-900/30">
        {/* Chat Control Toolbar */}
        <div className="h-12 border-b border-slate-800 px-4 flex items-center justify-between text-xs bg-slate-950/40">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={useAgents}
                onChange={(e) => setUseAgents(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-0"
              />
              <span className="flex items-center gap-1 font-medium">
                <Bot className="w-3.5 h-3.5 text-blue-400" /> Multi-Agent Mode (Supervisor, Research, Verification)
              </span>
            </label>
          </div>

          {/* Document filter picker */}
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Context Scope:</span>
            <select
              value={selectedDocIds[0] || 'all'}
              onChange={(e) => setSelectedDocIds(e.target.value === 'all' ? [] : [e.target.value])}
              className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-xs text-slate-300"
            >
              <option value="all">All Documents ({documents.length})</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title} ({d.file_type.toUpperCase()})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500">
              <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-400 mb-3">
                <Sparkles className="w-6 h-6 animate-pulse" />
              </div>
              <p className="text-sm font-semibold text-slate-300">AURA Enterprise Intelligence Workspace</p>
              <p className="text-xs max-w-md mt-1">
                Ask complex questions, compare requirements across PRDs, conduct gap analysis, or generate evidence-backed reports.
              </p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-3xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
              >
                <div
                  className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-xs font-bold ${
                    msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-blue-400 border border-slate-700'
                  }`}
                >
                  {msg.role === 'user' ? 'U' : <Bot className="w-4 h-4" />}
                </div>

                <div className="space-y-2 max-w-2xl">
                  {/* Agent Execution Steps Trace */}
                  {msg.agent_steps_json && msg.agent_steps_json.length > 0 && (
                    <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                      <p className="font-semibold text-slate-400 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                        <CheckCircle2 className="w-3 h-3 text-blue-400" /> Multi-Agent Execution Plan
                      </p>
                      {msg.agent_steps_json.map((step: any, idx: number) => (
                        <div key={idx} className="flex items-center gap-2 text-slate-300">
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                          <span className="font-medium capitalize">{step.agent || step.name}:</span>
                          <span className="text-slate-400">{step.name || step.status}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Message Bubble */}
                  <div
                    className={`p-4 rounded-xl text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'bg-slate-800/90 border border-slate-700/80 text-slate-200'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>

                  {/* Citations Panel */}
                  {msg.citations_json && msg.citations_json.length > 0 && (
                    <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 space-y-1.5">
                      <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                        <Bookmark className="w-3 h-3 text-blue-400" /> Verifiable Citations
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {msg.citations_json.map((c, i) => (
                          <div
                            key={i}
                            className="px-2 py-1 rounded bg-slate-800/80 border border-slate-700 text-xs text-blue-300 flex items-center gap-1.5"
                            title={c.excerpt}
                          >
                            <ExternalLink className="w-3 h-3 text-slate-400" />
                            <span className="font-semibold">{c.document_title}</span>
                            {c.page_number && <span className="opacity-70">: Page {c.page_number}</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Message Action Footer */}
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-3 text-xs text-slate-500 pt-1">
                      <span>{msg.latency_ms} ms</span>
                      <span>•</span>
                      <span>{msg.total_tokens} tokens</span>
                      <div className="flex items-center gap-1 ml-auto">
                        <button
                          onClick={() => handleCopy(msg.id, msg.content)}
                          className="p-1 hover:text-slate-300 transition-colors"
                          title="Copy response"
                        >
                          {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.id, 1)}
                          className={`p-1 transition-colors ${msg.feedback_rating === 1 ? 'text-emerald-400' : 'hover:text-slate-300'}`}
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.id, -1)}
                          className={`p-1 transition-colors ${msg.feedback_rating === -1 ? 'text-rose-400' : 'hover:text-slate-300'}`}
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {isSending && (
            <div className="flex items-center gap-3 text-xs text-slate-400 animate-pulse">
              <Bot className="w-4 h-4 text-blue-400 animate-spin" />
              <span>Agents reasoning and retrieving evidence...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Prompt Input Form */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-800 bg-slate-950/60">
          <div className="relative flex items-center">
            <input
              type="text"
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              placeholder="Ask questions about uploaded PRDs, compare documents, or request gap analysis..."
              className="w-full pl-4 pr-12 py-3 rounded-xl bg-slate-800/90 border border-slate-700/80 text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={isSending || !inputPrompt.trim()}
              className="absolute right-2 p-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 transition-all shadow-md"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
