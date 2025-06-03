# LLM Canvas Chatbot

## 🎯 Overview

The LLM Canvas Chatbot is a terminal-based interface that uses OpenAI's GPT models to control the canvas through natural language commands. It follows the same architecture pattern as the core AI engine modules and provides an intelligent way to manage containers on the visual canvas.

## 🏗️ Architecture

The chatbot follows a modular architecture similar to the core AI engine:

```
CanvasChatbot
├── CanvasLLMClient          # OpenAI API integration
├── CanvasFunctionExecutor   # Function call execution
└── CanvasController         # Browser automation
```

### Components

- **CanvasLLMClient**: Handles OpenAI API communication with canvas-specific function schemas
- **CanvasFunctionExecutor**: Bridges LLM function calls to canvas controller operations
- **CanvasChatbot**: Main orchestrator managing conversation flow and function calling

## 🚀 Setup

### Prerequisites

1. **Python Dependencies**: Install required packages
   ```bash
   pip install openai python-dotenv selenium webdriver-manager
   ```

2. **OpenAI API Key**: Set your API key in environment variables
   ```bash
   # In .env file
   OPENAI_API_KEY=your_api_key_here
   
   # Or export directly
   export OPENAI_API_KEY=your_api_key_here
   ```

3. **Chrome Browser**: Ensure Chrome is installed for Selenium automation

### Running the Chatbot

```bash
cd tests/python
python llm_canvas_chatbot.py
```

## 🎨 Available Functions

The LLM has access to the following canvas operations:

### Container Management
- **create_container**: Create new containers with specified position and size
- **delete_container**: Remove containers by ID
- **modify_container**: Change container position and size
- **clear_canvas**: Remove all containers

### Canvas Operations
- **get_canvas_state**: View current canvas state and all containers
- **get_canvas_size**: Get current canvas dimensions
- **edit_canvas_size**: Resize the canvas
- **take_screenshot**: Capture canvas state as image

## 💬 Usage Examples

### Basic Container Operations

```
You: Create a container called 'header' at position 100,50 with size 600x100
Assistant: I'll create a container called 'header' at the specified position and size.

🔧 EXECUTING: create_container({'container_id': 'header', 'x': 100, 'y': 50, 'width': 600, 'height': 100})
✅ Container 'header' created at (100, 50) with size 600x100

Perfect! I've successfully created a container named 'header' at position (100, 50) with dimensions 600x100 pixels. The container is now visible on your canvas and ready for content.

You: Show me what's on the canvas right now
Assistant: Let me check the current state of your canvas.

🔧 EXECUTING: get_canvas_state({})
📊 Canvas State:
   - Has containers: True
   - Container count: 1
   - Containers:
     * header: pos(100, 50) size(600x100)

Your canvas currently has 1 container:
- **header**: Located at position (100, 50) with size 600×100 pixels

The canvas is active and ready for more containers or modifications!

You: Delete the header container
Assistant: I'll remove the 'header' container from the canvas.

🔧 EXECUTING: delete_container({'container_id': 'header'})
✅ Container 'header' deleted successfully

The 'header' container has been successfully removed from the canvas. Your canvas is now empty and ready for new containers.
```

### Natural Language Commands

The chatbot understands natural language and can interpret various ways of expressing the same request:

```
You: Put a small container in the top left corner
Assistant: I'll create a small container in the top left corner of the canvas.

🔧 EXECUTING: create_container({'container_id': 'top_left_container', 'x': 20, 'y': 20, 'width': 150, 'height': 100})

You: Make a large container in the center
Assistant: I'll create a large container positioned in the center of the canvas.

🔧 EXECUTING: get_canvas_size({})
🔧 EXECUTING: create_container({'container_id': 'center_container', 'x': 275, 'y': 200, 'width': 250, 'height': 200})

You: Create three containers side by side
Assistant: I'll create three containers arranged horizontally side by side.

🔧 EXECUTING: create_container({'container_id': 'left_container', 'x': 50, 'y': 100, 'width': 200, 'height': 150})
🔧 EXECUTING: create_container({'container_id': 'middle_container', 'x': 270, 'y': 100, 'width': 200, 'height': 150})
🔧 EXECUTING: create_container({'container_id': 'right_container', 'x': 490, 'y': 100, 'width': 200, 'height': 150})
```

### Canvas Management

```
You: What's the current canvas size?
Assistant: Let me check the current canvas dimensions for you.

🔧 EXECUTING: get_canvas_size({})
The current canvas size is 800×600 pixels.

You: Resize the canvas to 1200x800
Assistant: I'll resize the canvas to 1200×800 pixels.

🔧 EXECUTING: edit_canvas_size({'width': 1200, 'height': 800})
✅ Canvas resized to 1200x800 pixels

You: Take a screenshot and save it as 'my_layout.png'
Assistant: I'll capture the current canvas state and save it as 'my_layout.png'.

🔧 EXECUTING: take_screenshot({'filename': 'my_layout.png'})
📸 Screenshot saved: /path/to/tests/python/screenshots/my_layout.png
```

## 🔧 Features

### Intelligent Function Calling
- **Multi-step Operations**: LLM can chain multiple function calls to complete complex requests
- **Context Awareness**: Maintains conversation history for follow-up commands
- **Error Handling**: Graceful error recovery and user feedback

### Auto-Adjustment & Overlap Prevention
- **Boundary Checking**: Containers automatically fit within canvas bounds
- **Collision Detection**: Prevents overlapping containers
- **Smart Positioning**: Finds optimal positions when conflicts occur

### Natural Language Processing
- **Flexible Commands**: Understands various ways to express the same request
- **Intent Recognition**: Interprets user goals and suggests appropriate actions
- **Conversational Flow**: Maintains context across multiple interactions

## 🎛️ Configuration

### Model Selection
Change the LLM model in the code:
```python
llm_client = CanvasLLMClient(model="gpt-4")  # Use GPT-4 for better performance
```

### Function Call Limits
Adjust maximum function calls per turn:
```python
chatbot.max_function_calls_per_turn = 10  # Allow more complex operations
```

### Browser Mode
Run in headless mode for background operation:
```python
chatbot = CanvasChatbot(headless=True)
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ❌ Error: OPENAI_API_KEY environment variable not set.
   ```
   **Solution**: Set your OpenAI API key in environment variables or .env file

2. **Browser Initialization Failed**
   ```
   ❌ Failed to initialize browser: ChromeDriver not found
   ```
   **Solution**: Install ChromeDriver or ensure Chrome is in PATH

3. **Function Call Errors**
   ```
   ❌ Error: Invalid function arguments
   ```
   **Solution**: The LLM occasionally generates invalid arguments. Try rephrasing your request.

### Debug Mode
Enable verbose logging by modifying the code:
```python
print(f"🔧 EXECUTING: {function_name}({arguments})")  # Already enabled
```

## 🔄 Integration with Core AI Engine

The chatbot follows the same patterns as the core AI engine modules:

- **Modular Architecture**: Separate concerns for LLM, function execution, and canvas control
- **Consistent Error Handling**: Structured error responses and recovery
- **Function Registry Pattern**: Similar to core function registry but specialized for canvas operations
- **Conversation Management**: Maintains context like the core conversation manager

This makes it easy to integrate with the main AI Data Analyst application or extend with additional capabilities.

## 🚀 Future Enhancements

Potential improvements:
- **Voice Input**: Add speech-to-text for voice commands
- **Visual Feedback**: Show container previews before creation
- **Template System**: Save and load canvas layouts
- **Collaboration**: Multi-user canvas editing
- **Advanced Layouts**: Grid snapping and alignment tools

## 📝 Example Session

```
🚀 Starting Canvas Control Chatbot...
Run browser in headless mode? (y/N): n

🤖 Initializing Canvas Chatbot...
🔧 Starting browser and canvas...
✅ Browser initialized successfully
✅ Frontend loaded: file:///path/to/tests/frontend/index.html
🧠 Connecting to OpenAI...
✅ Chatbot initialized successfully!
💡 You can now give me commands to control the canvas.
💡 Try: 'Create a container at position 100,100 with size 200x150'
💡 Type 'help' for more examples or 'quit' to exit.

============================================================
🎨 CANVAS CONTROL CHATBOT
============================================================

💬 You: Create a dashboard layout with a header, sidebar, and main content area

🤖 Assistant: I'll create a dashboard layout with three main sections: a header at the top, a sidebar on the left, and a main content area.

🔧 EXECUTING: create_container({'container_id': 'header', 'x': 0, 'y': 0, 'width': 800, 'height': 80})
✅ Container 'header' created at (0, 0) with size 800x80

🔧 EXECUTING: create_container({'container_id': 'sidebar', 'x': 0, 'y': 80, 'width': 200, 'height': 520})
✅ Container 'sidebar' created at (0, 80) with size 200x520

🔧 EXECUTING: create_container({'container_id': 'main_content', 'x': 200, 'y': 80, 'width': 600, 'height': 520})
✅ Container 'main_content' created at (200, 80) with size 600x520

Perfect! I've created a complete dashboard layout for you:

📋 **Dashboard Layout Created:**
- **Header**: Full-width header bar (800×80px) at the top
- **Sidebar**: Left navigation panel (200×520px) 
- **Main Content**: Primary content area (600×520px) on the right

The layout uses the full canvas space efficiently and provides a professional dashboard structure. You can now add content to each section or modify the sizes as needed!

💬 You: Take a screenshot of this layout

🤖 Assistant: I'll capture a screenshot of your dashboard layout.

🔧 EXECUTING: take_screenshot({})
📸 Screenshot saved: /path/to/tests/python/screenshots/canvas_screenshot_1703123456.png

Screenshot successfully saved! The image captures your complete dashboard layout with the header, sidebar, and main content areas. You can find it in the screenshots directory.

💬 You: quit
👋 Goodbye!

🔒 Closing browser...
``` 