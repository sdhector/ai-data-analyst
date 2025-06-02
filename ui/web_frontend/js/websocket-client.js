/**
 * WebSocket Client Module
 * Handles real-time communication with the Python backend
 */

class WebSocketClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.messageQueue = [];
        this.eventHandlers = new Map();
        this.init();
    }

    init() {
        // Connect to WebSocket server
        this.connect();
    }

    connect() {
        try {
            // Determine WebSocket URL based on current location
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/ws`;

            console.log('Connecting to WebSocket:', wsUrl);
            this.socket = new WebSocket(wsUrl);

            // Setup event handlers
            this.socket.onopen = this.handleOpen.bind(this);
            this.socket.onmessage = this.handleMessage.bind(this);
            this.socket.onclose = this.handleClose.bind(this);
            this.socket.onerror = this.handleError.bind(this);

        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }

    handleOpen(event) {
        console.log('WebSocket connected');
        this.connected = true;
        this.reconnectAttempts = 0;

        // Update UI status
        if (window.chatInterface) {
            window.chatInterface.updateConnectionStatus(true);
            window.chatInterface.addSystemMessage('Connected to AI backend');
        }

        // Send any queued messages
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message);
        }

        // Send initial handshake
        this.send({
            type: 'handshake',
            data: {
                clientType: 'web',
                version: '1.0.0'
            }
        });
    }

    handleMessage(event) {
        try {
            const message = JSON.parse(event.data);
            console.log('WebSocket message received:', message);

            // Handle different message types
            switch (message.type) {
                case 'chat_response':
                    this.handleChatResponse(message.data);
                    break;

                case 'function_result':
                    this.handleFunctionResult(message.data);
                    break;

                case 'grid_update':
                    this.handleGridUpdate(message.data);
                    break;

                case 'error':
                    this.handleErrorMessage(message.data);
                    break;

                case 'system':
                    this.handleSystemMessage(message.data);
                    break;

                default:
                    console.warn('Unknown message type:', message.type);
            }

            // Trigger custom event handlers
            if (this.eventHandlers.has(message.type)) {
                const handlers = this.eventHandlers.get(message.type);
                handlers.forEach(handler => handler(message.data));
            }

        } catch (error) {
            console.error('Error handling WebSocket message:', error);
        }
    }

    handleClose(event) {
        console.log('WebSocket closed:', event.code, event.reason);
        this.connected = false;

        // Update UI status
        if (window.chatInterface) {
            window.chatInterface.updateConnectionStatus(false);
        }

        // Schedule reconnection
        if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
        }
    }

    handleError(event) {
        console.error('WebSocket error:', event);
    }

    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
        
        setTimeout(() => {
            if (!this.connected) {
                this.connect();
            }
        }, delay);
    }

    /**
     * Send message through WebSocket
     */
    send(message) {
        if (this.connected && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            // Queue message if not connected
            this.messageQueue.push(message);
            console.log('Message queued (not connected):', message);
        }
    }

    /**
     * Handle chat response from backend
     */
    handleChatResponse(data) {
        if (window.chatInterface) {
            window.chatInterface.handleAssistantResponse(data);
        }
    }

    /**
     * Handle function result from backend
     */
    handleFunctionResult(data) {
        if (data.function_name === 'add_container' && data.result?.status === 'success') {
            // Add container to grid
            const config = data.result.result;
            try {
                const containerId = window.gridManager.addContainer({
                    startRow: config.startRow || 0,
                    startCol: config.startCol || 0,
                    endRow: config.endRow || config.startRow || 0,
                    endCol: config.endCol || config.startCol || 0,
                    title: config.title || 'Container',
                    id: config.container_id
                });
                console.log('Container added:', containerId);
            } catch (error) {
                console.error('Error adding container:', error);
                if (window.chatInterface) {
                    window.chatInterface.addSystemMessage(`Error: ${error.message}`);
                }
            }
        }
    }

    /**
     * Handle grid update from backend
     */
    handleGridUpdate(data) {
        // This could be used for syncing grid state
        console.log('Grid update:', data);
    }

    /**
     * Handle error message from backend
     */
    handleErrorMessage(data) {
        console.error('Backend error:', data);
        if (window.chatInterface) {
            window.chatInterface.addSystemMessage(`Error: ${data.message || 'Unknown error'}`);
        }
    }

    /**
     * Handle system message from backend
     */
    handleSystemMessage(data) {
        if (window.chatInterface) {
            window.chatInterface.addSystemMessage(data.message);
        }
    }

    /**
     * Register event handler
     */
    on(eventType, handler) {
        if (!this.eventHandlers.has(eventType)) {
            this.eventHandlers.set(eventType, []);
        }
        this.eventHandlers.get(eventType).push(handler);
    }

    /**
     * Remove event handler
     */
    off(eventType, handler) {
        if (this.eventHandlers.has(eventType)) {
            const handlers = this.eventHandlers.get(eventType);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    /**
     * Close WebSocket connection
     */
    close() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
            this.connected = false;
        }
    }

    /**
     * Get connection status
     */
    isConnected() {
        return this.connected && this.socket && this.socket.readyState === WebSocket.OPEN;
    }
}

// Create global instance
window.websocketClient = new WebSocketClient();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketClient;
} 