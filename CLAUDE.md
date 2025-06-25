# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based mock API server that simulates streaming responses for search queries. It's designed to mimic real-world (Siemens PLM Teamcenter "Knowledge Base") search APIs with streaming capabilities, citations, and rating functionality.

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
Server runs on http://127.0.0.1:8000

### Code Quality
```bash
# Linting
flake8 main.py
pylint main.py

# Type checking
mypy main.py
```

### Testing
No test framework is currently configured - check with the user for testing requirements before adding tests.

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
- `requrements.txt`: Contains fastapi and uvicorn dependencies (note: filename has typo)

## API Endpoints

- `GET /stream`: Main streaming endpoint with parameters for search_query, sessionID, topNDocuments, llm, language, and subfolder
- `POST /add_rating`: Rating submission endpoint
- `GET /health`: Health check
- `GET /`: Mock login endpoint  
- `GET /home`: Mock home/redirect endpoint

## Code Style

- Line length: 140 characters (flake8/pylint)
- Snake case for functions/variables
- PascalCase for classes
- Comprehensive docstrings for all endpoints
- Type hints throughout