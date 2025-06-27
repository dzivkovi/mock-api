# MCP Office Setup Instructions

## Problem Analysis 🔍

The working MCP server at home uses `auth_mcp_stdio.py` (authenticated version), not `basic_mcp_stdio.py`. 

**Evidence from logs:**
- Server name: `'Teamcenter-KB-Auth'` (not basic)
- Authentication flow: Session management, login calls, cookie handling
- File being called: `auth_mcp_stdio.py` (confirmed in git diff)

## Solution for Work (Windows 11) ✅

### 1. MCP Configuration File

Create/update `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "teamcenter": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/z0052v7s/ws/ghcp/context/mock-api",
        "run",
        "python", 
        "auth_mcp_stdio.py"
      ]
    }
  }
}
```

### 2. Required Files

Ensure these files exist in your work directory:
- `auth_mcp_stdio.py` (authenticated MCP server)
- `main.py` (API server with authentication)
- `pyproject.toml` (UV dependencies)

### 3. Startup Sequence

**Terminal 1: Start API Server**
```bash
uv run uvicorn main:app --reload
```
*Note: Both `--reload` and `--host 0.0.0.0 --port 8000 --reload` work fine*

**VS Code: Select MCP Server**
- Use "teamcenter" server (not "teamcenter-kb-legacy")
- Server should show `'Teamcenter-KB-Auth'` in logs

### 4. Path Format Notes

- Windows uses forward slashes in JSON: `C:/Users/...`
- Update the directory path to match your work environment
- Replace `C:/Users/z0052v7s/ws/ghcp/context/mock-api` with actual path

### 5. Verification

Working MCP server logs should show:
```
Starting MCP server 'Teamcenter-KB-Auth' with transport 'stdio'
🔧 AuthSession initialized with base_url: http://127.0.0.1:8000
Discovered 3 tools
```

### 6. Authentication Flow

The server handles authentication automatically:
- Auto-login with mock token on first request
- Session cookie management (55-minute expiry)
- Automatic re-authentication when sessions expire

## Key Insight

The difference between home and work is **not** the server startup command, but ensuring:
1. Correct MCP server file (`auth_mcp_stdio.py`)
2. Correct Windows path format
3. API server running on port 8000

Both startup commands work equally well:
- `uv run uvicorn main:app --reload` → 127.0.0.1:8000
- `uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload` → 0.0.0.0:8000