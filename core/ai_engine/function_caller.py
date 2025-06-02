"""
Function Caller

This module orchestrates the function calling workflow for the AI Data Analyst.
It integrates with the function registry and handles automatic container management.
"""

import json
from typing import Dict, Any, List, Optional
from ..function_registry import FunctionExecutor, AVAILABLE_FUNCTIONS, FUNCTION_SCHEMAS
from ..function_registry.grid_management_functions import add_container, update_container_content

class FunctionCaller:
    """
    Orchestrates function calling workflow with automatic container management
    """
    
    def __init__(self):
        """Initialize the function caller with the function registry"""
        self.function_executor = FunctionExecutor(AVAILABLE_FUNCTIONS, FUNCTION_SCHEMAS)
        
    def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call with enhanced logic for visualization functions
        
        Args:
            function_name: Name of the function to execute
            arguments: Arguments for the function
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Handle automatic container creation for visualization functions
            if self._is_visualization_function(function_name):
                container_result = self._handle_container_for_visualization(arguments)
                if container_result["status"] == "error":
                    return container_result
                
                # Update arguments with actual container ID
                if "container_id" in container_result:
                    arguments["container_id"] = container_result["container_id"]
            
            # Execute the function
            result = self.function_executor.execute_function_call(function_name, arguments)
            
            # Post-process visualization results
            if self._is_visualization_function(function_name) and result["status"] == "success":
                result = self._post_process_visualization_result(result, function_name)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error in function caller: {str(e)}",
                "function_name": function_name,
                "arguments": arguments
            }
    
    def execute_multiple_functions(self, function_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple function calls in sequence
        
        Args:
            function_calls: List of function call dictionaries with 'name' and 'arguments'
            
        Returns:
            List of execution results
        """
        results = []
        
        for call in function_calls:
            function_name = call.get("name")
            arguments = call.get("arguments", {})
            
            if not function_name:
                results.append({
                    "status": "error",
                    "error": "Function name is required",
                    "call": call
                })
                continue
            
            result = self.execute_function_call(function_name, arguments)
            results.append(result)
            
            # Stop execution if there's an error (unless it's a non-critical error)
            if result["status"] == "error" and not self._is_non_critical_error(result):
                break
        
        return results
    
    def _is_visualization_function(self, function_name: str) -> bool:
        """Check if a function is a visualization function"""
        visualization_functions = [
            "create_line_chart", "create_bar_chart", "create_scatter_plot", 
            "create_histogram", "create_data_table"
        ]
        return function_name in visualization_functions
    
    def _handle_container_for_visualization(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle container creation/management for visualization functions
        
        Args:
            arguments: Function arguments
            
        Returns:
            Dictionary with container handling results
        """
        container_id = arguments.get("container_id", "auto")
        
        if container_id == "auto":
            # Automatically create a new container
            container_result = add_container()
            
            if container_result["status"] == "success":
                return {
                    "status": "success",
                    "container_id": container_result["result"]["container_id"],
                    "message": f"Created new container at position {container_result['result']['position']}"
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to create container: {container_result.get('error', 'Unknown error')}"
                }
        else:
            # Use provided container ID
            return {
                "status": "success",
                "container_id": container_id,
                "message": f"Using existing container: {container_id}"
            }
    
    def _post_process_visualization_result(self, result: Dict[str, Any], function_name: str) -> Dict[str, Any]:
        """
        Post-process visualization results to update container content
        
        Args:
            result: Function execution result
            function_name: Name of the visualization function
            
        Returns:
            Enhanced result with container update information
        """
        try:
            if result["status"] != "success":
                return result
            
            function_result = result["result"]
            container_id = function_result.get("container_id")
            
            if not container_id:
                return result
            
            # Determine content type
            content_type = "chart" if function_name != "create_data_table" else "table"
            
            # Update container content
            update_result = update_container_content(
                container_id=container_id,
                content=function_result,
                content_type=content_type,
                title=function_result.get("title", f"{function_name.replace('_', ' ').title()}")
            )
            
            # Add container update info to result
            result["container_update"] = update_result
            
            return result
            
        except Exception as e:
            # Don't fail the main function if container update fails
            result["container_update"] = {
                "status": "error",
                "error": f"Failed to update container: {str(e)}"
            }
            return result
    
    def _is_non_critical_error(self, result: Dict[str, Any]) -> bool:
        """
        Check if an error is non-critical and execution should continue
        
        Args:
            result: Function execution result
            
        Returns:
            True if error is non-critical
        """
        error_message = result.get("error", "").lower()
        
        # Define non-critical error patterns
        non_critical_patterns = [
            "container not found",
            "grid full",
            "position already occupied"
        ]
        
        return any(pattern in error_message for pattern in non_critical_patterns)
    
    def get_available_functions(self) -> List[str]:
        """Get list of available function names"""
        return self.function_executor.get_available_functions()
    
    def get_function_schemas(self) -> List[Dict]:
        """Get function schemas for LLM"""
        return self.function_executor.get_function_schemas()
    
    def validate_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a function call without executing it
        
        Args:
            function_name: Name of the function
            arguments: Function arguments
            
        Returns:
            Validation result
        """
        try:
            # Check if function exists
            if not self.function_executor.is_function_available(function_name):
                return {
                    "status": "error",
                    "error": f"Function '{function_name}' not available",
                    "available_functions": self.get_available_functions()
                }
            
            # Get function schema for validation
            schema = None
            for s in self.get_function_schemas():
                if s["name"] == function_name:
                    schema = s
                    break
            
            if not schema:
                return {
                    "status": "error",
                    "error": f"Schema not found for function '{function_name}'"
                }
            
            # Basic validation of required parameters
            required_params = schema.get("parameters", {}).get("required", [])
            missing_params = [param for param in required_params if param not in arguments]
            
            if missing_params:
                return {
                    "status": "error",
                    "error": f"Missing required parameters: {missing_params}",
                    "required_parameters": required_params
                }
            
            return {
                "status": "success",
                "message": f"Function call '{function_name}' is valid",
                "function_name": function_name,
                "arguments": arguments
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Validation error: {str(e)}",
                "function_name": function_name
            }
    
    def get_function_help(self, function_name: str = None) -> Dict[str, Any]:
        """
        Get help information for functions
        
        Args:
            function_name: Specific function name (None for all functions)
            
        Returns:
            Help information
        """
        try:
            if function_name:
                # Get help for specific function
                if not self.function_executor.is_function_available(function_name):
                    return {
                        "status": "error",
                        "error": f"Function '{function_name}' not found"
                    }
                
                schema = None
                for s in self.get_function_schemas():
                    if s["name"] == function_name:
                        schema = s
                        break
                
                return {
                    "status": "success",
                    "function_name": function_name,
                    "description": schema.get("description", "No description available"),
                    "parameters": schema.get("parameters", {}),
                    "schema": schema
                }
            else:
                # Get help for all functions
                functions_help = {}
                for schema in self.get_function_schemas():
                    functions_help[schema["name"]] = {
                        "description": schema.get("description", "No description available"),
                        "parameters": schema.get("parameters", {})
                    }
                
                return {
                    "status": "success",
                    "total_functions": len(functions_help),
                    "functions": functions_help
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error getting function help: {str(e)}"
            } 