"""
Main Function Registry

This module combines all available functions and their schemas for the AI Data Analyst.
Based on the lesson-06 modular architecture pattern.
"""

from typing import Dict, Any, Callable, List

# Import all function modules
from .data_analysis_functions import (
    load_sample_data,
    get_current_data_info,
    filter_data,
    group_data,
    sort_data,
    calculate_statistics,
    get_data_sample
)

from .visualization_functions import (
    create_line_chart,
    create_bar_chart,
    create_scatter_plot,
    create_histogram,
    create_data_table
)

from .grid_management_functions import (
    add_container,
    remove_container,
    clear_grid,
    resize_container,
    get_grid_status,
    update_container_content
)

# ============================================================================
# FUNCTION REGISTRY - Maps string names to function objects
# ============================================================================

AVAILABLE_FUNCTIONS: Dict[str, Callable] = {
    # Data Analysis Functions
    "load_sample_data": load_sample_data,
    "get_current_data_info": get_current_data_info,
    "filter_data": filter_data,
    "group_data": group_data,
    "sort_data": sort_data,
    "calculate_statistics": calculate_statistics,
    "get_data_sample": get_data_sample,
    
    # Visualization Functions
    "create_line_chart": create_line_chart,
    "create_bar_chart": create_bar_chart,
    "create_scatter_plot": create_scatter_plot,
    "create_histogram": create_histogram,
    "create_data_table": create_data_table,
    
    # Grid Management Functions
    "add_container": add_container,
    "remove_container": remove_container,
    "clear_grid": clear_grid,
    "resize_container": resize_container,
    "get_grid_status": get_grid_status,
    "update_container_content": update_container_content
}

# ============================================================================
# FUNCTION SCHEMAS - OpenAI function calling schemas
# ============================================================================

FUNCTION_SCHEMAS = [
    # Data Analysis Functions
    {
        "name": "load_sample_data",
        "description": "Load a built-in sample dataset for analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "dataset_name": {
                    "type": "string",
                    "enum": ["sales", "employees", "stocks"],
                    "description": "Name of the sample dataset to load"
                }
            },
            "required": ["dataset_name"]
        }
    },
    {
        "name": "get_current_data_info",
        "description": "Get information about the currently loaded dataset",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "filter_data",
        "description": "Filter the current dataset based on a condition",
        "parameters": {
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Column name to filter on"
                },
                "operator": {
                    "type": "string",
                    "enum": ["==", "!=", ">", "<", ">=", "<=", "contains"],
                    "description": "Comparison operator"
                },
                "value": {
                    "description": "Value to compare against (string, number, or boolean)"
                }
            },
            "required": ["column", "operator", "value"]
        }
    },
    {
        "name": "group_data",
        "description": "Group data by a column and apply aggregation",
        "parameters": {
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Column to group by"
                },
                "aggregation": {
                    "type": "string",
                    "enum": ["count", "sum", "mean", "median", "min", "max"],
                    "description": "Aggregation function to apply"
                }
            },
            "required": ["column", "aggregation"]
        }
    },
    {
        "name": "sort_data",
        "description": "Sort the current dataset by a column",
        "parameters": {
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Column to sort by"
                },
                "ascending": {
                    "type": "boolean",
                    "description": "Sort in ascending order (true) or descending (false)",
                    "default": True
                }
            },
            "required": ["column"]
        }
    },
    {
        "name": "calculate_statistics",
        "description": "Calculate descriptive statistics for specified columns",
        "parameters": {
            "type": "object",
            "properties": {
                "columns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of column names to analyze (null for all numeric columns)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_data_sample",
        "description": "Get a sample of the current dataset",
        "parameters": {
            "type": "object",
            "properties": {
                "n_rows": {
                    "type": "integer",
                    "description": "Number of rows to return",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": []
        }
    },
    
    # Visualization Functions
    {
        "name": "create_line_chart",
        "description": "Create a line chart visualization",
        "parameters": {
            "type": "object",
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "ID of the container to place the chart (use 'auto' for automatic placement)"
                },
                "x_col": {
                    "type": "string",
                    "description": "Column name for x-axis"
                },
                "y_col": {
                    "type": "string",
                    "description": "Column name for y-axis"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title",
                    "default": ""
                },
                "color_col": {
                    "type": "string",
                    "description": "Optional column for color grouping"
                }
            },
            "required": ["container_id", "x_col", "y_col"]
        }
    },
    {
        "name": "create_bar_chart",
        "description": "Create a bar chart visualization",
        "parameters": {
            "type": "object",
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "ID of the container to place the chart (use 'auto' for automatic placement)"
                },
                "x_col": {
                    "type": "string",
                    "description": "Column name for x-axis (categories)"
                },
                "y_col": {
                    "type": "string",
                    "description": "Column name for y-axis (values)"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title",
                    "default": ""
                },
                "color_col": {
                    "type": "string",
                    "description": "Optional column for color grouping"
                }
            },
            "required": ["container_id", "x_col", "y_col"]
        }
    },
    {
        "name": "create_scatter_plot",
        "description": "Create a scatter plot visualization",
        "parameters": {
            "type": "object",
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "ID of the container to place the chart (use 'auto' for automatic placement)"
                },
                "x_col": {
                    "type": "string",
                    "description": "Column name for x-axis"
                },
                "y_col": {
                    "type": "string",
                    "description": "Column name for y-axis"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title",
                    "default": ""
                },
                "color_col": {
                    "type": "string",
                    "description": "Optional column for color mapping"
                },
                "size_col": {
                    "type": "string",
                    "description": "Optional column for size mapping"
                }
            },
            "required": ["container_id", "x_col", "y_col"]
        }
    },
    {
        "name": "create_histogram",
        "description": "Create a histogram visualization",
        "parameters": {
            "type": "object",
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "ID of the container to place the chart (use 'auto' for automatic placement)"
                },
                "column": {
                    "type": "string",
                    "description": "Column name for the histogram (must be numeric)"
                },
                "bins": {
                    "type": "integer",
                    "description": "Number of bins",
                    "default": 20,
                    "minimum": 5,
                    "maximum": 100
                },
                "title": {
                    "type": "string",
                    "description": "Chart title",
                    "default": ""
                }
            },
            "required": ["container_id", "column"]
        }
    },
    {
        "name": "create_data_table",
        "description": "Create a data table visualization",
        "parameters": {
            "type": "object",
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "ID of the container to place the table (use 'auto' for automatic placement)"
                },
                "columns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of columns to include (null for all columns)"
                },
                "max_rows": {
                    "type": "integer",
                    "description": "Maximum number of rows to display",
                    "default": 100,
                    "minimum": 10,
                    "maximum": 1000
                }
            },
            "required": ["container_id"]
        }
    },
    
    # Grid Management Functions
    {
        "name": "add_container",
        "description": "Add a new visualization container to the grid",
        "parameters": {
            "type": "object",
            "properties": {
                "position": {
                    "type": "integer",
                    "description": "Position in the grid (1-6, null for next available)",
                    "minimum": 1,
                    "maximum": 6
                },
                "size_ratio": {
                    "type": "number",
                    "description": "Relative size of the container",
                    "default": 1.0,
                    "minimum": 0.5,
                    "maximum": 2.0
                }
            },
            "required": []
        }
    },
    {
        "name": "remove_container",
        "description": "Remove a container from the grid",
        "parameters": {
            "type": "object",
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "ID of the container to remove"
                }
            },
            "required": ["container_id"]
        }
    },
    {
        "name": "clear_grid",
        "description": "Clear all containers from the grid",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "resize_container",
        "description": "Resize a container in the grid",
        "parameters": {
            "type": "object",
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "ID of the container to resize"
                },
                "size_ratio": {
                    "type": "number",
                    "description": "New size ratio",
                    "minimum": 0.5,
                    "maximum": 2.0
                }
            },
            "required": ["container_id", "size_ratio"]
        }
    },
    {
        "name": "get_grid_status",
        "description": "Get current grid status and layout information",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "update_container_content",
        "description": "Update the content of a container (internal function, typically called automatically)",
        "parameters": {
            "type": "object",
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "ID of the container to update"
                },
                "content": {
                    "type": "object",
                    "description": "Content data"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["chart", "table", "text"],
                    "description": "Type of content"
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the container"
                }
            },
            "required": ["container_id", "content", "content_type"]
        }
    }
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_available_function_names() -> List[str]:
    """Get list of all available function names"""
    return list(AVAILABLE_FUNCTIONS.keys())

def get_function_by_name(function_name: str) -> Callable:
    """Get function object by name"""
    return AVAILABLE_FUNCTIONS.get(function_name)

def is_function_available(function_name: str) -> bool:
    """Check if a function is available"""
    return function_name in AVAILABLE_FUNCTIONS

def get_function_schema(function_name: str) -> Dict[str, Any]:
    """Get schema for a specific function"""
    for schema in FUNCTION_SCHEMAS:
        if schema["name"] == function_name:
            return schema
    return None

def get_functions_by_category() -> Dict[str, List[str]]:
    """Get functions organized by category"""
    return {
        "data_analysis": [
            "load_sample_data", "get_current_data_info", "filter_data", 
            "group_data", "sort_data", "calculate_statistics", "get_data_sample"
        ],
        "visualization": [
            "create_line_chart", "create_bar_chart", "create_scatter_plot", 
            "create_histogram", "create_data_table"
        ],
        "grid_management": [
            "add_container", "remove_container", "clear_grid", 
            "resize_container", "get_grid_status", "update_container_content"
        ]
    }

# ============================================================================
# REGISTRY INFO
# ============================================================================

def print_registry_info():
    """Print information about the function registry"""
    print("🔧 AI DATA ANALYST FUNCTION REGISTRY")
    print("=" * 60)
    print(f"Total functions available: {len(AVAILABLE_FUNCTIONS)}")
    
    categories = get_functions_by_category()
    for category, functions in categories.items():
        print(f"\n📋 {category.replace('_', ' ').title()} Functions ({len(functions)}):")
        for func_name in functions:
            func = AVAILABLE_FUNCTIONS[func_name]
            description = func.__doc__.split('\n')[1].strip() if func.__doc__ else "No description"
            print(f"  • {func_name}: {description}")
    
    print("\n" + "=" * 60)
    print("🚀 Ready for AI-powered data analysis!")

if __name__ == "__main__":
    print_registry_info() 