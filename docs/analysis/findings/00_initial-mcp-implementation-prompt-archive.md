# Initial MCP Implementation Prompt (Archive)

> **Note:** This was the initial prompt that kicked off MCP server development. 
> The actual implementation evolved to use a two-server architecture instead 
> of in-process mounting. See `basic_mcp.py` and `auth_openapi_mcp.py` for 
> the working implementation, and `01_mcp-implementation-findings.md` for lessons learned.

# Original Implement MCP Server Command

## Command
Using the FastMCP in-process approach from DESIGN.md (Option A - server_inline.py), create an MCP server that:

1. Mounts at /mcp in our existing FastAPI app
2. Auto-generates tools from our OpenAPI spec
3. Overrides the /stream endpoint with proper SSE streaming using mcp.ctx.stream_content()
4. Names the main tool 'teamcenter_search' with a description that starts with 'Search the Teamcenter knowledge base for...'
5. Follows our TDD approach - write tests first using the pytest pattern from section 5

Start with the test file, then implement the minimal working server.

## Context
- Use FastMCP in-process mounting (not external proxy)
- Follow design principles in CLAUDE.md (simplicity, TDD, defensive programming)
- Base implementation on analysis/extrnal-docs/00_MCP_DESIGN.md Option A
- Test patterns from analysis/extrnal-docs/10_Playbook section 5
- Tool naming conventions from AWS MCP examples in analysis/extrnal-docs/11_AWS_MCP_servers.md

## Expected Outputs
1. `tests/test_mcp.py` - Test suite following pytest patterns
2. `server_inline.py` - FastMCP integration with existing FastAPI app
3. Updated requirements with FastMCP dependencies
4. Documentation on how to test the MCP endpoints