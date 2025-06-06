"""
Core New - Redesigned Function Architecture

This module implements the new modular architecture with separated concerns:
- Primitives: Core atomic operations
- Utilities: Shared functionality and algorithms  
- Guardrails: Security and validation mechanisms
- Tools: High-level LLM-accessible operations
- Registry: Tool registration and schema management
"""

__version__ = "0.1.0"
__author__ = "AI Data Analyst Team"

# Import main components for easy access
from . import primitives
from . import utilities
from . import guardrails
from . import tools
from . import registry

__all__ = [
    "primitives",
    "utilities", 
    "guardrails",
    "tools",
    "registry"
] 