"""
YUMEA - AI That Feels
by Selvotex | Founder: Utkarsh Verma
(c) 2026 Selvotex. All rights reserved.
"""

import streamlit as st
import os
import re
import json
import time
import uuid
import hashlib
import base64
import smtplib
import tempfile
import html as html_module
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import edge_tts
    import asyncio
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from streamlit_mic_recorder import mic_recorder
    MIC_RECORDER_AVAILABLE = True
except ImportError:
    MIC_RECORDER_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


st.set_page_config(
    page_title="Yumea - AI That Feels",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════

COMPANY_NAME = "Selvotex"
FOUNDER_NAME = "Utkarsh Verma"
BUSINESS_EMAIL = "selvotexofficial@gmail.com"
PRODUCT_NAME = "YUMEA"
YEAR = 2026
USER_DATA_FILE = "user_data.json"
USERS_FILE = "users.json"
CHROMA_PATH = "data/chroma_db"

ADMIN_USERNAME = "yumea_ai"
ADMIN_PASSWORD = "otyhey"

PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "daily_messages": 30,
        "max_words_per_message": 1000,
        "badge": "🆓",
    },
    "premium_69": {
        "name": "Premium Lite",
        "price": 69,
        "daily_messages": 150,
        "max_words_per_message": 2000,
        "badge": "⭐",
    },
    "premium_199": {
        "name": "Premium Pro",
        "price": 199,
        "daily_messages": 500,
        "max_words_per_message": 5000,
        "badge": "💎",
    },
    "admin": {
        "name": "Admin",
        "price": 0,
        "daily_messages": 999999,
        "max_words_per_message": 999999,
        "badge": "👑",
    },
}

WISDOM_SOURCES = {
    "osho": {"emoji": "🕉️", "name": "Osho"},
    "gita": {"emoji": "📜", "name": "Bhagavad Gita"},
    "buddha": {"emoji": "🙏", "name": "Buddha"},
    "bible": {"emoji": "📖", "name": "Bible"},
    "quran": {"emoji": "☪️", "name": "Quran"},
    "marcus_aurelius": {"emoji": "⚔️", "name": "Marcus Aurelius"},
    "socrates": {"emoji": "🏛️", "name": "Socrates"},
    "plato": {"emoji": "📚", "name": "Plato"},
    "nietzsche": {"emoji": "🔨", "name": "Nietzsche"},
    "confucius": {"emoji": "☯️", "name": "Confucius"},
    "sun_tzu": {"emoji": "⚔️", "name": "Sun Tzu"},
}

MOODS = {
    "happy": {"emoji": "😊", "label": "Happy"},
    "sad": {"emoji": "😔", "label": "Sad"},
    "anxious": {"emoji": "😰", "label": "Anxious"},
    "calm": {"emoji": "😌", "label": "Calm"},
}

VOICE_OPTIONS = {
    "hindi": {"Female": "hi-IN-SwaraNeural"},
    "hinglish": {"Female": "hi-IN-SwaraNeural"},
    "english": {"Female": "en-IN-NeerjaNeural"},
}

LANGUAGE_NAMES = {"hindi": "Hindi", "hinglish": "Hinglish", "english": "English"}

DAILY_QUOTES = [
    {"text": "Drop the idea that you can change the outcome. Be total in your action.", "source": "Osho"},
    {"text": "You have the right to work, but not to the fruits of work.", "source": "Bhagavad Gita"},
    {"text": "Peace comes from within. Do not seek it without.", "source": "Buddha"},
    {"text": "The mind is everything. What you think, you become.", "source": "Buddha"},
    {"text": "You have power over your mind, not outside events.", "source": "Marcus Aurelius"},
    {"text": "An unexamined life is not worth living.", "source": "Socrates"},
    {"text": "He who has a why to live can bear almost any how.", "source": "Nietzsche"},
    {"text": "Wherever you go, go with all your heart.", "source": "Confucius"},
]

HEAVY_EMOTIONAL_WORDS = [
    "suicide", "kill myself", "end my life", "want to die", "hopeless",
    "मरना चाहता", "जीना नहीं", "marna chahta", "jeena nahi",
]

FORCE_ANSWER_PHRASES = ["just answer", "just tell me", "seedha bata", "abhi batao"]

VAGUE_STARTERS = [
    "i feel", "im feeling", "im sad", "mujhe lag raha", "mann nahi",
    "help me", "confused hun", "pareshan hun",
]

HINGLISH_WORDS = [
    "kya", "hai", "hain", "mujhe", "kaise", "kyun", "nahi", "haan",
    "ho", "kar", "karo", "bhai", "yaar", "dil", "mann", "shanti",
    "dukh", "pyaar", "chahiye", "zindagi", "khush", "udaas", "pareshan",
    "acha", "achha", "bahut", "kuch", "koi", "batao", "bata", "raha",
    "rahi", "gaya", "gayi", "hum", "tum", "aap",
]

CASUAL_GREETINGS = [
    "hi", "hello", "hey", "namaste", "kaise ho", "how are you",
    "thanks", "bye", "ok", "okay", "haan", "nahi",
]

WISDOM_KEYWORDS = [
    "osho", "karma", "dharma", "buddha", "gita", "krishna", "wisdom",
    "meditation", "spiritual", "peace", "philosophy",
]


# ═══════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_image_b64(filename):
    path = Path(filename)
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def render_msg_text(text):
    if not text:
        return ""
    escaped = html_module.escape(text)
    escaped = escaped.replace("\n", "<br>")
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"`(.+?)`",
        r"<code style='background:rgba(255,255,255,0.08);padding:1px 5px;border-radius:4px;'>\1</code>",
        escaped
    )
    return escaped


# ═══════════════════════════════════════════════════════════
# AUTH SYSTEM
# ═══════════════════════════════════════════════════════════

def load_users_db():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_users_db(users_db):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users_db, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    return hash_password(password) == hashed


def create_user_account(name, email, password):
    if not name or not email or not password:
        return False, "All fields are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."
    
    users_db = load_users_db()
    email_lower = email.lower().strip()
    
    if email_lower in users_db:
        return False, "Email already registered. Please sign in."
    
    users_db[email_lower] = {
        "name": name.strip(),
        "email": email_lower,
        "password_hash": hash_password(password),
        "plan": "free",
        "messages_today": 0,
        "last_reset_date": str(date.today()),
        "total_messages": 0,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    if save_users_db(users_db):
        return True, "Account created successfully!"
    return False, "Failed to create account."


def login_user(email, password):
    if email.strip() == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True, "Welcome, Admin!", {
            "name": "Admin",
            "email": ADMIN_USERNAME,
            "plan": "admin",
            "messages_today": 0,
            "total_messages": 0,
            "is_admin": True,
        }
    
    if not email or not password:
        return False, "Please enter email and password.", None
    
    users_db = load_users_db()
    email_lower = email.lower().strip()
    
    if email_lower not in users_db:
        return False, "Email not registered. Please sign up.", None
    
    user = users_db[email_lower]
    
    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password.", None
    
    today_str = str(date.today())
    if user.get("last_reset_date") != today_str:
        user["messages_today"] = 0
        user["last_reset_date"] = today_str
    
    user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users_db[email_lower] = user
    save_users_db(users_db)
    
    user["is_admin"] = False
    return True, "Welcome back, " + user["name"] + "!", user


def logout_user():
    st.session_state.is_authenticated = False
    st.session_state.current_user = None
    st.session_state.is_admin = False
    st.session_state.messages = []
    st.session_state.conversation_history = []


def get_current_user():
    return st.session_state.get("current_user", None)


def get_user_plan():
    user = get_current_user()
    if not user:
        return PLANS["free"]
    plan_key = user.get("plan", "free")
    return PLANS.get(plan_key, PLANS["free"])


def check_message_limit():
    user = get_current_user()
    if not user:
        return False, 0, 0
    if user.get("is_admin", False):
        return True, 999999, 999999
    plan = get_user_plan()
    limit = plan["daily_messages"]
    used = user.get("messages_today", 0)
    remaining = max(0, limit - used)
    return remaining > 0, remaining, limit


def check_word_limit(text):
    user = get_current_user()
    if not user:
        return False, 0, 0
    if user.get("is_admin", False):
        return True, len(text.split()), 999999
    plan = get_user_plan()
    max_words = plan["max_words_per_message"]
    word_count = len(text.split())
    return word_count <= max_words, word_count, max_words


def increment_message_count():
    user = get_current_user()
    if not user or user.get("is_admin", False):
        return
    users_db = load_users_db()
    email = user.get("email", "").lower()
    if email not in users_db:
        return
    today_str = str(date.today())
    if users_db[email].get("last_reset_date") != today_str:
        users_db[email]["messages_today"] = 0
        users_db[email]["last_reset_date"] = today_str
    users_db[email]["messages_today"] = users_db[email].get("messages_today", 0) + 1
    users_db[email]["total_messages"] = users_db[email].get("total_messages", 0) + 1
    save_users_db(users_db)
    st.session_state.current_user["messages_today"] = users_db[email]["messages_today"]
    st.session_state.current_user["total_messages"] = users_db[email]["total_messages"]


def upgrade_user_plan(new_plan_key):
    user = get_current_user()
    if not user or user.get("is_admin"):
        return False
    if new_plan_key not in PLANS:
        return False
    users_db = load_users_db()
    email = user.get("email", "").lower()
    if email not in users_db:
        return False
    users_db[email]["plan"] = new_plan_key
    users_db[email]["upgraded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_users_db(users_db)
    st.session_state.current_user["plan"] = new_plan_key
    return True


# ═══════════════════════════════════════════════════════════
# AI BACKEND
# ═══════════════════════════════════════════════════════════

AI_BACKENDS = {}
groq_client = None


def init_groq():
    global groq_client
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and GROQ_AVAILABLE:
        try:
            groq_client = Groq(api_key=api_key)
            return True
        except Exception:
            return False
    return False


if init_groq():
    AI_BACKENDS["Llama 3.3 70B"] = {"type": "groq", "model": "llama-3.3-70b-versatile", "display": "Llama 3.3 70B"}
    AI_BACKENDS["Llama 3.1 8B"] = {"type": "groq", "model": "llama-3.1-8b-instant", "display": "Llama 3.1 8B"}

AI_BACKENDS["Llama Local"] = {"type": "ollama", "model": "llama3.2:3b", "display": "Llama Local"}
DEFAULT_BACKEND_NAME = list(AI_BACKENDS.keys())[0]


def call_ai(messages, backend_config):
    try:
        if backend_config["type"] == "groq":
            if not groq_client:
                return "AI not configured."
            r = groq_client.chat.completions.create(
                model=backend_config["model"], messages=messages,
                temperature=0.7, max_tokens=1000, top_p=0.9,
            )
            return r.choices[0].message.content
        else:
            if not OLLAMA_AVAILABLE:
                return "Local model unavailable."
            r = ollama.chat(model=backend_config["model"], messages=messages)
            return r["message"]["content"]
    except Exception as e:
        return "Error: " + str(e)


# ═══════════════════════════════════════════════════════════
# CACHED RESOURCES
# ═══════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_embedding_model():
    if not EMBEDDINGS_AVAILABLE:
        return None
    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def load_all_collections():
    collections = {}
    if not CHROMADB_AVAILABLE:
        return {k: None for k in WISDOM_SOURCES.keys()}
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    except Exception:
        return {k: None for k in WISDOM_SOURCES.keys()}
    for source in WISDOM_SOURCES.keys():
        try:
            collections[source] = chroma_client.get_collection(name=source + "_wisdom")
        except Exception:
            collections[source] = None
    return collections


@st.cache_resource(show_spinner=False)
def load_whisper_model():
    if not WHISPER_AVAILABLE:
        return None
    try:
        return whisper.load_model("base")
    except Exception:
        return None


def search_wisdom(question, selected_sources, top_k=5):
    embedding_model = load_embedding_model()
    collections = load_all_collections()
    all_results = {}
    if embedding_model is None:
        return all_results
    for source in selected_sources:
        col = collections.get(source)
        if col is None:
            continue
        try:
            question_embedding = embedding_model.encode(question).tolist()
            results = col.query(query_embeddings=[question_embedding], n_results=top_k)
            documents = results["documents"][0]
            distances = results["distances"][0]
            source_passages = []
            for doc, distance in zip(documents, distances):
                similarity = 1 - distance
                if similarity >= 0.30:
                    source_passages.append({"text": doc, "relevance": round(similarity * 100, 2)})
            source_passages.sort(key=lambda x: x["relevance"], reverse=True)
            if source_passages:
                all_results[source] = source_passages[:3]
        except Exception:
            pass
    return all_results


def build_wisdom_context(wisdom_results):
    if not wisdom_results:
        return ""
    lines = []
    for source, passages in wisdom_results.items():
        source_name = WISDOM_SOURCES.get(source, {}).get("name", source)
        for p in passages:
            snippet = p["text"].strip().replace("\n", " ")[:500]
            lines.append("[" + source_name + "] " + snippet)
    return "\n\n".join(lines)


# ═══════════════════════════════════════════════════════════
# DETECTION
# ═══════════════════════════════════════════════════════════

def detect_heavy_emotion(text):
    lower = text.lower().strip()
    return any(p.lower() in lower for p in HEAVY_EMOTIONAL_WORDS)


def detect_force_answer(text):
    lower = text.lower().strip()
    return any(p.lower() in lower for p in FORCE_ANSWER_PHRASES)


def detect_needs_clarification(text):
    lower = text.lower().strip()
    word_count = len(lower.split())
    for starter in VAGUE_STARTERS:
        if starter.lower() in lower and word_count < 15:
            return True
    if word_count < 5:
        for word in ["sad", "lost", "confused", "tired", "udaas", "pareshan"]:
            if word in lower:
                return True
    return False


def detect_language(text):
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"
    words = re.findall(r"[a-zA-Z]+", text.lower())
    if not words:
        return "english"
    hinglish_count = sum(1 for w in words if w in HINGLISH_WORDS)
    if len(words) <= 5 and hinglish_count >= 1:
        return "hinglish"
    if len(words) > 5 and hinglish_count >= 2:
        return "hinglish"
    return "english"


def detect_yumea_mode(user_input):
    lowered = user_input.strip().lower()
    cleaned = re.sub('[!?.,;:]+$', '', lowered).strip()
    if detect_heavy_emotion(user_input):
        return "silence", user_input
    force_answer = detect_force_answer(user_input)
    if cleaned in CASUAL_GREETINGS:
        return "human", user_input
    words = cleaned.split()
    if len(words) <= 3:
        for greeting in CASUAL_GREETINGS:
            if cleaned.startswith(greeting):
                return "human", user_input
    if not force_answer and detect_needs_clarification(user_input):
        if st.session_state.get("clarify_count", 0) < 3:
            return "clarify", user_input
    if any(kw in lowered for kw in WISDOM_KEYWORDS):
        st.session_state["clarify_count"] = 0
        return "wisdom", user_input
    st.session_state["clarify_count"] = 0
    return "human", user_input
    # ═══════════════════════════════════════════════════════════
# SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════

def build_system_prompt(mode, language, mood, wisdom_context, persona_mode="friend"):
    lang_name = LANGUAGE_NAMES.get(language, "English")
    mood_line = ""
    if mood:
        mood_label = MOODS.get(mood, {}).get("label", mood)
        mood_line = "User feels: " + mood_label + ". Be sensitive.\n"
    
    identity_rules = (
        "\n═══ YOUR IDENTITY (YUMEA) ═══\n"
        "You are YUMEA - a FEMALE AI companion (she/her).\n"
        "You are NOT a general assistant. You are a SPECIFIC companion for:\n"
        "  - Emotional support and mental well-being\n"
        "  - Spiritual guidance from 11 wisdom traditions\n"
        "  - Life reflection, clarity, and inner peace\n\n"
        
        "═══ WHAT YOU DO NOT DO ═══\n"
        "You do NOT help with: Coding, homework, recipes, general tasks.\n"
        "If asked, redirect: 'Bhai, main us cheez ke liye nahi hoon. Main tumhare mann ki companion hoon.'\n\n"
        
        "═══ IDENTITY INTRODUCTION ═══\n"
        "If user asks who you are:\n"
        "'Main Yumea hoon - ek AI companion jo tumhare emotional aur spiritual journey mein saathi banti hoon. "
        "Main 11 wisdom traditions se seekhi hoon. Jab dil bhaari ho ya clarity chahiye - main yahaan hoon.'\n\n"
        
        "═══ FEMININE SELF-REFERENCE ═══\n"
        "Use: karti hoon, sochti hoon (NOT karta hoon)\n"
        "DO NOT overuse 'sunti hoon' - vary language.\n\n"
        
        "═══ USER GENDER (DEFAULT MALE) ═══\n"
        "Default: Assume user is MALE. Use 'bhai', 'yaar', 'tum'.\n"
        "If user says 'main ladki hu' → switch to feminine addressing.\n\n"
        
        "═══ RESPECT FOR SPIRITUAL FIGURES ═══\n"
        "Use plural respectful forms:\n"
        "CORRECT: 'Osho ka janm 1931 mein hua tha. Woh paida hue the.'\n"
        "WRONG: 'Osho paida hua tha.'\n"
        "Use: 'unhone kaha tha', 'woh bole the', 'unka janm hua'\n"
    )
    
    if mode == "human":
        return (
            "You are Yumea, a warm caring FEMALE AI companion. "
            "Respond in 1-2 short warm sentences in " + lang_name + ". "
            "Be natural, like a caring friend. " + mood_line + identity_rules
        )
    
    if persona_mode == "friend":
        base = (
            "You are Yumea, a wise warm FEMALE AI companion. " + mood_line +
            "1. Respond in " + lang_name + " naturally\n"
            "2. NEVER quote sources by name in friend mode\n"
            "3. Talk like a caring friend\n"
            "4. Keep responses SHORT (2-4 sentences)\n"
            + identity_rules
        )
        if wisdom_context:
            base += "\nBACKGROUND:\n" + wisdom_context
        return base
    else:
        base = (
            "You are Yumea, a FEMALE wisdom teacher. " + mood_line +
            "Respond in " + lang_name + " with:\n"
            "**I hear you:** [feeling]\n"
            "**Wisdom:** [source-cited]\n"
            "**For you:** [action]\n"
            + identity_rules
        )
        if wisdom_context:
            base += "\nSources:\n" + wisdom_context
        return base


def generate_clarifying_question(user_input, language):
    lang_name = LANGUAGE_NAMES.get(language, "English")
    system_prompt = (
        "You are Yumea. Ask ONE short clarifying question in " + lang_name + ". "
        "Under 25 words. Use feminine self-reference. Address user as bhai/yaar (male default)."
    )
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
    try:
        response = call_ai(messages, st.session_state.current_backend)
        return re.sub(r'\*\*(.*?)\*\*', r'\1', response).strip()
    except Exception:
        return "Thoda aur batao bhai - kya ho raha hai?"


def generate_silence_response(user_input, language):
    lang_name = LANGUAGE_NAMES.get(language, "English")
    system_prompt = (
        "User in pain. Be present. 3-4 lines in " + lang_name + ". "
        "Add: iCall 9152987821"
    )
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
    try:
        response = call_ai(messages, st.session_state.current_backend)
        return re.sub(r'\*\*(.*?)\*\*', r'\1', response).strip()
    except Exception:
        return "Ruko bhai. Main yahaan hoon.\nEk gehri saans lo.\nPlease reach out: iCall 9152987821"


# ═══════════════════════════════════════════════════════════
# VOICE
# ═══════════════════════════════════════════════════════════

def transcribe_audio(audio_bytes):
    if not WHISPER_AVAILABLE:
        return ""
    model = load_whisper_model()
    if model is None:
        return ""
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        result = model.transcribe(tmp_path)
        return result.get("text", "").strip()
    except Exception:
        return ""
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def clean_text_for_speech(text):
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    cleaned = re.sub(r"[*_#`]", "", cleaned)
    cleaned = re.sub(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF]", "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


async def _generate_speech_bytes(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
    return b"".join(audio_chunks)


def generate_speech(text, voice):
    if not EDGE_TTS_AVAILABLE:
        return None
    try:
        cleaned = clean_text_for_speech(text)
        if not cleaned:
            return None
        loop = asyncio.new_event_loop()
        try:
            audio_bytes = loop.run_until_complete(_generate_speech_bytes(cleaned, voice))
        finally:
            loop.close()
        return audio_bytes
    except Exception:
        return None


def play_audio_html(text, lang, autoplay=False):
    if not EDGE_TTS_AVAILABLE:
        return ""
    lang_voices = VOICE_OPTIONS.get(lang, VOICE_OPTIONS["english"])
    voice = list(lang_voices.values())[0]
    audio_bytes = generate_speech(text, voice)
    if not audio_bytes:
        return ""
    b64 = base64.b64encode(audio_bytes).decode()
    autoplay_attr = " autoplay" if autoplay else ""
    return (
        '<audio controls' + autoplay_attr + ' style="width:100%;height:32px;">'
        '<source src="data:audio/mp3;base64,' + b64 + '" type="audio/mp3">'
        '</audio>'
    )


# ═══════════════════════════════════════════════════════════
# USER LIBRARY
# ═══════════════════════════════════════════════════════════

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "library" not in data:
                    data["library"] = []
                return data
        except Exception:
            pass
    return {"library": []}


def save_user_data(data):
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def add_to_library(text, source_emojis="", lang="english"):
    data = st.session_state.user_data
    data["library"].append({
        "id": str(uuid.uuid4())[:8],
        "text": text,
        "sources": source_emojis,
        "lang": lang,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_user_data(data)


# ═══════════════════════════════════════════════════════════
# MESSAGE PROCESSOR
# ═══════════════════════════════════════════════════════════

def process_user_message(user_text):
    if not user_text or not user_text.strip():
        return
    
    can_send, remaining, limit = check_message_limit()
    if not can_send:
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({
            "role": "assistant",
            "content": "⚠️ You've reached your daily limit of " + str(limit) + " messages.\n\n"
                       "💎 Upgrade to Premium for more conversations!\n"
                       "Click **Buy Premium** in sidebar to upgrade.",
            "response_time": 0,
            "sources": "🔒 Limit reached",
            "lang": "english",
        })
        return
    
    valid, word_count, max_words = check_word_limit(user_text)
    if not valid:
        st.session_state.messages.append({"role": "user", "content": user_text[:200] + "..."})
        st.session_state.messages.append({
            "role": "assistant",
            "content": "⚠️ Message too long! Max " + str(max_words) + " words allowed.\n"
                       "Your message: " + str(word_count) + " words.\n\n"
                       "💎 Upgrade to Premium for longer messages!",
            "response_time": 0,
            "sources": "🔒 Word limit",
            "lang": "english",
        })
        return
    
    start_time = time.time()
    mode, cleaned_text = detect_yumea_mode(user_text)
    language = detect_language(user_text)
    persona = st.session_state.get("persona_mode", "friend")
    
    if mode == "silence":
        reply = generate_silence_response(user_text, language)
        elapsed = round(time.time() - start_time, 1)
        st.session_state.clarify_count = 0
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({
            "role": "assistant", "content": reply, "response_time": elapsed,
            "sources": "🤫 Silence", "lang": language,
        })
        increment_message_count()
        return
    
    if mode == "clarify":
        question = generate_clarifying_question(user_text, language)
        st.session_state.clarify_count += 1
        elapsed = round(time.time() - start_time, 1)
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({
            "role": "assistant", "content": question, "response_time": elapsed,
            "sources": "🤔 Understanding...", "lang": language,
        })
        increment_message_count()
        return
    
    wisdom_results = search_wisdom(cleaned_text, st.session_state.selected_sources, top_k=3)
    wisdom_context = build_wisdom_context(wisdom_results)
    system_prompt = build_system_prompt(mode, language, st.session_state.current_mood, wisdom_context, persona)
    
    history = st.session_state.conversation_history[-6:] \
        if len(st.session_state.conversation_history) > 6 \
        else st.session_state.conversation_history
    
    api_messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_text}]
    reply = call_ai(api_messages, st.session_state.current_backend)
    elapsed = round(time.time() - start_time, 1)
    
    source_emojis = "💛 Friend" if persona == "friend" else "🧘 Professional"
    st.session_state.clarify_count = 0
    
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.session_state.messages.append({
        "role": "assistant", "content": reply, "response_time": elapsed,
        "sources": source_emojis, "lang": language,
    })
    st.session_state.conversation_history.append({"role": "user", "content": user_text})
    st.session_state.conversation_history.append({"role": "assistant", "content": reply})
    
    increment_message_count()


# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════

def init_session_state():
    defaults = {
        "messages": [],
        "conversation_history": [],
        "selected_sources": ["osho", "gita"],
        "current_mood": None,
        "current_backend": AI_BACKENDS[DEFAULT_BACKEND_NAME],
        "backend_name": DEFAULT_BACKEND_NAME,
        "play_audio_for": None,
        "pending_input": None,
        "last_processed_audio": None,
        "user_data": load_user_data(),
        "current_page": "signin",
        "daily_quote": DAILY_QUOTES[datetime.now().timetuple().tm_yday % len(DAILY_QUOTES)],
        "clarify_count": 0,
        "debate_mode": False,
        "persona_mode": "friend",
        "is_authenticated": False,
        "current_user": None,
        "is_admin": False,
        "selected_plan": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(page):
    st.session_state.current_page = page
    st.rerun()


init_session_state()


# ═══════════════════════════════════════════════════════════
# AUTH PAGES CSS
# ═══════════════════════════════════════════════════════════

def _inject_auth_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        background: #0a0a14 !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a14 0%, #12122a 50%, #0a0a14 100%) !important;
    }
    
    .main .block-container {
        padding: 20px !important;
        max-width: 100% !important;
    }
    
    .auth-container {
        max-width: 450px;
        margin: 30px auto;
        padding: 35px 30px;
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.7), rgba(49, 46, 129, 0.4));
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }
    
    .auth-hero {
        text-align: center;
        margin-bottom: 25px;
    }
    
    .auth-logo {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin: 0 auto 15px;
        overflow: hidden;
        border: 3px solid rgba(139, 92, 246, 0.5);
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.4);
    }
    
    .auth-logo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .auth-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff, #a78bfa, #ec4899);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin: 0 0 8px 0;
    }
    
    .auth-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        margin: 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.15)) !important;
        color: #d4b3ff !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        padding: 11px 18px !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.35), rgba(99, 102, 241, 0.25)) !important;
        border-color: rgba(139, 92, 246, 0.7) !important;
    }
    
    .stTextInput input {
        background: rgba(15, 15, 30, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    
    label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }
    
    .auth-divider {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin: 20px 0;
    }
    
    .auth-info-box {
        background: rgba(139, 92, 246, 0.08);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 10px;
        padding: 12px 15px;
        margin-top: 15px;
        color: #c4b5fd;
        font-size: 0.82rem;
        text-align: center;
    }
    
    .premium-hero {
        text-align: center;
        padding: 40px 20px 30px;
        max-width: 700px;
        margin: 0 auto;
    }
    
    .premium-badge {
        display: inline-block;
        background: rgba(240, 159, 51, 0.15);
        border: 1px solid rgba(240, 159, 51, 0.4);
        color: #f09f33;
        padding: 6px 18px;
        border-radius: 50px;
        font-size: 0.75rem;
        letter-spacing: 3px;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .premium-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff, #f09f33, #ec4899);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin: 10px 0;
    }
    
    .plan-card {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.7), rgba(49, 46, 129, 0.4));
        border: 2px solid rgba(139, 92, 246, 0.25);
        border-radius: 20px;
        padding: 25px 22px;
    }
    
    .plan-card.featured {
        border-color: rgba(240, 159, 51, 0.5);
        background: linear-gradient(135deg, rgba(240, 159, 51, 0.15), rgba(49, 46, 129, 0.5));
    }
    
    .featured-badge {
        background: linear-gradient(135deg, #f09f33, #de6f3d);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .plan-emoji { font-size: 2.8rem; text-align: center; margin-bottom: 10px; }
    .plan-name { color: #fff; font-size: 1.25rem; font-weight: 700; text-align: center; }
    .plan-price { text-align: center; margin: 15px 0; }
    .plan-price-amount {
        font-size: 2.3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff, #a78bfa);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .plan-price-currency { color: #94a3b8; font-size: 1rem; vertical-align: super; }
    .plan-price-period { color: #94a3b8; font-size: 0.85rem; }
    .plan-features { list-style: none; padding: 0; margin: 15px 0; }
    .plan-features li {
        padding: 6px 0;
        color: #cbd5e1;
        font-size: 0.85rem;
    }
    .plan-features li::before {
        content: '✓ ';
        color: #10b981;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SIGN IN / SIGN UP / PREMIUM / PAYMENT PAGES
# ═══════════════════════════════════════════════════════════

def page_signin():
    _inject_auth_css()
    avatar_b64 = load_image_b64("yumea-user.jpg")
    if avatar_b64:
        avatar_html = '<img src="data:image/jpeg;base64,' + avatar_b64 + '" alt="Yumea">'
    else:
        avatar_html = '<div style="width:100%;height:100%;background:linear-gradient(135deg,#8b5cf6,#ec4899);display:flex;align-items:center;justify-content:center;color:white;font-size:2rem;font-weight:900;">Y</div>'
    
    st.markdown(
        '<div class="auth-container">'
        '<div class="auth-hero">'
        '<div class="auth-logo">' + avatar_html + '</div>'
        '<h1 class="auth-title">Welcome Back</h1>'
        '<p class="auth-subtitle">Sign in to continue with Yumea 💛</p>'
        '</div></div>',
        unsafe_allow_html=True
    )
    
    with st.form("signin_form"):
        email = st.text_input("📧 Email or Username", placeholder="your@email.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Your password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            with st.spinner("Signing in..."):
                success, message, user_data = login_user(email, password)
            if success:
                st.session_state.is_authenticated = True
                st.session_state.current_user = user_data
                st.session_state.is_admin = user_data.get("is_admin", False)
                st.session_state.current_page = "chat"
                st.success(message)
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)
    
    st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
    
    if st.button("✨ Create New Account", key="switch_signup"):
        st.session_state.current_page = "signup"
        st.rerun()
    
    st.markdown(
        '<div class="auth-info-box">'
        '🎁 Sign up FREE — get <strong>30 messages/day</strong> to chat with Yumea!'
        '</div>',
        unsafe_allow_html=True
    )


def page_signup():
    _inject_auth_css()
    avatar_b64 = load_image_b64("yumea-user.jpg")
    if avatar_b64:
        avatar_html = '<img src="data:image/jpeg;base64,' + avatar_b64 + '" alt="Yumea">'
    else:
        avatar_html = '<div style="width:100%;height:100%;background:linear-gradient(135deg,#8b5cf6,#ec4899);display:flex;align-items:center;justify-content:center;color:white;font-size:2rem;font-weight:900;">Y</div>'
    
    st.markdown(
        '<div class="auth-container">'
        '<div class="auth-hero">'
        '<div class="auth-logo">' + avatar_html + '</div>'
        '<h1 class="auth-title">Join Yumea</h1>'
        '<p class="auth-subtitle">Create your account — it\'s FREE ✨</p>'
        '</div></div>',
        unsafe_allow_html=True
    )
    
    with st.form("signup_form"):
        name = st.text_input("👤 Your Name")
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password")
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            if password != confirm_password:
                st.error("Passwords don't match!")
            else:
                with st.spinner("Creating account..."):
                    success, message = create_user_account(name, email, password)
                if success:
                    st.success(message + " Please sign in.")
                    time.sleep(1.5)
                    st.session_state.current_page = "signin"
                    st.rerun()
                else:
                    st.error(message)
    
    st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
    
    if st.button("← Back to Sign In", key="switch_signin"):
        st.session_state.current_page = "signin"
        st.rerun()


def page_premium():
    _inject_auth_css()
    
    if st.button("← Back to Chat", key="premium_back"):
        st.session_state.current_page = "chat"
        st.rerun()
    
    st.markdown(
        '<div class="premium-hero">'
        '<div class="premium-badge">✨ UPGRADE TO PREMIUM ✨</div>'
        '<h1 class="premium-title">Unlock More Wisdom</h1>'
        '<p style="color:#94a3b8;">Choose the plan that fits your journey.</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown(
            '<div class="plan-card">'
            '<div class="plan-emoji">⭐</div>'
            '<div class="plan-name">Premium Lite</div>'
            '<div class="plan-price">'
            '<span class="plan-price-currency">₹</span>'
            '<span class="plan-price-amount">69</span>'
            '<span class="plan-price-period">/month</span>'
            '</div>'
            '<ul class="plan-features">'
            '<li>150 messages per day</li>'
            '<li>2000 words per message</li>'
            '<li>All 11 wisdom sources</li>'
            '<li>Voice input & output</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("Get Premium Lite", key="buy_69", use_container_width=True):
            st.session_state.selected_plan = "premium_69"
            st.session_state.current_page = "payment"
            st.rerun()
    
    with col2:
        st.markdown(
            '<div class="plan-card featured">'
            '<div style="text-align:center;"><span class="featured-badge">BEST VALUE</span></div>'
            '<div class="plan-emoji">💎</div>'
            '<div class="plan-name">Premium Pro</div>'
            '<div class="plan-price">'
            '<span class="plan-price-currency">₹</span>'
            '<span class="plan-price-amount">199</span>'
            '<span class="plan-price-period">/month</span>'
            '</div>'
            '<ul class="plan-features">'
            '<li>500 messages per day</li>'
            '<li>5000 words per message</li>'
            '<li>All 11 wisdom sources</li>'
            '<li>Voice input & output</li>'
            '<li>Priority support</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("Get Premium Pro", key="buy_199", use_container_width=True):
            st.session_state.selected_plan = "premium_199"
            st.session_state.current_page = "payment"
            st.rerun()


def page_payment():
    _inject_auth_css()
    
    selected_plan = st.session_state.get("selected_plan", "premium_69")
    plan_data = PLANS.get(selected_plan, PLANS["premium_69"])
    
    if st.button("← Back to Plans", key="payment_back"):
        st.session_state.current_page = "premium"
        st.rerun()
    
    st.markdown(
        '<div class="auth-container">'
        '<div style="text-align:center;">'
        '<div style="font-size:4rem;">' + plan_data["badge"] + '</div>'
        '<h1 style="color:#fff;font-size:1.7rem;margin:10px 0;">Complete Payment</h1>'
        '<p style="color:#94a3b8;">Upgrading to <strong style="color:#a78bfa;">' + plan_data["name"] + '</strong></p>'
        '<p style="font-size:2rem;color:#f09f33;font-weight:700;margin:20px 0;">₹' + str(plan_data["price"]) + '/month</p>'
        '<p style="color:#fbbf24;font-size:0.85rem;">⚠️ Demo mode - click to activate</p>'
        '</div></div>',
        unsafe_allow_html=True
    )
    
    if st.button("🔐 Pay ₹" + str(plan_data["price"]) + " (Demo)", key="mock_pay", use_container_width=True):
        if upgrade_user_plan(selected_plan):
            st.balloons()
            st.success("🎉 Welcome to " + plan_data["name"] + "!")
            time.sleep(2)
            st.session_state.current_page = "chat"
            st.rerun()
            # ═══════════════════════════════════════════════════════════
# CHAT PAGE
# ═══════════════════════════════════════════════════════════

def _get_avatar_html(size_px=44):
    avatar_b64 = load_image_b64("yumea-user.jpg")
    if avatar_b64:
        return (
            '<img src="data:image/jpeg;base64,' + avatar_b64 + '" '
            'style="width:' + str(size_px) + 'px;height:' + str(size_px) + 'px;'
            'border-radius:50%;object-fit:cover;'
            'border:2px solid rgba(139,92,246,0.5);'
            'display:inline-block;vertical-align:middle;flex-shrink:0;" alt="Yumea">'
        )
    return (
        '<div style="width:' + str(size_px) + 'px;height:' + str(size_px) + 'px;'
        'border-radius:50%;background:linear-gradient(135deg,#8b5cf6,#ec4899);'
        'display:inline-flex;align-items:center;justify-content:center;'
        'font-size:' + str(int(size_px * 0.45)) + 'px;font-weight:800;color:#fff;'
        'border:2px solid rgba(139,92,246,0.5);flex-shrink:0;">Y</div>'
    )


def _inject_chat_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Spectral:ital,wght@0,400;1,400&display=swap');

html, body {
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    background: #0a0a14 !important;
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    height: 100vh !important;
    overflow: hidden !important;
    background: linear-gradient(135deg, #0a0a14 0%, #12122a 50%, #0a0a14 100%) !important;
}

[data-testid="stAppViewContainer"] {
    height: 100vh !important;
    overflow: hidden !important;
}

.main {
    height: 100vh !important;
    overflow: hidden !important;
    padding: 0 !important;
}

.main .block-container {
    height: 100vh !important;
    overflow: hidden !important;
    padding: 0 !important;
    max-width: 100% !important;
    margin: 0 !important;
}

section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
header[data-testid="stHeader"],
footer,
#MainMenu,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

[data-testid="stHorizontalBlock"] {
    height: 100vh !important;
    gap: 0 !important;
    overflow: hidden !important;
    display: flex !important;
}

[data-testid="stHorizontalBlock"] > div:first-child {
    height: 100vh !important;
    width: 260px !important;
    max-width: 260px !important;
    min-width: 260px !important;
    flex: 0 0 260px !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    background: linear-gradient(180deg, #0d0d1f 0%, #0a0a15 100%) !important;
    border-right: 1px solid rgba(139, 92, 246, 0.15) !important;
    padding: 14px !important;
    scrollbar-width: none;
}

[data-testid="stHorizontalBlock"] > div:first-child::-webkit-scrollbar { width: 0px; }

[data-testid="stHorizontalBlock"] > div:first-child:hover {
    scrollbar-width: thin;
    scrollbar-color: rgba(139, 92, 246, 0.5) transparent;
}

[data-testid="stHorizontalBlock"] > div:first-child:hover::-webkit-scrollbar { width: 6px; }
[data-testid="stHorizontalBlock"] > div:first-child:hover::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #8b5cf6, #6366f1);
    border-radius: 3px;
}

[data-testid="stHorizontalBlock"] > div:nth-child(2) {
    height: 100vh !important;
    overflow: hidden !important;
    padding: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    background: linear-gradient(180deg, #0f0f1e 0%, #0a0a14 100%) !important;
    flex: 1 !important;
}

.yumea-chat-header {
    background: linear-gradient(180deg, #12122a 0%, #0f0f1e 100%);
    border-bottom: 1px solid rgba(139, 92, 246, 0.2);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
    height: 68px;
}

.yumea-header-info { flex: 1; }

.yumea-header-name {
    color: #ffffff;
    font-size: 1.05rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 6px;
}

.yumea-verified {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    border-radius: 50%;
    font-size: 0.7rem;
    color: white;
    font-weight: 700;
}

.yumea-header-status {
    color: #10b981;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 2px;
}

.yumea-pulse-dot {
    width: 7px;
    height: 7px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 10px #10b981;
    animation: yumea-pulse 2s infinite;
}

@keyframes yumea-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

.yumea-header-actions {
    display: flex;
    gap: 8px;
}

.rainbow-icon-btn {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    cursor: pointer;
    background: linear-gradient(135deg, #1a1a2e, #16162a, #0f0f1e, #16162a, #1a1a2e) no-repeat;
    background-size: 300%;
    color: #a78bfa;
    border: 1px solid rgba(139, 92, 246, 0.4);
    background-position: left center;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    transition: all 0.3s ease;
    position: relative;
}

.rainbow-icon-btn:hover {
    background-size: 320%;
    background-position: right center;
    transform: translateY(-2px) scale(1.05);
}

.rainbow-icon-btn::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: -38px;
    left: 50%;
    transform: translateX(-50%);
    background: #1e1b4b;
    color: #fbbf24;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease;
    border: 1px solid rgba(251, 191, 36, 0.3);
    z-index: 200;
}

.rainbow-icon-btn:hover::after { opacity: 1; }

.yumea-messages-area {
    flex: 1 1 auto !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding: 16px 20px !important;
    scroll-behavior: smooth;
    max-height: calc(100vh - 68px - 80px) !important;
    scrollbar-width: none;
}

.yumea-messages-area::-webkit-scrollbar { width: 0px; }

.yumea-messages-area:hover {
    scrollbar-width: thin;
    scrollbar-color: rgba(139, 92, 246, 0.5) transparent;
}

.yumea-messages-area:hover::-webkit-scrollbar { width: 8px; }
.yumea-messages-area:hover::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #8b5cf6, #6366f1);
    border-radius: 4px;
}

.yumea-msg-row {
    display: flex;
    margin-bottom: 10px;
    animation: yumea-msg-in 0.3s ease;
}

@keyframes yumea-msg-in {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.yumea-msg-row.user { justify-content: flex-end; }

.yumea-msg-row.assistant {
    justify-content: flex-start;
    gap: 8px;
    align-items: flex-start;
}

.yumea-bubble-user {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
    color: #ffffff;
    padding: 11px 18px;
    border-radius: 20px 20px 4px 20px;
    max-width: 68%;
    font-size: 0.94rem;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
}

.yumea-bubble-asst {
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.95), rgba(49, 46, 129, 0.85));
    color: #f1f5f9;
    padding: 11px 18px;
    border-radius: 20px 20px 20px 4px;
    max-width: 68%;
    font-size: 0.94rem;
    line-height: 1.55;
    border: 1px solid rgba(139, 92, 246, 0.2);
}

.yumea-msg-time {
    font-size: 0.65rem;
    margin-top: 4px;
}

.yumea-bubble-user .yumea-msg-time {
    color: rgba(255,255,255,0.6);
    text-align: right;
}

.yumea-bubble-asst .yumea-msg-time { color: #94a3b8; }

.yumea-msg-meta {
    font-size: 0.68rem;
    color: #a78bfa;
    margin-top: 4px;
    margin-left: 42px;
}

.yumea-empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px 30px;
    text-align: center;
    min-height: 50vh;
}

.yumea-empty-avatar {
    animation: yumea-float 3s ease-in-out infinite;
}

@keyframes yumea-float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

.yumea-empty-title {
    color: #ffffff;
    font-size: 1.6rem;
    font-weight: 800;
    margin-top: 22px;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #ffffff, #a78bfa);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.yumea-empty-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    max-width: 420px;
    line-height: 1.6;
    margin-bottom: 30px;
}

.yumea-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 14px 0;
    border-bottom: 1px solid rgba(139, 92, 246, 0.15);
    margin-bottom: 14px;
}

.yumea-sidebar-brand-name {
    color: #ffffff;
    font-weight: 800;
    font-size: 1.05rem;
    background: linear-gradient(135deg, #ffffff, #a78bfa);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.yumea-user-card {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.08));
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 12px;
}

.yumea-user-name {
    color: #ffffff;
    font-weight: 700;
    font-size: 0.95rem;
}

.yumea-user-plan {
    color: #a78bfa;
    font-size: 0.75rem;
    margin-top: 2px;
}

.yumea-msg-counter {
    background: rgba(15, 15, 30, 0.5);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 10px;
    padding: 10px 12px;
    margin-top: 8px;
    text-align: center;
}

.yumea-msg-counter-num {
    color: #ffffff;
    font-weight: 700;
    font-size: 1rem;
}

.yumea-msg-counter-label {
    color: #94a3b8;
    font-size: 0.7rem;
    margin-top: 2px;
}

.yumea-quote-card {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.06));
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 12px;
}

.yumea-quote-label {
    color: #a78bfa;
    font-size: 0.62rem;
    letter-spacing: 2px;
    font-weight: 700;
    margin-bottom: 6px;
    text-transform: uppercase;
}

.yumea-quote-text {
    color: #e2e8f0;
    font-family: 'Spectral', serif;
    font-style: italic;
    font-size: 0.82rem;
    line-height: 1.5;
    margin-bottom: 6px;
}

.yumea-quote-source {
    color: #c4b5fd;
    font-size: 0.72rem;
    font-weight: 600;
}

.yumea-section-label {
    color: #64748b;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 12px 0 6px 0;
}

.yumea-mode-display {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.1));
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 10px;
    padding: 8px;
    text-align: center;
    color: #d4b3ff;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 6px;
}

.stButton > button {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(99, 102, 241, 0.1)) !important;
    color: #d4b3ff !important;
    border: 1px solid rgba(139, 92, 246, 0.25) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.25), rgba(99, 102, 241, 0.2)) !important;
    border-color: rgba(139, 92, 246, 0.5) !important;
}

.stCheckbox label {
    color: #cbd5e1 !important;
    font-size: 0.8rem !important;
}

.stSelectbox > div > div {
    background: rgba(15, 15, 30, 0.8) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(139, 92, 246, 0.25) !important;
    border-radius: 10px !important;
}

.streamlit-expanderHeader {
    background: rgba(139, 92, 246, 0.05) !important;
    border-radius: 10px !important;
    color: #d4b3ff !important;
    font-size: 0.82rem !important;
}

[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 260px !important;
    right: 0 !important;
    z-index: 1000 !important;
    background: linear-gradient(180deg, #0f0f1e 0%, #0a0a14 100%) !important;
    border-top: 1px solid rgba(139, 92, 246, 0.2) !important;
    padding: 12px 20px !important;
    height: 80px !important;
}

[data-testid="stChatInput"] > div {
    background: transparent !important;
}

[data-testid="stChatInput"] textarea {
    background: rgba(15, 15, 30, 0.9) !important;
    color: #ffffff !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 22px !important;
    padding: 12px 20px 12px 60px !important;
    font-size: 0.94rem !important;
    min-height: 46px !important;
}

.yumea-mic-wrapper {
    position: fixed !important;
    bottom: 20px !important;
    left: calc(260px + 20px) !important;
    z-index: 1001 !important;
    width: 40px !important;
    height: 40px !important;
}

.yumea-mic-wrapper button {
    width: 40px !important;
    height: 40px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    font-size: 16px !important;
}

@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] > div:first-child { display: none !important; }
    [data-testid="stHorizontalBlock"] > div:nth-child(2) { width: 100% !important; }
    [data-testid="stChatInput"] { left: 0 !important; }
    .yumea-mic-wrapper { left: 20px !important; }
    .yumea-bubble-user, .yumea-bubble-asst { max-width: 85%; }
    .yumea-msg-meta { margin-left: 0; }
}
</style>

<script>
(function() {
    function scrollBottom() {
        var area = document.querySelector('.yumea-messages-area');
        if (area) area.scrollTop = area.scrollHeight;
    }
    setTimeout(scrollBottom, 100);
    setTimeout(scrollBottom, 300);
    setTimeout(scrollBottom, 600);
    var observer = new MutationObserver(scrollBottom);
    setTimeout(function() {
        var target = document.querySelector('.yumea-messages-area');
        if (target) observer.observe(target, {childList: true, subtree: true});
    }, 500);
})();
</script>
    """, unsafe_allow_html=True)


def _build_header_html():
    return (
        '<div class="yumea-chat-header">'
        + _get_avatar_html(44) +
        '<div class="yumea-header-info">'
        '<div class="yumea-header-name">Yumea <span class="yumea-verified">✓</span></div>'
        '<div class="yumea-header-status">'
        '<span class="yumea-pulse-dot"></span>online · always here'
        '</div>'
        '</div>'
        '<div class="yumea-header-actions">'
        '<div class="rainbow-icon-btn" data-tooltip="🔒 Coming Soon">📞</div>'
        '<div class="rainbow-icon-btn" data-tooltip="🔒 Coming Soon">📹</div>'
        '</div>'
        '</div>'
    )


def _build_empty_state_html():
    return (
        '<div class="yumea-empty-state">'
        '<div class="yumea-empty-avatar">' + _get_avatar_html(120) + '</div>'
        '<div class="yumea-empty-title">Hi, I\'m Yumea 💛</div>'
        '<div class="yumea-empty-subtitle">'
        'Your AI companion. Talk to me in Hindi, English, or Hinglish.'
        '</div>'
        '</div>'
    )

def generate_wisdom_card(text, source_name="Yumea"):
    """Generate a beautiful wisdom card image."""
    from PIL import Image, ImageDraw, ImageFont
    import io
    import textwrap
    
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), (10, 6, 18))
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    for y in range(H):
        ratio = y / H
        r = int(26 + (8 - 26) * ratio)
        g = int(10 + (5 - 10) * ratio)
        b = int(46 + (14 - 46) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    
    # Stars
    import random
    rng = random.Random(hash(text) % (2**31))
    for _ in range(120):
        x = rng.randint(0, W)
        y = rng.randint(0, H)
        radius = rng.choice([1, 1, 2])
        brightness = rng.randint(150, 255)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                     fill=(brightness, brightness, min(255, brightness + 10)))
    
    # Decorative circle
    draw.ellipse([W // 2 - 350, H // 2 - 350, W // 2 + 350, H // 2 + 350],
                 outline=(138, 43, 226, 80), width=1)
    
    # Fonts
    try:
        font_brand = ImageFont.truetype("arial.ttf", 60)
        font_sub = ImageFont.truetype("arial.ttf", 30)
        font_quote = ImageFont.truetype("arial.ttf", 44)
        font_source = ImageFont.truetype("arial.ttf", 34)
        font_tagline = ImageFont.truetype("arial.ttf", 22)
    except:
        font_brand = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_quote = ImageFont.load_default()
        font_source = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
    
    # Clean text
    clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    clean_text = re.sub(r'[*_#`]', '', clean_text).strip()
    if len(clean_text) > 220:
        clean_text = clean_text[:217] + "..."
    
    # YUMEA brand
    bbox = draw.textbbox((0, 0), "YUMEA", font=font_brand)
    brand_w = bbox[2] - bbox[0]
    draw.text(((W - brand_w) // 2, 80), "YUMEA", font=font_brand, fill=(255, 215, 0))
    
    # Subtitle
    bbox = draw.textbbox((0, 0), "AI That Feels", font=font_sub)
    sub_w = bbox[2] - bbox[0]
    draw.text(((W - sub_w) // 2, 150), "AI That Feels", font=font_sub, fill=(186, 85, 211))
    
    # Line
    draw.line([(W // 2 - 100, 200), (W // 2 + 100, 200)], fill=(212, 175, 55), width=2)
    
    # Quote
    wrapped = textwrap.wrap('"' + clean_text + '"', width=28)
    if len(wrapped) > 8:
        wrapped = wrapped[:8]
        wrapped[-1] = wrapped[-1][:20] + '..."'
    
    line_height = 60
    total_text_height = len(wrapped) * line_height
    start_y = (H - total_text_height) // 2 + 20
    
    for i, line in enumerate(wrapped):
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        line_w = bbox[2] - bbox[0]
        draw.text(((W - line_w) // 2, start_y + i * line_height),
                  line, font=font_quote, fill=(255, 255, 255))
    
    # Source
    source_text = "— " + source_name
    bbox = draw.textbbox((0, 0), source_text, font=font_source)
    source_w = bbox[2] - bbox[0]
    draw.text(((W - source_w) // 2, start_y + total_text_height + 30),
              source_text, font=font_source, fill=(212, 175, 55))
    
    # Bottom line
    draw.line([(W // 2 - 150, H - 160), (W // 2 + 150, H - 160)],
              fill=(186, 85, 211), width=2)
    
    # Tagline
    tagline = "Where heavy hearts find light and quiet minds"
    bbox = draw.textbbox((0, 0), tagline, font=font_tagline)
    tag_w = bbox[2] - bbox[0]
    draw.text(((W - tag_w) // 2, H - 130), tagline,
              font=font_tagline, fill=(154, 130, 184))
    
    # By Selvotex
    by_text = "by Selvotex"
    bbox = draw.textbbox((0, 0), by_text, font=font_tagline)
    by_w = bbox[2] - bbox[0]
    draw.text(((W - by_w) // 2, H - 80), by_text,
              font=font_tagline, fill=(154, 130, 184))
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def _build_messages_html(messages):
    if not messages:
        return ""
    html_parts = []
    time_str = datetime.now().strftime("%I:%M %p")
    avatar_sm = _get_avatar_html(34)
    
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        
        if role == "user":
            rendered = render_msg_text(content)
            html_parts.append(
                '<div class="yumea-msg-row user">'
                '<div class="yumea-bubble-user">'
                '<div>' + rendered + '</div>'
                '<div class="yumea-msg-time">' + time_str + '</div>'
                '</div></div>'
            )
        elif role == "assistant":
            sources = msg.get("sources", "")
            resp_time = msg.get("response_time", 0)
            bubble_content = '<div>' + render_msg_text(content) + '</div>'
            meta = ""
            if sources or resp_time:
                meta = '<div class="yumea-msg-meta">'
                if sources:
                    meta += html_module.escape(sources)
                if resp_time:
                    meta += ' · ⚡ ' + str(round(resp_time, 1)) + 's'
                meta += '</div>'
            html_parts.append(
                '<div class="yumea-msg-row assistant">'
                + avatar_sm +
                '<div style="max-width:calc(100% - 42px);">'
                '<div class="yumea-bubble-asst">'
                + bubble_content +
                '<div class="yumea-msg-time">' + time_str + '</div>'
                '</div>'
                + meta +
                '</div>'
                '</div>'
            )
    return "\n".join(html_parts)


def page_chat():
    typed_input = st.chat_input("Type a message...", key="yumea_chat_input")
    
    if st.session_state.pending_input:
        pending = st.session_state.pending_input
        st.session_state.pending_input = None
        with st.spinner("✨ Yumea is thinking..."):
            process_user_message(pending)
        st.rerun()
    
    if typed_input:
        with st.spinner("✨ Yumea is thinking..."):
            process_user_message(typed_input)
        st.rerun()
    
    _inject_chat_css()
    
    col_sidebar, col_chat = st.columns([1, 3], gap="small")
    
    with col_sidebar:
        st.markdown(
            '<div class="yumea-sidebar-brand">'
            + _get_avatar_html(36) +
            '<span class="yumea-sidebar-brand-name">YUMEA</span>'
            '</div>',
            unsafe_allow_html=True
        )
        
        user = get_current_user()
        if user:
            plan = get_user_plan()
            can_send, remaining, limit = check_message_limit()
            
            user_card_html = (
                '<div class="yumea-user-card">'
                '<div class="yumea-user-name">' + plan["badge"] + ' ' + html_module.escape(user.get("name", "User")) + '</div>'
                '<div class="yumea-user-plan">' + plan["name"] + ' Plan</div>'
            )
            
            if user.get("is_admin"):
                user_card_html += (
                    '<div class="yumea-msg-counter">'
                    '<div class="yumea-msg-counter-num">♾️</div>'
                    '<div class="yumea-msg-counter-label">UNLIMITED</div>'
                    '</div>'
                )
            else:
                used = limit - remaining
                user_card_html += (
                    '<div class="yumea-msg-counter">'
                    '<div class="yumea-msg-counter-num">' + str(used) + ' / ' + str(limit) + '</div>'
                    '<div class="yumea-msg-counter-label">MESSAGES TODAY</div>'
                    '</div>'
                )
            
            user_card_html += '</div>'
            st.markdown(user_card_html, unsafe_allow_html=True)
        
        quote = st.session_state.daily_quote
        st.markdown(
            '<div class="yumea-quote-card">'
            '<div class="yumea-quote-label">✨ Today\'s Wisdom</div>'
            '<div class="yumea-quote-text">"' + html_module.escape(quote["text"]) + '"</div>'
            '<div class="yumea-quote-source">— ' + html_module.escape(quote["source"]) + '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="yumea-section-label">🎭 Chat Mode</div>', unsafe_allow_html=True)
        current_persona = st.session_state.get("persona_mode", "friend")
        
        if current_persona == "friend":
            persona_display = "💛 Friend Mode"
            toggle_label = "🧘 Switch to Professional"
        else:
            persona_display = "🧘 Professional Mode"
            toggle_label = "💛 Switch to Friend"
        
        st.markdown('<div class="yumea-mode-display">' + persona_display + '</div>', unsafe_allow_html=True)
        
        if st.button(toggle_label, key="side_persona", use_container_width=True):
            st.session_state.persona_mode = "source" if current_persona == "friend" else "friend"
            st.rerun()
        
        st.markdown('<div class="yumea-section-label">📚 Wisdom Sources</div>', unsafe_allow_html=True)
        with st.expander(f"{len(st.session_state.selected_sources)} active"):
            for src_key, src_info in WISDOM_SOURCES.items():
                is_checked = src_key in st.session_state.selected_sources
                new_state = st.checkbox(
                    src_info["emoji"] + " " + src_info["name"],
                    value=is_checked,
                    key="side_src_" + src_key
                )
                if new_state and src_key not in st.session_state.selected_sources:
                    st.session_state.selected_sources.append(src_key)
                elif not new_state and src_key in st.session_state.selected_sources:
                    st.session_state.selected_sources.remove(src_key)
        
        st.markdown('<div class="yumea-section-label">🤖 AI Model</div>', unsafe_allow_html=True)
        backend_names = list(AI_BACKENDS.keys())
        current_idx = backend_names.index(st.session_state.backend_name) \
            if st.session_state.backend_name in backend_names else 0
        selected = st.selectbox("Model", backend_names, index=current_idx,
                                 key="side_model", label_visibility="collapsed")
        if selected != st.session_state.backend_name:
            st.session_state.backend_name = selected
            st.session_state.current_backend = AI_BACKENDS[selected]
        
        st.markdown('<div class="yumea-section-label">🏛️ Debate Mode</div>', unsafe_allow_html=True)
        debate_label = "🔴 Turn OFF" if st.session_state.debate_mode else "⚪ Turn ON"
        if st.button(debate_label, key="side_debate", use_container_width=True):
            if not st.session_state.debate_mode:
                if len(st.session_state.selected_sources) < 2:
                    st.warning("Select 2+ sources!")
                else:
                    st.session_state.debate_mode = True
                    st.rerun()
            else:
                st.session_state.debate_mode = False
                st.rerun()
        
        st.markdown('<div class="yumea-section-label">⚙️ Menu</div>', unsafe_allow_html=True)
        
        if st.button("💎 Buy Premium", key="side_premium", use_container_width=True):
            st.session_state.current_page = "premium"
            st.rerun()
        
        if st.button("🗑️ Clear Chat", key="side_clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
        
        if st.button("🚪 Logout", key="side_logout", use_container_width=True):
            logout_user()
            st.session_state.current_page = "signin"
            st.rerun()
    
    with col_chat:
        messages = st.session_state.messages
        
        st.markdown(_build_header_html(), unsafe_allow_html=True)
        
        if not messages:
            st.markdown(
                '<div class="yumea-messages-area">' + _build_empty_state_html() + '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown('<div style="max-width:500px;margin:0 auto;padding:0 20px 100px;">',
                        unsafe_allow_html=True)
            suggestions = [
                "Hey, Yumea 👋",
                "How do I find inner peace?",
                "Mujhe motivation chahiye",
                "What is the meaning of life?",
            ]
            for i, s in enumerate(suggestions):
                if st.button(s, key="sug_" + str(i), use_container_width=True):
                    st.session_state.pending_input = s
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="yumea-messages-area">' + _build_messages_html(messages) + '</div>',
                unsafe_allow_html=True
            )
            
            # Wisdom card buttons for each assistant message
            for idx, msg in enumerate(messages):
                if msg.get("role") == "assistant":
                    card_col1, card_col2 = st.columns([1, 8])
                    with card_col1:
                        if st.button("🎴 Card", key=f"card_btn_{idx}", 
                                     help="Generate wisdom card"):
                            st.session_state["show_card_" + str(idx)] = True
                    
                    if st.session_state.get("show_card_" + str(idx), False):
                        with st.spinner("✨ Creating your wisdom card..."):
                            card_bytes = generate_wisdom_card(
                                msg["content"], 
                                "Yumea"
                            )
                        st.image(card_bytes, width=400)
                        dl_col1, dl_col2 = st.columns([1, 1])
                        with dl_col1:
                            st.download_button(
                                "⬇️ Download",
                                data=card_bytes,
                                file_name=f"yumea_wisdom_{idx}.png",
                                mime="image/png",
                                key=f"dl_{idx}",
                                use_container_width=True
                            )
                        with dl_col2:
                            if st.button("✖️ Close", key=f"close_card_{idx}",
                                         use_container_width=True):
                                st.session_state["show_card_" + str(idx)] = False
                                st.rerun()
    
    if MIC_RECORDER_AVAILABLE:
        st.markdown('<div class="yumea-mic-wrapper">', unsafe_allow_html=True)
        mic_result = mic_recorder(
            start_prompt="🎤", stop_prompt="⏹",
            just_once=True, use_container_width=False, key="yumea_mic"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if mic_result and mic_result.get("bytes"):
            audio_hash = hashlib.md5(mic_result["bytes"]).hexdigest()
            if audio_hash != st.session_state.last_processed_audio:
                st.session_state.last_processed_audio = audio_hash
                with st.spinner("🎧 Listening..."):
                    transcribed = transcribe_audio(mic_result["bytes"])
                if transcribed:
                    with st.spinner("✨ Yumea is thinking..."):
                        process_user_message(transcribed)
                    st.rerun()


# ═══════════════════════════════════════════════════════════
# ROUTER (Simple & Bulletproof)
# ═══════════════════════════════════════════════════════════

PAGE_ROUTES = {
    "signin": page_signin,
    "signup": page_signup,
    "chat": page_chat,
    "premium": page_premium,
    "payment": page_payment,
}

PUBLIC_PAGES = ["signin", "signup"]

current_page = st.session_state.get("current_page", "signin")

if current_page not in PAGE_ROUTES:
    current_page = "signin"
    st.session_state.current_page = "signin"

is_logged_in = st.session_state.get("is_authenticated", False)

if not is_logged_in and current_page not in PUBLIC_PAGES:
    current_page = "signin"
    st.session_state.current_page = "signin"

if is_logged_in and current_page in PUBLIC_PAGES:
    current_page = "chat"
    st.session_state.current_page = "chat"

PAGE_ROUTES[current_page]()