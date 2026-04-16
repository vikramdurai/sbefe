import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { useWebSocket } from '../hooks/useWebSocket';
import { GameStateProvider, useGameState } from '../state/GameStateContext';
import StagingWindow from '../components/StagingWindow';
import PesterlogChat from '../components/PesterlogChat';
import BroadcastOverlay from '../components/BroadcastOverlay';
// Disabled HUD components
// import HealthBar from '../components/HealthBar';
// import ExperienceBar from '../components/ExperienceBar';
// import GristDisplay from '../components/GristDisplay';
// import EquipmentPanel from '../components/EquipmentPanel';
// import InventoryGrid from '../components/InventoryGrid';
// import CombatHUD from '../components/CombatHUD';
// import ActionButtons from '../components/ActionButtons';
// import AlchemyPanel from '../components/AlchemyPanel';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const STORAGE_KEY = (code) => `sburb_session_${code}`;

function loadStoredPlayerInfo(sessionCode) {
  const key = STORAGE_KEY(sessionCode);
  try {
    const tabScoped = sessionStorage.getItem(key);
    if (tabScoped) {
      return JSON.parse(tabScoped);
    }

    // Backward compatibility: migrate old localStorage session data once.
    const legacy = localStorage.getItem(key);
    if (legacy) {
      sessionStorage.setItem(key, legacy);
      localStorage.removeItem(key);
      return JSON.parse(legacy);
    }
  } catch {
    return null;
  }
  return null;
}

function GameRoomContent() {
  const { sessionCode } = useParams();
  const navigate = useNavigate();
  const { gameState, applyGameStatePatch, setInCombat } = useGameState();

  // Player info from tab-scoped sessionStorage (set during lobby join/rejoin)
  const [playerInfo, setPlayerInfo] = useState(() => {
    return loadStoredPlayerInfo(sessionCode);
  });

  // Rejoin form state (shown when stored tab data is missing)
  const [rejoinUsername, setRejoinUsername] = useState('');
  const [rejoinPassword, setRejoinPassword] = useState('');
  const [rejoinError, setRejoinError] = useState('');
  const [rejoinLoading, setRejoinLoading] = useState(false);

  // ── Game state ─────────────────────────────────────────────────────────────
  const [narrativeLog, setNarrativeLog] = useState([]);
  const [stagingDrafts, setStagingDrafts] = useState({}); // { player_id: draft_text }
  const [pesterlogMessages, setPesterlogMessages] = useState([]);
  const [broadcasts, setBroadcasts] = useState([]);
  const [connectedPlayers, setConnectedPlayers] = useState({}); // { player_id: PlayerStatus }
  const [isProcessing, setIsProcessing] = useState(false);
  const [actionInput, setActionInput] = useState('');
  const [showPesterlog, setShowPesterlog] = useState(false);
  const [showInventory, setShowInventory] = useState(false);
  const [actionButtons, setActionButtons] = useState([]);
  const [showAlchemy, setShowAlchemy] = useState(false);
  const [partyStatus, setPartyStatus] = useState({ active: false, partyMembers: [] });
  const [partyNotice, setPartyNotice] = useState('');
  const [isStreamingResponse, setIsStreamingResponse] = useState(false);
  const [streamingNarrative, setStreamingNarrative] = useState('');

  const narrativeEndRef = useRef(null);
  const stagingTimerRef = useRef(null);
  const partyDebounceRef = useRef(null);
  const partyNoticeTimerRef = useRef(null);

  // Fetch initial player list
  useEffect(() => {
    if (!sessionCode) return;
    fetch(`${API_URL}/api/sessions/${sessionCode}/status`)
      .then((r) => r.json())
      .then((data) => {
        const map = {};
        (data.players ?? []).forEach((p) => { map[p.player_id] = p; });
        setConnectedPlayers(map);
      })
      .catch(() => {});
  }, [sessionCode]);

  // Auto-scroll narrative to bottom
  useEffect(() => {
    narrativeEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [narrativeLog, isProcessing]);

  useEffect(() => () => {
    clearTimeout(stagingTimerRef.current);
    clearTimeout(partyDebounceRef.current);
    clearTimeout(partyNoticeTimerRef.current);
  }, []);

  // ── WebSocket message handler ──────────────────────────────────────────────
  const handleWsMessage = useCallback((msg) => {
    switch (msg.type) {

      case 'gm_response':
        setIsProcessing(false);
        setIsStreamingResponse(false);
        setStreamingNarrative('');
        if (msg.game_state_patch) {
          applyGameStatePatch(msg.game_state_patch);
        }
        if (Array.isArray(msg.actions)) {
          setActionButtons(msg.actions);
        }
        setNarrativeLog((log) => [
          ...log,
          {
            id: Date.now(),
            kind: 'gm',
            narrative: msg.narrative,
            updatesCount: msg.updates_count,
            timestamp: msg.timestamp,
          },
        ]);
        break;

      case 'gm_stream_start':
        setIsStreamingResponse(true);
        setStreamingNarrative('');
        break;

      case 'gm_stream_chunk':
        setStreamingNarrative((current) => current + (msg.chunk || ''));
        break;

      case 'gm_stream_end': {
        const finalNarrative = msg.narrative || streamingNarrative;
        if (msg.game_state_patch) {
          applyGameStatePatch(msg.game_state_patch);
        }
        if (Array.isArray(msg.actions)) {
          setActionButtons(msg.actions);
        }
        setNarrativeLog((log) => [
          ...log,
          {
            id: Date.now(),
            kind: 'gm',
            narrative: finalNarrative,
            updatesCount: msg.updates_count,
            timestamp: msg.timestamp,
          },
        ]);
        setIsStreamingResponse(false);
        setStreamingNarrative('');
        setIsProcessing(false);
        break;
      }

      case 'staging_update':
        setStagingDrafts((d) => ({ ...d, [msg.player_id]: msg.draft_text }));
        break;

      case 'pesterlog_message':
        setPesterlogMessages((m) => [...m, msg]);
        break;

      case 'broadcast_event': {
        const id = Date.now() + Math.random();
        setBroadcasts((b) => [...b, { ...msg, id }]);
        setPesterlogMessages((m) => [
          ...m,
          {
            from_player_id: 'broadcast',
            from_player_name: 'BROADCAST',
            from_player_color: '#ff7c7c',
            message: msg.event_text,
            is_broadcast: true,
            timestamp: msg.timestamp,
          },
        ]);
        setTimeout(() => setBroadcasts((b) => b.filter((e) => e.id !== id)), 8000);
        break;
      }

      case 'connection_status':
        setConnectedPlayers((prev) => ({
          ...prev,
          [msg.player_id]: {
            ...(prev[msg.player_id] ?? {}),
            connected: msg.connected,
          },
        }));
        break;

      case 'error':
        setIsProcessing(false);
        setNarrativeLog((log) => [
          ...log,
          {
            id: Date.now(),
            kind: 'error',
            narrative: msg.message ?? msg.error ?? 'An unknown error occurred.',
            timestamp: msg.timestamp ?? new Date().toISOString(),
          },
        ]);
        break;

      case 'action_buttons_update':
        setActionButtons(Array.isArray(msg.actions) ? msg.actions : []);
        break;

      case 'party_status': {
        if (msg.player_id !== playerInfo?.playerId) {
          break;
        }
        clearTimeout(partyDebounceRef.current);
        partyDebounceRef.current = setTimeout(() => {
          setPartyStatus({
            active: !!msg.active,
            partyMembers: msg.party_members || [],
          });
          if (msg.active) {
            const names = (msg.party_members || [])
              .map((id) => connectedPlayers[id]?.name || id)
              .join(', ');
            setPartyNotice(`Party formed with ${names}`);
          } else {
            setPartyNotice('Party disbanded');
          }

          clearTimeout(partyNoticeTimerRef.current);
          partyNoticeTimerRef.current = setTimeout(() => setPartyNotice(''), 2600);
        }, 2000);
        break;
      }

      default:
        break;
    }
  }, [connectedPlayers, playerInfo?.playerId]);

  const { connected, send } = useWebSocket({
    sessionCode,
    playerId: playerInfo?.playerId,
    onMessage: handleWsMessage,
    enabled: !!playerInfo,
  });

  // ── Rejoin handler ─────────────────────────────────────────────────────────
  const handleRejoin = async () => {
    if (!rejoinUsername.trim()) { setRejoinError('Username is required'); return; }
    if (!rejoinPassword) { setRejoinError('Password is required'); return; }
    setRejoinLoading(true);
    setRejoinError('');
    try {
      const res = await fetch(`${API_URL}/api/sessions/${sessionCode}/rejoin`, {
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
      sessionStorage.setItem(STORAGE_KEY(sessionCode), JSON.stringify(info));
      setPlayerInfo(info);
    } catch (e) {
      setRejoinError(e.message);
    } finally {
      setRejoinLoading(false);
    }
  };

  // ── Input handlers ─────────────────────────────────────────────────────────
  const handleActionChange = (e) => {
    const value = e.target.value;
    setActionInput(value);
    // Debounce staging update at 300 ms
    clearTimeout(stagingTimerRef.current);
    stagingTimerRef.current = setTimeout(() => {
      send({ type: 'staging_update', draft: value });
    }, 300);
  };

  const handleSubmitAction = () => {
    const text = actionInput.trim();
    if (!text || isProcessing || !connected) return;

    if (/^strife|attack|defend|fight|abscond|flee/i.test(text)) {
      setInCombat(true);
    }

    // Show the player's action immediately in the log
    setNarrativeLog((log) => [
      ...log,
      {
        id: Date.now(),
        kind: 'action',
        playerName: playerInfo.playerName,
        playerColor: playerInfo.playerColor,
        action: text,
        timestamp: new Date().toISOString(),
      },
    ]);

    send({ type: 'player_action', action: text });
    send({ type: 'staging_update', draft: '' }); // clear your own staging
    setStagingDrafts((d) => ({ ...d, [playerInfo.playerId]: '' }));
    setActionInput('');
    setIsProcessing(true);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmitAction();
    }
  };

  const dismissBroadcast = (id) =>
    setBroadcasts((b) => b.filter((e) => e.id !== id));

  useEffect(() => {
    const onKeyDown = (evt) => {
      if (evt.key.toLowerCase() === 'p' && !evt.metaKey && !evt.ctrlKey && !evt.altKey) {
        setShowPesterlog((v) => !v);
      }
      if (evt.key.toLowerCase() === 'a' && !evt.metaKey && !evt.ctrlKey && !evt.altKey) {
        setShowAlchemy((v) => !v);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const handleCombatAction = (action) => {
    if (isProcessing || !connected) return;
    send({ type: 'player_action', action: action.toLowerCase() });
    setIsProcessing(true);
  };

  const handleContextAction = (action) => {
    if (!connected || isProcessing) return;

    if (action.action_type === 'alchemy') {
      setShowAlchemy(true);
    }

    send({
      type: 'player_action',
      action_type: action.action_type,
      target: action.target,
      label: action.label,
      action: action.label,
    });
    setNarrativeLog((log) => [
      ...log,
      {
        id: Date.now(),
        kind: 'action',
        playerName: playerInfo.playerName,
        playerColor: playerInfo.playerColor,
        action: action.label,
        timestamp: new Date().toISOString(),
      },
    ]);
    setIsProcessing(true);
  };

  // Other players' non-empty staging drafts
  const otherDrafts = Object.entries(stagingDrafts).filter(
    ([pid, text]) => pid !== playerInfo?.playerId && text
  );

  if (!playerInfo) {
    return (
      <div className="game-room">
        <div className="rejoin-overlay">
          <h2>:: RECONNECT TO SESSION ::</h2>
          <p className="rejoin-session-code">SESSION: {sessionCode}</p>
          <p className="rejoin-hint">Your session data was not found. Enter your credentials to reconnect.</p>
          <div className="form-group">
            <label>USERNAME</label>
            <input
              type="text"
              value={rejoinUsername}
              onChange={(e) => setRejoinUsername(e.target.value)}
              placeholder="Your username"
              autoComplete="username"
              autoFocus
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
          {rejoinError && <p className="error-msg">{rejoinError}</p>}
          <div className="setup-actions">
            <button onClick={() => navigate('/lobby', { replace: true })} className="btn-secondary">
              &lt; LOBBY
            </button>
            <button onClick={handleRejoin} disabled={rejoinLoading}>
              {rejoinLoading ? 'RECONNECTING...' : '[ RECONNECT ]'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`game-room ${showPesterlog ? 'pesterlog-open' : ''}`}>
      <BroadcastOverlay broadcasts={broadcasts} onDismiss={dismissBroadcast} />

      {/* HUD layer disabled for clean main branch */}
      {/* <div className="game-hud-layer">
        <div className="hud-top-left">
          <HealthBar
            current={gameState.player.hp.current}
            max={gameState.player.hp.max}
            showNumbers
          />
        </div>
        <div className="hud-top-center">
          <ExperienceBar
            currentXP={gameState.player.xp.currentXP}
            xpToNextLevel={gameState.player.xp.xpToNextLevel}
            currentRung={gameState.player.xp.currentRung}
            level={gameState.player.xp.level}
          />
        </div>
        <div className="hud-top-right">
          <GristDisplay gristCounts={gameState.player.gristCounts} />
        </div>
        <div className="hud-bottom-left">
          <EquipmentPanel
            specibus={gameState.player.equipment.specibus}
            equippedWeapon={gameState.player.equipment.equippedWeapon}
            onToggleInventory={() => setShowInventory((v) => !v)}
          />
        </div>
      </div> */}

      {/* Inventory and Alchemy panels disabled for clean main branch */}
      {/* <InventoryGrid
        visible={showInventory}
        items={gameState.player.inventory.items}
        fetchModus={gameState.player.inventory.fetchModus}
        modusRules={gameState.player.inventory.modusRules}
        onClose={() => setShowInventory(false)}
      />

      <AlchemyPanel
        isOpen={showAlchemy}
        sessionCode={sessionCode}
        playerId={playerInfo.playerId}
        inventory={gameState.player.inventory.items}
        grist={gameState.player.gristCounts}
        onClose={() => setShowAlchemy(false)}
        onCreated={(data) => {
          applyGameStatePatch({
            player: {
              gristCounts: data.gristRemaining || gameState.player.gristCounts,
              inventory: {
                ...gameState.player.inventory,
                items: data.inventory || gameState.player.inventory.items,
              },
            },
          });
        }}
      /> */}

      {/* ── Top bar ── */}
      <div className="game-topbar">
        <div className="session-info">
          <span className="session-code-badge">SESSION: {sessionCode}</span>
          <span className={`ws-indicator ${connected ? 'connected' : 'disconnected'}`}>
            {connected ? '●' : '○'}
          </span>
        </div>

        <div className="player-badges">
          {Object.values(connectedPlayers).map((p) => (
            <span
              key={p.player_id}
              className={`player-badge ${!p.connected ? 'offline' : ''}`}
              style={{ borderColor: p.color, color: p.color }}
              title={p.name}
            >
              {p.name}
            </span>
          ))}
        </div>

        <button
          className={`pesterlog-toggle ${showPesterlog ? 'active' : ''}`}
          onClick={() => setShowPesterlog((s) => !s)}
        >
          [PESTERCHUM]{pesterlogMessages.length > 0 && ` (${pesterlogMessages.length})`}
        </button>
      </div>

      {/* ── Main layout ── */}
      <div className="game-main">

        {/* ── Center: narrative + staging + input ── */}
        <div className="game-center">

          {/* Narrative log */}
          <div className="narrative-panel">
            <div className="narrative-log">
              {narrativeLog.length === 0 && (
                <div className="narrative-empty">
                  The session is active. What do you do?
                </div>
              )}

              {narrativeLog.map((entry) =>
                entry.kind === 'action' ? (
                  <div key={entry.id} className="narrative-entry">
                    <div
                      className="player-action"
                      style={{ color: entry.playerColor || 'var(--pesterchum-yellow)' }}
                    >
                      <span className="action-prefix">{entry.playerName} &gt;</span>
                      <span className="action-text"> {entry.action}</span>
                    </div>
                  </div>
                ) : entry.kind === 'error' ? (
                  <div key={entry.id} className="narrative-entry error-entry">
                    <div className="gm-error">
                      ⚠ {entry.narrative}
                    </div>
                  </div>
                ) : (
                  <div key={entry.id} className="narrative-entry gm-entry">
                    <div className="gm-narrative">
                      <ReactMarkdown>{entry.narrative}</ReactMarkdown>
                      {entry.updatesCount > 0 && (
                        <small className="updates-count">
                          [{entry.updatesCount} state update{entry.updatesCount !== 1 ? 's' : ''}]
                        </small>
                      )}
                    </div>
                  </div>
                )
              )}

              {isProcessing && !isStreamingResponse && (
                <div className="gm-thinking">
                  <span className="thinking-dots">GM is thinking</span>
                </div>
              )}

              {isStreamingResponse && (
                <div className="narrative-entry gm-entry streaming">
                  <div className="gm-narrative">
                    <ReactMarkdown>{streamingNarrative || '...'}</ReactMarkdown>
                    <span className="gm-streaming-cursor">▋</span>
                  </div>
                </div>
              )}

              <div ref={narrativeEndRef} />
            </div>
          </div>

          {/* Staging window (only when others are typing) */}
          {partyNotice && <div className="party-notice">{partyNotice}</div>}

          {partyStatus.active && otherDrafts.length > 0 && (
            <StagingWindow drafts={otherDrafts} players={connectedPlayers} />
          )}

          {/* Combat HUD and Action Buttons disabled for clean main branch */}
          {/* <CombatHUD
            inCombat={gameState.player.inCombat}
            enemies={gameState.combat.enemies}
            turnState={gameState.combat.turnState}
            availableActions={gameState.combat.availableActions}
            onActionClick={handleCombatAction}
          />

          <ActionButtons actions={actionButtons} onActionSelect={handleContextAction} /> */}

          {/* Action input */}
          <div className="action-input-bar">
            <span
              className="input-prompt"
              style={{ color: playerInfo.playerColor || 'var(--pesterchum-yellow)' }}
            >
              {playerInfo.playerName} &gt;
            </span>
            <textarea
              className="action-input"
              value={actionInput}
              onChange={handleActionChange}
              onKeyDown={handleKeyDown}
              placeholder={
                !connected
                  ? 'Connecting...'
                  : isProcessing
                  ? 'Waiting for GM response...'
                  : 'What do you do?  (Enter = submit, Shift+Enter = newline)'
              }
              disabled={!connected || isProcessing}
              rows={2}
            />
            <button
              className="submit-action-btn"
              onClick={handleSubmitAction}
              disabled={!connected || isProcessing || !actionInput.trim()}
            >
              {isProcessing ? '...' : '▶ ACT'}
            </button>
          </div>
        </div>

        {/* ── Pesterlog panel ── */}
        {showPesterlog && (
          <PesterlogChat
            messages={pesterlogMessages}
            playerInfo={playerInfo}
            onSend={(text) => send({ type: 'pesterlog_message', message: text })}
          />
        )}
      </div>
    </div>
  );
}

function GameRoom() {
  return (
    <GameStateProvider>
      <GameRoomContent />
    </GameStateProvider>
  );
}

export default GameRoom;
