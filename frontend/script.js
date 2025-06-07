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
            executeCanvasCommand(message.command, message.data, message.command_id);
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
            
        case 'user_feedback':
            // Handle user feedback messages from backend
            handleUserFeedback(message);
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
        addMessage(response.message, 'success', { 
            source: 'assistant',
            persistent: true,
            groupId: response.request_id ? `response_${response.request_id}` : null
        });
        
        // If function calls were made, the canvas should update automatically
        if (response.function_calls_made > 0) {
            console.log(`🔧 ${response.function_calls_made} function call(s) executed`);
        }
    } else {
        addMessage(response.message, 'error', { 
            source: 'assistant',
            persistent: true 
        });
    }
}

/**
 * Get display name for message source
 */
function getSourceDisplayName(source) {
    switch (source) {
        case 'user': return 'You';
        case 'assistant': return 'Assistant';
        case 'system_frontend': return 'System';
        case 'system_backend': return 'System';
        case 'system': return 'System';
        default: return 'System';
    }
}

/**
 * Toggle message group visibility
 */
function toggleMessageGroup(groupId) {
    const groupElement = document.querySelector(`[data-group-id="${groupId}"]`);
    if (!groupElement) return;
    
    const groupContent = groupElement.querySelector('.message-group-content');
    const groupToggle = groupElement.querySelector('.group-toggle');
    
    if (groupContent.style.display === 'none') {
        groupContent.style.display = 'block';
        groupToggle.textContent = '▼';
        groupElement.classList.remove('collapsed');
    } else {
        groupContent.style.display = 'none';
        groupToggle.textContent = '▶';
        groupElement.classList.add('collapsed');
    }
}

/**
 * Handle user feedback messages from backend
 */
function handleUserFeedback(message) {
    console.log('📢 User feedback received:', message);
    
    const feedbackType = message.feedback_type;
    const operation = message.operation;
    const feedbackMessage = message.message;
    
    // Map feedback types to message types for UI
    let messageType = 'info';
    let messageOptions = {};
    
    switch (feedbackType) {
        case 'tool_start':
            messageType = 'tool_start';
            messageOptions = { 
                persistent: false,  // Start messages can be temporary
                timeout: 5000,      // Shorter timeout for start messages
                dismissible: true 
            };
            break;
        case 'tool_success':
            messageType = 'success';
            messageOptions = { 
                persistent: true,   // Success messages stay visible
                dismissible: true 
            };
            break;
        case 'tool_error':
            messageType = 'error';
            messageOptions = { 
                persistent: true,   // Error messages stay visible
                dismissible: true 
            };
            break;
        case 'tool_progress':
            messageType = 'tool_progress';
            messageOptions = { 
                persistent: false,
                timeout: 7000,      // Progress messages have medium timeout
                dismissible: true 
            };
            break;
        case 'system_info':
            messageType = 'info';
            messageOptions = { 
                persistent: false,
                timeout: 8000,
                dismissible: true 
            };
            break;
    }
    
    // Add grouping options if provided
    if (message.group_id) {
        messageOptions.groupId = message.group_id;
        messageOptions.startGroup = message.start_group || false;
        messageOptions.endGroup = message.end_group || false;
        messageOptions.source = 'system_backend';
    }
    
    // Display the feedback message to the user with appropriate persistence
    addMessage(feedbackMessage, messageType, messageOptions);
    
    // Log additional details for debugging
    if (message.details && Object.keys(message.details).length > 0) {
        console.log(`📊 ${operation} details:`, message.details);
    }
}

/**
 * Execute canvas command from backend
 */
function executeCanvasCommand(command, data, commandId = null) {
    console.log(`🎨 Executing canvas command: ${command}`, data);
    
    switch (command) {
        case 'create_container':
            createContainer(data.container_id, data.x, data.y, data.width, data.height);
            // TODO: Add acknowledgment for container creation
            break;
            
        case 'delete_container':
            deleteContainer(data.container_id);
            // TODO: Add acknowledgment for container deletion
            break;
            
        case 'modify_container':
            modifyContainer(data.container_id, data.x, data.y, data.width, data.height);
            // TODO: Add acknowledgment for container modification
            break;
            
        case 'move_container':
            moveContainer(data.container_id, data.x, data.y, commandId);
            break;
            
        case 'resize_container':
            resizeContainer(data.container_id, data.width, data.height, commandId);
            break;
            
        case 'clear_canvas':
            clearCanvas();
            // TODO: Add acknowledgment for canvas clearing
            break;
            
        case 'edit_canvas_size':
            resizeCanvas(data.width, data.height, commandId);
            break;
            
        case 'take_screenshot':
            takeScreenshot(data.filename);
            // TODO: Add acknowledgment for screenshot
            break;
            
        default:
            console.warn('⚠️ Unknown canvas command:', command);
            // Send error acknowledgment for unknown commands
            if (isConnected) {
                sendWebSocketMessage({
                    type: 'canvas_command_ack',
                    command: command,
                    status: 'error',
                    data: {
                        command_id: commandId,
                        error: `Unknown canvas command: ${command}`,
                        timestamp: new Date().toISOString()
                    },
                    message: `Unknown canvas command: ${command}`
                });
            }
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
    
    addMessage(`${message}`, 'info', { 
        source: 'user',
        persistent: true 
    });
    
    if (isConnected) {
        sendWebSocketMessage({
            type: 'chat_message',
            message: message,
            conversation_id: 'v0.1_session'
        });
    } else {
        addMessage('Not connected to backend. Please check connection.', 'error', { 
            source: 'system_frontend' 
        });
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
 * Add a message to the chat area with persistence control
 * @param {string} message - The message text
 * @param {string} type - Message type: 'info', 'success', 'error', 'warning'
 * @param {object} options - Options for message behavior
 * @param {boolean} options.persistent - If true, message won't auto-remove
 * @param {number} options.timeout - Custom timeout in milliseconds (default: 10000)
 * @param {boolean} options.dismissible - If true, adds a close button
 * @param {string} options.source - Message source: 'user', 'assistant', 'system_frontend', 'system_backend'
 * @param {string} options.groupId - Optional group ID for grouping related messages
 * @param {boolean} options.startGroup - If true, starts a new message group
 * @param {boolean} options.endGroup - If true, ends the current message group
 */
function addMessage(message, type = 'info', options = {}) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    // Default options
    const opts = {
        persistent: false,
        timeout: 10000,
        dismissible: true,
        source: 'system_frontend',
        groupId: null,
        startGroup: false,
        endGroup: false,
        ...options
    };

    // Remove welcome message if it exists and this is the first real message
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage && chatMessages.children.length === 1) {
        welcomeMessage.remove();
    }

    // Handle message grouping
    let groupElement = null;
    
    // Auto-group system messages (both frontend and backend)
    if (opts.source === 'system_frontend' || opts.source === 'system_backend' || opts.source === 'system') {
        // Use a unified system group ID, or create one if groupId is provided
        const systemGroupId = opts.groupId || 'system_messages';
        groupElement = chatMessages.querySelector(`[data-group-id="${systemGroupId}"]`);
        
        if (!groupElement) {
            // Create new system group
            groupElement = document.createElement('div');
            groupElement.className = 'message-group';
            groupElement.setAttribute('data-group-id', systemGroupId);
            
            // Create group header
            const groupHeader = document.createElement('div');
            groupHeader.className = 'message-group-header';
            groupHeader.innerHTML = `
                <span class="group-source-badge system">System</span>
                <span class="group-toggle" onclick="toggleMessageGroup('${systemGroupId}')">▼</span>
            `;
            
            // Create group content
            const groupContent = document.createElement('div');
            groupContent.className = 'message-group-content';
            
            groupElement.appendChild(groupHeader);
            groupElement.appendChild(groupContent);
            chatMessages.appendChild(groupElement);
        }
        
        // Update opts to use the unified group
        opts.groupId = systemGroupId;
    } else if (opts.groupId) {
        // Handle non-system groups (for other future use cases)
        groupElement = chatMessages.querySelector(`[data-group-id="${opts.groupId}"]`);
        
        if (!groupElement && opts.startGroup) {
            // Create new group
            groupElement = document.createElement('div');
            groupElement.className = 'message-group';
            groupElement.setAttribute('data-group-id', opts.groupId);
            
            // Create group header
            const groupHeader = document.createElement('div');
            groupHeader.className = 'message-group-header';
            groupHeader.innerHTML = `
                <span class="group-source-badge ${opts.source}">${getSourceDisplayName(opts.source)}</span>
                <span class="group-toggle" onclick="toggleMessageGroup('${opts.groupId}')">▼</span>
            `;
            
            // Create group content
            const groupContent = document.createElement('div');
            groupContent.className = 'message-group-content';
            
            groupElement.appendChild(groupHeader);
            groupElement.appendChild(groupContent);
            chatMessages.appendChild(groupElement);
        }
    }

    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    
    // Add source class
    messageElement.classList.add(`source-${opts.source}`);
    
    // Add persistent class if needed
    if (opts.persistent) {
        messageElement.classList.add('persistent');
    }
    
    // Get appropriate icon
    let icon = 'ℹ️';
    switch (type) {
        case 'success': icon = '✅'; break;
        case 'error': icon = '❌'; break;
        case 'warning': icon = '⚠️'; break;
        case 'tool_start': icon = '⚙️'; break;
        case 'tool_progress': icon = '🔄'; break;
        default: icon = 'ℹ️';
    }
    
    // Get source badge
    const sourceBadge = opts.groupId ? '' : `<span class="source-badge ${opts.source}">${getSourceDisplayName(opts.source)}</span>`;
    
    messageElement.innerHTML = `
        <div class="message-content">
            <span class="message-icon">${icon}</span>
            ${sourceBadge}
            <span class="message-text">${message}</span>
            ${opts.dismissible ? '<button class="message-close" onclick="this.parentElement.parentElement.remove()">×</button>' : ''}
        </div>
    `;
    
    // Append to group or chat messages
    if (groupElement) {
        const groupContent = groupElement.querySelector('.message-group-content');
        groupContent.appendChild(messageElement);
    } else {
        chatMessages.appendChild(messageElement);
    }
    
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Auto-remove logic with enhanced control
    const shouldAutoRemove = !opts.persistent && 
                            !message.startsWith('You:') && 
                            !message.startsWith('Assistant:') &&
                            !message.startsWith('The canvas size has been successfully');  // Keep LLM responses

    if (shouldAutoRemove) {
        setTimeout(() => {
            if (messageElement.parentElement) {
                messageElement.remove();
            }
        }, opts.timeout);
    }
    
    return messageElement;
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
 * Move a container to a new position
 */
function moveContainer(id, x, y, commandId = null) {
    const container = window.canvasState.containers.get(id);
    if (!container) {
        console.warn(`Container ${id} not found`);
        // Send error acknowledgment
        if (isConnected) {
            sendWebSocketMessage({
                type: 'canvas_command_ack',
                command: 'move_container',
                status: 'error',
                data: {
                    command_id: commandId,
                    container_id: id,
                    error: `Container ${id} not found`,
                    timestamp: new Date().toISOString()
                },
                message: `Container ${id} not found`
            });
        }
        return false;
    }
    
    // Validate bounds using current canvas size and existing container size
    const canvasWidth = window.canvasState.canvasSize.width;
    const canvasHeight = window.canvasState.canvasSize.height;
    const width = container.width;
    const height = container.height;
    
    if (x < 0 || y < 0 || x + width > canvasWidth || y + height > canvasHeight) {
        console.warn(`Container bounds exceed canvas size (${canvasWidth}x${canvasHeight})`);
        // Send error acknowledgment
        if (isConnected) {
            sendWebSocketMessage({
                type: 'canvas_command_ack',
                command: 'move_container',
                status: 'error',
                data: {
                    command_id: commandId,
                    container_id: id,
                    error: `Container bounds exceed canvas size (${canvasWidth}x${canvasHeight})`,
                    timestamp: new Date().toISOString()
                },
                message: `Container bounds exceed canvas size`
            });
        }
        return false;
    }
    
    try {
        // Store old position for acknowledgment
        const oldX = container.x;
        const oldY = container.y;
        
        // Update container position
        container.element.style.left = x + 'px';
        container.element.style.top = y + 'px';
        
        // Update stored data
        container.x = x;
        container.y = y;
        
        updateStateDisplay();
        console.log(`✅ Container ${id} moved from (${oldX}, ${oldY}) to (${x}, ${y})`);
        
        // Send success acknowledgment
        if (isConnected) {
            sendWebSocketMessage({
                type: 'canvas_command_ack',
                command: 'move_container',
                status: 'success',
                data: {
                    command_id: commandId,
                    container_id: id,
                    old_x: oldX,
                    old_y: oldY,
                    new_x: x,
                    new_y: y,
                    timestamp: new Date().toISOString()
                },
                message: `Container ${id} successfully moved to (${x}, ${y})`
            });
        }
        
        return true;
    } catch (error) {
        console.error(`❌ Failed to move container ${id}:`, error);
        // Send error acknowledgment
        if (isConnected) {
            sendWebSocketMessage({
                type: 'canvas_command_ack',
                command: 'move_container',
                status: 'error',
                data: {
                    command_id: commandId,
                    container_id: id,
                    error: error.message,
                    timestamp: new Date().toISOString()
                },
                message: `Failed to move container: ${error.message}`
            });
        }
        return false;
    }
}

/**
 * Resize a container
 */
function resizeContainer(id, width, height, commandId = null) {
    const container = window.canvasState.containers.get(id);
    if (!container) {
        console.warn(`Container ${id} not found`);
        // Send error acknowledgment
        if (isConnected) {
            sendWebSocketMessage({
                type: 'canvas_command_ack',
                command: 'resize_container',
                status: 'error',
                data: {
                    command_id: commandId,
                    container_id: id,
                    error: `Container ${id} not found`,
                    timestamp: new Date().toISOString()
                },
                message: `Container ${id} not found`
            });
        }
        return false;
    }
    
    // Validate bounds using current canvas size and container position
    const canvasWidth = window.canvasState.canvasSize.width;
    const canvasHeight = window.canvasState.canvasSize.height;
    const x = container.x;
    const y = container.y;
    
    if (width <= 0 || height <= 0) {
        console.warn(`Invalid container dimensions: ${width}x${height}`);
        // Send error acknowledgment
        if (isConnected) {
            sendWebSocketMessage({
                type: 'canvas_command_ack',
                command: 'resize_container',
                status: 'error',
                data: {
                    command_id: commandId,
                    container_id: id,
                    error: `Invalid container dimensions: ${width}x${height}`,
                    timestamp: new Date().toISOString()
                },
                message: `Invalid container dimensions`
            });
        }
        return false;
    }
    
    if (x + width > canvasWidth || y + height > canvasHeight) {
        console.warn(`Container bounds exceed canvas size (${canvasWidth}x${canvasHeight})`);
        // Send error acknowledgment
        if (isConnected) {
            sendWebSocketMessage({
                type: 'canvas_command_ack',
                command: 'resize_container',
                status: 'error',
                data: {
                    command_id: commandId,
                    container_id: id,
                    error: `Container bounds exceed canvas size (${canvasWidth}x${canvasHeight})`,
                    timestamp: new Date().toISOString()
                },
                message: `Container bounds exceed canvas size`
            });
        }
        return false;
    }
    
    try {
        // Store old dimensions for acknowledgment
        const oldWidth = container.width;
        const oldHeight = container.height;
        
        // Update container size
        container.element.style.width = width + 'px';
        container.element.style.height = height + 'px';
        
        // Update stored data
        container.width = width;
        container.height = height;
        
        updateStateDisplay();
        console.log(`✅ Container ${id} resized from ${oldWidth}x${oldHeight} to ${width}x${height}`);
        
        // Send success acknowledgment
        if (isConnected) {
            sendWebSocketMessage({
                type: 'canvas_command_ack',
                command: 'resize_container',
                status: 'success',
                data: {
                    command_id: commandId,
                    container_id: id,
                    old_width: oldWidth,
                    old_height: oldHeight,
                    new_width: width,
                    new_height: height,
                    timestamp: new Date().toISOString()
                },
                message: `Container ${id} successfully resized to ${width}x${height}`
            });
        }
        
        return true;
    } catch (error) {
        console.error(`❌ Failed to resize container ${id}:`, error);
        // Send error acknowledgment
        if (isConnected) {
            sendWebSocketMessage({
                type: 'canvas_command_ack',
                command: 'resize_container',
                status: 'error',
                data: {
                    command_id: commandId,
                    container_id: id,
                    error: error.message,
                    timestamp: new Date().toISOString()
                },
                message: `Failed to resize container: ${error.message}`
            });
        }
        return false;
    }
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
function resizeCanvas(width, height, commandId = null) {
    if (window.canvasState.canvas) {
        try {
            // Store old dimensions for verification
            const oldWidth = window.canvasState.canvasSize.width;
            const oldHeight = window.canvasState.canvasSize.height;
            
            // Update canvas element dimensions
            window.canvasState.canvas.style.width = width + 'px';
            window.canvasState.canvas.style.height = height + 'px';
            
            // Update internal state
            window.canvasState.canvasSize = { width, height };
            
            // Update state display to show new canvas size
            updateStateDisplay();
            
            console.log(`✅ Canvas resized successfully from ${oldWidth}x${oldHeight} to ${width}x${height}`);
            addMessage(`Canvas resized to ${width}x${height} pixels`, 'success', { 
                persistent: true,  // Canvas operations should be persistent
                dismissible: true,
                source: 'system_frontend'
            });
            
            // Send acknowledgment back to backend
            if (isConnected) {
                sendWebSocketMessage({
                    type: 'canvas_command_ack',
                    command: 'edit_canvas_size',
                    status: 'success',
                    data: {
                        requested_width: width,
                        requested_height: height,
                        actual_width: window.canvasState.canvasSize.width,
                        actual_height: window.canvasState.canvasSize.height,
                        old_width: oldWidth,
                        old_height: oldHeight,
                        command_id: commandId,
                        timestamp: new Date().toISOString()
                    },
                    message: `Canvas successfully resized to ${width}x${height}`
                });
                console.log('📤 Canvas resize acknowledgment sent to backend');
            }
            
            return true;
        } catch (error) {
            console.error('❌ Failed to resize canvas:', error);
            addMessage(`Failed to resize canvas: ${error.message}`, 'error');
            
            // Send failure acknowledgment
            if (isConnected) {
                sendWebSocketMessage({
                    type: 'canvas_command_ack',
                    command: 'edit_canvas_size',
                    status: 'error',
                    data: {
                        requested_width: width,
                        requested_height: height,
                        command_id: commandId,
                        error: error.message,
                        timestamp: new Date().toISOString()
                    },
                    message: `Failed to resize canvas: ${error.message}`
                });
            }
            
            return false;
        }
    }
    
    console.error('❌ Canvas element not found');
    addMessage('Canvas element not found', 'error');
    
    // Send failure acknowledgment
    if (isConnected) {
        sendWebSocketMessage({
            type: 'canvas_command_ack',
            command: 'edit_canvas_size',
            status: 'error',
            data: {
                requested_width: width,
                requested_height: height,
                command_id: commandId,
                error: 'Canvas element not found',
                timestamp: new Date().toISOString()
            },
            message: 'Canvas element not found'
        });
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
/**
 * Clear temporary messages (non-persistent ones)
 */
function clearTemporaryMessages() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messages = chatMessages.querySelectorAll('.message:not(.persistent)');
    messages.forEach(message => {
        if (!message.querySelector('.message-text').textContent.startsWith('You:') &&
            !message.querySelector('.message-text').textContent.startsWith('Assistant:')) {
            message.remove();
        }
    });
}

/**
 * Clear all messages
 */
function clearAllMessages() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach(message => message.remove());
}

window.canvasAPI = {
    getState,
    createContainer,
    deleteContainer,
    modifyContainer,
    clearCanvas,
    resizeCanvas,
    takeScreenshot,
    sendChatMessage,
    // Message utilities
    clearTemporaryMessages,
    clearAllMessages,
    addMessage  // Allow manual message creation
};

// Expose test functions
window.testCreateContainer = testCreateContainer;
window.testDeleteContainer = testDeleteContainer;
window.testModifyContainer = testModifyContainer;
window.testGetState = testGetState;
window.createTestDashboard = createTestDashboard;
window.runDemo = runDemo;