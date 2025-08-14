'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

export interface WebSocketMessage {
  action: string;
  topic?: string;
  roles?: {
    combatant_a: string;
    combatant_b: string;
    judge: string;
  };
  message?: string;
  agent_id?: string;
  round?: number;
  phase?: string;
  token?: string;
  metrics?: {
    tokens_per_second?: number;
    total_tokens?: number;
    time_elapsed?: number;
  };
}

export interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WebSocketMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export const useWebSocket = (options: UseWebSocketOptions) => {
  const {
    url,
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectAttempts = 5,
    reconnectDelay = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isConnectingRef = useRef(false);
  const optionsRef = useRef(options);
  
  // Update options ref when they change
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  const connect = useCallback(() => {
    // Check if already connected or connecting
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    // Prevent multiple connection attempts
    if (isConnectingRef.current) {
      return;
    }

    isConnectingRef.current = true;
    setIsConnecting(true);
    setError(null);

    const { url, onMessage, onOpen, onClose, onError, reconnectAttempts, reconnectDelay } = optionsRef.current;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setIsConnecting(false);
        isConnectingRef.current = false;
        setError(null);
        reconnectCountRef.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage?.(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setIsConnecting(false);
        isConnectingRef.current = false;
        wsRef.current = null;
        onClose?.();

        // Auto-reconnect logic - temporarily disabled to fix infinite loop
        // if (reconnectCountRef.current < (reconnectAttempts || 5)) {
        //   reconnectCountRef.current++;
        //   console.log(`Reconnecting... (${reconnectCountRef.current}/${reconnectAttempts || 5})`);
        //   
        //   reconnectTimeoutRef.current = setTimeout(() => {
        //     connect();
        //   }, reconnectDelay || 3000);
        // } else {
        //   setError('Maximum reconnection attempts reached');
        // }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error occurred');
        const errorMsg = `WebSocket connection failed. Please ensure the backend is running on ${url}`;
        setError(errorMsg);
        setIsConnecting(false);
        isConnectingRef.current = false;
        onError?.(event);
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError('Failed to create WebSocket connection');
      setIsConnecting(false);
      isConnectingRef.current = false;
    }
  }, []); // Remove dependencies to prevent recreation

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setIsConnecting(false);
    reconnectCountRef.current = 0;
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
      setError('Cannot send message: WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, []); // Empty dependency array - only run on mount/unmount

  return {
    isConnected,
    isConnecting,
    error,
    sendMessage,
    connect,
    disconnect,
  };
};