#!/usr/bin/env python3
"""
Quick test script to verify all components are working.
Run this to diagnose any issues with the chatbot.
"""

import sys
import os
import traceback

def test_imports():
    """Test that all required modules can be imported."""
    print("\n📦 Testing imports...")
    required_modules = {
        "fastapi": "FastAPI web framework",
        "sqlalchemy": "Database ORM",
        "pydantic": "Data validation",
        "uvicorn": "ASGI server",
    }
    
    failed = []
    for module, desc in required_modules.items():
        try:
            __import__(module)
            print(f"  ✓ {module:20} - {desc}")
        except ImportError as e:
            print(f"  ✗ {module:20} - {desc}")
            failed.append((module, str(e)))
    
    return len(failed) == 0, failed

def test_database():
    """Test database initialization and connection."""
    print("\n🗄️  Testing database...")
    try:
        from models import SessionLocal, Knowledge, User, Base, engine
        
        # Test connection
        db = SessionLocal()
        db_ok = db.query(Knowledge).count()
        db.close()
        
        print(f"  ✓ Database connection successful")
        print(f"  ✓ Knowledge entries in DB: {db_ok}")
        
        return True, None
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        traceback.print_exc()
        return False, str(e)

def test_admin():
    """Test admin user initialization."""
    print("\n👤 Testing admin user...")
    try:
        from app import ensure_default_admin, hash_password
        from models import SessionLocal, User
        
        ensure_default_admin()
        
        db = SessionLocal()
        admin = db.query(User).filter(User.username == "admin").first()
        db.close()
        
        if admin:
            print(f"  ✓ Admin user exists")
            print(f"  ✓ Username: {admin.username}")
            print(f"  ✓ Role: {admin.role}")
            return True, None
        else:
            print(f"  ✗ Admin user not found")
            return False, "Admin user creation failed"
    except Exception as e:
        print(f"  ✗ Admin error: {e}")
        traceback.print_exc()
        return False, str(e)

def test_chat():
    """Test chat functionality."""
    print("\n💬 Testing chat endpoints...")
    try:
        from app import chat, detect_intent, search_knowledge, ChatRequest
        
        # Test intent detection
        result = detect_intent("How to prevent diseases?")
        print(f"  ✓ Intent detection works: '{result}'")
        
        # Test chat function
        request = ChatRequest(message="test question", language="en")
        response = chat(req=request)
        if "reply" in response:
            print(f"  ✓ Chat endpoint works")
            print(f"  ✓ Response: {response['reply'][:50]}...")
            return True, None
        else:
            print(f"  ✗ Chat endpoint returned invalid response")
            return False, "Invalid response format"
            
    except Exception as e:
        print(f"  ✗ Chat error: {e}")
        traceback.print_exc()
        return False, str(e)

def test_files():
    """Check required files exist."""
    print("\n📁 Checking required files...")
    required_files = [
        ("app.py", "Main application"),
        ("models.py", "Database models"),
        ("requirements.txt", "Dependencies"),
        ("static/index.html", "Admin UI"),
        ("database/", "Database folder"),
    ]
    
    all_ok = True
    for filename, desc in required_files:
        if os.path.exists(filename):
            print(f"  ✓ {filename:30} - {desc}")
        else:
            print(f"  ✗ {filename:30} - {desc} (MISSING)")
            all_ok = False
    
    return all_ok, None

def main():
    print("\n" + "="*60)
    print("  🌾 AI FARMING CHATBOT - DIAGNOSTIC TEST")
    print("="*60)
    
    tests = [
        ("Files", test_files),
        ("Imports", test_imports),
        ("Database", test_database),
        ("Admin User", test_admin),
        ("Chat System", test_chat),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success, error = test_func()
            results.append((name, success, error))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            traceback.print_exc()
            results.append((name, False, str(e)))
    
    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status:10} - {name}")
        if error:
            print(f"           Error: {error}")
    
    print("\n" + "-"*60)
    print(f"  {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Your chatbot is ready to run.")
        print("\n   Run: python run.py")
        print("   Then visit: http://localhost:8000")
        return 0
    else:
        print("\n⚠️  Some tests failed. See errors above.")
        if passed < total:
            print("\n   Try running: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
