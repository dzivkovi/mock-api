# MCP Server Testing and Validation Guide

## Overview

Complete guide for testing the authenticated MCP server (`auth_mcp_stdio.py`) that integrates with the stateful mock authentication system. This guide covers all testing methods to validate the MCP server works correctly with VS Code and other MCP clients.

## Prerequisites

- Mock API server running on `http://127.0.0.1:8000`
- Authentication enabled in the mock API
- UV package manager installed
- Node.js ^22.7.5 (for MCP Inspector)

## Testing Methods

### Method 1: VS Code MCP Integration Testing (Primary)

#### Step 1: Ensure VS Code Setup
1. **Restart VS Code completely** (this is crucial for MCP configuration changes!)
2. **Open the Command Palette** (`Ctrl+Shift+P`)
3. **Search for "MCP"** - you should see MCP-related commands
4. **Verify configuration** in `.vscode/mcp.json`:
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

#### Step 2: Test MCP Server Availability
Your MCP server is named `teamcenter`, so try these in the VS Code chat:

```
/mcp.teamcenter.teamcenter_search How to implement authentication?
```

```
/mcp.teamcenter.teamcenter_health_check
```

```
/mcp.teamcenter.teamcenter_session_info
```

#### Step 3: Expected VS Code Behavior
- **Successful connection**: MCP commands should autocomplete
- **Tool execution**: Commands should return results from the mock API
- **Authentication flow**: Should auto-authenticate transparently
- **Error handling**: Should gracefully handle session expiry

### Method 2: MCP Inspector (Standalone Testing)

#### Step 1: Install and Run MCP Inspector
```bash
# Navigate to your project
cd C:/Users/z0052v7s/ws/ghcp/context/mock-api

# Test your MCP server directly
npx @modelcontextprotocol/inspector uv run python auth_mcp_stdio.py
```

#### Step 2: Open the Inspector Web UI
- Inspector runs on **http://localhost:6274**
- Open this in your browser
- You'll see a web UI to test your MCP tools
- Available tools should include:
  - `teamcenter_search`
  - `teamcenter_health_check`
  - `teamcenter_session_info`

#### Step 3: Test Tool Execution
1. **Health Check**: Verify API connectivity and authentication
2. **Session Info**: Check current authentication status
3. **Search**: Test the main search functionality with different queries

### Method 3: Manual STDIO Testing

#### Test the Server Directly
```bash
# In your project directory
uv run python auth_mcp_stdio.py
```

The server will start in STDIO mode. You can send JSON-RPC messages manually to test the MCP protocol.

#### Example JSON-RPC Messages
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "teamcenter_health_check",
    "arguments": {}
  }
}
```

### Method 4: Debug Logging (Current Implementation)

#### Debug Logging Configuration
The MCP server now includes comprehensive debug logging:

```python
# Logs to stderr (doesn't interfere with STDIO MCP protocol)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
```

#### Log Output Locations
- **VS Code**: Check the "Output" panel, look for MCP-related channels
- **Terminal**: When running directly, logs appear in stderr
- **MCP Inspector**: Logs visible in the browser console

#### Key Log Messages to Watch For
- `🔧 AuthSession initialized with base_url: http://127.0.0.1:8000`
- `🔐 Starting authentication process...`
- `✅ Authentication successful, session expires at [timestamp]`
- `🔍 MCP Tool called: teamcenter_search('query', 5)`
- `🔍 Session validity check: True/False`

## Validation Checklist

### ✅ Success Indicators

#### MCP Server Functionality
- [ ] VS Code recognizes the `teamcenter` MCP server
- [ ] MCP tools appear in VS Code autocomplete
- [ ] `/mcp.teamcenter.teamcenter_health_check` returns "healthy" status
- [ ] `/mcp.teamcenter.teamcenter_search` returns streaming responses
- [ ] `/mcp.teamcenter.teamcenter_session_info` shows valid session

#### Authentication Flow
- [ ] Auto-authentication with mock API succeeds
- [ ] Session cookie extraction from `/api/login` works
- [ ] Session expiry (55 minutes) calculated correctly
- [ ] Session revalidation on expiry works
- [ ] Invalid sessions trigger re-authentication

#### API Integration
- [ ] Mock API `/stream` endpoint returns streaming responses
- [ ] Session cookies sent correctly with API requests
- [ ] 401 errors trigger automatic re-authentication
- [ ] Tool responses include both content and citations

### 🚨 Common Issues & Solutions

#### VS Code doesn't see your MCP server:
```bash
# Check your path in .vscode/mcp.json matches exactly
# Restart VS Code completely
# Check VS Code output for MCP-related errors
# Verify UV and Python paths are correct
```

#### Authentication fails:
```bash
# Make sure your mock API is running on port 8000
# Check auth_mcp_stdio.py debug logs in stderr
# Verify the /api/login endpoint works manually:
curl -X POST http://127.0.0.1:8000/api/login \
  -H "Authorization: Bearer test_token" \
  -v
```

#### Tools don't execute:
```bash
# Check the MCP server process is running
# Verify UV installation: uv --version
# Check for import errors in auth_mcp_stdio.py
# Look for Python/dependency errors in logs
```

#### Session management issues:
```bash
# Check system clock synchronization
# Verify session expiry logic in logs
# Test manual session creation via /api/login
# Check if cookies are being parsed correctly
```

## Testing Workflow

### 1. Initial Setup Validation
```bash
# Terminal 1: Start mock API
uv run uvicorn main:app --reload

# Terminal 2: Test MCP server directly
uv run python auth_mcp_stdio.py
# Look for authentication success in logs
```

### 2. MCP Inspector Testing
```bash
# Terminal 3: Run MCP Inspector
npx @modelcontextprotocol/inspector uv run python auth_mcp_stdio.py

# Browser: Open http://localhost:6274
# Test all available tools
# Verify authentication flow in logs
```

### 3. VS Code Integration Testing
```bash
# Restart VS Code completely
# Open VS Code chat
# Test MCP tool commands:
/mcp.teamcenter.teamcenter_health_check
/mcp.teamcenter.teamcenter_search "test query"
/mcp.teamcenter.teamcenter_session_info
```

### 4. End-to-End Validation
```bash
# Verify complete flow:
# 1. MCP server starts → Auto-authenticates
# 2. VS Code connects → Tools available
# 3. Tool execution → API calls with session cookies
# 4. Session expiry → Automatic re-authentication
# 5. Error handling → Graceful degradation
```

## Debug Commands

### Check Mock API Health
```bash
curl http://127.0.0.1:8000/health
```

### Test Authentication Manually
```bash
curl -X POST http://127.0.0.1:8000/api/login \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -v
```

### Test Authenticated Endpoint
```bash
# First get session cookie from login, then:
curl -X GET "http://127.0.0.1:8000/stream?search_query=test&topNDocuments=2" \
  -H "Cookie: codesess=YOUR_SESSION_ID" \
  -v
```

### Check MCP Server Syntax
```bash
uv run python -m py_compile auth_mcp_stdio.py
```

## Success Criteria

### ✅ Development Complete When:
1. **VS Code Integration**: MCP tools work seamlessly in VS Code chat
2. **Authentication**: Auto-authentication with mock API is transparent
3. **Tool Execution**: All three tools return expected results
4. **Session Management**: Sessions expire and renew automatically
5. **Error Handling**: Graceful degradation on API/auth failures
6. **Documentation**: Team can reproduce setup and testing

### ✅ Production Ready When:
1. **Reliability**: Consistent tool execution across restarts
2. **Performance**: Sub-second response times for most queries
3. **Monitoring**: Comprehensive debug logging for troubleshooting
4. **Maintainability**: Clear separation of concerns and error handling
5. **Team Adoption**: Other developers can use and extend the system

## References

- [VS Code MCP Support Blog](https://code.visualstudio.com/blogs/2025/06/12/full-mcp-spec-support)
- [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [VS Code MCP Documentation](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
- [FastMCP Documentation](https://fastmcp.readthedocs.io/)

## Version History

- **v1.0**: Initial authenticated MCP server implementation
- **v1.1**: Added comprehensive debug logging
- **v1.2**: Enhanced error handling and session management
- **Current**: Full testing and validation guide