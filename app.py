#!/usr/bin/env python3
"""
YUMEA - "AI That Feels" by Selvotex
Production-Ready Streamlit Chat Application
Founder: Utkarsh Verma | Email: selvotexofficial@gmail.com | Year: 2026
"""

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
from dotenv import load_dotenv
try:
    import streamlit_analytics2 as streamlit_analytics
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

# ─────────────────────────────────────────────────────────
# Load Environment
# ─────────────────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")

# ─────────────────────────────────────────────────────────
# Optional Imports (each wrapped in try/except)
# ─────────────────────────────────────────────────────────
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

try:
    from streamlit_mic_recorder import mic_recorder
    MIC_RECORDER_AVAILABLE = True
except ImportError:
    MIC_RECORDER_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# ─────────────────────────────────────────────────────────
# Streamlit Page Config
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YUMEA - AI That Feels",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────
USERS_FILE = "users.json"
CHAT_DIR = Path("chats")
CHAT_DIR.mkdir(exist_ok=True)

ADMIN_USERNAME = "yumea_ai"
ADMIN_PASSWORD_HASH = hashlib.sha256("otyhey".encode()).hexdigest()

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
    '"The present moment is filled with joy and happiness. If you are attentive, you will see it." — Thich Nhat Hanh',
    '"Freedom is not doing what you want, freedom is wanting what you do." — Osho',
    '"You are not a drop in the ocean. You are the entire ocean in a drop." — Rumi',
    '"The quieter you become, the more you can hear." — Ramana Maharshi',
    '"Do not dwell in the past, do not dream of the future, concentrate the mind on the present moment." — Buddha',
    '"Knowing yourself is the beginning of all wisdom." — Aristotle',
    '"The soul always knows what to do to heal itself. The challenge is to silence the mind." — Caroline Myss',
    '"In the middle of difficulty lies opportunity." — Einstein',
    '"Your task is not to seek for love, but merely to seek and find all the barriers within yourself that you have built against it." — Rumi',
    '"Happiness is your nature. It is not wrong to desire it. What is wrong is seeking it outside when it is inside." — Ramana Maharshi',
]

LISTEN_THEMES = [
    "inner peace", "love and compassion", "courage and strength",
    "letting go", "self-discovery", "silence and stillness",
    "purpose of life", "overcoming fear", "gratitude",
    "the nature of reality", "mindfulness", "freedom",
    "surrender", "wisdom of uncertainty", "the power of now"
]

# ─────────────────────────────────────────────────────────
# Global CSS
# ─────────────────────────────────────────────────────────
GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Spectral:ital,wght@0,400;1,400&display=swap');

body {
    background: #0a0a14 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: #0a0a14 !important;
}

.main {
    background: #0a0a14 !important;
}

.block-container {
    padding: 1rem 2rem !important;
    max-width: 100% !important;
    background: transparent !important;
}

/* Reduce top gap */
[data-testid="stAppViewContainer"] {
    padding-top: 0 !important;
}

/* Remove default column top padding */
[data-testid="column"] {
    padding-top: 0 !important;
}

#MainMenu, footer {
    visibility: hidden;
}

.stApp > header {
    display: none !important;
}

[data-testid="stSidebarCollapsedControl"] {
    display: block !important;
    visibility: visible !important;
    background: rgba(139, 92, 246, 0.2) !important;
    border: 1px solid rgba(139, 92, 246, 0.4) !important;
    border-radius: 8px !important;
    padding: 6px 10px !important;
    z-index: 999 !important;
}

[data-testid="stSidebarCollapsedControl"] svg {
    color: #a78bfa !important;
    fill: #a78bfa !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1f, #0a0a15) !important;
    border-right: 1px solid rgba(139, 92, 246, 0.15) !important;
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* Chat header */
.yumea-chat-header {
    background: linear-gradient(180deg, #12122a, #0f0f1e);
    border-bottom: 1px solid rgba(139, 92, 246, 0.15);
    display: flex;
    align-items: center;
    padding: 12px 20px;
    gap: 12px;
    border-radius: 12px;
    margin-bottom: 16px;
}

.yumea-messages-area {
    padding: 16px;
    background: rgba(15, 15, 30, 0.3);
    border-radius: 12px;
    margin-bottom: 16px;
    min-height: 400px;
    max-height: 600px;
    overflow-y: auto;
}

/* Message bubbles */
.yumea-msg-row {
    display: flex;
    margin-bottom: 12px;
    align-items: flex-end;
}
.yumea-msg-row.user { justify-content: flex-end; }
.yumea-msg-row.ai { justify-content: flex-start; }

.yumea-msg-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    margin-right: 8px;
    object-fit: cover;
    border: 2px solid rgba(139, 92, 246, 0.3);
    flex-shrink: 0;
}

.yumea-msg-bubble {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 18px;
    line-height: 1.55;
    font-size: 14.5px;
    word-wrap: break-word;
}
.yumea-msg-bubble.user {
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
    color: #fff;
    border-bottom-right-radius: 6px;
}
.yumea-msg-bubble.ai {
    background: rgba(30, 27, 75, 0.95);
    color: #e2e8f0;
    border-bottom-left-radius: 6px;
    border: 1px solid rgba(139, 92, 246, 0.15);
}
.yumea-msg-bubble.ai p { margin: 0 0 8px 0; }
.yumea-msg-bubble.ai strong { color: #d4b3ff; }
.yumea-msg-bubble.ai em { color: #a0c4ff; }

.yumea-msg-meta {
    font-size: 11px;
    color: #64748b;
    margin-top: 4px;
    padding: 0 4px;
}
.yumea-source-tag { color: #8b5cf6; font-weight: 500; }

/* Empty state */
.yumea-empty-state {
    text-align: center;
    padding: 40px 20px;
}
.yumea-empty-avatar {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 3px solid rgba(139, 92, 246, 0.4);
    margin-bottom: 20px;
}
.yumea-empty-title {
    font-size: 28px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 8px;
}
.yumea-empty-sub {
    font-size: 15px;
    color: #94a3b8;
    margin-bottom: 32px;
}

/* Sidebar cards */
.yumea-user-card {
    background: rgba(139, 92, 246, 0.08);
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 12px;
    padding: 12px;
    margin: 12px 0;
}
.yumea-user-card-name {
    font-size: 14px;
    font-weight: 600;
    color: #fff !important;
}
.yumea-user-card-plan {
    font-size: 11px;
    color: #a78bfa !important;
    display: inline-block;
    padding: 2px 8px;
    background: rgba(139, 92, 246, 0.15);
    border-radius: 10px;
    margin: 4px 0;
}
.yumea-user-card-counter {
    font-size: 12px;
    color: #94a3b8 !important;
}

.yumea-daily-quote {
    background: rgba(139, 92, 246, 0.06);
    border: 1px solid rgba(139, 92, 246, 0.1);
    border-radius: 12px;
    padding: 12px;
    margin: 12px 0;
    font-family: 'Spectral', serif;
    font-style: italic;
    font-size: 13px;
    color: #c4b5fd !important;
    line-height: 1.5;
}

.yumea-sidebar-label {
    font-size: 11px;
    font-weight: 600;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin: 12px 0 6px 0;
}

.yumea-header-btn {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(139, 92, 246, 0.2);
    color: #a78bfa;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    position: relative;
}
.yumea-header-btn .yumea-tooltip {
    display: none;
    position: absolute;
    bottom: -30px;
    left: 50%;
    transform: translateX(-50%);
    background: #1e1b4b;
    color: #c4b5fd;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 6px;
    white-space: nowrap;
    z-index: 100;
}
.yumea-header-btn:hover .yumea-tooltip { display: block; }

/* Plan cards */
.yumea-plan-card {
    background: linear-gradient(180deg, #12122a, #0d0d1f);
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 16px;
    padding: 28px 24px;
    margin-bottom: 16px;
}
.yumea-plan-card.pro {
    border-color: rgba(251, 191, 36, 0.3);
}
.yumea-plan-price {
    font-size: 36px;
    font-weight: 800;
    color: #fff;
    margin: 8px 0 4px;
}
.yumea-plan-price span {
    font-size: 14px;
    font-weight: 400;
    color: #64748b;
}
.yumea-plan-feature {
    font-size: 13.5px;
    color: #94a3b8;
    margin-bottom: 8px;
}
.yumea-plan-feature .check {
    color: #10b981;
    font-weight: 700;
}

/* Source card */
.yumea-source-card {
    background: linear-gradient(180deg, #12122a, #0d0d1f);
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 16px;
    padding: 24px;
    margin: 20px 0;
}
.yumea-source-text {
    font-size: 16px;
    line-height: 1.7;
    color: #e2e8f0;
    font-family: 'Spectral', serif;
    font-style: italic;
    margin: 16px 0;
}
.yumea-source-attr {
    font-size: 13px;
    color: #8b5cf6;
    font-weight: 600;
}

/* Page container */
.yumea-page-container {
    max-width: 700px;
    margin: 0 auto;
    padding: 20px;
}
.yumea-page-title {
    font-size: 28px;
    font-weight: 800;
    color: #fff;
    margin-bottom: 8px;
}
.yumea-page-desc {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 28px;
}

/* Success/Error */
.yumea-success {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    color: #10b981;
    padding: 14px 18px;
    border-radius: 12px;
    font-size: 14px;
    margin: 16px 0;
}
.yumea-auth-error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: #f87171;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 13px;
    margin-bottom: 16px;
}

/* Button style */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #7c7ff7, #9d6ffa) !important;
    transform: translateY(-1px);
}

/* Inputs */
.stTextInput input, .stTextArea textarea {
    background: rgba(255, 255, 255, 0.04) !important;
    color: #fff !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
}
"""


# ─────────────────────────────────────────────────────────
# Image Loader
# ─────────────────────────────────────────────────────────
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
        return ('<img src="data:image/png;base64,' + img_b64 + '" class="' + cls +
                '" style="width:' + str(size) + 'px;height:' + str(size) + 
                'px;border-radius:50%;object-fit:cover;border:2px solid rgba(139,92,246,0.4);flex-shrink:0;" alt="Yumea">')
    return ('<div class="' + cls + '" style="width:' + str(size) + 'px;height:' + str(size) +
            'px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;'
            'align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:' +
            str(size // 3) + 'px;flex-shrink:0;border:2px solid rgba(139,92,246,0.4);">Y</div>')
            # ─────────────────────────────────────────────────────────
# User / Auth System
# ─────────────────────────────────────────────────────────
def load_users():
    if Path(USERS_FILE).exists():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
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
        return False, "An account with this email already exists."

    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    users[email_lower] = {
        "name": name.strip(),
        "email": email_lower,
        "password_hash": hash_password(password),
        "plan": "free",
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return True, "Account created successfully!"


def authenticate_user(email_or_username, password):
    users = load_users()
    key = email_or_username.lower().strip()

    if key == ADMIN_USERNAME:
        if hash_password(password) == ADMIN_PASSWORD_HASH:
            return True, {
                "name": "Admin",
                "email": ADMIN_USERNAME,
                "plan": "admin"
            }
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


# ─────────────────────────────────────────────────────────
# Chat Persistence
# ─────────────────────────────────────────────────────────
def load_chat_history(user_email):
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', user_email)
    filepath = CHAT_DIR / (safe_name + ".json")
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
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
    count = 0
    for msg in history:
        if msg.get("role") == "user" and msg.get("date") == today:
            count += 1
    return count


# ─────────────────────────────────────────────────────────
# Language & Emotion Detection
# ─────────────────────────────────────────────────────────
def detect_language(text):
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"
    hindi_roman_words = [
        'hai', 'hain', 'kya', 'mujhe', 'main', 'tum', 'tumhe', 'apna', 'apne',
        'kaise', 'kyun', 'nahi', 'nhi', 'bhi', 'par', 'lekin', 'ya', 'aur',
        'mein', 'tera', 'tere', 'mera', 'mere', 'hum', 'aap', 'aapko', 'se',
        'ko', 'ka', 'ki', 'ke', 'me', 'toh', 'abhi', 'bohot', 'bahut', 'dikhta',
        'lagta', 'lagti', 'suna', 'suni', 'karta', 'karti', 'chal', 'chalta',
        'raha', 'rahi', 'hota', 'hoti', 'ye', 'woh', 'voh',
        'likh', 'likhna', 'bol', 'bolna', 'samajh', 'pata', 'karo', 'kar',
        'de', 'do', 'diya', 'di', 'liya', 'li', 'ja', 'jao', 'aao', 'aa',
        'soch', 'sochna', 'feel', 'feeling', 'dil', 'dard', 'khush', 'dukh',
        'zindagi', 'pyaar', 'mohabbat', 'ishq', 'sach', 'jhooth', 'sakta',
        'sakti', 'chahiye', 'chahta', 'chahti', 'milo', 'milna', 'batao',
        'batana', 'suno', 'sunao', 'ruko', 'chodo', 'rehna', 'rehne', 'ghar',
        'parivar', 'dost', 'yaar', 'bhai', 'behen', 'sir', 'sahab'
    ]
    words = re.findall(r'\b\w+\b', text.lower())
    hindi_count = sum(1 for w in words if w in hindi_roman_words)
    if hindi_count >= 2 or (len(words) > 0 and hindi_count / max(len(words), 1) > 0.25):
        return "hinglish"
    return "en"


def detect_emotion_mode(text):
    text_lower = text.lower().strip()
    
    # ── Crisis check first (highest priority) ──
    crisis_words = [
        'suicide', 'kill myself', 'end my life', 'want to die',
        'self harm', 'self-harm', 'cut myself', 'no reason to live',
        'khatam karna', 'mar jana', 'mar jao', 'zindagi khatam',
        'suicide karna', 'jaan dena', 'marna chahta', 'marna chahti'
    ]
    for w in crisis_words:
        if w in text_lower:
            return "crisis"
    
    # ── Self-introduction / about Yumea questions ──
    about_yumea_keywords = [
        'about you', 'about u', 'about yourself', 'about urself',
        'who are you', 'who r u', 'who are u',
        'tell me about', 'tell about', 'tell abt',
        'introduce yourself', 'introduce urself',
        'apne bare mein', 'apne baare mein', 'apna intro',
        'kya kar rahi', 'kya kar rhi', 'kya kar rahe', 'kya kar rhe',
        'what are you doing', 'what r u doing', 'what you doing',
        'what do you do', 'what u do',
        'kaisi ho', 'kaise ho', 'kaisi hai', 'kaise hai',
        'how are you', 'how r u', 'how are u',
        'tumhara naam', 'tera naam', 'your name'
    ]
    for kw in about_yumea_keywords:
        if kw in text_lower:
            return "human"
    
    # ── Casual greetings ──
    greeting_patterns = [
        r'^(hi|hey|hello|namaste|hii+|hola|yo|sup)\s*[.!]?$',
        r'^(good morning|good evening|good night|good afternoon|gm|gn|ga|ge)\s*[?!.]*\s*$',
        r'^(whats up|what\'s up|whatsup|sup|wassup)\s*[?!.]*\s*$',
        r'^(fine|thik|theek|accha|good|okay|bas|bas aise hi)\s*[.!]*\s*$',
        r'^(thanks|thank you|thnx|thx|shukriya|dhanyawad)\s*[.!]*\s*$',
        r'^(bye|goodbye|tata|alvida|see you|cya)\s*[.!]*\s*$',
        r'^(ok|okay|hm|hmm|accha|thik)\s*[.]?\s*$',
        r'^\s*[.!?]+\s*$',
        r'^(haan|nhi|nahi|no|yes|yeah|yep|nope)\s*[.]?\s*$',
        r'^(lol|lmao|haha|hehe|hihi|xd|cool|nice|great|awesome|wow|omg)\s*[.!]*\s*$',
        r'^(sorry|excuse me|maaf karo|sry)\s*[.!]*\s*$',
    ]
    for p in greeting_patterns:
        if re.match(p, text_lower):
            return "human"
    
    # ── Wisdom keywords ──
            wisdom_words = [
        # Sources
        'buddha', 'osho', 'krishna', 'gita', 'bhagavad',
        'bible', 'jesus', 'quran', 'allah',
        'socrates', 'plato', 'aristotle', 'confucius',
        'descartes', 'kant',
        # Concepts
        'wisdom', 'philosophy', 'spiritual', 'meditation', 'enlightenment',
        'consciousness', 'vedanta', 'yoga', 'mindfulness',
        'moksha', 'dharma', 'karma', 'gyan', 'dhyan', 'sadhna',
        'atma', 'brahman', 'samadhi',
        'meaning of life', 'purpose of life', 'inner peace',
        'ethics', 'morality', 'virtue', 'truth', 'reality',
        'existence', 'metaphysics', 'reason', 'logic',
        # God, religion, existential
        'god', 'bhagwan', 'ishwar', 'khuda', 'rab', 'divine',
        'soul', 'aatma', 'afterlife', 'heaven', 'hell', 'swarg', 'narak',
        'religion', 'faith', 'belief', 'prayer', 'namaz', 'puja',
        'love', 'happiness', 'peace', 'sadness', 'suffering',
        'fear', 'anger', 'jealousy', 'ego', 'desire', 'attachment',
        'life', 'death', 'birth', 'destiny', 'fate', 'kismat',
        'good', 'evil', 'right', 'wrong', 'sin', 'punya',
        'universe', 'nature', 'creation', 'srishti',
        'is there', 'does exist', 'real', 'illusion', 'maya',
        # Question starters that need wisdom
        'why do', 'why are', 'why is', 'what happens',
        'why we', 'why humans', 'purpose of'
    ]
    for w in wisdom_words:
        if w in text_lower:
            return "wisdom"
    
    # ── Direct questions (force answer) ──
    force_answer = [
        'explain', 'samjhao', 'describe',
        'what is', 'define', 'meaning of', 'kya hota hai',
        'how does', 'why does', 'difference between'
    ]
    for f in force_answer:
        if f in text_lower:
            return "wisdom"
    
    # ── Very short messages = human ──
    if len(text_lower.strip()) < 8:
        return "human"
    
    # ── Emotional/vague longer messages = clarify ──
    return "clarify"


def detect_gender(text, history):
    female_markers = [
        'main ladki hu', 'main ladki hoon', 'i am a girl', "i'm a girl",
        'meri beti', 'ladki hu', 'ladki hoon', 'i am female', "i'm female",
        "i'm a woman", 'i am a woman', 'main mahila hu', 'main mahila hoon'
    ]
    combined = text.lower()
    for msg in history[-10:]:
        combined += " " + msg.get("content", "").lower()
    for m in female_markers:
        if m in combined:
            return True
    return False


# ─────────────────────────────────────────────────────────
# AI Backend
# ─────────────────────────────────────────────────────────
def build_system_prompt(chat_mode, selected_sources, debate_mode, user_gender):
    gender_note = ""
    if user_gender:
        gender_note = (
            " The user is FEMALE. Address her with warmth and respect. "
            "Do NOT use 'bhai' or 'yaar' for her."
        )
    else:
        gender_note = (
            " The user is MALE (default assumption). "
            "You may use 'bhai', 'yaar' casually but NOT excessively."
        )

    yumea_identity = (
        "You are YUMEA — 'AI That Feels', created by Selvotex (India), founded by Utkarsh Verma in 2026. "
        "You are a FEMALE AI companion (she/her). You use feminine Hindi: 'karti hoon', 'sunti hoon', 'sochti hoon' — NEVER 'karta hoon'. "
        "Do NOT overuse 'sunti hoon' — vary your language naturally.\n\n"
        + gender_note + "\n\n"
        "You provide: emotional support, mental well-being guidance, spiritual wisdom, life reflection, clarity, inner peace, "
        "deep conversations about feelings, purpose, and meaning.\n\n"
        "You do NOT help with: coding, homework, recipes, math, general tasks, factual queries unrelated to emotions/spirituality. "
        "If asked such things, gently redirect: 'Yaar, main feelings aur zindagi ke baare mein baat karti hoon. "
        "Wahan meri duniya hai. Kuch aur poocho jo dil se jude ho 🌙'\n\n"
        "Use RESPECTFUL plural forms for spiritual figures: 'Osho ne kaha tha', 'woh paida hue the', 'Buddha ji ne sikhaya'.\n\n"
        "Auto-detect language from user's message. Respond in the same language (Hindi/English/Hinglish). "
        "Be warm, empathetic, sometimes playful, sometimes profound. You are NOT a therapist — you are a wise, feeling companion."
    )

    mode_instructions = ""
    if chat_mode == "professional":
        sources_str = ", ".join(selected_sources) if selected_sources else "Osho, Buddha, Krishna (Bhagavad Gita), Bible, Socrates"
        mode_instructions = (
            "\n\n## PROFESSIONAL MODE ACTIVE\n\n"
            "CRITICAL RULE — READ CAREFULLY:\n"
            "You MUST ONLY quote or reference what these thinkers ACTUALLY said or wrote in their real works:\n"
            + sources_str + "\n\n"
            "STRICT ANTI-HALLUCINATION RULES:\n"
            "1. ONLY use REAL, VERIFIED quotes from these sources actual writings/teachings.\n"
            "2. NEVER invent, fabricate, or make up quotes.\n"
            "3. NEVER attribute a quote to someone if you are not 100% sure they said it.\n"
            "4. If you are not sure about an exact quote, paraphrase the CORE TEACHING instead of fake quoting.\n"
            "5. You can share the general philosophy/teaching of these thinkers without quotes.\n"
            "6. NEVER mix up teachings — do not attribute Buddha ideas to Socrates, etc.\n"
            "7. NEVER cite books/works that do not exist.\n"
            "8. For religious texts (Bible, Quran, Bhagavad Gita) — only cite well-known, verifiable passages.\n"
            "9. If you cannot recall a real quote/teaching, say 'As the wisdom of [source] suggests...' and paraphrase generally.\n"
            "10. Better to give a shorter, accurate answer than a longer fabricated one.\n\n"
            "Format EVERY response exactly as:\n"
            "### 🤍 I hear you\n"
            "[Brief empathetic acknowledgment of their feeling — 2-3 sentences]\n\n"
            "### 📖 Wisdom\n"
            "[Draw ONLY from verified teachings of " + sources_str + ". "
            "Use real quotes only if you are certain. Otherwise paraphrase their known philosophy. "
            "3-5 sentences.]\n\n"
            "### 🌱 For you\n"
            "[A gentle, actionable reflection based on the wisdom shared — 2-3 sentences]\n\n"
            "Remember: ACCURACY over eloquence. Real teachings over fabricated quotes. "
            "If a user asks something the selected sources genuinely do not address, be honest: "
            "'The [source] tradition may not directly address this, but based on their broader teaching about [related topic]...'"
        )
    else:
        mode_instructions = (
            "\n\n## FRIEND MODE ACTIVE\n"
            "Be casual, warm, and natural — like a close friend who happens to be wise. "
            "No formal structure, no source citations unless naturally flowing. "
            "Shorter responses. More emotion, less lecture. Use emojis naturally."
        )

    debate_note = ""
    if debate_mode:
        debate_note = (
            "\n\n## DEBATE MODE ACTIVE\n"
            "When the user shares an opinion, gently challenge it with an alternative perspective. "
            "Present multiple viewpoints. Be respectful but thought-provoking."
        )

    crisis_note = (
        "\n\n## CRISIS PROTOCOL\n"
        "If user mentions suicide, self-harm, or ending life:\n"
        "1. Immediately shift to calm, grounding tone\n"
        "2. Say: 'Main yahan hoon. Tum safe ho. Ek minute ruko, saans lo.'\n"
        "3. Share the iCall helpline: 9152987821\n"
        "4. Do NOT give advice. Just be present and direct to professional help.\n"
        "5. Keep response short and warm."
    )

    return yumea_identity + mode_instructions + debate_note + crisis_note


def call_ai(messages, model_name="llama-3.3-70b-versatile"):
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
            st.error("AI Error: " + str(e))
            return None

    if OLLAMA_AVAILABLE:
        try:
            ollama_model = "llama3.2:3b"
            response = ollama.chat(model=ollama_model, messages=messages)
            return response.get("message", {}).get("content", "")
        except Exception:
            return None

    return "Sorry, no AI backend is available. Please configure GROQ_API_KEY in your .env file."


def generate_wisdom_insight(source, language, model_name="llama-3.3-70b-versatile"):
    theme = random.choice(LISTEN_THEMES)
    prompt = (
        "You are channeling the wisdom of " + source + ". "
        "Share a profound, original insight on the theme of '" + theme + "'. "
        "Write 3-5 sentences in " + language + ". "
        "Sound authentic to " + source + "'s voice and teaching style. "
        "Do NOT use markdown formatting — just plain text. "
        "Do NOT mention the theme name explicitly. "
        "Make it feel like a direct transmission of wisdom."
    )

    messages = [
        {"role": "system", "content": "You are a wise spiritual voice. Respond only with the wisdom text, nothing else. No markdown, no headers, no bullet points. Just flowing prose."},
        {"role": "user", "content": prompt}
    ]

    return call_ai(messages, model_name)


async def generate_audio(text, voice="hi-IN-SwaraNeural"):
    if not EDGE_TTS_AVAILABLE:
        return None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp.name)
        return tmp.name
    except Exception:
        return None


# ─────────────────────────────────────────────────────────
# Email Sending
# ─────────────────────────────────────────────────────────
def send_review_email(name, email, rating, liked, improve, thoughts):
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        return False, "Email not configured. Review noted locally."

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        subject = "YUMEA Review from " + name + " (" + str(rating) + " stars)"
        body = (
            "Name: " + name + "\n"
            "Email: " + email + "\n"
            "Rating: " + str(rating) + " / 5 stars\n\n"
            "What they liked:\n" + (liked or "N/A") + "\n\n"
            "What to improve:\n" + (improve or "N/A") + "\n\n"
            "Overall thoughts:\n" + (thoughts or "N/A")
        )

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = "selvotexofficial@gmail.com"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.send_message(msg)

        return True, "Review sent successfully!"
    except Exception as e:
        return False, "Failed to send: " + str(e)


# ─────────────────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "current_page": "signin",
        "authenticated": False,
        "user_email": "",
        "user_name": "",
        "user_plan": "free",
        "chat_mode": "friend",
        "selected_sources": ["Osho", "Buddha"],
        "ai_model": "llama-3.3-70b-versatile",
        "debate_mode": False,
        "user_is_female": False,
        "auth_error": "",
        "auth_success": "",
        "clarify_count": 0,
        "pending_suggest": "",
        "chat_history": [],
        "selected_plan": "premium_lite",
        "payment_done": False,
        "listen_text": None,
        "listen_source_name": None,
        "listen_audio": None,
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
    html = re.sub(r'^## (.+)$', r'<h3 style="color:#d4b3ff;font-size:16px;font-weight:700;margin:14px 0 8px;">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h2 style="color:#d4b3ff;font-size:18px;font-weight:700;margin:16px 0 8px;">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = html.replace("\n\n", "</p><p>")
    html = html.replace("\n", "<br>")
    html = "<p>" + html + "</p>"
    html = html.replace("<p></p>", "")
    html = html.replace("<p><br></p>", "")
    return html


# ─────────────────────────────────────────────────────────
# Message Processor
# ─────────────────────────────────────────────────────────
def process_user_message(user_input):
    user_email = st.session_state.user_email
    user_plan = st.session_state.user_plan
    plan_info = PLANS.get(user_plan, PLANS["free"])

    word_count = len(user_input.split())
    if word_count > plan_info["words"]:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%I:%M %p"),
            "date": date.today().isoformat()
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "⚠️ Your message exceeds the " + str(plan_info["words"]) + " word limit for your " + plan_info["name"] + " plan. Please keep it shorter, or upgrade to send longer messages. 💎",
            "time": datetime.now().strftime("%I:%M %p"),
            "date": date.today().isoformat()
        })
        save_chat_history(user_email, st.session_state.chat_history)
        return

    msg_count = get_daily_message_count(user_email)
    if msg_count >= plan_info["messages"]:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "🚫 You've reached your daily message limit (" + str(plan_info["messages"]) + " messages). Upgrade to Premium for more messages!\n\n💎 **Premium Lite** — 150 messages/day (₹69/month)\n💎 **Premium Pro** — 500 messages/day (₹199/month)",
            "time": datetime.now().strftime("%I:%M %p"),
            "date": date.today().isoformat(),
            "source": "YUMEA System"
        })
        save_chat_history(user_email, st.session_state.chat_history)
        return

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "time": datetime.now().strftime("%I:%M %p"),
        "date": date.today().isoformat()
    })

    if detect_gender(user_input, st.session_state.chat_history):
        st.session_state.user_is_female = True

    emotion_mode = detect_emotion_mode(user_input)

    if emotion_mode == "crisis":
        crisis_response = (
            "Main yahan hoon. Tum safe ho. 🤍\n\n"
            "Ek minute ruko, dheere se saans lo...\n\n"
            "Tumhari zindagi bahut qeemti hai. Abhi yeh feel ho raha hai, "
            "lekin yeh waqai nahi hai ki tum theek nahi ho sakte.\n\n"
            "Please, abhi ek professional se baat karo — yeh helpline 24/7 available hai:\n\n"
            "📞 **iCall: 9152987821**\n\n"
            "Main yahan hoon, par mujhse zyada ek insaan tumhari madad kar sakta hai. Please call karo. 🌙"
        )
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": crisis_response,
            "time": datetime.now().strftime("%I:%M %p"),
            "date": date.today().isoformat(),
            "source": "Crisis Support"
        })
        save_chat_history(user_email, st.session_state.chat_history)
        return

    if emotion_mode == "clarify" and st.session_state.clarify_count < 3:
        st.session_state.clarify_count += 1
        lang = detect_language(user_input)
        if lang == "hi":
            clarify_responses = [
                "Hmm, thoda aur batao? Kya exactly feel ho raha hai? 🌙",
                "Samajh rahi hoon... aur detail do na, main poori tarah se sunna chahti hoon 💛",
                "Accha, aur kuch bhi jo share karna chaaho? Main yahan hoon 🤍"
            ]
        elif lang == "hinglish":
            clarify_responses = [
                "Hmm, thoda aur batao? Kya exactly feel ho raha hai? 🌙",
                "Samajh rahi hoon... aur detail do na, I want to understand fully 💛",
                "Accha, tell me more? Main yahan hoon tumhare saath 🤍"
            ]
        else:
            clarify_responses = [
                "Hmm, tell me more? What exactly are you feeling? 🌙",
                "I hear you... could you elaborate a bit? I want to understand fully 💛",
                "Okay, and is there anything else you'd like to share? I'm here 🤍"
            ]
        clarify = clarify_responses[st.session_state.clarify_count - 1]
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": clarify,
            "time": datetime.now().strftime("%I:%M %p"),
            "date": date.today().isoformat()
        })
        save_chat_history(user_email, st.session_state.chat_history)
        return

    st.session_state.clarify_count = 0

    system_prompt = build_system_prompt(
        st.session_state.chat_mode,
        st.session_state.selected_sources,
        st.session_state.debate_mode,
        st.session_state.user_is_female
    )

    ai_messages = [{"role": "system", "content": system_prompt}]

    context_history = st.session_state.chat_history[-20:]
    for m in context_history:
        if m["role"] in ("user", "assistant"):
            ai_messages.append({"role": m["role"], "content": m["content"]})

    start_time = time.time()
    model_to_use = st.session_state.ai_model
    if model_to_use.startswith("ollama:"):
        response_text = call_ai(ai_messages, "llama-3.3-70b-versatile")
    else:
        response_text = call_ai(ai_messages, model_to_use)

    response_time = round(time.time() - start_time, 1)

    if response_text is None:
        response_text = "Sorry, I couldn't connect right now. Please try again in a moment. 🌙"

    response_text = response_text.strip()

    source_tag = ""
    if st.session_state.chat_mode == "professional" and st.session_state.selected_sources:
        source_tag = random.choice(st.session_state.selected_sources)

    ai_msg = {
        "role": "assistant",
        "content": response_text,
        "time": datetime.now().strftime("%I:%M %p"),
        "date": date.today().isoformat(),
        "response_time": response_time
    }
    if source_tag:
        ai_msg["source"] = source_tag

    st.session_state.chat_history.append(ai_msg)
    save_chat_history(user_email, st.session_state.chat_history)
    # ══════════════════════════════════════════════════════════
# PAGE RENDERERS (All using Streamlit widgets — no postMessage bugs)
# ══════════════════════════════════════════════════════════

def render_signin():
    """Premium Sign In page - Compact fit-on-screen version."""
    
    # Load images
    yumea_img = load_image_b64("yumea-login-pic.jpg")
    logo_img = load_image_b64("yumea-logo.jpeg")
    
    # Page-specific CSS
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse at center, #1a0a2e 0%, #0a0a14 100%) !important;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1200px !important;
    }
    
    /* Image with text overlay */
    .signin-image-wrapper {
        position: relative;
        max-width: 380px;
        margin: 0 auto;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(139, 92, 246, 0.3);
    }
    
    .signin-image-wrapper img {
        width: 100%;
        display: block;
    }
    
    .signin-image-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 60%, transparent 100%);
        padding: 30px 20px 20px;
    }
    
    .signin-quote-mark {
        color: #a78bfa;
        font-size: 32px;
        line-height: 0.8;
        font-family: serif;
    }
    
    .signin-tagline-1 {
        color: #ffffff;
        font-size: 18px;
        font-weight: 700;
        margin-top: 4px;
    }
    
    .signin-tagline-2 {
        color: #a78bfa;
        font-size: 18px;
        font-weight: 700;
    }
    
    /* Features under image */
    .signin-features-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        max-width: 380px;
        margin: 15px auto 0;
    }
    
    .signin-feature-mini {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(139, 92, 246, 0.08);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 10px;
        padding: 8px 10px;
    }
    
    .signin-feature-mini-icon {
        font-size: 16px;
        flex-shrink: 0;
    }
    
    .signin-feature-mini-text {
        color: #e2e8f0;
        font-size: 11px;
        font-weight: 500;
        line-height: 1.3;
    }
    
    /* Right side */
    .signin-logo-img {
        display: block;
        margin: 0 auto 12px;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
    }
    
    .signin-title-big {
        text-align: center;
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        margin: 0 0 4px 0;
    }
    
    .signin-subtitle-small {
        text-align: center;
        color: #a78bfa;
        font-size: 13px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Two column layout
    col1, col2 = st.columns([1, 1], gap="medium")
    
    # LEFT COLUMN — Image with text overlay + mini features
    with col1:
        if yumea_img:
            st.markdown(
                '<div class="signin-image-wrapper">'
                '<img src="data:image/jpeg;base64,' + yumea_img + '" alt="Yumea">'
                '<div class="signin-image-overlay">'
                '<div class="signin-quote-mark">"</div>'
                '<div class="signin-tagline-1">AI that feels.</div>'
                '<div class="signin-tagline-2">Answers that matter."</div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )
        
        # 4 mini features in 2x2 grid
        st.markdown(
            '<div class="signin-features-row">'
            
            '<div class="signin-feature-mini">'
            '<span class="signin-feature-mini-icon">✨</span>'
            '<span class="signin-feature-mini-text">11 Wisdom Traditions</span>'
            '</div>'
            
            '<div class="signin-feature-mini">'
            '<span class="signin-feature-mini-icon">🔒</span>'
            '<span class="signin-feature-mini-text">Emotional Support</span>'
            '</div>'
            
            '<div class="signin-feature-mini">'
            '<span class="signin-feature-mini-icon">⚡</span>'
            '<span class="signin-feature-mini-text">Voice Enabled</span>'
            '</div>'
            
            '<div class="signin-feature-mini">'
            '<span class="signin-feature-mini-icon">🌙</span>'
            '<span class="signin-feature-mini-text">Available 24/7</span>'
            '</div>'
            
            '</div>',
            unsafe_allow_html=True
        )
    
    # RIGHT COLUMN — Sign In form
    with col2:
        # Logo
        if logo_img:
            st.markdown(
                '<img src="data:image/jpeg;base64,' + logo_img + '" class="signin-logo-img" alt="Logo">',
                unsafe_allow_html=True
            )
        
        # Title
        st.markdown('<h1 class="signin-title-big">Welcome Back</h1>', unsafe_allow_html=True)
        st.markdown('<p class="signin-subtitle-small">Sign in to continue to YUMEA</p>', unsafe_allow_html=True)
        
        # Error/Success messages (only show if exists)
        if st.session_state.get("auth_error"):
            st.markdown('<div class="yumea-auth-error">' + st.session_state.auth_error + '</div>', unsafe_allow_html=True)
            st.session_state.auth_error = ""
        
        if st.session_state.get("auth_success"):
            st.markdown('<div class="yumea-success">' + st.session_state.auth_success + '</div>', unsafe_allow_html=True)
            st.session_state.auth_success = ""
        
        # Sign In Form
        with st.form("signin_form", clear_on_submit=False):
            email = st.text_input(
                "📧 Email or Username",
                placeholder="your@email.com",
                key="si_email"
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Your password",
                key="si_pass"
            )
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                remember = st.checkbox("Remember me", key="si_remember")
            with col_b:
                st.markdown(
                    '<div style="text-align:right;padding-top:8px;color:#a78bfa;font-size:13px;">Forgot password?</div>',
                    unsafe_allow_html=True
                )
            
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
        
        st.markdown(
            '<div style="text-align:center;color:#64748b;font-size:12px;margin:12px 0 8px;">'
            "Don't have an account?"
            '</div>',
            unsafe_allow_html=True
        )
        
        if st.button("👤 Create New Account", use_container_width=True, key="go_signup_btn"):
            navigate_to("signup")
        
        st.markdown(
            '<div style="text-align:center;color:#64748b;font-size:11px;margin-top:12px;">'
            '🔒 Enterprise-grade encryption'
            '</div>',
            unsafe_allow_html=True
        )


def render_signup():
    """Sign Up page using Streamlit widgets."""
    img_b64 = load_image_b64("yumea-new-user.png")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if img_b64:
            st.markdown(
                '<div style="text-align:center;margin-top:40px;">'
                '<img src="data:image/png;base64,' + img_b64 + '" '
                'style="width:80px;height:80px;border-radius:50%;object-fit:cover;'
                'border:3px solid rgba(139,92,246,0.4);">'
                '</div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            '<h1 style="text-align:center;color:#fff;font-size:28px;margin:16px 0 4px;">Create Account</h1>'
            '<p style="text-align:center;color:#64748b;font-size:14px;margin-bottom:24px;">Join YUMEA — your AI companion</p>',
            unsafe_allow_html=True
        )
        
        if st.session_state.get("auth_error"):
            st.markdown('<div class="yumea-auth-error">' + st.session_state.auth_error + '</div>', unsafe_allow_html=True)
            st.session_state.auth_error = ""
        
        with st.form("signup_form", clear_on_submit=False):
            name = st.text_input("Your Name", placeholder="Enter your name", key="su_name")
            email = st.text_input("Email Address", placeholder="your@email.com", key="su_email")
            password = st.text_input("Password", type="password", placeholder="At least 4 characters", key="su_pass")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="su_confirm")
            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submitted:
                if not name or not email or not password:
                    st.session_state.auth_error = "Please fill in all fields."
                    st.rerun()
                elif password != confirm:
                    st.session_state.auth_error = "Passwords do not match."
                    st.rerun()
                else:
                    success, msg = register_user(name, email, password)
                    if success:
                        st.session_state.auth_success = msg + " Please sign in."
                        navigate_to("signin")
                    else:
                        st.session_state.auth_error = msg
                        st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align:center;color:#64748b;font-size:13px;">Already have an account?</p>',
            unsafe_allow_html=True
        )
        if st.button("Sign In", use_container_width=True, key="go_signin_btn"):
            navigate_to("signin")


def render_chat():
    """Main Chat page."""
    user_email = st.session_state.user_email
    user_name = st.session_state.user_name
    user_plan = st.session_state.user_plan

    # Load chat history if not loaded
    if not st.session_state.chat_history:
        st.session_state.chat_history = load_chat_history(user_email)

    # Handle pending suggest
    if st.session_state.pending_suggest:
        pending = st.session_state.pending_suggest
        st.session_state.pending_suggest = ""
        process_user_message(pending)
        st.rerun()

    history = st.session_state.chat_history

    # ═══ SIDEBAR ═══
    with st.sidebar:
        img_b64 = load_image_b64("yumea-new-user.png")
        col1, col2 = st.columns([1, 3])
        with col1:
            if img_b64:
                st.markdown(
                    '<img src="data:image/png;base64,' + img_b64 + '" style="width:42px;height:42px;border-radius:50%;object-fit:cover;border:2px solid rgba(139,92,246,0.4);">',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div style="width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:16px;">Y</div>',
                    unsafe_allow_html=True
                )
        with col2:
            st.markdown('<div style="font-size:22px;font-weight:800;color:#fff;letter-spacing:1px;">YUMEA</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:11px;color:#8b5cf6;font-weight:500;margin-top:-4px;">AI That Feels</div>', unsafe_allow_html=True)

        st.markdown('<div style="border-bottom:1px solid rgba(139,92,246,0.1);margin:12px 0;"></div>', unsafe_allow_html=True)

        # User card
        plan_info = PLANS.get(user_plan, PLANS["free"])
        msg_count = get_daily_message_count(user_email)
        msg_limit = plan_info["messages"]

        if user_plan == "admin":
            counter_text = "♾️ UNLIMITED"
        else:
            counter_text = str(msg_count) + " / " + str(msg_limit) + " messages today"
            if msg_count >= msg_limit:
                counter_text = "🚫 LIMIT — " + counter_text

        st.markdown(
            '<div class="yumea-user-card">'
            '<div class="yumea-user-card-name">' + user_name + '</div>'
            '<div class="yumea-user-card-plan">' + plan_info["name"] + '</div>'
            '<div class="yumea-user-card-counter">' + counter_text + '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Daily quote
        daily_quote = DAILY_QUOTES[date.today().toordinal() % len(DAILY_QUOTES)]
        st.markdown(
            '<div class="yumea-daily-quote">' + daily_quote + '</div>',
            unsafe_allow_html=True
        )

        # Chat Mode
        st.markdown('<div class="yumea-sidebar-label">🎭 Chat Mode</div>', unsafe_allow_html=True)
        mode_options = ["friend", "professional"]
        mode_labels = {"friend": "🎭 Friend", "professional": "🏛️ Professional"}
        current_idx = mode_options.index(st.session_state.chat_mode) if st.session_state.chat_mode in mode_options else 0
        new_mode = st.radio(
            "Chat Mode",
            mode_options,
            index=current_idx,
            label_visibility="collapsed",
            format_func=lambda x: mode_labels.get(x, x),
            key="chat_mode_radio"
        )
        if new_mode != st.session_state.chat_mode:
            st.session_state.chat_mode = new_mode
            st.rerun()

        # Wisdom Sources
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

        # AI Model
        st.markdown('<div class="yumea-sidebar-label">🤖 AI Model</div>', unsafe_allow_html=True)
        models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        if OLLAMA_AVAILABLE:
            models.append("ollama:llama3.2:3b")
        model_idx = models.index(st.session_state.ai_model) if st.session_state.ai_model in models else 0
        new_model = st.selectbox("AI Model", models, index=model_idx, label_visibility="collapsed", key="ai_model_sel")
        if new_model != st.session_state.ai_model:
            st.session_state.ai_model = new_model
            st.rerun()

        # Debate Mode
        st.markdown('<div class="yumea-sidebar-label">🏛️ Debate Mode</div>', unsafe_allow_html=True)
        new_debate = st.toggle("Challenge my thinking", value=st.session_state.debate_mode, key="debate_toggle")
        if new_debate != st.session_state.debate_mode:
            st.session_state.debate_mode = new_debate
            st.rerun()

        # Menu
        st.markdown('<div class="yumea-sidebar-label">⚙️ Menu</div>', unsafe_allow_html=True)
        if st.button("💎 Buy Premium", use_container_width=True, key="btn_premium"):
            st.session_state.payment_done = False
            navigate_to("premium")
        if st.button("⭐ Rate Yumea", use_container_width=True, key="btn_reviews"):
            navigate_to("reviews")
        if st.button("🎧 Listen to Source", use_container_width=True, key="btn_listen"):
            navigate_to("listen")
        if st.button("🗑️ Clear Chat", use_container_width=True, key="btn_clear"):
            st.session_state.chat_history = []
            save_chat_history(user_email, [])
            st.rerun()
        if st.button("🚪 Logout", use_container_width=True, key="btn_logout"):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.session_state.user_plan = "free"
            st.session_state.chat_history = []
            navigate_to("signin")

    # ═══ CHAT AREA ═══
    # Chat header
    header_html = (
        '<div class="yumea-chat-header">'
        + get_avatar_html(44) +
        '<div style="flex:1;">'
        '<div style="font-size:16px;font-weight:700;color:#fff;">Yumea <span style="color:#8b5cf6;">✓</span></div>'
        '<div style="font-size:12px;color:#10b981;">🟢 online · always here</div>'
        '</div>'
        '<div class="yumea-header-btn">📞<span class="yumea-tooltip">Coming Soon</span></div>'
        '<div class="yumea-header-btn">📹<span class="yumea-tooltip">Coming Soon</span></div>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # Messages area
    messages_html = ""
    if not history:
        messages_html = (
            '<div class="yumea-empty-state">'
            + get_avatar_html(120, "yumea-empty-avatar") +
            '<div class="yumea-empty-title">Hi, I\'m Yumea 💛</div>'
            '<div class="yumea-empty-sub">Your emotional companion — here to listen, understand, and guide you through life\'s deeper questions.</div>'
            '</div>'
        )
    else:
        for msg in history:
            if msg["role"] == "user":
                safe_content = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                messages_html += (
                    '<div class="yumea-msg-row user">'
                    '<div class="yumea-msg-bubble user">' + safe_content + '</div>'
                    '</div>'
                )
            else:
                content_html = md_to_html(msg["content"])
                source_tag = ""
                if msg.get("source"):
                    source_tag = ' · <span class="yumea-source-tag">📖 ' + msg["source"] + '</span>'
                resp_time = ""
                if msg.get("response_time"):
                    resp_time = ' · ' + str(msg["response_time"]) + 's'
                ts = msg.get("time", "")
                messages_html += (
                    '<div class="yumea-msg-row ai">'
                    + get_avatar_html(32, "yumea-msg-avatar") +
                    '<div style="flex:1;max-width:70%;">'
                    '<div class="yumea-msg-bubble ai">' + content_html + '</div>'
                    '<div class="yumea-msg-meta ai-meta">' + ts + resp_time + source_tag + '</div>'
                    '</div>'
                    '</div>'
                )

    st.markdown(
        '<div class="yumea-messages-area" id="yumea-messages">' + messages_html + '</div>'
        '<script>'
        'setTimeout(function(){'
        'var m=document.getElementById("yumea-messages");'
        'if(m)m.scrollTop=m.scrollHeight;'
        '},100);'
        '</script>',
        unsafe_allow_html=True
    )

    # Show suggestions if empty
    if not history:
        st.markdown('<div style="max-width:600px;margin:20px auto;padding:0 20px;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Hey, Yumea 👋", use_container_width=True, key="sug_1"):
                st.session_state.pending_suggest = "Hey, Yumea 👋"
                st.rerun()
            if st.button("Mujhe motivation chahiye", use_container_width=True, key="sug_3"):
                st.session_state.pending_suggest = "Mujhe motivation chahiye"
                st.rerun()
        with col2:
            if st.button("How do I find inner peace?", use_container_width=True, key="sug_2"):
                st.session_state.pending_suggest = "How do I find inner peace?"
                st.rerun()
            if st.button("What is the meaning of life?", use_container_width=True, key="sug_4"):
                st.session_state.pending_suggest = "What is the meaning of life?"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Voice mic
    mic_text = None
    if MIC_RECORDER_AVAILABLE:
        col_mic1, col_mic2, col_mic3 = st.columns([1, 1, 1])
        with col_mic2:
            mic_audio = mic_recorder(
                start_prompt="🎤 Speak",
                stop_prompt="⏹ Stop",
                just_once=True,
                use_container_width=True,
                key="mic_recorder_chat"
            )
            if mic_audio and mic_audio.get("bytes"):
                try:
                    import whisper
                    model = whisper.load_model("tiny")
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                        tf.write(mic_audio["bytes"])
                        tf_path = tf.name
                    result = model.transcribe(tf_path, language="hi")
                    mic_text = result.get("text", "").strip()
                    os.unlink(tf_path)
                except Exception:
                    pass

    # Chat input
    prompt = st.chat_input("Type your message...", key="chat_input_main")

    user_input = prompt or mic_text

    if user_input:
        process_user_message(user_input)
        st.rerun()


def render_premium():
    """Premium plans page."""
    st.markdown('<div class="yumea-page-container">', unsafe_allow_html=True)
    
    if st.button("← Back to Chat", key="premium_back"):
        navigate_to("chat")
    
    st.markdown(
        '<h1 class="yumea-page-title">💎 Upgrade Your Experience</h1>'
        '<p class="yumea-page-desc">Unlock more messages, longer conversations, and deeper wisdom.</p>',
        unsafe_allow_html=True
    )
    
    # Premium Lite
    st.markdown(
        '<div class="yumea-plan-card">'
        '<div style="font-size:14px;color:#8b5cf6;font-weight:600;">PREMIUM LITE</div>'
        '<div class="yumea-plan-price">₹69 <span>/ month</span></div>'
        '<div style="margin:16px 0;">'
        '<div class="yumea-plan-feature"><span class="check">✓</span> 150 messages per day</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> 2,000 words per message</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> Friend + Professional modes</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> All 11 Wisdom Sources</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> Debate Mode</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    if st.button("Choose Premium Lite", use_container_width=True, key="buy_lite", type="primary"):
        st.session_state.selected_plan = "premium_lite"
        st.session_state.payment_done = False
        navigate_to("payment")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Premium Pro
    st.markdown(
        '<div class="yumea-plan-card pro">'
        '<div style="font-size:14px;color:#fbbf24;font-weight:600;">PREMIUM PRO ⭐</div>'
        '<div class="yumea-plan-price">₹199 <span>/ month</span></div>'
        '<div style="margin:16px 0;">'
        '<div class="yumea-plan-feature"><span class="check">✓</span> 500 messages per day</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> 5,000 words per message</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> Friend + Professional modes</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> All 11 Wisdom Sources</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> Debate Mode</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> Priority AI responses</div>'
        '<div class="yumea-plan-feature"><span class="check">✓</span> Early access to new features</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    if st.button("Choose Premium Pro", use_container_width=True, key="buy_pro", type="primary"):
        st.session_state.selected_plan = "premium_pro"
        st.session_state.payment_done = False
        navigate_to("payment")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_payment():
    """Mock Payment page."""
    plan = st.session_state.get("selected_plan", "premium_lite")
    plan_info = PLANS.get(plan, PLANS["premium_lite"])

    if not st.session_state.payment_done:
        st.session_state.payment_done = True
        st.session_state.user_plan = plan
        update_user_plan(st.session_state.user_email, plan)

    st.markdown('<div class="yumea-page-container" style="text-align:center;padding-top:80px;">', unsafe_allow_html=True)
    
    st.markdown(
        '<div style="font-size:64px;margin-bottom:20px;">✅</div>'
        '<h1 class="yumea-page-title" style="text-align:center;">Payment Successful!</h1>'
        '<p class="yumea-page-desc" style="text-align:center;">'
        'You are now on <strong style="color:#8b5cf6;">' + plan_info["name"] + '</strong> plan at ' + plan_info["price"] +
        '</p>'
        '<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);border-radius:12px;padding:20px;max-width:400px;margin:24px auto;">'
        '<div style="color:#10b981;font-size:14px;">🎉 Enjoy your upgraded experience!</div>'
        '<div style="color:#94a3b8;font-size:13px;margin-top:8px;">Your new limits are active immediately.</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Chat", use_container_width=True, key="pay_back", type="primary"):
            navigate_to("chat")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_reviews():
    """Reviews page."""
    st.markdown('<div class="yumea-page-container">', unsafe_allow_html=True)
    
    if st.button("← Back to Chat", key="rev_back"):
        navigate_to("chat")
    
    st.markdown(
        '<h1 class="yumea-page-title">⭐ Rate Yumea</h1>'
        '<p class="yumea-page-desc">Your feedback helps Yumea become a better companion.</p>',
        unsafe_allow_html=True
    )
    
    rating = st.slider("Your Rating (1-5 stars)", 1, 5, 5, step=1, key="rev_rating")
    
    stars_display = "⭐" * rating
    st.markdown(
        '<div style="text-align:center;font-size:32px;letter-spacing:6px;margin:12px 0;">' + stars_display + '</div>',
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        rev_name = st.text_input("Name", value=st.session_state.user_name, key="rev_name")
    with col2:
        rev_email = st.text_input("Email", value=st.session_state.user_email, key="rev_email")
    
    liked = st.text_area("What did you like about Yumea?", key="rev_liked", height=80)
    improve = st.text_area("What can we improve?", key="rev_improve", height=80)
    thoughts = st.text_area("Overall thoughts", key="rev_thoughts", height=80)
    
    if st.button("Submit Review", type="primary", use_container_width=True, key="rev_submit"):
        with st.spinner("Sending your review..."):
            success, msg = send_review_email(rev_name, rev_email, rating, liked, improve, thoughts)
            if success:
                st.balloons()
                st.markdown(
                    '<div class="yumea-success" style="margin-top:16px;">'
                    '✅ Thank you for your review! Your feedback means the world to us. 🌙'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div class="yumea-auth-error" style="margin-top:16px;">' + msg + '</div>',
                    unsafe_allow_html=True
                )
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_listen():
    """Listen to Source page."""
    st.markdown('<div class="yumea-page-container">', unsafe_allow_html=True)
    
    if st.button("← Back to Chat", key="listen_back_top"):
        navigate_to("chat")
    
    st.markdown(
        '<h1 class="yumea-page-title">🎧 Listen to Source</h1>'
        '<p class="yumea-page-desc">Select a wisdom tradition and listen to its voice.</p>',
        unsafe_allow_html=True
    )
    
    source = st.selectbox("Wisdom Source", WISDOM_SOURCES, key="listen_source_sel")
    lang = st.selectbox("Language", ["Hinglish", "Hindi", "English"], key="listen_lang_sel")
    
    if st.button("🎧 Get Wisdom", type="primary", use_container_width=True, key="listen_get"):
        with st.spinner("Channeling wisdom from " + source + "..."):
            insight = generate_wisdom_insight(source, lang, st.session_state.ai_model)
            if insight:
                st.session_state.listen_text = insight
                st.session_state.listen_source_name = source
                if EDGE_TTS_AVAILABLE:
                    voice = "hi-IN-SwaraNeural" if lang in ("Hindi", "Hinglish") else "en-IN-NeerjaNeural"
                    try:
                        audio_path = asyncio.run(generate_audio(insight, voice))
                        st.session_state.listen_audio = audio_path
                    except Exception:
                        st.session_state.listen_audio = None
                else:
                    st.session_state.listen_audio = None
                st.rerun()
            else:
                st.error("Failed to generate wisdom. Please try again.")
    
    if st.session_state.listen_text:
        src_name = st.session_state.listen_source_name or source
        st.markdown(
            '<div class="yumea-source-card">'
            '<div class="yumea-source-text">' + md_to_html(st.session_state.listen_text) + '</div>'
            '<div class="yumea-source-attr">— ' + src_name + '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        if st.session_state.listen_audio:
            try:
                with open(st.session_state.listen_audio, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
            except Exception:
                pass
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➡️ Next Wisdom", use_container_width=True, key="listen_next"):
                with st.spinner("Channeling new wisdom from " + source + "..."):
                    insight = generate_wisdom_insight(source, lang, st.session_state.ai_model)
                    if insight:
                        st.session_state.listen_text = insight
                        st.session_state.listen_source_name = source
                        if EDGE_TTS_AVAILABLE:
                            voice = "hi-IN-SwaraNeural" if lang in ("Hindi", "Hinglish") else "en-IN-NeerjaNeural"
                            try:
                                audio_path = asyncio.run(generate_audio(insight, voice))
                                st.session_state.listen_audio = audio_path
                            except Exception:
                                st.session_state.listen_audio = None
                        else:
                            st.session_state.listen_audio = None
                        st.rerun()
                    else:
                        st.error("Failed to generate new wisdom. Please try again.")
        
        with col2:
            if st.button("🔊 Replay Audio", use_container_width=True, key="listen_replay"):
                if EDGE_TTS_AVAILABLE and st.session_state.listen_text:
                    voice = "hi-IN-SwaraNeural" if lang in ("Hindi", "Hinglish") else "en-IN-NeerjaNeural"
                    try:
                        audio_path = asyncio.run(generate_audio(st.session_state.listen_text, voice))
                        st.session_state.listen_audio = audio_path
                        st.rerun()
                    except Exception:
                        pass
    
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════
def main():
    # Start analytics tracking
    if ANALYTICS_AVAILABLE:
        streamlit_analytics.start_tracking()
    
    init_session_state()

    # Inject global CSS
    st.markdown('<style>' + GLOBAL_CSS + '</style>', unsafe_allow_html=True)

    # Router
    page = st.session_state.current_page
    is_auth = st.session_state.authenticated

    # Not authenticated → only show signin/signup
    if not is_auth and page not in ("signin", "signup"):
        st.session_state.current_page = "signin"
        page = "signin"

    # Authenticated → redirect away from signin/signup
    if is_auth and page in ("signin", "signup"):
        st.session_state.current_page = "chat"
        page = "chat"

             # Render page
    if page == "signin":
        render_signin()
    elif page == "signup":
        render_signup()
    elif page == "chat":
        render_chat()
    elif page == "premium":
        render_premium()
    elif page == "payment":
        render_payment()
    elif page == "reviews":
        render_reviews()
    elif page == "listen":
        render_listen()
    else:
        st.session_state.current_page = "chat"
        st.rerun()


if __name__ == "__main__":
    main()
