#!/usr/bin/env python3
"""
Test script to validate the lightweight ICI Chat solution for Cloud Run deployment.
This script tests core functionality without heavy ML dependencies.
"""

import sys
import os
import time
import json
from threading import Thread

print("🧪 ICI Chat Lightweight Solution Test Suite")
print("=" * 50)

def test_imports():
    """Test that all backend imports work correctly"""
    print("\n🔍 Testing Imports...")
    
    try:
        # Test core backend imports
        sys.path.insert(0, os.path.dirname(__file__))
        from backend.factory import create_app
        print("✅ PASS: Backend Factory Import")
        return True
    except Exception as e:
        print(f"❌ FAIL: Backend Factory Import - {e}")
        return False

def test_memory_functions():
    """Test lightweight memory functions"""
    print("\n💭 Testing Memory Functions...")
    
    try:
        from backend.utils.memory_utils import (
            is_statement_worth_remembering,
            is_question_seeking_memory,
            store_information_in_memory,
            search_memory_for_context
        )
        
        # Test statement recognition
        assert is_statement_worth_remembering("Tommy should go at 2pm") == True
        assert is_statement_worth_remembering("Hello world") == False
        
        # Test question recognition
        assert is_question_seeking_memory("When should Tommy go?") == True
        assert is_question_seeking_memory("Hello there") == False
        
        print("✅ PASS: Memory Functions")
        return True
    except Exception as e:
        print(f"❌ FAIL: Memory Functions - {e}")
        return False

def test_app_creation():
    """Test Flask app creation"""
    print("\n🏗️ Testing App Creation...")
    
    try:
        from backend.factory import create_app
        app, socketio = create_app()
        
        assert app is not None
        assert socketio is not None
        
        print("✅ PASS: App Creation")
        return True
    except Exception as e:
        print(f"❌ FAIL: App Creation - {e}")
        return False

def test_resource_requirements():
    """Test that heavy dependencies are removed"""
    print("\n📦 Testing Dependency Requirements...")
    
    try:
        # These should fail to import (good!)
        heavy_deps = ['transformers', 'torch', 'sentence_transformers', 'faiss']
        
        for dep in heavy_deps:
            try:
                __import__(dep)
                print(f"❌ FAIL: Heavy dependency '{dep}' is still available")
                return False
            except ImportError:
                print(f"✅ GOOD: Heavy dependency '{dep}' successfully removed")
        
        print("✅ PASS: Dependency Requirements")
        return True
    except Exception as e:
        print(f"❌ FAIL: Dependency Requirements - {e}")
        return False

def run_all_tests():
    """Run all tests"""
    tests = [
        test_imports,
        test_memory_functions,
        test_app_creation,
        test_resource_requirements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ FAIL: {test.__name__} crashed - {e}")
    
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Solution ready for Cloud Run deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Please review before deployment.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test suite crashed: {e}")
        sys.exit(1)
