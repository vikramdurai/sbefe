import { useEffect, useRef, useState, useCallback } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE = API_URL.replace(/^http/, 'ws');

/**
 * useWebSocket - manages a WebSocket connection for a session player.
 *
 * @param {object} opts
 * @param {string}   opts.sessionCode  - 6-char session code
 * @param {string}   opts.playerId     - player UUID slice
 * @param {function} opts.onMessage    - callback(parsedData) for incoming messages
 * @param {boolean}  [opts.enabled]    - whether to connect (default true)
 * @returns {{ connected: boolean, send: function }}
 */
export function useWebSocket({ sessionCode, playerId, onMessage, enabled = true }) {
  const wsRef = useRef(null);
  const [connected, setConnected] = useState(false);

  // Keep the callback ref fresh so the effect doesn't need to re-run when it changes
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!enabled || !sessionCode || !playerId) return;

    const url = `${WS_BASE}/ws/${sessionCode}/${playerId}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessageRef.current?.(data);
      } catch (e) {
        console.error('[WS] parse error:', e);
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
      setConnected(false);
    };
  }, [sessionCode, playerId, enabled]);

  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { connected, send };
}
