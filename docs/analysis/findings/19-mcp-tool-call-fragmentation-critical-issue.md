# MCP Tool Call Fragmentation: Critical Protocol Breakdown Analysis

**Timestamp:** 2025-07-09 23:45 UTC  
**Context:** Debugging persistent 401 authentication errors in MCP search functionality after multiple fixes  
**Status:** CRITICAL - MCP protocol breakdown detected  

## Query Context

User attempted to execute:
```
@MCP Teamcenter search: What is the role of the HierarchyInfoAndOptions structure in classification operations?
```

After implementing multiple fixes:
- v0.1.4: Fixed cookie name from `AppServiceAuthSession` to `codesess`
- v0.1.5: Added query parameters support to `make_authenticated_request`

## Critical Discovery: Tool Call Fragmentation

### Observed Behavior

Instead of a single, clean tool call:
```json
{
  "name": "mcp_server_teamcenter_search",
  "arguments": {
    "search_query": "What is the role of the HierarchyInfoAndOptions structure in classification operations?",
    "topNDocuments": 5
  }
}
```

Continue.dev is fragmenting the tool call into **25+ micro-calls**:

```
Tool call: {"arguments": ""}
Tool call: {"arguments": "{\"search_q"}  
Tool call: {"arguments": "uery\": \""}
Tool call: {"arguments": "What is"}
Tool call: {"arguments": " the "}
Tool call: {"arguments": "role "}
Tool call: {"arguments": "and pur"}
Tool call: {"arguments": "pose o"}
Tool call: {"arguments": "f Hier"}
Tool call: {"arguments": "archyInfo"}
Tool call: {"arguments": "AndO"}
Tool call: {"arguments": "ptions stru"}
Tool call: {"arguments": "cture in "}
Tool call: {"arguments": "classificat"}
Tool call: {"arguments": "ion"}
Tool call: {"arguments": " o"}
Tool call: {"arguments": "pe"}
Tool call: {"arguments": "rations"}
Tool call: {"arguments": "? H"}
Tool call: {"arguments": "ow is it"}
Tool call: {"arguments": " use"}
Tool call: {"arguments": "d?\""}
Tool call: {"arguments": ", \""}
Tool call: {"arguments": "topNDocument"}
Tool call: {"arguments": "s\": 5}"}
```

## Root Cause Analysis

### Potential Causes

1. **Continue.dev MCP Client Bug**
   - Client incorrectly streaming/chunking tool call arguments
   - Should send complete JSON in single call
   - Character-by-character transmission is abnormal

2. **FastMCP Tool Definition Issue**
   - Tool description mentions "streaming response"
   - Might confuse Continue.dev into thinking the tool itself streams
   - Current description: `"Search Teamcenter knowledge base with streaming response"`

3. **MCP Protocol Version Mismatch**
   - Continue.dev using different MCP protocol version than FastMCP
   - Incompatible serialization between client/server

4. **Tool Parameter Schema Problem**
   - Complex parameter schema causing fragmentation
   - JSON serialization issues

## Impact Assessment

### Why This Explains Previous Issues

- **Tool Definition Visible**: Continue.dev correctly shows tool schema in output
- **Authentication Working**: Health check and session info work (no parameters)
- **Search Failing**: Fragmented parameters never reach our MCP server properly
- **401 Errors**: Server receives malformed requests without proper search_query

### What Actually Reaches Our Server

Instead of:
```
GET /stream?search_query=What+is+the+role...&topNDocuments=5
```

Server likely receives:
```
GET /stream?search_query=&topNDocuments=
```

Or multiple incomplete requests, causing 401/400 errors.

## Immediate Diagnostics Needed

1. **Timing Analysis**: Did this behavior start with v0.1.5 or exist before?
2. **Continue.dev Version**: What version is being used?
3. **Cross-Reference**: Does this happen with other MCP servers (SQLite)?
4. **Protocol Version**: Check MCP protocol versions in use

## Potential Fixes

### Quick Fix Attempt
1. Remove "streaming" mention from tool description:
   ```python
   """Search Teamcenter knowledge base for technical information"""
   ```

2. Simplify tool schema to minimal parameters

3. Test with basic string parameter only

### Long-term Solutions
1. Update Continue.dev if this is a known issue
2. Switch to different MCP client implementation
3. Implement workaround for fragmented calls

## Conclusion

**This is NOT an authentication issue** - it's a fundamental MCP protocol breakdown where tool calls are being fragmented character-by-character instead of sent as complete JSON objects. 

The authentication fixes (cookie name, query parameters) were correct but cannot work if the tool calls never reach the server properly.

**Priority:** CRITICAL - This affects all MCP functionality requiring parameters.

## Next Steps

1. Determine if this is a regression or existing issue
2. Test with simplified tool definition
3. Check Continue.dev configuration and version
4. Consider alternative MCP client if issue persists