import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWebSocket } from '../hooks/useWebSocket';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DRAFT_KEY = 'sburb_character_draft';

const STORAGE_KEY = (code) => `sburb_session_${code}`;

function SessionLobby() {
  const navigate = useNavigate();

  // ── State machine ─────────────────────────────────────────────────────────
  const [mode, setMode] = useState('choose'); // 'choose' | 'setup' | 'lobby'
  const [isCreating, setIsCreating] = useState(false);
  const [sessionCode, setSessionCode] = useState('');
  const [codeInput, setCodeInput] = useState('');

  const [playerInfo, setPlayerInfo] = useState(null); // stored after joining
  const [sessionStatus, setSessionStatus] = useState(null);

  // Credentials for new joins
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  // Rejoin mode state
  const [rejoinCode, setRejoinCode] = useState('');
  const [rejoinUsername, setRejoinUsername] = useState('');
  const [rejoinPassword, setRejoinPassword] = useState('');

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const pollRef = useRef(null);

  // ── Character form ─────────────────────────────────────────────────────────
  // Load character creator draft — required to enter the lobby
  const [characterData] = useState(() => {
    try {
      const draft = localStorage.getItem(DRAFT_KEY);
      return draft ? JSON.parse(draft) : null;
    } catch { return null; }
  });

  // Guard: if no draft, send the player to create their character first
  useEffect(() => {
    if (!characterData) navigate('/create-character', { replace: true });
  }, [characterData, navigate]);

  // ── LLM-generated mechanical fields ─────────────────────────────────────
  const [generatedFields, setGeneratedFields] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [generationError, setGenerationError] = useState('');

  const generateFields = useCallback(async () => {
    if (!characterData) return;
    setGenerating(true);
    setGenerationError('');
    setGeneratedFields(null);
    try {
      const res = await fetch(`${API_URL}/api/generate-character`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ character_data: characterData }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Character generation failed');
      }
      setGeneratedFields(await res.json());
    } catch (e) {
      setGenerationError(e.message);
    } finally {
      setGenerating(false);
    }
  }, [characterData]);

  // ── API helpers ────────────────────────────────────────────────────────────
  const fetchStatus = useCallback(async (code) => {
    try {
      const res = await fetch(`${API_URL}/api/sessions/${code}/status`);
      if (res.ok) setSessionStatus(await res.json());
    // eslint-disable-next-line no-unused-vars, no-empty
    } catch (_e) {}
  }, []);

  // Poll session status while in lobby
  useEffect(() => {
    if (mode === 'lobby' && sessionCode) {
      fetchStatus(sessionCode);
      pollRef.current = setInterval(() => fetchStatus(sessionCode), 3000);
      return () => clearInterval(pollRef.current);
    }
  }, [mode, sessionCode, fetchStatus]);

  // ── WebSocket (lobby only) ────────────────────────────────────────────────
  const handleWsMessage = useCallback(
    (msg) => {
      if (msg.type === 'session_started') {
        navigate(`/game/${sessionCode}`, { replace: true });
      } else if (
        msg.type === 'player_ready_status' ||
        msg.type === 'connection_status'
      ) {
        fetchStatus(sessionCode);
      }
    },
    [sessionCode, navigate, fetchStatus]
  );

  const { connected } = useWebSocket({
    sessionCode,
    playerId: playerInfo?.playerId,
    onMessage: handleWsMessage,
    enabled: mode === 'lobby',
  });

  // ── Actions ────────────────────────────────────────────────────────────────
  const handleCreate = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/sessions`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to create session');
      const data = await res.json();
      setSessionCode(data.session_code);
      setIsCreating(true);
      setMode('setup');
      generateFields(); // kick off in parallel while player sees the code
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinSetup = () => {
    setIsCreating(false);
    setMode('setup');
    generateFields();
  };

  const handleJoinSubmit = async () => {
    const code = isCreating ? sessionCode : codeInput.trim().toUpperCase();
    if (!code) { setError('Session code is required'); return; }
    if (generating) { setError('Still processing your character — please wait.'); return; }
    if (!generatedFields) { setError('Character generation failed. Please retry.'); return; }
    if (!username.trim()) { setError('Username is required'); return; }
    if (!password) { setError('Password is required'); return; }

    setLoading(true);
    setError('');
    try {
      // Store land_full and lunar_sway in character_data.generated so the GM has them
      const enrichedCharacterData = {
        ...characterData,
        generated: {
          land_full: generatedFields.land_full,
          lunar_sway: generatedFields.lunar_sway,
        },
      };
      const res = await fetch(`${API_URL}/api/sessions/${code}/join`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_name:      generatedFields.player_name,
          username:         username.trim(),
          password:         password,
          player_class:     generatedFields.player_class,
          aspect:           generatedFields.aspect,
          title:            generatedFields.title,
          land:             generatedFields.land,
          denizen:          generatedFields.denizen,
          echeladder_rung:  generatedFields.echeladder_rung,
          strife_specibus:  generatedFields.strife_specibus,
          current_weapon:   generatedFields.current_weapon,
          sprite:           generatedFields.sprite,
          character_data:   enrichedCharacterData,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to join session');
      }
      const data = await res.json();
      const info = {
        playerId:    data.player_id,
        playerName:  data.player_name,
        playerColor: data.player_color,
        username:    username.trim(),
        ...generatedFields,
      };
      setPlayerInfo(info);
      setSessionCode(code);
      sessionStorage.setItem(STORAGE_KEY(code), JSON.stringify(info));
      setMode('lobby');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleReady = async () => {
    const myStatus = sessionStatus?.players?.find(
      (p) => p.player_id === playerInfo?.playerId
    );
    const nowReady = !myStatus?.ready;
    try {
      await fetch(
        `${API_URL}/api/sessions/${sessionCode}/players/${playerInfo.playerId}/ready`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ready: nowReady }),
        }
      );
      fetchStatus(sessionCode);
    // eslint-disable-next-line no-unused-vars, no-empty
    } catch (_e) {}
  };

  const handleStart = async () => {
    try {
      const res = await fetch(`${API_URL}/api/sessions/${sessionCode}/start`, {
        method: 'POST',
      });
      if (!res.ok) {
        const err = await res.json();
        setError(err.detail || 'Failed to start session');
      }
    // eslint-disable-next-line no-unused-vars, no-empty
    } catch (_e) {}
  };

  const handleRejoin = async () => {
    const code = rejoinCode.trim().toUpperCase();
    if (!code) { setError('Session code is required'); return; }
    if (!rejoinUsername.trim()) { setError('Username is required'); return; }
    if (!rejoinPassword) { setError('Password is required'); return; }
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/sessions/${code}/rejoin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: rejoinUsername.trim(), password: rejoinPassword }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Rejoin failed');
      }
      const data = await res.json();
      const info = {
        playerId:    data.player_id,
        playerName:  data.player_name,
        playerColor: data.player_color,
        username:    rejoinUsername.trim(),
      };
      sessionStorage.setItem(STORAGE_KEY(code), JSON.stringify(info));
      if (data.session_state === 'active') {
        navigate(`/game/${code}`, { replace: true });
      } else {
        setPlayerInfo(info);
        setSessionCode(code);
        setMode('lobby');
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const myPlayer = sessionStatus?.players?.find(
    (p) => p.player_id === playerInfo?.playerId
  );
  const allReady =
    (sessionStatus?.players?.length ?? 0) > 0 &&
    sessionStatus.players.every((p) => p.ready);

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="session-lobby">

      {/* ── CHOOSE ── */}
      {mode === 'choose' && (
        <div className="lobby-choose">
          <h1>:: SBURB MULTIPLAYER ::</h1>
          <p className="lobby-tagline">
            The game is about to begin.<br />Are you ready to enter the Medium?
          </p>
          <div className="lobby-actions">
            <button onClick={handleCreate} disabled={loading} className="btn-create">
              {loading ? 'CREATING...' : '[ CREATE SESSION ]'}
            </button>
            <button onClick={handleJoinSetup} className="btn-join">
              [ JOIN SESSION ]
            </button>
            <button onClick={() => { setMode('rejoin'); setError(''); }} className="btn-rejoin">
              [ REJOIN SESSION ]
            </button>
          </div>
          {error && <p className="error-msg">{error}</p>}
        </div>
      )}

      {/* ── SETUP ── */}
      {mode === 'setup' && (
        <div className="lobby-setup">
          <h1>:: SBURB SESSION ::</h1>

          {isCreating ? (
            <div
              className="session-code-display"
              onClick={() => navigator.clipboard.writeText(sessionCode)}
              title="Click to copy"
            >
              <span className="code-label">YOUR SESSION CODE (click to copy)</span>
              <span className="code-value">{sessionCode}</span>
              <small>Share this with your players!</small>
            </div>
          ) : (
            <div className="form-group">
              <label>SESSION CODE</label>
              <input
                type="text"
                value={codeInput}
                onChange={(e) => setCodeInput(e.target.value.toUpperCase())}
                placeholder="ENTER CODE  (e.g. ABC123)"
                maxLength={6}
                className="code-input"
                autoFocus
              />
            </div>
          )}

          {/* Character identity — locked from Character Creator */}
          <div className="character-identity-banner">
            <span className="identity-name">{characterData?.identity?.name || '???'}</span>
            <button
              type="button"
              className="btn-edit-character"
              onClick={() => navigate('/create-character')}
            >
              ✎ Edit Character
            </button>
          </div>

          {/* Credentials — used to rejoin later if the tab is closed */}
          <div className="credentials-section">
            <div className="form-group">
              <label>USERNAME</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Choose a username"
                autoComplete="username"
              />
            </div>
            <div className="form-group">
              <label>PASSWORD</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Choose a password to rejoin later"
                autoComplete="new-password"
              />
            </div>
          </div>

            {/* LLM-generated character preview */}
          {generating && (
            <div className="char-generating">
              <p className="generating-message">
                <span className="thinking-dots">The Sburb servers are processing your data</span>
              </p>
              <p className="generating-sub">Assigning your session parameters...</p>
            </div>
          )}

          {!generating && generationError && (
            <div className="char-gen-error">
              <p>⚠ {generationError}</p>
              <button onClick={generateFields} className="btn-secondary">↻ Retry</button>
            </div>
          )}

          {!generating && generatedFields && (
            <div className="char-preview">
              <div className="char-preview-row">
                <span className="preview-label">STRIFE SPECIBUS</span>
                <span className="preview-value">{generatedFields.strife_specibus}</span>
              </div>
              <div className="char-preview-row">
                <span className="preview-label">STARTING WEAPON</span>
                <span className="preview-value">{generatedFields.current_weapon}</span>
              </div>
              <div className="char-preview-row">
                <span className="preview-label">ECHELADDER</span>
                <span className="preview-value">{generatedFields.echeladder_rung}</span>
              </div>
              <div className="char-preview-row">
                <span className="preview-label">LAND</span>
                <span className="preview-value">{generatedFields.land_full || generatedFields.land}</span>
              </div>
              <div className="char-preview-row">
                <span className="preview-label">DREAM MOON</span>
                <span className={`preview-value sway-${generatedFields.lunar_sway?.toLowerCase()}`}>
                  {generatedFields.lunar_sway}
                </span>
              </div>
              <p className="preview-hint">Your class and aspect will reveal themselves through play.</p>
            </div>
          )}

          {error && <p className="error-msg">{error}</p>}

          <div className="setup-actions">
            <button
              onClick={() => { setMode('choose'); setError(''); }}
              className="btn-secondary"
            >
              &lt; BACK
            </button>
            <button
              onClick={handleJoinSubmit}
              disabled={loading || generating || !!generationError || !generatedFields}
            >
              {loading ? 'JOINING...' : generating ? 'PROCESSING...' : (isCreating ? '[ ENTER LOBBY ]' : '[ JOIN SESSION ]')}
            </button>
          </div>
        </div>
      )}

      {/* ── REJOIN ── */}
      {mode === 'rejoin' && (
        <div className="lobby-setup">
          <h1>:: REJOIN SESSION ::</h1>
          <p className="lobby-tagline">Enter your credentials to reconnect.</p>

          <div className="form-group">
            <label>SESSION CODE</label>
            <input
              type="text"
              value={rejoinCode}
              onChange={(e) => setRejoinCode(e.target.value.toUpperCase())}
              placeholder="ENTER CODE  (e.g. ABC123)"
              maxLength={6}
              className="code-input"
              autoFocus
            />
          </div>
          <div className="form-group">
            <label>USERNAME</label>
            <input
              type="text"
              value={rejoinUsername}
              onChange={(e) => setRejoinUsername(e.target.value)}
              placeholder="Your username"
              autoComplete="username"
            />
          </div>
          <div className="form-group">
            <label>PASSWORD</label>
            <input
              type="password"
              value={rejoinPassword}
              onChange={(e) => setRejoinPassword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleRejoin()}
              placeholder="Your password"
              autoComplete="current-password"
            />
          </div>

          {error && <p className="error-msg">{error}</p>}

          <div className="setup-actions">
            <button
              onClick={() => { setMode('choose'); setError(''); }}
              className="btn-secondary"
            >
              &lt; BACK
            </button>
            <button onClick={handleRejoin} disabled={loading}>
              {loading ? 'RECONNECTING...' : '[ RECONNECT ]'}
            </button>
          </div>
        </div>
      )}

      {/* ── LOBBY ── */}
      {mode === 'lobby' && playerInfo && (
        <div className="lobby-waiting">
          <h1>:: SESSION LOBBY ::</h1>

          <div
            className="session-code-display"
            onClick={() => navigator.clipboard.writeText(sessionCode)}
            title="Click to copy"
          >
            <span className="code-label">SESSION CODE (click to copy)</span>
            <span className="code-value">{sessionCode}</span>
            <small>Share with your players!</small>
          </div>

          <div className={`ws-status ${connected ? 'connected' : 'disconnected'}`}>
            {connected ? '● CONNECTED' : '○ CONNECTING...'}
          </div>

          <div className="player-list">
            <h3>PLAYERS IN SESSION</h3>
            {(sessionStatus?.players ?? []).map((p) => (
              <div key={p.player_id} className={`player-entry ${p.ready ? 'ready' : ''}`}>
                <span className="player-color-dot" style={{ backgroundColor: p.color }} />
                <span className="player-name">
                  {p.name}
                  {p.player_id === playerInfo.playerId && ' (you)'}
                </span>
                <span className="player-status">
                  {!p.connected && '(offline) '}
                  {p.ready ? '[ READY ]' : '[ NOT READY ]'}
                </span>
              </div>
            ))}
            {(sessionStatus?.players?.length ?? 0) === 0 && (
              <p style={{ color: '#888', margin: 0 }}>Waiting for players...</p>
            )}
          </div>

          <div className="lobby-controls">
            <button
              onClick={handleToggleReady}
              className={myPlayer?.ready ? 'btn-secondary' : ''}
            >
              {myPlayer?.ready ? '[ UNREADY ]' : '[ MARK READY ]'}
            </button>
            {allReady && (
              <button onClick={handleStart} className="btn-start">
                ▶ START GAME
              </button>
            )}
          </div>

          <p className="lobby-hint">
            {allReady
              ? 'All players ready! Press START GAME to begin.'
              : 'Waiting for all players to mark ready...'}
          </p>
        </div>
      )}

    </div>
  );
}

export default SessionLobby;
