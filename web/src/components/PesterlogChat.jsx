import React, { useState, useEffect, useRef } from 'react';

const QUIRK_STORAGE_KEY = (playerId) => `sburb_quirk_${playerId}`;

function applyQuirk(text, quirk) {
  if (!text) return text;
  if (quirk === 'leet-b') {
    return text.replace(/b/gi, '8');
  }
  if (quirk === 'caps-loud') {
    return `${text.toUpperCase()}!!!`;
  }
  if (quirk === 'zero-o') {
    return text.replace(/o/gi, '0');
  }
  return text;
}

/**
 * PesterlogChat – in-session real-time chat panel.
 *
 * @param {Array}    messages   – array of pesterlog_message WS payloads
 * @param {object}   playerInfo – { playerId, playerName, playerColor, ... }
 * @param {function} onSend     – callback(text: string) to send a message
 */
function PesterlogChat({ messages, playerInfo, onSend }) {
  const [input, setInput] = useState('');
  const [quirk, setQuirk] = useState(() => {
    try {
      return localStorage.getItem(QUIRK_STORAGE_KEY(playerInfo?.playerId)) || 'none';
    } catch {
      return 'none';
    }
  });
  const endRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    try {
      localStorage.setItem(QUIRK_STORAGE_KEY(playerInfo?.playerId), quirk);
    } catch {
      // no-op when storage is unavailable
    }
  }, [quirk, playerInfo?.playerId]);

  const handleSend = () => {
    const text = input.trim();
    if (!text) return;
    onSend(applyQuirk(text, quirk));
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="pesterlog-panel">
      <div className="pesterlog-header">:: PESTERCHUM ::</div>

      <div className="pesterlog-quirk-row">
        <label htmlFor="pesterlog-quirk" className="pesterlog-quirk-label">Quirk:</label>
        <select
          id="pesterlog-quirk"
          className="pesterlog-quirk-select"
          value={quirk}
          onChange={(e) => setQuirk(e.target.value)}
        >
          <option value="none">None</option>
          <option value="leet-b">b → 8</option>
          <option value="caps-loud">ALL CAPS + !!!</option>
          <option value="zero-o">o → 0</option>
        </select>
      </div>

      <div className="pesterlog-messages">
        {messages.length === 0 && (
          <p className="pesterlog-empty">No messages yet.</p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`pesterlog-msg ${msg.from_player_id === playerInfo.playerId ? 'own-msg' : ''} ${msg.is_broadcast ? 'broadcast-msg' : ''}`}
          >
            <span className="pesterlog-time">
              {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
            </span>
            <span
              className="pesterlog-sender"
              style={{ color: msg.from_player_color || '#ff8b8b' }}
            >
              {msg.from_player_name}:
            </span>
            <span className="pesterlog-text"> {msg.message}</span>
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <div className="pesterlog-input-row">
        <input
          type="text"
          className="pesterlog-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="say something..."
          style={{ borderColor: playerInfo.playerColor }}
        />
        <button className="pesterlog-send" onClick={handleSend}>
          SEND
        </button>
      </div>
    </div>
  );
}

export default PesterlogChat;
