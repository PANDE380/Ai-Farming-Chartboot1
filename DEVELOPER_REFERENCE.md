# AI Farming Chatbot - Developer Quick Reference

## System Components Overview

### Backend (FastAPI)
- **Port**: 8000
- **Type**: RESTful API
- **Database**: SQLite

### Frontend (HTML/JS)
- **Pages**: 5 main pages
- **Storage**: LocalStorage for tokens
- **Communication**: JSON over HTTP

## Key Files

### Backend Files
| File | Purpose |
|------|---------|
| `app.py` | Main FastAPI application with all endpoints |
| `models.py` | SQLAlchemy database models |
| `run.py` | Server startup script |
| `seed_demo.py` | Create demo users and data |
| `test_integration.py` | Integration test suite |

### Frontend Files
| File | Purpose | Route |
|------|---------|-------|
| `home.html` | Landing/home page | `/` |
| `signup.html` | User registration | `/signup` |
| `login.html` | User login | `/login` |
| `chat.html` | Chatbot interface | `/chat` |
| `index.html` | Admin dashboard | `/admin` |

## API Endpoints Reference

### Public Endpoints (No Auth Required)
```
POST   /chat                    - Chat with bot
GET    /chat?message=...        - Chat (query string)
POST   /signup                  - Register user
GET    /                        - Landing page
GET    /signup                  - Signup page
GET    /login                   - Login page
```

### User Endpoints (Token Required)
```
POST   /user/login              - Login user
POST   /user/logout             - Logout user
GET    /chat                    - Chat page (HTML)
```

### Admin Endpoints (Admin Token Required)
```
POST   /admin/login             - Admin login
POST   /admin/logout            - Admin logout
GET    /admin                   - Admin dashboard (HTML)
GET    /admin/knowledge         - List KB entries
POST   /admin/knowledge         - Create KB entry
PUT    /admin/knowledge/{id}    - Update KB entry
DELETE /admin/knowledge/{id}    - Delete KB entry
GET    /admin/chats             - List chat history
GET    /admin/chats/export      - Export as CSV
```

## Request/Response Examples

### Send Message
**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "x-token: YOUR_TOKEN" \
  -d '{"message": "How to grow tomatoes?", "language": "auto"}'
```

**Response:**
```json
{
  "reply": "Tomatoes need full sun...",
  "intent": "planting",
  "language": "en"
}
```

### Login
**Request:**
```bash
curl -X POST http://localhost:8000/user/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

**Response:**
```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "expires_in": 10800,
  "username": "demo",
  "role": "farmer"
}
```

### Get Knowledge Base
**Request:**
```bash
curl -X GET http://localhost:8000/admin/knowledge \
  -H "x-token: YOUR_ADMIN_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "question": "What are common crop diseases?",
    "answer": "Common diseases include...",
    "intent": "disease",
    "crop": "general",
    "language": "english"
  }
]
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR UNIQUE NOT NULL,
  email VARCHAR UNIQUE,
  password VARCHAR NOT NULL,
  role VARCHAR DEFAULT 'farmer',  -- 'admin' or 'farmer'
  created_at DATETIME
);
```

### Knowledge Table
```sql
CREATE TABLE knowledge (
  id INTEGER PRIMARY KEY,
  question VARCHAR,
  answer VARCHAR,
  intent VARCHAR,
  crop VARCHAR,
  language VARCHAR,
  topic VARCHAR
);
```

## Frontend LocalStorage Keys

| Key | Purpose |
|-----|---------|
| `af_user_token` | User authentication token |
| `af_admin_token` | Admin authentication token (unused, for future) |
| `af_username` | Current logged-in username |
| `af_api_base` | API base URL (for custom servers) |

## Common Code Patterns

### Frontend: API Call with Token
```javascript
const token = localStorage.getItem("af_user_token");
const response = await fetch('/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'x-token': token
    },
    body: JSON.stringify({
        message: userMessage,
        language: 'auto'
    })
});
```

### Frontend: Login Flow
```javascript
// 1. Authenticate
const response = await fetch('/user/login', {...});
const data = await response.json();

// 2. Store token
localStorage.setItem("af_user_token", data.token);
localStorage.setItem("af_username", data.username);

// 3. Redirect to chat
window.location.href = "/chat";
```

### Backend: Verify Admin Token
```python
@app.get("/admin/something")
def admin_endpoint(x_token: str | None = Header(None)):
    require_admin(x_token)  # Raises 401 if invalid
    # ... endpoint logic
```

## Intent Types

The chatbot recognizes these intents:
- `disease` - Crop disease questions
- `fertilizer` - Fertilizer and soil nutrient questions
- `irrigation` - Water and irrigation questions
- `weather` - Weather impact questions
- `harvest` - Harvest timing questions
- `general` - General farming questions

## Language Support

Currently supports:
- `en` - English
- `es` - Spanish
- `auto` - Auto-detect based on keywords

## Token Expiration

- **User tokens**: 3 hours (10800 seconds)
- **Admin tokens**: 3 hours (10800 seconds)
- **Token storage**: In-memory (lost on server restart)

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 500 | Server error |

## Development Tips

### 1. Add New Knowledge Entry
```python
# In admin dashboard or via API
curl -X POST http://localhost:8000/admin/knowledge \
  -H "x-token: ADMIN_TOKEN" \
  -d '{
    "question": "How to...",
    "answer": "You should...",
    "intent": "disease",
    "crop": "tomato",
    "language": "english"
  }'
```

### 2. Add New Intent Detection
```python
# Edit app.py detect_intent() function
def detect_intent(msg: str) -> str:
    msg_lower = msg.lower()
    if any(word in msg_lower for word in ["your_keywords"]):
        return "your_intent"
    # ...
```

### 3. Add New Response
```python
# Edit responses dictionary in app.py
responses = {
    "your_intent": {
        "en": "Your English response",
        "es": "Tu respuesta en español"
    }
}
```

### 4. Test Endpoint
```bash
# Simple GET test
curl http://localhost:8000/

# POST with JSON
curl -X POST http://localhost:8000/chat \
  -d '{"message": "test"}' \
  -H "Content-Type: application/json"
```

## Debugging

### Check Server Logs
Server logs appear in terminal where you ran `python run.py`

### Browser Console
Check browser dev tools (F12) → Console for JavaScript errors

### Check Database
```bash
# View all users
sqlite3 database/farming.db "SELECT * FROM users;"

# View all knowledge entries
sqlite3 database/farming.db "SELECT question FROM knowledge LIMIT 5;"
```

### Enable Detailed Logging
Add to app.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Notes

- **Chat endpoint**: ~100-200ms response time
- **Socket capacity**: FastAPI default is single-threaded
- **Database**: SQLite suitable for single server
- **Session storage**: In-memory (consider Redis for production)

## Security Considerations

- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Validate all inputs
- [ ] Use proper password hashing (bcrypt)
- [ ] Implement CSRF protection
- [ ] Use secure session storage
- [ ] Implement proper access controls
- [ ] Add input sanitization

## Production Checklist

- [ ] Change default passwords
- [ ] Use environment variables for config
- [ ] Set up proper logging
- [ ] Use production WSGI server (Gunicorn)
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring
- [ ] Configure database backup
- [ ] Implement rate limiting
- [ ] Add authentication audit logs

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)

---

**Last Updated**: February 26, 2026
**For Questions**: Check INTEGRATION_GUIDE.md or SETUP_COMPLETE.md
