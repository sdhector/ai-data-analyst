# AI Data Analyst - Web Frontend

This is the modern web frontend for the AI Data Analyst application, featuring a dynamic 6x6 grid system for flexible data visualization layouts.

## Features

- **Dynamic 6x6 Grid System**: Place visualizations anywhere on a flexible grid
- **Natural Language Interface**: Chat with AI to analyze data and create visualizations
- **Real-time Updates**: WebSocket communication for instant updates
- **Multiple Chart Types**: Support for line, bar, scatter, pie charts and data tables
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Custom Layouts**: Pre-defined templates or create your own grid layouts

## Architecture

```
web_frontend/
├── index.html          # Main HTML file
├── styles.css          # CSS with purple gradient theme
└── js/
    ├── grid-manager.js     # Dynamic grid management
    ├── chart-manager.js    # Chart rendering (Chart.js & Plotly)
    ├── chat-interface.js   # Chat UI and message handling
    ├── websocket-client.js # Real-time communication
    └── app.js             # Main application entry point
```

## Running the Application

1. Make sure you have Python and the required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Start the web server:
   ```bash
   python main.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Usage

### Basic Commands

- **Load data**: "Load the sales dataset"
- **Create visualizations**: "Create a bar chart showing sales by region"
- **Place containers**: "Add a container in the bottom right corner"
- **Clear grid**: Click the "Clear Grid" button or say "Clear all containers"

### Grid Positions

The AI understands natural language positions:
- "top left", "top right", "bottom left", "bottom right"
- "center", "top", "bottom", "left", "right"
- "small", "medium", "large" (for container sizes)

### Grid Templates

Click "Grid Config" to access pre-defined layouts:
- **Single**: One container taking the entire grid
- **Two Columns**: Split vertically
- **Two Rows**: Split horizontally
- **Quadrants**: Four equal sections
- **Three Columns**: Three vertical sections
- **Custom**: Design your own layout

## Development

### Testing the Frontend

Open the browser console and use these debug commands:

```javascript
// Create a sample dashboard
sampleActions.createSampleDashboard()

// Add a test container
debug.addTestContainer()

// Get current grid state
debug.getGridState()
```

### WebSocket Events

The frontend communicates with the backend via WebSocket:
- `chat_message`: Send user messages
- `chat_response`: Receive AI responses
- `grid_update`: Grid state changes
- `function_result`: Function execution results

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Responsive design with touch support 