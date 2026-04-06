import { useState, useEffect, useRef, useCallback } from 'react';

const API = 'http://localhost:15001';

// ── Types ──────────────────────────────────────────────────────────────────────

interface ResearchSession {
  id: string;
  topic: string;
  created_at: string;
  updated_at: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface VideoIdea {
  id: string;
  title: string;
  hook: string;
  format: string;
  main_points: string[];
  script_outline: string;
  cta: string;
  target_audience: string;
}

type ChatMode = 'chat' | 'research' | 'ideas';

interface ResearchWorkspaceProps {
  onMakeVideo?: (idea: VideoIdea) => void;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

const formatTime = (iso?: string) => {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
};

const formatLabel = (iso?: string) => {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
  } catch {
    return '';
  }
};

const FORMAT_BADGES: Record<string, string> = {
  tips: 'bg-blue-500/20 text-blue-300',
  story: 'bg-purple-500/20 text-purple-300',
  facts: 'bg-green-500/20 text-green-300',
  tutorial: 'bg-orange-500/20 text-orange-300',
  trend: 'bg-pink-500/20 text-pink-300',
  pov: 'bg-yellow-500/20 text-yellow-300',
  reaction: 'bg-red-500/20 text-red-300',
};

// ── Markdown-lite renderer ─────────────────────────────────────────────────────

function renderMarkdown(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<h3 class="text-sm font-semibold text-amber-400 mt-3 mb-1">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-sm font-bold text-amber-300 mt-4 mb-1">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-base font-bold text-amber-200 mt-4 mb-2">$1</h1>')
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc text-sm">$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 list-decimal text-sm">$2</li>')
    .replace(/\n{2,}/g, '</p><p class="mb-1">')
    .replace(/\n/g, '<br/>');
}

// ── IdeaCard ───────────────────────────────────────────────────────────────────

function IdeaCard({ idea, onMakeVideo }: { idea: VideoIdea; onMakeVideo?: (idea: VideoIdea) => void }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const badgeClass = FORMAT_BADGES[idea.format] ?? 'bg-zinc-500/20 text-zinc-300';

  const handleCopy = () => {
    const text = [
      `Title: ${idea.title}`,
      `Hook: ${idea.hook}`,
      `Format: ${idea.format}`,
      `Target: ${idea.target_audience}`,
      '',
      'Main Points:',
      ...(idea.main_points || []).map((p, i) => `  ${i + 1}. ${p}`),
      '',
      'Script Outline:',
      idea.script_outline,
      '',
      `CTA: ${idea.cta}`,
    ].join('\n');
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="rounded-lg border border-zinc-700/50 bg-zinc-800/60 p-3 mb-2 hover:border-amber-500/40 transition-colors">
      {/* Header */}
      <div className="flex items-start gap-2 mb-2">
        <span className="text-amber-400 text-base mt-0.5">💡</span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white leading-tight">{idea.title}</p>
          <div className="flex items-center gap-1.5 mt-1">
            <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${badgeClass}`}>
              {idea.format}
            </span>
            {idea.target_audience && (
              <span className="text-xs text-zinc-500 truncate">{idea.target_audience}</span>
            )}
          </div>
        </div>
      </div>

      {/* Hook */}
      <div className="bg-amber-500/10 border border-amber-500/20 rounded px-2.5 py-1.5 mb-2">
        <p className="text-xs text-amber-200 font-medium leading-relaxed">
          🎣 &ldquo;{idea.hook}&rdquo;
        </p>
      </div>

      {/* Expand / Collapse */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-xs text-zinc-400 hover:text-zinc-200 mb-2 transition-colors"
      >
        {expanded ? '▲ Thu gọn' : '▼ Xem chi tiết'}
      </button>

      {expanded && (
        <div className="space-y-2 text-xs">
          {idea.main_points?.length > 0 && (
            <div>
              <p className="text-zinc-400 font-medium mb-1">Điểm chính:</p>
              <ul className="space-y-0.5">
                {idea.main_points.map((pt, i) => (
                  <li key={i} className="text-zinc-300 flex gap-1.5">
                    <span className="text-amber-400 shrink-0">{i + 1}.</span>
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {idea.script_outline && (
            <div>
              <p className="text-zinc-400 font-medium mb-1">Script outline:</p>
              <p className="text-zinc-300 leading-relaxed whitespace-pre-wrap bg-zinc-900/50 rounded p-2">
                {idea.script_outline}
              </p>
            </div>
          )}

          {idea.cta && (
            <div className="flex items-center gap-1.5">
              <span className="text-zinc-400">CTA:</span>
              <span className="text-zinc-300">{idea.cta}</span>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 mt-2.5">
        <button
          onClick={handleCopy}
          className="flex-1 text-xs bg-zinc-700/60 hover:bg-zinc-600/60 text-zinc-300 hover:text-white rounded px-2 py-1.5 transition-colors"
        >
          {copied ? '✓ Đã copy' : '📋 Copy'}
        </button>
        {onMakeVideo && (
          <button
            onClick={() => onMakeVideo(idea)}
            className="flex-1 text-xs bg-amber-500/20 hover:bg-amber-500/40 text-amber-300 hover:text-amber-100 rounded px-2 py-1.5 transition-colors font-medium border border-amber-500/30"
          >
            🎬 Tạo Video
          </button>
        )}
      </div>
    </div>
  );
}

// ── ChatBubble ─────────────────────────────────────────────────────────────────

function ChatBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div className={`max-w-[85%] ${isUser ? 'order-2' : 'order-1'}`}>
        {!isUser && (
          <div className="flex items-center gap-1.5 mb-1">
            <span className="text-xs text-amber-400 font-medium">AI Research</span>
          </div>
        )}
        <div
          className={`rounded-lg px-3 py-2 text-sm leading-relaxed ${
            isUser
              ? 'bg-amber-500/20 text-amber-100 border border-amber-500/30'
              : 'bg-zinc-800/80 text-zinc-200 border border-zinc-700/50'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{msg.content}</p>
          ) : (
            <div
              className="prose-sm"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
            />
          )}
        </div>
        {msg.timestamp && (
          <p className={`text-xs text-zinc-600 mt-0.5 ${isUser ? 'text-right' : 'text-left'}`}>
            {formatTime(msg.timestamp)}
          </p>
        )}
      </div>
    </div>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────────

export default function ResearchWorkspace({ onMakeVideo }: ResearchWorkspaceProps) {
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [activeId, setActiveId] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [ideas, setIdeas] = useState<VideoIdea[]>([]);
  const [topic, setTopic] = useState('');
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<ChatMode>('chat');
  const [streaming, setStreaming] = useState(false);
  const [streamBuffer, setStreamBuffer] = useState('');
  const [statusMsg, setStatusMsg] = useState('');
  const [error, setError] = useState('');
  const [showSessions, setShowSessions] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamBuffer]);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  // Load history when session changes
  useEffect(() => {
    if (activeId) {
      loadHistory(activeId);
      loadIdeas(activeId);
    }
  }, [activeId]);

  const loadSessions = async () => {
    try {
      const res = await fetch(`${API}/research/sessions`);
      if (res.ok) {
        const data: ResearchSession[] = await res.json();
        setSessions(data);
        // Auto-select latest session if none selected
        if (!activeId && data.length > 0) {
          setActiveId(data[0].id);
          setTopic(data[0].topic);
        }
      }
    } catch (e) {
      console.error('Failed to load sessions:', e);
    }
  };

  const loadHistory = async (sessionId: string) => {
    try {
      const res = await fetch(`${API}/research/sessions/${sessionId}/history`);
      if (res.ok) {
        const data: ChatMessage[] = await res.json();
        setMessages(data);
      }
    } catch (e) {
      console.error('Failed to load history:', e);
    }
  };

  const loadIdeas = async (sessionId: string) => {
    try {
      const res = await fetch(`${API}/research/sessions/${sessionId}/ideas`);
      if (res.ok) {
        const data: VideoIdea[] = await res.json();
        setIdeas(data);
      }
    } catch (e) {
      console.error('Failed to load ideas:', e);
    }
  };

  const createSession = async () => {
    try {
      const res = await fetch(`${API}/research/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: topic.trim() }),
      });
      if (res.ok) {
        const session: ResearchSession = await res.json();
        setSessions(prev => [session, ...prev]);
        setActiveId(session.id);
        setMessages([]);
        setIdeas([]);
        setShowSessions(false);
      }
    } catch {
      setError('Không thể tạo session mới');
    }
  };

  const deleteSession = async (sessionId: string) => {
    if (!confirm('Xóa session này?')) return;
    try {
      await fetch(`${API}/research/sessions/${sessionId}`, { method: 'DELETE' });
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (activeId === sessionId) {
        const remaining = sessions.filter(s => s.id !== sessionId);
        if (remaining.length > 0) {
          setActiveId(remaining[0].id);
        } else {
          setActiveId('');
          setMessages([]);
          setIdeas([]);
        }
      }
    } catch {
      setError('Không thể xóa session');
    }
  };

  const sendMessage = useCallback(async () => {
    const msg = input.trim();
    if (!msg || streaming) return;
    if (!activeId) {
      setError('Hãy tạo session mới trước');
      return;
    }

    setInput('');
    setError('');
    setStreaming(true);
    setStreamBuffer('');
    setStatusMsg('');

    // Optimistically add user message
    const userMsg: ChatMessage = { role: 'user', content: msg };
    setMessages(prev => [...prev, userMsg]);

    try {
      const res = await fetch(`${API}/research/sessions/${activeId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, mode }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let assistantContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const evt = JSON.parse(line.slice(6));

            if (evt.type === 'status') {
              setStatusMsg(evt.message ?? '');
            } else if (evt.type === 'chunk') {
              assistantContent += evt.content ?? '';
              setStreamBuffer(assistantContent);
            } else if (evt.type === 'done') {
              setStatusMsg('');
              if (assistantContent) {
                const assistantMsg: ChatMessage = {
                  role: 'assistant',
                  content: assistantContent,
                  timestamp: new Date().toISOString(),
                };
                setMessages(prev => [...prev, assistantMsg]);
                setStreamBuffer('');
              }
              if (evt.ideas && evt.ideas.length > 0) {
                setIdeas(evt.ideas);
              }
            } else if (evt.type === 'error') {
              setError(evt.message ?? 'Có lỗi xảy ra');
              setStreamBuffer('');
            }
          } catch {
            // Skip malformed SSE lines
          }
        }
      }
    } catch (e) {
      setError(`Lỗi kết nối: ${e}`);
      setStreamBuffer('');
    } finally {
      setStreaming(false);
      setStatusMsg('');
      // Reload sessions to update updated_at
      loadSessions();
    }
  }, [input, streaming, activeId, mode]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const activeSession = sessions.find(s => s.id === activeId);

  const MODE_OPTIONS: { value: ChatMode; label: string; desc: string; color: string }[] = [
    { value: 'chat', label: '💬 Chat', desc: 'Hỏi đáp tự do', color: 'border-zinc-600 text-zinc-300' },
    { value: 'research', label: '🔍 Research', desc: 'Tìm kiếm + phân tích', color: 'border-blue-500/50 text-blue-300' },
    { value: 'ideas', label: '💡 Ideas', desc: 'Tạo 5 ý tưởng video', color: 'border-amber-500/50 text-amber-300' },
  ];

  return (
    <div className="flex h-full gap-0 overflow-hidden">
      {/* ── Left: Chat Panel ─────────────────────────────────────────────────── */}
      <div className="flex flex-col flex-1 min-w-0 border-r border-zinc-700/50">
        {/* Header */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-zinc-700/50 bg-zinc-900/50 shrink-0">
          <span className="text-amber-400 text-lg">🔬</span>
          <div className="flex-1 min-w-0">
            <h2 className="text-sm font-semibold text-white">Research & Ideas</h2>
            {activeSession?.topic && (
              <p className="text-xs text-zinc-400 truncate">{activeSession.topic}</p>
            )}
          </div>
          <button
            onClick={() => setShowSessions(!showSessions)}
            className="text-xs text-zinc-400 hover:text-white px-2 py-1 rounded hover:bg-zinc-700/50 transition-colors"
          >
            📁 Sessions
          </button>
        </div>

        {/* Sessions Dropdown */}
        {showSessions && (
          <div className="border-b border-zinc-700/50 bg-zinc-900/80 max-h-48 overflow-y-auto shrink-0">
            <div className="p-2">
              {/* New session */}
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={topic}
                  onChange={e => setTopic(e.target.value)}
                  placeholder="Topic mới (vd: cooking tips, crypto 2025...)"
                  className="flex-1 text-xs bg-zinc-800 border border-zinc-600 rounded px-2 py-1.5 text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500/50"
                  onKeyDown={e => e.key === 'Enter' && createSession()}
                />
                <button
                  onClick={createSession}
                  className="text-xs bg-amber-500/20 hover:bg-amber-500/40 text-amber-300 border border-amber-500/30 rounded px-3 py-1.5 transition-colors"
                >
                  + Mới
                </button>
              </div>

              {/* Session list */}
              {sessions.length === 0 ? (
                <p className="text-xs text-zinc-500 text-center py-2">Chưa có session nào</p>
              ) : (
                <div className="space-y-1">
                  {sessions.map(s => (
                    <div
                      key={s.id}
                      className={`flex items-center gap-2 rounded px-2 py-1.5 cursor-pointer transition-colors ${
                        s.id === activeId
                          ? 'bg-amber-500/20 border border-amber-500/30'
                          : 'hover:bg-zinc-700/50'
                      }`}
                      onClick={() => {
                        setActiveId(s.id);
                        setTopic(s.topic);
                        setShowSessions(false);
                      }}
                    >
                      <span className="text-xs text-zinc-400 shrink-0">{formatLabel(s.updated_at)}</span>
                      <span className="flex-1 text-xs text-white truncate">
                        {s.topic || 'Untitled session'}
                      </span>
                      <button
                        onClick={e => { e.stopPropagation(); deleteSession(s.id); }}
                        className="text-xs text-zinc-600 hover:text-red-400 transition-colors px-1"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 py-3">
          {messages.length === 0 && !streaming && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <span className="text-4xl mb-3">🔬</span>
              <p className="text-sm text-zinc-400 mb-1">Research & Idea Chat</p>
              <p className="text-xs text-zinc-600 max-w-xs">
                Chọn mode phù hợp và bắt đầu chat. Mode <strong className="text-blue-400">Research</strong> sẽ
                tự động tìm kiếm web, mode <strong className="text-amber-400">Ideas</strong> tạo 5 ý tưởng video.
              </p>
              {!activeId && (
                <button
                  onClick={() => setShowSessions(true)}
                  className="mt-4 text-xs bg-amber-500/20 hover:bg-amber-500/40 text-amber-300 border border-amber-500/30 rounded px-3 py-2 transition-colors"
                >
                  + Tạo session mới để bắt đầu
                </button>
              )}
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatBubble key={i} msg={msg} />
          ))}

          {/* Streaming buffer */}
          {streamBuffer && (
            <ChatBubble
              msg={{ role: 'assistant', content: streamBuffer }}
            />
          )}

          {/* Status indicator */}
          {statusMsg && !streamBuffer && (
            <div className="flex items-center gap-2 mb-3">
              <div className="flex gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <p className="text-xs text-zinc-400">{statusMsg}</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error */}
        {error && (
          <div className="mx-4 mb-2 px-3 py-2 rounded bg-red-500/10 border border-red-500/30 text-xs text-red-400">
            {error}
            <button onClick={() => setError('')} className="ml-2 hover:text-red-300">✕</button>
          </div>
        )}

        {/* Mode selector */}
        <div className="px-4 pb-2 shrink-0">
          <div className="flex gap-1.5">
            {MODE_OPTIONS.map(opt => (
              <button
                key={opt.value}
                onClick={() => setMode(opt.value)}
                title={opt.desc}
                className={`flex-1 text-xs rounded px-2 py-1.5 border transition-colors ${
                  mode === opt.value
                    ? `${opt.color} bg-zinc-800`
                    : 'border-zinc-700 text-zinc-500 hover:text-zinc-300 hover:border-zinc-600'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="px-4 pb-4 shrink-0">
          <div className="flex gap-2 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                mode === 'research'
                  ? 'Nhập topic để tìm kiếm xu hướng (Enter để gửi)...'
                  : mode === 'ideas'
                  ? 'Mô tả yêu cầu video, tôi sẽ tạo 5 ý tưởng (Enter để gửi)...'
                  : 'Hỏi bất cứ điều gì về content strategy (Enter để gửi)...'
              }
              rows={2}
              disabled={streaming || !activeId}
              className="flex-1 text-sm bg-zinc-800/80 border border-zinc-600 rounded-lg px-3 py-2 text-white placeholder-zinc-500 resize-none focus:outline-none focus:border-amber-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              onClick={sendMessage}
              disabled={streaming || !input.trim() || !activeId}
              className="shrink-0 bg-amber-500 hover:bg-amber-400 disabled:bg-zinc-700 disabled:text-zinc-500 text-black font-semibold rounded-lg px-3 py-2 text-sm transition-colors h-[52px] w-12 flex items-center justify-center"
            >
              {streaming ? (
                <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
              ) : (
                '▶'
              )}
            </button>
          </div>
          <p className="text-xs text-zinc-600 mt-1">
            {mode === 'research' && '🔍 Sẽ tìm kiếm web rồi phân tích bằng AI'}
            {mode === 'ideas' && '💡 Sẽ tạo 5 ý tưởng video với script outline đầy đủ'}
            {mode === 'chat' && '💬 Chat tự do với AI về content strategy'}
          </p>
        </div>
      </div>

      {/* ── Right: Ideas Panel ────────────────────────────────────────────────── */}
      <div className="w-80 shrink-0 flex flex-col overflow-hidden">
        {/* Ideas Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-700/50 bg-zinc-900/50 shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-amber-400">💡</span>
            <h3 className="text-sm font-semibold text-white">Video Ideas</h3>
            {ideas.length > 0 && (
              <span className="text-xs bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded-full">
                {ideas.length}
              </span>
            )}
          </div>
          {activeId && (
            <button
              onClick={() => {
                setMode('ideas');
                setInput('Tạo 5 ý tưởng video ngắn về topic này');
                setTimeout(() => inputRef.current?.focus(), 100);
              }}
              className="text-xs text-zinc-400 hover:text-amber-400 transition-colors"
              title="Tạo ý tưởng mới"
            >
              🔄 Tạo lại
            </button>
          )}
        </div>

        {/* Ideas List */}
        <div className="flex-1 overflow-y-auto px-3 py-3">
          {ideas.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <span className="text-3xl mb-3 opacity-50">🎬</span>
              <p className="text-xs text-zinc-500 mb-2">Chưa có ý tưởng nào</p>
              <p className="text-xs text-zinc-600 max-w-52">
                Chọn mode <strong className="text-amber-400">💡 Ideas</strong> rồi gửi yêu cầu để tạo 5 ý tưởng video
              </p>
              {activeId && (
                <button
                  onClick={() => {
                    setMode('ideas');
                    setInput('Tạo 5 ý tưởng video ngắn về topic này');
                    setTimeout(() => sendMessage(), 100);
                  }}
                  className="mt-3 text-xs bg-amber-500/20 hover:bg-amber-500/40 text-amber-300 border border-amber-500/30 rounded px-3 py-1.5 transition-colors"
                >
                  💡 Tạo ngay
                </button>
              )}
            </div>
          ) : (
            <div>
              {ideas.map(idea => (
                <IdeaCard
                  key={idea.id}
                  idea={idea}
                  onMakeVideo={onMakeVideo}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
