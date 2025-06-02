# AI Data Analyst Web Application - Project Plan

## 🎯 Project Vision

Create a web-based AI data analyst with agentic capabilities that can dynamically modify visualizations through function calling, using a highly modularized, framework-agnostic architecture.

## 🏗️ Modular Architecture Overview

```
ai-data-analyst/
├── PROJECT_PLAN.md                 # This document
├── core/                          # Core business logic (framework-agnostic)
│   ├── README.md
│   ├── function_registry/         # Function calling system
│   ├── ai_engine/                 # LLM integration
│   ├── data_manager/              # Data handling
│   └── visualization_engine/      # Visualization logic
├── ui/                           # User interface layer (framework-specific)
│   ├── README.md
│   ├── streamlit_app/            # Streamlit implementation
│   ├── flask_app/                # Future Flask implementation
│   └── react_app/                # Future React implementation
├── adapters/                     # Interface adapters
│   ├── README.md
│   ├── ui_adapter/               # UI framework adapter
│   └── data_adapter/             # Data source adapter
├── config/                       # Configuration management
│   ├── README.md
│   └── settings.py
└── utils/                        # Shared utilities
    ├── README.md
    └── helpers.py
```

## 📋 Detailed Module Specifications

### 1. Core Modules (Framework-Agnostic)

#### `core/function_registry/`
**Purpose**: Function calling system based on lesson-06 architecture
**Contents**:
- `function_registry.py` - Function definitions and schemas
- `function_executor.py` - Generic execution engine
- `data_analysis_functions.py` - Data analysis specific functions
- `visualization_functions.py` - Visualization creation functions
- `grid_management_functions.py` - Grid container management
- `README.md` - Module documentation

#### `core/ai_engine/`
**Purpose**: LLM integration and conversation management
**Contents**:
- `llm_client.py` - OpenAI API integration
- `conversation_manager.py` - Chat history and context
- `function_caller.py` - LLM function calling workflow
- `README.md` - Module documentation

#### `core/data_manager/`
**Purpose**: Data handling and manipulation
**Contents**:
- `data_loader.py` - Load data from various sources
- `data_processor.py` - Data transformation and filtering
- `data_validator.py` - Data validation and cleaning
- `sample_datasets.py` - Built-in sample datasets
- `README.md` - Module documentation

#### `core/visualization_engine/`
**Purpose**: Visualization creation and management (framework-agnostic)
**Contents**:
- `chart_factory.py` - Chart creation logic
- `visualization_config.py` - Chart configuration schemas
- `grid_manager.py` - Grid layout management
- `export_manager.py` - Export functionality
- `README.md` - Module documentation

### 2. UI Layer (Framework-Specific)

#### `ui/streamlit_app/`
**Purpose**: Streamlit-specific implementation
**Contents**:
- `main.py` - Main Streamlit application
- `components/` - Streamlit components
  - `chat_panel.py` - Chat interface component
  - `visualization_grid.py` - Grid display component
- `README.md` - Streamlit-specific documentation

#### `ui/flask_app/` (Future)
**Purpose**: Flask-specific implementation for more control
**Contents**:
- `app.py` - Flask application
- `templates/` - HTML templates
- `static/` - CSS/JS assets
- `README.md` - Flask-specific documentation

#### `ui/react_app/` (Future)
**Purpose**: React frontend with Python backend
**Contents**:
- `src/` - React components
- `public/` - Static assets
- `README.md` - React-specific documentation

### 3. Adapter Layer

#### `adapters/ui_adapter/`
**Purpose**: Abstract interface between core and UI frameworks
**Contents**:
- `base_ui_adapter.py` - Abstract base class
- `streamlit_adapter.py` - Streamlit-specific adapter
- `flask_adapter.py` - Flask-specific adapter (future)
- `README.md` - Adapter documentation

#### `adapters/data_adapter/`
**Purpose**: Abstract interface for data sources
**Contents**:
- `base_data_adapter.py` - Abstract base class
- `file_adapter.py` - File-based data sources
- `api_adapter.py` - API data sources (future)
- `database_adapter.py` - Database sources (future)
- `README.md` - Data adapter documentation

## 🔧 Technical Implementation Strategy

### Framework Abstraction Pattern

```python
# Core business logic (framework-agnostic)
class VisualizationEngine:
    def create_chart(self, chart_type, data, config):
        # Pure business logic
        return chart_definition

# UI Adapter (framework-specific)
class StreamlitAdapter:
    def render_chart(self, chart_definition):
        # Convert to Streamlit-specific rendering
        return st.plotly_chart(chart_definition)

class FlaskAdapter:
    def render_chart(self, chart_definition):
        # Convert to Flask/HTML rendering
        return render_template('chart.html', chart=chart_definition)
```

### Dependency Injection Pattern

```python
# Main application assembly
def create_app(ui_framework='streamlit'):
    # Core components (framework-agnostic)
    data_manager = DataManager()
    viz_engine = VisualizationEngine()
    ai_engine = AIEngine()
    
    # Framework-specific adapter
    if ui_framework == 'streamlit':
        ui_adapter = StreamlitAdapter()
    elif ui_framework == 'flask':
        ui_adapter = FlaskAdapter()
    
    # Inject dependencies
    app = Application(data_manager, viz_engine, ai_engine, ui_adapter)
    return app
```

## 📋 Function Registry Specifications

### Visualization Functions
```python
# Grid Management
add_container(position: int, size_ratio: float) -> dict
remove_container(container_id: str) -> dict
clear_grid() -> dict
resize_container(container_id: str, size_ratio: float) -> dict

# Chart Creation
create_line_chart(container_id: str, data: dict, x_col: str, y_col: str, title: str) -> dict
create_bar_chart(container_id: str, data: dict, x_col: str, y_col: str, title: str) -> dict
create_scatter_plot(container_id: str, data: dict, x_col: str, y_col: str, title: str) -> dict
create_histogram(container_id: str, data: dict, column: str, bins: int) -> dict
create_heatmap(container_id: str, data: dict, x_col: str, y_col: str, value_col: str) -> dict

# Table Creation
create_data_table(container_id: str, data: dict, columns: list) -> dict
create_summary_table(container_id: str, data: dict, group_by: str) -> dict

# Data Analysis
load_sample_data(dataset_name: str) -> dict
filter_data(column: str, operator: str, value: any) -> dict
group_data(column: str, aggregation: str) -> dict
sort_data(column: str, ascending: bool) -> dict
calculate_statistics(columns: list) -> dict
```

## 🚀 Implementation Phases

### Phase 1: Core Foundation
1. Create modular directory structure
2. Implement core function registry system
3. Create basic AI engine with OpenAI integration
4. Implement data manager with sample datasets
5. Create visualization engine (framework-agnostic)

### Phase 2: Streamlit Implementation
1. Create Streamlit UI adapter
2. Implement chat panel component
3. Implement visualization grid component
4. Integrate all core modules with Streamlit
5. Test complete workflow

### Phase 3: Framework Abstraction
1. Refactor to ensure framework independence
2. Create abstract UI adapter interface
3. Test modularity by creating basic Flask adapter
4. Document framework switching process

### Phase 4: Advanced Features
1. Add more visualization types
2. Implement data export functionality
3. Add advanced data analysis functions
4. Create plugin system for custom functions

## 🎯 Success Criteria

1. **Modularity**: Each module can be developed/tested independently
2. **Framework Independence**: Core logic works with any UI framework
3. **Extensibility**: Easy to add new functions and capabilities
4. **Maintainability**: Clear separation of concerns
5. **Documentation**: Each module has comprehensive README
6. **Testability**: Each module can be unit tested

## 🔄 Framework Migration Strategy

To switch from Streamlit to another framework:
1. Keep all core modules unchanged
2. Create new UI adapter for target framework
3. Implement framework-specific components
4. Update main application assembly
5. Test complete functionality

**Estimated effort**: 2-3 days for basic Flask migration, 1-2 weeks for React migration

## 📝 Development Guidelines

1. **Core modules** must remain framework-agnostic
2. **UI adapters** handle all framework-specific code
3. **Each module** must have comprehensive README
4. **Function registry** follows lesson-06 patterns exactly
5. **All interfaces** use dependency injection
6. **Configuration** centralized in config module

## 🎉 Expected Outcome

A highly modular, extensible AI data analyst that can:
- Switch UI frameworks with minimal effort
- Add new functions through simple registry updates
- Scale to enterprise requirements
- Maintain clean architecture principles
- Support multiple data sources and visualization types

---

**Next Steps**: Create feature branch and begin Phase 1 implementation 