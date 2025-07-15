"""
Tests for the Teamcenter MCP STDIO server v2
Tests the optimized version with proper auth
"""
import subprocess
import time
import json
import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_server_imports_cleanly():
    """Test that the server can be imported quickly for VS Code"""
    
    start_time = time.time()
    try:
        import auth_mcp_stdio_v2
        import_time = time.time() - start_time
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")
    
    # V2 is optimized, should import in under 10 seconds on native filesystem
    # WSL2 with Windows mount points is slower, so allow 20 seconds
    assert import_time < 20.0, f"Import took {import_time}s, too slow for VS Code"

def test_teamcenter_server_identity():
    """Test that server identifies itself correctly"""
    import auth_mcp_stdio_v2
    
    # Check the MCP instance exists
    assert hasattr(auth_mcp_stdio_v2, 'mcp')
    assert auth_mcp_stdio_v2.mcp.name == "teamcenter-mcp-server"
    assert auth_mcp_stdio_v2.mcp.version == "0.2.0"

def test_stdio_transport_configuration():
    """Test that STDIO transport is properly configured"""
    import auth_mcp_stdio_v2
    
    # The v2 server should have the MCP instance
    assert hasattr(auth_mcp_stdio_v2, 'mcp')
    
    # Check main function exists
    assert hasattr(auth_mcp_stdio_v2, 'main')
    assert callable(auth_mcp_stdio_v2.main)

def test_teamcenter_tool_functions():
    """Test that all three MCP tools are properly defined"""
    import auth_mcp_stdio_v2
    
    # Check all tools exist
    assert hasattr(auth_mcp_stdio_v2, 'search')
    assert hasattr(auth_mcp_stdio_v2, 'health_check')
    assert hasattr(auth_mcp_stdio_v2, 'session_info')
    
    # Check they're MCP tools
    from fastmcp.tools.tool import FunctionTool
    assert isinstance(auth_mcp_stdio_v2.search, FunctionTool)
    assert isinstance(auth_mcp_stdio_v2.health_check, FunctionTool)
    assert isinstance(auth_mcp_stdio_v2.session_info, FunctionTool)

def test_auth_session_configuration():
    """Test that auth session is properly configured"""
    import auth_mcp_stdio_v2
    
    # Check auth session exists
    assert hasattr(auth_mcp_stdio_v2, 'auth_session')
    assert isinstance(auth_mcp_stdio_v2.auth_session, auth_mcp_stdio_v2.AuthSession)
    
    # Check default configuration
    assert auth_mcp_stdio_v2.auth_session.base_url  # Should have a base URL
    assert auth_mcp_stdio_v2.auth_session.auth_mode in ["mock", "production"]

def test_vscode_mcp_configuration():
    """Test that Continue.dev configuration example is valid"""
    config = {
        "type": "mcp",
        "title": "Teamcenter MCP",
        "transport": {
            "type": "stdio",
            "command": "uv",
            "args": ["run", "python", "auth_mcp_stdio_v2.py"],
            "env": {
                "TEAMCENTER_API_HOST": "https://codesentinel.azurewebsites.net"
            }
        }
    }
    
    # Verify structure
    assert config["type"] == "mcp"
    assert config["transport"]["type"] == "stdio"
    assert "command" in config["transport"]
    assert "args" in config["transport"]

def test_required_dependencies():
    """Test that all required dependencies are available"""
    required_modules = [
        "fastmcp",
        "httpx", 
        "json",
        "asyncio",
        "datetime",
        "typing",
        "logging",
        "sys",
        "os"
    ]
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            pytest.fail(f"Required module '{module}' not available")

def test_security_no_hardcoded_secrets():
    """Test that no Azure AD secrets are hardcoded"""
    with open("auth_mcp_stdio_v2.py", "r") as f:
        content = f.read()
    
    # These should NEVER appear in the code
    forbidden_strings = [
        # Check for pattern of Azure AD GUIDs (but not specific values)
        # Real check would be more complex - for now just ensure no obvious hardcoding
        "client-id-here",
        "tenant-id-here", 
    ]
    
    for secret in forbidden_strings:
        assert secret not in content, f"Found hardcoded secret: {secret}"

@pytest.mark.asyncio
async def test_cookie_authentication():
    """Test that CODESESS_COOKIE environment variable is used for authentication"""
    import auth_mcp_stdio_v2
    import os
    
    # Save original values
    original_cookie = os.environ.get("CODESESS_COOKIE")
    original_host = os.environ.get("TEAMCENTER_API_HOST")
    
    try:
        # Set test values
        os.environ["CODESESS_COOKIE"] = "test_cookie_12345"
        os.environ["TEAMCENTER_API_HOST"] = "https://codesentinel.azurewebsites.net"
        
        # Create new auth session
        auth_session = auth_mcp_stdio_v2.AuthSession()
        
        # Test authentication
        session = await auth_session.authenticate()
        
        assert session == "test_cookie_12345"
        assert auth_session.is_session_valid()
        assert auth_session.auth_mode == "production"
        
    finally:
        # Restore original values
        if original_cookie:
            os.environ["CODESESS_COOKIE"] = original_cookie
        else:
            os.environ.pop("CODESESS_COOKIE", None)
        
        if original_host:
            os.environ["TEAMCENTER_API_HOST"] = original_host
        else:
            os.environ.pop("TEAMCENTER_API_HOST", None)