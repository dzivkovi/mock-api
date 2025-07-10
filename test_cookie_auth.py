#!/usr/bin/env python3
"""
Test cookie authentication works independently
This verifies we can access the working auth pattern from the other repo
"""
import sys
import os
from pathlib import Path

# Add path to teamcenter-auth-workaround
workaround_path = "/mnt/c/Users/z0052v7s/ws/AzureAD/teamcenter-auth-workaround"
if os.path.exists(workaround_path):
    sys.path.insert(0, workaround_path)

def test_cookie_auth():
    """Test that we can access cached cookie authentication"""
    try:
        # Try to import the working auth client
        from easy_auth_client import EasyAuthClient
        
        print("✅ Successfully imported EasyAuthClient")
        
        # Create client instance
        client = EasyAuthClient()
        
        # Check if we have a cached cookie
        if client.auth_cookie:
            print("✅ Found cached authentication cookie")
            print(f"📅 Cookie expires: {client.cookie_expiry}")
            
            # Test API call to health endpoint
            try:
                response = client.make_request("health")
                if response and response.status_code == 200:
                    print("✅ Health check passed with cached cookie")
                    print(f"📊 Response: {response.text[:100]}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status_code if response else 'No response'}")
                    return False
            except Exception as e:
                print(f"❌ API call failed: {e}")
                return False
        else:
            print("❌ No cached cookie found")
            print("💡 Run 'python easy_auth_client.py ask \"test\"' first to authenticate")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import EasyAuthClient: {e}")
        print(f"📂 Checking path: {workaround_path}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_cache_file():
    """Check if cache file exists and is readable"""
    cache_file = os.path.expanduser("~/.teamcenter_easy_auth_cache.json")
    cache_path = Path(cache_file)
    
    if cache_path.exists():
        print(f"✅ Cache file exists: {cache_file}")
        try:
            import json
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            print(f"📝 Cache contains: {list(cache_data.keys())}")
            return True
        except Exception as e:
            print(f"❌ Cache file exists but cannot be read: {e}")
            return False
    else:
        print(f"❌ Cache file not found: {cache_file}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Cookie Authentication Independence")
    print("=" * 50)
    
    # Check cache file first
    cache_ok = check_cache_file()
    print()
    
    # Test cookie auth
    auth_ok = test_cookie_auth()
    print()
    
    if cache_ok and auth_ok:
        print("🎉 Cookie authentication test PASSED")
        print("👍 Ready to extract auth logic for MCP server")
        sys.exit(0)
    else:
        print("⚠️  Cookie authentication test FAILED")
        print("💡 Ensure you've run easy_auth_client.py to authenticate first")
        sys.exit(1)