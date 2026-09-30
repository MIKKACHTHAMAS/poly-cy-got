import { useState, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function App() {
  const [message, setMessage] = useState("");
  const [language, setLanguage] = useState("auto");
  const [level, setLevel] = useState("simple");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => "user_" + Math.random().toString(36).slice(2, 10));
  const [memoryConsent, setMemoryConsent] = useState(false);
  const [memoryStatus, setMemoryStatus] = useState(null);

  // Load memory on mount
  useEffect(() => {
    fetch(`${API_URL}/memory/${sessionId}`)
      .then(r => r.json())
      .then(data => {
        if (data.preferences) {
          setMemoryStatus(data.preferences);
          setLanguage(data.preferences.preferred_language || "auto");
          setLevel(data.preferences.explanation_level || "simple");
          setMemoryConsent(true);
        }
      })
      .catch(() => {});
  }, [sessionId]);

  async function sendMessage() {
    if (!message.trim() || loading) return;

    const userMessage = message;
    setMessages(prev => [...prev, { role: "user", text: userMessage }]);
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          language,
          explanation_level: level,
          session_id: sessionId,
          memory_consent: memoryConsent
        })
      });

      if (!response.ok) throw new Error("Request failed");
      const data = await response.json();

      setMessages(prev => [...prev, {
        role: "assistant",
        text: data.reply,
        indicators: data.risk_indicators,
        detectedLang: data.detected_language
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: "assistant",
        text: "Unable to connect. Please try again."
      }]);
    } finally {
      setLoading(false);
    }
  }

  async function clearMemory() {
    await fetch(`${API_URL}/memory/${sessionId}`, { method: "DELETE" });
    setMemoryStatus(null);
    setMemoryConsent(false);
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white p-5">
      <h1 className="text-3xl font-bold">🛡️ PolyCyGot</h1>
      <p className="text-slate-400">Adaptive multilingual cybersecurity agent</p>

      {/* Controls */}
      <div className="my-5 flex flex-wrap gap-3 items-center">
        <select
          value={language}
          onChange={e => setLanguage(e.target.value)}
          className="bg-slate-800 p-2 rounded"
        >
          <option value="auto">Auto-detect</option>
          <option value="en-IN">English</option>
          <option value="ta-IN">Tamil</option>
        </select>

        <select
          value={level}
          onChange={e => setLevel(e.target.value)}
          className="bg-slate-800 p-2 rounded"
        >
          <option value="simple">Beginner</option>
          <option value="technical">Technical</option>
        </select>

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={memoryConsent}
            onChange={e => setMemoryConsent(e.target.checked)}
          />
          Save preferences
        </label>

        {memoryStatus && (
          <button
            onClick={clearMemory}
            className="bg-red-800 px-3 py-1 rounded text-sm"
          >
            Clear memory
          </button>
        )}
      </div>

      {/* Memory indicator */}
      {memoryStatus && (
        <div className="bg-teal-900/50 p-2 rounded mb-3 text-sm">
          Memory active: {memoryStatus.preferred_language}, {memoryStatus.explanation_level}
        </div>
      )}

      {/* Messages */}
      <section className="space-y-3 mb-5">
        {messages.map((item, index) => (
          <div key={index} className="bg-slate-800 p-4 rounded-xl">
            <div className="flex justify-between">
              <b>{item.role === "user" ? "You" : "PolyCyGot"}</b>
              {item.detectedLang && (
                <span className="text-xs text-slate-500">
                  detected: {item.detectedLang}
                </span>
              )}
            </div>
            <p className="mt-2 whitespace-pre-wrap">{item.text}</p>
            {item.indicators?.length > 0 && (
              <div className="mt-2 text-xs text-amber-400">
                ⚠️ {item.indicators.map(i => i.indicator).join(" | ")}
              </div>
            )}
          </div>
        ))}
        {loading && <p className="text-slate-400">PolyCyGot is thinking...</p>}
      </section>

      {/* Input */}
      <div className="flex gap-2">
        <input
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Ask a cybersecurity question..."
          className="flex-1 bg-slate-800 p-3 rounded-xl"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-teal-600 px-5 rounded-xl disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </main>
  );
}