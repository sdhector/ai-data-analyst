# Function Registry Module

## 🎯 Purpose

This module implements the function calling system based on the lesson-06 modular architecture. It provides a complete registry of functions that the AI can call to manipulate data and visualizations.

## 📁 Structure

```
function_registry/
├── README.md                        # This file
├── __init__.py                      # Module initialization
├── function_registry.py             # Main function registry
├── function_executor.py             # Generic execution engine
├── data_analysis_functions.py       # Data analysis functions
├── visualization_functions.py       # Visualization creation functions
├── grid_management_functions.py     # Grid container management
└── function_schemas.py              # OpenAI function schemas
```

## 🔧 Core Components

### Function Registry
Central registry mapping function names to callable objects:
```python
AVAILABLE_FUNCTIONS = {
    "create_line_chart": create_line_chart,
    "filter_data": filter_data,
    "add_container": add_container,
    # ... more functions
}
```

### Function Executor
Generic execution engine that works with any function registry:
```python
executor = FunctionExecutor(AVAILABLE_FUNCTIONS, FUNCTION_SCHEMAS)
result = executor.execute_function_call("create_line_chart", arguments)
```

### Function Categories

#### 1. Data Analysis Functions
- `load_sample_data(dataset_name)` - Load built-in datasets
- `filter_data(column, operator, value)` - Filter data by conditions
- `group_data(column, aggregation)` - Group and aggregate data
- `sort_data(column, ascending)` - Sort data by column
- `calculate_statistics(columns)` - Calculate descriptive statistics

#### 2. Visualization Functions
- `create_line_chart(container_id, data, x_col, y_col, title)` - Line charts
- `create_bar_chart(container_id, data, x_col, y_col, title)` - Bar charts
- `create_scatter_plot(container_id, data, x_col, y_col, title)` - Scatter plots
- `create_histogram(container_id, data, column, bins)` - Histograms
- `create_data_table(container_id, data, columns)` - Data tables

#### 3. Grid Management Functions
- `add_container(position, size_ratio)` - Add new visualization container
- `remove_container(container_id)` - Remove container
- `clear_grid()` - Clear all containers
- `resize_container(container_id, size_ratio)` - Resize container

## 🚀 Usage

### Basic Function Execution
```python
from core.function_registry import FunctionExecutor, AVAILABLE_FUNCTIONS, FUNCTION_SCHEMAS

# Create executor
executor = FunctionExecutor(AVAILABLE_FUNCTIONS, FUNCTION_SCHEMAS)

# Execute function
result = executor.execute_function_call(
    "create_line_chart",
    {
        "container_id": "chart_1",
        "data": {"x": [1, 2, 3], "y": [4, 5, 6]},
        "x_col": "x",
        "y_col": "y",
        "title": "Sample Chart"
    }
)
```

### With LLM Integration
```python
from core.function_registry import LLMFunctionCaller

# Create LLM function caller
caller = LLMFunctionCaller(executor)

# Chat with function calling
response = caller.chat_with_functions(
    "Create a line chart showing sales over time"
)
```

## 📋 Function Specifications

### Input/Output Format
All functions follow a consistent pattern:
```python
def function_name(param1: type, param2: type = default) -> Dict[str, Any]:
    """Function description"""
    try:
        # Function logic
        return {
            "status": "success",
            "result": result_data,
            "metadata": additional_info
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "function_name": "function_name"
        }
```

### Schema Format
Each function has an OpenAI-compatible schema:
```python
{
    "name": "function_name",
    "description": "What this function does",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
}
```

## 🔧 Extending the Registry

### Adding New Functions
1. Define the function in appropriate module:
```python
def new_analysis_function(data: dict, param: str) -> dict:
    """New analysis function"""
    # Implementation
    return {"status": "success", "result": result}
```

2. Add to registry:
```python
AVAILABLE_FUNCTIONS["new_analysis_function"] = new_analysis_function
```

3. Add schema:
```python
NEW_FUNCTION_SCHEMA = {
    "name": "new_analysis_function",
    "description": "Description of new function",
    "parameters": {
        # Parameter specification
    }
}
FUNCTION_SCHEMAS.append(NEW_FUNCTION_SCHEMA)
```

### Creating Custom Registries
```python
# Domain-specific registry
custom_functions = {
    "domain_function_1": function_1,
    "domain_function_2": function_2
}

custom_schemas = [schema_1, schema_2]

# Use with same executor
custom_executor = FunctionExecutor(custom_functions, custom_schemas)
```

## 🧪 Testing

### Unit Testing Functions
```python
def test_create_line_chart():
    result = create_line_chart(
        container_id="test",
        data={"x": [1, 2], "y": [3, 4]},
        x_col="x",
        y_col="y",
        title="Test"
    )
    assert result["status"] == "success"
    assert "chart_config" in result["result"]
```

### Integration Testing
```python
def test_function_executor():
    executor = FunctionExecutor(AVAILABLE_FUNCTIONS, FUNCTION_SCHEMAS)
    result = executor.execute_function_call("create_line_chart", test_args)
    assert result["status"] == "success"
```

## 📝 Development Guidelines

1. **Consistent Return Format**: All functions return structured dictionaries
2. **Error Handling**: Comprehensive error catching and reporting
3. **Type Hints**: Full type annotations for all functions
4. **Documentation**: Clear docstrings for all functions
5. **Validation**: Input validation for all parameters
6. **Framework Independence**: No UI framework dependencies

## 🔗 Dependencies

- **OpenAI**: For LLM integration
- **Pandas**: For data manipulation
- **NumPy**: For numerical operations
- **Plotly**: For chart generation (framework-agnostic)
- **Python-dotenv**: For environment variables 