# Project Context: Engram

## Purpose
Engram is a specialized neural architecture designed for localized "context awareness" in LLMs, using n-gram hashing and hyper-connection mechanisms.

## Tech Stack
- **Core Engine**: Python (PyTorch, SymPy, Transformers)
- **Agentic Framework**: OpenSpec (Specification-driven development)
- **Interoperability**: OpenResponses (Universal API schema)
- **Plugin System**: OpenCode (Local code execution)

## Project Conventions

### Code Style
- **Python**: PEP 8 compliant, heavy use of dataclasses for configuration.
- **Agent Docs**: OpenSpec markdown format (Requirements/Scenarios).

### Architecture Patterns
- **Neural Hashing**: Uses prime numbers and bitwise XOR for token hashing.
- **Hyper-connections**: Multi-group convolutional layers for branching hidden states.

## Domain Context
- The project aims to provide LLMs with long-term memory and context without traditional massive attention windows, using the Engram "memory" layer.

## Important Constraints
- **Local First**: All code should run on local hardware (or WSL) where possible.
- **Strict Specs**: All changes must be proposed via OpenSpec before implementation.

## External Dependencies
- LM Studio / GLM-4.7-Flash (as the primary reasoning engine).
