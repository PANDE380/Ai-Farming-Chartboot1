#!/usr/bin/env python3
"""
Main entry point for the AI Farming Chatbot application.
Initializes the database and starts the FastAPI server.
"""

import sys
import os

# Ensure database directory exists
os.makedirs("./database", exist_ok=True)

# Initialize database
try:
    from models import Base, engine, SessionLocal
    print("✓ Database initialized")
except Exception as e:
    print(f"✗ Database initialization failed: {e}")
    sys.exit(1)

# Ensure default admin exists
try:
    from app import ensure_default_admin
    ensure_default_admin()
    print("✓ Admin user verified")
except Exception as e:
    print(f"✗ Admin creation failed: {e}")
    sys.exit(1)

# Start the server
if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting AI Farming Chatbot...")
    print("📖 Admin panel: http://localhost:8000")
    print("💬 Chat endpoint: http://localhost:8000/chat")
    print("\n✓ Server running. Press Ctrl+C to stop.\n")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
