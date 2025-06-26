"""
Test API endpoints to verify mock API matches real API signatures
"""
import httpx
import pytest
import json


@pytest.mark.asyncio
async def test_api_login():
    """Test that /api/login endpoint works correctly."""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": "Bearer test_token_123",
            "X-Refresh-Token": "refresh_token_456"
        }
        
        response = await client.post(
            "http://127.0.0.1:8000/api/login",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test that /health endpoint returns OK status."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OK"


@pytest.mark.asyncio
async def test_unauthorized_endpoint():
    """Test that /unauthorized endpoint returns HTML content."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/unauthorized")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert "<h1>Unauthorized</h1>" in response.text


@pytest.mark.asyncio
async def test_token_endpoint():
    """Test that /token endpoint works with bearer auth."""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": "Bearer test_token_123"
        }
        
        response = await client.get(
            "http://127.0.0.1:8000/token?sid=test_session_id",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert "token" in data
        assert data["sid"] == "test_session_id"


@pytest.mark.asyncio
async def test_stream_endpoint():
    """Test that /stream endpoint accepts minimal parameters."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://127.0.0.1:8000/stream",
            params={
                "search_query": "test query",
                "topNDocuments": 3
            }
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Verify streaming response format
        content = response.text
        assert "data: " in content
        assert '"type": "metadata"' in content
        assert '"type": "response"' in content
        assert '"type": "citation"' in content


@pytest.mark.asyncio
async def test_add_rating_endpoint():
    """Test that /add_rating endpoint accepts ratings."""
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": "test_session_123",
            "search_query": "test query",
            "rating": 4.5
        }
        
        response = await client.post(
            "http://127.0.0.1:8000/add_rating",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Rating added successfully"


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_api_login())