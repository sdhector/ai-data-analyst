# Pie Chart Functionality

## 🥧 Overview

The pie chart functionality has been added to the LLM Canvas Chatbot in the Python test environment. This feature allows you to create interactive pie charts within containers using natural language commands.

## ✨ Features

- **Sample Data**: Default pie chart with Technology, Healthcare, Finance, Education, and Retail sectors
- **Custom Data**: Create pie charts with your own labels and values
- **SVG-based**: High-quality scalable vector graphics
- **Interactive**: Hover tooltips showing values and percentages
- **Responsive**: Charts adapt to container size
- **Colorful**: Predefined color palette for visual appeal
- **Legend**: Automatic legend generation with percentages

## 🚀 Quick Start

### Prerequisites

1. **OpenAI API Key**: Set your API key in environment variables
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

2. **Dependencies**: Ensure you have the required packages
   ```bash
   pip install openai python-dotenv selenium
   ```

### Running the Demo

```bash
cd tests/python
python demo_pie_chart.py
```

### Running Tests

```bash
cd tests/python
python test_pie_chart.py
```

## 💬 Usage Examples

### Basic Pie Chart with Sample Data

```
You: Create a container at 100,100 with size 400x300 called 'chart1'
Assistant: ✅ Container 'chart1' created at (100, 100) with size 400x300

You: Create a pie chart in container 'chart1' with title 'Market Share'
Assistant: ✅ Pie chart 'Market Share' created successfully in container 'chart1' using sample data
```

### Custom Pie Chart

```
You: Create a pie chart in container 'chart1' with custom data:
     Labels: Sales, Marketing, Development, Support
     Values: 40, 25, 30, 5
     Title: Department Budget
Assistant: ✅ Pie chart 'Department Budget' created successfully in container 'chart1' using custom data with 4 segments
```

### Natural Language Commands

The LLM understands various ways to express pie chart requests:

```
You: Add a pie chart to the container I just created
You: Create a pie chart showing sales data
You: Make a pie chart with custom values for each department
You: Show market share in a pie chart format
```

## 🔧 Technical Details

### Function Schema

The `create_pie_chart` function accepts the following parameters:

- **container_id** (required): ID of an existing container
- **title** (optional): Chart title (default: "Pie Chart")
- **use_sample_data** (optional): Whether to use sample data (default: true)
- **labels** (optional): Array of custom labels (required if use_sample_data is false)
- **values** (optional): Array of custom values (required if use_sample_data is false)

### Sample Data

Default sample data includes:
- Technology: 35%
- Healthcare: 25%
- Finance: 20%
- Education: 12%
- Retail: 8%

### Color Palette

The pie chart uses a predefined color palette:
- #667eea (Blue)
- #764ba2 (Purple)
- #f093fb (Pink)
- #4facfe (Light Blue)
- #00f2fe (Cyan)
- #fa709a (Rose)
- #fee140 (Yellow)
- #30cfd0 (Teal)
- #a8edea (Light Green)
- #fed6e3 (Light Pink)

## 📋 Requirements

### Container Dependency

Pie charts **must** be placed inside existing containers. The function will:
1. Check if the specified container exists
2. Validate the container ID against current canvas state
3. Provide helpful error messages if container is not found

### Data Validation

For custom data:
- Labels and values arrays must have the same length
- Values should be positive numbers
- At least one data point is required

## 🐛 Error Handling

### Common Errors and Solutions

1. **Container Not Found**
   ```
   Error: Container 'chart1' not found. Available containers: container_1, container_2
   Solution: Create the container first or use an existing container ID
   ```

2. **Mismatched Arrays**
   ```
   Error: Labels and values must have the same length. Got 3 labels and 2 values.
   Solution: Ensure labels and values arrays have the same number of elements
   ```

3. **No Containers**
   ```
   Error: No containers exist on canvas. Create a container first before adding a pie chart.
   Solution: Create at least one container before adding pie charts
   ```

## 🎨 Visual Examples

### Sample Data Pie Chart
- Clean, professional appearance
- Hover tooltips with percentages
- Color-coded legend
- Responsive design

### Custom Data Pie Chart
- User-defined segments
- Automatic percentage calculation
- Consistent styling
- Interactive elements

## 🔄 Integration

The pie chart functionality integrates seamlessly with:
- **Container Management**: Works with existing container system
- **Canvas Operations**: Supports screenshots, state management
- **LLM Function Calling**: Natural language interface
- **Error Handling**: Consistent error reporting

## 🚀 Future Enhancements

Potential improvements:
- **Animation**: Smooth transitions and loading effects
- **Themes**: Multiple color schemes and styles
- **Export**: Direct chart export functionality
- **Data Sources**: Integration with external data sources
- **3D Effects**: Optional 3D pie chart rendering
- **Drill-down**: Interactive segment exploration

## 📝 Example Session

```bash
$ python demo_pie_chart.py

🎯 PIE CHART FUNCTIONALITY DEMO
==================================================
This demo shows how to create pie charts using the LLM Canvas Chatbot.
You can interact with the chatbot using natural language!

Run browser in headless mode? (y/N): n

🤖 Initializing Canvas Chatbot...
🔧 Starting browser and canvas...
✅ Browser initialized successfully!
✅ Frontend loaded: file:///path/to/tests/frontend/index.html
🧠 Connecting to OpenAI...
✅ Chatbot initialized successfully!

🎨 DEMO SEQUENCE
==============================

1. Command: Clear the canvas to start fresh
   Processing...
   ✅ Response: Canvas cleared successfully! Ready for new containers and visualizations.

2. Command: Create a container at position 100,100 with size 400x300 called 'sales_chart'
   Processing...
   ✅ Response: Container 'sales_chart' created successfully at (100, 100) with size 400x300 pixels...

3. Command: Create a pie chart in container 'sales_chart' with the title 'Q4 Sales by Region'
   Processing...
   ✅ Response: Pie chart 'Q4 Sales by Region' created successfully in container 'sales_chart'...

🎉 Demo completed successfully!

💬 Your command (or 'quit' to exit): Show me the current canvas state
🤖 Processing...
🤖 Assistant: Your canvas currently has 2 containers with pie charts displaying sales and budget data...
```

## 📚 Related Documentation

- [LLM Canvas Chatbot README](README_LLM_CHATBOT.md)
- [Canvas Controller Documentation](canvas_controller.py)
- [Interactive Test Menu](interactive_test.py)

---

**Note**: This pie chart functionality is part of the Python test environment and demonstrates how visualization features can be integrated with the LLM Canvas Chatbot system. 