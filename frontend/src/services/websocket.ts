type MessageHandler = (data: any) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private messageHandlers: Set<MessageHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private draftId: string | null = null;

  connect(draftId: string) {
    console.log(`[WS] Attempting to connect to draft: ${draftId}`);

    // Check if already connected to the same draft
    if (this.ws?.readyState === WebSocket.OPEN && this.draftId === draftId) {
      console.log('[WS] Already connected to this draft, skipping reconnection');
      return;
    }

    // Check if connecting
    if (this.ws?.readyState === WebSocket.CONNECTING && this.draftId === draftId) {
      console.log('[WS] Already connecting to this draft, skipping');
      return;
    }

    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('[WS] Closing existing connection before new connection');
      this.disconnect();
    }

    this.draftId = draftId;
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    const fullUrl = `${wsUrl}/ws/${draftId}`;
    console.log(`[WS] Creating new WebSocket connection to: ${fullUrl}`);

    this.ws = new WebSocket(fullUrl);

    this.ws.onopen = () => {
      console.log(`[WS] Connected successfully to draft: ${draftId}`);
      console.log(`[WS] WebSocket readyState: ${this.ws?.readyState}`);
      this.reconnectAttempts = 0;

      // Send a ping message to test the connection
      console.log('[WS] Sending initial ping message');
      this.send({ type: 'ping', draftId });
    };

    this.ws.onmessage = (event) => {
      console.log(`[WS] Message received: ${event.data}`);
      try {
        const data = JSON.parse(event.data);
        this.messageHandlers.forEach(handler => handler(data));
      } catch (error) {
        console.error('[WS] Failed to parse WebSocket message:', error);
        console.error('[WS] Raw message data:', event.data);
      }
    };

    this.ws.onclose = (event) => {
      console.log(`[WS] Disconnected - Code: ${event.code}, Reason: ${event.reason}`);
      console.log(`[WS] Was clean close: ${event.wasClean}`);
      console.log(`[WS] Close event details:`, {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        type: event.type,
        timeStamp: event.timeStamp
      });

      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('[WS] WebSocket error:', error);
      // Log more details about the error
      if (error instanceof Event) {
        const target = error.target as WebSocket;
        console.error(`[WS] Error details - readyState: ${target.readyState}, url: ${target.url}`);
      }
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.draftId) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * this.reconnectAttempts;
      console.log(`[WS] Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      console.log(`[WS] Reconnecting in ${delay}ms`);
      console.log(`[WS] Current WebSocket state:`, {
        readyState: this.ws?.readyState,
        url: this.ws?.url,
        draftId: this.draftId
      });
      setTimeout(() => {
        this.connect(this.draftId!);
      }, delay);
    } else {
      console.log(`[WS] Max reconnection attempts reached or no draftId. Giving up.`);
      console.log(`[WS] Final state:`, {
        reconnectAttempts: this.reconnectAttempts,
        maxReconnectAttempts: this.maxReconnectAttempts,
        draftId: this.draftId
      });
    }
  }

  disconnect() {
    console.log('[WS] Disconnect called');
    if (this.ws) {
      console.log(`[WS] Closing WebSocket connection (readyState: ${this.ws.readyState})`);

      // Only close if not already closed/closing
      if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close(1000, 'Client disconnect');
      }

      this.ws = null;
      this.draftId = null;
      this.reconnectAttempts = 0;
    } else {
      console.log('[WS] No WebSocket connection to close');
    }
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message = JSON.stringify(data);
      console.log(`[WS] Sending message: ${message}`);
      this.ws.send(message);
    } else {
      console.error(`[WS] Cannot send - WebSocket not connected (readyState: ${this.ws?.readyState})`);
    }
  }

  addMessageHandler(handler: MessageHandler) {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  isConnected() {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

export const wsService = new WebSocketService();
