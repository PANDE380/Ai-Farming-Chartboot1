# app.py
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from models import SessionLocal, Knowledge, User
import hashlib, re, json, os, time, uuid, csv, datetime

# --------------------
# App setup
# --------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("static/index.html")


# --------------------
# NLP & Chat utilities
# --------------------
def preprocess(text: str) -> str:
    """Clean and normalize text for matching."""
    text = text.lower().strip()
    return re.sub(r"[^a-zA-Z0-9\s]", "", text)

def auto_lang(msg: str) -> str:
    """Auto-detect language from message (simplified: returns 'en' for now)."""
    # In a real system, use langdetect or textblob
    try:
        # Simple detection: if contains common Spanish words
        spanish_words = ["el", "la", "de", "que", "y", "a", "en", "es", "se", "del", "para", "con"]
        words = msg.lower().split()
        spanish_count = sum(1 for w in words if w in spanish_words)
        if spanish_count > len(words) * 0.3:
            return "es"
    except:
        pass
    return "en"

def detect_intent(msg: str) -> str:
    """Simple intent detection based on keywords."""
    msg_lower = msg.lower()
    if any(word in msg_lower for word in ["disease", "pest", "illness", "sick", "damage"]):
        return "disease"
    elif any(word in msg_lower for word in ["fertilizer", "nutrient", "soil", "pH", "compost"]):
        return "fertilizer"
    elif any(word in msg_lower for word in ["water", "irrigation", "rain", "drought"]):
        return "irrigation"
    elif any(word in msg_lower for word in ["weather", "temperature", "climate", "season"]):
        return "weather"
    elif any(word in msg_lower for word in ["harvest", "mature", "ready", "pick", "crop"]):
        return "harvest"
    return "general"

def search_knowledge(question: str) -> str | None:
    """Search the knowledge base for an answer."""
    try:
        db = SessionLocal()
        clean_q = preprocess(question)
        result = db.query(Knowledge).filter(Knowledge.question.ilike(f"%{clean_q}%")).first()
        db.close()
        return result.answer if result else None
    except Exception as e:
        print(f"Search knowledge error: {e}")
        try:
            db.close()
        except:
            pass
        return None

# Default responses for common intents
responses = {
    "disease": {
        "en": "I can help with disease management. Please describe the symptoms you're seeing on your crops.",
        "es": "Puedo ayudar con el manejo de enfermedades. Por favor describe los síntomas que ves en tus cultivos.",
    },
    "fertilizer": {
        "en": "For fertilizer advice, I recommend checking your soil pH and nutrient levels first.",
        "es": "Para consejos sobre fertilizantes, recomiendo verificar primero el pH del suelo y los niveles de nutrientes.",
    },
    "irrigation": {
        "en": "Proper irrigation depends on your crop type and soil conditions. How much rainfall have you had recently?",
        "es": "El riego adecuado depende del tipo de cultivo y las condiciones del suelo. ¿Cuanta lluvia ha habido recientemente?",
    },
    "weather": {
        "en": "Weather can significantly impact crop yields. What region are you farming in?",
        "es": "El clima puede impactar significativamente los rendimientos. ¿En qué región estás cultivando?",
    },
    "harvest": {
        "en": "Great question about harvesting! The right time depends on your crop. What are you growing?",
        "es": "¡Gran pregunta sobre la cosecha! El momento adecuado depende de tu cultivo. ¿Qué estás cultivando?",
    },
    "general": {
        "en": "I'm here to help with agricultural questions. What would you like to know?",
        "es": "Estoy aquí para ayudar con preguntas agrícolas. ¿Qué te gustaría saber?",
    }
}

# Fallback response if no knowledge base match
fallback = {
    "en": "I'm not sure about that. Try asking about diseases, fertilizers, irrigation, weather, or harvest timing.",
    "es": "No estoy seguro de eso. Intenta preguntar sobre enfermedades, fertilizantes, riego, clima o momento de cosecha.",
}


# --------------------
# Models for requests
# --------------------
class ChatRequest(BaseModel):
    message: str
    language: str = "auto"
    theme: str = "dark"

class SignupRequest(BaseModel):
    username: str
    password: str
    email: str | None = None

class LoginRequest(BaseModel):
    username: str
    password: str

class KnowledgeIn(BaseModel):
    question: str
    answer: str
    intent: str | None = None
    crop: str | None = None
    language: str = "english"
    topic: str | None = None


# --------------------
# Utilities
# --------------------
CHAT_LOG_FILE = "chat_logs.txt"
ADMIN_TOKEN_EXP_SECONDS = 60 * 60 * 3  # 3 hours

# in-memory token store: token -> {username, expires}
admin_tokens: dict = {}

def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

def ensure_default_admin():
    """Create a default admin user if none exist (username=admin, password=admin123)."""
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.username == "admin").first()
        if not u:
            # try to create admin providing an email to satisfy potential NOT NULL constraints
            admin = User(
                username="admin",
                email="admin@example.com",
                password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin)
            try:
                db.commit()
            except Exception:
                db.rollback()
    finally:
        db.close()

ensure_default_admin()

def verify_admin_token(token: str | None):
    if not token:
        return False
    entry = admin_tokens.get(token)
    if not entry:
        return False
    if entry["expires"] < time.time():
        del admin_tokens[token]
        return False
    return True

def require_admin(token: str | None):
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired admin token")


# --------------------
# Chat endpoint (fixed)
# --------------------

@app.post("/chat")
@app.get("/chat")  # allow browser testing
def chat(req: ChatRequest | None = None, message: str | None = None):
    """Handle chat requests from users."""
    try:
        # support both POST JSON and GET query
        msg = ""
        if req and hasattr(req, 'message') and req.message:
            msg = req.message.strip()
        elif message:
            msg = str(message).strip()
        
        if not msg:
            return {"reply": "Please send a message.", "intent": "general", "language": "en"}

        # Determine language
        lang = "en"
        if req and hasattr(req, 'language') and req.language:
            if req.language.lower() == "auto":
                lang = auto_lang(msg)
            else:
                lang = req.language.lower()

        # Detect intent
        intent = detect_intent(msg)

        # Get response
        reply = ""
        if intent in responses and lang in responses[intent]:
            reply = responses[intent][lang]
        elif intent in responses and "en" in responses[intent]:
            reply = responses[intent]["en"]
        else:
            # Try knowledge base search
            ans = search_knowledge(msg)
            if ans:
                reply = ans
            elif lang in fallback:
                reply = fallback[lang]
            else:
                reply = fallback.get("en", "I'm not sure about that. Try asking about farming topics.")

        # Log chat
        try:
            with open(CHAT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "ts": int(time.time()),
                    "message": msg,
                    "lang": lang,
                    "reply": reply,
                    "intent": intent
                }, ensure_ascii=False) + "\n")
        except Exception as log_err:
            print(f"Chat log error: {log_err}")

        return {"reply": reply, "intent": intent, "language": lang}
    
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return {"reply": "Sorry, I encountered an error. Please try again.", "error": str(e), "intent": "error", "language": "en"}


# --------------------
# Admin: login / logout
# --------------------
@app.post("/admin/login")
def admin_login(creds: LoginRequest):
    """Authenticate admin user and issue token."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == creds.username).first()
        if not user or user.password != hash_password(creds.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        # only allow admin role to access admin panel
        if getattr(user, "role", "farmer") != "admin":
            raise HTTPException(status_code=403, detail="Not an admin user")
        # generate token
        token = str(uuid.uuid4())
        admin_tokens[token] = {"username": creds.username, "expires": time.time() + ADMIN_TOKEN_EXP_SECONDS}
        return {"token": token, "expires_in": ADMIN_TOKEN_EXP_SECONDS, "username": creds.username}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    finally:
        db.close()

@app.post("/admin/logout")
def admin_logout(x_token: str | None = Header(None)):
    if x_token and x_token in admin_tokens:
        del admin_tokens[x_token]
    return {"ok": True}


# --------------------
# Signup endpoint (stores optional email)
# --------------------
@app.post("/signup")
def signup(req: SignupRequest):
    """Register a new user account."""
    db = SessionLocal()
    try:
        # Validate input
        if not req.username or len(req.username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        if not req.password or len(req.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # check username/email collisions
        if db.query(User).filter(User.username == req.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        if req.email and db.query(User).filter(User.email == req.email).first():
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user = User(
            username=req.username,
            email=req.email,
            password=hash_password(req.password),
            role="farmer"
        )
        db.add(user)
        db.commit()
        return {"message": "Signup successful!", "username": req.username}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Signup failed")
    finally:
        db.close()


# --------------------
# Admin: Knowledge CRUD
# --------------------
@app.get("/admin/knowledge")
def list_knowledge(x_token: str | None = Header(None), q: str | None = None):
    """List all knowledge base entries (admin only)."""
    try:
        require_admin(x_token)
    except HTTPException:
        raise
    
    db = SessionLocal()
    try:
        query = db.query(Knowledge)
        if q:
            qclean = f"%{q.lower()}%"
            query = query.filter(Knowledge.question.ilike(qclean))
        rows = query.order_by(Knowledge.id.desc()).limit(1000).all()
        return [{"id": r.id, "question": r.question, "answer": r.answer, "intent": r.intent, "crop": r.crop, "language": r.language, "topic": r.topic} for r in rows]
    except Exception as e:
        print(f"List knowledge error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list knowledge")
    finally:
        db.close()

@app.post("/admin/knowledge")
def create_knowledge(item: KnowledgeIn, x_token: str | None = Header(None)):
    """Create a new knowledge base entry (admin only)."""
    try:
        require_admin(x_token)
    except HTTPException:
        raise
    
    db = SessionLocal()
    try:
        if not item.question or not item.answer:
            raise HTTPException(status_code=400, detail="Question and answer are required")
        
        k = Knowledge(
            question=item.question.strip(),
            answer=item.answer.strip(),
            intent=(item.intent or "general").strip(),
            crop=(item.crop or "").strip() or None,
            language=(item.language or "english").strip(),
            topic=(item.topic or "").strip() or None
        )
        db.add(k)
        db.commit()
        db.refresh(k)
        return {"ok": True, "id": k.id, "message": "Knowledge entry created"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create knowledge error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create knowledge")
    finally:
        db.close()

@app.put("/admin/knowledge/{kid}")
def update_knowledge(kid: int, item: KnowledgeIn, x_token: str | None = Header(None)):
    """Update a knowledge base entry (admin only)."""
    try:
        require_admin(x_token)
    except HTTPException:
        raise
    
    db = SessionLocal()
    try:
        r = db.query(Knowledge).filter(Knowledge.id == kid).first()
        if not r:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        
        if not item.question or not item.answer:
            raise HTTPException(status_code=400, detail="Question and answer are required")
        
        r.question = item.question.strip()
        r.answer = item.answer.strip()
        r.intent = (item.intent or "general").strip()
        r.crop = (item.crop or "").strip() or None
        r.language = (item.language or "english").strip()
        r.topic = (item.topic or "").strip() or None
        db.commit()
        return {"ok": True, "message": "Knowledge entry updated"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update knowledge error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update knowledge")
    finally:
        db.close()

@app.delete("/admin/knowledge/{kid}")
def delete_knowledge(kid: int, x_token: str | None = Header(None)):
    """Delete a knowledge base entry (admin only)."""
    try:
        require_admin(x_token)
    except HTTPException:
        raise
    
    db = SessionLocal()
    try:
        r = db.query(Knowledge).filter(Knowledge.id == kid).first()
        if not r:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        db.delete(r)
        db.commit()
        return {"ok": True, "message": "Knowledge entry deleted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete knowledge error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete knowledge")
    finally:
        db.close()


# --------------------
# Admin: Chats (view & export)
# --------------------
@app.get("/admin/chats")
def get_chats(x_token: str | None = Header(None), limit: int = 100):
    """Get recent chat logs (admin only)."""
    try:
        require_admin(x_token)
    except HTTPException:
        raise
    
    try:
        if not os.path.exists(CHAT_LOG_FILE):
            return []
        
        limit = max(1, min(limit, 1000))  # Between 1 and 1000
        out = []
        with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        
        for ln in lines:
            try:
                out.append(json.loads(ln))
            except:
                continue
        
        return out
    except Exception as e:
        print(f"Get chats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chats")

@app.get("/admin/chats/export")
def export_chats_csv(x_token: str | None = Header(None)):
    """Export chat logs as CSV (admin only)."""
    try:
        require_admin(x_token)
    except HTTPException:
        raise
    
    try:
        if not os.path.exists(CHAT_LOG_FILE):
            raise HTTPException(status_code=404, detail="No chat logs found")
        
        csv_file = "chat_export.csv"
        rows = []
        
        with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
            for ln in f:
                try:
                    j = json.loads(ln)
                    rows.append(j)
                except:
                    continue
        
        if not rows:
            raise HTTPException(status_code=404, detail="No chat data to export")
        
        # write CSV
        with open(csv_file, "w", newline="", encoding="utf-8") as csvf:
            writer = csv.writer(csvf)
            writer.writerow(["timestamp", "message", "language", "reply"])
            for r in rows:
                ts = r.get("ts", "")
                msg = r.get("message", "")
                lang = r.get("lang", "")
                reply = r.get("reply", "")
                writer.writerow([ts, msg, lang, reply])
        
        return FileResponse(csv_file, media_type="text/csv", filename=csv_file)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Export chats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to export chats")
