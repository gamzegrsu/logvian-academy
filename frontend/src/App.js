// src/App.js
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

function App() {
  // görev sistemi
  const [tasks, setTasks] = useState([]);
  const [currentTask, setCurrentTask] = useState(null);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState(null);
  const [loadingTasks, setLoadingTasks] = useState(true);

  // chat (wizard)
  const [chatOpen, setChatOpen] = useState(true); // "her zaman açık" istedin -> true
  const [messages, setMessages] = useState([
    { id: "sys-0", sender: "bot", text: "🔮 Merhaba! Ben Bilge Logvian. Sor, öğren, pratiğe geçelim." }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sending, setSending] = useState(false);
  const messagesRef = useRef(null);

  // Load tasks from backend (task backend port 8000)
  useEffect(() => {
    setLoadingTasks(true);
    axios.get("http://127.0.0.1:8000/tasks")
      .then(res => setTasks(res.data || []))
      .catch(err => {
        console.error("Görev fetch hatası:", err);
        setTasks([]);
      })
      .finally(() => setLoadingTasks(false));
  }, []);

  // Autoscroll chat
  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // load single task
  const loadTask = (id) => {
    axios.get(`http://127.0.0.1:8000/tasks/${id}`)
      .then(res => {
        setCurrentTask(res.data);
        setResult(null);
        setAnswer("");
      })
      .catch(err => console.error("Görev yüklenemedi:", err));
  };

  const submitAnswer = () => {
    if (!currentTask) return;
    axios.post(`http://127.0.0.1:8000/tasks/${currentTask.id}/answer`, { answer })
      .then(res => setResult(res.data))
      .catch(err => {
        console.error("Cevap hatası:", err);
        setResult({ sonuc: "❌ Hata", feedback: "Sunucuya bağlanırken hata oluştu." });
      });
  };

  // Chat: send message to LLM server
  const sendChat = async () => {
    const text = chatInput.trim();
    if (!text || sending) return;
    setSending(true);

    const userMsg = { id: `u-${Date.now()}`, sender: "user", text };
    setMessages((m) => [...m, userMsg]);
    setChatInput("");

    try {
      setIsTyping(true); // "yazıyor" göstergesi
      // ask LLM (llm server on 8001)
      const res = await axios.post("http://127.0.0.1:8001/chat", { message: text }, { timeout: 120000 });
      const reply = res.data?.reply ?? "⚠️ Modelden geçerli cevap alınamadı.";
      const botMsg = { id: `b-${Date.now()}`, sender: "bot", text: reply };
      setMessages((m) => [...m, botMsg]);
    } catch (err) {
      console.error("Chat gönderme hatası:", err);
      setMessages((m) => [...m, { id: `err-${Date.now()}`, sender: "bot", text: "🚨 Sunucuya bağlanılamadı." }]);
    } finally {
      setIsTyping(false);
      setSending(false);
    }
  };

  // keys: enter to send (Shift+Enter yeni satır)
  const onChatKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChat();
    }
  };

  return (
    <div className="app-root">
      {/* Background video */}
      <video className="bg-video" autoPlay loop muted playsInline>
        <source src="/background.mp4" type="video/mp4" />
      </video>

      {/* Main centered content (title + tasks) */}
      <header className="main-header">
        <h1>🔮 Bilge Logvian - Siber Eğitmeni</h1>
        <h2>Görev Seç</h2>
        {loadingTasks ? (
          <p className="muted">⏳ Görevler yükleniyor...</p>
        ) : tasks.length === 0 ? (
          <p className="muted">🚨 Backend'den hiç görev gelmedi!</p>
        ) : (
          <div className="task-grid">
            {tasks.map((t) => (
              <button key={t.id} className="task-button" onClick={() => loadTask(t.id)}>
                {t.id}. {t.isim}
              </button>
            ))}
          </div>
        )}
      </header>

      {/* If a task is loaded show detail */}
      {currentTask && (
        <section className="task-detail">
          <h3>🌀 {currentTask.isim}</h3>
          <p>{currentTask.aciklama}</p>
          <div className="answer-row">
            <input className="answer-input" value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Cevabını yaz..." />
            <button className="btn primary" onClick={submitAnswer}>Gönder</button>
          </div>
          {result && (
            <div className="result-box">
              <b>{result.sonuc}</b>
              <p>{result.feedback}</p>
              {result.sonraki_gorev && <button className="btn" onClick={() => loadTask(result.sonraki_gorev)}>Sonraki Görev → {result.sonraki_gorev}</button>}
            </div>
          )}
          <button className="btn danger" onClick={() => setCurrentTask(null)}>Görev Listesine Dön</button>
        </section>
      )}

      {/* Wizard avatar bottom-right (click toggles chat) */}
      <div className="wizard-wrap">
        <img src="/logvian.png" alt="Bilge Logvian" className="wizard-avatar" onClick={() => setChatOpen((s) => !s)} />
      </div>

      {/* Chat box anchored under avatar (always visible if chatOpen true) */}
      {chatOpen && (
        <aside className="chat-panel" role="complementary" aria-label="Bilge Logvian Chat">
          <div className="chat-header">
            <div className="chat-avatar-title">
              <img src="/logvian.png" alt="" className="mini-avatar" />
              <div>
                <div className="chat-title">Bilge Logvian</div>
                <div className="chat-sub">Siber eğitmen — yardım için yaz</div>
              </div>
            </div>
            <button className="close-chat" onClick={() => setChatOpen(false)}>✕</button>
          </div>

          <div className="chat-messages" ref={messagesRef}>
            {messages.map((m) => (
              <div key={m.id} className={`chat-message ${m.sender === "user" ? "msg-user" : "msg-bot"}`}>
                <div className="msg-text">{m.text}</div>
              </div>
            ))}

            {isTyping && (
              <div className="chat-message msg-bot typing">
                <div className="msg-text">Bilge Logvian yazıyor<span className="dot">.</span><span className="dot">.</span><span className="dot">.</span></div>
              </div>
            )}
          </div>

          <div className="chat-input-row">
            <textarea
              className="chat-input"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={onChatKey}
              placeholder="Sorunu yaz (Enter gönderir, Shift+Enter yeni satır)..."
            />
            <button className="btn send" onClick={sendChat} disabled={sending}>
              {sending ? "Gönderiliyor..." : "Gönder"}
            </button>
          </div>
        </aside>
      )}
    </div>
  );
}

export default App;

