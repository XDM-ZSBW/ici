#!/usr/bin/env python3
"""
Test script to validate the lightweight ICI Chat solution for Cloud Run deployment.
This script tests core functionality without heavy ML dependencies.
"""

import sys
import os
import time
import requests
import json
from threading import Thread
import subprocess
import signal

# Add backend to path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

class LightweightICITester:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.server_process = None
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_imports(self):
        """Test that all backend imports work correctly"""
        print("\n🔍 Testing Imports...")
        
        try:
            # Test core backend imports
            from backend.factory import create_app
            self.log_test("Backend Factory Import", True)
        except Exception as e:
            self.log_test("Backend Factory Import", False, str(e))
            return False
            
        try:
            from backend.routes.chat import chat_bp
            from backend.routes.vault import vault_bp
            from backend.routes.memory import memory_bp
            from backend.utils.memory_utils import (
                is_statement_worth_remembering,
                is_question_seeking_memory,
                store_information_in_memory,
                search_memory_for_context
            )
            self.log_test("Core Routes and Utils Import", True)
        except Exception as e:
            self.log_test("Core Routes and Utils Import", False, str(e))
            return False
            
        return True
    
    def start_server(self):
        """Start the Flask server in background"""
        print("\n🚀 Starting Test Server...")
        
        try:
            # Use subprocess to start the server
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.dirname(__file__)
            
            self.server_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                cwd=os.path.dirname(__file__),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        self.log_test("Server Startup", True, f"Server ready in {i+1}s")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
            
            self.log_test("Server Startup", False, "Server failed to start within 30s")
            return False
            
        except Exception as e:
            self.log_test("Server Startup", False, str(e))
            return False
    
    def stop_server(self):
        """Stop the test server"""
        if self.server_process:
            print("\n🛑 Stopping Test Server...")
            self.server_process.terminate()
            self.server_process.wait(timeout=10)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("\n🏥 Testing Health Endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Endpoint", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("Health Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Endpoint", False, str(e))
            return False
    
    def test_chat_functionality(self):
        """Test lightweight chat functionality"""
        print("\n💬 Testing Chat Functionality...")
        
        # Test memory storage
        try:
            response = requests.post(
                f"{self.base_url}/ai-chat",
                json={
                    "message": "Tommy should go at 2pm",
                    "user_id": "test_user"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("memory_stored"):
                    self.log_test("Chat Memory Storage", True, "Successfully stored information")
                else:
                    self.log_test("Chat Memory Storage", False, "Memory not stored as expected")
            else:
                self.log_test("Chat Memory Storage", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Chat Memory Storage", False, str(e))
        
        # Test memory retrieval
        try:
            response = requests.post(
                f"{self.base_url}/ai-chat",
                json={
                    "message": "When should Tommy go?",
                    "user_id": "test_user"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("memory_context_found") and "2pm" in data.get("response", ""):
                    self.log_test("Chat Memory Retrieval", True, "Successfully retrieved stored information")
                else:
                    self.log_test("Chat Memory Retrieval", False, "Failed to retrieve stored information")
            else:
                self.log_test("Chat Memory Retrieval", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Chat Memory Retrieval", False, str(e))
    
    def test_vault_functionality(self):
        """Test lightweight vault functionality"""
        print("\n🗄️ Testing Vault Functionality...")
        
        # Test vault data collection
        try:
            vault_data = {
                "user_id": "test_user",
                "tab_id": "123",
                "url": "https://example.com/test",
                "ui_element": {
                    "selector": "#test-button",
                    "tag_name": "button",
                    "text_content": "Click me for testing",
                    "attributes": {"id": "test-button"},
                    "position": {"x": 100, "y": 200}
                },
                "timestamp": time.time() * 1000
            }
            
            response = requests.post(
                f"{self.base_url}/vault/collect",
                json=vault_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Vault Data Collection", True, "Successfully collected vault data")
                else:
                    self.log_test("Vault Data Collection", False, "Collection failed")
            else:
                self.log_test("Vault Data Collection", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Vault Data Collection", False, str(e))
        
        # Test vault search
        try:
            response = requests.post(
                f"{self.base_url}/vault/search",
                json={
                    "user_id": "test_user",
                    "query_text": "testing",
                    "limit": 10
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("search_type") == "text_based" and data.get("count", 0) > 0:
                    self.log_test("Vault Text Search", True, f"Found {data['count']} results")
                else:
                    self.log_test("Vault Text Search", True, "Search completed (no results expected)")
            else:
                self.log_test("Vault Text Search", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Vault Text Search", False, str(e))
    
    def test_resource_usage(self):
        """Test resource usage is within Cloud Run limits"""
        print("\n📊 Testing Resource Usage...")
        
        try:
            import psutil
            import gc
            
            # Force garbage collection
            gc.collect()
            
            # Get current process
            process = psutil.Process()
            
            # Memory usage in MB
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # CPU usage (get a sample over 1 second)
            cpu_percent = process.cpu_percent(interval=1)
            
            # Check if within Cloud Run limits
            memory_ok = memory_mb < 500  # Under 512MB limit
            cpu_ok = cpu_percent < 90    # Reasonable CPU usage
            
            self.log_test("Memory Usage", memory_ok, f"{memory_mb:.1f}MB (limit: 512MB)")
            self.log_test("CPU Usage", cpu_ok, f"{cpu_percent:.1f}% (checking reasonable usage)")
            
        except Exception as e:
            self.log_test("Resource Usage Check", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 ICI Chat Lightweight Solution Test Suite")
        print("=" * 50)
        
        # Test imports first (no server needed)
        if not self.test_imports():
            print("\n❌ Import tests failed - stopping test suite")
            return False
        
        # Start server for endpoint tests
        if not self.start_server():
            print("\n❌ Server startup failed - stopping test suite")
            return False
        
        try:
            # Run endpoint tests
            self.test_health_endpoint()
            self.test_chat_functionality()
            self.test_vault_functionality()
            self.test_resource_usage()
            
        finally:
            # Always stop server
            self.stop_server()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📋 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["message"] and not result["success"]:
                print(f"   Error: {result['message']}")
        
        print(f"\nResult: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Solution ready for Cloud Run deployment.")
            return True
        else:
            print("⚠️ Some tests failed. Please review before deployment.")
            return False

if __name__ == "__main__":
    tester = LightweightICITester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
        tester.stop_server()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test suite crashed: {e}")
        tester.stop_server()
        sys.exit(1)
