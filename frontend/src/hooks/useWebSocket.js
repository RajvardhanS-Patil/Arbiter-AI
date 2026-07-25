import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * React hook to hook into the session's WebSocket real-time events.
 * Handles automatic reconnects and messages streaming.
 */
export const useWebSocket = (sessionId, onEvent) => {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    if (!sessionId) return;
    
    // Clear any previous connect timers
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    const loc = window.location;
    const protocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use target address or proxy address
    const wsUrl = `${protocol}//${loc.hostname}:${loc.port}/ws/session/${sessionId}`;

    console.log(`Connecting to WebSocket: ${wsUrl}`);
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connection opened');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (onEvent) {
          onEvent(payload);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket event payload:', err);
      }
    };

    ws.onclose = (event) => {
      console.log('WebSocket connection closed. Reconnecting...', event.reason);
      setIsConnected(false);
      
      // Auto-reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    ws.onerror = (err) => {
      console.error('WebSocket connection error:', err);
      ws.close();
    };
  }, [sessionId, onEvent]);

  useEffect(() => {
    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  const send = useCallback((message) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);

  return { isConnected, send };
};
export { }
