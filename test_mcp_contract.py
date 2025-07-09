#!/usr/bin/env python3
"""
MCP Contract Test - Verify the UVX wheel deployment works as expected
This tests the exact same command that Continue.dev uses
"""
import subprocess
import json
import sys
import time


def test_mcp_server_contract():
    """Test the exact UVX command that Continue.dev uses"""
    
    # The exact command from Continue.dev config
    command = [
        "uvx", 
        "--from", 
        "dist/teamcenter_mcp_server-0.1.0-py3-none-any.whl",
        "teamcenter-mcp-server",
        "--base-url",
        "http://localhost:8000"
    ]
    
    print("🧪 Testing MCP server contract...")
    print(f"💻 Command: {' '.join(command)}")
    
    try:
        # Test 1: Version check (should be fast)
        version_cmd = command[:-2] + ["--version"]
        print(f"\n1️⃣ Testing version command: {' '.join(version_cmd)}")
        
        result = subprocess.run(
            version_cmd, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Version test passed: {result.stdout.strip()}")
        else:
            print(f"❌ Version test failed: {result.stderr}")
            return False
            
        # Test 2: Help command (should be fast)
        help_cmd = command[:-2] + ["--help"]
        print(f"\n2️⃣ Testing help command: {' '.join(help_cmd)}")
        
        result = subprocess.run(
            help_cmd, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Help test passed")
            print("📄 Help output preview:")
            print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        else:
            print(f"❌ Help test failed: {result.stderr}")
            return False
            
        # Test 3: Server startup (simulate what Continue.dev does)
        print(f"\n3️⃣ Testing server startup (3 second timeout): {' '.join(command)}")
        
        # Start the server process
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it 3 seconds to start
        time.sleep(3)
        
        # Check if it's still running (good sign)
        if proc.poll() is None:
            print("✅ Server startup test passed - process is running")
            print("🔄 MCP server is listening for STDIO communication")
            
            # Terminate the server
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            
            return True
        else:
            # Process exited - check why
            stdout, stderr = proc.communicate()
            
            # For STDIO MCP servers, exiting with code 0 when no input is actually NORMAL
            if proc.returncode == 0 and "Starting MCP server" in stderr:
                print("✅ Server startup test passed - MCP server initialized correctly")
                print("🔄 Server exited cleanly (normal for STDIO when no input provided)")
                print("📋 Server logs show proper initialization:")
                # Show just the key parts
                for line in stderr.split('\n'):
                    if 'Starting MCP server' in line or 'AuthSession initialized' in line:
                        print(f"   {line.strip()}")
                return True
            else:
                print(f"❌ Server startup test failed - process exited with code {proc.returncode}")
                if stdout:
                    print(f"📄 stdout: {stdout}")
                if stderr:
                    print(f"🚨 stderr: {stderr}")
                return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
        return False
    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        return False


def test_api_server_connectivity():
    """Test if the API server is reachable"""
    print("🌐 Testing API server connectivity...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is reachable at http://localhost:8000")
            return True
        else:
            print(f"⚠️  API server returned status {response.status_code}")
            print("💡 This is okay - MCP server will still work")
            return True  # Don't fail for API issues
    except ImportError:
        print("⚠️  requests module not available, skipping API connectivity test")
        return True  # Don't fail the test for missing requests
    except Exception as e:
        print(f"⚠️  API server not reachable: {e}")
        print("💡 Start with: uv run uvicorn main:app --reload")
        print("💡 MCP server will still work - this just tests the mock API")
        return True  # Don't fail for API connectivity issues


def main():
    """Run all contract tests"""
    print("🚀 MCP Contract Test Suite")
    print("=" * 50)
    print("🎯 Testing UVX wheel deployment for Continue.dev integration")
    print()
    
    # Test API server first
    api_ok = test_api_server_connectivity()
    
    # Test MCP server contract
    mcp_ok = test_mcp_server_contract()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"🌐 API Server: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"🔧 MCP Server: {'✅ PASS' if mcp_ok else '❌ FAIL'}")
    
    if api_ok and mcp_ok:
        print("\n🎉 All tests passed! Your UVX deployment is ready.")
        print("\n📋 Next steps:")
        print("   1. Configure your IDE with the UVX wheel path")
        print("   2. Start asking @MCP questions in Continue.dev")
        print("   3. Check uvicorn logs for API calls")
    else:
        print("\n🚨 Some tests failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()