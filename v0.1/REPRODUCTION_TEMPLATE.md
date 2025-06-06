# AI Data Analyst Reproduction Template v0.1

## 🎯 Overview

This template provides step-by-step instructions for reproducing the AI Data Analyst system with different parameters, configurations, and use cases. Use this guide to adapt the system for your specific requirements.

## 📋 Table of Contents

1. [Quick Start Template](#quick-start-template)
2. [Configuration Templates](#configuration-templates)
3. [Function Registry Templates](#function-registry-templates)
4. [Frontend Customization Templates](#frontend-customization-templates)
5. [Testing Templates](#testing-templates)
6. [Deployment Templates](#deployment-templates)

---

## Quick Start Template

### Basic Setup Checklist

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd ai-data-analyst
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -r tests/python/requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Test the system
cd tests/python
python quick_pie_chart_test.py

# 5. Run the application
cd ../..
python main.py
```

### Environment Variables Template

```bash
# Required - OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini  # Options: gpt-3.5-turbo, gpt-4, gpt-4o-mini

# Optional - Server Configuration
HOST=localhost            # Change to 0.0.0.0 for external access
PORT=8000                # Change port as needed
DEBUG=true               # Set to false for production

# Optional - Canvas Configuration
CANVAS_WIDTH=800         # Default canvas width
CANVAS_HEIGHT=600        # Default canvas height
AUTO_ADJUST=true         # Auto-adjust containers to fit canvas
OVERLAP_PREVENTION=false # Prevent container overlaps

# Optional - AI Configuration
MAX_TOKENS=1000          # Maximum tokens per response
TEMPERATURE=0.3          # LLM temperature (0.0-1.0)
MAX_FUNCTION_CALLS=5     # Maximum function calls per request
```

---

## Configuration Templates

### 1. Canvas Size Configurations

#### Small Canvas (Mobile/Tablet)
```json
{
    "canvas": {
        "default_width": 400,
        "default_height": 300,
        "max_containers": 10,
        "auto_adjust": true,
        "overlap_prevention": true
    }
}
```

#### Standard Canvas (Desktop)
```json
{
    "canvas": {
        "default_width": 800,
        "default_height": 600,
        "max_containers": 25,
        "auto_adjust": true,
        "overlap_prevention": false
    }
}
```

#### Large Canvas (Presentation/Dashboard)
```json
{
    "canvas": {
        "default_width": 1200,
        "default_height": 800,
        "max_containers": 50,
        "auto_adjust": true,
        "overlap_prevention": false
    }
}
```

### 2. AI Model Configurations

#### Fast Response (GPT-3.5 Turbo)
```json
{
    "ai": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 500,
        "temperature": 0.2,
        "max_function_calls": 3,
        "timeout": 10
    }
}
```

#### Balanced (GPT-4o-mini)
```json
{
    "ai": {
        "model": "gpt-4o-mini",
        "max_tokens": 1000,
        "temperature": 0.3,
        "max_function_calls": 5,
        "timeout": 20
    }
}
```

#### High Quality (GPT-4)
```json
{
    "ai": {
        "model": "gpt-4",
        "max_tokens": 2000,
        "temperature": 0.1,
        "max_function_calls": 10,
        "timeout": 30
    }
}
```

### 3. Use Case Configurations

#### Data Analysis Focus
```json
{
    "enabled_functions": [
        "load_data", "filter_data", "group_data", "calculate_statistics",
        "create_line_chart", "create_bar_chart", "create_scatter_plot",
        "create_data_table", "export_data"
    ],
    "canvas": {
        "default_width": 1000,
        "default_height": 700,
        "grid_layout": "analysis_dashboard"
    }
}
```

#### Presentation Focus
```json
{
    "enabled_functions": [
        "create_pie_chart", "create_bar_chart", "create_line_chart",
        "add_text_container", "take_screenshot", "export_presentation"
    ],
    "canvas": {
        "default_width": 1200,
        "default_height": 800,
        "grid_layout": "presentation_mode"
    }
}
```

#### Educational Focus
```json
{
    "enabled_functions": [
        "create_simple_chart", "add_explanation", "create_tutorial",
        "step_by_step_guide", "interactive_examples"
    ],
    "canvas": {
        "default_width": 800,
        "default_height": 600,
        "grid_layout": "educational_layout"
    }
}
```

---

## Function Registry Templates

### 1. Custom Function Template

```python
# File: custom_functions.py

def custom_analysis_function(data: Dict, parameter: str) -> Dict[str, Any]:
    """
    Template for creating custom analysis functions
    
    Args:
        data: Input data dictionary
        parameter: Analysis parameter
        
    Returns:
        Standardized function result
    """
    try:
        # 1. Input validation
        if not data or not isinstance(data, dict):
            raise ValueError("Data must be a non-empty dictionary")
        
        if not parameter or not isinstance(parameter, str):
            raise ValueError("Parameter must be a non-empty string")
        
        # 2. Your custom logic here
        result = perform_custom_analysis(data, parameter)
        
        # 3. Return standardized format
        return {
            "status": "success",
            "result": result,
            "metadata": {
                "function_name": "custom_analysis_function",
                "execution_time": "...",
                "data_size": len(data)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "function_name": "custom_analysis_function"
        }

# Function schema for LLM
CUSTOM_FUNCTION_SCHEMA = {
    "name": "custom_analysis_function",
    "description": "Performs custom analysis on data with specified parameter",
    "parameters": {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "description": "Data to analyze"
            },
            "parameter": {
                "type": "string",
                "description": "Analysis parameter"
            }
        },
        "required": ["data", "parameter"]
    }
}

# Registration
AVAILABLE_FUNCTIONS["custom_analysis_function"] = custom_analysis_function
FUNCTION_SCHEMAS.append(CUSTOM_FUNCTION_SCHEMA)
```

### 2. Domain-Specific Function Sets

#### Financial Analysis Functions
```python
FINANCIAL_FUNCTIONS = {
    "calculate_returns": calculate_stock_returns,
    "risk_analysis": perform_risk_analysis,
    "portfolio_optimization": optimize_portfolio,
    "create_candlestick_chart": create_candlestick_chart,
    "technical_indicators": calculate_technical_indicators
}

FINANCIAL_SCHEMAS = [
    {
        "name": "calculate_returns",
        "description": "Calculate stock returns from price data",
        "parameters": {
            "type": "object",
            "properties": {
                "price_data": {"type": "array", "description": "Array of price data"},
                "period": {"type": "string", "enum": ["daily", "weekly", "monthly"]}
            },
            "required": ["price_data"]
        }
    }
    # ... more schemas
]
```

#### Scientific Analysis Functions
```python
SCIENTIFIC_FUNCTIONS = {
    "statistical_test": perform_statistical_test,
    "correlation_analysis": calculate_correlations,
    "regression_analysis": perform_regression,
    "create_heatmap": create_correlation_heatmap,
    "hypothesis_testing": test_hypothesis
}
```

### 3. Custom Function Registry

```python
# File: custom_registry.py

class CustomFunctionRegistry(FunctionRegistry):
    def __init__(self, domain="general"):
        super().__init__()
        self.domain = domain
        self.load_domain_functions()
    
    def load_domain_functions(self):
        """Load functions based on domain"""
        if self.domain == "financial":
            self.register_functions(FINANCIAL_FUNCTIONS, FINANCIAL_SCHEMAS)
        elif self.domain == "scientific":
            self.register_functions(SCIENTIFIC_FUNCTIONS, SCIENTIFIC_SCHEMAS)
        elif self.domain == "educational":
            self.register_functions(EDUCATIONAL_FUNCTIONS, EDUCATIONAL_SCHEMAS)
        else:
            self.register_functions(DEFAULT_FUNCTIONS, DEFAULT_SCHEMAS)
    
    def register_functions(self, functions, schemas):
        """Register a set of functions with their schemas"""
        for name, func in functions.items():
            schema = next((s for s in schemas if s["name"] == name), None)
            if schema:
                self.register_function(name, func, schema, self.domain)
```

---

## Frontend Customization Templates

### 1. Custom Canvas Themes

#### Dark Theme
```css
/* File: css/dark-theme.css */
:root {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --text-primary: #ffffff;
    --text-secondary: #cccccc;
    --accent-color: #6366f1;
    --border-color: #404040;
}

.canvas {
    background: var(--bg-primary);
    border: 2px solid var(--border-color);
}

.container {
    background: var(--bg-secondary);
    border: 2px solid var(--accent-color);
    color: var(--text-primary);
}
```

#### Professional Theme
```css
/* File: css/professional-theme.css */
:root {
    --bg-primary: #f8f9fa;
    --bg-secondary: #ffffff;
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --accent-color: #0d6efd;
    --border-color: #dee2e6;
}
```

### 2. Custom Canvas Layouts

#### Grid Layout Template
```javascript
// File: js/custom-layouts.js

class GridLayoutManager {
    constructor(canvas, rows = 3, cols = 3) {
        this.canvas = canvas;
        this.rows = rows;
        this.cols = cols;
        this.setupGrid();
    }
    
    setupGrid() {
        const cellWidth = this.canvas.offsetWidth / this.cols;
        const cellHeight = this.canvas.offsetHeight / this.rows;
        
        this.gridCells = [];
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                this.gridCells.push({
                    x: col * cellWidth,
                    y: row * cellHeight,
                    width: cellWidth,
                    height: cellHeight,
                    occupied: false
                });
            }
        }
    }
    
    getNextAvailableCell() {
        return this.gridCells.find(cell => !cell.occupied);
    }
    
    occupyCell(x, y) {
        const cell = this.gridCells.find(c => 
            c.x <= x && x < c.x + c.width &&
            c.y <= y && y < c.y + c.height
        );
        if (cell) cell.occupied = true;
        return cell;
    }
}
```

### 3. Custom Chart Types

#### Custom Visualization Template
```javascript
// File: js/custom-charts.js

class CustomChartRenderer {
    constructor(container) {
        this.container = container;
    }
    
    renderCustomChart(data, options) {
        // Clear container
        this.container.innerHTML = '';
        
        // Create chart based on type
        switch (options.type) {
            case 'custom_pie':
                return this.renderCustomPieChart(data, options);
            case 'custom_bar':
                return this.renderCustomBarChart(data, options);
            default:
                throw new Error(`Unknown chart type: ${options.type}`);
        }
    }
    
    renderCustomPieChart(data, options) {
        // Custom pie chart implementation
        const svg = this.createSVG();
        // ... chart rendering logic
        this.container.appendChild(svg);
    }
    
    createSVG() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.setAttribute('viewBox', '0 0 400 400');
        return svg;
    }
}
```

---

## Testing Templates

### 1. Custom Test Suite Template

```python
# File: tests/custom_test_suite.py

import pytest
from your_custom_module import CustomFunctionRegistry, CustomCanvasController

class TestCustomFunctionality:
    
    @pytest.fixture
    def custom_registry(self):
        """Setup custom function registry for testing"""
        return CustomFunctionRegistry(domain="your_domain")
    
    @pytest.fixture
    def canvas_controller(self):
        """Setup canvas controller for testing"""
        return CustomCanvasController(
            width=800,
            height=600,
            headless=True
        )
    
    def test_custom_function_execution(self, custom_registry):
        """Test custom function execution"""
        result = custom_registry.execute_function(
            "your_custom_function",
            {"param1": "value1", "param2": "value2"}
        )
        
        assert result["status"] == "success"
        assert "result" in result
        # Add your specific assertions
    
    def test_canvas_integration(self, canvas_controller):
        """Test canvas integration with custom functions"""
        # Create container
        success = canvas_controller.create_container(
            "test_container", 100, 100, 200, 150
        )
        assert success
        
        # Test custom visualization
        result = canvas_controller.add_custom_visualization(
            "test_container", "your_chart_type", {"data": "test_data"}
        )
        assert result["status"] == "success"
    
    @pytest.mark.parametrize("canvas_size,expected_containers", [
        ((400, 300), 5),
        ((800, 600), 15),
        ((1200, 800), 25)
    ])
    def test_different_canvas_sizes(self, canvas_size, expected_containers):
        """Test system with different canvas sizes"""
        width, height = canvas_size
        controller = CustomCanvasController(
            width=width, height=height, headless=True
        )
        
        # Test container creation up to expected limit
        for i in range(expected_containers):
            success = controller.create_container(f"container_{i}", 0, 0, 50, 50)
            assert success
        
        state = controller.get_current_state()
        assert len(state['containers']) == expected_containers
```

### 2. Performance Testing Template

```python
# File: tests/performance_test_template.py

import time
import pytest
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    
    def test_function_execution_speed(self, function_registry):
        """Test function execution performance"""
        start_time = time.time()
        
        # Execute function multiple times
        for i in range(100):
            result = function_registry.execute_function(
                "test_function", {"iteration": i}
            )
            assert result["status"] == "success"
        
        execution_time = time.time() - start_time
        assert execution_time < 10.0  # Should complete in under 10 seconds
    
    def test_concurrent_function_calls(self, function_registry):
        """Test concurrent function execution"""
        def execute_function(iteration):
            return function_registry.execute_function(
                "test_function", {"iteration": iteration}
            )
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(execute_function, i) for i in range(50)]
            results = [future.result() for future in futures]
        
        execution_time = time.time() - start_time
        
        # All should succeed
        assert all(r["status"] == "success" for r in results)
        # Should handle concurrency efficiently
        assert execution_time < 15.0
    
    def test_memory_usage(self, canvas_controller):
        """Test memory usage with many containers"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create many containers
        for i in range(100):
            canvas_controller.create_container(
                f"container_{i}", i*10, i*10, 50, 50
            )
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024
```

### 3. Integration Testing Template

```python
# File: tests/integration_test_template.py

class TestIntegration:
    
    def test_end_to_end_workflow(self, chatbot):
        """Test complete workflow from user input to result"""
        # Test sequence of operations
        test_commands = [
            ("Clear canvas", "clear"),
            ("Create container", "create_container"),
            ("Add visualization", "add_chart"),
            ("Take screenshot", "screenshot")
        ]
        
        for description, expected_action in test_commands:
            response = chatbot.process_user_message(
                f"Please {description.lower()}"
            )
            
            # Verify response contains expected action
            assert expected_action in response.lower()
            assert "error" not in response.lower()
    
    def test_error_handling_workflow(self, chatbot):
        """Test error handling in complete workflow"""
        # Test invalid operations
        error_commands = [
            "Delete non-existent container",
            "Create chart in missing container",
            "Use invalid chart type"
        ]
        
        for command in error_commands:
            response = chatbot.process_user_message(command)
            
            # Should handle errors gracefully
            assert "error" in response.lower() or "not found" in response.lower()
            assert "sorry" in response.lower() or "unable" in response.lower()
```

---

## Deployment Templates

### 1. Docker Deployment Template

#### Development Dockerfile
```dockerfile
# File: Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
COPY tests/python/requirements.txt ./tests/python/
RUN pip install -r requirements.txt
RUN pip install -r tests/python/requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Expose port
EXPOSE 8000

# Development command with auto-reload
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### Production Dockerfile
```dockerfile
# File: Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Production command
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

### 2. Docker Compose Templates

#### Development Environment
```yaml
# File: docker-compose.dev.yml
version: '3.8'

services:
  ai-data-analyst:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=true
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - .:/app
      - /app/venv
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

#### Production Environment
```yaml
# File: docker-compose.prod.yml
version: '3.8'

services:
  ai-data-analyst:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=false
      - HOST=0.0.0.0
      - PORT=8000
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-data-analyst
    restart: unless-stopped

volumes:
  redis_data:
```

### 3. Kubernetes Deployment Template

```yaml
# File: k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-data-analyst
  labels:
    app: ai-data-analyst
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-data-analyst
  template:
    metadata:
      labels:
        app: ai-data-analyst
    spec:
      containers:
      - name: ai-data-analyst
        image: your-registry/ai-data-analyst:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: ai-data-analyst-service
spec:
  selector:
    app: ai-data-analyst
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

---

## 🔧 Customization Checklist

### Before You Start
- [ ] Define your use case and requirements
- [ ] Choose appropriate canvas size and layout
- [ ] Select AI model based on performance needs
- [ ] Identify required function categories
- [ ] Plan your testing strategy

### Configuration Steps
- [ ] Copy and customize environment variables
- [ ] Modify canvas configuration for your use case
- [ ] Adjust AI model settings
- [ ] Configure function registry for your domain
- [ ] Set up custom themes if needed

### Development Steps
- [ ] Implement custom functions following templates
- [ ] Add custom UI components if needed
- [ ] Create domain-specific schemas
- [ ] Write tests for your customizations
- [ ] Document your changes

### Deployment Steps
- [ ] Choose deployment method (Docker, K8s, etc.)
- [ ] Configure production environment variables
- [ ] Set up monitoring and logging
- [ ] Test deployment in staging environment
- [ ] Deploy to production

### Testing Steps
- [ ] Run unit tests for custom functions
- [ ] Execute integration tests
- [ ] Perform end-to-end testing
- [ ] Conduct performance testing
- [ ] Validate error handling

---

## 📚 Additional Templates

### Environment-Specific Configurations

#### Local Development
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
HOST=localhost
PORT=8000
DEBUG=true
CANVAS_WIDTH=800
CANVAS_HEIGHT=600
```

#### Staging Environment
```bash
OPENAI_API_KEY=your_staging_key
OPENAI_MODEL=gpt-4o-mini
HOST=0.0.0.0
PORT=8000
DEBUG=false
CANVAS_WIDTH=1000
CANVAS_HEIGHT=700
```

#### Production Environment
```bash
OPENAI_API_KEY=your_production_key
OPENAI_MODEL=gpt-4
HOST=0.0.0.0
PORT=8000
DEBUG=false
CANVAS_WIDTH=1200
CANVAS_HEIGHT=800
```

This template provides a comprehensive foundation for reproducing and customizing the AI Data Analyst system for various use cases and environments.