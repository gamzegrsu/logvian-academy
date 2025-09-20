import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

// Görsel dosyalarını import ediyoruz
import logvianImage from "./logvian.png";
import backgroundVideo from "./background.mp4";
import logvianAvatar from "./logvian.png";
import userAvatar from "./logvian.png";
import systemAvatar from "./logvian.png";

function App() {
  const [tasks, setTasks] = useState([]);
  const [chatMessages, setChatMessages] = useState([
    {
      id: 1,
      character: "wizard",
      text: "🔮 Merhaba! Ben Bilge Logvian. Siber güvenlik yolculuğunda sana rehberlik edeceğim. Hadi başlayalım!",
      avatar: logvianAvatar,
      timestamp: new Date()
    }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [userProgress, setUserProgress] = useState({
    level: 1,
    total_xp: 0,
    total_coins: 100,
    next_level_xp: 100,
    completed_tasks: [],
    hints: []
  });
  const [userId] = useState(`user_${Math.random().toString(36).substr(2, 9)}`);
  const [activeTask, setActiveTask] = useState(null);
  const [runningLabs, setRunningLabs] = useState({});
  const [showLabModal, setShowLabModal] = useState(false);
  const [activeLab, setActiveLab] = useState(null);
  const [answerInput, setAnswerInput] = useState("");
  const [particleEffects, setParticleEffects] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadTasks();
    loadUserProgress();
    loadRunningLabs();

    // Partikül efekti için periyodik temizlik
    const interval = setInterval(() => {
      if (particleEffects.length > 15) {
        setParticleEffects(prev => prev.slice(5));
      }
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, isTyping]);

  const addParticleEffect = (x, y, type) => {
    const newParticle = {
      id: Date.now(),
      x,
      y,
      type,
      createdAt: Date.now()
    };
    setParticleEffects(prev => [...prev, newParticle]);
  };

  const loadTasks = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/tasks?user_id=${userId}`);
      setTasks(response.data.tasks);
    } catch (error) {
      console.error("Görevler yüklenemedi:", error);
      // Fallback görevler
      setTasks([
        { id: 1, title: "SQL Injection", description: "SQL enjeksiyon saldırılarını öğren", reward: { xp: 25, coins: 15 }, completed: false, locked: false },
        { id: 2, title: "XSS - Stored", description: "XSS payload'larını deneyimle", reward: { xp: 30, coins: 20 }, completed: false, locked: true },
        { id: 3, title: "Hash Cracking", description: "Hash fonksiyonlarını çözümle", reward: { xp: 35, coins: 25 }, completed: false, locked: true }
      ]);
    }
  };

  const loadUserProgress = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/user/${userId}/progress`);
      setUserProgress(response.data.progress);
    } catch (error) {
      console.error("Kullanıcı ilerlemesi yüklenemedi:", error);
    }
  };

  const loadRunningLabs = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/lab/running");
      setRunningLabs(response.data.running);
    } catch (error) {
      console.error("Çalışan lablar yüklenemedi:", error);
    }
  };

  const startLab = async (taskId) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/lab/${taskId}/start`, {
        user_id: userId
      });

      setRunningLabs(prev => ({
        ...prev,
        [response.data.container_name]: response.data
      }));

      setActiveLab(response.data);
      setShowLabModal(true);

      // Partikül efekti
      addParticleEffect('50%', '50%', 'reward');

      const labMessage = {
        id: Date.now(),
        character: "system",
        text: `🔬 Lab başlatıldı! Görevi burada tamamlayabilirsin: ${response.data.lab_url}`,
        avatar: systemAvatar,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, labMessage]);

    } catch (error) {
      console.error("Lab başlatılamadı:", error);
      alert("Lab başlatılamadı: " + (error.response?.data?.detail || error.message));
    }
  };

  const stopLab = async (containerName) => {
    try {
      await axios.post("http://localhost:8000/api/lab/stop", {
        container_name: containerName
      });

      setRunningLabs(prev => {
        const newLabs = { ...prev };
        delete newLabs[containerName];
        return newLabs;
      });

    } catch (error) {
      console.error("Lab durdurulamadı:", error);
    }
  };

  const submitAnswer = async (taskId, answer) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/tasks/${taskId}/answer`, {
        user_id: userId,
        answer: answer
      });

      if (response.data.correct) {
        setUserProgress(response.data.user_progress);
        setAnswerInput("");

        // Partikül efekti
        addParticleEffect('50%', '50%', 'levelup');

        alert(`🎉 Tebrikler! ${response.data.rewards.xp} XP ve ${response.data.rewards.coins} jeton kazandın!`);
      } else {
        alert("❌ Yanlış cevap. Tekrar dene!");
      }
    } catch (error) {
      console.error("Cevap gönderilemedi:", error);
    }
  };

  const getHint = async (taskId) => {
    try {
      const response = await axios.post("http://localhost:8000/api/hint", {
        user_id: userId,
        task_id: taskId
      });

      alert(`💡 İpucu: ${response.data.hint}\nKalan jetonlar: ${response.data.coins_left}`);
      setUserProgress(prev => ({ ...prev, coins: response.data.coins_left }));

    } catch (error) {
      console.error("İpucu alınamadı:", error);
      alert("İpucu alınamadı: " + (error.response?.data?.detail || "Yeterli jetonun yok"));
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || isTyping) return;

    // Mesaj gönderme partikül efekti
    addParticleEffect('80%', '90%', 'message');

    const userMessage = {
      id: Date.now(),
      character: "user",
      text: chatInput,
      avatar: userAvatar,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput("");
    setIsTyping(true);

    try {
      const response = await axios.post("http://localhost:8000/api/chat", {
        message: chatInput,
        user_id: userId,
        character: "Bilge Logvian"
      });

      const botMessage = {
        id: Date.now() + 1,
        character: "wizard",
        text: response.data.response,
        avatar: logvianAvatar,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error("Mesaj gönderilemedi:", error);
      const errorMessage = {
        id: Date.now() + 1,
        character: "system",
        text: "⚠️ Sunucuya bağlanılamadı. Lütfen tekrar dene.",
        avatar: systemAvatar,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  const xpPercentage = (userProgress.total_xp / 1000) * 100; // 1000 XP'de level atla

  return (
    <div className="app-container">
      {/* Arka Plan Video */}
      <video className="background-video" autoPlay loop muted playsInline>
        <source src={backgroundVideo} type="video/mp4" />
      </video>

      {/* Partikül Efektleri */}
      <div className="particle-container">
        {particleEffects.map(particle => (
          <div
            key={particle.id}
            className={`particle ${particle.type}`}
            style={{
              left: particle.x,
              top: particle.y
            }}
          >
            {particle.type === 'reward' && '✨'}
            {particle.type === 'levelup' && '🚀'}
            {particle.type === 'message' && '💬'}
          </div>
        ))}
      </div>

      {/* Ana İçerik */}
      <div className="main-content">
        {/* Üst Panel */}
        <div className="top-panel">
          <div className="user-stats">
            <div className="level-display">
              <span className="level-badge">Seviye {Math.floor(userProgress.total_xp / 1000) + 1}</span>
              <div className="xp-bar">
                <div
                  className="xp-progress"
                  style={{ width: `${xpPercentage}%` }}
                ></div>
                <span className="xp-text">{userProgress.total_xp}/1000 XP</span>
              </div>
            </div>

            <div className="currency-display">
              <div className="coins">
                <span className="coin-icon">🪙</span>
                <span className="coin-amount">{userProgress.total_coins}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="content-wrapper">
          {/* Sol Panel - Görevler */}
          <div className="left-panel">
            <div className="panel-header">
              <h2>📜 Görev Seç</h2>
            </div>
            <div className="tasks-grid">
              {tasks.map(task => (
                <div
                  key={task.id}
                  className={`task-card ${task.completed ? 'completed' : ''} ${task.locked ? 'locked' : ''}`}
                  onClick={() => !task.locked && setActiveTask(task)}
                >
                  <div className="task-header">
                    <h3>{task.title}</h3>
                    <span className="task-badge">{task.reward.xp} XP</span>
                  </div>
                  <p>{task.description}</p>
                  <div className="task-actions">
                    {!task.locked && !task.completed && (
                      <>
                        <button onClick={(e) => { e.stopPropagation(); startLab(task.id); }} className="lab-button">
                          🔬 Lab Başlat
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); getHint(task.id); }} className="hint-button">
                          💡 İpucu (10🪙)
                        </button>
                      </>
                    )}
                    {task.completed && (
                      <span className="completed-badge">✓ Tamamlandı</span>
                    )}
                    {task.locked && (
                      <span className="locked-badge">🔒 Kilitli</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Orta Panel - Chat */}
          <div className="chat-section">
            {/* Chat Arka Planında Bilge Logvian */}
            <div className="chat-bg-wizard">
              <img src={logvianImage} alt="Bilge Logvian" />
            </div>

            <div className="chat-header">
              <h2>🔮 Bilge Logvian</h2>
              <div className="online-indicator"></div>
              <div className="magic-sparkle"></div>
            </div>

            <div className="chat-messages">
              {chatMessages.map(msg => (
                <div key={msg.id} className={`message ${msg.character}`}>
                  <img src={msg.avatar} alt="avatar" className="avatar" />
                  <div className="message-content">
                    <div className="message-text">{msg.text}</div>
                    <div className="message-time">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="message wizard typing">
                  <img src={logvianAvatar} alt="avatar" className="avatar" />
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef}></div>
            </div>

            <div className="chat-input-container">
              <textarea
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Bilge Logvian'a soru sor..."
                rows="1"
              />
              <button
                onClick={sendChatMessage}
                disabled={!chatInput.trim() || isTyping}
                className="send-button"
              >
                📤
              </button>
            </div>
          </div>

          {/* Sağ Panel - Lab Durumu ve Cevap Kutusu */}
          <div className="right-panel">
            <div className="panel-tabs">
              <button className="active">🔬 Aktif Lablar</button>
            </div>

            <div className="panel-content">
              <div className="labs-list">
                {Object.keys(runningLabs).length === 0 ? (
                  <div className="no-labs">
                    <p>Şu anda aktif lab bulunmuyor</p>
                  </div>
                ) : (
                  Object.entries(runningLabs).map(([name, lab]) => (
                    <div key={name} className="lab-item">
                      <h4>{lab.lab}</h4>
                      <p>URL: <a href={lab.url} target="_blank" rel="noopener noreferrer">{lab.url}</a></p>
                      <button
                        onClick={() => stopLab(name)}
                        className="stop-lab-button"
                      >
                        ⏹ Durdur
                      </button>
                    </div>
                  ))
                )}
              </div>

              {activeTask && (
                <div className="answer-section">
                  <h3>✏️ Cevap Gönder</h3>
                  <p>{activeTask.title} görevi için flag gönder:</p>
                  <div className="answer-input-container">
                    <input
                      type="text"
                      value={answerInput}
                      onChange={e => setAnswerInput(e.target.value)}
                      placeholder="Flag girin..."
                    />
                    <button
                      onClick={() => submitAnswer(activeTask.id, answerInput)}
                      className="submit-answer-button"
                    >
                      Gönder
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Lab Modal */}
      {showLabModal && activeLab && (
        <div className="modal-overlay" onClick={() => setShowLabModal(false)}>
          <div className="lab-modal" onClick={e => e.stopPropagation()}>
            <h2>🔬 Lab Başlatıldı!</h2>
            <p>Görevi tamamlamak için aşağıdaki linke tıklayabilirsin:</p>
            <a href={activeLab.lab_url} target="_blank" rel="noopener noreferrer" className="lab-link">
              {activeLab.lab_url}
            </a>
            <div className="modal-actions">
              <button onClick={() => setShowLabModal(false)}>Tamam</button>
              <button onClick={() => stopLab(activeLab.container_name)} className="stop-button">
                Lab'ı Durdur
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;