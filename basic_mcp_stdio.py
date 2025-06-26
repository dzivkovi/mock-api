"""
Basic MCP server - STDIO transport for VS Code integration
This version uses STDIO instead of HTTP for VS Code to manage the process
"""
from fastmcp import FastMCP

# Create basic MCP server
mcp = FastMCP(name="Teamcenter-KB")

@mcp.tool()
async def teamcenter_search(search_query: str, sessionID: str = "vscode_session", topNDocuments: int = 5) -> str:
    """Search the Teamcenter knowledge base for technical information and documentation."""
    import httpx
    
    # Call the existing stream endpoint (running on port 8000)
    async with httpx.AsyncClient() as client:
        params = {
            "search_query": search_query,
            "sessionID": sessionID,
            "topNDocuments": topNDocuments
        }
        try:
            response = await client.get("http://127.0.0.1:8000/stream", params=params)
            
            # Parse SSE response and return accumulated content
            content = []
            citations = []
            
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    import json
                    try:
                        data = json.loads(line[6:])
                        if data.get('type') == 'response':
                            content.append(data.get('data', ''))
                        elif data.get('type') == 'citation':
                            citations.append(data.get('data', ''))
                    except:
                        pass
            
            result = ''.join(content)
            if citations:
                result += "\n\nCitations:\n" + '\n'.join(citations)
            
            return result
            
        except Exception as e:
            return f"Error calling Teamcenter API: {str(e)}"

@mcp.tool()
def health_check() -> str:
    """Check if the Teamcenter KB API is healthy and server status"""
    import httpx
    try:
        with httpx.Client() as client:
            response = client.get("http://127.0.0.1:8000/health", timeout=5.0)
            if response.status_code == 200:
                return "✅ Teamcenter KB API is healthy and MCP server is running"
            else:
                return f"⚠️ Teamcenter KB API returned status {response.status_code}"
    except Exception as e:
        return f"❌ Cannot reach Teamcenter KB API: {str(e)}"

if __name__ == "__main__":
    # Use STDIO transport - VS Code will manage this process
    mcp.run(transport="stdio")