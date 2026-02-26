#!/usr/bin/env python3
"""
 AI FARMING CHATBOT - QUICK REFERENCE GUIDE

Use this as your go-to guide for running the chatbot.
"""

QUICK_START = """
╔═══════════════════════════════════════════════════════════╗
║            AI FARMING CHATBOT - QUICK START             ║
╚═══════════════════════════════════════════════════════════╝

📌 FASTEST WAY TO GET STARTED:

  1. python start.py
     (Interactive setup - installs everything, creates DB, and runs server)

  2. Open browser: http://localhost:8000
     
  3. Login: admin / admin123

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 MANUAL SETUP (if you prefer):

  pip install -r requirements.txt
  python setup.py
  python run.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 VERIFY SYSTEM WORKS:

  python test_diagnose.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  IMPORT YOUR FARMING DATA:

  python import_dataset.py

  (Make sure you have: a sample_Farming_FAQ_Assistant_Dataset.csv)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

COMMANDS = """
╔═══════════════════════════════════════════════════════════╗
║              COMMON COMMANDS & URLs                       ║
╚═══════════════════════════════════════════════════════════╝

START SERVER:
  python run.py                 Main server (port 8000)
  python start.py               Interactive setup + server

TESTING & DIAGNOSTICS:
  python test_diagnose.py       Run all diagnostics
  python test_app.py            Original test script

DATA MANAGEMENT:
  python import_dataset.py      Import FAQ dataset from CSV
  python train_intent.py        Train ML intent classifier

URLS & ENDPOINTS:
  http://localhost:8000/        Admin panel
  http://localhost:8000/chat    Chat API
  http://localhost:8000/docs    API documentation
  http://localhost:8000/redoc   Alternative API docs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

API_EXAMPLES = """
╔═══════════════════════════════════════════════════════════╗
║              API USAGE EXAMPLES                           ║
╚═══════════════════════════════════════════════════════════╝

1  CHAT WITH THE BOT:

   GET /chat?message=How+to+grow+rice
   
   POST /chat
   {
     "message": "How to prevent crop diseases?",
     "language": "en"
   }

   Response:
   {
     "reply": "I can help with disease management...",
     "intent": "disease",
     "language": "en"
   }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2  ADMIN LOGIN:

   POST /admin/login
   {
     "username": "admin",
     "password": "admin123"
   }

   Response:
   {
     "token": "550e8400-e29b-41d4-a716-446655440000",
     "expires_in": 10800,
     "username": "admin"
   }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3  ADD KNOWLEDGE ENTRY:

   POST /admin/knowledge
   X-Token: {token}
   
   {
     "question": "How to treat corn rust?",
     "answer": "Corn rust can be managed using...",
     "intent": "disease",
     "crop": "corn"
   }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4  LIST KNOWLEDGE ENTRIES:

   GET /admin/knowledge?q=maize
   X-Token: {token}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5  SIGN UP NEW USER:

   POST /signup
   {
     "username": "farmer123",
     "password": "secure_password",
     "email": "farmer@example.com"
   }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

TROUBLESHOOTING = """
╔═══════════════════════════════════════════════════════════╗
║              TROUBLESHOOTING                              ║
╚═══════════════════════════════════════════════════════════╝

❌ ModuleNotFoundError: No module named 'fastapi'
   ✅ Solution: pip install -r requirements.txt

❌ ERROR: unable to open database file
   ✅ Solution: mkdir database && python setup.py

❌ Admin login fails
   ✅ Solution: python -c "from app import ensure_default_admin; ensure_default_admin()"

❌ Port 8000 already in use
   ✅ Solution: Change port in run.py or use: lsof -ti :8000 | xargs kill -9

❌ ImportError: No module named 'sklearn'
   ✅ Solution: pip install scikit-learn (only needed for train_intent.py)

❌ CSV import fails
   ✅ Solution: Check file name is exactly: "a sample_Farming_FAQ_Assistant_Dataset.csv"
              Check columns are: "Question" and "Answer"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

FILES_INFO = """
╔═══════════════════════════════════════════════════════════╗
║              PROJECT FILES & DESCRIPTIONS                 ║
╚═══════════════════════════════════════════════════════════╝

CORE APPLICATION:
  app.py                    Main FastAPI application
  models.py                 Database models (User, Knowledge)
  run.py                    Start the server
  
SETUP & TESTING:
  start.py                  Interactive setup wizard 🎯 USE THIS
  setup.py                  Automated setup script
  test_diagnose.py          System diagnostics
  test_app.py               Original tests

DATA & ML:
  import_dataset.py         Import FAQ dataset from CSV
  train_intent.py           Train intent classifier
  requirements.txt          Python dependencies

DOCUMENTATION:
  README.md                 Full documentation
  FIXES_SUMMARY.md          What was fixed
  .env.example              Configuration template
  .gitignore                Git ignore rules

FRONTEND:
  static/index.html         Admin panel
  static/manifest.json      PWA manifest
  static/service-worker.js  Service worker

DATABASE:
  database/farming.db       SQLite database (created on first run)
  chat_logs.txt             Chat history (JSON lines)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

DEFAULTS = """
╔═══════════════════════════════════════════════════════════╗
║              DEFAULT CREDENTIALS & SETTINGS                ║
╚═══════════════════════════════════════════════════════════╝

ADMIN LOGIN:
  Username: admin
  Password: admin123

SERVER:
  Host: 0.0.0.0
  Port: 8000
  Database: SQLite (database/farming.db)

TOKEN:
  Expires in: 3 hours (10800 seconds)
  Passed via: X-Token header

DEFAULT INTENTS:
  disease       - Disease/pest management
  fertilizer    - Soil nutrients and fertilizers
  irrigation    - Water management
  weather       - Climate and weather
  harvest       - Harvesting and timing
  general       - General agriculture

SUPPORTED LANGUAGES:
  en (English)
  es (Spanish)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

CHECKLIST = """
╔═══════════════════════════════════════════════════════════╗
║              SETUP CHECKLIST                              ║
╚═══════════════════════════════════════════════════════════╝

Before you start using the chatbot:

  ☐ Python 3.8+ installed
  ☐ Dependencies installed (pip install -r requirements.txt)
  ☐ Database folder created (database/)
  ☐ Admin user created (default: admin/admin123)
  ☐ System diagnostics passed (python test_diagnose.py)
  ☐ Server starts without errors (python run.py)
  ☐ Can access admin panel (http://localhost:8000)
  ☐ Chat API responds (POST /chat)
  ☐ Dataset imported (optional - python import_dataset.py)

If any fails, check TROUBLESHOOTING section above.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def show_menu():
    """Interactive menu."""
    while True:
        print("""
╔═══════════════════════════════════════════════════════════╗
║          AI FARMING CHATBOT - HELP MENU                ║
╚═══════════════════════════════════════════════════════════╝

  1. Quick Start Guide
  2. Common Commands
  3. API Examples
  4. Troubleshooting
  5. File Information
  6. Default Settings
  7. Setup Checklist
  8. Exit

Select an option (1-8): """)
        
        choice = input().strip()
        
        if choice == "1":
            print(QUICK_START)
        elif choice == "2":
            print(COMMANDS)
        elif choice == "3":
            print(API_EXAMPLES)
        elif choice == "4":
            print(TROUBLESHOOTING)
        elif choice == "5":
            print(FILES_INFO)
        elif choice == "6":
            print(DEFAULTS)
        elif choice == "7":
            print(CHECKLIST)
        elif choice == "8":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n Invalid option. Please enter 1-8.\n")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Show specific section if argument provided
        section = sys.argv[1].lower()
        if section == "quick":
            print(QUICK_START)
        elif section == "commands":
            print(COMMANDS)
        elif section == "api":
            print(API_EXAMPLES)
        elif section == "help":
            print(TROUBLESHOOTING)
        elif section == "files":
            print(FILES_INFO)
        elif section == "defaults":
            print(DEFAULTS)
        elif section == "checklist":
            print(CHECKLIST)
        else:
            print("Usage: python help.py [quick|commands|api|help|files|defaults|checklist]")
    else:
        # Show interactive menu
        show_menu()
