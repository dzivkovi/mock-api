# Universal MCP Server Cross-Platform Solution

**Timestamp:** 2025-07-09  
**Context:** Demo preparation - addressing cross-platform path issues and multi-IDE compatibility

## The Question/Challenge

User identified three critical issues with the current MCP server setup:

1. **Multi-IDE compatibility**: Need support for VS Code, Continue.dev, Visual Studio, Eclipse, and JetBrains (not just VS Code workspace variables)
2. **Package separation**: Only the MCP server should be packaged (not the mock API server which is just for demo)
3. **Configurable target URLs**: Currently hardcoded to localhost:8000, but needs to work with varying office URLs

## Analysis and Research Findings

### Multi-IDE MCP Support

Research revealed that all major IDEs now support MCP servers with similar configuration patterns:

- **VS Code**: `.vscode/mcp.json` with `${workspaceFolder}` variables
- **Continue.dev**: `config.json` with `experimental.modelContextProtocolServers`
- **JetBrains**: `~/.mcp.json` or solution-specific `.mcp.json`
- **Visual Studio**: `%USERPROFILE%\.mcp.json` or solution-specific `.vs\mcp.json`

All support console script commands uniformly across platforms.

### Python Package Distribution

Best practices for MCP server packaging:

- Use `pyproject.toml` with `[project.scripts]` for console script entry points
- Support command-line arguments for configuration
- Environment variable fallback for flexible deployment
- PyPI/uvx distribution for universal installation

### Cross-Platform Configuration Strategies

1. **Workspace Variables**: Limited to specific IDEs
2. **Package Distribution**: Universal solution across all IDEs
3. **Environment Variables**: Flexible but requires setup
4. **Command Arguments**: Most portable and explicit

## Recommended Solution: Standalone Python Package

### Package Structure
```
teamcenter-mcp/
├── pyproject.toml
├── README.md
├── src/
│   └── teamcenter_mcp/
│       ├── __init__.py
│       └── server.py  # Enhanced auth_mcp_stdio.py
```

### Key Features

**Console Script Entry Point:**
- Creates `teamcenter-mcp` command after installation
- Accepts `--base-url` argument for API endpoint
- Falls back to environment variable `TEAMCENTER_API_URL`
- Defaults to `localhost:8000` for demo

**Universal IDE Configuration:**

All IDEs use the same command with different target URLs:

```bash
teamcenter-mcp --base-url https://your-api.company.com
```

**VS Code Configuration (`.vscode/mcp.json`):**
```json
{
  "servers": {
    "teamcenter": {
      "type": "stdio",
      "command": "teamcenter-mcp",
      "args": ["--base-url", "https://your-api.company.com"]
    }
  }
}
```

**Continue.dev Configuration (`config.json`):**
```json
{
  "experimental": {
    "modelContextProtocolServers": [{
      "transport": {
        "type": "stdio",
        "command": "teamcenter-mcp",
        "args": ["--base-url", "https://your-api.company.com"]
      }
    }]
  }
}
```

**JetBrains/Visual Studio Configuration (`~/.mcp.json`):**
```json
{
  "mcpServers": {
    "teamcenter": {
      "command": "teamcenter-mcp",
      "args": ["--base-url", "https://your-api.company.com"]
    }
  }
}
```

### Implementation Steps

1. **Create package structure** with proper `pyproject.toml`
2. **Enhance server.py** with `argparse` for `--base-url` parameter
3. **Add console script entry point** in `[project.scripts]`
4. **Test locally** with `pip install -e .`
5. **Package for distribution** via PyPI or internal registry

### Benefits

✅ **Universal compatibility**: Same command works in all IDEs  
✅ **Clean separation**: MCP server independent of mock API  
✅ **Environment flexibility**: Works with any API URL  
✅ **Professional deployment**: Proper Python packaging  
✅ **Easy installation**: `pip install teamcenter-mcp` or `uvx teamcenter-mcp`  
✅ **Team sharing**: Package once, use everywhere  
✅ **No hardcoded paths**: Eliminates cross-platform path issues  
✅ **Production ready**: Configurable for different environments

## Next Steps

This solution addresses all three concerns by creating a proper Python package that can be installed once and configured differently for each environment, eliminating path dependencies and ensuring compatibility across all major IDEs.