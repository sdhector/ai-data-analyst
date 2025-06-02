"""
Data Analysis Functions

This module contains all data analysis and manipulation functions
that the AI can call to work with datasets.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union
import json

# Global data storage (in production, this would be managed by a proper data manager)
_current_dataset = None
_dataset_metadata = {}

def load_sample_data(dataset_name: str) -> Dict[str, Any]:
    """
    Load a built-in sample dataset
    
    Args:
        dataset_name: Name of the dataset to load
        
    Returns:
        Dictionary with dataset information and status
    """
    global _current_dataset, _dataset_metadata
    
    try:
        # Define available sample datasets
        sample_datasets = {
            "sales": {
                "description": "Sample sales data with dates, regions, products, and amounts",
                "data": pd.DataFrame({
                    'Date': pd.date_range('2023-01-01', periods=100, freq='D'),
                    'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
                    'Product': np.random.choice(['Product A', 'Product B', 'Product C'], 100),
                    'Sales_Amount': np.random.normal(1000, 300, 100).round(2),
                    'Units_Sold': np.random.randint(1, 50, 100),
                    'Customer_ID': np.random.randint(1000, 9999, 100)
                })
            },
            "employees": {
                "description": "Employee data with departments, salaries, and performance metrics",
                "data": pd.DataFrame({
                    'Employee_ID': range(1, 51),
                    'Name': [f'Employee_{i}' for i in range(1, 51)],
                    'Department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR'], 50),
                    'Salary': np.random.normal(75000, 20000, 50).round(0),
                    'Years_Experience': np.random.randint(1, 15, 50),
                    'Performance_Score': np.random.uniform(3.0, 5.0, 50).round(1),
                    'Age': np.random.randint(22, 65, 50)
                })
            },
            "stocks": {
                "description": "Stock price data with multiple companies over time",
                "data": pd.DataFrame({
                    'Date': pd.date_range('2023-01-01', periods=252, freq='D'),
                    'Company': np.tile(['AAPL', 'GOOGL', 'MSFT', 'TSLA'], 63),
                    'Price': np.random.normal(150, 30, 252).round(2),
                    'Volume': np.random.randint(1000000, 10000000, 252),
                    'Market_Cap': np.random.normal(2000000000, 500000000, 252).round(0)
                })
            }
        }
        
        if dataset_name not in sample_datasets:
            return {
                "status": "error",
                "error": f"Dataset '{dataset_name}' not found",
                "available_datasets": list(sample_datasets.keys())
            }
        
        dataset_info = sample_datasets[dataset_name]
        _current_dataset = dataset_info["data"].copy()
        _dataset_metadata = {
            "name": dataset_name,
            "description": dataset_info["description"],
            "shape": _current_dataset.shape,
            "columns": _current_dataset.columns.tolist(),
            "dtypes": _current_dataset.dtypes.to_dict()
        }
        
        return {
            "status": "success",
            "result": {
                "dataset_name": dataset_name,
                "description": dataset_info["description"],
                "shape": _current_dataset.shape,
                "columns": _current_dataset.columns.tolist(),
                "sample_data": _current_dataset.head().to_dict('records'),
                "data_types": {col: str(dtype) for col, dtype in _current_dataset.dtypes.items()}
            },
            "metadata": _dataset_metadata
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error loading dataset: {str(e)}",
            "function_name": "load_sample_data"
        }

def get_current_data_info() -> Dict[str, Any]:
    """
    Get information about the currently loaded dataset
    
    Returns:
        Dictionary with current dataset information
    """
    global _current_dataset, _dataset_metadata
    
    try:
        if _current_dataset is None:
            return {
                "status": "error",
                "error": "No dataset currently loaded. Use load_sample_data() first."
            }
        
        return {
            "status": "success",
            "result": {
                "dataset_info": _dataset_metadata,
                "shape": _current_dataset.shape,
                "columns": _current_dataset.columns.tolist(),
                "memory_usage": f"{_current_dataset.memory_usage(deep=True).sum() / 1024:.1f} KB",
                "null_counts": _current_dataset.isnull().sum().to_dict()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error getting data info: {str(e)}",
            "function_name": "get_current_data_info"
        }

def filter_data(column: str, operator: str, value: Union[str, int, float]) -> Dict[str, Any]:
    """
    Filter the current dataset based on a condition
    
    Args:
        column: Column name to filter on
        operator: Comparison operator ('==', '!=', '>', '<', '>=', '<=', 'contains')
        value: Value to compare against
        
    Returns:
        Dictionary with filtered data information
    """
    global _current_dataset
    
    try:
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
        
        # Apply filter based on operator
        if operator == '==':
            filtered_data = _current_dataset[_current_dataset[column] == value]
        elif operator == '!=':
            filtered_data = _current_dataset[_current_dataset[column] != value]
        elif operator == '>':
            filtered_data = _current_dataset[_current_dataset[column] > value]
        elif operator == '<':
            filtered_data = _current_dataset[_current_dataset[column] < value]
        elif operator == '>=':
            filtered_data = _current_dataset[_current_dataset[column] >= value]
        elif operator == '<=':
            filtered_data = _current_dataset[_current_dataset[column] <= value]
        elif operator == 'contains':
            if _current_dataset[column].dtype == 'object':
                filtered_data = _current_dataset[_current_dataset[column].str.contains(str(value), na=False)]
            else:
                return {
                    "status": "error",
                    "error": f"'contains' operator only works with text columns"
                }
        else:
            return {
                "status": "error",
                "error": f"Unsupported operator: {operator}",
                "supported_operators": ['==', '!=', '>', '<', '>=', '<=', 'contains']
            }
        
        # Update current dataset with filtered data
        _current_dataset = filtered_data.copy()
        
        return {
            "status": "success",
            "result": {
                "filter_applied": f"{column} {operator} {value}",
                "rows_remaining": len(filtered_data),
                "rows_filtered_out": len(_current_dataset) - len(filtered_data) if len(_current_dataset) > len(filtered_data) else 0,
                "sample_data": filtered_data.head().to_dict('records') if len(filtered_data) > 0 else []
            },
            "metadata": {
                "shape": filtered_data.shape,
                "filter_condition": f"{column} {operator} {value}"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error filtering data: {str(e)}",
            "function_name": "filter_data"
        }

def group_data(column: str, aggregation: str) -> Dict[str, Any]:
    """
    Group data by a column and apply aggregation
    
    Args:
        column: Column to group by
        aggregation: Aggregation function ('count', 'sum', 'mean', 'median', 'min', 'max')
        
    Returns:
        Dictionary with grouped data results
    """
    global _current_dataset
    
    try:
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
        
        # Apply grouping and aggregation
        if aggregation == 'count':
            grouped_data = _current_dataset.groupby(column).size().reset_index(name='count')
        elif aggregation in ['sum', 'mean', 'median', 'min', 'max']:
            # Get numeric columns for aggregation
            numeric_columns = _current_dataset.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_columns:
                return {
                    "status": "error",
                    "error": "No numeric columns found for aggregation"
                }
            
            grouped_data = _current_dataset.groupby(column)[numeric_columns].agg(aggregation).reset_index()
        else:
            return {
                "status": "error",
                "error": f"Unsupported aggregation: {aggregation}",
                "supported_aggregations": ['count', 'sum', 'mean', 'median', 'min', 'max']
            }
        
        return {
            "status": "success",
            "result": {
                "grouped_by": column,
                "aggregation": aggregation,
                "groups_count": len(grouped_data),
                "grouped_data": grouped_data.to_dict('records'),
                "summary": f"Grouped by {column} with {aggregation} aggregation"
            },
            "metadata": {
                "original_shape": _current_dataset.shape,
                "grouped_shape": grouped_data.shape
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error grouping data: {str(e)}",
            "function_name": "group_data"
        }

def sort_data(column: str, ascending: bool = True) -> Dict[str, Any]:
    """
    Sort the current dataset by a column
    
    Args:
        column: Column to sort by
        ascending: Sort in ascending order (True) or descending (False)
        
    Returns:
        Dictionary with sorted data information
    """
    global _current_dataset
    
    try:
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
        
        # Sort the data
        _current_dataset = _current_dataset.sort_values(by=column, ascending=ascending).reset_index(drop=True)
        
        return {
            "status": "success",
            "result": {
                "sorted_by": column,
                "ascending": ascending,
                "total_rows": len(_current_dataset),
                "sample_data": _current_dataset.head().to_dict('records')
            },
            "metadata": {
                "sort_column": column,
                "sort_order": "ascending" if ascending else "descending"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error sorting data: {str(e)}",
            "function_name": "sort_data"
        }

def calculate_statistics(columns: List[str] = None) -> Dict[str, Any]:
    """
    Calculate descriptive statistics for specified columns or all numeric columns
    
    Args:
        columns: List of column names to analyze (None for all numeric columns)
        
    Returns:
        Dictionary with statistical analysis results
    """
    global _current_dataset
    
    try:
        if _current_dataset is None:
            return {
                "status": "error",
                "error": "No dataset currently loaded. Use load_sample_data() first."
            }
        
        # Determine which columns to analyze
        if columns is None:
            # Use all numeric columns
            numeric_columns = _current_dataset.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_columns:
                return {
                    "status": "error",
                    "error": "No numeric columns found in dataset"
                }
            columns = numeric_columns
        else:
            # Validate specified columns exist
            missing_columns = [col for col in columns if col not in _current_dataset.columns]
            if missing_columns:
                return {
                    "status": "error",
                    "error": f"Columns not found: {missing_columns}",
                    "available_columns": _current_dataset.columns.tolist()
                }
        
        # Calculate statistics
        stats_data = _current_dataset[columns].describe()
        
        # Convert to a more readable format
        statistics = {}
        for column in columns:
            if _current_dataset[column].dtype in [np.number, 'int64', 'float64']:
                statistics[column] = {
                    "count": int(stats_data.loc['count', column]),
                    "mean": float(stats_data.loc['mean', column]),
                    "std": float(stats_data.loc['std', column]),
                    "min": float(stats_data.loc['min', column]),
                    "25%": float(stats_data.loc['25%', column]),
                    "50%": float(stats_data.loc['50%', column]),
                    "75%": float(stats_data.loc['75%', column]),
                    "max": float(stats_data.loc['max', column])
                }
        
        return {
            "status": "success",
            "result": {
                "columns_analyzed": columns,
                "statistics": statistics,
                "summary": f"Statistical analysis completed for {len(columns)} columns"
            },
            "metadata": {
                "analysis_type": "descriptive_statistics",
                "columns_count": len(columns)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error calculating statistics: {str(e)}",
            "function_name": "calculate_statistics"
        }

def get_data_sample(n_rows: int = 10) -> Dict[str, Any]:
    """
    Get a sample of the current dataset
    
    Args:
        n_rows: Number of rows to return
        
    Returns:
        Dictionary with sample data
    """
    global _current_dataset
    
    try:
        if _current_dataset is None:
            return {
                "status": "error",
                "error": "No dataset currently loaded. Use load_sample_data() first."
            }
        
        sample_data = _current_dataset.head(n_rows)
        
        return {
            "status": "success",
            "result": {
                "sample_size": len(sample_data),
                "total_rows": len(_current_dataset),
                "sample_data": sample_data.to_dict('records'),
                "columns": _current_dataset.columns.tolist()
            },
            "metadata": {
                "requested_rows": n_rows,
                "returned_rows": len(sample_data)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error getting data sample: {str(e)}",
            "function_name": "get_data_sample"
        } 