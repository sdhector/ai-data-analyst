# Container Canvas Testing Environment

This is a minimal testing environment for container placement and management functionality.

## Structure

```
tests/
├── frontend/           # Minimal HTML frontend
│   └── index.html     # Canvas with container display
├── python/            # Python controller scripts
│   ├── canvas_controller.py  # Main controller class
│   └── requirements.txt      # Python dependencies
└── README.md          # This file
```

## Setup

1. **Install Python dependencies:**
   ```bash
   cd tests/python
   pip install -r requirements.txt
   ```

2. **Install ChromeDriver:**
   - Download from: https://chromedriver.chromium.org/
   - Or use webdriver-manager (automatic): `pip install webdriver-manager`

## Frontend

The frontend (`tests/frontend/index.html`) provides:
- A simple 800x600 canvas area
- Real-time display of container state
- JavaScript API for container manipulation
- Visual feedback with hover effects

## Python Controller

The `CanvasController` class provides these functions:

### 1. Get Current State
```python
controller = CanvasController()
state = controller.get_current_state()
# Returns: {hasContainers: bool, containerCount: int, containers: [...]}
```

### 2. Create Container
```python
controller.create_container(
    container_id="my_container",
    x=100,           # X position in pixels
    y=50,            # Y position in pixels  
    width=200,       # Width in pixels
    height=150       # Height in pixels
)
```

### 3. Delete Container
```python
controller.delete_container("my_container")
```

### 4. Modify Container
```python
controller.modify_container(
    container_id="my_container",
    x=150,           # New X position
    y=75,            # New Y position
    width=250,       # New width
    height=180       # New height
)
```

## Usage Example

```python
from canvas_controller import CanvasController

# Initialize (browser will open)
controller = CanvasController(headless=False)

try:
    # Check initial state
    state = controller.get_current_state()
    print(f"Canvas has {state['containerCount']} containers")
    
    # Create containers
    controller.create_container("chart1", 50, 50, 200, 150)
    controller.create_container("chart2", 300, 100, 150, 100)
    
    # Modify a container
    controller.modify_container("chart1", 75, 75, 250, 180)
    
    # Take screenshot
    controller.take_screenshot("my_layout.png")
    
    # Delete container
    controller.delete_container("chart2")
    
finally:
    # Always cleanup
    controller.close()
```

## Demo

Run the built-in demo:
```bash
cd tests/python
python canvas_controller.py
```

This will:
1. Open a browser window
2. Create several test containers
3. Modify and delete containers
4. Take screenshots
5. Show the final state

## Features

- **Visual Feedback**: Containers have hover effects and smooth transitions
- **State Tracking**: Real-time display of all container positions and sizes
- **Screenshots**: Capture canvas state for documentation
- **Error Handling**: Comprehensive validation and error reporting
- **Canvas Bounds**: Automatic validation of container placement within bounds
- **Headless Mode**: Option to run without visible browser window

## Canvas Specifications

- **Size**: 800x600 pixels
- **Coordinate System**: Top-left origin (0,0)
- **Container Styling**: Blue borders, hover effects, centered labels
- **State Display**: Live updates below the canvas

This testing environment provides a clean, minimal foundation for testing container placement algorithms and UI interactions. 