# AI Data Analyst - Streamlit Application

## 🚀 Quick Start

### 1. Setup Environment

Create a `.env` file in the project root with your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run ui/streamlit_app/app.py
```

## 🎯 Features

### Left Panel: AI Chatbot
- **Conversational Interface**: Natural language interaction with AI
- **Function Calling**: AI can execute data analysis and visualization functions
- **Chat History**: Persistent conversation with function call tracking
- **System Status**: Real-time status indicators and usage metrics

### Right Panel: Visualization Grid
- **6-Container Grid**: 2x3 layout for visualizations (positions 1-6)
- **Dynamic Content**: Charts, tables, and data displays
- **Interactive Controls**: Remove containers, clear grid, refresh content
- **Auto-Management**: AI automatically creates containers for visualizations

### Sidebar: System Controls
- **System Status**: Connection status, token usage, cost estimation
- **Conversation Management**: Clear chat history
- **Function Registry**: View available functions by category

## 🤖 AI Capabilities

### Data Analysis Functions
- `load_sample_data`: Load built-in datasets (sales, employees, stocks)
- `filter_data`: Filter data based on conditions
- `group_data`: Group and aggregate data
- `sort_data`: Sort data by columns
- `calculate_statistics`: Descriptive statistics
- `get_data_sample`: View data samples

### Visualization Functions
- `create_line_chart`: Time series and trend analysis
- `create_bar_chart`: Categorical comparisons
- `create_scatter_plot`: Correlation analysis
- `create_histogram`: Distribution analysis
- `create_data_table`: Tabular data display

### Grid Management Functions
- `add_container`: Create new visualization containers
- `remove_container`: Remove specific containers
- `clear_grid`: Clear all containers
- `resize_container`: Adjust container sizes
- `get_grid_status`: View grid information

## 💬 Example Conversations

### Getting Started
```
User: "Hello! What can you help me with?"
AI: "I'm your AI Data Analyst! I can help you load datasets, create visualizations, and analyze data..."
```

### Load and Explore Data
```
User: "Load the sales dataset and show me the first 10 rows"
AI: [Calls load_sample_data and create_data_table functions]
```

### Create Visualizations
```
User: "Create a line chart showing sales over time"
AI: [Calls create_line_chart function with appropriate parameters]
```

### Data Analysis
```
User: "Filter the data for sales > 1000 and create a bar chart by region"
AI: [Calls filter_data and create_bar_chart functions]
```

## 🔧 Technical Architecture

### Framework-Agnostic Core
- All business logic in `core/` modules
- No Streamlit dependencies in core components
- Easy to port to other frameworks (Flask, FastAPI, etc.)

### Modular Function Registry
- Functions organized by category
- OpenAI function calling schemas
- Automatic container management for visualizations

### AI Engine Integration
- LLM client with retry logic and error handling
- Conversation management with context optimization
- Function calling orchestration with multi-step workflows

## 🎨 UI Components

### Custom Styling
- Modern chat interface with message bubbles
- Grid layout with visual indicators
- Status indicators and metrics
- Responsive design

### Interactive Elements
- Chat input with real-time processing
- Container management buttons
- Grid controls and status displays
- Sidebar with system information

## 🔍 Troubleshooting

### Common Issues

**API Key Not Found**
- Ensure `.env` file exists in project root
- Check `OPENAI_API_KEY` is set correctly
- Restart the application after adding the key

**Function Calling Errors**
- Check internet connection for OpenAI API
- Verify API key has sufficient credits
- Review error messages in chat interface

**Visualization Not Displaying**
- Check if container was created successfully
- Verify chart data is valid
- Try refreshing the container

### Debug Mode

Run with debug information:
```bash
streamlit run ui/streamlit_app/app.py --logger.level=debug
```

## 📊 Performance

### Token Usage
- Efficient context management
- Function calling optimization
- Usage tracking and cost estimation

### Response Times
- Async processing where possible
- Caching for repeated operations
- Optimized chart rendering

## 🔮 Future Enhancements

- [ ] File upload for custom datasets
- [ ] Export visualizations and reports
- [ ] Advanced chart customization
- [ ] Multi-user support
- [ ] Dashboard templates
- [ ] Real-time data connections 