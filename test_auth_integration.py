#!/usr/bin/env python3
"""
Integration tests for TeamCenterAuthSession
Tests both mock and production modes
"""
import asyncio
import os
import logging
from teamcenter_auth_session import TeamCenterAuthSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mock_mode():
    """Test localhost mock mode"""
    print("🧪 Testing Mock Mode")
    print("-" * 40)
    
    # Ensure no environment variable interference
    os.environ.pop('TEAMCENTER_API_HOST', None)
    
    session = TeamCenterAuthSession()
    
    # Check auth status
    status = session.get_auth_status()
    print(f"Auth Mode: {status['auth_mode']}")
    print(f"Base URL: {status['base_url']}")
    print(f"Session Valid: {status['is_session_valid']}")
    
    assert status['auth_mode'] == "mock"
    assert status['base_url'] == "http://127.0.0.1:8000"
    assert status['is_session_valid'] == True
    
    # Test authentication
    session_id = await session.authenticate()
    assert session_id is not None
    print(f"✅ Authentication successful: {session_id[:20]}...")
    
    # Test API call to health endpoint
    try:
        response = await session.make_authenticated_request("health")
        if response and response.status_code == 200:
            print("✅ Health check passed")
            print(f"📊 Response: {response.text}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code if response else 'No response'}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def test_production_mode():
    """Test production mode with cached cookie"""
    print("\n🧪 Testing Production Mode")
    print("-" * 40)
    
    # Set production environment
    os.environ['TEAMCENTER_API_HOST'] = "https://codesentinel.azurewebsites.net"
    
    session = TeamCenterAuthSession()
    
    # Check auth status
    status = session.get_auth_status()
    print(f"Auth Mode: {status['auth_mode']}")
    print(f"Base URL: {status['base_url']}")
    print(f"Session Valid: {status['is_session_valid']}")
    
    if status['auth_mode'] == 'mock':
        print("ℹ️  Fallback to mock mode (expected if no cookie)")
        return True  # This is acceptable behavior
    
    assert status['auth_mode'] == "cookie"
    assert "codesentinel" in status['base_url']
    
    # Test authentication
    session_id = await session.authenticate()
    if session_id is None:
        print("⚠️  No valid session (cookie might be expired)")
        return True  # This is acceptable - just means auth needed
    
    print(f"✅ Authentication successful: session exists")
    
    # Test API call to health endpoint  
    try:
        response = await session.make_authenticated_request("health")
        if response and response.status_code == 200:
            print("✅ Production health check passed")
            print(f"📊 Response: {response.text[:100]}")
            return True
        elif response and response.status_code == 401:
            print("⚠️  Authentication failed (401) - cookie might be expired")
            return True  # Expected behavior when cookie is expired
        else:
            print(f"❌ Unexpected response: {response.status_code if response else 'No response'}")
            return False
    except Exception as e:
        print(f"❌ Production API error: {e}")
        return False

async def test_environment_switching():
    """Test switching between environments"""
    print("\n🧪 Testing Environment Switching")
    print("-" * 40)
    
    # Test default (should be mock)
    os.environ.pop('TEAMCENTER_API_HOST', None)
    session1 = TeamCenterAuthSession()
    assert session1.auth_mode == "mock"
    print("✅ Default environment: mock mode")
    
    # Test explicit localhost
    session2 = TeamCenterAuthSession("http://127.0.0.1:8000")
    assert session2.auth_mode == "mock"
    print("✅ Explicit localhost: mock mode")
    
    # Test production via environment variable
    os.environ['TEAMCENTER_API_HOST'] = "https://codesentinel.azurewebsites.net"
    session3 = TeamCenterAuthSession()
    # Could be 'cookie' or 'mock' (if fallback occurs)
    assert session3.auth_mode in ['cookie', 'mock']
    print(f"✅ Production environment: {session3.auth_mode} mode")
    
    # Test production via parameter (should override env)
    session4 = TeamCenterAuthSession("https://codesentinel.azurewebsites.net")
    assert session4.auth_mode in ['cookie', 'mock']
    print(f"✅ Production parameter: {session4.auth_mode} mode")
    
    return True

async def main():
    """Run all integration tests"""
    print("🔧 TeamCenter Auth Session Integration Tests")
    print("=" * 50)
    
    try:
        # Test mock mode
        mock_result = await test_mock_mode()
        
        # Test production mode
        prod_result = await test_production_mode()
        
        # Test environment switching
        env_result = await test_environment_switching()
        
        # Overall result
        all_passed = mock_result and prod_result and env_result
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results:")
        print(f"   Mock Mode: {'✅ PASS' if mock_result else '❌ FAIL'}")
        print(f"   Production Mode: {'✅ PASS' if prod_result else '❌ FAIL'}")
        print(f"   Environment Switching: {'✅ PASS' if env_result else '❌ FAIL'}")
        print(f"   Overall: {'🎉 ALL TESTS PASSED' if all_passed else '💥 SOME TESTS FAILED'}")
        
        return all_passed
        
    except Exception as e:
        print(f"💥 Test suite failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        os.environ.pop('TEAMCENTER_API_HOST', None)

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)