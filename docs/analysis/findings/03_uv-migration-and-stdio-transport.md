# UV Migration and STDIO Transport Decision

## Migration Overview

Migrated entire project from pip/venv to UV package management for improved MCP server distribution and modern Python tooling.

## Key Decisions

### UV Package Manager
- **Problem**: Uncertain client-side Python library availability for MCP server distribution
- **Solution**: UV provides deterministic dependency resolution and simplified distribution
- **Rationale**: In Python AI/agentic development, UV dominates like NPX does in Node.js

### STDIO Transport 
- **Problem**: HTTP transport partially supported, not widely implemented across IDEs
- **Solution**: Switched to STDIO transport for VS Code integration
- **Rationale**: STDIO is most portable, supported everywhere, perfect for initial POC

## Implementation Changes

### Package Management
- Created `pyproject.toml` replacing `requirements.txt`
- Updated all commands to use `uv run`
- 40 dependencies resolved deterministically
- Updated documentation and VS Code configuration

### Transport Layer
- HTTP MCP server encountered VS Code integration issues
- STDIO transport works with VS Code's managed process model
- Single server file (`basic_mcp_stdio.py`) handles full lifecycle

## Benefits

1. **Distribution**: UV enables easy MCP server distribution without dependency conflicts
2. **Portability**: STDIO works across maximum IDE ecosystem 
3. **Simplicity**: Single command deployment (`uv run python basic_mcp_stdio.py`)
4. **Modern Tooling**: Aligns with current Python AI development standards

## Trade-offs

- Abandoned HTTP transport (more complex but feature-rich)
- UV learning curve for traditional pip users
- STDIO limited to single-client connections

## Outcome

Successfully deployed Teamcenter MCP server with:
- ✅ VS Code integration via STDIO
- ✅ UV-managed dependencies  
- ✅ Comprehensive test coverage
- ✅ Clean project structure

Migration positions project for broader IDE support and reliable distribution in Python AI ecosystem.