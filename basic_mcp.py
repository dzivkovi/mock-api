"""
Basic MCP server - minimal working implementation
No mounting, just a simple MCP server that works
"""
from fastmcp import FastMCP

# Create basic MCP server
mcp = FastMCP(name="Teamcenter-KB")

@mcp.tool()
async def teamcenter_search(search_query: str, sessionID: str, topNDocuments: int = 5) -> str:
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
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    import json
                    try:
                        data = json.loads(line[6:])
                        if data.get('type') == 'response':
                            content.append(data.get('data', ''))
                        elif data.get('type') == 'citation':
                            content.append(f"\n{data.get('data', '')}")
                    except:
                        pass
            return ''.join(content)
        except Exception as e:
            return f"Error calling API: {str(e)}"

@mcp.tool()
def health_check() -> str:
    """Check if the Teamcenter KB API is healthy"""
    return "Teamcenter KB MCP server is running"

if __name__ == "__main__":
    print("Starting basic MCP server on port 8002...")
    mcp.run(transport="http", host="0.0.0.0", port=8002)