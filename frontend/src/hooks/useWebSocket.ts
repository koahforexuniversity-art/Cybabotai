/**
 * WebSocket hook for real-time agent streaming.
 * Manages connection lifecycle and message handling.
 */

import { useEffect, useRef, useCallback, useState } from "react";

export type AgentStreamMessage = {
  type:
    | "agent_start"
    | "agent_progress"
    | "agent_complete"
    | "agent_error"
    | "crew_complete"
    | "crew_error";
  agent_id: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  message: string;
  data?: {
    equity_point?: { x: number; y: number };
    radar_data?: Record<string, number>;
    metrics?: Record<string, number>;
    exports?: Record<string, string>;
    progress?: number;
    error?: string;
  };
};

type WebSocketStatus = "disconnected" | "connecting" | "connected" | "error";

interface UseWebSocketOptions {
  strategyId: string | null;
  token: string | null;
  onMessage?: (message: AgentStreamMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export function useWebSocket({
  strategyId,
  token,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
}: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<WebSocketStatus>("disconnected");
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!strategyId || !token) return;

    const wsUrl = process.env.NEXT_PUBLIC_BACKEND_WS_URL || "ws://localhost:8000";
    const url = `${wsUrl}/ws/${strategyId}?token=${token}`;

    setStatus("connecting");

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus("connected");
      onConnect?.();

      // Start ping interval to keep connection alive
      pingIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as AgentStreamMessage;
        if (message.type !== ("pong" as AgentStreamMessage["type"])) {
          onMessage?.(message);
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };

    ws.onclose = () => {
      setStatus("disconnected");
      onDisconnect?.();

      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };

    ws.onerror = (error) => {
      setStatus("error");
      onError?.(error);
    };
  }, [strategyId, token, onMessage, onConnect, onDisconnect, onError]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus("disconnected");
  }, []);

  useEffect(() => {
    if (strategyId && token) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [strategyId, token, connect, disconnect]);

  return { status, connect, disconnect };
}
