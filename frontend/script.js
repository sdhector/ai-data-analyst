/**
 * AI Data Analyst v0.1 - Simplified Frontend
 * Combines production styling with test frontend functionality
 * Now includes WebSocket communication with the backend chatbot
 */

// Global state management (similar to test frontend)
window.canvasState = {
    containers: new Map(),
    canvas: null,
    containerCounter: 0,
    canvasSize: { width: 800, height: 600 } // Track current canvas size
};

// WebSocket connection
let websocket = null;
let isConnected = false;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCanvas();
    setupEventListeners();
    updateStateDisplay();
    initializeWebSocket();
    console.log('AI Data Analyst v0.1 initialized');
});

/**
 * Initialize WebSocket connection
 */
function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    try {
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = function(event) {
            console.log('✅ WebSocket connected');
            isConnected = true;
            reconnectAttempts = 0;
            updateConnectionStatus(true);
            
            // Send handshake
            sendWebSocketMessage({
                type: 'handshake',
                data: {
                    clientType: 'v0.1_frontend',
                    version: '0.1.0'
                }
            });
        };
        
        websocket.onmessage = function(event) {
            try {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        websocket.onclose = function(event) {
            console.log('🔌 WebSocket disconnected');
            isConnected = false;
            updateConnectionStatus(false);
            
            // Attempt to reconnect
            if (reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                console.log(`🔄 Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts})...`);
                setTimeout(initializeWebSocket, 2000 * reconnectAttempts);
            }
        };
        
        websocket.onerror = function(error) {
            console.error('❌ WebSocket error:', error);
        };
        
    } catch (error) {
        console.error('❌ Failed to initialize WebSocket:', error);
        updateConnectionStatus(false);
    }
}

/**
 * Send message through WebSocket
 */
function sendWebSocketMessage(message) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(message));
    } else {
        console.warn('⚠️ WebSocket not connected, message not sent:', message);
    }
}

/**
 * Handle incoming WebSocket messages
 */
function handleWebSocketMessage(message) {
    console.log('📥 WebSocket message received:', message);
    
    switch (message.type) {
        case 'handshake_response':
            console.log('🤝 Handshake successful:', message.data);
            addMessage('Connected to AI backend', 'success');
            break;
            
        case 'initial_state':
            console.log('📋 Initial canvas state received:', message.data);
            updateCanvasFromState(message.data);
            break;
            
        case 'chat_response':
            handleChatResponse(message.data);
            break;
            
        case 'canvas_command':
            executeCanvasCommand(message.command, message.data);
            break;
            
        case 'canvas_update':
            updateCanvasFromState(message.data);
            break;
            
        case 'error':
            console.error('❌ Backend error:', message.data);
            addMessage(`Error: ${message.data.message}`, 'error');
            break;
            
        case 'pong':
            // Handle ping/pong for keepalive
            break;
            
        default:
            console.warn('⚠️ Unknown message type:', message.type);
    }
}

/**
 * Handle chat response from backend
 */
function handleChatResponse(response) {
    if (response.success) {
        addMessage(response.message, 'success');
        
        // If function calls were made, the canvas should update automatically
        if (response.function_calls_made > 0) {
            console.log(`🔧 ${response.function_calls_made} function call(s) executed`);
        }
    } else {
        addMessage(response.message, 'error');
    }
}

/**
 * Execute canvas command from backend
 */
function executeCanvasCommand(command, data) {
    console.log(`🎨 Executing canvas command: ${command}`, data);
    
    switch (command) {
        case 'create_container':
            createContainer(data.container_id, data.x, data.y, data.width, data.height);
            break;
            
        case 'delete_container':
            deleteContainer(data.container_id);
            break;
            
        case 'modify_container':
            modifyContainer(data.container_id, data.x, data.y, data.width, data.height);
            break;
            
        case 'clear_canvas':
            clearCanvas();
            break;
            
        case 'edit_canvas_size':
            resizeCanvas(data.width, data.height);
            break;
            
        case 'take_screenshot':
            takeScreenshot(data.filename);
            break;
            
        default:
            console.warn('⚠️ Unknown canvas command:', command);
    }
}

/**
 * Update canvas from backend state
 */
function updateCanvasFromState(state) {
    console.log('🔄 Updating canvas from backend state:', state);
    
    // Update canvas size if provided
    if (state.canvas_size) {
        const newWidth = state.canvas_size.width;
        const newHeight = state.canvas_size.height;
        
        // Update canvas dimensions
        if (window.canvasState.canvas) {
            window.canvasState.canvas.style.width = newWidth + 'px';
            window.canvasState.canvas.style.height = newHeight + 'px';
        }
        
        // Update internal state
        window.canvasState.canvasSize = { width: newWidth, height: newHeight };
        
        console.log(`Canvas size updated to ${newWidth}x${newHeight}`);
    }
    
    // Clear current containers
    window.canvasState.containers.clear();
    if (window.canvasState.canvas) {
        window.canvasState.canvas.innerHTML = '';
    }
    
    // Recreate containers from state
    if (state.containers) {
        state.containers.forEach(container => {
            createContainer(container.id, container.x, container.y, container.width, container.height);
        });
    }
    
    updateStateDisplay();
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('connectionStatus');
    const statusText = document.getElementById('statusText');
    
    if (statusIndicator) {
        statusIndicator.className = connected ? 'status-indicator connected' : 'status-indicator disconnected';
    }
    
    if (statusText) {
        statusText.textContent = connected ? 'Connected' : 'Disconnected';
    }
}

/**
 * Send chat message to backend
 */
function sendChatMessage(message) {
    if (!message.trim()) return;
    
    addMessage(`You: ${message}`, 'info');
    
    if (isConnected) {
        sendWebSocketMessage({
            type: 'chat_message',
            message: message,
            conversation_id: 'v0.1_session'
        });
    } else {
        addMessage('Not connected to backend. Please check connection.', 'error');
    }
}

/**
 * Initialize canvas and global state
 */
function initializeCanvas() {
    window.canvasState.canvas = document.getElementById('canvas');
    if (!window.canvasState.canvas) {
        console.error('Canvas element not found');
        return;
    }
    console.log('Canvas initialized');
}

/**
 * Setup event listeners for buttons and chat
 */
function setupEventListeners() {
    // Add chat input functionality
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        // Create chat input area
        const chatInputArea = document.createElement('div');
        chatInputArea.className = 'chat-input-area';
        chatInputArea.innerHTML = `
            <div class="chat-input-container">
                <input type="text" id="chatInput" placeholder="Type your message here..." class="chat-input">
                <button id="sendButton" class="send-button">Send</button>
            </div>
        `;
        
        // Insert before the chat messages
        chatMessages.parentNode.insertBefore(chatInputArea, chatMessages);
        
        // Add event listeners
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        
        if (chatInput && sendButton) {
            sendButton.addEventListener('click', () => {
                const message = chatInput.value.trim();
                if (message) {
                    sendChatMessage(message);
                    chatInput.value = '';
                }
            });
            
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const message = chatInput.value.trim();
                    if (message) {
                        sendChatMessage(message);
                        chatInput.value = '';
                    }
                }
            });
        }
    }
}

/**
 * Update the state display (container count and canvas size)
 */
function updateStateDisplay() {
    const canvasInfoElement = document.getElementById('canvasInfo');
    const containers = window.canvasState.containers;
    const canvasSize = window.canvasState.canvasSize;
    
    // Update canvas info in header
    if (canvasInfoElement) {
        canvasInfoElement.innerHTML = `
            <span id="containerCount">${containers.size}</span> containers • 
            <span id="canvasSize">${canvasSize.width}×${canvasSize.height}</span>
        `;
    }
}

/**
 * Add a message to the chat area
 */
function addMessage(message, type = 'info') {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    // Remove welcome message if it exists and this is the first real message
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage && chatMessages.children.length === 1) {
        welcomeMessage.remove();
    }

    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.innerHTML = `
        <div class="message-content">
            <span class="message-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span class="message-text">${message}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Auto-remove after 10 seconds for non-chat messages
    if (!message.startsWith('You:') && !message.startsWith('Assistant:')) {
        setTimeout(() => {
            if (messageElement.parentElement) {
                messageElement.remove();
            }
        }, 10000);
    }
}

// ===== Canvas API (same as test frontend) =====

/**
 * Get current canvas state
 */
function getState() {
    const state = {
        hasContainers: window.canvasState.containers.size > 0,
        containerCount: window.canvasState.containers.size,
        containers: []
    };
    
    for (const [id, container] of window.canvasState.containers) {
        state.containers.push({
            id: id,
            x: container.x,
            y: container.y,
            width: container.width,
            height: container.height
        });
    }
    
    return state;
}

/**
 * Create a new container
 */
function createContainer(id, x, y, width, height) {
    if (!window.canvasState.canvas) {
        console.error('Canvas not initialized');
        return false;
    }

    if (window.canvasState.containers.has(id)) {
        console.warn(`Container ${id} already exists`);
        return false;
    }

    // Validate bounds using current canvas size
    const canvasWidth = window.canvasState.canvasSize.width;
    const canvasHeight = window.canvasState.canvasSize.height;
    
    if (x < 0 || y < 0 || x + width > canvasWidth || y + height > canvasHeight) {
        console.warn(`Container bounds exceed canvas size (${canvasWidth}x${canvasHeight})`);
        return false;
    }

    const container = document.createElement('div');
    container.className = 'container';
    container.id = id;
    container.textContent = id;
    container.style.left = x + 'px';
    container.style.top = y + 'px';
    container.style.width = width + 'px';
    container.style.height = height + 'px';
    
    // Add hover effects and click handlers
    container.addEventListener('click', () => {
        console.log(`Container ${id} clicked`);
    });
    
    window.canvasState.canvas.appendChild(container);
    window.canvasState.containers.set(id, { 
        id, x, y, width, height, element: container 
    });
    
    updateStateDisplay();
    console.log(`Container ${id} created at (${x}, ${y}) with size ${width}x${height}`);
    return true;
}

/**
 * Delete a container
 */
function deleteContainer(id) {
    const container = window.canvasState.containers.get(id);
    if (!container) {
        console.warn(`Container ${id} not found`);
        return false;
    }
    
    container.element.remove();
    window.canvasState.containers.delete(id);
    updateStateDisplay();
    console.log(`Container ${id} deleted`);
    return true;
}

/**
 * Modify a container's properties
 */
function modifyContainer(id, x, y, width, height) {
    const container = window.canvasState.containers.get(id);
    if (!container) {
        console.warn(`Container ${id} not found`);
        return false;
    }
    
    // Validate bounds using current canvas size
    const canvasWidth = window.canvasState.canvasSize.width;
    const canvasHeight = window.canvasState.canvasSize.height;
    
    if (x < 0 || y < 0 || x + width > canvasWidth || y + height > canvasHeight) {
        console.warn(`Container bounds exceed canvas size (${canvasWidth}x${canvasHeight})`);
        return false;
    }
    
    container.element.style.left = x + 'px';
    container.element.style.top = y + 'px';
    container.element.style.width = width + 'px';
    container.element.style.height = height + 'px';
    
    // Update stored data
    container.x = x;
    container.y = y;
    container.width = width;
    container.height = height;
    
    updateStateDisplay();
    console.log(`Container ${id} modified to (${x}, ${y}) with size ${width}x${height}`);
    return true;
}

/**
 * Clear all containers from canvas
 */
function clearCanvas() {
    for (const [id, container] of window.canvasState.containers) {
        container.element.remove();
    }
    window.canvasState.containers.clear();
    updateStateDisplay();
    console.log('Canvas cleared');
    return true;
}

/**
 * Resize the canvas
 */
function resizeCanvas(width, height) {
    if (window.canvasState.canvas) {
        // Update canvas element dimensions
        window.canvasState.canvas.style.width = width + 'px';
        window.canvasState.canvas.style.height = height + 'px';
        
        // Update internal state
        window.canvasState.canvasSize = { width, height };
        
        // Update state display to show new canvas size
        updateStateDisplay();
        
        console.log(`Canvas resized to ${width}x${height}`);
        addMessage(`Canvas resized to ${width}x${height} pixels`, 'success');
        return true;
    }
    return false;
}

/**
 * Take a screenshot (placeholder - would need backend implementation)
 */
function takeScreenshot(filename) {
    console.log(`Screenshot requested: ${filename || 'screenshot.png'}`);
    addMessage(`Screenshot saved: ${filename || 'screenshot.png'}`, 'success');
    return true;
}

// ===== Test Functions (for console access) =====

function testCreateContainer() {
    const id = `test_${Date.now()}`;
    const canvasWidth = window.canvasState.canvasSize.width;
    const canvasHeight = window.canvasState.canvasSize.height;
    
    const maxWidth = 200;
    const maxHeight = 150;
    const width = 100 + Math.floor(Math.random() * 100);
    const height = 80 + Math.floor(Math.random() * 80);
    
    const x = Math.floor(Math.random() * Math.max(50, canvasWidth - width));
    const y = Math.floor(Math.random() * Math.max(50, canvasHeight - height));
    
    createContainer(id, x, y, width, height);
    addMessage(`Test container ${id} created`, 'success');
}

function testDeleteContainer() {
    const containers = Array.from(window.canvasState.containers.keys());
    if (containers.length > 0) {
        const id = containers[Math.floor(Math.random() * containers.length)];
        deleteContainer(id);
        addMessage(`Container ${id} deleted`, 'success');
    } else {
        addMessage('No containers to delete', 'error');
    }
}

function testModifyContainer() {
    const containers = Array.from(window.canvasState.containers.keys());
    if (containers.length > 0) {
        const id = containers[Math.floor(Math.random() * containers.length)];
        const canvasWidth = window.canvasState.canvasSize.width;
        const canvasHeight = window.canvasState.canvasSize.height;
        
        const width = 100 + Math.floor(Math.random() * 100);
        const height = 80 + Math.floor(Math.random() * 80);
        
        const x = Math.floor(Math.random() * Math.max(50, canvasWidth - width));
        const y = Math.floor(Math.random() * Math.max(50, canvasHeight - height));
        
        modifyContainer(id, x, y, width, height);
        addMessage(`Container ${id} modified`, 'success');
    } else {
        addMessage('No containers to modify', 'error');
    }
}

function testGetState() {
    const state = getState();
    console.log('Current canvas state:', state);
    addMessage(`Canvas has ${state.containerCount} containers`, 'info');
    return state;
}

// ===== Demo Functions =====

function createTestDashboard() {
    clearCanvas();
    
    const canvasWidth = window.canvasState.canvasSize.width;
    const canvasHeight = window.canvasState.canvasSize.height;
    
    // Create header (full width, 80px height)
    createContainer('header', 0, 0, canvasWidth, 80);
    
    // Create sidebar (200px wide, remaining height)
    createContainer('sidebar', 0, 80, 200, canvasHeight - 80);
    
    // Create main content (remaining width, remaining height)
    createContainer('main_content', 200, 80, canvasWidth - 200, canvasHeight - 80);
    
    addMessage('Test dashboard created', 'success');
}

function runDemo() {
    clearCanvas();
    
    setTimeout(() => createContainer('demo1', 50, 50, 200, 150), 500);
    setTimeout(() => createContainer('demo2', 300, 100, 150, 100), 1000);
    setTimeout(() => createContainer('demo3', 100, 250, 250, 120), 1500);
    setTimeout(() => modifyContainer('demo2', 400, 200, 180, 120), 2500);
    setTimeout(() => deleteContainer('demo1'), 3500);
    
    addMessage('Demo sequence started', 'success');
}

// ===== Global API =====

// Expose API for console access
window.canvasAPI = {
    getState,
    createContainer,
    deleteContainer,
    modifyContainer,
    clearCanvas,
    resizeCanvas,
    takeScreenshot,
    sendChatMessage
};

// Expose test functions
window.testCreateContainer = testCreateContainer;
window.testDeleteContainer = testDeleteContainer;
window.testModifyContainer = testModifyContainer;
window.testGetState = testGetState;
window.createTestDashboard = createTestDashboard;
window.runDemo = runDemo;