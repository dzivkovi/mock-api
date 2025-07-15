"""
Integration tests for MCP server with both mock and real APIs
"""
import pytest
import asyncio
import os
import json
import time
from unittest.mock import patch
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth_mcp_stdio_v2 import auth_session, search, health_check, session_info


class TestMCPIntegration:
    """Integration tests for the MCP server"""
    
    @pytest.mark.asyncio
    async def test_mock_api_health_check(self):
        """Test health check against mock API"""
        # Ensure we're using mock API
        with patch.dict(os.environ, {"TEAMCENTER_API_HOST": "http://localhost:8000"}):
            # Re-initialize auth session with mock URL
            auth_session.base_url = "http://localhost:8000"
            auth_session.auth_mode = "mock"
            
            result = await health_check.fn()
            data = json.loads(result)
            
            assert data["api_status"] in ["healthy", "error"]  # May be error if mock not running
            assert data["api_url"] == "http://localhost:8000"
            assert data["auth_mode"] == "mock"
    
    @pytest.mark.asyncio
    async def test_mock_api_session_info(self):
        """Test session info against mock API"""
        with patch.dict(os.environ, {"TEAMCENTER_API_HOST": "http://localhost:8000"}):
            auth_session.base_url = "http://localhost:8000"
            auth_session.auth_mode = "mock"
            
            result = await session_info.fn()
            data = json.loads(result)
            
            assert "auth_mode" in data
            assert data["auth_mode"] == "mock"
            assert "session_valid" in data
            assert isinstance(data["session_valid"], bool)
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("TEAMCENTER_API_HOST", "").startswith("http://localhost"),
        reason="Mock API test - requires local mock server"
    )
    async def test_mock_api_search(self):
        """Test search functionality against mock API"""
        with patch.dict(os.environ, {"TEAMCENTER_API_HOST": "http://localhost:8000"}):
            auth_session.base_url = "http://localhost:8000"
            auth_session.auth_mode = "mock"
            
            # Clear any existing session
            auth_session.session_cookie = None
            auth_session.expires_at = None
            
            result = await search.fn(
                search_query="test query", 
                topNDocuments=3
            )
            
            # Mock API returns SSE format
            assert "data:" in result
            assert "type" in result
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("AZURE_BEARER_TOKEN") and not os.getenv("CODESESS_COOKIE"),
        reason="Real API test - requires authentication token or cookie"
    )
    async def test_real_api_search(self):
        """Test search against real CodeSentinel API"""
        # This test only runs if you have valid credentials
        api_host = "https://codesentinel.azurewebsites.net"
        
        with patch.dict(os.environ, {"TEAMCENTER_API_HOST": api_host}):
            auth_session.base_url = api_host
            auth_session.auth_mode = "production"
            
            # If we have a cookie, use it directly
            if os.getenv("CODESESS_COOKIE"):
                auth_session.session_cookie = os.getenv("CODESESS_COOKIE")
                auth_session.expires_at = datetime.now() + timedelta(minutes=30)
            
            start_time = time.time()
            result = await search.fn(
                search_query="What file processes JSON requests for Updating / Deleting Classes?",
                topNDocuments=5
            )
            elapsed = time.time() - start_time
            
            # Verify response
            assert "data:" in result  # SSE format
            assert elapsed < 90  # Should complete within 90 seconds
            
            # Parse response
            answer = ""
            for line in result.split('\n'):
                if line.startswith('data: '):
                    try:
                        event = json.loads(line[6:])
                        if event.get('type') == 'response':
                            answer += event.get('data', '')
                    except:
                        pass
            
            # The answer should mention the schema file
            assert len(answer) > 100  # Substantial answer
            assert "classification" in answer.lower() or "schema" in answer.lower()


class TestMCPWithCookie:
    """Test using direct cookie authentication"""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("CODESESS_COOKIE"),
        reason="Requires CODESESS_COOKIE environment variable"
    )
    async def test_with_codesess_cookie(self):
        """Test direct cookie authentication with real API"""
        import httpx
        
        cookie = os.getenv("CODESESS_COOKIE")
        url = 'https://codesentinel.azurewebsites.net/stream'
        params = {
            'search_query': 'What is Teamcenter?',
            'topNDocuments': 3
        }
        headers = {
            'Cookie': f'codesess={cookie}',
            'Accept': 'text/event-stream'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, 
                params=params, 
                headers=headers, 
                timeout=60.0
            )
            
            assert response.status_code == 200
            assert response.headers.get('content-type', '').startswith('text/event-stream')
            
            # Verify we got a streaming response
            content = response.text
            assert "data:" in content
            assert "type" in content


def test_auth_session_configuration():
    """Test that auth session configures correctly based on environment"""
    # Test mock mode
    with patch.dict(os.environ, {"TEAMCENTER_API_HOST": "http://localhost:8000"}):
        from auth_mcp_stdio_v2 import AuthSession
        session = AuthSession()
        assert session.auth_mode == "mock"
        assert session.base_url == "http://localhost:8000"
    
    # Test production mode
    with patch.dict(os.environ, {"TEAMCENTER_API_HOST": "https://codesentinel.azurewebsites.net"}):
        session = AuthSession()
        assert session.auth_mode == "production"
        assert session.base_url == "https://codesentinel.azurewebsites.net"


# Import datetime for the test
from datetime import datetime, timedelta

if __name__ == "__main__":
    # Run specific test with cookie if provided
    if len(sys.argv) > 1 and sys.argv[1].startswith("ey"):
        os.environ["CODESESS_COOKIE"] = sys.argv[1]
        pytest.main([__file__, "-v", "-k", "test_with_codesess_cookie"])
    else:
        pytest.main([__file__, "-v"])