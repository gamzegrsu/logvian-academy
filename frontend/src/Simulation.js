// Simulation.js
import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import axios from 'axios';

const Simulation = () => {
  const { labName } = useParams();
  const [searchParams] = useSearchParams();
  const userId = searchParams.get('user_id');

  const [simulation, setSimulation] = useState(null);
  const [currentChallenge, setCurrentChallenge] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadSimulation();
  }, [labName, userId]);

  const loadSimulation = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/simulation/${labName}/status?user_id=${userId}`);
      setSimulation(response.data);
      setCurrentChallenge(response.data.current_challenge_data);
    } catch (error) {
      console.error("Simülasyon yüklenemedi:", error);
    }
  };

  const submitAnswer = async () => {
    try {
      const response = await axios.post(`http://localhost:8000/api/simulation/${labName}/submit?user_id=${userId}`, {
        answer: userAnswer
      });

      setMessage(response.data.message);

      if (response.data.correct) {
        setUserAnswer('');
        if (response.data.completed) {
          setMessage(`${response.data.message} 🎉 Lab tamamlandı!`);
        } else {
          loadSimulation(); // Sonraki challenge'ı yükle
        }
      }
    } catch (error) {
      setMessage("Cevap gönderilemedi: " + error.message);
    }
  };

  if (!simulation) return <div>Yükleniyor...</div>;

  return (
    <div className="simulation-container">
      <h1>🔬 {labName.replace('_', ' ').toUpperCase()} Simülasyonu</h1>

      {simulation.completed ? (
        <div className="completed-message">
          <h2>🎉 Tebrikler! Lab tamamlandı!</h2>
          <button onClick={() => window.close()}>Sayfayı Kapat</button>
        </div>
      ) : (
        <div className="challenge-container">
          <h2>Görev {simulation.current_challenge + 1}/{simulation.total_challenges}</h2>
          <h3>{currentChallenge?.title}</h3>
          <p>{currentChallenge?.description}</p>

          <div className="answer-section">
            <input
              type="text"
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              placeholder="Cevabınızı girin..."
              onKeyPress={(e) => e.key === 'Enter' && submitAnswer()}
            />
            <button onClick={submitAnswer}>Gönder</button>
          </div>

          {message && <div className="message">{message}</div>}
        </div>
      )}
    </div>
  );
};

export default Simulation;