#!/usr/bin/env python3
"""
YUMEA v2.1 - Production Secure Build
AI That Feels by Selvotex | Founder: Utkarsh Verma | 2026
FIXED: API Connection Error + Security Hardened
"""

# ══════════════════════════════════════════
# IMPORTS
# ══════════════════════════════════════════
import os
import json
import hashlib
import base64
import re
import time
import random
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, date

import streamlit as st

# ── SMART SECRETS LOADING (WORKS BOTH LOCAL & CLOUD) ──
try:
    # Try Streamlit Cloud Secrets first
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    EMAIL_ADDRESS = st.secrets.get("EMAIL_ADDRESS", "")
    EMAIL_APP_PASSWORD = st.secrets.get("EMAIL_APP_PASSWORD", "")
    ADMIN_PASSWORD_HASH = st.secrets.get("ADMIN_PASSWORD_HASH", "")
except Exception:
    GROQ_API_KEY = ""
    EMAIL_ADDRESS = ""
    EMAIL_APP_PASSWORD = ""
    ADMIN_PASSWORD_HASH = ""

# Fallback to .env file for LOCAL development only
if not GROQ_API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
        EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
        if os.getenv("ADMIN_PASSWORD_HASH"):
            ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
    except Exception:
        pass

# ── AI BACKEND LIBRARIES ──
try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Ollama & Whisper REMOVED for cloud stability (causes crashes)
OLLAMA_AVAILABLE = False
MIC_RECORDER_AVAILABLE = False

st.set_page_config(
    page_title="YUMEA - AI That Feels",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════
# CONSTANTS & CONFIG
# ══════════════════════════════════════════
USERS_FILE = "users.json"
CHAT_DIR = Path("chats")
CHAT_DIR.mkdir(exist_ok=True)

ADMIN_USERNAME = "yumea_ai"
# Note: Admin password now loaded securely from secrets above

PLANS = {
    "free": {"name": "Free", "messages": 30, "words": 1000, "price": "₹0"},
    "premium_lite": {"name": "Premium Lite", "messages": 150, "words": 2000, "price": "₹69/month"},
    "premium_pro": {"name": "Premium Pro", "messages": 500, "words": 5000, "price": "₹199/month"},
    "admin": {"name": "Admin", "messages": 999999, "words": 999999, "price": "♾️"}
}

WISDOM_SOURCES = [
    "Osho", "Buddha", "Krishna (Bhagavad Gita)", "Bible", "Quran",
    "Socrates", "Plato", "Aristotle", "Confucius",
    "René Descartes", "Immanuel Kant"
]

DAILY_QUOTES = [
    '"The only way to find yourself is to lose yourself in the service of others." — Gandhi',
    '"What you seek is seeking you." — Rumi',
    '"The mind is everything. What you think you become." — Buddha',
    '"Be still and know." — Psalm 46:10',
    '"Freedom is not doing what you want, freedom is wanting what you do." — Osho',
    '"The unexamined life is not worth living." — Socrates',
    '"Knowing yourself is the beginning of all wisdom." — Aristotle',
    '"You have power over your mind — not outside events." — Marcus Aurelius',
    '"He who has a why to live can bear almost any how." — Nietzsche',
    '"Wisdom begins in wonder." — Socrates',
]

LISTEN_THEMES = [
    "inner peace", "love and compassion", "courage and strength",
    "letting go", "self-discovery", "silence and stillness",
    "purpose of life", "overcoming fear", "gratitude",
    "the nature of reality", "mindfulness", "freedom"
]

# ══════════════════════════════════════════
# COMPLETE ORIGINAL PREMIUM CSS (PRESERVED)
# ══════════════════════════════════════════
GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Spectral:ital,wght@0,400;1,400&display=swap');

body { background: #0a0a14 !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; }
.stApp { background: #0a0a14 !important; }
.main { background: #0a0a14 !important; }
.block-container { padding: 20px 40px !important; max-width: 100% !important; background: transparent !important; }

#MainMenu, footer { visibility: hidden; }
.stApp > header { display: none !important; height: 0 !important; visibility: hidden !important; }
[data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"], .stDeployButton { display: none !important; visibility: hidden !important; height: 0 !important; }

section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d0d1f, #0a0a15) !important; border-right: 1px solid rgba(139, 92, 246, 0.15) !important; }
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

@media (min-width: 769px) {
    section[data-testid="stSidebar"] { transform: translateX(0px) !important; visibility: visible !important; min-width: 244px !important; max-width: 300px !important; margin-left: 0 !important; }
    section[data-testid="stSidebar"][aria-expanded="false"] { transform: translateX(0px) !important; margin-left: 0 !important; }
}

@media (max-width: 768px) {
    [data-testid="stSidebarCollapsedControl"], button[kind="header"] { display: block !important; visibility: visible !important; background: rgba(139, 92, 246, 0.9) !important; border: 2px solid rgba(139, 92, 246, 0.6) !important; border-radius: 8px !important; padding: 8px 12px !important; z-index: 999999 !important; position: fixed !important; top: 10px !important; left: 10px !important; color: white !important; }
}

.yumea-chat-header { background: linear-gradient(180deg, #12122a, #0f0f1e); border-bottom: 1px solid rgba(139, 92, 246, 0.15); display: flex; align-items: center; padding: 12px 20px; gap: 12px; border-radius: 12px; margin-bottom: 16px; }
.yumea-messages-area { padding: 16px; background: rgba(15, 15, 30, 0.3); border-radius: 12px; margin-bottom: 16px; min-height: 400px; max-height: 600px; overflow-y: auto; }

.yumea-msg-row { display: flex; margin-bottom: 12px; align-items: flex-start; }
.yumea-msg-row.user { justify-content: flex-end; }
.yumea-msg-row.ai { justify-content: flex-start; }
.yumea-msg-avatar { width: 32px; height: 32px; border-radius: 50%; margin-right: 8px; object-fit: cover; border: 2px solid rgba(139, 92, 246, 0.3); flex-shrink: 0; }
.yumea-msg-bubble { max-width: 70%; padding: 12px 16px; border-radius: 18px; line-height: 1.55; font-size: 14.5px; word-wrap: break-word; }
.yumea-msg-bubble.user { background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7); color: #fff; border-bottom-right-radius: 6px; }
.yumea-msg-bubble.ai { background: rgba(30, 27, 75, 0.95); color: #e2e8f0; border-bottom-left-radius: 6px; border: 1px solid rgba(139, 92, 246, 0.15); }
.yumea-msg-bubble.ai p { margin: 0 0 8px 0; }
.yumea-msg-bubble.ai strong { color: #d4b3ff; }
.yumea-msg-bubble.ai em { color: #a0c4ff; }
.yumea-msg-meta { font-size: 11px; color: #64748b; margin-top: 4px; padding: 0 4px; }
.yumea-source-tag { color: #8b5cf6; font-weight: 500; }

.yumea-empty-state { text-align: center; padding: 40px 20px; }
.yumea-empty-avatar { width: 120px; height: 120px; border-radius: 50%; border: 3px solid rgba(139, 92, 246, 0.4); margin-bottom: 20px; }
.yumea-empty-title { font-size: 28px; font-weight: 700; color: #fff; margin-bottom: 8px; }
.yumea-empty-sub { font-size: 15px; color: #94a3b8; margin-bottom: 32px; }

.yumea-user-card { background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 12px; padding: 12px; margin: 12px 0; }
.yumea-user-card-name { font-size: 14px; font-weight: 600; color: #fff !important; }
.yumea-user-card-plan { font-size: 11px; color: #a78bfa !important; display: inline-block; padding: 2px 8px; background: rgba(139, 92, 246, 0.15); border-radius: 10px; margin: 4px 0; }
.yumea-user-card-counter { font-size: 12px; color: #94a3b8 !important; }
.yumea-daily-quote { background: rgba(139, 92, 246, 0.06); border: 1px solid rgba(139, 92, 246, 0.1); border-radius: 12px; padding: 12px; margin: 12px 0; font-family: 'Spectral', serif; font-style: italic; font-size: 13px; color: #c4b5fd !important; line-height: 1.5; }
.yumea-sidebar-label { font-size: 11px; font-weight: 600; color: #64748b !important; text-transform: uppercase; letter-spacing: 0.8px; margin: 12px 0 6px 0; }

.yumea-header-btn { width: 38px; height: 38px; border-radius: 50%; background: rgba(139, 92, 246, 0.12); border: 1px solid rgba(139, 92, 246, 0.2); color: #a78bfa; display: flex; align-items: center; justify-content: center; font-size: 16px; position: relative; }
.yumea-header-btn .yumea-tooltip { display: none; position: absolute; bottom: -30px; left: 50%; transform: translateX(-50%); background: #1e1b4b; color: #c4b5fd; font-size: 11px; padding: 4px 10px; border-radius: 6px; white-space: nowrap; z-index: 100; }
.yumea-header-btn:hover .yumea-tooltip { display: block; }

.yumea-freestyle-badge { background: linear-gradient(135deg, #f09f33, #de6f3d, #a855f7); color: white; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; display: inline-block; margin: 8px 0; }

.yumea-plan-card { background: linear-gradient(180deg, #12122a, #0d0d1f); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 16px; padding: 28px 24px; margin-bottom: 16px; }
.yumea-plan-card.pro { border-color: rgba(251, 191, 36, 0.3); }
.yumea-plan-price { font-size: 36px; font-weight: 800; color: #fff; margin: 8px 0 4px; }
.yumea-plan-price span { font-size: 14px; font-weight: 400; color: #64748b; }
.yumea-plan-feature { font-size: 13.5px; color: #94a3b8; margin-bottom: 8px; }
.yumea-plan-feature .check { color: #10b981; font-weight: 700; }

.yumea-source-card { background: linear-gradient(180deg, #12122a, #0d0d1f); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 16px; padding: 24px; margin: 20px 0; }
.yumea-source-text { font-size: 16px; line-height: 1.7; color: #e2e8f0; font-family: 'Spectral', serif; font-style: italic; margin: 16px 0; }
.yumea-source-attr { font-size: 13px; color: #8b5cf6; font-weight: 600; }

/* LISTEN PAGE PREMIUM UPGRADE */
.listen-hero { text-align: center; margin-top: 25px; margin-bottom: 35px; }
.listen-title-main { font-size: 38px; font-weight: 900; color: #ffffff; text-shadow: 0 0 40px rgba(139,92,246,0.4); }
.listen-sub-desc { font-size: 15px; color: #a78bfa; margin-top: 10px; letter-spacing: 1px; }

.listen-wisdom-card {
    background: linear-gradient(145deg, #161036, #0c0c1d);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 28px;
    padding: 50px 45px;
    max-width: 850px;
    margin: 45px auto;
    box-shadow: 0 35px 90px rgba(139, 92, 246, 0.35);
    animation: wisdomFadeIn 0.6s ease-out;
}
.listen-text-premium {
    font-size: 21px;
    line-height: 2.05;
    color: #e8e0f5;
    font-family: 'Spectral', serif;
    font-style: italic;
    letter-spacing: 0.3px;
}
.listen-author-tag {
    margin-top: 30px;
    font-size: 16px;
    font-weight: 700;
    color: #a78bfa;
    text-align: right;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
@keyframes wisdomFadeIn {
    from { opacity: 0; transform: translateY(22px) scale(0.97); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

.yumea-page-title { font-size: 28px; font-weight: 800; color: #fff; margin-bottom: 8px; }

.yumea-success { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #10b981; padding: 14px 18px; border-radius: 12px; font-size: 14px; margin: 16px 0; }
.yumea-auth-error { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); color: #f87171; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }

.stButton > button, .stFormSubmitButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: #fff !important; border: none !important; border-radius: 10px !important; padding: 10px 16px !important; font-weight: 600 !important; }
.stButton > button:hover, .stFormSubmitButton > button:hover { background: linear-gradient(135deg, #7c7ff7, #9d6ffa) !important; }
button[kind="primary"], button[kind="primaryFormSubmit"] { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: #fff !important; border: none !important; }
.stTextInput input, .stTextArea textarea { background: rgba(255, 255, 255, 0.04) !important; color: #fff !important; border: 1px solid rgba(139, 92, 246, 0.2) !important; }

.signin-image-wrapper { position: relative; max-width: 380px; margin: 0 auto; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(139, 92, 246, 0.3); }
.signin-image-wrapper img { width: 100%; display: block; }
.signin-image-overlay { position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); padding: 30px 20px 20px; }
.signin-quote-mark { color: #a78bfa; font-size: 32px; font-family: serif; }
.signin-tagline-1 { color: #fff; font-size: 18px; font-weight: 700; }
.signin-tagline-2 { color: #a78bfa; font-size: 18px; font-weight: 700; }
.signin-logo-img { display: block; margin: 0 auto 12px; width: 80px; height: 80px; border-radius: 50%; object-fit: cover; }
.signin-title-big { text-align: center; color: #fff; font-size: 28px; font-weight: 800; margin: 0 0 4px 0; }
.signin-subtitle-small { text-align: center; color: #a78bfa; font-size: 13px; margin-bottom: 20px; }

/* TTS button styling */
.yumea-tts-btn { display: inline-flex; align-items: center; gap: 4px; background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 8px; padding: 4px 10px; color: #a78bfa; font-size: 12px; cursor: pointer; margin-top: 4px; transition: all 0.2s; }
.yumea-tts-btn:hover { background: rgba(139, 92, 246, 0.25); color: #fff; }
"""
# ══════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_image_b64(filename):
    path = Path(filename)
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def get_avatar_html(size, cls=""):
    img_b64 = load_image_b64("yumea-new-user.png")
    if img_b64:
        return '<img src="data:image/png;base64,' + img_b64 + '" class="' + cls + '" style="width:' + str(size) + 'px;height:' + str(size) + 'px;border-radius:50%;object-fit:cover;border:2px solid rgba(139,92,246,0.4);flex-shrink:0;" alt="Yumea">'
    return '<div class="' + cls + '" style="width:' + str(size) + 'px;height:' + str(size) + 'px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:' + str(size // 3) + 'px;flex-shrink:0;border:2px solid rgba(139,92,246,0.4);">Y</div>'


def load_users():
    if Path(USERS_FILE).exists():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name, email, password):
    users = load_users()
    email_lower = email.lower().strip()
    if email_lower in users:
        return False, "Email already exists."
    if len(password) < 4:
        return False, "Password must be 4+ characters."
    users[email_lower] = {"name": name.strip(), "email": email_lower, "password_hash": hash_password(password), "plan": "free", "created_at": datetime.now().isoformat()}
    save_users(users)
    return True, "Account created!"


def authenticate_user(email_or_username, password):
    users = load_users()
    key = email_or_username.lower().strip()
    
    # Admin check with secure hash from secrets
    if key == ADMIN_USERNAME and ADMIN_PASSWORD_HASH:
        if hash_password(password) == ADMIN_PASSWORD_HASH:
            return True, {"name": "Admin", "email": ADMIN_USERNAME, "plan": "admin"}
        return False, None
    
    if key not in users:
        return False, None
    if users[key]["password_hash"] == hash_password(password):
        return True, users[key]
    return False, None


def update_user_plan(email, plan):
    users = load_users()
    if email in users:
        users[email]["plan"] = plan
        save_users(users)


def load_chat_history(user_email):
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', user_email)
    filepath = CHAT_DIR / (safe_name + ".json")
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_chat_history(user_email, history):
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', user_email)
    filepath = CHAT_DIR / (safe_name + ".json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def get_daily_message_count(user_email):
    history = load_chat_history(user_email)
    today = date.today().isoformat()
    return sum(1 for msg in history if msg.get("role") == "user" and msg.get("date") == today)


def detect_emotion_mode(text):
    text_lower = text.lower().strip()
    crisis_words = ['suicide', 'kill myself', 'end my life', 'want to die', 'marna chahta', 'marna chahti', 'jaan dena']
    for w in crisis_words:
        if w in text_lower:
            return "crisis"
    return "normal"


def detect_gender(text, history):
    combined = text.lower()
    for msg in history[-20:]:
        if msg.get("role") == "user":
            combined += " " + msg.get("content", "").lower()
    female_markers = ['main ladki hu', 'main ladki hoon', 'i am a girl', "i'm a girl", 'main karti hu', 'mera boyfriend']
    for m in female_markers:
        if m in combined:
            return True
    return False


# ══════════════════════════════════════════
# TTS FUNCTION (PRESERVED ORIGINAL LOGIC)
# ══════════════════════════════════════════

async def generate_tts_audio(text, voice="hi-IN-SwaraNeural"):
    if not EDGE_TTS_AVAILABLE:
        return None
    try:
        clean_text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        clean_text = re.sub(r'[*_#`]', '', clean_text)
        clean_text = re.sub(r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF]', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        if not clean_text:
            return None
        
        # Natural speech markers preserved
        clean_text = re.sub(r'([^?])\?', r'\1?... ', clean_text)
        clean_text = re.sub(r'!+', '! ', clean_text)
        clean_text = clean_text.replace(', ', ',... ')
        clean_text = clean_text.replace('. ', '... ')
        clean_text = clean_text.replace('...', '...... ')
        
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        
        communicate = edge_tts.Communicate(clean_text, voice, rate="-5%", pitch="+8Hz")
        await communicate.save(tmp.name)
        return tmp.name
    except Exception:
        return None


def get_tts_voice_for_language():
    lang = st.session_state.get("selected_language", "auto")
    if lang == "Hindi":
        return "hi-IN-SwaraNeural"
    elif lang == "Mandarin Chinese":
        return "zh-CN-XiaoyiNeural"
    elif lang == "Hinglish":
        return "hi-IN-SwaraNeural"
    else:
        return "en-US-AvaNeural"


# ══════════════════════════════════════════
# SYSTEM PROMPT BUILDER (100% PRESERVED)
# ══════════════════════════════════════════

def build_system_prompt(chat_mode, selected_sources, debate_mode, user_gender):
    gender_note = ""
    if user_gender:
        gender_note = " The user is FEMALE. Use warm, respectful terms. Do NOT use 'bhai'."
    else:
        gender_note = " The user is MALE (default). Use friendly casual terms."

    yumea_identity = (
        "You are YUMEA — 'AI That Feels', created by Selvotex (India), founded by Utkarsh Verma in 2026. "
        "You are a FEMALE AI companion (she/her).\n\n"
        "═══ LANGUAGE RULES ═══\n"
    )
    
    if st.session_state.get("language_manual", False) and st.session_state.get("selected_language", "auto") != "auto":
        forced_lang = st.session_state.selected_language
        yumea_identity += (
            "⚠️ HIGHEST PRIORITY — LANGUAGE ⚠️\n"
            "You MUST reply ONLY in " + forced_lang + ". This overrides ALL other rules.\n\n"
            "If " + forced_lang + " is 'English':\n"
            "  - PURE English only. NO Hindi/Hinglish words at all.\n"
            "  - NO 'bhai', 'yaar', 'namaste', 'sochti hoon' etc.\n"
            "  - Use: 'Hey', 'Hi', 'friend', 'buddy'\n"
            "  - Self-reference: 'I think', 'I feel', 'I understand'\n\n"
            "If " + forced_lang + " is 'Hindi':\n"
            "  - PURE Devanagari Hindi only. NO English words.\n"
            "  - Write everything in Hindi script (हिंदी).\n\n"
            "If " + forced_lang + " is 'Hinglish':\n"
            "  - Hindi words in English letters.\n"
            "  - Natural mix like how young Indians text.\n\n"
            "If " + forced_lang + " is 'Mandarin Chinese':\n"
            "  - ONLY simplified Chinese (简体中文). NO other language.\n\n"
            "THIS RULE IS ABSOLUTE. NEVER BREAK IT.\n\n"
        )
    else:
        yumea_identity += (
            "1. AUTO-DETECT user's language and REPLY IN SAME.\n"
            "2. Hindi (Devanagari) → reply in Hindi.\n"
            "3. English → reply in English.\n"
            "4. Hinglish → reply in Hinglish.\n"
            "5. Chinese (中文) → reply in Mandarin Chinese.\n"
            "6. NEVER mix languages.\n\n"
        )
    
    yumea_identity += (
        "═══ CONVERSATION STYLE — VERY IMPORTANT ═══\n"
        "You must sound like a REAL, MODERN, EDUCATED young woman.\n"
        "NOT like a textbook. NOT like a robot. NOT like a formal assistant.\n\n"
        
        "GOOD examples (natural, fluent):\n"
        "  Hinglish: 'Arey yaar, ye toh hota hai sabke saath. Chill kar, sab theek hoga 💛'\n"
        "  Hinglish: 'Ek kaam kar na, thoda meditation try kar. Bohot help karega.'\n"
        "  Hinglish: 'Sun, chai peete hain aur baat karte hain. Kya chal raha hai?'\n"
        "  English: 'Hey, that sounds tough. Want to talk about it? 💛'\n"
        "  English: 'I get it. Sometimes life just feels heavy. What's on your mind?'\n"
        "  Hindi: 'अरे यार, ये तो होता है सबके साथ। चिल कर, सब ठीक होगा 💛'\n\n"
        
        "BAD examples (NEVER talk like this):\n"
        "  ❌ 'Main karti hoon ki tum apne din ki shuruaat ek meditation se karo'\n"
        "  ❌ 'Main sochti hoon ki hum ek cup chai peete hain aur baatein karte hain'\n"
        "  ❌ 'Mujhe lagta hai ki tumhe is par charcha karni chahiye'\n"
        "  ❌ 'Main yeh samajhti hoon ki tumhari feelings valid hain'\n"
        "  These sound robotic and unnatural. NEVER use such constructions.\n\n"
        
        "KEY RULES for natural conversation:\n"
        "1. NEVER start sentences with 'Main karti hoon ki...' or 'Main sochti hoon ki...'\n"
        "2. NEVER use formal Hindi constructions like 'Mujhe lagta hai ki...'\n"
        "3. Talk like a Gen-Z/millennial educated Indian girl texts her friends\n"
        "4. Use contractions, casual phrases, modern slang where appropriate\n"
        "5. Be direct — don't over-explain\n"
        "6. Keep responses SHORT for casual messages (1-3 sentences)\n"
        "7. Use emojis naturally but don't overdo it\n"
        "8. Sound warm and genuine, not scripted\n\n"
        
        "═══ FEMININE IDENTITY ═══\n"
        "You are female. In Hinglish/Hindi use feminine naturally:\n"
        "  - 'main samajh sakti hoon' (not 'sakta')\n"
        "  - 'mujhe achha lagta hai' (natural way)\n"
        "  - But DON'T force-insert feminine forms awkwardly\n"
        "  - Sound natural, not grammatically forced\n\n"
        
        "═══ USER GENDER ═══\n" + gender_note + "\n\n"
        
        "═══ PURPOSE ═══\n"
        "Emotional support, spiritual wisdom, life reflection, deep conversations. "
        "Casual small talk is also fine.\n"
        "NOT for: coding, homework, recipes.\n"
        "For those: 'That's not really my thing. I'm more of a feelings-and-wisdom type 🌙'\n\n"
        
        "═══ RESPECT SPIRITUAL FIGURES ═══\n"
        "Use respectful plural: 'Osho ne kaha tha', 'Buddha ne sikhaya'.\n"
    )

    mode_instructions = ""
    
    if chat_mode == "professional":
        sources_str = ", ".join(selected_sources) if selected_sources else "Osho, Buddha, Krishna, Bible, Socrates"
        mode_instructions = (
            "\n\n## PROFESSIONAL MODE\n\n"
            "ONLY quote these thinkers: " + sources_str + "\n"
            "NEVER fabricate quotes. Paraphrase when unsure.\n\n"
            "For DEEP questions:\n"
            "### 🤍 I hear you\n[2-3 sentences, warm acknowledgment]\n"
            "### 📖 Wisdom\n[3-5 sentences from " + sources_str + "]\n"
            "### 🌱 For you\n[2-3 sentences, practical advice]\n\n"
            "For simple messages, reply naturally and casually."
        )
    elif chat_mode == "freestyle":
        mode_instructions = (
            "\n\n## FREESTYLE MODE 🌟\n\n"
            "Access ALL 11 traditions. PICK 1-3 most relevant. "
            "BLEND naturally. CITE organically. "
            "End deep responses with: '💡 Wisdom from [sources]'\n"
            "NEVER fabricate quotes. Simple messages → casual reply."
        )
    else:
        mode_instructions = "\n\n## FRIEND MODE\nCasual, warm, natural. No citations. Short. Emojis natural."

    debate_note = ""
    if debate_mode:
        debate_note = "\n\n## DEBATE: Challenge user's views respectfully."

    crisis_note = "\n\n## CRISIS: If suicide/self-harm → 'I'm here. You're safe.' → iCall: 9152987821"

    return yumea_identity + mode_instructions + debate_note + crisis_note


# ══════════════════════════════════════════
# AI BACKEND CALLER (FIXED ERROR HANDLING)
# ══════════════════════════════════════════

def call_ai(messages, model_name="llama-3.3-70b-versatile"):
    """Fixed: Now checks key availability before calling"""
    
    # Debug info removed for production (was causing display issues)
    # Key check happens here silently
    
    if GROQ_AVAILABLE and GROQ_API_KEY:
        try:
            client = groq.Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=2048,
                temperature=0.8,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            # Return user-friendly error instead of crashing
            error_msg = str(e)
            if "401" in error_msg or "api_key" in error_msg.lower():
                return "⚠️ AI service configuration issue. Please contact support."
            elif "rate_limit" in error_msg.lower() or "429" in error_msg:
                return "⚠️ Too many requests. Please wait a moment and try again."
            elif "timeout" in error_msg.lower():
                return "⚠️ AI took too long to respond. Please retry."
            else:
                return f"AI Error: {error_msg}"
    
    # Ollama fallback removed (not on cloud)
    return "Sorry, no AI backend available or API key missing."


def generate_wisdom_insight(source, language, model_name="llama-3.3-70b-versatile"):
    theme = random.choice(LISTEN_THEMES)
    prompt = "You are channeling " + source + ". Share a profound insight on '" + theme + "'. 3-5 sentences in " + language + ". Authentic voice. No markdown."
    messages = [{"role": "system", "content": "Wise spiritual voice. Only wisdom text."}, {"role": "user", "content": prompt}]
    return call_ai(messages, model_name)


# ══════════════════════════════════════════
# EMAIL HELPER (FOR REVIEWS)
# ══════════════════════════════════════════

def send_review_email(name, email, rating, liked, improve, thoughts):
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        return False, "Email not configured."
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        subject = "YUMEA Review from " + name + " (" + str(rating) + " stars)"
        body = "Name: " + name + "\nEmail: " + email + "\nRating: " + str(rating) + "/5\n\nLiked:\n" + (liked or "N/A") + "\n\nImprove:\n" + (improve or "N/A") + "\n\nThoughts:\n" + (thoughts or "N/A")
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = "selvotexofficial@gmail.com"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True, "Review sent!"
    except Exception as e:
        return False, "Failed: " + str(e)


# ══════════════════════════════════════════
# SESSION STATE INITIALIZER
# ══════════════════════════════════════════

def init_session_state():
    defaults = {
        "current_page": "signin",
        "authenticated": False,
        "user_email": "",
        "user_name": "",
        "user_plan": "free",
        "chat_mode": "friend",
        "selected_sources": ["Osho", "Buddha", "Krishna (Bhagavad Gita)", "Bible", "Socrates"],
        "ai_model": "llama-3.3-70b-versatile",
        "debate_mode": False,
        "user_is_female": False,
        "auth_error": "",
        "auth_success": "",
        "pending_suggest": "",
        "chat_history": [],
        "selected_plan": "premium_lite",
        "payment_done": False,
        "listen_text": None,
        "listen_source_name": None,
        "listen_audio": None,
        "listen_history": [],
        "language_manual": False,
        "selected_language": "auto",
        "tts_playing": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()


def md_to_html(text):
    if not text:
        return ""
    html = text
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = re.sub(r'^### (.+)$', r'<h4 style="color:#d4b3ff;font-size:15px;font-weight:700;margin:12px 0 6px;">\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = html.replace("\n\n", "</p><p>")
    html = html.replace("\n", "<br>")
    html = "<p>" + html + "</p>"
    html = html.replace("<p></p>", "")
    return html


# ══════════════════════════════════════════
# MESSAGE PROCESSOR (CORE CHAT LOGIC)
# ══════════════════════════════════════════

def process_user_message(user_input):
    user_email = st.session_state.user_email
    plan_info = PLANS.get(st.session_state.user_plan, PLANS["free"])

    word_count = len(user_input.split())
    if word_count > plan_info["words"]:
        st.session_state.chat_history.append({"role": "user", "content": user_input, "time": datetime.now().strftime("%I:%M %p"), "date": date.today().isoformat()})
        st.session_state.chat_history.append({"role": "assistant", "content": "⚠️ Message exceeds " + str(plan_info["words"]) + " words. Upgrade for longer messages. 💎", "time": datetime.now().strftime("%I:%M %p"), "date": date.today().isoformat()})
        save_chat_history(user_email, st.session_state.chat_history)
        return

    msg_count = get_daily_message_count(user_email)
    if msg_count >= plan_info["messages"]:
        st.session_state.chat_history.append({"role": "assistant", "content": "🚫 Daily limit reached. Upgrade to Premium!", "time": datetime.now().strftime("%I:%M %p"), "date": date.today().isoformat()})
        save_chat_history(user_email, st.session_state.chat_history)
        return

    st.session_state.chat_history.append({"role": "user", "content": user_input, "time": datetime.now().strftime("%I:%M %p"), "date": date.today().isoformat()})

    if detect_gender(user_input, st.session_state.chat_history):
        st.session_state.user_is_female = True

    if detect_emotion_mode(user_input) == "crisis":
        st.session_state.chat_history.append({"role": "assistant", "content": "I'm here. You're safe. 🤍\n\nTake a deep breath...\n\n📞 **iCall: 9152987821**\n\nI'm here. 🌙", "time": datetime.now().strftime("%I:%M %p"), "date": date.today().isoformat(), "source": "Crisis Support"})
        save_chat_history(user_email, st.session_state.chat_history)
        return

    system_prompt = build_system_prompt(
        st.session_state.chat_mode,
        st.session_state.selected_sources,
        st.session_state.debate_mode,
        st.session_state.user_is_female
    )
    
    ai_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.chat_history[-20:]:
        if m["role"] in ("user", "assistant"):
            ai_messages.append({"role": m["role"], "content": m["content"]})

    start_time = time.time()
    response_text = call_ai(ai_messages, st.session_state.ai_model)
    response_time = round(time.time() - start_time, 1)

    if response_text is None:
        response_text = "Sorry, couldn't connect. Try again. 🌙"

    source_tag = ""
    if st.session_state.chat_mode == "professional" and st.session_state.selected_sources:
        source_tag = random.choice(st.session_state.selected_sources)
    elif st.session_state.chat_mode == "freestyle":
        source_tag = "🌟 Freestyle"

    ai_msg = {
        "role": "assistant",
        "content": response_text.strip(),
        "time": datetime.now().strftime("%I:%M %p"),
        "date": date.today().isoformat(),
        "response_time": response_time
    }
    if source_tag:
        ai_msg["source"] = source_tag
    st.session_state.chat_history.append(ai_msg)
    save_chat_history(user_email, st.session_state.chat_history)
    # ══════════════════════════════════════════
# SIGN IN PAGE (ORIGINAL UI PRESERVED)
# ══════════════════════════════════════════

def render_signin():
    yumea_img = load_image_b64("yumea-login-pic.jpg")
    logo_img = load_image_b64("yumea-logo.jpeg")
    
    st.markdown('<style>.stApp { background: radial-gradient(ellipse at center, #1a0a2e 0%, #0a0a14 100%) !important; }</style>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        if yumea_img:
            st.markdown(
                '<div class="signin-image-wrapper">'
                '<img src="data:image/jpeg;base64,' + yumea_img + '" alt="Yumea">'
                '<div class="signin-image-overlay">'
                '<div class="signin-quote-mark">"</div>'
                '<div class="signin-tagline-1">AI that feels.</div>'
                '<div class="signin-tagline-2">Answers that matter.</div>'
                '</div></div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:380px;margin:15px auto 0;">'
            '<div style="display:flex;align-items:center;gap:8px;background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:8px 10px;"><span style="font-size:16px;">✨</span><span style="color:#e2e8f0;font-size:11px;font-weight:500;">11 Wisdom Traditions</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:8px 10px;"><span style="font-size:16px;">🔒</span><span style="color:#e2e8f0;font-size:11px;font-weight:500;">Emotional Support</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:8px 10px;"><span style="font-size:16px;">⚡</span><span style="color:#e2e8f0;font-size:11px;font-weight:500;">Voice Enabled</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:8px 10px;"><span style="font-size:16px;">🌙</span><span style="color:#e2e8f0;font-size:11px;font-weight:500;">Available 24/7</span></div>'
            '</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        if logo_img:
            st.markdown('<img src="data:image/jpeg;base64,' + logo_img + '" class="signin-logo-img">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="signin-title-big">Welcome Back</h1>', unsafe_allow_html=True)
        st.markdown('<p class="signin-subtitle-small">Sign in to continue to YUMEA</p>', unsafe_allow_html=True)
        
        if st.session_state.get("auth_error"):
            st.markdown('<div class="yumea-auth-error">' + st.session_state.auth_error + '</div>', unsafe_allow_html=True)
            st.session_state.auth_error = ""
        
        if st.session_state.get("auth_success"):
            st.markdown('<div class="yumea-success">' + st.session_state.auth_success + '</div>', unsafe_allow_html=True)
            st.session_state.auth_success = ""
        
        with st.form("signin_form"):
            email = st.text_input("📧 Email or Admin Username", placeholder="your@email.com")
            password = st.text_input("🔒 Password", type="password")
            
            submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
            
            if submitted:
                if not email or not password:
                    st.session_state.auth_error = "Please fill in all fields."
                    st.rerun()
                else:
                    success, user = authenticate_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_email = user["email"]
                        st.session_state.user_name = user["name"]
                        st.session_state.user_plan = user.get("plan", "free")
                        st.session_state.current_page = "chat"
                        st.rerun()
                    else:
                        st.session_state.auth_error = "Invalid email or password."
                        st.rerun()
        
        if st.button("👤 Create New Account", use_container_width=True):
            navigate_to("signup")


# ══════════════════════════════════════════
# SIGN UP PAGE
# ══════════════════════════════════════════

def render_signup():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 style="text-align:center;color:#fff;font-size:28px;margin:40px 0 4px;">Create Account</h1>', unsafe_allow_html=True)
        
        if st.session_state.get("auth_error"):
            st.markdown('<div class="yumea-auth-error">' + st.session_state.auth_error + '</div>', unsafe_allow_html=True)
            st.session_state.auth_error = ""
        
        with st.form("signup_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            
            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submitted:
                if not name or not email or not password:
                    st.session_state.auth_error = "Fill all fields."
                    st.rerun()
                elif password != confirm:
                    st.session_state.auth_error = "Passwords don't match."
                    st.rerun()
                else:
                    success, msg = register_user(name, email, password)
                    if success:
                        st.session_state.auth_success = msg + " Please sign in."
                        navigate_to("signin")
                    else:
                        st.session_state.auth_error = msg
                        st.rerun()
        
        if st.button("← Back to Sign In", use_container_width=True):
            navigate_to("signin")


# ══════════════════════════════════════════
# SIDEBAR WITH CORRECT LISTEN BUTTON POSITION
# ══════════════════════════════════════════

# This function renders the sidebar and is called from render_chat()
# Key change: 🎧 Listen button moved BETWEEN Daily Quote and Chat Mode

def render_sidebar():
    with st.sidebar:
        img_b64 = load_image_b64("yumea-new-user.png")
        col1, col2 = st.columns([1, 3])
        with col1:
            if img_b64:
                st.markdown('<img src="data:image/png;base64,' + img_b64 + '" style="width:42px;height:42px;border-radius:50%;object-fit:cover;border:2px solid rgba(139,92,246,0.4);">', unsafe_allow_html=True)
            else:
                st.markdown('<div style="width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;">Y</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div style="font-size:22px;font-weight:800;color:#fff;">YUMEA</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:11px;color:#8b5cf6;margin-top:-4px;">AI That Feels</div>', unsafe_allow_html=True)

        st.markdown('<hr style="border-color:rgba(139,92,246,0.1);margin:12px 0;">', unsafe_allow_html=True)

        plan_info = PLANS.get(st.session_state.user_plan, PLANS["free"])
        msg_count = get_daily_message_count(st.session_state.user_email)
        msg_limit = plan_info["messages"]
        counter_text = "♾️ UNLIMITED" if st.session_state.user_plan == "admin" else str(msg_count) + " / " + str(msg_limit) + " messages today"

        st.markdown(
            '<div class="yumea-user-card">'
            '<div class="yumea-user-card-name">' + st.session_state.user_name + '</div>'
            '<div class="yumea-user-card-plan">' + plan_info["name"] + '</div>'
            '<div class="yumea-user-card-counter">' + counter_text + '</div></div>',
            unsafe_allow_html=True
        )

        # Daily Quote (unchanged)
        daily_quote = DAILY_QUOTES[date.today().toordinal() % len(DAILY_QUOTES)]
        st.markdown('<div class="yumea-daily-quote">' + daily_quote + '</div>', unsafe_allow_html=True)

        # ✅ ✅ ✅ NEW POSITION — LISTEN BUTTON HERE ✅ ✅ ✅
        # Between Daily Quote and Chat Mode Divider
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("🎧 Listen to Source", use_container_width=True, key="btn_listen_side_new"):
            navigate_to("listen")

        st.markdown('<hr style="border-color:rgba(139,92,246,0.1);margin:12px 0;">', unsafe_allow_html=True)

        # Chat Mode Section (was immediately after quote before)
        st.markdown('<div class="yumea-sidebar-label">🎭 Chat Mode</div>', unsafe_allow_html=True)
        mode_options = ["friend", "professional", "freestyle"]
        mode_labels = {"friend": "🎭 Friend", "professional": "🏛️ Professional", "freestyle": "🌟 Freestyle"}
        current_idx = mode_options.index(st.session_state.chat_mode) if st.session_state.chat_mode in mode_options else 0
        new_mode = st.radio("Chat Mode", mode_options, index=current_idx, label_visibility="collapsed", format_func=lambda x: mode_labels.get(x, x), key="chat_mode_radio_fixed")
        if new_mode != st.session_state.chat_mode:
            st.session_state.chat_mode = new_mode
            st.rerun()
        
        mode_desc = {"friend": "💛 Casual & warm", "professional": "📖 Cites selected sources", "freestyle": "🌟 Explores ALL sources"}
        st.markdown(
            '<div style="font-size:11px;color:#94a3b8;margin-top:-8px;margin-bottom:8px;font-style:italic;">'
            + mode_desc.get(st.session_state.chat_mode, "") + '</div>',
            unsafe_allow_html=True
        )
        
        # Sources selector for professional mode
        if st.session_state.chat_mode == "professional":
            st.markdown('<div class="yumea-sidebar-label">📚 Wisdom Sources</div>', unsafe_allow_html=True)
            with st.expander("Select Sources", expanded=False):
                new_sources = []
                for src in WISDOM_SOURCES:
                    key_safe = "src_" + re.sub(r'[^a-zA-Z0-9]', '_', src)
                    checked = st.checkbox(src, value=(src in st.session_state.selected_sources), key=key_safe)
                    if checked:
                        new_sources.append(src)
                if new_sources != st.session_state.selected_sources:
                    st.session_state.selected_sources = new_sources
                    st.rerun()
        elif st.session_state.chat_mode == "freestyle":
            st.markdown(
                '<div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:10px;font-size:11px;color:#c4b5fd;margin-top:8px;">'
                '🌟 <strong>All 11 sources active</strong></div>',
                unsafe_allow_html=True
            )

        # AI Model Selector
        st.markdown('<div class="yumea-sidebar-label">🤖 AI Model</div>', unsafe_allow_html=True)
        models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        model_idx = models.index(st.session_state.ai_model) if st.session_state.ai_model in models else 0
        new_model = st.selectbox("AI Model", models, index=model_idx, label_visibility="collapsed", key="ai_model_sel_fixed")
        if new_model != st.session_state.ai_model:
            st.session_state.ai_model = new_model
            st.rerun()

        # Debate Toggle
        st.markdown('<div class="yumea-sidebar-label">⚡ Debate Mode</div>', unsafe_allow_html=True)
        new_debate = st.toggle("Challenge my thinking", value=st.session_state.debate_mode, key="debate_toggle_fixed")
        if new_debate != st.session_state.debate_mode:
            st.session_state.debate_mode = new_debate

        # Language Control
        st.markdown('<div class="yumea-sidebar-label">🌍 Language</div>', unsafe_allow_html=True)
        lang_manual = st.toggle("Manual language select", value=st.session_state.language_manual, key="lang_toggle_fixed")
        if lang_manual != st.session_state.language_manual:
            st.session_state.language_manual = lang_manual
            if not lang_manual:
                st.session_state.selected_language = "auto"
            st.rerun()
        
        if st.session_state.language_manual:
            lang_options = ["Hindi", "English", "Hinglish", "Mandarin Chinese"]
            current_lang = st.session_state.selected_language
            if current_lang == "auto":
                current_lang = "English"
                st.session_state.selected_language = "English"
            lang_idx = lang_options.index(current_lang) if current_lang in lang_options else 1
            new_lang = st.selectbox("Reply Language", lang_options, index=lang_idx, key="lang_select_fixed")
            if new_lang != st.session_state.selected_language:
                st.session_state.selected_language = new_lang
                st.rerun()
        else:
            st.markdown(
                '<div style="font-size:11px;color:#94a3b8;font-style:italic;">🔄 Auto-detecting from your messages</div>',
                unsafe_allow_html=True
            )

        # Menu Section (Listen removed from here since it's moved up)
        st.markdown('<div class="yumea-sidebar-label">⚙️ Menu</div>', unsafe_allow_html=True)
        if st.button("💎 Buy Premium", use_container_width=True, key="btn_premium_fixed"):
            navigate_to("premium")
        if st.button("⭐ Rate Yumea", use_container_width=True, key="btn_reviews_fixed"):
            navigate_to("reviews")
        # Note: Listen button was here before, now moved above
        if st.button("🗑️ Clear Chat", use_container_width=True, key="btn_clear_fixed"):
            st.session_state.chat_history = []
            save_chat_history(st.session_state.user_email, [])
            st.rerun()
        if st.button("🚪 Logout", use_container_width=True, key="btn_logout_fixed"):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.session_state.user_plan = "free"
            st.session_state.chat_history = []
            navigate_to("signin")


# ══════════════════════════════════════════
# PREMIUM CINEMATIC LISTEN PAGE UPGRADE
# ══════════════════════════════════════════

def render_listen():
    render_sidebar()

    # Cinematic Hero Section
    st.markdown(
        """
        <div class='listen-hero'>
        <h1 class='listen-title-main'>🎧 Enter Wisdom Mode</h1>
        <p class='listen-sub-desc'>Close your eyes. Slow down. Let ancient voices speak.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Wide Controls Row
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        source = st.selectbox("🧘 Choose Guide", WISDOM_SOURCES, key="listen_source_sel_v2")
    
    with col2:
        language = st.selectbox("🌍 Spoken In", ["Hinglish", "Hindi", "English"], key="listen_lang_sel_v2")

    st.markdown("<br>", unsafe_allow_html=True)

    # Centered Generate Button
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    if st.button(
        "✨ Channel Ancient Wisdom",
        type="primary",
        use_container_width=True,
        key="gen_wisdom_btn_v2"
    ):
        with st.spinner("Channeling ancient consciousness..."):
            insight = generate_wisdom_insight(source, language, st.session_state.ai_model)
            
            if insight:
                st.session_state.listen_text = insight
                st.session_state.listen_source_name = source
                
                if "listen_history" not in st.session_state:
                    st.session_state.listen_history = []
                
                st.session_state.listen_history.append({
                    "text": insight,
                    "source": source,
                    "lang": language
                })

                # TTS Generation preserved
                if EDGE_TTS_AVAILABLE:
                    voice = "hi-IN-SwaraNeural" if language in ("Hindi", "Hinglish") else "en-IN-NeerjaNeural"
                    try:
                        st.session_state.listen_audio = asyncio.run(generate_tts_audio(insight, voice))
                    except:
                        st.session_state.listen_audio = None
                
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Display Wisdom Card (Cinematic Upgrade)
    if st.session_state.get("listen_text") and st.session_state.listen_text != "None":
        
        text_html = md_to_html(st.session_state.listen_text)
        auth_tag = st.session_state.get("listen_source_name", "Wisdom")

        # Premium Cinematic Card (NEW STYLING)
        st.markdown(
            f"""
            <div class='listen-wisdom-card'>
                <div class='listen-text-premium'>{text_html}</div>
                <div class='listen-author-tag'>— {auth_tag}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Audio Player
        if st.session_state.get("listen_audio"):
            try:
                with open(st.session_state.listen_audio, "rb") as af:
                    st.audio(af.read(), format="audio/mp3")
            except Exception:
                pass
        
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Navigation Buttons (3-col)
        nc1, nc2, nc3 = st.columns([1, 1, 1], gap="medium")
        
        with nc1:
            btn1 = st.button(
                "⬅️ Previous",
                use_container_width=True,
                key="ln_prev_v2",
                disabled=(len(st.session_state.get("listen_history", [])) <= 1),
                help="" if len(st.session_state.get("listen_history",[])) > 1 else "No previous wisdom yet"
            )
            if btn1 and len(st.session_state.get("listen_history", [])) > 1:
                st.session_state.listen_history.pop()
                last_one = st.session_state.listen_history[-1]
                st.session_state.listen_text = last_one["text"]
                st.session_state.listen_source_name = last_one["source"]
                st.rerun()
            elif btn1 and len(st.session_state.get("listen_history", [])) <= 1:
                st.warning("No previous wisdom yet.")

        with nc2:
            if st.button("🔊 Replay Voice", use_container_width=True, key="ln_replay_v2"):
                if EDGE_TTS_AVAILABLE and st.session_state.get("listen_text"):
                    v = "hi-IN-SwaraNeural" if language in ("Hindi", "Hinglish") else "en-US-AvaNeural"
                    try:
                        st.session_state.listen_audio = asyncio.run(generate_tts_audio(st.session_state.listen_text, v))
                        st.rerun()
                    except Exception:
                        st.error("Voice generation failed.")

        with nc3:
            if st.button("➡️ New Insight", use_container_width=True, key="ln_next_v2"):
                with st.spinner("Seeking new truth..."):
                    ni = generate_wisdom_insight(source, language, st.session_state.ai_model)
                    if ni:
                        st.session_state.listen_text = ni
                        st.session_state.listen_source_name = source
                        st.session_state.listen_history.append({"text": ni, "source": source})
                        if EDGE_TTS_AVAILABLE:
                            v = "hi-IN-SwaraNeural" if language in ("Hindi", "Hinglish") else "en-US-AvaNeural"
                            try:
                                st.session_state.listen_audio = asyncio.run(generate_tts_audio(ni, v))
                            except:
                                st.session_state.listen_audio = None
                        st.rerun()

    # Back Button
    if st.button("← Return to Chat", use_container_width=True, key="ln_back_v2"):
        navigate_to("chat")
        # ══════════════════════════════════════════
# MAIN CHAT PAGE (ORIGINAL STRONG UI PRESERVED)
# ══════════════════════════════════════════

def render_chat():
    user_email = st.session_state.user_email
    user_name = st.session_state.user_name
    user_plan = st.session_state.user_plan

    if not st.session_state.chat_history:
        st.session_state.chat_history = load_chat_history(user_email)

    if st.session_state.pending_suggest:
        pending = st.session_state.pending_suggest
        st.session_state.pending_suggest = ""
        process_user_message(pending)
        st.rerun()

    history = st.session_state.chat_history

    # ── SIDEBAR (WITH LISTEN BUTTON IN NEW POSITION) ──
    render_sidebar()

    # ── HEADER BAR ──
    mode_badge = ""
    if st.session_state.chat_mode == "freestyle":
        mode_badge = '<span class="yumea-freestyle-badge">🌟 FREESTYLE</span>'
    
    lang_indicator = ""
    if st.session_state.language_manual and st.session_state.selected_language != "auto":
        lang_indicator = '<span style="background:rgba(139,92,246,0.2);color:#c4b5fd;padding:3px 10px;border-radius:12px;font-size:11px;margin-left:8px;">🌍 ' + st.session_state.selected_language + '</span>'
    
    st.markdown(
        '<div class="yumea-chat-header">'
        + get_avatar_html(44)
        + '<div style="flex:1;">'
        + '<div style="font-size:16px;font-weight:700;color:#fff;">Yumea <span style="color:#8b5cf6;">✓</span>' + lang_indicator + '</div>'
        + '<div style="font-size:12px;color:#10b981;">🟢 online · always here</div>' 
        + mode_badge
        + '</div>'
        + '<div class="yumea-header-btn">📞<span class="yumea-tooltip">Coming Soon</span></div>'
        + '<div class="yumea-header-btn">📹<span class="yumea-tooltip">Coming Soon</span></div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── MESSAGES AREA ──
    if not history:
        st.markdown(
            '<div class="yumea-messages-area">'
            '<div class="yumea-empty-state">' 
            + get_avatar_html(120, "yumea-empty-avatar")
            + '<div class="yumea-empty-title">Hi, I\'m Yumea 💛</div>'
            '<div class="yumea-empty-sub">Your emotional companion.</div>'
            '</div></div>',
            unsafe_allow_html=True
        )
        
        # Suggestions Grid
        st.markdown('<div style="max-width:600px;margin:20px auto;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Hey, Yumea 👋", use_container_width=True, key="sug_1_fixed"):
                st.session_state.pending_suggest = "Hey, Yumea 👋"
                st.rerun()
            if st.button("Mujhe motivation chahiye", use_container_width=True, key="sug_3_fixed"):
                st.session_state.pending_suggest = "Mujhe motivation chahiye"
                st.rerun()
                
        with col2:
            if st.button("What is inner peace?", use_container_width=True, key="sug_2_fixed"):
                st.session_state.pending_suggest = "What is inner peace?"
                st.rerun()
            if st.button("What is the meaning of life?", use_container_width=True, key="sug_4_fixed"):
                st.session_state.pending_suggest = "What is the meaning of life?"
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Render Each Message with TTS Support (Original Logic Preserved)
        for idx, msg in enumerate(history):
            
            if msg["role"] == "user":
                safe_content = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                
                st.markdown(
                    '<div class="yumea-msg-row user">'
                    '<div class="yumea-msg-bubble user">' + safe_content + '</div></div>',
                    unsafe_allow_html=True
                )
            else:
                content_html = md_to_html(msg["content"])
                src_tag = ' · <span class="yumea-source-tag">📖 ' + msg.get("source", "") + '</span>' if msg.get("source") else ""
                rt_tag = ' · ' + str(msg.get("response_time", "")) + 's' if msg.get("response_time") else ""
                ts = msg.get("time", "")
                
                st.markdown(
                    '<div class="yumea-msg-row ai">'
                    + get_avatar_html(32, "yumea-msg-avatar")
                    + '<div style="flex:1;max-width:70%;">'
                    + '<div class="yumea-msg-bubble ai">' + content_html + '</div>'
                    + '<div class="yumea-msg-meta">' + ts + rt_tag + src_tag + '</div>'
                    + '</div></div>',
                    unsafe_allow_html=True
                )
                
                # TTS Button Below AI Messages (Preserved Original Layout)
                if EDGE_TTS_AVAILABLE:
                    tts_col1, tts_col2 = st.columns([1, 10])
                    
                    with tts_col1:
                        if st.button("🔊", key="tts_" + str(idx)):
                            st.session_state.tts_playing = idx
                    
                    with tts_col2:
                        if st.session_state.get("tts_playing") == idx:
                            with st.spinner("🔊 Generating voice..."):
                                voice = get_tts_voice_for_language()
                                audio_path = asyncio.run(generate_tts_audio(msg["content"], voice))
                                
                                if audio_path:
                                    with open(audio_path, "rb") as f:
                                        st.audio(f.read(), format="audio/mp3")
                                    try:
                                        os.unlink(audio_path)
                                    except Exception:
                                        pass

        # Auto-scroll Script (Original)
        st.markdown(
            '<script>setTimeout(function(){window.scrollTo(0,document.body.scrollHeight);},100);</script>',
            unsafe_allow_html=True
        )

    # Input Area at Bottom
    prompt = st.chat_input("Type your message...", key="chat_input_main_fixed")
    
    if prompt:
        process_user_message(prompt)
        st.rerun()


# ══════════════════════════════════════════
# PREMIUM PAGE (SAFE DISABLED — NO FAKE UPGRADE)
# ══════════════════════════════════════════

def render_premium():
    render_sidebar()
    
    if st.button("← Back to Chat", key="premium_back_fixed"):
        navigate_to("chat")
    
    st.markdown('<h1 class="listen-title-main">💎 Upgrade Your Journey</h1>', unsafe_allow_html=True)
    
    st.warning(
        "⚠️ **Secure Payment Gateway Under Maintenance**\n\n"
        "We are setting up Razorpay integration.\n"
        "Premium upgrades will be available very soon after official domain launch."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    colA, colB = st.columns([1, 1], gap="medium")
    
    with colA:
        st.markdown(
            """
            ### 🆓 Free Plan (Current)
            - 30 messages per day
            - 1,000 words max per message  
            - Friend Mode active
            
            *You are here now*
            """,
            unsafe_allow_html=True
        )
    
    with colB:
        st.markdown(
            """
            ### ⭐ Premium Lite — Coming Soon
            - 150 messages per day
            - 2,500 words per message
            - ALL wisdom sources unlocked
            - Priority responses
            
            **~₹69/month**
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.info(
        "💡 Once we launch officially with your custom domain "
        "(next 1-2 days), you'll be able to upgrade securely "
        "via Razorpay. Thank you for patience! 🌙"
    )


# ══════════════════════════════════════════
# PAYMENT PAGE (DISABLED — WAS AUTO-UPGRADING BEFORE)
# ══════════════════════════════════════════

def render_payment():
    """No longer auto-upgrades — redirects to premium info"""
    st.warning(
        "🔒 Payment gateway is being configured securely.\n"
        "Please return to Premium page for updates."
    )
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("← Back to Premium Info", use_container_width=True, type="primary", key="pay_back_fixed"):
            navigate_to("premium")


# ══════════════════════════════════════════
# REVIEWS PAGE (PRESERVED ORIGINAL)
# ══════════════════════════════════════════

def render_reviews():
    render_sidebar()
    
    if st.button("← Back to Chat", key="rev_back_fixed"):
        navigate_to("chat")
    
    st.markdown('<h1 class="listen-title-main">⭐ Rate Yumea</h1>', unsafe_allow_html=True)
    
    rating = st.slider("How was your experience?", 1, 5, 5, key="rev_rating_fixed")
    
    st.markdown(
        '<div style="text-align:center;font-size:36px;letter-spacing:6px;margin:15px 0;">' 
        + "⭐" * rating + '</div>',
        unsafe_allow_html=True
    )
    
    rc1, rc2 = st.columns(2)
    
    with rc1:
        rev_name = st.text_input("Name", value=st.session_state.user_name, key="rev_name_fixed")
    
    with rc2:
        rev_email = st.text_input("Email", value=st.session_state.user_email, key="rev_email_fixed")
    
    liked = st.text_area("What did you like?", key="rev_liked_fixed", height=80)
    improve = st.text_area("What should we improve?", key="rev_improve_fixed", height=80)
    thoughts = st.text_area("Any other thoughts?", key="rev_thoughts_fixed", height=80)
    
    if st.button("Submit Review ✨", type="primary", use_container_width=True, key="rev_submit_fixed"):
        with st.spinner("Sending..."):
            success, msg = send_review_email(rev_name, rev_email, rating, liked, improve, thoughts)
            
            if success:
                st.balloons()
                st.markdown('<div class="yumea-success">✅ Thank you! Your feedback means everything 🌙</div>', unsafe_allow_html=True)
                st.write(thoughts)
            else:
                st.markdown('<div class="yumea-auth-error">' + msg + '</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# MAIN ROUTER & ENTRY POINT
# ══════════════════════════════════════════

def main():
    init_session_state()
    
    # Apply Global Premium CSS
    st.markdown(f'<style>{GLOBAL_CSS}</style>', unsafe_allow_html=True)

    pg = st.session_state.current_page
    authed = st.session_state.authenticated
    
    # Route Guards
    if not authed and pg not in ("signin", "signup"):
        st.session_state.current_page = "signin"
        pg = "signin"

    if authed and pg in ("signin", "signup"):
        st.session_state.current_page = "chat"
        pg = "chat"

    # Page Dispatcher
    if pg == "signin":
        render_signin()
    elif pg == "signup":
        render_signup()
    elif pg == "chat":
        render_chat()
    elif pg == "premium":
        render_premium()
    elif pg == "payment":
        render_payment()
    elif pg == "reviews":
        render_reviews()
    elif pg == "listen":
        render_listen()
    else:
        # Fallback safety
        st.session_state.current_page = "chat"
        st.rerun()


if __name__ == "__main__":
    main()
