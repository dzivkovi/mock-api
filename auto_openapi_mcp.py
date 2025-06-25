"""
Auto-OpenAPI MCP Server - Works with ANY OpenAPI spec
No manual tool definition needed!
"""
import os
import httpx
from fastmcp import FastMCP

# Environment configuration
OPENAPI_SPEC_URL = os.getenv("OPENAPI_SPEC_URL", "http://127.0.0.1:8000/openapi.json")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_NAME = os.getenv("API_NAME", "Auto-Generated-API")

async def create_auto_mcp():
    """Create MCP server from any OpenAPI spec automatically"""
    
    # Fetch the OpenAPI spec
    async with httpx.AsyncClient() as client:
        try:
            spec_response = await client.get(OPENAPI_SPEC_URL)
            openapi_spec = spec_response.json()
            print(f"✅ Loaded OpenAPI spec from: {OPENAPI_SPEC_URL}")
            print(f"📋 Found {len(openapi_spec.get('paths', {}))} endpoints")
        except Exception as e:
            print(f"❌ Failed to load OpenAPI spec: {e}")
            return None
    
    # Create HTTP client for API calls  
    api_client = httpx.AsyncClient(base_url=API_BASE_URL)
    
    # Auto-generate MCP server from OpenAPI spec
    mcp = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=api_client,
        name=API_NAME
    )
    
    print(f"🚀 Auto-generated MCP server '{API_NAME}' ready!")
    return mcp

if __name__ == "__main__":
    import asyncio
    
    # Create the MCP server
    mcp = asyncio.run(create_auto_mcp())
    
    if mcp:
        print(f"Starting auto-generated MCP server on port 8001...")
        # Use the synchronous run method - no asyncio.run needed
        mcp.run(transport="http", host="0.0.0.0", port=8001)