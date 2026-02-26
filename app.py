# app.py
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from models import SessionLocal, Knowledge, User
import hashlib, re, json, os, time, uuid, csv, datetime, pickle

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
    return FileResponse("static/home.html")

@app.get("/admin")
def admin():
    return FileResponse("static/index.html")

@app.get("/signup")
def signup_page():
    return FileResponse("static/templates/signup.html")

@app.get("/login")
def login_page():
    return FileResponse("static/templates/login.html")

@app.get("/chat")
def chat_page():
    return FileResponse("static/chat.html")


# --------------------
# NLP & Chat utilities
# --------------------
def preprocess(text: str) -> str:
    """Clean and normalize text for matching."""
    text = text.lower().strip()
    return re.sub(r"[^a-zA-Z0-9\s]", "", text)

def auto_lang(msg: str) -> str:
    """Auto-detect language from message using keyword heuristics.

    Returns language codes used in this app:
      en - English
      es - Spanish
      lg - Luganda
      sw - Swahili
      rn - Runyankole
      ach - Acholi/Luo
      lg2 - Lango
      fr - French
      ar - Arabic
      hi - Hindi
      (others default to en)
    """
    try:
        words = msg.lower().split()
        # Spanish detection
        spanish_words = ["el", "la", "de", "que", "y", "a", "en", "es", "se", "del", "para", "con"]
        if sum(1 for w in words if w in spanish_words) > len(words) * 0.3:
            return "es"
        # Luganda keywords
        luganda_words = ["kyokka", "nze", "obulimi", "ssebo", "mukyala", "bye" , "ggwe"]
        if any(w in luganda_words for w in words):
            return "lg"
        # Swahili keywords
        swahili_words = ["sala", "mimi", "kwa", "ni", "jina", "chakula", "sawa"]
        if any(w in swahili_words for w in words):
            return "sw"
        # Runyankole keywords
        runyankole_words = ["ye", "omuntu", "enkorogoto", "obulimi", "togye"]
        if any(w in runyankole_words for w in words):
            return "rn"
        # Acholi/Luo keywords
        acholi_words = ["awuok", "anyo", "lul", "kede", "romo", "iny" ]
        if any(w in acholi_words for w in words):
            return "ach"
        # Lango keywords
        lango_words = ["par", "laber", "pi", "wak", "iyo", "yɛ" ]
        if any(w in lango_words for w in words):
            return "lg2"
        # French keywords
        french_words = ["bonjour","merci","oui","non","s'il","vous","être"]
        if any(w in french_words for w in words):
            return "fr"
        # Arabic keywords
        arabic_words = ["مرحبا","شكرا","نعم","لا","زراعة","مزارع"]
        if any(w in arabic_words for w in words):
            return "ar"
        # Hindi keywords
        hindi_words = ["नमस्ते","धन्यवाद","हाँ","नहीं","कृषि","फसल"]
        if any(w in hindi_words for w in words):
            return "hi"
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
        
        # Try exact match first
        result = db.query(Knowledge).filter(Knowledge.question.ilike(f"%{clean_q}%")).first()
        if result:
            db.close()
            return result.answer
        
        # Try keyword matching if exact match fails
        keywords = clean_q.split()
        best_match = None
        best_score = 0
        
        for kb in db.query(Knowledge).all():
            kb_text = preprocess(kb.question)
            kb_words = kb_text.split()
            
            # Calculate matching score
            matches = sum(1 for kw in keywords if kw in kb_words)
            if matches > best_score:
                best_score = matches
                best_match = kb.answer
        
        db.close()
        return best_match if best_score > 0 else None
    except Exception as e:
        print(f"Search knowledge error: {e}")
        try:
            db.close()
        except:
            pass
        return None

def generate_smart_response(msg: str, intent: str, lang: str) -> str:
    """Generate intelligent response based on intent and message."""
    msg_lower = msg.lower().strip()
    
    # Handle greetings first
    # expanded to recognize salutations in all supported languages
    greetings = [
        "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
        "good evening", "what's up", "whats up", "how are you", "howdy", "yo",
        "hola", "buenos", "buenas",               # Spanish
        "bonjour", "salut", "allo",              # French
        "مرحبا", "أهلا", "سلام",                  # Arabic
        "नमस्ते", "नमस्कार", "हैलो",             # Hindi
        "gyebale", "hujambo", "bwakabona",       # Ugandan greetings
        "anywak", "kieni"
    ]

    if any(greeting in msg_lower for greeting in greetings):
        responses_greetings = {
            "en": "Hello! I'm here to help with whatever's going on with your crops. Ask me anything.",
            "es": "¡Hola! Estoy aquí para ayudarte con tus cultivos. Pregúntame lo que necesites.",
            "lg": "Gyebale! Nja kukuyamba mu bikwata ku bulimi bwo. Nkwogeraiki.",
            "sw": "Hujambo! Niko hapa kusaidia kuhusu kilimo chako. Uliza chochote.",
            "rn": "Bwakabona! Ninkusiima kukuyamba ku bulimi bwo. Nyikiriza ekibuuzo.",
            "ach": "Anywak! Kinyi ne kelo pa i ndeke? Twero kekenal.",
            "lg2": "Keni! Awe poto ni pi. Nyero kacek.",
            "fr": "Bonjour! Je suis là pour vous aider avec vos cultures. Demandez-moi ce que vous voulez.",
            "ar": "مرحبا! أنا هنا لمساعدتك في زراعتك. اسألني أي شيء.",
            "hi": "नमस्ते! मैं आपकी खेती में मदद के लिए यहाँ हूँ। मुझसे कुछ भी पूछें।"
        }
        return responses_greetings.get(lang, responses_greetings["en"])
    
    # Handle thank you / appreciation
    thanks = ["thanks", "thank you", "gracias", "thx", "appreciated", "appreciate it", "thanks so much"]
    if any(t in msg_lower for t in thanks):
        responses_thanks = {
            "en": "No problem at all! That's what I'm here for. Reach out anytime - farming life gets complicated and two heads are better than one.",
            "es": "¡Sin problema! Para eso estoy aquí. Comunícate en cualquier momento - la vida agrícola es complicada y dos mentes son mejor que una.",
            "lg": "Tolina kintu! Kino kye nnina okubaweereza. Omanyi okunyumya emirundi gyonna.",
            "sw": "Hakuna shida! Niko hapa kukusaidia. Uliza wakati wowote.",
            "rn": "Togenda! Ninkuhereza. Kabiririze emikolo gyonna.",
            "ach": "Ket ma? Aneno iye. Win kit me tye.",
            "lg2": "Okato! An iweyo. Nyumara chik.",
        }
        return responses_thanks.get(lang, responses_thanks["en"])
    
    # Handle yes/no responses
    yes_words = ["yes", "yeah", "yep", "sure", "okay", "ok", "fine", "si", "sí", "claro"]
    no_words = ["no", "nope", "nah", "not really", "no gracias"]
    
    if any(word in msg_lower for word in yes_words):
        responses_yes = {
            "en": "Awesome! Let's dig into it. What's giving you trouble?",
            "es": "¡Genial! Vamos a profundizar. ¿Qué te está dando problemas?",
            "lg": "Kikulu! Tujja kulaba. Kiki ekikuwangawo?",
            "sw": "Vizuri! Tuanzie. Kuna tatizo gani?",
            "rn": "Enkera! Tugendeeko. Kiki ekikukyungulira?",
            "ach": "Tye otin! Dwala?",
            "lg2": "Amwi! Min ma?",
        }
        return responses_yes.get(lang, responses_yes["en"])
    
    if any(word in msg_lower for word in no_words):
        responses_no = {
            "en": "All good. Just holler if you hit a snag later. I'll be around!",
            "es": "Está bien. ¡Solo grita si tienes problemas luego! Estaré por aquí.",
            "lg": "Byonna biri bulungi. Osobola kuneenya okumangiramu obuzibu. Nzijja kuba wano!",
            "sw": "Sawa sawa. Niambie kama kupata shida baadaye. Niko hapa!",
            "rn": "Byonna bisiima. Wanibainda obunaku obulungi. Ninkuba wano!",
            "ach": "Bile! Kwena kony? Iko woko!",
            "lg2": "Onyo! Watt? An iweyo.",
        
        }
        return responses_no.get(lang, responses_no["en"])
    
    # Check for specific question keywords
    if any(word in msg_lower for word in ["how", "what", "why", "when", "where", "can", "should", "do", "help"]):
        # It's a question - try to find relevant answer
        kb_answer = search_knowledge(msg)
        if kb_answer:
            return kb_answer
    
    # Generate contextual response based on intent
    if intent == "disease":
        if any(word in msg_lower for word in ["solution", "fix", "treatment", "cure", "prevent"]):
            return "Okay, so here's what I'd do: First, remove any obviously infected plants - don't want it spreading. Then spray with a fungicide if it's fungal, or an organic option like neem oil. Keep your plants with room to breathe and avoid getting water on the leaves. Next year, try rotating your crops to break the disease cycle."
        elif any(word in msg_lower for word in ["identify", "recognize", "see", "symptoms", "signs"]):
            return "Tell me what you're seeing - are the leaves yellowing? Brown spots? Powdery white stuff? Is the stem soft and mushy? The more details you give me, the better I can help you pin down what it is."
        else:
            return "Disease problems? That's rough. We can figure this out. The usual suspects are blight, mildew, and various leaf spots. What crops are affected and what do the symptoms look like?"
    
    elif intent == "fertilizer":
        if any(word in msg_lower for word in ["nitrogen", "phosphorus", "potassium", "npk"]):
            return "So NPK - that's your nitrogen, phosphorus, and potassium. Nitrogen makes plants green and leafy, phosphorus builds strong roots, and potassium keeps plants healthy overall. A 10-10-10 mix works for most situations, but your soil test will tell you if you need to adjust."
        elif any(word in msg_lower for word in ["soil", "test", "check", "measure"]):
            return "Honestly, get your soil tested - saves you money in the long run. Your local ag extension office can check it. You want to know your pH (most crops like it between 6 and 7) and what nutrients you're lacking. Game changer."
        elif any(word in msg_lower for word in ["type", "which", "best", "amount"]):
            return "You got organic (compost, manure, that kind of thing) or chemical fertilizers. Use what makes sense for your farm. Start with a soil test to know what you need, then apply before planting and maybe once a month during the season."
        else:
            return "Fertilizer can be tricky. First move is get your soil tested. What crop are you working with?"
    
    elif intent == "irrigation":
        if any(word in msg_lower for word in ["how much", "how often", "frequency", "amount", "schedule"]):
            return "Most crops want about 1-2 inches of water a week, but the key is watering deep not daily. You want big roots, not shallow ones. Stick your finger in the soil 4 inches down - if it's dry, water it. Simple as that."
        elif any(word in msg_lower for word in ["drought", "dry", "water", "rain"]):
            return "Dry spell? Water early in the morning when it's cool - less waste that way. Throw down some mulch to keep moisture in the soil. Younger plants need it more than established ones. And if you can, drip irrigation is a lifesaver in drought."
        elif any(word in msg_lower for word in ["method", "type", "system", "spray", "drip"]):
            return "Drip systems are the most water-efficient. Sprinklers work well if you got the pressure. Flooding's simple but wastes water. Overhead's fine if you gotta keep bugs off. Depends what works for your setup."
        else:
            return "Watering's one of those things that takes practice. Tell me - are you letting it dry out between waterings or keeping it soaked?"
    
    elif intent == "weather":
        if any(word in msg_lower for word in ["frost", "freeze", "cold", "temperature"]):
            return "Frost coming? Get ready early - grab a frost cloth or blanket and get it on those plants before the sun goes down. Water a bit before the freeze, too - sounds weird but it helps. Next year, plant cold-hardy varieties."
        elif any(word in msg_lower for word in ["rain", "rainfall", "wet", "waterlog"]):
            return "Too much rain? First, make sure your ground drains okay - raised beds help if you got drainage issues. Don't work the soil when it's soaked - you'll mess up the structure. Raised beds are your friend here."
        elif any(word in msg_lower for word in ["hot", "heat", "temperature", "sun", "shade"]):
            return "Heat getting brutal? Shade cloth helps during peak heat, and mulch keeps the soil cooler. Water a bit more during heat waves. And yeah, some crops just handle heat better than others."
        else:
            return "Weather can make or break a season. What's the forecast looking like where you are?"
    
    elif intent == "harvest":
        if any(word in msg_lower for word in ["when", "time", "mature", "ready", "ripe"]):
            return "Timing is everything. Fruits should be fully colored, veggies should be at full size, greens before they bolt. Pick in the morning when it's cool - the produce stays fresher longer. What are you harvesting?"
        elif any(word in msg_lower for word in ["how", "method", "technique", "proper"]):
            return "Use clean tools, be gentle so you don't bruise anything, and harvest when it's cool. Handle with care - one bruise and it goes downhill fast."
        elif any(word in msg_lower for word in ["storage", "keep", "preserve", "fresh"]):
            return "Cool it down quick after you pick. Store it right - temperature matters, humidity matters. Keep stuff separate if you can, especially fruit that's ripening. Check on it regularly."
        else:
            return "Harvest time is exciting. What're you bringing in?"
    
    else:  # general intent
        if "crop" in msg_lower or "plant" in msg_lower or "grow" in msg_lower:
            return "Growing stuff is always an adventure. What's your question - disease issues, need to fertilize, watering problems, or something else?"
        elif "soil" in msg_lower:
            return "Soil's everything in farming. You gotta test it to know what you're working with, add organic stuff to keep it alive, watch your pH. What's going on with yours?"
        elif "pest" in msg_lower:
            return "Pests are the worst. First thing is figure out what bug you've actually got. Then you can decide whether to go the natural route or spray. What's bugging your crops?"
        else:
            # If we have knowledge base entry, return it
            kb_answer = search_knowledge(msg)
            if kb_answer:
                return kb_answer
            return "I'm here if you need help. Ask me anything about your farm - pests, diseases, watering, fertilizer, weather... what's on your mind?"

# Default responses for common intents
responses = {
    "disease": {
        "en": "Diseases are no fun. Tell me what you're seeing - I can help.",
        "es": "Las enfermedades son desagradables. Dime qué estás viendo - puedo ayudar.",
    },
    "fertilizer": {
        "en": "Get your soil tested first - that way you know what you're actually lacking.",
        "es": "Primero haz un análisis del suelo - así sabrás qué te falta.",
    },
    "irrigation": {
        "en": "Check your soil - stick your finger 4 inches down and see if it's dry. That's your sign.",
        "es": "Revisa tu suelo - mete el dedo 4 pulgadas y ve si está seco. Esa es tu señal.",
    },
    "weather": {
        "en": "Weather's one of those things you can't control, but you can prepare for it.",
        "es": "El clima es algo que no puedes controlar, pero puedes prepararte para ello.",
    },
    "harvest": {
        "en": "Harvest time is when it all pays off. What are you bringing in?",
        "es": "La cosecha es cuando todo vale la pena. ¿Qué estás recolectando?",
    },
    "general": {
        "en": "I'm here for your farming questions. Shoot.",
        "es": "Estoy aquí para tus preguntas agrícolas. Adelante.",
    }
}

# Fallback response if no knowledge base match
fallback = {
    "en": "Hmm, that one's not in my playbook, but I'm still here to help. Any farming challenges I can tackle?",
    "es": "Esa no está en mi libro juego, pero sigo aquí para ayudar. ¿Algún desafío agrícola que pueda resolver?",
    "lg": "Nnyinza okukyusa? Kino tekiri mu gida lyange naye ndyewunyisa okukuyamba. Eyini ekitufu mu bulimi?",
    "sw": "Huo! Hii haipo katika kitabu changu, lakini niko hapa kusaidia. Kuna shida ya kilimo mail twressa?",
    "rn": "Kino tekiri mu kyagenda kyange naye nkyopeerera okukuyamba. Ogira ekizibu ky'obulimi?",
    "ach": "Ka! Iyi ritimo pa anena, toparo kany. En obedo ni?",
    "lg2": "Keni! Okwero ni pi, laber okwera. Anyineri munyago?",
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

        # Generate intelligent response
        reply = generate_smart_response(msg, intent, lang)

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
# User: login / logout
# --------------------
@app.post("/user/login")
def user_login(creds: LoginRequest):
    """Authenticate user (not admin) and issue token."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == creds.username).first()
        if not user or user.password != hash_password(creds.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        # generate token
        token = str(uuid.uuid4())
        admin_tokens[token] = {"username": creds.username, "expires": time.time() + ADMIN_TOKEN_EXP_SECONDS}
        return {"token": token, "expires_in": ADMIN_TOKEN_EXP_SECONDS, "username": creds.username, "role": user.role}
    except HTTPException:
        raise
    except Exception as e:
        print(f"User login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    finally:
        db.close()

@app.post("/user/logout")
def user_logout(x_token: str | None = Header(None)):
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
