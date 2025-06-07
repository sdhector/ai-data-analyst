# Core New - Redesigned Function Architecture

This directory contains the redesigned function architecture that separates concerns into distinct, modular layers for better maintainability, security, and extensibility.

## Architecture Overview

The new architecture follows a layered approach with clear separation of responsibilities:

```
core_new/
├── primitives/     # Core atomic operations
├── utilities/      # Shared functionality and algorithms
├── guardrails/     # Security and validation mechanisms
├── tools/          # High-level LLM-accessible operations
└── registry/       # Tool registration and schema management
```

## Design Principles

### 1. **Separation of Concerns**
- Each layer has a specific responsibility
- No cross-layer dependencies except in defined directions
- Clear interfaces between layers

### 2. **Modularity**
- Functions are atomic and focused
- Easy to test, maintain, and extend
- Reusable components across different tools

### 3. **Security by Design**
- Guardrails provide validation and safety checks
- Primitive functions are isolated from direct AI access
- Multiple validation layers prevent harmful operations

### 4. **Extensibility**
- New tools can be added without modifying existing code
- Registry system enables dynamic tool discovery
- Utilities provide common functionality for new features

## Layer Descriptions

### Primitives
Core atomic operations that directly manipulate canvas state. These functions:
- Have single responsibility
- Perform no validation or optimization
- Interact directly with canvas_bridge
- Are not exposed to AI directly

### Utilities
Shared functionality and algorithms used by multiple tools:
- Layout optimization algorithms
- Data transformation utilities
- Common validation helpers
- Mathematical calculations

### Guardrails
Security and validation mechanisms:
- Input validation and sanitization
- Rate limiting and permission checks
- Safety constraints and bounds checking
- Error prevention and recovery

### Tools
High-level operations exposed to the AI:
- Orchestrate primitives, utilities, and guardrails
- Provide AI-friendly interfaces
- Handle complex workflows
- Generate rich response formatting

### Registry
Tool registration and schema management:
- Dynamic tool discovery
- OpenAI function schema generation
- Tool metadata and documentation
- Version management and compatibility

## Implementation Status

- ✅ **Primitives**: Fully implemented with container, canvas, and state operations
- 🚧 **Utilities**: Placeholder - to be implemented
- 🚧 **Guardrails**: Placeholder - to be implemented  
- 🚧 **Tools**: Placeholder - to be implemented
- 🚧 **Registry**: Placeholder - to be implemented

## Usage Guidelines

1. **For Developers**: Use tools layer for AI interactions, never expose primitives directly
2. **For AI Integration**: Only access functions through the tools layer
3. **For Testing**: Test each layer independently with appropriate mocks
4. **For Extensions**: Follow the established patterns and layer responsibilities

## Migration Path

This new architecture will gradually replace the existing monolithic function executor while maintaining backward compatibility during the transition period.

## Documentation

Each subdirectory contains its own README.md with detailed information about that layer's implementation, patterns, and usage guidelines. 