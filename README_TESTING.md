# MCP Test Runner Guide

## Clean Start (Recommended)

If you have background processes running or want a fresh start:

```bash
# Clean any background processes first
pkill -f "uvicorn" || true
pkill -f "python.*mcp" || true

# Verify cleanup
ps aux | grep -E "(uvicorn|python.*mcp)" | grep -v grep
```

**Recommended**: Exit terminal session and start fresh to avoid process confusion.

## Manual Server Setup

### Terminal 1 - Original API
```bash
cd ~/work/mock-api
va
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 - Focused Teamcenter MCP Server
```bash
cd ~/work/mock-api
va
python basic_mcp.py  # Runs on port 8002
```

### Terminal 3 - Run Tests
```bash
cd ~/work/mock-api
va
# Simple working test
pytest tests/test_mcp_simple.py -v

# Full test suite (needs session fixes)
pytest tests/test_mcp.py -v
```

## Verify Setup

1. **Original API**: <http://localhost:8000/health> should return `{"status":"OK"}`
2. **Focused MCP**: <http://localhost:8002/mcp/> should handle MCP protocol  
3. **Tests**: All 5 tests should pass

## Test MCP Manually

```bash
# Initialize MCP session
curl -X POST -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"clientInfo":{"name":"test-client","version":"1.0.0"}}}' \
  http://localhost:8002/mcp/

# Test tools after initializing (session management needed)
# See working curl command above
```

## Expected Red→Green Cycle

1. **Red Phase**: Tests fail initially (expected)
2. **Green Phase**: Start servers, tests should pass
3. **Refactor Phase**: Improve implementation while keeping tests green

## Process Control

- **NEVER** use `&` to run servers in background during development
- **ALWAYS** use separate terminals for each server
- **CLEAN UP** processes between test runs to avoid confusion
- **EXIT** terminal session if you lose track of background processes

This approach follows defensive programming - explicit process control!