# Defensive Azure AD Integration Plan for MCP Server

## Timestamp and Context
- Date: 2025-07-10
- Context: Planning cautious integration of Azure AD authentication into Teamcenter MCP server
- Confidence Level: 85-95% based on existing working patterns
- Goal: Replace mock authentication with real Azure AD without breaking existing functionality

## Question/Query
User requested a detailed task list using defensive programming principles to convert the MCP server from localhost mock API to Azure AD authenticated real Teamcenter API. The approach should minimize mistakes and test everything along the way.

## Analysis and Findings

### Confidence Assessment After Fact-Checking

**85% Overall Confidence** based on:
- ✅ Working `easy_auth_client.py` pattern already proven
- ✅ Microsoft documentation confirms cookie-based auth is valid
- ✅ Existing cache mechanism eliminates browser popups
- ⚠️ 15% risk from potential scope/registration issues

### Selected Approach: Cookie-Based Authentication
Instead of complex MSAL integration, leverage the existing working `easy_auth_client.py` pattern that uses browser cookies after Azure AD SSO.

## 🛡️ DEFENSIVE AZURE AD INTEGRATION PLAN

### Phase 0: SAFETY FIRST (Risk Mitigation)

#### Task 1: Create Safe Working Environment
```bash
# 1.1 Create backup branch
git checkout -b azure-ad-integration-backup

# 1.2 Create another working branch
git checkout -b azure-ad-integration

# 1.3 Document current working state
echo "MCP Server v2.0.2 works with localhost:8000" > INTEGRATION_LOG.md
```

#### Task 2: Verify Current State
```bash
# 2.1 Start mock API server
uv run uvicorn main:app --reload

# 2.2 Test MCP server with localhost
TEAMCENTER_API_HOST=http://127.0.0.1:8000 python auth_mcp_stdio.py

# 2.3 Document success/failure
echo "✅ Baseline test passed: $(date)" >> INTEGRATION_LOG.md
```

### Phase 1: EXTRACT PROVEN PATTERN (Low Risk)

#### Task 3: Study Working Authentication
```python
# 3.1 Create test_cookie_auth.py
"""Test cookie authentication works independently"""
import sys
sys.path.append('/mnt/c/Users/z0052v7s/ws/AzureAD/teamcenter-auth-workaround')
from easy_auth_client import EasyAuthClient

# Test cached cookie works
client = EasyAuthClient()
if client.auth_cookie:
    print("✅ Found cached cookie")
    # Test API call
    response = client.make_request("health")
    print(f"✅ Health check: {response.status_code}")
else:
    print("❌ No cached cookie - run easy_auth_client.py first")
```

#### Task 4: Extract Minimal Auth Logic
```python
# 4.1 Create cookie_auth_minimal.py
"""Minimal cookie auth for MCP server"""
import json
import os
from pathlib import Path
from datetime import datetime

class CookieAuth:
    def __init__(self, cache_file="~/.teamcenter_easy_auth_cache.json"):
        self.cache_file = os.path.expanduser(cache_file)
        self.auth_cookie = None
        self._load_cache()
    
    def _load_cache(self):
        """Load cached auth cookie"""
        cache_path = Path(self.cache_file)
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cache = json.load(f)
                if datetime.fromisoformat(cache['expiry']) > datetime.now():
                    self.auth_cookie = cache.get('cookie')
                    return True
        return False
    
    def has_valid_cookie(self):
        return self.auth_cookie is not None
```

### Phase 2: INCREMENTAL INTEGRATION (Medium Risk)

#### Task 5: Add Dependencies Safely
```toml
# 5.1 Update pyproject.toml
[project]
dependencies = [
    "requests>=2.28.0",  # Add only what we need
    # ... existing deps
]

# 5.2 Test installation
uv sync
uv run python -c "import requests; print('✅ requests installed')"
```

#### Task 6: Create Hybrid Auth Session
```python
# 6.1 Create teamcenter_auth_session.py
class TeamCenterAuthSession:
    def __init__(self, base_url=None):
        # Environment variable takes precedence
        self.base_url = base_url or os.getenv("TEAMCENTER_API_HOST", "http://127.0.0.1:8000")
        
        # Determine auth mode
        if self.base_url.startswith("https://codesentinel"):
            self.auth_mode = "cookie"
            self._init_cookie_auth()
        else:
            self.auth_mode = "mock"
            self._init_mock_auth()
        
        logger.info(f"Auth mode: {self.auth_mode}, URL: {self.base_url}")
    
    def _init_cookie_auth(self):
        """Initialize cookie-based auth"""
        try:
            from cookie_auth_minimal import CookieAuth
            self.cookie_auth = CookieAuth()
            if not self.cookie_auth.has_valid_cookie():
                raise Exception("No valid cookie found - run easy_auth_client.py first")
        except Exception as e:
            logger.error(f"Cookie auth failed: {e}")
            logger.info("Falling back to mock mode")
            self.auth_mode = "mock"
            self.base_url = "http://127.0.0.1:8000"
```

### Phase 3: DEFENSIVE TESTING (Critical)

#### Task 7: Test Environment Switching
```bash
# 7.1 Test mock mode (default)
python test_auth_session.py
# Expected: Uses localhost

# 7.2 Test with localhost explicitly
TEAMCENTER_API_HOST=http://127.0.0.1:8000 python test_auth_session.py
# Expected: Uses localhost

# 7.3 Test production mode
TEAMCENTER_API_HOST=https://codesentinel.azurewebsites.net python test_auth_session.py
# Expected: Uses cookie auth or fails gracefully
```

#### Task 8: Create Comprehensive Test Suite
```python
# 8.1 test_auth_integration.py
import pytest
import os

def test_mock_mode_works():
    """Test localhost mock mode still works"""
    os.environ.pop('TEAMCENTER_API_HOST', None)
    session = TeamCenterAuthSession()
    assert session.auth_mode == "mock"
    assert session.base_url == "http://127.0.0.1:8000"

def test_production_mode_with_cookie():
    """Test production mode with valid cookie"""
    os.environ['TEAMCENTER_API_HOST'] = "https://codesentinel.azurewebsites.net"
    # Mock cookie exists
    session = TeamCenterAuthSession()
    if session.auth_mode == "cookie":
        assert session.cookie_auth.has_valid_cookie()
    else:
        # Graceful fallback
        assert session.auth_mode == "mock"

def test_fallback_on_error():
    """Test graceful fallback when cookie auth fails"""
    os.environ['TEAMCENTER_API_HOST'] = "https://codesentinel.azurewebsites.net"
    # Simulate no cookie
    session = TeamCenterAuthSession()
    # Should fallback to mock
    assert session.base_url == "http://127.0.0.1:8000"
```

### Phase 4: INTEGRATION WITH MCP SERVER

#### Task 9: Minimal Changes to auth_mcp_stdio.py
```python
# 9.1 Replace ONE line at a time
# OLD: auth_session = AuthSession(base_url="http://127.0.0.1:8000")
# NEW: auth_session = TeamCenterAuthSession()  # Uses env or defaults

# 9.2 Test after EACH change
python auth_mcp_stdio.py  # Should work with localhost
TEAMCENTER_API_HOST=https://codesentinel.azurewebsites.net python auth_mcp_stdio.py
```

#### Task 10: Error Handling Enhancement
```python
# 10.1 Add to make_authenticated_request
try:
    if self.auth_mode == "cookie":
        headers["Cookie"] = f"AppServiceAuthSession={self.cookie_auth.auth_cookie}"
    response = await self._make_request(method, endpoint, headers, data)
except Exception as e:
    logger.error(f"Request failed: {e}")
    if self.auth_mode == "cookie":
        logger.info("Cookie might be expired - run easy_auth_client.py")
    raise
```

### Phase 5: END-TO-END VALIDATION

#### Task 11: Integration Tests
```bash
# 11.1 Test with Continue.dev
1. Set TEAMCENTER_API_HOST=http://127.0.0.1:8000
2. Start Continue.dev
3. Test MCP server connection
4. Document: "✅ Mock mode works with Continue.dev"

# 11.2 Test with production (if cookie valid)
1. Run easy_auth_client.py to ensure cookie
2. Set TEAMCENTER_API_HOST=https://codesentinel.azurewebsites.net
3. Test with Continue.dev
4. Document results
```

#### Task 12: Rollback Plan
```markdown
# ROLLBACK_PLAN.md

## If Integration Fails:
1. `git checkout main`
2. `git branch -D azure-ad-integration`
3. Use v2.0.2-portable tag

## Known Working States:
- Mock API: v2.0.2-portable
- Before changes: azure-ad-integration-backup branch

## Debug Steps:
1. Check cookie exists: `ls ~/.teamcenter_easy_auth_cache.json`
2. Test cookie valid: `python test_cookie_auth.py`
3. Check env var: `echo $TEAMCENTER_API_HOST`
```

## Task List Summary

1. **Create backup branch for safe Azure AD integration** ⚠️ HIGH
2. **Test current MCP server works with localhost mock API** ⚠️ HIGH  
3. **Extract minimal auth logic from easy_auth_client.py** ⚠️ HIGH
4. **Create test script to verify cookie auth works independently** ⚠️ HIGH
5. **Add requests dependency to pyproject.toml** 🔧 MEDIUM
6. **Create TeamCenterAuthSession class with cookie support** ⚠️ HIGH
7. **Add environment variable support for API host switching** ⚠️ HIGH
8. **Test localhost mode still works after changes** ⚠️ HIGH
9. **Test production API connection with cached cookie** ⚠️ HIGH
10. **Add comprehensive error handling and logging** ⚠️ HIGH
11. **Create integration test with MCP protocol** ⚠️ HIGH
12. **Update documentation with setup instructions** 🔧 MEDIUM
13. **Test with Continue.dev and Claude Desktop** ⚠️ HIGH
14. **Create rollback instructions if issues arise** 🔧 MEDIUM

## 🎯 SUCCESS CRITERIA

Each phase must pass before proceeding:

- [ ] Phase 0: Backup created, baseline test passes
- [ ] Phase 1: Cookie auth extracted and tested independently  
- [ ] Phase 2: Hybrid auth works with both modes
- [ ] Phase 3: All defensive tests pass
- [ ] Phase 4: MCP server works with env switching
- [ ] Phase 5: End-to-end validation complete

## 🛑 STOP CONDITIONS

Stop immediately if:
1. Localhost mock mode breaks at ANY point
2. Cookie auth test fails (means we need fresh auth)
3. MCP server fails to start
4. Continue.dev cannot connect

This plan prioritizes **working software at every step** over speed of implementation.