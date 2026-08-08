#!/usr/bin/env python3
"""
YUMEA v2 - Clean Core Build
AI That Feels 🌙
Founder: Utkarsh Verma | 2026
"""

# =========================================================
# IMPORTS
# =========================================================

import os
import json
import hashlib
import random
import time
import re
from pathlib import Path
from datetime import datetime, date

import streamlit as st

try:
    import groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="YUMEA - AI That Feels",
    page_icon="🌙",
    layout="wide"
)

# =========================================================
# SECRETS
# =========================================================

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
ADMIN_PASSWORD_HASH = st.secrets.get("ADMIN_PASSWORD_HASH", "")

# =========================================================
# STORAGE PATHS
# =========================================================

USERS_FILE = "users.json"
CHAT_DIR = Path("chats")
CHAT_DIR.mkdir(exist_ok=True)

# =========================================================
# CONSTANTS
# =========================================================

ADMIN_USERNAME = "yumea_ai"

PLANS = {
    "free": {"name": "Free", "messages": 30, "words": 1000},
    "premium_lite": {"name": "Premium Lite", "messages": 150, "words": 3000},
    "premium_pro": {"name": "Premium Pro", "messages": 500, "words": 5000},
    "admin": {"name": "Admin", "messages": 999999, "words": 999999}
}

WISDOM_SOURCES = [
    "Osho",
    "Buddha",
    "Krishna (Bhagavad Gita)",
    "Bible",
    "Quran",
    "Socrates",
    "Plato",
    "Aristotle",
    "Confucius",
    "René Descartes",
    "Immanuel Kant"
]

DAILY_QUOTES = [
    "“What you seek is seeking you.” — Rumi",
    "“The mind is everything.” — Buddha",
    "“Freedom is wanting what you do.” — Osho",
    "“Know yourself.” — Socrates",
]

# =========================================================
# UTILITY FUNCTIONS
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if Path(USERS_FILE).exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def load_chat(email):
    safe = re.sub(r'[^a-zA-Z0-9]', '_', email)
    path = CHAT_DIR / f"{safe}.json"
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return []


def save_chat(email, history):
    safe = re.sub(r'[^a-zA-Z0-9]', '_', email)
    path = CHAT_DIR / f"{safe}.json"
    with open(path, "w") as f:
        json.dump(history, f, indent=2)


# =========================================================
# AUTH SYSTEM
# =========================================================

def register_user(name, email, password):
    users = load_users()
    email = email.lower()

    if email in users:
        return False, "Email already exists."

    users[email] = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "plan": "free",
        "created": datetime.now().isoformat()
    }

    save_users(users)
    return True, "Account created."


def authenticate_user(username_or_email, password):
    users = load_users()
    key = username_or_email.lower()

    # Admin
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
    # =========================================================
# AI BACKEND
# =========================================================

def call_ai(messages, model="llama-3.3-70b-versatile"):
    if not GROQ_AVAILABLE or not GROQ_API_KEY:
        return "AI backend not configured."

    try:
        client = groq.Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.8,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI Error: {str(e)}"


def generate_wisdom_insight(source, language):
    theme = random.choice([
        "inner peace",
        "love",
        "fear",
        "purpose",
        "self discovery"
    ])

    prompt = f"""
You are channeling {source}.
Share a deep spiritual insight on '{theme}'.
Write in {language}.
3-5 meaningful sentences.
No markdown.
"""

    messages = [
        {"role": "system", "content": "You are a wise spiritual teacher."},
        {"role": "user", "content": prompt}
    ]

    return call_ai(messages)


# =========================================================
# SESSION STATE INIT
# =========================================================

def init_session():
    defaults = {
        "authenticated": False,
        "page": "signin",
        "user_email": "",
        "user_name": "",
        "user_plan": "free",
        "chat_history": [],
        "listen_text": None,
        "listen_source": None
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():
    with st.sidebar:

        st.markdown("## 🌙 YUMEA")

        st.markdown(f"**{st.session_state.user_name}**")
        st.markdown(f"Plan: `{PLANS[st.session_state.user_plan]['name']}`")

        st.markdown("---")

        # Daily Quote
        quote = DAILY_QUOTES[date.today().toordinal() % len(DAILY_QUOTES)]
        st.info(quote)

        # ✅ LISTEN BUTTON BETWEEN QUOTE & CHAT MODE
        if st.button("🎧 Listen to Source", use_container_width=True):
            st.session_state.page = "listen"
            st.rerun()

        st.markdown("---")

        # Chat Mode (simplified)
        st.markdown("### 💬 Chat Mode")
        st.write("Friend Mode Active")

        st.markdown("---")

        if st.button("💎 Premium"):
            st.session_state.page = "premium"
            st.rerun()

        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.page = "signin"
            st.rerun()


# =========================================================
# CHAT PAGE
# =========================================================

def render_chat():

    render_sidebar()

    st.title("Yumea 💛")

    if not st.session_state.chat_history:
        st.markdown("Start a conversation...")

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:

        plan = PLANS[st.session_state.user_plan]

        if len(user_input.split()) > plan["words"]:
            st.warning("Message too long for your plan.")
            return

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        messages = [
            {"role": "system", "content": "You are Yumea, a warm emotional AI."}
        ]

        for m in st.session_state.chat_history[-15:]:
            messages.append(m)

        with st.spinner("Thinking..."):
            response = call_ai(messages)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

        save_chat(st.session_state.user_email,
                  st.session_state.chat_history)

        st.rerun()
        # =========================================================
# SIGN IN PAGE
# =========================================================

def render_signin():

    st.title("Welcome Back 🌙")

    email = st.text_input("Email or Admin Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):

        success, user = authenticate_user(email, password)

        if success:
            st.session_state.authenticated = True
            st.session_state.user_email = user["email"]
            st.session_state.user_name = user["name"]
            st.session_state.user_plan = user.get("plan", "free")
            st.session_state.chat_history = load_chat(user["email"])
            st.session_state.page = "chat"
            st.rerun()
        else:
            st.error("Invalid credentials.")

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()


# =========================================================
# SIGN UP PAGE
# =========================================================

def render_signup():

    st.title("Create Account ✨")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):

        success, msg = register_user(name, email, password)

        if success:
            st.success(msg)
            st.session_state.page = "signin"
            st.rerun()
        else:
            st.error(msg)

    if st.button("Back to Sign In"):
        st.session_state.page = "signin"
        st.rerun()


# =========================================================
# PREMIUM PAGE (SAFE DISABLED)
# =========================================================

def render_premium():

    render_sidebar()

    st.title("Premium Plans 💎")

    st.warning("Payment system is under maintenance.")

    st.markdown("""
### Free Plan
- 30 messages/day  
- 1000 words per message  

### Premium Lite (Coming Soon)
- 150 messages/day  
- Longer responses  

### Premium Pro (Coming Soon)
- 500 messages/day  
- Priority AI  
""")

    if st.button("Back to Chat"):
        st.session_state.page = "chat"
        st.rerun()


# =========================================================
# PREMIUM LISTEN PAGE (UPGRADED)
# =========================================================

def render_listen():

    render_sidebar()

    st.markdown(
        """
        <div style='text-align:center;margin-top:20px'>
        <h1 style='font-size:36px;color:white'>🎧 Enter Wisdom Mode</h1>
        <p style='color:#a78bfa'>Slow down. Let ancient voices speak.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        source = st.selectbox("Wisdom Source", WISDOM_SOURCES)

    with col2:
        language = st.selectbox("Language", ["English", "Hindi", "Hinglish"])

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✨ Channel Wisdom", use_container_width=True):

        with st.spinner("Channeling..."):
            insight = generate_wisdom_insight(source, language)

        st.session_state.listen_text = insight
        st.session_state.listen_source = source
        st.rerun()

    if st.session_state.listen_text:

        st.markdown(
            f"""
            <div style='
                background:linear-gradient(135deg,#1e1b4b,#0f0f1e);
                border-radius:25px;
                padding:40px;
                margin-top:40px;
                box-shadow:0 20px 60px rgba(139,92,246,0.3);
            '>
                <div style='
                    font-size:20px;
                    line-height:1.9;
                    font-style:italic;
                    color:#e2e8f0;
                '>
                    {st.session_state.listen_text}
                </div>
                <div style='
                    margin-top:20px;
                    text-align:right;
                    color:#8b5cf6;
                    font-weight:600;
                '>
                    — {st.session_state.listen_source}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.button("← Back to Chat"):
        st.session_state.page = "chat"
        st.rerun()


# =========================================================
# MAIN ROUTER
# =========================================================

def main():

    init_session()

    if not st.session_state.authenticated:
        if st.session_state.page == "signup":
            render_signup()
        else:
            render_signin()
        return

    # Authenticated Routes
    if st.session_state.page == "chat":
        render_chat()
    elif st.session_state.page == "premium":
        render_premium()
    elif st.session_state.page == "listen":
        render_listen()
    else:
        render_chat()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()
