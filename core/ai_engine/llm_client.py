"""
LLM Client

This module provides a robust OpenAI API client with error handling,
retry logic, and configuration management.
"""

import os
import time
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import openai
from openai import OpenAI
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LLMClient:
    """
    OpenAI API client with enhanced error handling and configuration
    """
    
    def __init__(self, 
                 api_key: str = None,
                 model: str = None,
                 max_tokens: int = None,
                 temperature: float = 0.7):
        """
        Initialize the LLM client
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model: Model to use (default: gpt-3.5-turbo)
            max_tokens: Maximum tokens per response (default: 1000)
            temperature: Response creativity (0.0-1.0)
        """
        # Configuration
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = max_tokens or int(os.getenv("MAX_TOKENS", "1000").strip('"'))
        self.temperature = temperature
        
        # Validate API key
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Usage tracking
        self.total_tokens_used = 0
        self.request_count = 0
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       functions: List[Dict] = None,
                       function_call: str = "auto") -> Dict[str, Any]:
        """
        Create a chat completion with optional function calling
        
        Args:
            messages: List of conversation messages
            functions: List of available functions for function calling
            function_call: Function calling mode ("auto", "none", or specific function)
            
        Returns:
            Dictionary with response data and metadata
        """
        try:
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Add function calling if functions provided
            if functions:
                request_params["functions"] = functions
                request_params["function_call"] = function_call
            
            # Make API call with retry logic
            response = self._make_request_with_retry(request_params)
            
            # Extract response data
            choice = response.choices[0]
            message = choice.message
            
            # Track usage
            if hasattr(response, 'usage'):
                self.total_tokens_used += response.usage.total_tokens
            self.request_count += 1
            
            # Prepare result
            result = {
                "status": "success",
                "message": message,
                "content": message.content,
                "function_call": getattr(message, 'function_call', None),
                "finish_reason": choice.finish_reason,
                "usage": getattr(response, 'usage', None),
                "model": self.model
            }
            
            return result
            
        except Exception as e:
            logger.error(
                f"LLM chat completion failed for model {self.model}. Error: {str(e)}",
                exc_info=True
            )
            error_payload = {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "model": self.model
            }
            if isinstance(e, openai.APIError):
                if hasattr(e, 'http_status'): # For older versions of openai client, it might be e.status_code
                    error_payload["http_status"] = e.http_status
                elif hasattr(e, 'status_code'): # Fallback for some versions
                     error_payload["http_status"] = e.status_code
                if hasattr(e, 'code'):
                    error_payload["code"] = e.code
                if hasattr(e, 'param'):
                    error_payload["param"] = e.param
                # For openai client v1.x.x, request_id is typically on the response headers,
                # but some error objects might carry it directly or through the response attribute.
                if hasattr(e, 'request_id'): # Direct attribute first
                     error_payload["request_id"] = e.request_id
                elif hasattr(e, 'response') and hasattr(e.response, 'headers'):
                    error_payload["request_id"] = e.response.headers.get("x-request-id")

            return error_payload
    
    def _make_request_with_retry(self, request_params: Dict[str, Any]):
        """
        Make API request with retry logic
        
        Args:
            request_params: Parameters for the API request
            
        Returns:
            OpenAI response object
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(**request_params)
                return response
                
            except (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError, openai.APIError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    error_type = type(e).__name__
                    logger.warning(
                        f"{error_type} encountered. Waiting {wait_time:.2f}s "
                        f"before retry {attempt + 1}/{self.max_retries}. Error: {e}"
                    )
                    time.sleep(wait_time)
                    continue

            except Exception as e: # Catch any other exception that is not an OpenAI specific retryable error
                # For other errors, don't retry, raise immediately
                raise e
        
        # If we get here, all retries failed
        raise last_error
    
    def simple_chat(self, user_message: str, system_message: str = None) -> Dict[str, Any]:
        """
        Simple chat without function calling
        
        Args:
            user_message: User's message
            system_message: Optional system message
            
        Returns:
            Dictionary with response
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": user_message})
        
        return self.chat_completion(messages)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics
        
        Returns:
            Dictionary with usage information
        """
        return {
            "total_tokens_used": self.total_tokens_used,
            "request_count": self.request_count,
            "average_tokens_per_request": self.total_tokens_used / max(self.request_count, 1),
            "model": self.model,
            "estimated_cost_usd": self._estimate_cost()
        }
    
    def _estimate_cost(self) -> float:
        """
        Estimate cost based on token usage
        
        Returns:
            Estimated cost in USD
        """
        # Rough cost estimates (as of 2024)
        cost_per_1k_tokens = {
            "gpt-3.5-turbo": 0.002,
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01
        }
        
        rate = cost_per_1k_tokens.get(self.model, 0.002)
        return (self.total_tokens_used / 1000) * rate
    
    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.total_tokens_used = 0
        self.request_count = 0
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the OpenAI API connection
        
        Returns:
            Dictionary with connection test results
        """
        try:
            response = self.simple_chat("Hello", "You are a helpful assistant. Respond with just 'Hello!'")
            
            if response["status"] == "success":
                return {
                    "status": "success",
                    "message": "OpenAI API connection successful",
                    "model": self.model,
                    "response_content": response["content"]
                }
            else:
                return {
                    "status": "error",
                    "message": "OpenAI API connection failed",
                    "error": response.get("error", "Unknown error")
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": "OpenAI API connection failed",
                "error": str(e),
                "error_type": type(e).__name__
            } 