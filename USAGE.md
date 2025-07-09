# How to Use Teamcenter MCP Server

Ultra-simple copy & paste examples for both IDEs.

## VS Code (GitHub Copilot)

Open **GitHub Copilot Chat** and paste these:

### Health Check
```
Check if the Teamcenter knowledge base is healthy
```

### Search Examples
```
@workspace get Teamcenter API documentation for part creation

@teamcenter MCP server to search for PLM functions in any programming language
```

## Continue.dev

Open **Continue Chat** and paste these:

### Health Check
```
@MCP check if the Teamcenter knowledge base is healthy
```

### Search Examples
```
@MCP search Teamcenter for PLM workflow integration documentation

@MCP find CAD model versioning guides in Teamcenter
```

## What You'll See

Both IDEs will show:
- ✅ **Response from Teamcenter MCP server**
- ✅ **Citations with numbered references**
- ✅ **Formatted documentation snippets**

## Tips

- **VS Code**: Use `@workspace` or `@teamcenter` - both work
- **Continue.dev**: Always use `@MCP` prefix
- **Smart routing**: Just ask naturally - the AI will find your MCP server

## Troubleshooting

**No response?**
1. Check mock API server is running: `curl http://localhost:8000/health`
2. Restart your IDE
3. Verify configuration in `.vscode/mcp.json` or `~/.continue/config.json`

**That's it!** The MCP server handles everything else automatically.