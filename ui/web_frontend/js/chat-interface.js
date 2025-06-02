/**
 * Chat Interface Module
 * Handles chat UI, messages, and user interactions
 */

class ChatInterface {
    constructor() {
        this.messagesContainer = null;
        this.chatInput = null;
        this.chatForm = null;
        this.typingIndicator = null;
        this.messages = [];
        this.isTyping = false;
        this.init();
    }

    init() {
        // Get DOM elements
        this.messagesContainer = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.chatForm = document.getElementById('chatForm');
        this.typingIndicator = document.getElementById('typingIndicator');

        // Setup event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleUserMessage();
        });

        // Enter key handling
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleUserMessage();
            }
        });
    }

    /**
     * Handle user message submission
     */
    handleUserMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);

        // Clear input
        this.chatInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        // Send message to backend
        if (window.websocketClient && window.websocketClient.connected) {
            window.websocketClient.send({
                type: 'chat_message',
                message: message
            });
        } else {
            // Fallback to HTTP if WebSocket not connected
            this.sendMessageHTTP(message);
        }
    }

    /**
     * Add message to chat
     */
    addMessage(role, content, functionCalls = []) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;

        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        
        // Parse and render markdown if needed
        contentElement.innerHTML = this.parseMarkdown(content);
        
        messageElement.appendChild(contentElement);

        // Add function calls if any
        if (functionCalls.length > 0) {
            const functionsContainer = document.createElement('div');
            functionsContainer.className = 'function-calls';
            
            functionCalls.forEach(call => {
                const callElement = document.createElement('div');
                callElement.className = 'function-call';
                const icon = call.result?.status === 'success' ? '✅' : '❌';
                callElement.innerHTML = `${icon} ${call.function_name}`;
                functionsContainer.appendChild(callElement);
            });
            
            messageElement.appendChild(functionsContainer);
        }

        // Remove welcome message if it exists
        const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        // Add to container
        this.messagesContainer.appendChild(messageElement);

        // Store message
        this.messages.push({
            role,
            content,
            functionCalls,
            timestamp: new Date().toISOString()
        });

        // Scroll to bottom
        this.scrollToBottom();

        // Hide typing indicator if showing
        if (role === 'assistant') {
            this.hideTypingIndicator();
        }
    }

    /**
     * Simple markdown parser
     */
    parseMarkdown(text) {
        // Escape HTML
        text = text.replace(/&/g, '&amp;')
                   .replace(/</g, '&lt;')
                   .replace(/>/g, '&gt;')
                   .replace(/"/g, '&quot;')
                   .replace(/'/g, '&#39;');

        // Parse markdown
        text = text
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code blocks
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            // Inline code
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
            // Line breaks
            .replace(/\n/g, '<br>');

        return text;
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
    }

    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    /**
     * Send message via HTTP (fallback)
     */
    async sendMessageHTTP(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: window.conversationId || null
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Process response
            this.handleAssistantResponse(data);
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('assistant', 'Sorry, I encountered an error processing your request. Please try again.');
        }
    }

    /**
     * Handle assistant response
     */
    handleAssistantResponse(response) {
        if (response.status === 'success') {
            // Add assistant message
            this.addMessage('assistant', response.message, response.function_calls || []);

            // Process function results
            if (response.function_calls) {
                this.processFunctionResults(response.function_calls);
            }

            // Update conversation ID if provided
            if (response.conversation_id) {
                window.conversationId = response.conversation_id;
            }
        } else {
            this.addMessage('assistant', `Error: ${response.error || 'Unknown error occurred'}`);
        }
    }

    /**
     * Process function call results
     */
    processFunctionResults(functionCalls) {
        functionCalls.forEach(call => {
            if (call.result?.status === 'success') {
                // Handle specific function types
                switch (call.function_name) {
                    case 'add_container':
                        this.handleAddContainer(call.result.result);
                        break;
                    
                    case 'create_line_chart':
                    case 'create_bar_chart':
                    case 'create_scatter_plot':
                    case 'create_histogram':
                    case 'create_data_table':
                        this.handleCreateChart(call.result.result);
                        break;
                    
                    case 'remove_container':
                    case 'clear_grid':
                        // Grid manager handles these automatically
                        break;
                    
                    default:
                        console.log('Function result:', call);
                }
            }
        });
    }

    /**
     * Handle add container result
     */
    handleAddContainer(result) {
        // Container is already added by the backend response
        // We can add any additional UI updates here if needed
        console.log('Container added:', result.container_id);
    }

    /**
     * Handle create chart result
     */
    handleCreateChart(result) {
        if (result.container_id && result.chart_config) {
            // Render chart in the container
            window.chartManager.renderChart(result.container_id, result);
        }
    }

    /**
     * Clear chat history
     */
    clearChat() {
        this.messages = [];
        this.messagesContainer.innerHTML = `
            <div class="welcome-message">
                <p>👋 Welcome! I'm your AI Data Analyst.</p>
                <p>I can help you:</p>
                <ul>
                    <li>Load and analyze datasets</li>
                    <li>Create dynamic visualizations</li>
                    <li>Place charts anywhere on the grid</li>
                    <li>Customize grid layouts</li>
                </ul>
                <p>Try: "Load the sales dataset and create a bar chart in the bottom right corner"</p>
            </div>
        `;
    }

    /**
     * Export chat history
     */
    exportChatHistory() {
        const chatData = {
            messages: this.messages,
            exportedAt: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_history_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Add system message
     */
    addSystemMessage(content) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message system';
        messageElement.innerHTML = `
            <div class="message-content system-message">
                <span class="icon">ℹ️</span> ${content}
            </div>
        `;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connectionStatus');
        const statusText = document.getElementById('statusText');
        
        if (connected) {
            statusIndicator.classList.add('connected');
            statusIndicator.classList.remove('error');
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.classList.add('error');
            statusIndicator.classList.remove('connected');
            statusText.textContent = 'Disconnected';
        }
    }

    /**
     * Handle suggested actions
     */
    addSuggestedActions(actions) {
        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'suggested-actions';
        
        actions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'suggested-action';
            button.textContent = action;
            button.onclick = () => {
                this.chatInput.value = action;
                this.handleUserMessage();
            };
            actionsContainer.appendChild(button);
        });
        
        this.messagesContainer.appendChild(actionsContainer);
        this.scrollToBottom();
    }
}

// Create global instance
window.chatInterface = new ChatInterface();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatInterface;
} 