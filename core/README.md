# Core Module

## 🎯 Purpose

The core module contains all framework-agnostic business logic for the AI Data Analyst application. This module is completely independent of any UI framework and can be used with Streamlit, Flask, React, or any other interface.

## 📁 Structure

```
core/
├── README.md                    # This file
├── function_registry/           # Function calling system
├── ai_engine/                   # LLM integration
├── data_manager/                # Data handling
└── visualization_engine/        # Visualization logic
```

## 🔧 Design Principles

1. **Framework Independence**: No UI framework dependencies
2. **Pure Business Logic**: Only domain-specific functionality
3. **Dependency Injection**: All external dependencies injected
4. **Interface-Based**: Uses abstract interfaces for external communication
5. **Testable**: Each component can be unit tested independently

## 🚀 Usage

```python
# Import core components
from core.function_registry import FunctionRegistry
from core.ai_engine import AIEngine
from core.data_manager import DataManager
from core.visualization_engine import VisualizationEngine

# Create instances (framework-agnostic)
registry = FunctionRegistry()
ai_engine = AIEngine()
data_manager = DataManager()
viz_engine = VisualizationEngine()

# Use with any UI framework through adapters
```

## 📋 Module Dependencies

- **function_registry**: Based on lesson-06 modular architecture
- **ai_engine**: OpenAI API integration
- **data_manager**: Pandas, NumPy for data handling
- **visualization_engine**: Plotly for chart generation

## 🔗 Integration

Core modules integrate with UI frameworks through the adapter pattern:

```python
# Framework-agnostic core
result = viz_engine.create_chart(chart_type, data, config)

# Framework-specific rendering (via adapter)
ui_adapter.render_chart(result)
```

## 📝 Development Guidelines

1. **No UI imports**: Never import Streamlit, Flask, etc. in core modules
2. **Return data structures**: Always return dictionaries or data classes
3. **Use dependency injection**: Accept external dependencies as parameters
4. **Document interfaces**: Clear input/output specifications
5. **Error handling**: Return structured error information

## 🧪 Testing

Each core module can be tested independently:

```bash
python -m pytest core/function_registry/tests/
python -m pytest core/ai_engine/tests/
python -m pytest core/data_manager/tests/
python -m pytest core/visualization_engine/tests/
``` 