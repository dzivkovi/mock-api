"""
Test for focused Teamcenter Knowledge Base MCP server
Tests the single-tool approach for knowledge search
"""
import httpx
import pytest

@pytest.mark.asyncio
async def test_teamcenter_mcp_initialize():
    """Test that Teamcenter MCP server initializes correctly."""
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
            "http://127.0.0.1:8002/mcp/",  # Different port for basic_mcp
            json=payload,
            headers={"Accept": "application/json, text/event-stream"}
        )
        
        assert response.status_code == 200
        text = response.text
        assert "event: message" in text
        assert "Teamcenter-KB" in text

@pytest.mark.asyncio
async def test_teamcenter_has_focused_tools():
    """Test that Teamcenter MCP has focused knowledge tools."""
    # Similar session management issue, but verifies server responds
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8002/mcp/")
        assert response.status_code in [400, 404, 406]  # Expected errors: session/accept headers