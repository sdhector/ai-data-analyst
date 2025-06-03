"""
Visualization Functions

This module contains all visualization creation functions that generate
framework-agnostic chart configurations using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union
import logging

# Setup logger
logger = logging.getLogger(__name__)

def _serialize_dataframe_for_table(df: pd.DataFrame) -> List[Dict]:
    """
    Serialize a DataFrame for table display with JSON-compatible format
    
    Args:
        df: DataFrame to serialize
        
    Returns:
        List of dictionaries with JSON-serializable values
    """
    df_copy = df.copy()
    
    # Convert datetime columns to strings
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        elif pd.api.types.is_timedelta64_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].astype(str)
    
    # Convert to records and ensure all values are JSON serializable
    records = []
    for _, row in df_copy.iterrows():
        record = {}
        for col, value in row.items():
            if pd.isna(value):
                record[col] = None
            elif isinstance(value, (np.integer, np.floating)):
                record[col] = float(value) if isinstance(value, np.floating) else int(value)
            elif isinstance(value, np.bool_):
                record[col] = bool(value)
            else:
                record[col] = str(value)
        records.append(record)
    
    return records

def _convert_numpy_to_list_recursive(item: Any) -> Any:
    """
    Recursively convert numpy arrays to lists within nested data structures.

    Args:
        item: The item to process.

    Returns:
        The processed item with numpy arrays converted to lists.
    """
    if isinstance(item, np.ndarray):
        return item.tolist()
    if isinstance(item, dict):
        return {k: _convert_numpy_to_list_recursive(v) for k, v in item.items()}
    if isinstance(item, list):
        return [_convert_numpy_to_list_recursive(elem) for elem in item]
    return item

def create_line_chart(container_id: str, x_col: str, y_col: str, title: str = "", 
                     color_col: str = None) -> Dict[str, Any]:
    """
    Create a line chart configuration
    
    Args:
        container_id: ID of the container to place the chart
        x_col: Column name for x-axis
        y_col: Column name for y-axis  
        title: Chart title
        color_col: Optional column for color grouping
        
    Returns:
        Dictionary with chart configuration
    """
    try:
        # Import current dataset from data_analysis_functions
        from .data_analysis_functions import _current_dataset
        
        if _current_dataset is None:
            return {
                "status": "error",
                "error": "No dataset currently loaded. Use load_sample_data() first."
            }
        
        # Validate columns exist
        required_cols = [x_col, y_col]
        if color_col:
            required_cols.append(color_col)
            
        missing_cols = [col for col in required_cols if col not in _current_dataset.columns]
        if missing_cols:
            return {
                "status": "error",
                "error": f"Columns not found: {missing_cols}",
                "available_columns": _current_dataset.columns.tolist()
            }
        
        # Create the chart
        if color_col:
            fig = px.line(_current_dataset, x=x_col, y=y_col, color=color_col, title=title)
        else:
            fig = px.line(_current_dataset, x=x_col, y=y_col, title=title)
        
        # Update layout for better appearance
        fig.update_layout(
            title_font_size=16,
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode='x unified'
        )
        
        return {
            "status": "success",
            "result": {
                "chart_type": "line_chart",
                "container_id": container_id,
                "chart_config": _convert_numpy_to_list_recursive(fig.to_dict()),
                "data_points": len(_current_dataset),
                "x_column": x_col,
                "y_column": y_col,
                "color_column": color_col,
                "title": title
            },
            "metadata": {
                "chart_library": "plotly",
                "interactive": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating line chart for x_col='{x_col}', y_col='{y_col}', color_col='{color_col}': {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Error creating line chart: {str(e)}",
            "function_name": "create_line_chart"
        }

def create_bar_chart(container_id: str, x_col: str, y_col: str, title: str = "",
                    color_col: str = None) -> Dict[str, Any]:
    """
    Create a bar chart configuration
    
    Args:
        container_id: ID of the container to place the chart
        x_col: Column name for x-axis (categories)
        y_col: Column name for y-axis (values)
        title: Chart title
        color_col: Optional column for color grouping
        
    Returns:
        Dictionary with chart configuration
    """
    try:
        from .data_analysis_functions import _current_dataset
        
        if _current_dataset is None:
            return {
                "status": "error",
                "error": "No dataset currently loaded. Use load_sample_data() first."
            }
        
        # Validate columns exist
        required_cols = [x_col, y_col]
        if color_col:
            required_cols.append(color_col)
            
        missing_cols = [col for col in required_cols if col not in _current_dataset.columns]
        if missing_cols:
            return {
                "status": "error",
                "error": f"Columns not found: {missing_cols}",
                "available_columns": _current_dataset.columns.tolist()
            }
        
        # Create the chart
        if color_col:
            fig = px.bar(_current_dataset, x=x_col, y=y_col, color=color_col, title=title)
        else:
            fig = px.bar(_current_dataset, x=x_col, y=y_col, title=title)
        
        # Update layout
        fig.update_layout(
            title_font_size=16,
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=bool(color_col)
        )
        
        return {
            "status": "success",
            "result": {
                "chart_type": "bar_chart",
                "container_id": container_id,
                "chart_config": _convert_numpy_to_list_recursive(fig.to_dict()),
                "data_points": len(_current_dataset),
                "x_column": x_col,
                "y_column": y_col,
                "color_column": color_col,
                "title": title
            },
            "metadata": {
                "chart_library": "plotly",
                "interactive": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating bar chart for x_col='{x_col}', y_col='{y_col}', color_col='{color_col}': {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Error creating bar chart: {str(e)}",
            "function_name": "create_bar_chart"
        }

def create_scatter_plot(container_id: str, x_col: str, y_col: str, title: str = "",
                       color_col: str = None, size_col: str = None) -> Dict[str, Any]:
    """
    Create a scatter plot configuration
    
    Args:
        container_id: ID of the container to place the chart
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
        color_col: Optional column for color mapping
        size_col: Optional column for size mapping
        
    Returns:
        Dictionary with chart configuration
    """
    try:
        from .data_analysis_functions import _current_dataset
        
        if _current_dataset is None:
            return {
                "status": "error",
                "error": "No dataset currently loaded. Use load_sample_data() first."
            }
        
        # Validate columns exist
        required_cols = [x_col, y_col]
        if color_col:
            required_cols.append(color_col)
        if size_col:
            required_cols.append(size_col)
            
        missing_cols = [col for col in required_cols if col not in _current_dataset.columns]
        if missing_cols:
            return {
                "status": "error",
                "error": f"Columns not found: {missing_cols}",
                "available_columns": _current_dataset.columns.tolist()
            }
        
        # Create the chart
        fig = px.scatter(_current_dataset, x=x_col, y=y_col, color=color_col, 
                        size=size_col, title=title)
        
        # Update layout
        fig.update_layout(
            title_font_size=16,
            xaxis_title=x_col,
            yaxis_title=y_col
        )
        
        return {
            "status": "success",
            "result": {
                "chart_type": "scatter_plot",
                "container_id": container_id,
                "chart_config": _convert_numpy_to_list_recursive(fig.to_dict()),
                "data_points": len(_current_dataset),
                "x_column": x_col,
                "y_column": y_col,
                "color_column": color_col,
                "size_column": size_col,
                "title": title
            },
            "metadata": {
                "chart_library": "plotly",
                "interactive": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating scatter plot for x_col='{x_col}', y_col='{y_col}', color_col='{color_col}', size_col='{size_col}': {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Error creating scatter plot: {str(e)}",
            "function_name": "create_scatter_plot"
        }

def create_histogram(container_id: str, column: str, bins: int = 20, title: str = "") -> Dict[str, Any]:
    """
    Create a histogram configuration
    
    Args:
        container_id: ID of the container to place the chart
        column: Column name for the histogram
        bins: Number of bins
        title: Chart title
        
    Returns:
        Dictionary with chart configuration
    """
    try:
        from .data_analysis_functions import _current_dataset
        
        if _current_dataset is None:
            return {
                "status": "error",
                "error": "No dataset currently loaded. Use load_sample_data() first."
            }
        
        if column not in _current_dataset.columns:
            return {
                "status": "error",
                "error": f"Column '{column}' not found in dataset",
                "available_columns": _current_dataset.columns.tolist()
            }
        
        # Check if column is numeric
        if not pd.api.types.is_numeric_dtype(_current_dataset[column]):
            return {
                "status": "error",
                "error": f"Column '{column}' must be numeric for histogram"
            }
        
        # Create the chart
        fig = px.histogram(_current_dataset, x=column, nbins=bins, title=title)
        
        # Update layout
        fig.update_layout(
            title_font_size=16,
            xaxis_title=column,
            yaxis_title="Count",
            bargap=0.1
        )
        
        return {
            "status": "success",
            "result": {
                "chart_type": "histogram",
                "container_id": container_id,
                "chart_config": _convert_numpy_to_list_recursive(fig.to_dict()),
                "data_points": len(_current_dataset),
                "column": column,
                "bins": bins,
                "title": title
            },
            "metadata": {
                "chart_library": "plotly",
                "interactive": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating histogram for column='{column}', bins={bins}: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Error creating histogram: {str(e)}",
            "function_name": "create_histogram"
        }

def create_data_table(container_id: str, columns: List[str] = None, max_rows: int = 100) -> Dict[str, Any]:
    """
    Create a data table configuration
    
    Args:
        container_id: ID of the container to place the table
        columns: List of columns to include (None for all columns)
        max_rows: Maximum number of rows to display
        
    Returns:
        Dictionary with table configuration
    """
    try:
        from .data_analysis_functions import _current_dataset
        
        if _current_dataset is None:
            return {
                "status": "error",
                "error": "No dataset currently loaded. Use load_sample_data() first."
            }
        
        # Determine which columns to include
        if columns is None:
            columns = _current_dataset.columns.tolist()
        else:
            # Validate specified columns exist
            missing_columns = [col for col in columns if col not in _current_dataset.columns]
            if missing_columns:
                return {
                    "status": "error",
                    "error": f"Columns not found: {missing_columns}",
                    "available_columns": _current_dataset.columns.tolist()
                }
        
        # Get the data subset
        table_data = _current_dataset[columns].head(max_rows)
        
        return {
            "status": "success",
            "result": {
                "chart_type": "data_table",
                "container_id": container_id,
                "table_data": _serialize_dataframe_for_table(table_data),
                "columns": columns,
                "total_rows": len(_current_dataset),
                "displayed_rows": len(table_data),
                "column_types": {col: str(_current_dataset[col].dtype) for col in columns}
            },
            "metadata": {
                "table_type": "data_table",
                "interactive": True,
                "max_rows": max_rows
            }
        }
        
    except Exception as e:
        columns_str = str(columns) if columns is not None else "all"
        logger.error(f"Error creating data table for columns='{columns_str}', max_rows={max_rows}: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Error creating data table: {str(e)}",
            "function_name": "create_data_table"
        } 