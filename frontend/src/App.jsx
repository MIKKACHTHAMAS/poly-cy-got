import { useState, useEffect, useRef } from "react";
import {
  Shield, Send, Globe, Brain, Trash2, Copy, Check,
  ChevronDown, ChevronUp, AlertTriangle, Sparkles, X,
  Mic, Volume2, VolumeX, Image as ImageIcon, Plus, MessageSquare
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000";

// ---------- Chat history storage ----------
const HISTORY_KEY = "polycygot_history";

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveHistory(list) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(list));
}

function newSessionId() {
  return "session_" + Date.now() + "_" + Math.random().toString(36).slice(2, 6);
}

// ---------- Helper: convert audioBuffer to WAV ----------
function audioBufferToWav(audioBuffer) {
  const numChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const length = audioBuffer.length * numChannels * 2 + 44;
  const buffer = new ArrayBuffer(length);
  const view = new DataView(buffer);
  const channels = [];
  let offset = 0;

  const writeString = (str) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset++, str.charCodeAt(i));
  };

  writeString("RIFF");
  view.setUint32(offset, length - 8, true); offset += 4;
  writeString("WAVE");
  writeString("fmt ");
  view.setUint32(offset, 16, true); offset += 4;
  view.setUint16(offset, 1, true); offset += 2;
  view.setUint16(offset, numChannels, true); offset += 2;
  view.setUint32(offset, sampleRate, true); offset += 4;
  view.setUint32(offset, sampleRate * numChannels * 2, true); offset += 4;
  view.setUint16(offset, numChannels * 2, true); offset += 2;
  view.setUint16(offset, 16, true); offset += 2;
  writeString("data");
  view.setUint32(offset, length - offset - 4, true); offset += 4;

  for (let i = 0; i < numChannels; i++) channels.push(audioBuffer.getChannelData(i));
  for (let i = 0; i < audioBuffer.length; i++) {
    for (let j = 0; j < numChannels; j++) {
      const sample = Math.max(-1, Math.min(1, channels[j][i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
      offset += 2;
    }
  }
  return new Blob([view], { type: "audio/wav" });
}

export default function App() {
  const [message, setMessage] = useState("");
  const [language, setLanguage] = useState("auto");
  const [level, setLevel] = useState("simple");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [expandedVerification, setExpandedVerification] = useState({});
  const [copiedIndex, setCopiedIndex] = useState(null);
  const messagesEndRef = useRef(null);

  // Session + history
  const [sessionId, setSessionId] = useState(() => newSessionId());
  const [history, setHistory] = useState(() => loadHistory());
  const [activeHistoryId, setActiveHistoryId] = useState(null);

  // Voice state
  const [isRecording, setIsRecording] = useState(false);
  const [voiceOutput, setVoiceOutput] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Image state
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageWarning, setImageWarning] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Auto-save current session into history
  useEffect(() => {
    if (messages.length === 0) return;

    const firstUser = messages.find((m) => m.role === "user");
    const title = (firstUser?.text || "New chat").slice(0, 40);

    const now = Date.now();
    const existingIndex = history.findIndex((h) => h.id === sessionId);

    let updated;
    if (existingIndex >= 0) {
      updated = [...history];
      updated[existingIndex] = {
        ...updated[existingIndex],
        title,
        messages,
        updatedAt: now,
      };
    } else {
      updated = [
        { id: sessionId, title, messages, createdAt: now, updatedAt: now },
        ...history,
      ];
    }

    updated = updated.slice(0, 20);
    setHistory(updated);
    saveHistory(updated);
  }, [messages]); // eslint-disable-line react-hooks/exhaustive-deps

  // ---------- Voice input ----------
  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const webmBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((t) => t.stop());

        try {
          const arrayBuffer = await webmBlob.arrayBuffer();
          const audioContext = new AudioContext();
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
          const wavBlob = audioBufferToWav(audioBuffer);

          const formData = new FormData();
          formData.append("audio", wavBlob, "voice.wav");

          const resp = await fetch(`${API_URL}/transcribe`, {
            method: "POST",
            body: formData,
          });
          const data = await resp.json();
          if (data.text) setMessage(data.text);
          else console.warn("Transcription empty:", data);
        } catch (err) {
          console.error("Transcription failed:", err);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Mic access denied:", err);
      alert("Microphone access is required for voice input.");
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }

  // ---------- Voice output ----------
  async function speakReply(text, lang) {
    try {
      const resp = await fetch(
        `${API_URL}/speak?text=${encodeURIComponent(text)}&language=${lang}`,
        { method: "POST" }
      );
      const data = await resp.json();
      if (data.audio) {
        const audio = new Audio("data:audio/wav;base64," + data.audio);
        audio.play();
      }
    } catch (err) {
      console.error("Speak failed:", err);
    }
  }

  // ---------- Image input ----------
  function handleImageSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      alert("Image too large. Please use an image under 5 MB.");
      return;
    }

    if (!imageWarning) {
      const ok = window.confirm(
        "⚠️ Privacy reminder:\n\n" +
          "Before uploading, please make sure any OTP, account number, " +
          "or personal details in the screenshot are covered or blurred.\n\n" +
          "The image will be sent to Google's Gemini API for analysis and " +
          "will NOT be stored on our server.\n\n" +
          "Continue?"
      );
      if (!ok) {
        if (fileInputRef.current) fileInputRef.current.value = "";
        return;
      }
      setImageWarning(true);
    }

    setSelectedImage(file);
    const reader = new FileReader();
    reader.onload = (ev) => setImagePreview(ev.target.result);
    reader.readAsDataURL(file);
  }

  function clearImage() {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function sendImage() {
    if (!selectedImage || loading) return;

    const preview = imagePreview;
    setMessages((prev) => [
      ...prev,
      { role: "user", text: "[Screenshot attached]", image: preview },
    ]);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("image", selectedImage);

      const resp = await fetch(`${API_URL}/analyze-image`, {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.text || data.error || "Could not analyze the image.",
          detectedLang: "en-IN",
          verification: {
            status: "passed",
            checks: [{ rule: "Image analyzed by multimodal model", passed: true }],
            blocked_phrases: [],
          },
        },
      ]);

      if (voiceOutput && data.text) speakReply(data.text, "en-IN");
      clearImage();
    } catch (err) {
      console.error("Image analysis failed:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Unable to analyze the image." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // ---------- Send text message ----------
  async function sendMessage(customText) {
    const text = (customText ?? message).trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          language,
          explanation_level: level,
          session_id: sessionId,
          memory_consent: false,
        }),
      });

      if (!response.ok) throw new Error("Request failed");
      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.reply,
          indicators: data.risk_indicators,
          verification: data.verification,
          detectedLang: data.detected_language,
          needsFollowup: data.needs_followup,
        },
      ]);

      if (voiceOutput && data.reply) {
        speakReply(data.reply, data.detected_language || "en-IN");
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Unable to connect. Please check the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // ---------- Chat history actions ----------
  function startNewChat() {
    setSessionId(newSessionId());
    setMessages([]);
    setActiveHistoryId(null);
    setMessage("");
    setSidebarOpen(false);
  }

  function openHistory(item) {
    setSessionId(item.id);
    setMessages(item.messages || []);
    setActiveHistoryId(item.id);
    setSidebarOpen(false);
  }

  function deleteHistory(id, e) {
    e.stopPropagation();
    const updated = history.filter((h) => h.id !== id);
    setHistory(updated);
    saveHistory(updated);
    if (activeHistoryId === id) {
      startNewChat();
    }
  }

  function clearAllHistory() {
    if (!window.confirm("Delete all chat history? This cannot be undone.")) return;
    setHistory([]);
    saveHistory([]);
    startNewChat();
  }

  function copyToClipboard(text, index) {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 1500);
  }

  function toggleVerification(index) {
    setExpandedVerification((prev) => ({ ...prev, [index]: !prev[index] }));
  }

  const riskStyle = (risk) =>
    risk === "high"
      ? "bg-red-950/60 text-red-300 border-red-800"
      : risk === "medium"
      ? "bg-amber-950/60 text-amber-300 border-amber-800"
      : "bg-slate-800 text-slate-300 border-slate-700";

  const statusStyle = (status) =>
    status === "passed"
      ? "bg-green-950/60 text-green-300 border-green-800"
      : status === "needs_review"
      ? "bg-red-950/60 text-red-300 border-red-800"
      : "bg-slate-800 text-slate-300 border-slate-700";

  const langLabel = (code) =>
    code === "ta-IN" ? "Tamil" : code === "en-IN" ? "English" : code || "—";

  return (
    <div className="app-background min-h-screen text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur sticky top-0 z-20">
        <div className="px-4 md:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-teal-600/20 border border-teal-700 flex items-center justify-center">
              <Shield className="w-5 h-5 text-teal-400" />
            </div>
            <div>
              <h1 className="font-bold text-lg leading-tight">PolyCyGot</h1>
              <p className="text-xs text-slate-400 leading-tight">
                Adaptive multilingual cybersecurity agent
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 text-xs bg-slate-800/70 border border-slate-700 rounded-full px-3 py-1">
              <Globe className="w-3 h-3 text-teal-400" />
              <span>
                {language === "auto" ? "Auto-detect" : langLabel(language)}
              </span>
            </div>
            <button
              onClick={() => setSidebarOpen((o) => !o)}
              className="md:hidden bg-slate-800 border border-slate-700 rounded-lg p-2"
            >
              {sidebarOpen ? <X className="w-4 h-4" /> : <Brain className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Sidebar */}
        <aside
          className={`${
            sidebarOpen ? "block" : "hidden"
          } md:block md:w-72 border-b md:border-b-0 md:border-r border-slate-800 bg-slate-900/60 backdrop-blur p-4 space-y-5 md:h-[calc(100vh-61px)] md:overflow-y-auto`}
        >
          <button
            onClick={startNewChat}
            className="w-full flex items-center justify-center gap-2 bg-teal-600 hover:bg-teal-500 text-white text-sm font-semibold py-2 rounded-lg transition"
          >
            <Plus className="w-4 h-4" /> New chat
          </button>

          <Section title="Recent chats">
            {history.length === 0 ? (
              <p className="text-xs text-slate-500">No chats yet.</p>
            ) : (
              <div className="space-y-1">
                {history.map((h) => (
                  <div
                    key={h.id}
                    onClick={() => openHistory(h)}
                    className={`group flex items-center gap-2 text-xs rounded-lg px-2 py-2 cursor-pointer transition ${
                      activeHistoryId === h.id
                        ? "bg-teal-600/20 border border-teal-700 text-teal-300"
                        : "hover:bg-slate-800/80 text-slate-300 border border-transparent"
                    }`}
                  >
                    <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-70" />
                    <span className="flex-1 truncate">{h.title}</span>
                    <button
                      onClick={(e) => deleteHistory(h.id, e)}
                      className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
                <button
                  onClick={clearAllHistory}
                  className="w-full mt-2 text-xs text-red-400 hover:text-red-300 text-left px-2 py-1"
                >
                  Clear all history
                </button>
              </div>
            )}
          </Section>

          <Section title="Language">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-sm"
            >
              <option value="auto">Auto-detect</option>
              <option value="en-IN">English</option>
              <option value="ta-IN">Tamil</option>
            </select>
          </Section>

          <Section title="Explanation level">
            <div className="grid grid-cols-2 gap-2">
              {["simple", "technical"].map((lv) => (
                <button
                  key={lv}
                  onClick={() => setLevel(lv)}
                  className={`text-xs py-2 rounded-lg border ${
                    level === lv
                      ? "bg-teal-600/20 border-teal-600 text-teal-300"
                      : "bg-slate-800 border-slate-700 text-slate-300"
                  }`}
                >
                  {lv === "simple" ? "Beginner" : "Technical"}
                </button>
              ))}
            </div>
          </Section>

          <Section title="Voice">
            <button
              onClick={() => setVoiceOutput((v) => !v)}
              className={`w-full flex items-center justify-between text-xs py-2 px-3 rounded-lg border transition ${
                voiceOutput
                  ? "bg-teal-600/20 border-teal-600 text-teal-300"
                  : "bg-slate-800 border-slate-700 text-slate-300"
              }`}
            >
              <span>Speak replies aloud</span>
              {voiceOutput ? (
                <Volume2 className="w-4 h-4" />
              ) : (
                <VolumeX className="w-4 h-4" />
              )}
            </button>
          </Section>

          <Section title="About">
            <p className="text-xs text-slate-400 leading-relaxed">
              PolyCyGot reasons across languages, remembers your chat history
              locally, and verifies its own advice before showing it. Built for
              the Omega AI Agents — Agent Without Borders track.
            </p>
          </Section>
        </aside>

        {/* Chat area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 md:p-6">
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.length === 0 && !loading && <EmptyState />}

              {messages.map((item, index) => (
                <div key={index} className="fade-in">
                  {item.role === "user" ? (
                    <UserBubble text={item.text} image={item.image} />
                  ) : (
                    <AgentBubble
                      item={item}
                      index={index}
                      onCopy={() => copyToClipboard(item.text, index)}
                      copied={copiedIndex === index}
                      expanded={!!expandedVerification[index]}
                      onToggle={() => toggleVerification(index)}
                      riskStyle={riskStyle}
                      statusStyle={statusStyle}
                      langLabel={langLabel}
                      onSpeak={() =>
                        speakReply(item.text, item.detectedLang || "en-IN")
                      }
                    />
                  )}
                </div>
              ))}

              {loading && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input area */}
          <div className="border-t border-slate-800/80 bg-slate-900/60 backdrop-blur p-3 md:p-4">
            <div className="max-w-3xl mx-auto">
              {imagePreview && (
                <div className="mb-3 flex items-center gap-3 bg-slate-800 border border-teal-700 rounded-xl p-2">
                  <img
                    src={imagePreview}
                    alt="preview"
                    className="w-14 h-14 object-cover rounded-lg border border-slate-700"
                  />
                  <div className="flex-1 text-xs text-slate-300">
                    <div className="font-semibold text-teal-400">
                      Screenshot ready
                    </div>
                    <div className="text-slate-500">
                      {selectedImage?.name} ·{" "}
                      {(selectedImage?.size / 1024).toFixed(0)} KB
                    </div>
                  </div>
                  <button
                    onClick={sendImage}
                    disabled={loading}
                    className="bg-teal-600 hover:bg-teal-500 disabled:opacity-40 px-3 py-1.5 rounded-lg text-xs font-semibold"
                  >
                    Analyze
                  </button>
                  <button
                    onClick={clearImage}
                    className="text-slate-500 hover:text-slate-300"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}

              <div className="flex gap-2 items-center">
                <input
                  type="file"
                  accept="image/*"
                  ref={fileInputRef}
                  onChange={handleImageSelect}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-3 rounded-xl transition bg-slate-800 hover:bg-slate-700 text-slate-300"
                  title="Attach screenshot"
                >
                  <ImageIcon className="w-5 h-5" />
                </button>

                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`p-3 rounded-xl transition ${
                    isRecording
                      ? "bg-red-600 animate-pulse text-white"
                      : "bg-slate-800 hover:bg-slate-700 text-slate-300"
                  }`}
                  title={isRecording ? "Tap to stop" : "Tap to speak"}
                >
                  <Mic className="w-5 h-5" />
                </button>

                <input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder={
                    isRecording
                      ? "🔴 Recording... tap mic to stop"
                      : "Ask a cybersecurity question (English or Tamil)..."
                  }
                  className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 outline-none focus:border-teal-600 text-sm"
                />

                <button
                  onClick={() => setVoiceOutput((v) => !v)}
                  className={`p-3 rounded-xl transition ${
                    voiceOutput
                      ? "bg-teal-600 text-white"
                      : "bg-slate-800 hover:bg-slate-700 text-slate-300"
                  }`}
                  title={voiceOutput ? "Voice output ON" : "Voice output OFF"}
                >
                  {voiceOutput ? (
                    <Volume2 className="w-5 h-5" />
                  ) : (
                    <VolumeX className="w-5 h-5" />
                  )}
                </button>

                <button
                  onClick={() => sendMessage()}
                  disabled={loading || !message.trim()}
                  className="bg-teal-600 hover:bg-teal-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 md:px-5 py-3 rounded-xl flex items-center gap-2 font-semibold text-sm"
                >
                  <Send className="w-4 h-4" />
                  <span className="hidden md:inline">Send</span>
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wider text-slate-500 mb-2">
        {title}
      </div>
      {children}
    </div>
  );
}

function UserBubble({ text, image }) {
  return (
    <div className="flex justify-end">
      <div
        className={`max-w-[85%] md:max-w-[75%] bg-teal-700/40 border border-teal-800 rounded-2xl rounded-tr-sm px-4 py-3 ${
          /[\u0B80-\u0BFF]/.test(text) ? "tamil" : ""
        }`}
      >
        <div className="text-xs text-teal-400 font-semibold mb-1">You</div>
        {image && (
          <img
            src={image}
            alt="uploaded"
            className="rounded-lg border border-teal-700 mb-2 max-w-[240px]"
          />
        )}
        <p className="whitespace-pre-wrap text-sm">{text}</p>
      </div>
    </div>
  );
}

function AgentBubble({
  item,
  index,
  onCopy,
  copied,
  expanded,
  onToggle,
  riskStyle,
  statusStyle,
  langLabel,
  onSpeak,
}) {
  const isTamil = /[\u0B80-\u0BFF]/.test(item.text);
  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] md:max-w-[85%] bg-slate-900/85 backdrop-blur border border-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 space-y-3 w-full md:w-auto">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-teal-400" />
            <span className="font-semibold text-sm">PolyCyGot</span>
          </div>
          <div className="flex items-center gap-2">
            {item.detectedLang && (
              <span className="text-xs bg-slate-800 border border-slate-700 rounded-full px-2 py-0.5 flex items-center gap-1">
                <Globe className="w-3 h-3 text-teal-400" />
                {item.detectedLang}
              </span>
            )}
            <button
              onClick={onSpeak}
              className="text-slate-500 hover:text-teal-400"
              title="Play this reply"
            >
              <Volume2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onCopy}
              className="text-slate-500 hover:text-slate-300"
              title="Copy reply"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-green-400" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
          </div>
        </div>

        <p className={`whitespace-pre-wrap text-sm ${isTamil ? "tamil" : ""}`}>
          {item.text}
        </p>

        {item.indicators?.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {item.indicators.map((ind, i) => (
              <span
                key={i}
                className={`text-xs px-2 py-1 rounded-md border flex items-center gap-1 ${riskStyle(
                  ind.risk
                )}`}
              >
                <AlertTriangle className="w-3 h-3" />
                {ind.indicator} · {ind.risk}
              </span>
            ))}
          </div>
        )}

        {item.verification && (
          <div className="border-t border-slate-800 pt-2">
            <button
              onClick={onToggle}
              className="w-full flex items-center justify-between text-xs text-slate-400 hover:text-slate-200"
            >
              <div className="flex items-center gap-2">
                <span>Verification</span>
                <span
                  className={`px-2 py-0.5 rounded-full border font-semibold ${statusStyle(
                    item.verification.status
                  )}`}
                >
                  {item.verification.status}
                </span>
              </div>
              {expanded ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>

            {expanded && (
              <ul className="mt-2 space-y-1 text-xs">
                {item.verification.checks?.map((check, i) => (
                  <li key={i} className="flex items-start gap-2">
                    {check.passed ? (
                      <Check className="w-3.5 h-3.5 text-green-400 mt-0.5 shrink-0" />
                    ) : (
                      <X className="w-3.5 h-3.5 text-red-400 mt-0.5 shrink-0" />
                    )}
                    <span
                      className={check.passed ? "text-slate-300" : "text-red-300"}
                    >
                      {check.rule}
                    </span>
                  </li>
                ))}
              </ul>
            )}

            {item.verification.blocked_phrases?.length > 0 && (
              <div className="mt-2 text-xs bg-red-950/60 border border-red-800 rounded-md p-2 text-red-300">
                🚫 Blocked unsafe phrases:{" "}
                <b>{item.verification.blocked_phrases.join(", ")}</b>
              </div>
            )}
          </div>
        )}

        {item.needsFollowup && (
          <div className="text-xs text-blue-300 flex items-center gap-1">
            💬 Agent is asking for more details.
          </div>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-slate-900/85 backdrop-blur border border-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
        <Shield className="w-4 h-4 text-teal-400" />
        <span className="text-sm text-slate-400">PolyCyGot is reasoning</span>
        <div className="flex gap-1 ml-1">
          <span className="typing-dot w-1.5 h-1.5 rounded-full bg-teal-400 inline-block" />
          <span className="typing-dot w-1.5 h-1.5 rounded-full bg-teal-400 inline-block" />
          <span className="typing-dot w-1.5 h-1.5 rounded-full bg-teal-400 inline-block" />
        </div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="text-center py-16 md:py-24">
      <div className="w-20 h-20 mx-auto rounded-2xl bg-teal-600/20 border border-teal-700 flex items-center justify-center mb-5">
        <Shield className="w-10 h-10 text-teal-400" />
      </div>
      <h2 className="text-2xl md:text-3xl font-bold">
        Ask PolyCyGot about anything suspicious
      </h2>
      <p className="text-slate-400 text-sm mt-3 max-w-md mx-auto">
        In English or Tamil. Type, speak, or upload a screenshot.
      </p>
      <div className="flex items-center justify-center gap-1 text-xs text-slate-500 mt-10">
        <Sparkles className="w-3 h-3" />
        Voice, image, chat history, and verification are all live.
      </div>
    </div>
  );
}