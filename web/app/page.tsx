"use client";

import { useState, useRef, useEffect } from "react";
import { Send, GraduationCap, ChevronRight, Sparkles } from "lucide-react";

const EXAMPLE_PROMPTS = [
  "Who's the best professor for ECS 36C?",
  "I want an easy A for my GE requirement",
  "Compare Johnson and Martinez for ECS 50",
  "Who teaches MAT 21A and how are they rated?",
  "Best lecturers in the psychology department?",
  "Which math professor has the lightest workload?",
];

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: Message = { id: Date.now().toString(), role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    // TODO: replace with real API call to /api/chat
    setTimeout(() => {
      const reply: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "I'm pulling professor data from Rate My Professor for UC Davis... This is a placeholder response. Connect `/api/chat` to your backend to get real recommendations.",
      };
      setMessages((prev) => [...prev, reply]);
      setLoading(false);
    }, 1200);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="root">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <GraduationCap size={22} strokeWidth={1.5} />
          <span>Compass AI</span>
        </div>
        <p className="sidebar-subtitle">UC Davis Professor Guide</p>

        <div className="sidebar-section">
          <p className="sidebar-label">Try asking</p>
          <ul className="prompt-list">
            {EXAMPLE_PROMPTS.map((p) => (
              <li key={p}>
                <button className="prompt-btn" onClick={() => sendMessage(p)}>
                  <ChevronRight size={12} className="prompt-icon" />
                  {p}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="sidebar-footer">
          <span>Powered by Rate My Professor</span>
        </div>
      </aside>

      {/* Main chat */}
      <main className="main">
        <div className="chat-area">
          {isEmpty ? (
            <div className="hero">
              <div className="hero-icon">
                <Sparkles size={28} strokeWidth={1.5} />
              </div>
              <h1 className="hero-title">Find your perfect professor</h1>
              <p className="hero-sub">
                Ask anything about UC Davis professors — ratings, workload,
                teaching style, course comparisons, and more.
              </p>
            </div>
          ) : (
            <div className="messages">
              {messages.map((m) => (
                <div key={m.id} className={`message message-${m.role}`}>
                  {m.role === "assistant" && (
                    <div className="avatar">
                      <GraduationCap size={14} strokeWidth={1.5} />
                    </div>
                  )}
                  <div className="bubble">{m.content}</div>
                </div>
              ))}
              {loading && (
                <div className="message message-assistant">
                  <div className="avatar">
                    <GraduationCap size={14} strokeWidth={1.5} />
                  </div>
                  <div className="bubble typing">
                    <span /><span /><span />
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Input bar */}
        <div className="input-wrap">
          <div className="input-box">
            <textarea
              ref={inputRef}
              className="input-field"
              placeholder="Ask about a professor, course, or department…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <button
              className={`send-btn ${input.trim() ? "active" : ""}`}
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
              aria-label="Send"
            >
              <Send size={16} strokeWidth={2} />
            </button>
          </div>
          <p className="input-hint">Press Enter to send · Shift+Enter for new line</p>
        </div>
      </main>

      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=DM+Sans:wght@300;400;500&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
          --bg:        #0e0f13;
          --surface:   #15161c;
          --border:    #252630;
          --gold:      #c9a84c;
          --gold-dim:  #9e7e35;
          --text:      #e8e6e0;
          --muted:     #6b6a72;
          --user-bg:   #1e1f2a;
          --ai-bg:     #191a22;
          --radius:    12px;
          --sidebar-w: 260px;
          --font-display: 'Playfair Display', Georgia, serif;
          --font-body:    'DM Sans', sans-serif;
        }

        html, body { height: 100%; background: var(--bg); color: var(--text); font-family: var(--font-body); }

        .root {
          display: flex;
          height: 100vh;
          overflow: hidden;
        }

        /* ── Sidebar ── */
        .sidebar {
          width: var(--sidebar-w);
          min-width: var(--sidebar-w);
          background: var(--surface);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          padding: 24px 16px;
          gap: 0;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 10px;
          color: var(--gold);
          font-family: var(--font-display);
          font-size: 1.15rem;
          font-weight: 600;
          letter-spacing: 0.01em;
          margin-bottom: 4px;
        }

        .sidebar-subtitle {
          font-size: 0.7rem;
          color: var(--muted);
          letter-spacing: 0.08em;
          text-transform: uppercase;
          padding-left: 32px;
          margin-bottom: 32px;
        }

        .sidebar-section { flex: 1; }

        .sidebar-label {
          font-size: 0.65rem;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: var(--muted);
          margin-bottom: 10px;
          padding-left: 4px;
        }

        .prompt-list { list-style: none; display: flex; flex-direction: column; gap: 2px; }

        .prompt-btn {
          width: 100%;
          text-align: left;
          background: none;
          border: none;
          color: #a09fa8;
          font-family: var(--font-body);
          font-size: 0.78rem;
          font-weight: 400;
          padding: 7px 8px;
          border-radius: 8px;
          cursor: pointer;
          display: flex;
          align-items: flex-start;
          gap: 6px;
          line-height: 1.4;
          transition: background 0.15s, color 0.15s;
        }
        .prompt-btn:hover { background: var(--border); color: var(--text); }
        .prompt-icon { margin-top: 3px; flex-shrink: 0; color: var(--gold-dim); }

        .sidebar-footer {
          font-size: 0.65rem;
          color: var(--muted);
          text-align: center;
          padding-top: 16px;
          border-top: 1px solid var(--border);
        }

        /* ── Main ── */
        .main {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          position: relative;
        }

        .chat-area {
          flex: 1;
          overflow-y: auto;
          padding: 40px 24px 16px;
          scrollbar-width: thin;
          scrollbar-color: var(--border) transparent;
        }

        /* ── Hero ── */
        .hero {
          max-width: 520px;
          margin: 80px auto 0;
          text-align: center;
        }

        .hero-icon {
          width: 56px;
          height: 56px;
          border-radius: 16px;
          background: linear-gradient(135deg, #1e1a10, #2a2210);
          border: 1px solid #3a3010;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--gold);
          margin: 0 auto 24px;
        }

        .hero-title {
          font-family: var(--font-display);
          font-size: 2rem;
          font-weight: 500;
          color: var(--text);
          margin-bottom: 12px;
          line-height: 1.2;
        }

        .hero-sub {
          font-size: 0.9rem;
          color: var(--muted);
          line-height: 1.7;
          font-weight: 300;
        }

        /* ── Messages ── */
        .messages {
          max-width: 680px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 16px;
          padding-bottom: 16px;
        }

        .message { display: flex; gap: 12px; align-items: flex-start; }

        .message-user { flex-direction: row-reverse; }

        .avatar {
          width: 28px;
          height: 28px;
          border-radius: 8px;
          background: linear-gradient(135deg, #1e1a10, #2a2210);
          border: 1px solid #3a3010;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--gold);
          flex-shrink: 0;
          margin-top: 2px;
        }

        .bubble {
          max-width: 80%;
          padding: 12px 16px;
          border-radius: var(--radius);
          font-size: 0.88rem;
          line-height: 1.65;
          font-weight: 400;
        }

        .message-user .bubble {
          background: var(--user-bg);
          border: 1px solid var(--border);
          color: var(--text);
          border-top-right-radius: 4px;
        }

        .message-assistant .bubble {
          background: var(--ai-bg);
          border: 1px solid var(--border);
          color: #ccc9c0;
          border-top-left-radius: 4px;
        }

        /* Typing dots */
        .typing {
          display: flex;
          gap: 5px;
          align-items: center;
          padding: 14px 16px;
        }
        .typing span {
          width: 6px; height: 6px;
          border-radius: 50%;
          background: var(--gold-dim);
          animation: pulse 1.2s ease-in-out infinite;
        }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse {
          0%, 80%, 100% { opacity: 0.2; transform: scale(0.85); }
          40% { opacity: 1; transform: scale(1); }
        }

        /* ── Input ── */
        .input-wrap {
          padding: 12px 24px 20px;
          background: linear-gradient(to top, var(--bg) 70%, transparent);
        }

        .input-box {
          max-width: 680px;
          margin: 0 auto;
          display: flex;
          align-items: flex-end;
          gap: 10px;
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 10px 10px 10px 16px;
          transition: border-color 0.2s;
        }
        .input-box:focus-within { border-color: var(--gold-dim); }

        .input-field {
          flex: 1;
          background: none;
          border: none;
          outline: none;
          color: var(--text);
          font-family: var(--font-body);
          font-size: 0.9rem;
          font-weight: 400;
          resize: none;
          line-height: 1.5;
          max-height: 120px;
          overflow-y: auto;
        }
        .input-field::placeholder { color: var(--muted); }

        .send-btn {
          width: 34px;
          height: 34px;
          border-radius: 9px;
          border: none;
          background: var(--border);
          color: var(--muted);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          flex-shrink: 0;
          transition: background 0.15s, color 0.15s, transform 0.1s;
        }
        .send-btn.active { background: var(--gold); color: #0e0f13; }
        .send-btn.active:hover { background: #e0bc5a; transform: scale(1.05); }
        .send-btn:disabled { cursor: not-allowed; }

        .input-hint {
          text-align: center;
          font-size: 0.65rem;
          color: #3e3d46;
          margin-top: 8px;
          max-width: 680px;
          margin-left: auto;
          margin-right: auto;
        }

        /* Scrollbar */
        .chat-area::-webkit-scrollbar { width: 4px; }
        .chat-area::-webkit-scrollbar-track { background: transparent; }
        .chat-area::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
      `}</style>
    </div>
  );
}