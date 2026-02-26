# AI Farming Chatbot - Integration Guide

## Overview

This guide explains how the frontend and backend are now connected in the AI Farming Chatbot application.

## Architecture

### Frontend Components
- **Landing Page** (`/`) - Home page with feature overview
- **Signup** (`/signup`) - User registration page
- **Login** (`/login`) - User login page  
- **Chat** (`/chat`) - Main chatbot interface for users
- **Admin Dashboard** (`/admin`) - Administration panel for managing knowledge base

### Backend API Endpoints

#### Public Endpoints
- `POST /chat` - Chat with the bot (supports public access)
- `GET /chat` - Chat with the bot (query parameter support)
- `POST /signup` - Register new user

#### User Endpoints (Require Token)
- `POST /user/login` - User login
- `POST /user/logout` - User logout

#### Admin Endpoints (Require Admin Token)
- `POST /admin/login` - Admin login
- `POST /admin/logout` - Admin logout
- `GET /admin/knowledge` - List knowledge base entries
- `POST /admin/knowledge` - Create knowledge base entry
- `PUT /admin/knowledge/{id}` - Update knowledge base entry
- `DELETE /admin/knowledge/{id}` - Delete knowledge base entry
- `GET /admin/chats` - View recent chat logs
- `GET /admin/chats/export` - Export chats as CSV

## How To Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Demo Data (Optional)
```bash
python seed_demo.py
```

This creates:
- Demo user (username: `demo`, password: `demo123`)
- Admin user (username: `admin`, password: `admin123`)
- Sample knowledge base entries

### 3. Start the Server
```bash
python run.py
```

The server will start at `http://localhost:8000`

### 4. Open in Browser
- **Home**: http://localhost:8000
- **User Signup**: http://localhost:8000/signup
- **User Login**: http://localhost:8000/login
- **Chat**: http://localhost:8000/chat
- **Admin**: http://localhost:8000/admin

## User Flow

1. **New User**: Visit http://localhost:8000 → Click "Get Started" → Sign up with email
2. **Returning User**: Visit http://localhost:8000 → Click "Sign In" → Enter credentials
3. **Chat**: After login, user is redirected to `/chat` to start chatting with the bot
4. **Logout**: Click "Logout" button to end session

## Admin Flow

1. **Login**: Visit http://localhost:8000/admin
2. **Dashboard**: View KB stats and recent chats
3. **Knowledge Management**: Add, edit, or delete knowledge entries
4. **Chat Logs**: View user chat history and export as CSV
5. **User Management**: View and manage users
6. **Settings**: Configure API base URL

## Frontend-Backend Communication

### Authentication
- Frontend stores auth tokens in `localStorage`
- Tokens are sent in `x-token` header for authenticated requests
- Tokens expire after 3 hours

### API Communication Pattern
```javascript
// Example: Chat request with token
const response = await fetch('/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'x-token': userToken  // For authenticated requests
    },
    body: JSON.stringify({
        message: userMessage,
        language: 'auto'  // or 'en', 'es'
    })
});
```

### Response Format
```json
{
    "reply": "Bot response...",
    "intent": "disease|fertilizer|irrigation|weather|harvest|general",
    "language": "en|es"
}
```

## Testing Integration

Run the integration test to verify all connections:

```bash
python test_integration.py
```

This will test:
- Server connectivity
- User signup
- User login
- Chat endpoint
- Admin login
- Knowledge base operations

## File Structure

```
project/
├── app.py                          # Main FastAPI application
├── models.py                       # Database models
├── run.py                          # Server startup script
├── seed_demo.py                    # Demo data seeding
├── test_integration.py             # Integration tests
├── requirements.txt                # Python dependencies
├── static/
│   ├── index.html                 # Admin dashboard
│   ├── home.html                  # Landing page
│   ├── chat.html                  # Chatbot interface
│   ├── templates/
│   │   ├── signup.html           # Signup form
│   │   ├── login.html            # Login form
│   │   └── admin_login.html      # Admin login form
│   └── images/
└── database/
    └── farming.db                  # SQLite database
```

## Features Connected

### 1. User Authentication
- ✅ Signup with email validation
- ✅ Login with token generation
- ✅ Session management
- ✅ Password hashing

### 2. Chat Interface
- ✅ Input field with message sending
- ✅ Message history display
- ✅ Loading states
- ✅ Error handling
- ✅ Language detection
- ✅ Intent recognition

### 3. Knowledge Base
- ✅ Create entries
- ✅ Search entries
- ✅ Edit entries
- ✅ Delete entries
- ✅ View all entries

### 4. Admin Dashboard
- ✅ Dashboard with stats
- ✅ Knowledge management
- ✅ Chat log viewing
- ✅ CSV export
- ✅ User management
- ✅ Settings

## Troubleshooting

### "Cannot connect to server"
- Make sure the server is running: `python run.py`
- Check if port 8000 is available
- Try accessing http://localhost:8000 in browser

### "Invalid credentials" on login
- Make sure you created demo data: `python seed_demo.py`
- Default credentials: admin/admin123 or demo/demo123
- Check database is in `./database/farming.db`

### "Token expired"
- Login again to get a fresh token
- Tokens expire after 3 hours

### Chat not working
- Make sure you're logged in (token is stored)
- Check browser console for errors
- Verify backend is returning chat responses

## Database

- **Type**: SQLite
- **Location**: `./database/farming.db`
- **Tables**: 
  - `users` - User accounts and credentials
  - `knowledge` - Knowledge base entries

### Reset Database
```bash
rm ./database/farming.db
python run.py  # Will recreate fresh database
```

## Environment Variables

Optional configuration in `.env` file:

```
DATABASE_URL=sqlite:///./database/farming.db
ADMIN_TOKEN_EXP_SECONDS=10800  # 3 hours
CORS_ORIGINS=*
```

## Next Steps

1. ✅ Frontend and backend are now connected
2. Add more knowledge base entries via admin dashboard
3. Customize intent detection in `detect_intent()`
4. Add email verification for signup
5. Implement user-specific chat history
6. Add analytics and usage statistics
7. Deploy to production (Heroku, AWS, etc.)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review `test_integration.py` for debugging
3. Check server logs in terminal
4. Verify database exists: `ls -la database/`

## Security Notes

- Passwords are hashed with SHA256
- Tokens are randomly generated UUIDs
- Implement rate limiting for production
- Use HTTPS in production
- Validate all user inputs
- Add CSRF protection
- Implement proper access controls

---

**Status**: ✅ Frontend-Backend Integration Complete

All frontend pages are now properly connected to backend API endpoints!
