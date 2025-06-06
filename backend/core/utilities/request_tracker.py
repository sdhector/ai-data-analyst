"""
Request Tracking Utility

Provides request ID generation and context management for tracing execution flows.
Each user message gets a unique request ID that propagates through all components.
"""

import uuid
import logging
import os
from datetime import datetime
from typing import Optional
# Global variable to store the current request ID (thread-safe for single-threaded async)
_current_request_id: Optional[str] = None

class RequestTracker:
    """Manages request IDs and provides logging utilities"""
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate a new unique request ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"req_{timestamp}_{short_uuid}"
    
    @staticmethod
    def set_request_id(request_id: str) -> None:
        """Set the current request ID"""
        global _current_request_id
        _current_request_id = request_id
    
    @staticmethod
    def get_request_id() -> Optional[str]:
        """Get the current request ID"""
        return _current_request_id
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger that includes request ID in messages"""
        logger = logging.getLogger(name)
        
        # Add custom formatter that includes request ID
        if not logger.handlers:
            debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
            if debug_mode:
                handler = logging.StreamHandler()
                formatter = RequestFormatter()
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.DEBUG)
        
        return logger

class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request ID in log messages"""
    
    def format(self, record):
        request_id = _current_request_id
        if request_id:
            record.request_id = request_id
            format_string = '%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - %(message)s'
        else:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        formatter = logging.Formatter(format_string)
        return formatter.format(record)

def setup_file_logging():
    """Setup persistent file logging for requests"""
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    if debug_mode:
        try:
            # Create logs directory if it doesn't exist
            os.makedirs("logs", exist_ok=True)
            
            # Setup file handler for all requests
            file_handler = logging.FileHandler("logs/requests.log")
            file_formatter = RequestFormatter()
            file_handler.setFormatter(file_formatter)
            
            # Setup daily rotating file handler
            from logging.handlers import TimedRotatingFileHandler
            rotating_handler = TimedRotatingFileHandler(
                "logs/requests_daily.log",
                when="midnight",
                interval=1,
                backupCount=30
            )
            rotating_handler.setFormatter(file_formatter)
            
            # Add handlers to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)
            root_logger.addHandler(rotating_handler)
            root_logger.setLevel(logging.DEBUG)
            
            print("[DEBUG] File logging setup complete - logs will be saved to logs/ directory")
            
        except Exception as e:
            print(f"[ERROR] Failed to setup file logging: {e}")
            print("[DEBUG] Continuing without file logging...")

def log_request_start(request_id: str, user_message: str, conversation_id: Optional[str] = None):
    """Log the start of a new request"""
    logger = RequestTracker.get_logger("REQUEST_TRACKER")
    logger.info(f"🚀 REQUEST STARTED - Message: '{user_message}' | Conversation: {conversation_id}")

def log_request_end(request_id: str, success: bool, duration_ms: float):
    """Log the end of a request"""
    logger = RequestTracker.get_logger("REQUEST_TRACKER")
    status = "✅ SUCCESS" if success else "❌ FAILED"
    logger.info(f"🏁 REQUEST COMPLETED - {status} | Duration: {duration_ms:.2f}ms")

def log_component_entry(component: str, operation: str, details: str = ""):
    """Log entry into a component"""
    logger = RequestTracker.get_logger("REQUEST_TRACKER")
    logger.debug(f"➡️ {component} | {operation} | {details}")

def log_component_exit(component: str, operation: str, status: str, details: str = ""):
    """Log exit from a component"""
    logger = RequestTracker.get_logger("REQUEST_TRACKER")
    logger.debug(f"⬅️ {component} | {operation} | {status} | {details}")

def log_handover(from_component: str, to_component: str, operation: str, data: str = ""):
    """Log handover between components"""
    logger = RequestTracker.get_logger("REQUEST_TRACKER")
    logger.debug(f"🔄 HANDOVER: {from_component} → {to_component} | {operation} | {data}") 