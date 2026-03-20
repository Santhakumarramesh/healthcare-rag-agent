"use client";
import { useState, useRef, useEffect } from "react";
import { aiApi } from "@/lib/api";
import toast from "react-hot-toast";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const SUGGESTIONS = [
  "What do my latest blood test results mean?",
  "Should I be worried about my cholesterol levels?",
  "What are common side effects of Metformin?",
  "How can I improve my sleep quality?",
];

export default function AIChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const content = text || input.trim();
    if (!content || loading) return;
    setInput("");

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await aiApi.chat(content, conversationId);
      const { response, conversation_id } = res.data;
      if (!conversationId) setConversationId(conversation_id);

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      toast.error("AI is temporarily unavailable. Please try again.");
      setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen lg:h-[calc(100vh-0px)] bg-surface">
      {/* Header */}
      <header className="bg-surface-container-lowest border-b border-outline-variant/20 px-6 py-4 flex items-center gap-3 sticky top-0 z-20">
        <div className="w-10 h-10 rounded-xl bg-secondary-fixed flex items-center justify-center">
          <span className="material-symbols-outlined text-on-secondary-container ms-fill">smart_toy</span>
        </div>
        <div>
          <h1 className="font-bold text-on-surface font-headline">AI Health Assistant</h1>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-on-tertiary-container" />
            <span className="text-xs text-on-surface-variant">Powered by HealthCopilot AI</span>
          </div>
        </div>
        <button
          onClick={() => { setMessages([]); setConversationId(undefined); }}
          className="ml-auto text-xs text-on-surface-variant hover:text-on-surface font-medium flex items-center gap-1"
        >
          <span className="material-symbols-outlined text-sm">refresh</span>
          New chat
        </button>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-6 max-w-2xl mx-auto w-full">
        {messages.length === 0 ? (
          <div className="space-y-6">
            {/* Welcome */}
            <div className="text-center space-y-3 pt-8">
              <div className="w-16 h-16 rounded-2xl bg-primary-container flex items-center justify-center mx-auto">
                <span className="material-symbols-outlined text-3xl text-on-primary ms-fill">health_metrics</span>
              </div>
              <h2 className="text-xl font-bold text-primary font-headline">How can I help you today?</h2>
              <p className="text-sm text-on-surface-variant max-w-xs mx-auto">
                Ask me anything about your health records, medications, symptoms, or get general health guidance.
              </p>
              <div className="flex items-center justify-center gap-2 text-xs text-on-surface-variant">
                <span className="material-symbols-outlined text-sm text-amber-500 ms-fill">info</span>
                <span>Not a substitute for professional medical advice</span>
              </div>
            </div>

            {/* Suggestions */}
            <div className="space-y-2">
              <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider px-1">Suggested questions</p>
              <div className="grid gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => sendMessage(s)}
                    className="text-left p-3 rounded-xl bg-surface-container hover:bg-surface-container-high transition-colors text-sm text-on-surface border border-outline-variant/20"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                msg.role === "user"
                  ? "bg-primary text-white"
                  : "bg-secondary-fixed"
              }`}>
                <span className="material-symbols-outlined text-sm ms-fill">
                  {msg.role === "user" ? "person" : "smart_toy"}
                </span>
              </div>
              <div className={`max-w-[80%] space-y-1 ${msg.role === "user" ? "items-end" : ""}`}>
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-primary text-white rounded-tr-md"
                    : "bg-surface-container-lowest border border-outline-variant/20 text-on-surface rounded-tl-md"
                }`}>
                  {msg.content}
                </div>
                <p className="text-[10px] text-on-surface-variant px-1">
                  {msg.timestamp.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
            </div>
          ))
        )}

        {/* Typing indicator */}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-xl bg-secondary-fixed flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-sm ms-fill text-on-secondary-container">smart_toy</span>
            </div>
            <div className="bg-surface-container-lowest border border-outline-variant/20 rounded-2xl rounded-tl-md px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="w-2 h-2 rounded-full bg-on-surface-variant animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="bg-surface-container-lowest border-t border-outline-variant/20 px-5 py-4 pb-safe">
        <div className="max-w-2xl mx-auto flex gap-3 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask about your health, reports, medications…"
            rows={1}
            className="flex-1 input-field resize-none min-h-[44px] max-h-32"
            style={{ height: "auto" }}
            onInput={(e) => {
              const el = e.currentTarget;
              el.style.height = "auto";
              el.style.height = Math.min(el.scrollHeight, 128) + "px";
            }}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            className="w-11 h-11 rounded-xl bg-primary text-white flex items-center justify-center disabled:opacity-50 transition-all active:scale-95 shrink-0"
          >
            <span className="material-symbols-outlined text-sm ms-fill">send</span>
          </button>
        </div>
        <p className="text-center text-[10px] text-on-surface-variant mt-2 max-w-2xl mx-auto">
          AI responses are for informational purposes only. Always consult a healthcare professional.
        </p>
      </div>
    </div>
  );
}
