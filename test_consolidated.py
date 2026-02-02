#!/usr/bin/env python3
"""
Test Consolidated Flask App
Quick validation that everything works
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from services.wechat_service import WeChatService
        from services.ai_service import AIService
        print("✓ Services imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_service_initialization():
    """Test that services can be initialized"""
    print("\nTesting service initialization...")
    try:
        from services.wechat_service import WeChatService
        from services.ai_service import AIService

        wechat = WeChatService()
        print(f"✓ WeChat service initialized (chats: {wechat.chat_names})")

        ai = AIService()
        print(f"✓ AI service initialized (model: {ai.model})")

        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_wechat_detection():
    """Test WeChat detection"""
    print("\nTesting WeChat detection...")
    try:
        from services.wechat_service import WeChatService

        wechat = WeChatService()
        is_running = wechat.is_wechat_running()

        if is_running:
            print("✓ WeChat is running")
        else:
            print("⚠ WeChat is not running (this is OK for testing)")

        return True
    except Exception as e:
        print(f"✗ WeChat detection failed: {e}")
        return False

def test_ai_status():
    """Test AI service status"""
    print("\nTesting AI service status...")
    try:
        from services.ai_service import AIService

        ai = AIService()
        status = ai.get_status()

        print(f"✓ AI Provider: {status['provider']}")
        print(f"✓ Model: {status['model']}")
        print(f"✓ API Key: {'Configured' if status['api_key_configured'] else 'Not configured'}")

        return True
    except Exception as e:
        print(f"✗ AI status check failed: {e}")
        return False

def test_flask_app():
    """Test Flask app can be imported"""
    print("\nTesting Flask app...")
    try:
        # Just test import, don't run
        import app_consolidated
        print("✓ Flask app imported successfully")
        return True
    except Exception as e:
        print(f"✗ Flask app import failed: {e}")
        return False

def main():
    print("=" * 60)
    print("RealChat Consolidated - Quick Validation Test")
    print("=" * 60)
    print()

    tests = [
        test_imports,
        test_service_initialization,
        test_wechat_detection,
        test_ai_status,
        test_flask_app
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append(False)

    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed! Ready to run.")
        return 0
    else:
        print("⚠ Some tests failed. Check errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
