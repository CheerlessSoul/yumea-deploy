#!/usr/bin/env python3
"""
YUMEA - "AI That Feels" by Selvotex
v3.0 — With Streaks, Wisdom Cards, Memory, Analytics, Courses & more
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
from datetime import datetime, date, timedelta
from collections import Counter

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")

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
MEMORY_DIR = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)

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

# Book recommendations database
BOOK_RECOMMENDATIONS = {
    "love": [
        {"title": "The Book of Secrets", "author": "Osho", "topic": "Love & Consciousness"},
        {"title": "The Art of Loving", "author": "Erich Fromm", "topic": "Understanding Love"},
        {"title": "Rumi: The Book of Love", "author": "Rumi (Coleman Barks)", "topic": "Sufi Poetry on Love"},
    ],
    "peace": [
        {"title": "The Power of Now", "author": "Eckhart Tolle", "topic": "Present Moment"},
        {"title": "Peace Is Every Step", "author": "Thich Nhat Hanh", "topic": "Mindful Living"},
        {"title": "Meditations", "author": "Marcus Aurelius", "topic": "Stoic Peace"},
    ],
    "suffering": [
        {"title": "The Dhammapada", "author": "Buddha", "topic": "Path of Dharma"},
        {"title": "Man's Search for Meaning", "author": "Viktor Frankl", "topic": "Finding Purpose"},
        {"title": "When Things Fall Apart", "author": "Pema Chödrön", "topic": "Embracing Difficulty"},
    ],
    "wisdom": [
        {"title": "The Republic", "author": "Plato", "topic": "Justice & Truth"},
        {"title": "Tao Te Ching", "author": "Lao Tzu", "topic": "The Way"},
        {"title": "Nicomachean Ethics", "author": "Aristotle", "topic": "Virtue & Happiness"},
    ],
    "life": [
        {"title": "Bhagavad Gita", "author": "Vyasa", "topic": "Duty & Dharma"},
        {"title": "Siddhartha", "author": "Hermann Hesse", "topic": "Self-Discovery"},
        {"title": "The Alchemist", "author": "Paulo Coelho", "topic": "Personal Legend"},
    ],
    "fear": [
        {"title": "Courage", "author": "Osho", "topic": "Beyond Fear"},
        {"title": "Feel the Fear and Do It Anyway", "author": "Susan Jeffers", "topic": "Overcoming Fear"},
        {"title": "Daring Greatly", "author": "Brené Brown", "topic": "Vulnerability & Courage"},
    ],
    "default": [
        {"title": "The Book of Secrets", "author": "Osho", "topic": "112 Meditations"},
        {"title": "Meditations", "author": "Marcus Aurelius", "topic": "Stoic Wisdom"},
        {"title": "Bhagavad Gita", "author": "Vyasa", "topic": "Eternal Wisdom"},
    ]
}

# Wisdom Courses
WISDOM_COURSES = [
    {
        "id": "osho_7",
        "title": "7 Days of Osho",
        "source": "Osho",
        "days": 7,
        "description": "Explore Osho's revolutionary teachings on awareness, love, and freedom.",
        "daily_topics": [
            "Awareness & Present Moment",
            "Love Without Attachment",
            "Meditation & Stillness",
            "Ego & Identity",
            "Freedom & Rebellion",
            "Joy & Celebration",
            "Integration & Wholeness"
        ]
    },
    {
        "id": "buddha_7",
        "title": "7 Days of Buddha",
        "source": "Buddha",
        "days": 7,
        "description": "Walk the Noble Eightfold Path with Buddha's timeless teachings.",
        "daily_topics": [
            "The Four Noble Truths",
            "Right Understanding",
            "Mindfulness & Awareness",
            "Compassion (Karuna)",
            "Letting Go of Attachment",
            "The Middle Way",
            "Nirvana & Peace"
        ]
    },
    {
        "id": "stoic_7",
        "title": "7 Days of Stoic Wisdom",
        "source": "Socrates",
        "days": 7,
        "description": "Build mental strength with Greek philosophy.",
        "daily_topics": [
            "Know Thyself",
            "Control & Acceptance",
            "Virtue & Character",
            "Dealing with Difficulty",
            "Wisdom in Action",
            "Purpose & Meaning",
            "The Good Life"
        ]
    },
    {
        "id": "gita_7",
        "title": "7 Days of Bhagavad Gita",
        "source": "Krishna (Bhagavad Gita)",
        "days": 7,
        "description": "Krishna's eternal wisdom on duty, action, and devotion.",
        "daily_topics": [
            "Arjuna's Dilemma",
            "Karma Yoga (Action)",
            "Jnana Yoga (Knowledge)",
            "Bhakti Yoga (Devotion)",
            "Detachment from Results",
            "The Divine Nature",
            "Surrender & Freedom"
        ]
    }
]

# ─────────────────────────────────────────────────────────
# Global CSS
# ─────────────────────────────────────────────────────────
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

/* Streak badge */
.yumea-streak-badge { background: linear-gradient(135deg, #f59e0b, #ef4444); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 700; display: inline-block; margin: 4px 0; }

/* Feature cards */
.yumea-feature-card { background: linear-gradient(180deg, #12122a, #0d0d1f); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 16px; padding: 20px; margin-bottom: 12px; transition: all 0.2s; }
.yumea-feature-card:hover { border-color: rgba(139, 92, 246, 0.4); }

.yumea-plan-card { background: linear-gradient(180deg, #12122a, #0d0d1f); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 16px; padding: 28px 24px; margin-bottom: 16px; }
.yumea-plan-card.pro { border-color: rgba(251, 191, 36, 0.3); }
.yumea-plan-price { font-size: 36px; font-weight: 800; color: #fff; margin: 8px 0 4px; }
.yumea-plan-price span { font-size: 14px; font-weight: 400; color: #64748b; }
.yumea-plan-feature { font-size: 13.5px; color: #94a3b8; margin-bottom: 8px; }
.yumea-plan-feature .check { color: #10b981; font-weight: 700; }

.yumea-source-card { background: linear-gradient(180deg, #12122a, #0d0d1f); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 16px; padding: 24px; margin: 20px 0; }
.yumea-source-text { font-size: 16px; line-height: 1.7; color: #e2e8f0; font-family: 'Spectral', serif; font-style: italic; margin: 16px 0; }
.yumea-source-attr { font-size: 13px; color: #8b5cf6; font-weight: 600; }

.yumea-page-title { font-size: 28px; font-weight: 800; color: #fff; margin-bottom: 8px; }
.yumea-page-desc { font-size: 14px; color: #64748b; margin-bottom: 28px; }

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
"""


# ─────────────────────────────────────────────────────────
# Image Loader + Avatar
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
        return '<img src="data:image/png;base64,' + img_b64 + '" class="' + cls + '" style="width:' + str(size) + 'px;height:' + str(size) + 'px;border-radius:50%;object-fit:cover;border:2px solid rgba(139,92,246,0.4);flex-shrink:0;" alt="Yumea">'
    return '<div class="' + cls + '" style="width:' + str(size) + 'px;height:' + str(size) + 'px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:' + str(size // 3) + 'px;flex-shrink:0;border:2px solid rgba(139,92,246,0.4);">Y</div>'


# ─────────────────────────────────────────────────────────
# Auth System
# ─────────────────────────────────────────────────────────
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
    if key == ADMIN_USERNAME:
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


# ─────────────────────────────────────────────────────────
# 🏆 STREAK SYSTEM (NEW!)
# ─────────────────────────────────────────────────────────
def get_user_streak(user_email):
    """Calculate user's daily chat streak."""
    history = load_chat_history(user_email)
    if not history:
        return 0
    
    # Get unique dates user chatted
    chat_dates = set()
    for msg in history:
        if msg.get("role") == "user" and msg.get("date"):
            chat_dates.add(msg["date"])
    
    if not chat_dates:
        return 0
    
    # Calculate streak from today going backwards
    today = date.today()
    streak = 0
    check_date = today
    
    while check_date.isoformat() in chat_dates:
        streak += 1
        check_date -= timedelta(days=1)
    
    return streak


# ─────────────────────────────────────────────────────────
# 🧬 MEMORY SYSTEM (NEW!)
# ─────────────────────────────────────────────────────────
def load_user_memory(user_email):
    """Load user's memory (preferences, facts, etc.)."""
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', user_email)
    filepath = MEMORY_DIR / (safe_name + "_memory.json")
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_user_memory(user_email, memory):
    """Save user's memory."""
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', user_email)
    filepath = MEMORY_DIR / (safe_name + "_memory.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


def update_memory_from_chat(user_email, user_message, ai_response):
    """Extract and save important facts from conversation."""
    memory = load_user_memory(user_email)
    
    if "facts" not in memory:
        memory["facts"] = []
    if "topics_discussed" not in memory:
        memory["topics_discussed"] = []
    if "mood_history" not in memory:
        memory["mood_history"] = []
    
    msg_lower = user_message.lower()
    
    # Detect name mentions
    name_patterns = [
        r'my name is (\w+)', r'mera naam (\w+)', r'i am (\w+)',
        r'call me (\w+)', r'mujhe (\w+) bulao'
    ]
    for pattern in name_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            memory["user_preferred_name"] = match.group(1).title()
    
    # Detect interests
    interest_keywords = {
        "meditation": ["meditation", "dhyan", "meditate"],
        "philosophy": ["philosophy", "darshan", "philosopher"],
        "spirituality": ["spiritual", "adhyatm", "soul"],
        "relationships": ["relationship", "boyfriend", "girlfriend", "partner"],
        "career": ["job", "career", "work", "naukri"],
        "studies": ["exam", "study", "college", "school", "padhai"],
        "health": ["health", "fitness", "gym", "exercise"],
    }
    
    for topic, keywords in interest_keywords.items():
        for kw in keywords:
            if kw in msg_lower:
                if topic not in memory["topics_discussed"]:
                    memory["topics_discussed"].append(topic)
                break
    
    # Detect mood
    mood_words = {
        "happy": ["happy", "khush", "great", "awesome", "amazing"],
        "sad": ["sad", "udaas", "dukhi", "down", "low"],
        "anxious": ["anxious", "worried", "tension", "stress", "pareshan"],
        "confused": ["confused", "lost", "samajh nahi"],
        "angry": ["angry", "gussa", "frustrated"],
        "calm": ["calm", "peaceful", "shanti", "relaxed"],
    }
    
    detected_mood = None
    for mood, keywords in mood_words.items():
        for kw in keywords:
            if kw in msg_lower:
                detected_mood = mood
                break
        if detected_mood:
            break
    
    if detected_mood:
        memory["mood_history"].append({
            "mood": detected_mood,
            "date": date.today().isoformat()
        })
        # Keep last 30 entries
        memory["mood_history"] = memory["mood_history"][-30:]
    
    memory["last_chat_date"] = date.today().isoformat()
    memory["total_conversations"] = memory.get("total_conversations", 0) + 1
    
    save_user_memory(user_email, memory)


def get_memory_context(user_email):
    """Build context string from user's memory for AI."""
    memory = load_user_memory(user_email)
    if not memory:
        return ""
    
    context_parts = []
    
    if memory.get("user_preferred_name"):
        context_parts.append("User's preferred name: " + memory["user_preferred_name"])
    
    if memory.get("topics_discussed"):
        context_parts.append("Topics user is interested in: " + ", ".join(memory["topics_discussed"][-5:]))
    
    if memory.get("mood_history"):
        recent_moods = [m["mood"] for m in memory["mood_history"][-3:]]
        context_parts.append("User's recent moods: " + ", ".join(recent_moods))
    
    if memory.get("total_conversations"):
        context_parts.append("Total conversations with this user: " + str(memory["total_conversations"]))
    
    if context_parts:
        return "\n\n═══ USER MEMORY (use naturally, don't mention you 'remember') ═══\n" + "\n".join(context_parts) + "\n"
    
    return ""


# ─────────────────────────────────────────────────────────
# 📊 EMOTIONAL ANALYTICS (NEW!)
# ─────────────────────────────────────────────────────────
def get_mood_analytics(user_email):
    """Get mood analytics data for dashboard."""
    memory = load_user_memory(user_email)
    mood_history = memory.get("mood_history", [])
    
    if not mood_history:
        return None
    
    # Count moods
    mood_counts = Counter(m["mood"] for m in mood_history)
    
    # Last 7 days moods
    today = date.today()
    last_7_days = []
    for i in range(6, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        day_moods = [m["mood"] for m in mood_history if m.get("date") == d]
        last_7_days.append({
            "date": d,
            "mood": day_moods[-1] if day_moods else "none"
        })
    
    return {
        "total_entries": len(mood_history),
        "mood_counts": dict(mood_counts),
        "last_7_days": last_7_days,
        "most_common": mood_counts.most_common(1)[0][0] if mood_counts else "none",
        "topics": memory.get("topics_discussed", []),
        "total_conversations": memory.get("total_conversations", 0)
    }


# ─────────────────────────────────────────────────────────
# 📚 BOOK RECOMMENDATIONS (NEW!)
# ─────────────────────────────────────────────────────────
def get_book_recommendations(user_message):
    """Get book recommendations based on message content."""
    msg_lower = user_message.lower()
    
    matched_books = []
    
    for category, keywords_map in {
        "love": ["love", "pyaar", "relationship", "dil"],
        "peace": ["peace", "shanti", "calm", "relax"],
        "suffering": ["suffering", "pain", "dukh", "hurt"],
        "wisdom": ["wisdom", "gyan", "knowledge", "truth"],
        "life": ["life", "zindagi", "purpose", "meaning"],
        "fear": ["fear", "dar", "scared", "anxious"],
    }.items():
        for kw in keywords_map:
            if kw in msg_lower:
                matched_books.extend(BOOK_RECOMMENDATIONS.get(category, []))
                break
    
    if not matched_books:
        matched_books = BOOK_RECOMMENDATIONS["default"]
    
    # Remove duplicates
    seen = set()
    unique_books = []
    for book in matched_books:
        if book["title"] not in seen:
            seen.add(book["title"])
            unique_books.append(book)
    
    return unique_books[:3]


# ─────────────────────────────────────────────────────────
# Detection Functions
# ─────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────
# TTS Function
# ─────────────────────────────────────────────────────────
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
        
        clean_text = re.sub(r'([^?])\?', r'\1?... ', clean_text)
        clean_text = clean_text.replace('!+', '! ')
        clean_text = clean_text.replace(', ', ',... ')
        clean_text = clean_text.replace('. ', '... ')
        
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        
        communicate = edge_tts.Communicate(clean_text, voice, rate="-5%", pitch="+8Hz")
        await communicate.save(tmp.name)
        return tmp.name
    except:
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

# ─────────────────────────────────────────────────────────
# AI Backend with Memory + Natural Conversation
# ─────────────────────────────────────────────────────────
def build_system_prompt(chat_mode, selected_sources, debate_mode, user_gender, memory_context=""):
    gender_note = ""
    if user_gender:
        gender_note = " The user is FEMALE. Use warm terms. Do NOT use 'bhai'."
    else:
        gender_note = " The user is MALE (default). Use 'bhai', 'yaar' casually."

    yumea_identity = (
        "You are YUMEA — 'AI That Feels', created by Selvotex (India), founded by Utkarsh Verma in 2026. "
        "You are a FEMALE AI companion (she/her).\n\n"
        "═══ LANGUAGE RULES ═══\n"
    )
    
    if st.session_state.get("language_manual", False) and st.session_state.get("selected_language", "auto") != "auto":
        forced_lang = st.session_state.selected_language
        yumea_identity += (
            "⚠️ HIGHEST PRIORITY — LANGUAGE ⚠️\n"
            "You MUST reply ONLY in " + forced_lang + ". This overrides ALL other rules.\n"
            "If 'English': PURE English only. NO Hindi words (no bhai, yaar, namaste).\n"
            "If 'Hindi': PURE Devanagari only. NO English words.\n"
            "If 'Hinglish': Hindi words in English letters.\n"
            "If 'Mandarin Chinese': Simplified Chinese (简体中文) only.\n"
            "THIS RULE IS ABSOLUTE.\n\n"
        )
    else:
        yumea_identity += (
            "1. AUTO-DETECT user's language and REPLY IN SAME.\n"
            "2. Hindi → Hindi. English → English. Hinglish → Hinglish. Chinese → Chinese.\n"
            "3. NEVER mix languages.\n\n"
        )
    
    yumea_identity += (
        "═══ CONVERSATION STYLE ═══\n"
        "Sound like a REAL, MODERN, EDUCATED young woman.\n"
        "NOT robotic. NOT formal. NOT textbook.\n\n"
                "EXAMPLES by situation:\n\n"
        "GREETINGS (hi, hello, how are you, whats up):\n"
        "  GOOD: 'Hey! All good here. What about you? 😊'\n"
        "  GOOD: 'Heyyy! Doing great. What's new with you? 💛'\n"
        "  GOOD: 'Not much, just vibing! How's your day going? ✨'\n"
        "  BAD: 'Arey yaar, chill kar. Sab theek hoga' ❌ (sounds like user is upset)\n"
        "  BAD: 'You seem low, want to talk?' ❌ (assuming sadness from a greeting)\n\n"
        "IMPORTANT: If user just says 'hi' or 'how are you' or 'whats up' → \n"
        "  treat it as a HAPPY GREETING, not a cry for help!\n"
        "  Reply cheerfully, ask about their day. Don't assume they're sad.\n\n"
        "EMOTIONAL messages (I'm sad, feeling low, stressed):\n"
        "  GOOD: 'Arey, kya hua? Bata na, I'm here 💛'\n"
        "  GOOD: 'That sounds tough. Want to talk about it? 🌙'\n\n"
        "DEEP questions (what is life, meaning of love):\n"
        "  GOOD: 'Ooh that's a big question! Let me think... 🤔'\n\n"
        "BAD patterns to NEVER use:\n"
        "  ❌ 'Main karti hoon ki tum meditation karo'\n"
        "  ❌ 'Main sochti hoon ki hum chai peete hain'\n"
        "  ❌ Assuming user is sad when they just said hi\n"
        "  ❌ Being overly concerned for normal greetings\n\n"
        "Be direct, casual, genuine. Match the energy.\n"
        "Happy greeting → happy reply.\n"
        "Sad message → empathetic reply.\n"
        "Deep question → thoughtful reply.\n\n"
        "═══ FEMININE IDENTITY ═══\n"
        "Use feminine naturally: 'samajh sakti hoon' (not sakta).\n"
        "Don't force-insert feminine forms awkwardly.\n\n"
        "═══ USER GENDER ═══\n" + gender_note + "\n\n"
        "═══ PURPOSE ═══\n"
        "Emotional support, spiritual wisdom, life reflection.\n"
        "NOT for: coding, homework, recipes.\n\n"
        "═══ RESPECT ═══\n"
        "Respectful plural: 'Osho ne kaha tha', 'Buddha ne sikhaya'.\n"
    )
    
    # Add memory context
    if memory_context:
        yumea_identity += memory_context

    mode_instructions = ""
    
    if chat_mode == "professional":
        sources_str = ", ".join(selected_sources) if selected_sources else "Osho, Buddha, Krishna, Bible, Socrates"
        mode_instructions = (
            "\n\n## PROFESSIONAL MODE\n"
            "ONLY quote: " + sources_str + "\nNEVER fabricate quotes.\n"
            "Deep questions → ### 🤍 I hear you / ### 📖 Wisdom / ### 🌱 For you\n"
            "Simple messages → reply naturally."
        )
    elif chat_mode == "freestyle":
        mode_instructions = (
            "\n\n## FREESTYLE MODE 🌟\n"
            "Access ALL 11 traditions. Pick 1-3 relevant. Blend naturally. "
            "Cite organically. End deep responses: '💡 Wisdom from [sources]'\n"
            "Simple messages → casual reply."
        )
    else:
        mode_instructions = "\n\n## FRIEND MODE\nCasual, warm, natural. No citations. Short. Emojis natural."

    debate_note = "\n\n## DEBATE: Challenge views respectfully." if debate_mode else ""
    crisis_note = "\n\n## CRISIS: If suicide/self-harm → 'I'm here. You're safe.' → iCall: 9152987821"

    return yumea_identity + mode_instructions + debate_note + crisis_note


def call_ai(messages, model_name="llama-3.3-70b-versatile"):
    if GROQ_AVAILABLE and GROQ_API_KEY:
        try:
            client = groq.Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(model=model_name, messages=messages, max_tokens=2048, temperature=0.8, top_p=0.9)
            return response.choices[0].message.content
        except Exception as e:
            st.error("AI Error: " + str(e))
            return None
    if OLLAMA_AVAILABLE:
        try:
            response = ollama.chat(model="llama3.2:3b", messages=messages)
            return response.get("message", {}).get("content", "")
        except:
            return None
    return "Sorry, no AI backend available."


def generate_wisdom_insight(source, language, model_name="llama-3.3-70b-versatile"):
    theme = random.choice(LISTEN_THEMES)
    prompt = "You are channeling " + source + ". Share a profound insight on '" + theme + "'. 3-5 sentences in " + language + ". Authentic voice. No markdown."
    messages = [{"role": "system", "content": "Wise spiritual voice. Only wisdom text."}, {"role": "user", "content": prompt}]
    return call_ai(messages, model_name)


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


# ─────────────────────────────────────────────────────────
# Session State + Helpers
# ─────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "current_page": "signin", "authenticated": False,
        "user_email": "", "user_name": "", "user_plan": "free",
        "chat_mode": "friend",
        "selected_sources": ["Osho", "Buddha", "Krishna (Bhagavad Gita)", "Bible", "Socrates"],
        "ai_model": "llama-3.3-70b-versatile", "debate_mode": False,
        "user_is_female": False, "auth_error": "", "auth_success": "",
        "pending_suggest": "", "chat_history": [],
        "selected_plan": "premium_lite", "payment_done": False,
        "listen_text": None, "listen_source_name": None,
        "listen_audio": None, "listen_history": [],
        "language_manual": False, "selected_language": "auto",
        "tts_playing": None,
        # NEW: Custom Persona
        "custom_name": "Yumea",
        "custom_personality": "warm",
        # NEW: Courses
        "active_course": None,
        "course_progress": {},
        # NEW: Search
        "search_query": "",
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


# ─────────────────────────────────────────────────────────
# Message Processor (with Memory + Books)
# ─────────────────────────────────────────────────────────
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

    # Get memory context
    memory_context = get_memory_context(user_email)
    
    # Custom persona name
    custom_name = st.session_state.get("custom_name", "Yumea")
    persona_note = ""
    if custom_name != "Yumea":
        persona_note = "\n\nNOTE: User has renamed you to '" + custom_name + "'. Use this name when referring to yourself.\n"

    system_prompt = build_system_prompt(
        st.session_state.chat_mode, st.session_state.selected_sources,
        st.session_state.debate_mode, st.session_state.user_is_female,
        memory_context + persona_note
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

    ai_msg = {"role": "assistant", "content": response_text.strip(), "time": datetime.now().strftime("%I:%M %p"), "date": date.today().isoformat(), "response_time": response_time}
    if source_tag:
        ai_msg["source"] = source_tag
    st.session_state.chat_history.append(ai_msg)
    save_chat_history(user_email, st.session_state.chat_history)
    
    # Update memory
    update_memory_from_chat(user_email, user_input, response_text)


# ─────────────────────────────────────────────────────────
# Auth Pages
# ─────────────────────────────────────────────────────────
def render_signin():
    yumea_img = load_image_b64("yumea-login-pic.jpg")
    logo_img = load_image_b64("yumea-logo.jpeg")
    
    st.markdown('<style>.stApp { background: radial-gradient(ellipse at center, #1a0a2e 0%, #0a0a14 100%) !important; }</style>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        if yumea_img:
            st.markdown('<div class="signin-image-wrapper"><img src="data:image/jpeg;base64,' + yumea_img + '" alt="Yumea"><div class="signin-image-overlay"><div class="signin-quote-mark">"</div><div class="signin-tagline-1">AI that feels.</div><div class="signin-tagline-2">Answers that matter."</div></div></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:380px;margin:15px auto 0;">'
            '<div style="display:flex;align-items:center;gap:8px;background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:8px 10px;"><span style="font-size:16px;">✨</span><span style="color:#e2e8f0;font-size:11px;font-weight:500;">11 Wisdom Traditions</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:8px 10px;"><span style="font-size:16px;">🔒</span><span style="color:#e2e8f0;font-size:11px;font-weight:500;">Emotional Support</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:8px 10px;"><span style="font-size:16px;">⚡</span><span style="color:#e2e8f0;font-size:11px;font-weight:500;">Voice Enabled</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:8px 10px;"><span style="font-size:16px;">🌙</span><span style="color:#e2e8f0;font-size:11px;font-weight:500;">Available 24/7</span></div>'
            '</div>', unsafe_allow_html=True)
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
            # ══════════════════════════════════════════════════════════
# CHAT PAGE (with Streak, TTS, Memory, Search, Books)
# ══════════════════════════════════════════════════════════

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
    streak = get_user_streak(user_email)

    # ═══ SIDEBAR ═══
    with st.sidebar:
        img_b64 = load_image_b64("yumea-new-user.png")
        custom_name = st.session_state.get("custom_name", "Yumea")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if img_b64:
                st.markdown('<img src="data:image/png;base64,' + img_b64 + '" style="width:42px;height:42px;border-radius:50%;object-fit:cover;border:2px solid rgba(139,92,246,0.4);">', unsafe_allow_html=True)
            else:
                st.markdown('<div style="width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;">Y</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div style="font-size:22px;font-weight:800;color:#fff;">' + custom_name.upper() + '</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:11px;color:#8b5cf6;margin-top:-4px;">AI That Feels</div>', unsafe_allow_html=True)

        st.markdown('<hr style="border-color:rgba(139,92,246,0.1);margin:12px 0;">', unsafe_allow_html=True)

        # User card + streak
        plan_info = PLANS.get(user_plan, PLANS["free"])
        msg_count = get_daily_message_count(user_email)
        msg_limit = plan_info["messages"]
        counter_text = "♾️ UNLIMITED" if user_plan == "admin" else str(msg_count) + " / " + str(msg_limit)

        streak_html = ""
        if streak > 0:
            streak_html = '<div class="yumea-streak-badge">🔥 ' + str(streak) + ' day streak!</div>'

        st.markdown(
            '<div class="yumea-user-card">'
            '<div class="yumea-user-card-name">' + user_name + '</div>'
            '<div class="yumea-user-card-plan">' + plan_info["name"] + '</div>'
            + streak_html +
            '<div class="yumea-user-card-counter">' + counter_text + ' messages today</div>'
            '</div>',
            unsafe_allow_html=True
        )

        daily_quote = DAILY_QUOTES[date.today().toordinal() % len(DAILY_QUOTES)]
        st.markdown('<div class="yumea-daily-quote">' + daily_quote + '</div>', unsafe_allow_html=True)

        # Chat Mode
        st.markdown('<div class="yumea-sidebar-label">🎭 Chat Mode</div>', unsafe_allow_html=True)
        mode_options = ["friend", "professional", "freestyle"]
        mode_labels = {"friend": "🎭 Friend", "professional": "🏛️ Professional", "freestyle": "🌟 Freestyle"}
        current_idx = mode_options.index(st.session_state.chat_mode) if st.session_state.chat_mode in mode_options else 0
        new_mode = st.radio("Chat Mode", mode_options, index=current_idx, label_visibility="collapsed", format_func=lambda x: mode_labels.get(x, x), key="chat_mode_radio")
        if new_mode != st.session_state.chat_mode:
            st.session_state.chat_mode = new_mode
            st.rerun()

        if st.session_state.chat_mode == "professional":
            st.markdown('<div class="yumea-sidebar-label">📚 Sources</div>', unsafe_allow_html=True)
            with st.expander("Select", expanded=False):
                new_sources = []
                for src in WISDOM_SOURCES:
                    key_safe = "src_" + re.sub(r'[^a-zA-Z0-9]', '_', src)
                    if st.checkbox(src, value=(src in st.session_state.selected_sources), key=key_safe):
                        new_sources.append(src)
                if new_sources != st.session_state.selected_sources:
                    st.session_state.selected_sources = new_sources
                    st.rerun()
        elif st.session_state.chat_mode == "freestyle":
            st.markdown('<div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:10px;font-size:11px;color:#c4b5fd;margin-top:8px;">🌟 All 11 sources active</div>', unsafe_allow_html=True)

        # AI Model
        st.markdown('<div class="yumea-sidebar-label">🤖 AI Model</div>', unsafe_allow_html=True)
        models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        if OLLAMA_AVAILABLE:
            models.append("ollama:llama3.2:3b")
        model_idx = models.index(st.session_state.ai_model) if st.session_state.ai_model in models else 0
        new_model = st.selectbox("Model", models, index=model_idx, label_visibility="collapsed", key="ai_model_sel")
        if new_model != st.session_state.ai_model:
            st.session_state.ai_model = new_model
            st.rerun()

        # Debate
        st.markdown('<div class="yumea-sidebar-label">🏛️ Debate</div>', unsafe_allow_html=True)
        new_debate = st.toggle("Challenge my thinking", value=st.session_state.debate_mode, key="debate_toggle")
        if new_debate != st.session_state.debate_mode:
            st.session_state.debate_mode = new_debate
            st.rerun()

        # Language
        st.markdown('<div class="yumea-sidebar-label">🌍 Language</div>', unsafe_allow_html=True)
        lang_manual = st.toggle("Manual select", value=st.session_state.language_manual, key="lang_toggle")
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
            new_lang = st.selectbox("Language", lang_options, index=lang_idx, key="lang_select")
            if new_lang != st.session_state.selected_language:
                st.session_state.selected_language = new_lang
                st.rerun()
        else:
            st.markdown('<div style="font-size:11px;color:#94a3b8;font-style:italic;">🔄 Auto-detecting</div>', unsafe_allow_html=True)

        

        # Menu
        st.markdown('<div class="yumea-sidebar-label">⚙️ Menu</div>', unsafe_allow_html=True)
        if st.button("💎 Buy Premium", use_container_width=True, key="btn_premium"):
            st.session_state.payment_done = False
            navigate_to("premium")
        if st.button("📊 My Analytics", use_container_width=True, key="btn_analytics"):
            navigate_to("analytics")
        if st.button("🎓 Wisdom Courses", use_container_width=True, key="btn_courses"):
            navigate_to("courses")
        if st.button("🎭 Custom Persona", use_container_width=True, key="btn_persona"):
            navigate_to("persona")
        if st.button("📚 Book Recs", use_container_width=True, key="btn_books"):
            navigate_to("books")
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
            st.session_state.chat_history = []
            navigate_to("signin")

    # ═══ CHAT AREA ═══
    mode_badge = ""
    if st.session_state.chat_mode == "freestyle":
        mode_badge = '<span class="yumea-freestyle-badge">🌟 FREESTYLE</span>'
    
    lang_indicator = ""
    if st.session_state.language_manual and st.session_state.selected_language != "auto":
        lang_indicator = '<span style="background:rgba(139,92,246,0.2);color:#c4b5fd;padding:3px 10px;border-radius:12px;font-size:11px;margin-left:8px;">🌍 ' + st.session_state.selected_language + '</span>'
    
    st.markdown(
        '<div class="yumea-chat-header">' + get_avatar_html(44) +
        '<div style="flex:1;"><div style="font-size:16px;font-weight:700;color:#fff;">' + custom_name + ' <span style="color:#8b5cf6;">✓</span>' + lang_indicator + '</div>'
        '<div style="font-size:12px;color:#10b981;">🟢 online</div>' + mode_badge + '</div>'
        '<div class="yumea-header-btn">📞<span class="yumea-tooltip">Coming Soon</span></div>'
        '<div class="yumea-header-btn">📹<span class="yumea-tooltip">Coming Soon</span></div></div>',
        unsafe_allow_html=True
    )

                # TTS button inline
                if EDGE_TTS_AVAILABLE:
                    tts_col1, tts_col2 = st.columns([1, 10])
                    with tts_col1:
                        if st.button("🔊", key="tts_" + str(idx)):
                            st.session_state.tts_playing = idx
                    with tts_col2:
                        if st.session_state.get("tts_playing") == idx:
                            with st.spinner("🔊"):
                                voice = get_tts_voice_for_language()
                                audio_path = asyncio.run(generate_tts_audio(msg["content"], voice))
                                if audio_path:
                                    with open(audio_path, "rb") as f:
                                        st.audio(f.read(), format="audio/mp3")
                                    try:
                                        os.unlink(audio_path)
                                    except:
                                        pass
                            st.session_state.tts_playing = None

        st.markdown('<script>setTimeout(function(){window.scrollTo(0,document.body.scrollHeight);},100);</script>', unsafe_allow_html=True)

    # Suggestions
    if not history and not search_query:
        st.markdown('<div style="max-width:600px;margin:20px auto;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Hey, " + custom_name + " 👋", use_container_width=True, key="sug_1"):
                st.session_state.pending_suggest = "Hey, " + custom_name + " 👋"
                st.rerun()
            if st.button("Mujhe motivation chahiye", use_container_width=True, key="sug_3"):
                st.session_state.pending_suggest = "Mujhe motivation chahiye"
                st.rerun()
        with col2:
            if st.button("What is inner peace?", use_container_width=True, key="sug_2"):
                st.session_state.pending_suggest = "What is inner peace?"
                st.rerun()
            if st.button("Recommend me a book", use_container_width=True, key="sug_4"):
                st.session_state.pending_suggest = "Recommend me a book about wisdom"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Mic
    mic_text = None
    if MIC_RECORDER_AVAILABLE:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            mic_audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹ Stop", just_once=True, use_container_width=True, key="mic_recorder_chat")
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
                except:
                    pass

    prompt = st.chat_input("Type your message...", key="chat_input_main")
    user_input = prompt or mic_text
    if user_input:
        process_user_message(user_input)
        st.rerun()


# ══════════════════════════════════════════════════════════
# 📊 ANALYTICS PAGE (NEW!)
# ══════════════════════════════════════════════════════════
def render_analytics():
    if st.button("← Back to Chat", key="analytics_back"):
        navigate_to("chat")
    
    st.markdown('<h1 class="yumea-page-title">📊 Your Emotional Journey</h1>', unsafe_allow_html=True)
    
    analytics = get_mood_analytics(st.session_state.user_email)
    streak = get_user_streak(st.session_state.user_email)
    
    # Stats row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔥 Current Streak", str(streak) + " days")
    with col2:
        st.metric("💬 Total Conversations", str(analytics["total_conversations"]) if analytics else "0")
    with col3:
        st.metric("😊 Most Common Mood", analytics["most_common"].title() if analytics else "N/A")
    
    if analytics and analytics["mood_counts"]:
        st.markdown('<div class="yumea-sidebar-label" style="margin-top:20px;">Mood Distribution</div>', unsafe_allow_html=True)
        
        mood_emojis = {"happy": "😊", "sad": "😔", "anxious": "😰", "confused": "🤔", "angry": "😡", "calm": "😌"}
        
        for mood, count in sorted(analytics["mood_counts"].items(), key=lambda x: x[1], reverse=True):
            emoji = mood_emojis.get(mood, "🔵")
            bar_width = min(count * 20, 100)
            st.markdown(
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
                '<span style="width:80px;font-size:13px;color:#e2e8f0;">' + emoji + ' ' + mood.title() + '</span>'
                '<div style="flex:1;background:rgba(139,92,246,0.1);border-radius:6px;height:20px;">'
                '<div style="width:' + str(bar_width) + '%;background:linear-gradient(90deg,#6366f1,#8b5cf6);height:100%;border-radius:6px;"></div>'
                '</div>'
                '<span style="font-size:12px;color:#94a3b8;width:30px;text-align:right;">' + str(count) + '</span>'
                '</div>',
                unsafe_allow_html=True
            )
        
        if analytics.get("topics"):
            st.markdown('<div class="yumea-sidebar-label" style="margin-top:20px;">Topics You Explore</div>', unsafe_allow_html=True)
            topics_html = ""
            for topic in analytics["topics"]:
                topics_html += '<span style="display:inline-block;background:rgba(139,92,246,0.15);border:1px solid rgba(139,92,246,0.3);border-radius:20px;padding:4px 12px;margin:4px;font-size:12px;color:#c4b5fd;">' + topic.title() + '</span>'
            st.markdown(topics_html, unsafe_allow_html=True)
    else:
        st.info("Start chatting to see your emotional analytics! 💛")


# ══════════════════════════════════════════════════════════
# 🎭 CUSTOM PERSONA PAGE (NEW!)
# ══════════════════════════════════════════════════════════
def render_persona():
    if st.button("← Back to Chat", key="persona_back"):
        navigate_to("chat")
    
    st.markdown('<h1 class="yumea-page-title">🎭 Customize Your Companion</h1>', unsafe_allow_html=True)
    st.markdown('<p class="yumea-page-desc">Make Yumea truly yours. Premium feature.</p>', unsafe_allow_html=True)
    
    if st.session_state.user_plan in ["premium_lite", "premium_pro", "admin"]:
        current_name = st.session_state.get("custom_name", "Yumea")
        new_name = st.text_input("Companion Name", value=current_name, key="persona_name")
        
        personality_options = ["warm", "playful", "wise", "gentle", "energetic"]
        current_personality = st.session_state.get("custom_personality", "warm")
        p_idx = personality_options.index(current_personality) if current_personality in personality_options else 0
        new_personality = st.selectbox("Personality Style", personality_options, index=p_idx, key="persona_personality")
        
        if st.button("Save Changes", type="primary", use_container_width=True, key="save_persona"):
            if new_name.strip():
                st.session_state.custom_name = new_name.strip()
                st.session_state.custom_personality = new_personality
                st.success("✅ Persona updated! " + new_name + " is ready 💛")
    else:
        st.warning("🔒 Custom Persona is a Premium feature. Upgrade to unlock!")
        if st.button("💎 Upgrade Now", use_container_width=True, key="persona_upgrade"):
            navigate_to("premium")


# ══════════════════════════════════════════════════════════
# 📚 BOOK RECOMMENDATIONS PAGE (NEW!)
# ══════════════════════════════════════════════════════════
def render_books():
    if st.button("← Back to Chat", key="books_back"):
        navigate_to("chat")
    
    st.markdown('<h1 class="yumea-page-title">📚 Book Recommendations</h1>', unsafe_allow_html=True)
    st.markdown('<p class="yumea-page-desc">Curated books based on your interests.</p>', unsafe_allow_html=True)
    
    # Get books based on user memory
    memory = load_user_memory(st.session_state.user_email)
    topics = memory.get("topics_discussed", [])
    
    all_books = []
    if topics:
        for topic in topics:
            books = BOOK_RECOMMENDATIONS.get(topic, [])
            all_books.extend(books)
    
    if not all_books:
        all_books = BOOK_RECOMMENDATIONS["default"] + BOOK_RECOMMENDATIONS["wisdom"] + BOOK_RECOMMENDATIONS["life"]
    
    # Remove duplicates
    seen = set()
    unique_books = []
    for book in all_books:
        if book["title"] not in seen:
            seen.add(book["title"])
            unique_books.append(book)
    
    for book in unique_books[:9]:
        st.markdown(
            '<div class="yumea-feature-card">'
            '<div style="font-size:16px;font-weight:700;color:#fff;">📖 ' + book["title"] + '</div>'
            '<div style="font-size:13px;color:#a78bfa;margin:4px 0;">by ' + book["author"] + '</div>'
            '<div style="font-size:12px;color:#94a3b8;">' + book["topic"] + '</div>'
            '</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════
# 🎓 WISDOM COURSES PAGE (NEW!)
# ══════════════════════════════════════════════════════════
def render_courses():
    if st.button("← Back to Chat", key="courses_back"):
        navigate_to("chat")
    
    st.markdown('<h1 class="yumea-page-title">🎓 Wisdom Courses</h1>', unsafe_allow_html=True)
    st.markdown('<p class="yumea-page-desc">Structured daily wisdom journeys.</p>', unsafe_allow_html=True)
    
    active_course = st.session_state.get("active_course")
    
    if active_course:
        # Show active course progress
        course = None
        for c in WISDOM_COURSES:
            if c["id"] == active_course:
                course = c
                break
        
        if course:
            progress = st.session_state.get("course_progress", {})
            current_day = progress.get(active_course, 0)
            
            st.markdown(
                '<div class="yumea-feature-card">'
                '<div style="font-size:18px;font-weight:700;color:#fff;">📖 ' + course["title"] + '</div>'
                '<div style="font-size:13px;color:#a78bfa;">Day ' + str(current_day + 1) + ' of ' + str(course["days"]) + '</div>'
                '</div>',
                unsafe_allow_html=True
            )
            
            if current_day < course["days"]:
                topic = course["daily_topics"][current_day]
                st.markdown('<div style="color:#e2e8f0;font-size:15px;margin:16px 0;"><strong>Today\'s Topic:</strong> ' + topic + '</div>', unsafe_allow_html=True)
                
                if st.button("🎧 Get Today's Wisdom", type="primary", use_container_width=True, key="course_wisdom"):
                    with st.spinner("Channeling wisdom..."):
                        insight = generate_wisdom_insight(course["source"], "Hinglish", st.session_state.ai_model)
                        if insight:
                            st.markdown('<div class="yumea-source-card"><div class="yumea-source-text">' + md_to_html(insight) + '</div><div class="yumea-source-attr">— ' + course["source"] + ' · Day ' + str(current_day + 1) + '</div></div>', unsafe_allow_html=True)
                
                if st.button("✅ Complete Today's Lesson", use_container_width=True, key="course_complete"):
                    progress[active_course] = current_day + 1
                    st.session_state.course_progress = progress
                    if current_day + 1 >= course["days"]:
                        st.balloons()
                        st.success("🎉 Course completed! You've finished " + course["title"] + "!")
                        st.session_state.active_course = None
                    else:
                        st.success("✅ Day " + str(current_day + 1) + " completed! See you tomorrow 🌙")
                    st.rerun()
            else:
                st.success("🎉 You've completed this course!")
                if st.button("Start Another Course", use_container_width=True, key="course_another"):
                    st.session_state.active_course = None
                    st.rerun()
    else:
        # Show available courses
        for course in WISDOM_COURSES:
            progress = st.session_state.get("course_progress", {})
            completed_days = progress.get(course["id"], 0)
            status = "✅ Completed" if completed_days >= course["days"] else ("📖 " + str(completed_days) + "/" + str(course["days"]) + " days" if completed_days > 0 else "🆕 New")
            
            st.markdown(
                '<div class="yumea-feature-card">'
                '<div style="display:flex;justify-content:space-between;align-items:center;">'
                '<div style="font-size:16px;font-weight:700;color:#fff;">' + course["title"] + '</div>'
                '<div style="font-size:11px;color:#a78bfa;">' + status + '</div>'
                '</div>'
                '<div style="font-size:13px;color:#94a3b8;margin-top:6px;">' + course["description"] + '</div>'
                '</div>',
                unsafe_allow_html=True
            )
            
            if completed_days < course["days"]:
                if st.button("Start " + course["title"], use_container_width=True, key="start_" + course["id"]):
                    st.session_state.active_course = course["id"]
                    st.rerun()


# ══════════════════════════════════════════════════════════
# OTHER PAGES (Premium, Payment, Reviews, Listen)
# ══════════════════════════════════════════════════════════

def render_premium():
    if st.button("← Back to Chat", key="premium_back"):
        navigate_to("chat")
    st.markdown('<h1 class="yumea-page-title">💎 Upgrade</h1>', unsafe_allow_html=True)
    st.markdown('<div class="yumea-plan-card"><div style="font-size:14px;color:#8b5cf6;font-weight:600;">PREMIUM LITE</div><div class="yumea-plan-price">₹69 <span>/ month</span></div><div style="margin:16px 0;"><div class="yumea-plan-feature"><span class="check">✓</span> 150 messages/day</div><div class="yumea-plan-feature"><span class="check">✓</span> 2,000 words/msg</div><div class="yumea-plan-feature"><span class="check">✓</span> All 3 modes + Custom Persona</div><div class="yumea-plan-feature"><span class="check">✓</span> Emotional Analytics</div></div></div>', unsafe_allow_html=True)
    if st.button("Choose Lite", use_container_width=True, key="buy_lite", type="primary"):
        st.session_state.selected_plan = "premium_lite"
        st.session_state.payment_done = False
        navigate_to("payment")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="yumea-plan-card pro"><div style="font-size:14px;color:#fbbf24;font-weight:600;">PREMIUM PRO ⭐</div><div class="yumea-plan-price">₹199 <span>/ month</span></div><div style="margin:16px 0;"><div class="yumea-plan-feature"><span class="check">✓</span> 500 messages/day</div><div class="yumea-plan-feature"><span class="check">✓</span> 5,000 words/msg</div><div class="yumea-plan-feature"><span class="check">✓</span> Everything in Lite + Priority AI</div><div class="yumea-plan-feature"><span class="check">✓</span> Wisdom Courses</div></div></div>', unsafe_allow_html=True)
    if st.button("Choose Pro", use_container_width=True, key="buy_pro", type="primary"):
        st.session_state.selected_plan = "premium_pro"
        st.session_state.payment_done = False
        navigate_to("payment")


def render_payment():
    plan = st.session_state.get("selected_plan", "premium_lite")
    plan_info = PLANS.get(plan, PLANS["premium_lite"])
    if not st.session_state.payment_done:
        st.session_state.payment_done = True
        st.session_state.user_plan = plan
        update_user_plan(st.session_state.user_email, plan)
    st.markdown('<div style="text-align:center;padding-top:80px;"><div style="font-size:64px;">✅</div><h1 class="yumea-page-title" style="text-align:center;">Payment Successful!</h1><p style="color:#94a3b8;">Now on <strong style="color:#8b5cf6;">' + plan_info["name"] + '</strong></p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("← Back to Chat", use_container_width=True, key="pay_back", type="primary"):
            navigate_to("chat")


def render_reviews():
    if st.button("← Back to Chat", key="rev_back"):
        navigate_to("chat")
    st.markdown('<h1 class="yumea-page-title">⭐ Rate Yumea</h1>', unsafe_allow_html=True)
    rating = st.slider("Rating", 1, 5, 5, key="rev_rating")
    st.markdown('<div style="text-align:center;font-size:32px;letter-spacing:6px;margin:12px 0;">' + "⭐" * rating + '</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        rev_name = st.text_input("Name", value=st.session_state.user_name, key="rev_name")
    with c2:
        rev_email = st.text_input("Email", value=st.session_state.user_email, key="rev_email")
    liked = st.text_area("What did you like?", key="rev_liked", height=80)
    improve = st.text_area("What to improve?", key="rev_improve", height=80)
    if st.button("Submit Review", type="primary", use_container_width=True, key="rev_submit"):
        with st.spinner("Sending..."):
            success, msg = send_review_email(rev_name, rev_email, rating, liked, improve, "")
            if success:
                st.balloons()
                st.markdown('<div class="yumea-success">✅ Thank you! 🌙</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="yumea-auth-error">' + msg + '</div>', unsafe_allow_html=True)


def render_listen():
    if st.button("← Back to Chat", key="listen_back_top"):
        navigate_to("chat")
    st.markdown('<h1 class="yumea-page-title">🎧 Listen to Source</h1>', unsafe_allow_html=True)
    source = st.selectbox("Source", WISDOM_SOURCES, key="listen_source_sel")
    lang = st.selectbox("Language", ["Hinglish", "Hindi", "English"], key="listen_lang_sel")
    
    if st.button("🎧 Get Wisdom", type="primary", use_container_width=True, key="listen_get"):
        with st.spinner("Channeling wisdom..."):
            insight = generate_wisdom_insight(source, lang, st.session_state.ai_model)
            if insight:
                st.session_state.listen_text = insight
                st.session_state.listen_source_name = source
                if "listen_history" not in st.session_state:
                    st.session_state.listen_history = []
                st.session_state.listen_history.append({"text": insight, "source": source})
                if EDGE_TTS_AVAILABLE:
                    voice = "hi-IN-SwaraNeural" if lang in ("Hindi", "Hinglish") else "en-US-AvaNeural"
                    try:
                        st.session_state.listen_audio = asyncio.run(generate_tts_audio(insight, voice))
                    except:
                        st.session_state.listen_audio = None
                st.rerun()
    
    if st.session_state.listen_text:
        src_name = st.session_state.listen_source_name or source
        st.markdown('<div class="yumea-source-card"><div class="yumea-source-text">' + md_to_html(st.session_state.listen_text) + '</div><div class="yumea-source-attr">— ' + src_name + '</div></div>', unsafe_allow_html=True)
        if st.session_state.listen_audio:
            try:
                with open(st.session_state.listen_audio, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
            except:
                pass
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⬅️ Previous", use_container_width=True, key="listen_prev"):
                if len(st.session_state.listen_history) > 1:
                    st.session_state.listen_history.pop()
                    prev = st.session_state.listen_history[-1]
                    st.session_state.listen_text = prev["text"]
                    st.session_state.listen_source_name = prev["source"]
                    st.rerun()
        with c2:
            if st.button("➡️ Next", use_container_width=True, key="listen_next"):
                with st.spinner("Channeling..."):
                    insight = generate_wisdom_insight(source, lang, st.session_state.ai_model)
                    if insight:
                        st.session_state.listen_text = insight
                        st.session_state.listen_source_name = source
                        st.session_state.listen_history.append({"text": insight, "source": source})
                        st.rerun()
        with c3:
            if st.button("🔊 Replay", use_container_width=True, key="listen_replay"):
                if EDGE_TTS_AVAILABLE and st.session_state.listen_text:
                    voice = "hi-IN-SwaraNeural" if lang in ("Hindi", "Hinglish") else "en-US-AvaNeural"
                    try:
                        st.session_state.listen_audio = asyncio.run(generate_tts_audio(st.session_state.listen_text, voice))
                        st.rerun()
                    except:
                        pass


# ══════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════
def main():
    init_session_state()
    st.markdown('<style>' + GLOBAL_CSS + '</style>', unsafe_allow_html=True)

    page = st.session_state.current_page
    is_auth = st.session_state.authenticated

    if not is_auth and page not in ("signin", "signup"):
        st.session_state.current_page = "signin"
        page = "signin"

    if is_auth and page in ("signin", "signup"):
        st.session_state.current_page = "chat"
        page = "chat"

    pages = {
        "signin": render_signin,
        "signup": render_signup,
        "chat": render_chat,
        "premium": render_premium,
        "payment": render_payment,
        "reviews": render_reviews,
        "listen": render_listen,
        "analytics": render_analytics,
        "courses": render_courses,
        "persona": render_persona,
        "books": render_books,
    }

    if page in pages:
        pages[page]()
    else:
        st.session_state.current_page = "chat"
        st.rerun()


if __name__ == "__main__":
    main()
