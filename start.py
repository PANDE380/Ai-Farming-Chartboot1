#!/usr/bin/env python3
"""
🌾 AI FARMING CHATBOT - QUICK START GUIDE

This script provides an interactive setup experience.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print welcome banner."""
    banner = """
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        🌾  AI FARMING CHATBOT - QUICK START  🌾          ║
║                                                            ║
║   A Conversational AI for Agricultural Assistance         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python():
    """Check Python version."""
    print("📌 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor} (requires 3.8+)")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing dependencies...")
    print("   (This may take a few minutes...)\n")
    
    cmd = f"{sys.executable} -m pip install -r requirements.txt -q"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ All dependencies installed")
            return True
        else:
            print("   ✗ Failed to install dependencies")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ✗ Installation error: {e}")
        return False

def initialize_database():
    """Initialize database."""
    print("\n🗄️  Initializing database...")
    
    try:
        from models import Base, engine
        Base.metadata.create_all(bind=engine)
        print("   ✓ Database created/verified")
        return True
    except Exception as e:
        print(f"   ✗ Database error: {e}")
        return False

def create_admin():
    """Create/verify admin user."""
    print("\n👤 Setting up admin user...")
    
    try:
        from app import ensure_default_admin
        from models import SessionLocal, User
        
        ensure_default_admin()
        
        db = SessionLocal()
        admin = db.query(User).filter(User.username == "admin").first()
        db.close()
        
        if admin:
            print("   ✓ Admin user verified")
            print("   ✓ Default credentials: admin / admin123")
            return True
        else:
            print("   ✗ Failed to create admin user")
            return False
    except Exception as e:
        print(f"   ✗ Admin setup error: {e}")
        return False

def import_dataset():
    """Optionally import dataset."""
    print("\n📊 Checking for dataset...")
    
    if not os.path.exists("a sample_Farming_FAQ_Assistant_Dataset.csv"):
        print("   ℹ Dataset file not found (optional)")
        return True
    
    print("   Found dataset. Importing...")
    
    try:
        from import_dataset import import_dataset
        return import_dataset()
    except Exception as e:
        print(f"   ⚠ Dataset import failed (non-critical): {e}")
        return True

def run_diagnostics():
    """Run diagnostic tests."""
    print("\n🧪 Running diagnostics...")
    
    tests_passed = 0
    tests_total = 3
    
    # Test 1: Imports
    try:
        from fastapi import FastAPI
        from sqlalchemy import create_engine
        from pydantic import BaseModel
        print("   ✓ All required modules found")
        tests_passed += 1
    except ImportError as e:
        print(f"   ✗ Missing module: {e}")
    
    # Test 2: Database
    try:
        from models import SessionLocal, Knowledge
        db = SessionLocal()
        count = db.query(Knowledge).count()
        db.close()
        print(f"   ✓ Database connected ({count} entries)")
        tests_passed += 1
    except Exception as e:
        print(f"   ✗ Database error: {e}")
    
    # Test 3: Chat system
    try:
        from app import chat, detect_intent, ChatRequest
        req = ChatRequest(message="test", language="en")
        response = chat(req=req)
        if "reply" in response:
            print("   ✓ Chat system ready")
            tests_passed += 1
        else:
            print("   ✗ Chat system returned invalid response")
    except Exception as e:
        print(f"   ✗ Chat error: {e}")
    
    return tests_passed == tests_total

def start_server():
    """Ask user if they want to start the server."""
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    
    print("\n📖 Documentation:")
    print("   - README.md: Full documentation")
    print("   - .env.example: Configuration template")
    
    print("\n🚀 Next steps:")
    print("   1. Run: python run.py")
    print("   2. Open: http://localhost:8000")
    print("   3. Login: admin / admin123")
    
    print("\n💬 API Examples:")
    print("   Chat:    POST http://localhost:8000/chat")
    print("   Admin:   POST http://localhost:8000/admin/login")
    print("   Docs:    http://localhost:8000/docs")
    
    print("\n" + "="*60)
    
    choice = input("\nWould you like to start the server now? (y/n): ").strip().lower()
    return choice in ['y', 'yes']

def main():
    """Main setup flow."""
    print_banner()
    
    # Step 1: Check Python
    if not check_python():
        print("\n✗ Setup failed: Python 3.8+ required")
        return False
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n✗ Setup failed: Could not install dependencies")
        print("\nTry running manually:")
        print(f"  {sys.executable} -m pip install -r requirements.txt")
        return False
    
    # Step 3: Initialize database
    if not initialize_database():
        print("\n✗ Setup failed: Could not initialize database")
        return False
    
    # Step 4: Create admin
    if not create_admin():
        print("\n✗ Setup failed: Could not create admin user")
        return False
    
    # Step 5: Import dataset (optional)
    import_dataset()
    
    # Step 6: Run diagnostics
    if not run_diagnostics():
        print("\n⚠ Some diagnostics failed, but setup may still work")
    
    # Step 7: Offer to start server
    if start_server():
        print("\n🚀 Starting server...\n")
        try:
            import uvicorn
            uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped by user")
            return True
        except Exception as e:
            print(f"\n✗ Server error: {e}")
            return False
    else:
        print("\n👋 Setup complete! Run 'python run.py' when ready.\n")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
