# MCP Debug Logs Reading Guide

## VS Code MCP Log Output Interpretation

When debugging your MCP server in VS Code, you'll see logs in the "OUTPUT" tab under "MCP: teamcenter". Here's how to read them:

## 1. Server Startup Sequence ✅

```
[info] Starting server teamcenter
[info] Connection state: Starting
[info] Connection state: Running
[warning] [server stderr] Starting MCP server 'Teamcenter' with transport 'stdio'
[warning] [server stderr] 🔧 AuthSession initialized with base_url: http://127.0.0.1:8000
[info] Discovered 3 tools
```

**What this means:**
- ✅ Server started successfully
- ✅ Connected to API on port 8000
- ✅ Found 3 MCP tools (teamcenter_search, health_check, authenticate)

## 2. Common Startup Errors ❌

### Error: File Not Found
```
[warning] [server stderr] error: No such file or directory (os error 2)
[info] Connection state: Error Process exited with code 2
[error] Server exited before responding to `initialize` request.
```
**Fix:** Wrong path in mcp.json or missing `auth_mcp_stdio.py` file

### Error: Python/UV Not Found
```
[error] Failed to start server: spawn uv ENOENT
```
**Fix:** UV not installed or not in PATH

### Error: API Server Not Running
```
[warning] [server stderr] httpcore.ConnectError: All connection attempts failed
```
**Fix:** Start API server first: `uv run uvicorn main:app --reload`

## 3. Successful Tool Call 🎯

```
[warning] [server stderr] 🔍 MCP Tool called: teamcenter_search('PLM functions', 5)
[warning] [server stderr] 🔍 Session validity check: True, expires at 2025-06-27 15:30:46.417177
[warning] [server stderr] 🔍 Session is valid, no authentication needed
[warning] [server stderr] HTTP Request: GET http://127.0.0.1:8000/stream?search_query=PLM+functions&topNDocuments=5 "HTTP/1.1 200 OK"
[warning] [server stderr] Response sent
```

**What this means:**
- ✅ Tool called with correct parameters
- ✅ Session authentication working
- ✅ API call successful (200 OK)
- ✅ Response sent back to VS Code

## 4. Authentication Flow 🔐

```
[warning] [server stderr] 🔍 Session invalid: missing cookie or expiry
[warning] [server stderr] 🔐 Session expired or missing, authenticating...
[warning] [server stderr] 🔐 Starting authentication process...
[warning] [server stderr] 🔐 Calling http://127.0.0.1:8000/api/login with headers: {...}
[warning] [server stderr] HTTP Request: POST http://127.0.0.1:8000/api/login "HTTP/1.1 200 OK"
[warning] [server stderr] 🔐 Extracted session cookie: 474b5602...
[warning] [server stderr] ✅ Authentication successful, session expires at 2025-06-27 15:30:46.417177
```

**What this means:**
- ✅ Auto-authentication triggered
- ✅ Login successful
- ✅ Session cookie saved (55-minute expiry)

## 5. Log Level Meanings

| Level | Color | Meaning |
|-------|-------|---------|
| `[info]` | Blue | Normal operation |
| `[warning]` | Yellow | Expected verbose output |
| `[error]` | Red | Actual problems |

**Note:** Most MCP output appears as `[warning] [server stderr]` - this is **normal**! It's just verbose logging, not actual warnings.

## 6. Key Debug Indicators

### ✅ Success Patterns
- `Connection state: Running`
- `Discovered X tools`
- `HTTP/1.1 200 OK`
- `Response sent`
- `✅ Authentication successful`

### ❌ Problem Patterns
- `Connection state: Error`
- `Process exited with code 2`
- `ConnectError: All connection attempts failed`
- `HTTP/1.1 4XX` or `HTTP/1.1 5XX`

## 7. Debugging Checklist

When MCP isn't working:

1. **Check API server:** Is `uvicorn main:app --reload` running?
2. **Check paths:** Does mcp.json point to correct Windows path?
3. **Check files:** Does `auth_mcp_stdio.py` exist?
4. **Check UV:** Run `uv --version` in terminal
5. **Check logs:** Look for the patterns above

## 8. Quick Test Commands

In your terminal (to verify everything works):
```bash
# Test API server
curl http://127.0.0.1:8000/health

# Test authentication
curl -X POST "http://127.0.0.1:8000/api/login" -H "Authorization: Bearer test"

# Test MCP server directly
uv run python auth_mcp_stdio.py
```

## 9. Log Volume

Don't be alarmed by lots of `[warning] [server stderr]` output - this includes:
- HTTP connection details
- Request/response debugging
- Session management
- All normal operation verbose logging

Focus on the **actual error levels** and **connection state** messages for real issues.