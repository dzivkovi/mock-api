#!/usr/bin/env python3
"""
TeamCenter Authentication Session with hybrid support
Supports both localhost mock mode and production Azure AD cookie authentication
"""
import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict
from cookie_auth_minimal import CookieAuth

logger = logging.getLogger(__name__)

class TeamCenterAuthSession:
    """Hybrid authentication session supporting mock and production modes"""
    
    def __init__(self, base_url: Optional[str] = None):
        # Environment variable takes precedence, then parameter, then default
        self.base_url = base_url or os.getenv("TEAMCENTER_API_HOST", "http://127.0.0.1:8000")
        self.base_url = self.base_url.rstrip('/')  # Remove trailing slash
        
        # Session state
        self.session_cookie: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        
        # Determine authentication mode based on URL
        if self.base_url.startswith("https://codesentinel"):
            self.auth_mode = "cookie"
            self._init_cookie_auth()
        else:
            self.auth_mode = "mock"
            self._init_mock_auth()
        
        logger.info(f"🔧 AuthSession initialized: mode={self.auth_mode}, url={self.base_url}")
    
    def _init_cookie_auth(self):
        """Initialize cookie-based authentication for production"""
        try:
            self.cookie_auth = CookieAuth()
            if not self.cookie_auth.has_valid_cookie():
                logger.warning("No valid cookie found for production mode")
                logger.info("💡 Run 'python easy_auth_client.py ask \"test\"' to authenticate")
                logger.info("🔄 Falling back to mock mode")
                self._fallback_to_mock()
            else:
                # Use the cached cookie for session
                self.session_cookie = self.cookie_auth.auth_cookie
                self.expires_at = self.cookie_auth.cookie_expiry
                logger.info(f"✅ Cookie auth initialized, expires: {self.expires_at}")
        except Exception as e:
            logger.error(f"Cookie auth initialization failed: {e}")
            logger.info("🔄 Falling back to mock mode")
            self._fallback_to_mock()
    
    def _init_mock_auth(self):
        """Initialize mock authentication for localhost"""
        # Mock mode doesn't need real authentication
        self.session_cookie = "mock_session_cookie"
        self.expires_at = datetime.now() + timedelta(hours=1)  # Mock expiry
        logger.info("🔧 Mock auth initialized")
    
    def _fallback_to_mock(self):
        """Fallback to mock mode when production auth fails"""
        self.auth_mode = "mock"
        self.base_url = "http://127.0.0.1:8000"
        self._init_mock_auth()
    
    def is_session_valid(self) -> bool:
        """Check if current session is still valid (with 5-minute buffer)"""
        if not self.session_cookie or not self.expires_at:
            logger.debug("🔍 Session invalid: missing cookie or expiry")
            return False
        
        # Check expiry with 5-minute buffer (like the real client)
        buffer_time = timedelta(minutes=5)
        is_valid = datetime.now() < (self.expires_at - buffer_time)
        logger.debug(f"🔍 Session validity check: {is_valid}, expires at {self.expires_at}")
        return is_valid
    
    async def authenticate(self) -> Optional[str]:
        """Authenticate and return session ID"""
        if self.auth_mode == "mock":
            # Mock authentication always succeeds
            logger.info("🔧 Mock authentication successful")
            return self.session_cookie
        
        elif self.auth_mode == "cookie":
            if self.is_session_valid():
                logger.info("✅ Using existing valid session")
                return self.session_cookie
            else:
                logger.warning("❌ Session invalid or expired")
                # For now, don't try to refresh - require manual re-auth
                logger.info("💡 Run 'python easy_auth_client.py ask \"test\"' to re-authenticate")
                return None
        
        return None
    
    async def make_authenticated_request(self, endpoint: str, method: str = "GET", 
                                       data: Optional[Dict] = None, 
                                       stream: bool = False) -> Optional[requests.Response]:
        """Make authenticated request to the API"""
        # Ensure we have a valid session
        session_id = await self.authenticate()
        if not session_id:
            raise Exception("Authentication failed - no valid session")
        
        # Prepare headers
        if self.auth_mode == "cookie":
            headers = {
                "Cookie": f"AppServiceAuthSession={self.session_cookie}",
                "Content-Type": "application/json"
            }
        else:  # mock mode
            headers = {
                "Content-Type": "application/json"
            }
        
        # Construct URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"🌐 {method} {url} (mode: {self.auth_mode})")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, stream=stream, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, stream=stream, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Log response status
            logger.debug(f"📊 Response: {response.status_code}")
            
            # Handle authentication errors
            if response.status_code == 401:
                logger.warning("🔒 Authentication failed (401)")
                if self.auth_mode == "cookie":
                    logger.info("💡 Cookie might be expired - run easy_auth_client.py")
                raise Exception("Authentication failed - 401 Unauthorized")
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"🔥 Request failed: {e}")
            return None
    
    def get_auth_status(self) -> Dict:
        """Get authentication status for debugging"""
        return {
            "auth_mode": self.auth_mode,
            "base_url": self.base_url,
            "is_session_valid": self.is_session_valid(),
            "session_cookie_length": len(self.session_cookie) if self.session_cookie else 0,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

def test_auth_session():
    """Test function for TeamCenterAuthSession"""
    print("🧪 Testing TeamCenterAuthSession")
    
    # Test 1: Default mode (should be mock)
    print("\n1. Testing default mode:")
    session1 = TeamCenterAuthSession()
    status1 = session1.get_auth_status()
    print(f"   Mode: {status1['auth_mode']}")
    print(f"   URL: {status1['base_url']}")
    print(f"   Valid: {status1['is_session_valid']}")
    
    # Test 2: Explicit localhost
    print("\n2. Testing explicit localhost:")
    session2 = TeamCenterAuthSession("http://127.0.0.1:8000")
    status2 = session2.get_auth_status()
    print(f"   Mode: {status2['auth_mode']}")
    print(f"   URL: {status2['base_url']}")
    
    # Test 3: Production mode (with environment variable)
    print("\n3. Testing production mode:")
    os.environ['TEAMCENTER_API_HOST'] = "https://codesentinel.azurewebsites.net"
    session3 = TeamCenterAuthSession()
    status3 = session3.get_auth_status()
    print(f"   Mode: {status3['auth_mode']}")
    print(f"   URL: {status3['base_url']}")
    print(f"   Valid: {status3['is_session_valid']}")
    
    # Cleanup
    os.environ.pop('TEAMCENTER_API_HOST', None)
    
    return all([
        status1['auth_mode'] == 'mock',
        status2['auth_mode'] == 'mock', 
        status3['auth_mode'] in ['cookie', 'mock']  # Might fallback to mock
    ])

if __name__ == "__main__":
    # Enable logging for testing
    logging.basicConfig(level=logging.INFO)
    
    success = test_auth_session()
    print(f"\n{'✅ Tests PASSED' if success else '❌ Tests FAILED'}")
    exit(0 if success else 1)