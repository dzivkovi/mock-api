# Teamcenter MCP Server Tutorial

### Sample Continue.dev session for Teamcenter Knowledge Base search

This tutorial demonstrates how to use the Teamcenter MCP server with Continue.dev to search technical documentation and knowledge base content.

## Prerequisites

1. **API Server Running**: Ensure your mock Teamcenter API is running on `http://localhost:8000`
2. **MCP Configuration**: Continue.dev configured with Teamcenter MCP server (using UVX wheel deployment)

## Sample Session Commands

### 1. Health Check - Verify Connection

**Command:**
```
@MCP check if the Teamcenter knowledge base is healthy and working
```

**Expected Response:**
- ✅ Teamcenter KB API is healthy
- 🔐 Authentication: working  
- 📅 Session: valid (expires at [timestamp])

### 2. Basic Technical Search

**Command:**
```
@MCP search the Teamcenter knowledge base for information about PLM workflow integration
```

**What this does:**
- Searches Teamcenter documentation for PLM workflow-related content
- Returns relevant technical information with citations
- Demonstrates basic search functionality

### 3. Product-Specific Documentation Search

**Command:**
```
@MCP find documentation about CAD model versioning and lifecycle management in Teamcenter
```

**Expected Response:**
- Technical documentation about CAD versioning
- Lifecycle management processes
- Version control best practices
- Related citations and references

### 4. API Integration Query

**Command:**
```
@MCP search for REST API endpoints and integration guides for part data retrieval
```

**Use Case:**
- Developers looking for API documentation
- Integration patterns and examples
- Authentication requirements
- Sample code snippets

### 5. Workflow and Process Documentation

**Command:**
```
@MCP look up documentation on workflow approval processes for engineering changes
```

**What you'll get:**
- Step-by-step workflow processes
- Approval chain documentation
- Engineering change management procedures
- Best practice guidelines

### 6. User Management and Security

**Command:**
```
@MCP find information about user role permissions and access control in Teamcenter
```

**Response includes:**
- Role-based access control (RBAC) information
- Permission matrices
- Security configuration guides
- User management procedures

### 7. Data Import/Export Procedures

**Command:**
```
@MCP search for technical guides on bulk data import and export procedures
```

**Documentation covers:**
- Bulk data handling procedures
- Import/export formats
- Data validation processes
- Troubleshooting guides

### 8. Advanced Multi-Topic Search

**Command:**
```
@MCP search for information combining Java API integration with workflow automation in Teamcenter
```

**Advanced features:**
- Multi-concept search
- Cross-referenced documentation
- Integration examples
- Code samples and patterns

### 9. Session Information

**Command:**
```
@MCP show me the current authentication session details
```

**Provides:**
- Session ID preview
- Expiration timestamp
- Authentication status
- Connection health

## Key Features Demonstrated

### Authentication Handling
- **Automatic**: MCP server handles Azure AD token exchange
- **Session Management**: 55-minute sessions with auto-renewal
- **Transparent**: No manual authentication steps required

### Search Capabilities
- **Natural Language**: Ask questions in plain English
- **Technical Focus**: Optimized for engineering and technical documentation
- **Citation Support**: Results include source references
- **Multi-format**: Handles various document types and formats

### Cross-Platform Compatibility
- **Windows/WSL**: Works seamlessly across environments
- **Universal Access**: Same commands work everywhere
- **No Path Dependencies**: UVX deployment eliminates environment conflicts

## Usage Tips

1. **Be Specific**: More specific queries yield better results
   - ✅ "CAD model versioning in Teamcenter NX integration"
   - ❌ "models"

2. **Use Technical Terms**: Leverage Teamcenter-specific terminology
   - Examples: PLM, CAD, PDM, workflow, lifecycle, versioning

3. **Combine Concepts**: Search for multiple related topics
   - "Java API workflow automation"
   - "REST endpoints part data security"

4. **Health Checks**: Start sessions with health checks to verify connectivity

## Troubleshooting

### If MCP server doesn't respond:
1. Check if API server is running on `http://localhost:8000`
2. Verify Continue.dev MCP configuration
3. Check UVX wheel deployment path

### For authentication issues:
- MCP server automatically handles authentication
- Check API server logs for authentication errors
- Verify Azure AD token simulation is working

## Next Steps

After completing this tutorial:
1. **Customize URLs**: Replace `http://localhost:8000` with your production Teamcenter API
2. **Production Deployment**: Use the same UVX wheel approach for production
3. **Team Rollout**: Share the wheel file and configuration with your team
4. **Advanced Queries**: Experiment with complex, multi-concept searches

## Configuration Reference

**Continue.dev MCP Configuration:**
```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "uvx",
          "args": ["--from", "teamcenter_mcp_server-0.1.0-py3-none-any.whl", "teamcenter-mcp-server", "--base-url", "http://localhost:8000"]
        }
      }
    ]
  }
}
```

This tutorial demonstrates the power of combining Continue.dev with specialized MCP servers for domain-specific knowledge access!
