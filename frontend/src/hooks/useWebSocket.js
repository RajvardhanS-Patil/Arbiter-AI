import { useEffect, useRef, useState } from 'react';

/**
 * React hook for session WebSocket real-time events.
 * Fixed: stable refs to prevent infinite reconnection loops.
 */
export const useWebSocket = (sessionId, onEvent) => {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const onEventRef = useRef(onEvent);

  // Keep the callback ref up to date without causing reconnects
  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    if (!sessionId) return;

    let isCancelled = false;

    const connect = () => {
      if (isCancelled) return;

      // Clear any previous reconnect timer
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      // Use Vite proxy: connect through the same origin (port 5173)
      // Vite proxies /ws/* to ws://localhost:8000
      const loc = window.location;
      const protocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${loc.host}/ws/session/${sessionId}`;

      console.log(`[WS] Connecting to: ${wsUrl}`);
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        if (isCancelled) { ws.close(); return; }
        console.log('[WS] Connected');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (onEventRef.current) {
            onEventRef.current(payload);
          }
        } catch (err) {
          console.error('[WS] Failed to parse event:', err);
        }
      };

      ws.onclose = (event) => {
        if (isCancelled) return;
        console.log('[WS] Closed. Reconnecting in 5s...', event.reason);
        setIsConnected(false);
        reconnectTimeoutRef.current = setTimeout(connect, 5000);
      };

      ws.onerror = (err) => {
        console.error('[WS] Error:', err);
        ws.close();
      };
    };

    connect();

    return () => {
      isCancelled = true;
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, [sessionId]); // Only reconnect when sessionId changes

  const send = (message) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, send };
};
