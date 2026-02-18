#!/usr/bin/env python3
"""
Setup script to initialize the AI Farming Chatbot system.
Installs dependencies, creates database, and imports dataset.
"""

import os
import sys
import subprocess

def run_command(cmd, description):
    """Run a command and report status."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    print("\n" + "="*60)
    print("  🌾 AI FARMING CHATBOT - SETUP")
    print("="*60 + "\n")
    
    # Step 1: Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Step 1: Installing Python dependencies..."
    ):
        print("✗ Failed to install dependencies")
        return False
    print("✓ Dependencies installed successfully")
    
    # Step 2: Initialize database
    if not run_command(
        f"{sys.executable} -c \"from models import Base, engine; Base.metadata.create_all(bind=engine); print('✓ Database initialized')\"",
        "Step 2: Initializing database..."
    ):
        print("✗ Failed to initialize database")
        return False
    
    # Step 3: Import dataset
    if os.path.exists("a sample_Farming_FAQ_Assistant_Dataset.csv"):
        if not run_command(
            f"{sys.executable} import_dataset.py",
            "Step 3: Importing farming dataset..."
        ):
            print("⚠ Failed to import dataset (non-critical)")
    else:
        print("\n⚠ Dataset file not found, skipping import")
    
    # Step 4: Create admin user
    print("\n" + "="*60)
    print("  Step 4: Verifying admin user...")
    print("="*60 + "\n")
    
    if not run_command(
        f"{sys.executable} -c \"from app import ensure_default_admin; ensure_default_admin(); print('✓ Admin user verified')\"",
        ""
    ):
        print("✗ Failed to create admin user")
        return False
    
    print("\n" + "="*60)
    print("  ✓ SETUP COMPLETE!")
    print("="*60)
    print("\n🚀 To start the chatbot, run:")
    print(f"   {sys.executable} run.py")
    print("\n📖 Admin Panel: http://localhost:8000")
    print("💬 Chat API: http://localhost:8000/chat")
    print("\n🔑 Default credentials: admin / admin123")
    print("\n" + "="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
