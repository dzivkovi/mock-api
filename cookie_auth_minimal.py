#!/usr/bin/env python3
"""
Minimal cookie auth for MCP server
Extracted from working easy_auth_client.py pattern
"""
import json
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CookieAuth:
    """Minimal cookie authentication using cached credentials"""
    
    def __init__(self, cache_file=None):
        # Use Windows cache file location by default
        if cache_file is None:
            windows_cache = "/mnt/c/Users/z0052v7s/.teamcenter_easy_auth_cache.json"
            linux_cache = os.path.expanduser("~/.teamcenter_easy_auth_cache.json")
            
            # Prefer Windows cache if available
            if os.path.exists(windows_cache):
                cache_file = windows_cache
            else:
                cache_file = linux_cache
        
        self.cache_file = cache_file
        self.auth_cookie = None
        self.cookie_expiry = None
        self.user_info = None
        self._load_cache()
    
    def _load_cache(self):
        """Load cached auth cookie if available and not expired"""
        try:
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    cache = json.load(f)
                
                # Check expiry
                expiry_str = cache.get('expiry')
                if expiry_str:
                    expiry = datetime.fromisoformat(expiry_str)
                    if expiry > datetime.now():
                        self.auth_cookie = cache.get('cookie')
                        self.cookie_expiry = expiry
                        self.user_info = cache.get('user_info', {})
                        logger.info(f"Loaded valid cookie, expires: {expiry}")
                        return True
                    else:
                        logger.warning(f"Cached cookie expired: {expiry}")
                else:
                    logger.warning("No expiry found in cache")
            else:
                logger.info(f"Cache file not found: {cache_path}")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
        
        return False
    
    def has_valid_cookie(self):
        """Check if we have a valid authentication cookie"""
        if not self.auth_cookie or not self.cookie_expiry:
            return False
        
        # Check if still valid (with small buffer)
        return datetime.now() < self.cookie_expiry
    
    def get_auth_headers(self):
        """Get authentication headers for API requests"""
        if self.has_valid_cookie():
            return {
                "Cookie": f"AppServiceAuthSession={self.auth_cookie}",
                "Content-Type": "application/json"
            }
        else:
            raise Exception("No valid authentication cookie available")
    
    def get_user_info(self):
        """Get user information from cache"""
        return self.user_info or {}

def test_cookie_auth():
    """Test function to verify cookie auth works"""
    print("🧪 Testing CookieAuth class")
    
    auth = CookieAuth()
    
    if auth.has_valid_cookie():
        print("✅ Valid cookie found")
        print(f"📅 Expires: {auth.cookie_expiry}")
        
        user_info = auth.get_user_info()
        if user_info:
            print(f"👤 User: {user_info.get('name', 'Unknown')}")
            print(f"📧 Email: {user_info.get('email', 'Unknown')}")
        
        try:
            headers = auth.get_auth_headers()
            print("✅ Auth headers generated successfully")
            # Don't print the actual cookie for security
            print(f"🔑 Cookie length: {len(headers.get('Cookie', ''))}")
            return True
        except Exception as e:
            print(f"❌ Failed to get auth headers: {e}")
            return False
    else:
        print("❌ No valid cookie found")
        print("💡 Run 'python easy_auth_client.py ask \"test\"' to authenticate first")
        return False

if __name__ == "__main__":
    # Enable logging for testing
    logging.basicConfig(level=logging.INFO)
    
    success = test_cookie_auth()
    exit(0 if success else 1)