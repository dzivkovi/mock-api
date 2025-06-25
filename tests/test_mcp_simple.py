"""
Simple MCP test - just verify the server responds
"""
import httpx
import pytest

@pytest.mark.asyncio
async def test_mcp_initialize_works():
    """Test that MCP server initialization works."""
    async with httpx.AsyncClient() as client:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        response = await client.post(
            "http://127.0.0.1:8001/mcp/",
            json=payload,
            headers={"Accept": "application/json, text/event-stream"}
        )
        
        assert response.status_code == 200
        
        # Response should be SSE format
        text = response.text
        assert "event: message" in text
        assert "Auto-Generated-API" in text

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mcp_initialize_works())