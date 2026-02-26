# 🚀 AI Farming Chatbot - Quick Reference Card

## Getting Started in 3 Commands

```bash
pip install -r requirements.txt
python seed_demo.py
python run.py
```

Then open: **http://localhost:8000**

---

## 🔓 Test Credentials

| Type | Username | Password |
|------|----------|----------|
| User | demo | demo123 |
| Admin | admin | admin123 |

---

## 🌐 Important URLs

| Page | URL |
|------|-----|
| Home | http://localhost:8000 |
| Signup | http://localhost:8000/signup |
| Login | http://localhost:8000/login |
| Chat | http://localhost:8000/chat |
| Admin | http://localhost:8000/admin |

---

## 🔑 API Endpoints Quick Ref

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /chat | Send message to bot |
| POST | /signup | Register new user |
| POST | /user/login | User login |
| GET | /admin/knowledge | List KB entries |
| POST | /admin/knowledge | Create KB entry |

---

## 📝 Files You Need to Know

| File | Purpose |
|------|---------|
| app.py | Main backend |
| static/chat.html | Chat interface |
| static/home.html | Landing page |
| seed_demo.py | Create test data |
| test_integration.py | Run tests |

---

## 🛠️ Common Commands

```bash
# Start server
python run.py

# Create demo data
python seed_demo.py

# Run tests  
python test_integration.py

# Check database
sqlite3 database/farming.db "SELECT * FROM users;"
```

---

## 📚 Documentation

- **INTEGRATION_GUIDE.md** - Full technical docs
- **SETUP_COMPLETE.md** - Setup & usage guide
- **DEVELOPER_REFERENCE.md** - API reference
- **CHANGES_SUMMARY.md** - All changes made

---

## ❓ Troubleshooting

**Can't connect to server**
- Check if python run.py is running
- Port 8000 must be free

**Login fails**
- Run: python seed_demo.py
- Check credentials above

**Module not found**
- Run: pip install -r requirements.txt

---

## 🎯 User Flow

1. Visit http://localhost:8000
2. Click "Get Started" or "Sign In"
3. Sign up (or use demo/demo123)
4. Login
5. Start chatting!
6. Logout when done

---

## ✅ Integration Status

- [x] Frontend connected to backend
- [x] User authentication working
- [x] Chat interface functional
- [x] Admin panel accessible
- [x] Documentation complete
- [x] Tests passing

**Status: ✅ PRODUCTION READY**

---

**Questions?** See INTEGRATION_GUIDE.md or SETUP_COMPLETE.md
