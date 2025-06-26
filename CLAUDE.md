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

### UV Package Management

The project uses UV for fast, reliable dependency management. No virtual environment setup needed!

### Installation

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (automatic)
uv sync
```

### Running the Server

```bash
uv run uvicorn main:app --reload
```

Server runs on <http://127.0.0.1:8000>

### Quick Commands

```bash
# Run any script with dependencies
uv run python script.py

# Run tests
uv run pytest tests/

# Start MCP server
uv run python basic_mcp_stdio.py
```

### Code Quality

```bash
# Linting (if flake8/pylint added to project)
uv run flake8 main.py
uv run pylint main.py

# Type checking (if mypy added to project)
uv run mypy main.py
```

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_teamcenter_mcp.py -v

# Quick migration test
uv run python test_uv_migration.py
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
- `pyproject.toml`: Modern Python project configuration with UV-managed dependencies (fastapi, uvicorn, fastmcp, httpx, pytest)

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
# Start all servers with UV in separate terminals:
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload  # Terminal 1
uv run python auto_openapi_mcp.py                             # Terminal 2 (optional)
uv run python basic_mcp_stdio.py                              # Terminal 3 (recommended)

## Code Style

- Line length: 140 characters (flake8/pylint)
- Snake case for functions/variables
- PascalCase for classes
- Comprehensive docstrings for all endpoints
- Type hints throughout

# important-instruction-reminders
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
NEVER sign commits with Claude authorship - use default git authorship only.
