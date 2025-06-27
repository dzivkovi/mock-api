# Mock API Server

This repository contains a mock API that simulates a streaming response for search queries. It's designed to mimic the behavior of a real API that might be used in a question-answering or search system.

## Features

- Streaming response for search queries
- Simulated response and citation data
- Configurable number of top documents (citations)
- MCP (Model Context Protocol) server integration
- Multiple MCP implementations: universal auto-generated and focused Teamcenter

## Installation

To install and run this mock API, follow these steps:

1. **Install UV** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository**

3. **Install dependencies and run**:

   ```bash
   # Install dependencies (automatic with UV)
   uv sync

   # Start the API server
   uv run uvicorn main:app --reload
   ```

   This will start the server on `http://127.0.0.1:8000`.

### Alternative: Quick Run (No Installation)

UV can handle everything automatically:

```bash
# Run directly without manual dependency management
uv run uvicorn main:app --reload
```

## API Documentation

Once running, view the interactive API documentation at:

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Usage

You can interact with the API using curl or any HTTP client. **Note: The streaming endpoint now requires authentication.**

1. **First, authenticate to get a session cookie**:

    ```bash
    curl -X POST "http://127.0.0.1:8000/api/login" \
        -H "Authorization: Bearer your-azure-ad-token" \
        -c cookies.txt
    ```

2. **Basic search query with authentication**:

    ```bash
    curl -X GET "http://127.0.0.1:8000/stream?search_query=meaning%20of%20life&topNDocuments=3" \
        -b cookies.txt \
        -H "accept: text/event-stream"
    ```

3. **Search query with more top documents**:

    ```bash
    curl -N "http://127.0.0.1:8000/stream?search_query=what%20is%20the%20meaning%20of%20life&topNDocuments=5" \
        -b cookies.txt
    ```

3. Rating endpoint:

    ```bash
    curl -X POST "http://127.0.0.1:8000/add_rating" \
        -H "Content-Type: application/json" \
        -d '{"chat_id":"123","search_query":"test","rating":5}'
    ```

### Parameters

- `search_query`: The search query (URL-encoded) - **Required**
- `topNDocuments`: The number of citation documents to return (default: 5)

### Authentication

The API now requires session-based authentication:

1. Obtain session cookie via `/api/login` with Azure AD Bearer token
2. Include session cookie in subsequent requests to `/stream`

### Response Format

The API returns a stream of data in the following format:

```log
data: {"type": "response", "data": "word"}
data: {"type": "citation", "data": "citation_id"}
```

- Response data contains individual words from the search query
- Citation data contains citation identifiers

## MCP Server Integration

This repository includes MCP (Model Context Protocol) servers that allow LLM clients to interact with the mock Teamcenter API:

### Available MCP Servers

1. **Focused Teamcenter MCP** (`basic_mcp.py`):
   - Single-purpose server for Teamcenter knowledge search
   - Runs on port 8002
   - Tool: `teamcenter_search` for knowledge base queries

2. **Universal Auto-Generated MCP** (`auto_openapi_mcp.py`):
   - Auto-generates MCP tools from any OpenAPI specification
   - Runs on port 8001
   - Demonstrates universal MCP capability

## Run with API server for full coverage

```bash
# Terminal 1: Main API
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Running MCP Servers

These are *normally* executed by your IDEs (like VScode GitHub Copilot or Continue.dev), but you can run them manually for testing:

```bash
# Terminal 2: Focused Teamcenter MCP
uv run python basic_mcp_stdio.py

# Terminal 3: Universal MCP (optional)
uv run python auto_openapi_mcp.py
```

### Testing MCP Integration

```bash
# Run only authentication tests (all pass)
uv run pytest tests/test_auth_flow.py -v

# Run only MCP STDIO tests (mostly pass)
uv run pytest tests/test_teamcenter_mcp_stdio.py -v
```

### IDE Integration

#### VS Code MCP Configuration

Add to `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "teamcenter-kb": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mock-api",
        "run",
        "python",
        "basic_mcp_stdio.py"
      ]
    }
  }
}
```

#### Continue.dev Configuration

Add to `$HOME/.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "uv",
          "args": ["--directory", "/path/to/mock-api", "run", "python", "basic_mcp_stdio.py"]
        }  
      }
    ]
  }
}
```

#### Sample Questions to Ask Your MCP Server

Try these questions to test the Teamcenter MCP integration:

1. **Basic Search**: "Search the Teamcenter knowledge base for technical information and documentation on Java and C++ based products"

2. **Product Documentation**: "Find documentation about CAD model versioning and lifecycle management in Teamcenter"

3. **API Integration**: "Search for information about REST API endpoints for part data retrieval"

4. **Workflow Queries**: "Look up documentation on workflow approval processes for engineering changes"

5. **User Management**: "Find information about user role permissions and access control in Teamcenter"

6. **Data Import/Export**: "Search for technical guides on bulk data import and export procedures"

The MCP servers provide LLM clients with structured access to the mock Teamcenter knowledge base, enabling AI assistants to search and retrieve information programmatically.
