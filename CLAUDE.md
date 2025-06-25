# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based mock API server that simulates streaming responses for search queries. It's designed to mimic real-world (Siemens PLM Teamcenter "Knowledge Base") search APIs with streaming capabilities, citations, and rating functionality.

## Design Principles

- **Less is More**: Simplicity always wins over complexity. The most intelligent solutions are usually the simplest ones.
- Follow **Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away** advice by Antoine de Saint-Exupéry.
- **Defensive Programming**: Test everything, validate all assumptions, never rush implementation. Every query must be unit tested (before coding) and integration tested against localhost server (before documenting the API). Expect failures and plan for them!
- **Evals are tests for prompts**: Just as tests verify code, evals verify AI behavior. Write tests first, let them fail, then implement until they pass consistently (5+ runs for nondeterministic systems).
- **Tests are immutable**: Once written, tests define success. Implementation serves tests, not vice versa.

## Development Setup

### Virtual Environment

The project uses a Python virtual environment. Use these bash aliases (defined in ~/.bashrc):

```bash
mkv  # Create virtual environment (python -m venv venv)
va   # Activate virtual environment (source venv/bin/activate)  
vp   # Upgrade pip (pip install --upgrade pip)
```

### Installation

```bash
mkv                              # Create venv
va                               # Activate venv
vp                               # Upgrade pip
pip install -r requrements.txt  # Install dependencies (note: filename has typo)
```

### Running the Server

```bash
uvicorn main:app --reload
```

Server runs on <http://127.0.0.1:8000>

### Code Quality

```bash
# Linting
flake8 main.py
pylint main.py

# Type checking
mypy main.py
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_teamcenter_mcp.py -v

# Run with coverage (if installed)
pytest tests/ --cov=main --cov=basic_mcp --cov=auto_openapi_mcp
```

## API Architecture

The application consists of a single FastAPI module (`main.py`) with:

- **Streaming endpoint** (`/stream`): Main functionality that tokenizes search queries and streams responses with simulated citations
- **Rating endpoint** (`/add_rating`): Accepts user feedback for search queries
- **Health/utility endpoints**: Basic health check and mock login/home endpoints

### Key Components

- **Enums**: `LLMEnum` and `LanguageEnum` for parameter validation
- **Pydantic Models**: `RatingRequest` for request validation
- **Streaming Logic**: Token-based streaming with configurable citations and metadata

### Configuration Files

- `.flake8`: Line length 140, excludes common directories
- `.pylintrc`: Comprehensive linting configuration with 140 char line limit
- `mypy.ini`: Type checking with external library ignore rules
- `requrements.txt`: Contains fastapi, uvicorn, fastmcp, httpx, and pytest dependencies (note: filename has typo)

## API Endpoints

- `GET /stream`: Main streaming endpoint with parameters for search_query, sessionID, topNDocuments, llm, language, and subfolder
- `POST /add_rating`: Rating submission endpoint
- `GET /health`: Health check
- `GET /`: Mock login endpoint  
- `GET /home`: Mock home/redirect endpoint

## MCP Server Architecture

The repository includes two MCP (Model Context Protocol) server implementations:

### Files
- `basic_mcp.py`: Focused Teamcenter Knowledge Base MCP server (port 8002)
- `auto_openapi_mcp.py`: Universal auto-generated MCP server (port 8001)
- `tests/test_teamcenter_mcp.py`: Tests for focused MCP server
- `tests/test_auto_mcp.py`: Tests for auto-generated MCP server
- `tests/test_mcp_simple.py`: Basic MCP functionality tests

### Architecture Decision
Two-server approach chosen over in-process mounting:
- Port 8000: Original mock Teamcenter API
- Port 8001: Universal auto-generated MCP server  
- Port 8002: Focused Teamcenter MCP server

This separation provides better architecture (microservices), easier deployment to Azure App Service, and cleaner separation of concerns.

### Running MCP Servers
```bash
# Start all three servers in separate terminals:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload  # Terminal 1
python auto_openapi_mcp.py                             # Terminal 2 (optional)
python basic_mcp.py                                    # Terminal 3 (recommended)

## Code Style

- Line length: 140 characters (flake8/pylint)
- Snake case for functions/variables
- PascalCase for classes
- Comprehensive docstrings for all endpoints
- Type hints throughout
