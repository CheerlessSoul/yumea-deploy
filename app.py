"""
YUMEA - AI That Feels by Selvotex
Founder: Utkarsh Verma | Year: 2026
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

st.set_page_config(page_title="YUMEA", page_icon="🌙", layout="wide", initial_sidebar_state="expanded")

USERS_FILE = "users.json"
CHAT_DIR = Path("chats")
CHAT_DIR.mkdir(exist_ok=True)

ADMIN_USERNAME = "yumea_ai"
ADMIN_PASSWORD_HASH = hashlib.sha256("otyhey".encode()).hexdigest()

PLANS = {
    "free": {"name": "Free", "messages": 30, "words": 1000},
    "premium_lite": {"name": "Premium Lite", "messages": 150, "words": 2000},
    "premium_pro": {"name": "Premium Pro", "messages": 500, "words": 5000},
    "admin": {"name": "Admin", "messages": 999999, "words": 999999}
}

WISDOM_SOURCES = ["Osho", "Buddha", "Krishna (Bhagavad Gita)", "Bible", "Quran", "Socrates", "Plato", "Aristotle", "Confucius", "Rene Descartes", "Immanuel Kant"]

DAILY_QUOTES = [
    '"What you seek is seeking you." - Rumi',
    '"The mind is everything. What you think you become." - Buddha',
    '"Freedom is not doing what you want, freedom is wanting what you do." - Osho',
    '"The unexamined life is not worth living." - Socrates',
    '"You have power over your mind - not outside events." - Marcus Aurelius',
]

LISTEN_THEMES = ["inner peace", "love and compassion", "courage", "letting go", "self-discovery", "silence", "purpose of life", "gratitude", "mindfulness", "freedom"]

GLOBAL_CSS = """
body { background: #0a0a14 !important; color: #e2e8f0 !important; }
.stApp { background: #0a0a14 !important; }
.block-container { padding: 20px 40px !important; max-width: 100% !important; }
#MainMenu, footer { visibility: hidden; }
.stApp > header { display: none !important; }
section[data-testid="stSidebar"] { background: #0d0d1f !important; }
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.yumea-chat-header { background: #12122a; border-bottom: 1px solid rgba(139,92,246,0.15); display: flex; align-items: center; padding: 12px 20px; gap: 12px; border-radius: 12px; margin-bottom: 16px; }
.yumea-msg-row { display: flex; margin-bottom: 12px; align-items: flex-start; }
.yumea-msg-row.user { justify-content: flex-end; }
.yumea-msg-bubble { max-width: 70%; padding: 12px 16px; border-radius: 18px; line-height: 1.55; font-size: 14.5px; word-wrap: break-word; }
.yumea-msg-bubble.user { background: linear-gradient(135deg, #6366f1, #a855f7); color: #fff; }
.yumea-msg-bubble.ai { background: rgba(30,27,75,0.95); color: #e2e8f0; border: 1px solid rgba(139,92,246,0.15); }
.yumea-msg-meta { font-size: 11px; color: #64748b; margin-top: 4px; }
.yumea-source-tag { color: #8b5cf6; font-weight: 500; }
.yumea-user-card { background: rgba(139,92,246,0.08); border: 1px solid rgba(139,92,246,0.15); border-radius: 12px; padding: 12px; margin: 12px 0; }
.yumea-daily-quote { background: rgba(139,92,246,0.06); border-radius: 12px; padding: 12px; margin: 12px 0; font-style: italic; font-size: 13px; color: #c4b5fd !important; }
.yumea-sidebar-label { font-size: 11px; font-weight: 600; color: #64748b !important; text-transform: uppercase; margin: 12px 0 6px 0; }
.yumea-page-title { font-size: 28px; font-weight: 800; color: #fff; margin-bottom: 8px; }
.yumea-success { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); color: #10b981; padding: 14px; border-radius: 12px; margin: 16px 0; }
.yumea-auth-error { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); color: #f87171; padding: 10px; border-radius: 10px; margin-bottom: 16px; }
.yumea-plan-card { background: #12122a; border: 1px solid rgba(139,92,246,0.15); border-radius: 16px; padding: 28px 24px; margin-bottom: 16px; }
.yumea-source-card { background: #12122a; border: 1px solid rgba(139,92,246,0.15); border-radius: 16px; padding: 24px; margin: 20px 0; }
.stButton > button, .stFormSubmitButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: #fff !important; border: none !important; border-radius: 10px !important; padding: 10px 16px !important; font-weight: 600 !important; }
.stTextInput input, .stTextArea textarea { background: rgba(255,255,255,0.04) !important; color: #fff !important; border: 1px solid rgba(139,92,246,0.2) !important; }
"""


@st.cache_data(show_spinner=False)
def load_image_b64(filename):
    path = Path(filename)
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def get_avatar_html(size):
    img_b64 = load_image_b64("yumea-new-user.png")
    if img_b64:
        return '<img src="data:image/png;base64,' + img_b64 + '" style="width:' + str(size) + 'px;height:' + str(size) + 'px;border-radius:50%;object-fit:cover;border:2px solid rgba(139,92,246,0.4);flex-shrink:0;">'
    return '<div style="width:' + str(size) + 'px;height:' + str(size) + 'px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;">Y</div>'


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
    crisis_words = ['suicide', 'kill myself', 'end my life', 'want to die', 'marna chahta', 'marna chahti']
    for w in crisis_words:
        if w in text_lower:
            return "crisis"
    return "normal"


def detect_gender(text, history):
    combined = text.lower()
    for msg in history[-20:]:
        if msg.get("role") == "user":
            combined += " " + msg.get("content", "").lower()
    female_markers = ['main ladki hu', 'main ladki hoon', 'i am a girl', 'main karti hu', 'mera boyfriend']
    for m in female_markers:
        if m in combined:
            return True
    return False


async def generate_tts_audio(text, voice="hi-IN-SwaraNeural"):
    if not EDGE_TTS_AVAILABLE:
        return None
    try:
        clean_text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        clean_text = re.sub(r'[*_#`]', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        if not clean_text:
            return None
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
    if lang == "Mandarin Chinese":
        return "zh-CN-XiaoyiNeural"
    if lang == "Hinglish":
        return "hi-IN-SwaraNeural"
    return "en-US-AvaNeural"


def build_system_prompt(chat_mode, selected_sources, debate_mode, user_gender):
    if user_gender:
        gender_note = " The user is FEMALE. Use warm, respectful terms. Do NOT use bhai."
    else:
        gender_note = " The user is MALE. Use friendly casual terms."
    language_rule = ""
    lang_manual = st.session_state.get("language_manual", False)
    selected_lang = st.session_state.get("selected_language", "auto")
    if lang_manual and selected_lang != "auto":
        if selected_lang == "English":
            language_rule = "CRITICAL LANGUAGE RULE - READ FIRST. YOU MUST REPLY IN 100 PERCENT PURE ENGLISH ONLY. FORBIDDEN: Hindi words (yaar, bhai, achha, hoon, hai, kya), Sanskrit words (karmanye, yoga karmasu, dharma, namaste), Hinglish phrases, untranslated Sanskrit quotes. MANDATORY: Use ONLY English words. If quoting scriptures, give ENGLISH TRANSLATION ONLY. Use friend or buddy instead of yaar. Say I think, I feel in pure English. Examples: Hey I hear you, that sounds tough. Krishna teaches us to focus on actions not results. IF YOU USE ANY HINDI OR SANSKRIT WORD YOU HAVE FAILED. THIS RULE OVERRIDES EVERYTHING.\n\n"
        elif selected_lang == "Hindi":
            language_rule = "CRITICAL LANGUAGE RULE. YOU MUST REPLY IN 100 PERCENT PURE HINDI DEVANAGARI SCRIPT ONLY. FORBIDDEN: NO English words, NO Roman script, NO Hinglish. Write EVERYTHING in Devanagari. THIS RULE OVERRIDES EVERYTHING.\n\n"
        elif selected_lang == "Hinglish":
            language_rule = "CRITICAL LANGUAGE RULE. YOU MUST REPLY IN HINGLISH (Hindi in English letters). Example: Arey yaar tension mat le sab theek hoga. FORBIDDEN: NO Devanagari, NO pure English. THIS RULE OVERRIDES EVERYTHING.\n\n"
        elif selected_lang == "Mandarin Chinese":
            language_rule = "CRITICAL LANGUAGE RULE. YOU MUST REPLY IN 100 PERCENT SIMPLIFIED CHINESE ONLY. FORBIDDEN: NO English, NO Hindi. THIS RULE OVERRIDES EVERYTHING.\n\n"
    else:
        language_rule = "LANGUAGE AUTO-DETECT. Detect user language and reply in SAME language. NEVER mix languages.\n\n"
    yumea_identity = "You are YUMEA - AI That Feels, by Selvotex India, founded by Utkarsh Verma in 2026. You are a FEMALE AI companion (she/her). Sound like a REAL modern educated young woman. NOT a textbook. Keep casual messages SHORT (1-3 sentences). Use emojis naturally. Be direct, warm, genuine. NEVER start with 'Main karti hoon' or 'Mujhe lagta hai'. USER GENDER:" + gender_note + " PURPOSE: Emotional support, spiritual wisdom, life reflection. NOT for coding or homework. SPIRITUAL FIGURES: Use respectful terms like Osho said, Buddha taught. When quoting scriptures ALWAYS use translation in active language. NEVER use Sanskrit transliteration unless language is Hindi or Hinglish.\n"
    mode_instructions = ""
    if chat_mode == "professional":
        if selected_sources:
            sources_str = ", ".join(selected_sources)
        else:
            sources_str = "Osho, Buddha, Krishna, Bible, Socrates"
        mode_instructions = "\n\nPROFESSIONAL MODE. ONLY quote: " + sources_str + ". NEVER fabricate quotes. Paraphrase when unsure. For DEEP questions use structured sections: I hear you / Wisdom / For you."
    elif chat_mode == "freestyle":
        mode_instructions = "\n\nFREESTYLE MODE. Access ALL 11 traditions. Pick 1-3 most relevant. Blend naturally. End deep responses with Wisdom from [sources]. NEVER fabricate quotes."
    else:
        mode_instructions = "\n\nFRIEND MODE. Casual, warm, natural. No citations. Short. Emojis natural."
    debate_note = ""
    if debate_mode:
        debate_note = "\n\nDEBATE: Challenge user views respectfully."
    crisis_note = "\n\nCRISIS: If suicide/self-harm mentioned, say I am here you are safe and share iCall 9152987821"
    final_prompt = language_rule + yumea_identity + mode_instructions + debate_note + crisis_note
    if lang_manual and selected_lang != "auto":
        final_prompt += "\n\nFINAL REMINDER: Reply ONLY in " + selected_lang + ". NO other language. NO exceptions."
    return final_prompt


def call_ai(messages, model_name="llama-3.3-70b-versatile"):
    lang_manual = st.session_state.get("language_manual", False)
    if lang_manual:
        temp = 0.5
    else:
        temp = 0.8
    if GROQ_AVAILABLE and GROQ_API_KEY:
        try:
            client = groq.Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(model=model_name, messages=messages, max_tokens=2048, temperature=temp, top_p=0.9)
            return response.choices[0].message.content
        except Exception as e:
            st.error("AI Error: " + str(e))
            return None
    return "Sorry, no AI backend available."


def generate_wisdom_insight(source, language, model_name="llama-3.3-70b-versatile"):
    theme = random.choice(LISTEN_THEMES)
    prompt = "You are channeling " + source + ". Share a profound insight on '" + theme + "'. 3-5 sentences in " + language + ". Authentic voice. No markdown."
    messages = [{"role": "system", "content": "Wise spiritual voice."}, {"role": "user", "content": prompt}]
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


def init_session_state():
    defaults = {
        "current_page": "signin", "authenticated": False, "user_email": "", "user_name": "", "user_plan": "free",
        "chat_mode": "friend", "selected_sources": ["Osho", "Buddha", "Krishna (Bhagavad Gita)", "Bible", "Socrates"],
        "ai_model": "llama-3.3-70b-versatile", "debate_mode": False, "user_is_female": False,
        "auth_error": "", "auth_success": "", "pending_suggest": "", "chat_history": [],
        "selected_plan": "premium_lite", "payment_done": False,
        "listen_text": None, "listen_source_name": None, "listen_audio": None, "listen_history": [],
        "language_manual": False, "selected_language": "auto", "tts_playing": None,
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


def process_user_message(user_input):
    user_email = st.session_state.user_email
    plan_info = PLANS.get(st.session_state.user_plan, PLANS["free"])
    word_count = len(user_input.split())
    now_time = datetime.now().strftime("%I:%M %p")
    today = date.today().isoformat()
    if word_count > plan_info["words"]:
        st.session_state.chat_history.append({"role": "user", "content": user_input, "time": now_time, "date": today})
        st.session_state.chat_history.append({"role": "assistant", "content": "Message exceeds " + str(plan_info["words"]) + " words. Upgrade for longer messages.", "time": now_time, "date": today})
        save_chat_history(user_email, st.session_state.chat_history)
        return
    msg_count = get_daily_message_count(user_email)
    if msg_count >= plan_info["messages"]:
        st.session_state.chat_history.append({"role": "assistant", "content": "Daily limit reached. Upgrade to Premium!", "time": now_time, "date": today})
        save_chat_history(user_email, st.session_state.chat_history)
        return
    st.session_state.chat_history.append({"role": "user", "content": user_input, "time": now_time, "date": today})
    if detect_gender(user_input, st.session_state.chat_history):
        st.session_state.user_is_female = True
    if detect_emotion_mode(user_input) == "crisis":
        st.session_state.chat_history.append({"role": "assistant", "content": "I'm here. You're safe.\n\nTake a deep breath...\n\n**iCall: 9152987821**", "time": now_time, "date": today, "source": "Crisis Support"})
        save_chat_history(user_email, st.session_state.chat_history)
        return
    system_prompt = build_system_prompt(st.session_state.chat_mode, st.session_state.selected_sources, st.session_state.debate_mode, st.session_state.user_is_female)
    ai_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.chat_history[-20:]:
        if m["role"] in ("user", "assistant"):
            ai_messages.append({"role": m["role"], "content": m["content"]})
    lang_manual = st.session_state.get("language_manual", False)
    selected_lang = st.session_state.get("selected_language", "auto")
    if lang_manual and selected_lang != "auto":
        reminder = {"role": "system", "content": "REMINDER: You MUST reply in " + selected_lang + " ONLY. No mixing. No Sanskrit transliteration."}
        ai_messages.append(reminder)
    start_time = time.time()
    response_text = call_ai(ai_messages, st.session_state.ai_model)
    response_time = round(time.time() - start_time, 1)
    if response_text is None:
        response_text = "Sorry, couldn't connect. Try again."
    source_tag = ""
    if st.session_state.chat_mode == "professional" and st.session_state.selected_sources:
        source_tag = random.choice(st.session_state.selected_sources)
    elif st.session_state.chat_mode == "freestyle":
        source_tag = "Freestyle"
    ai_msg = {"role": "assistant", "content": response_text.strip(), "time": now_time, "date": today, "response_time": response_time}
    if source_tag:
        ai_msg["source"] = source_tag
    st.session_state.chat_history.append(ai_msg)
    save_chat_history(user_email, st.session_state.chat_history)


def render_signin():
    logo_img = load_image_b64("yumea-logo.jpeg")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img:
            st.markdown('<img src="data:image/jpeg;base64,' + logo_img + '" style="display:block;margin:0 auto 12px;width:80px;height:80px;border-radius:50%;object-fit:cover;">', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align:center;color:#fff;font-size:28px;margin:0 0 4px 0;">Welcome to YUMEA</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#a78bfa;font-size:13px;margin-bottom:20px;">Sign in to continue</p>', unsafe_allow_html=True)
        if st.session_state.get("auth_error"):
            st.markdown('<div class="yumea-auth-error">' + st.session_state.auth_error + '</div>', unsafe_allow_html=True)
            st.session_state.auth_error = ""
        if st.session_state.get("auth_success"):
            st.markdown('<div class="yumea-success">' + st.session_state.auth_success + '</div>', unsafe_allow_html=True)
            st.session_state.auth_success = ""
        with st.form("signin_form"):
            email = st.text_input("Email or Admin Username", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
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
        if st.button("Create New Account", use_container_width=True):
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
        if st.button("Back to Sign In", use_container_width=True):
            navigate_to("signin")


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
    with st.sidebar:
        st.markdown('<div style="font-size:22px;font-weight:800;color:#fff;">YUMEA</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:11px;color:#8b5cf6;margin-top:-4px;">AI That Feels</div>', unsafe_allow_html=True)
        st.markdown('<hr style="border-color:rgba(139,92,246,0.1);margin:12px 0;">', unsafe_allow_html=True)
        plan_info = PLANS.get(user_plan, PLANS["free"])
        msg_count = get_daily_message_count(user_email)
        msg_limit = plan_info["messages"]
        if user_plan == "admin":
            counter_text = "UNLIMITED"
        else:
            counter_text = str(msg_count) + " / " + str(msg_limit) + " messages today"
        st.markdown('<div class="yumea-user-card"><div style="font-size:14px;font-weight:600;color:#fff;">' + user_name + '</div><div style="font-size:11px;color:#a78bfa;">' + plan_info["name"] + '</div><div style="font-size:12px;color:#94a3b8;">' + counter_text + '</div></div>', unsafe_allow_html=True)
        daily_quote = DAILY_QUOTES[date.today().toordinal() % len(DAILY_QUOTES)]
        st.markdown('<div class="yumea-daily-quote">' + daily_quote + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="yumea-sidebar-label">Chat Mode</div>', unsafe_allow_html=True)
        mode_options = ["friend", "professional", "freestyle"]
        mode_labels = {"friend": "Friend", "professional": "Professional", "freestyle": "Freestyle"}
        if st.session_state.chat_mode in mode_options:
            current_idx = mode_options.index(st.session_state.chat_mode)
        else:
            current_idx = 0
        new_mode = st.radio("Chat Mode", mode_options, index=current_idx, label_visibility="collapsed", format_func=lambda x: mode_labels.get(x, x), key="chat_mode_radio")
        if new_mode != st.session_state.chat_mode:
            st.session_state.chat_mode = new_mode
            st.rerun()
        if st.session_state.chat_mode == "professional":
            st.markdown('<div class="yumea-sidebar-label">Wisdom Sources</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="yumea-sidebar-label">AI Model</div>', unsafe_allow_html=True)
        models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        if st.session_state.ai_model in models:
            model_idx = models.index(st.session_state.ai_model)
        else:
            model_idx = 0
        new_model = st.selectbox("AI Model", models, index=model_idx, label_visibility="collapsed", key="ai_model_sel")
        if new_model != st.session_state.ai_model:
            st.session_state.ai_model = new_model
            st.rerun()
        st.markdown('<div class="yumea-sidebar-label">Debate Mode</div>', unsafe_allow_html=True)
        new_debate = st.toggle("Challenge my thinking", value=st.session_state.debate_mode, key="debate_toggle")
        if new_debate != st.session_state.debate_mode:
            st.session_state.debate_mode = new_debate
            st.rerun()
        st.markdown('<div class="yumea-sidebar-label">Language</div>', unsafe_allow_html=True)
        lang_manual = st.toggle("Manual language select", value=st.session_state.language_manual, key="lang_toggle")
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
            if current_lang in lang_options:
                lang_idx = lang_options.index(current_lang)
            else:
                lang_idx = 1
            new_lang = st.selectbox("Reply Language", lang_options, index=lang_idx, key="lang_select")
            if new_lang != st.session_state.selected_language:
                st.session_state.selected_language = new_lang
                st.rerun()
        else:
            st.markdown('<div style="font-size:11px;color:#94a3b8;font-style:italic;">Auto-detecting from your messages</div>', unsafe_allow_html=True)
        st.markdown('<div class="yumea-sidebar-label">Menu</div>', unsafe_allow_html=True)
        if st.button("Buy Premium", use_container_width=True, key="btn_premium"):
            st.session_state.payment_done = False
            navigate_to("premium")
        if st.button("Rate Yumea", use_container_width=True, key="btn_reviews"):
            navigate_to("reviews")
        if st.button("Listen to Source", use_container_width=True, key="btn_listen"):
            navigate_to("listen")
        if st.button("Clear Chat", use_container_width=True, key="btn_clear"):
            st.session_state.chat_history = []
            save_chat_history(user_email, [])
            st.rerun()
        if st.button("Logout", use_container_width=True, key="btn_logout"):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.session_state.user_plan = "free"
            st.session_state.chat_history = []
            navigate_to("signin")
    lang_indicator = ""
    if st.session_state.language_manual and st.session_state.selected_language != "auto":
        lang_indicator = ' <span style="background:rgba(139,92,246,0.2);color:#c4b5fd;padding:3px 10px;border-radius:12px;font-size:11px;">' + st.session_state.selected_language + '</span>'
    st.markdown('<div class="yumea-chat-header">' + get_avatar_html(44) + '<div style="flex:1;"><div style="font-size:16px;font-weight:700;color:#fff;">Yumea <span style="color:#8b5cf6;">✓</span>' + lang_indicator + '</div><div style="font-size:12px;color:#10b981;">online · always here</div></div></div>', unsafe_allow_html=True)
    if not history:
        st.markdown('<div style="text-align:center;padding:40px 20px;">' + get_avatar_html(120) + '<div style="font-size:28px;font-weight:700;color:#fff;margin-top:20px;">Hi, I am Yumea</div><div style="font-size:15px;color:#94a3b8;margin-bottom:32px;">Your emotional companion.</div></div>', unsafe_allow_html=True)
    else:
        for idx, msg in enumerate(history):
            if msg["role"] == "user":
                safe = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                st.markdown('<div class="yumea-msg-row user"><div class="yumea-msg-bubble user">' + safe + '</div></div>', unsafe_allow_html=True)
            else:
                content_html = md_to_html(msg["content"])
                if msg.get("source"):
                    src = ' · <span class="yumea-source-tag">' + msg["source"] + '</span>'
                else:
                    src = ""
                if msg.get("response_time"):
                    rt = ' · ' + str(msg["response_time"]) + 's'
                else:
                    rt = ""
                ts = msg.get("time", "")
                st.markdown('<div class="yumea-msg-row ai">' + get_avatar_html(32) + '<div style="flex:1;max-width:70%;"><div class="yumea-msg-bubble ai">' + content_html + '</div><div class="yumea-msg-meta">' + ts + rt + src + '</div></div></div>', unsafe_allow_html=True)
                if EDGE_TTS_AVAILABLE:
                    tts_col1, tts_col2 = st.columns([1, 10])
                    with tts_col1:
                        if st.button("🔊", key="tts_" + str(idx)):
                            st.session_state.tts_playing = idx
                    with tts_col2:
                        if st.session_state.get("tts_playing") == idx:
                            with st.spinner("Loading audio..."):
                                voice = get_tts_voice_for_language()
                                audio_path = asyncio.run(generate_tts_audio(msg["content"], voice))
                                if audio_path:
                                    with open(audio_path, "rb") as f:
                                        st.audio(f.read(), format="audio/mp3")
                                    try:
                                        os.unlink(audio_path)
                                    except:
                                        pass
    if not history:
        st.markdown('<div style="max-width:600px;margin:20px auto;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Hey, Yumea", use_container_width=True, key="sug_1"):
                st.session_state.pending_suggest = "Hey, Yumea"
                st.rerun()
            if st.button("Mujhe motivation chahiye", use_container_width=True, key="sug_3"):
                st.session_state.pending_suggest = "Mujhe motivation chahiye"
                st.rerun()
        with col2:
            if st.button("What is inner peace?", use_container_width=True, key="sug_2"):
                st.session_state.pending_suggest = "What is inner peace?"
                st.rerun()
            if st.button("What is the meaning of life?", use_container_width=True, key="sug_4"):
                st.session_state.pending_suggest = "What is the meaning of life?"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    mic_text = None
    if MIC_RECORDER_AVAILABLE:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            mic_audio = mic_recorder(start_prompt="Speak", stop_prompt="Stop", just_once=True, use_container_width=True, key="mic_recorder_chat")
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


def render_premium():
    if st.button("Back to Chat", key="premium_back"):
        navigate_to("chat")
    st.markdown('<h1 class="yumea-page-title">Upgrade</h1>', unsafe_allow_html=True)
    st.markdown('<div class="yumea-plan-card"><div style="font-size:14px;color:#8b5cf6;font-weight:600;">PREMIUM LITE</div><div style="font-size:36px;font-weight:800;color:#fff;margin:8px 0;">Rs 69 <span style="font-size:14px;color:#64748b;">/ month</span></div><div style="font-size:13.5px;color:#94a3b8;">✓ 150 messages/day<br>✓ 2000 words/msg<br>✓ All 3 modes</div></div>', unsafe_allow_html=True)
    if st.button("Choose Lite", use_container_width=True, key="buy_lite", type="primary"):
        st.session_state.selected_plan = "premium_lite"
        st.session_state.payment_done = False
        navigate_to("payment")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="yumea-plan-card"><div style="font-size:14px;color:#fbbf24;font-weight:600;">PREMIUM PRO</div><div style="font-size:36px;font-weight:800;color:#fff;margin:8px 0;">Rs 199 <span style="font-size:14px;color:#64748b;">/ month</span></div><div style="font-size:13.5px;color:#94a3b8;">✓ 500 messages/day<br>✓ 5000 words/msg<br>✓ Priority AI</div></div>', unsafe_allow_html=True)
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
        if st.button("Back to Chat", use_container_width=True, key="pay_back", type="primary"):
            navigate_to("chat")


def render_reviews():
    if st.button("Back to Chat", key="rev_back"):
        navigate_to("chat")
    st.markdown('<h1 class="yumea-page-title">Rate Yumea</h1>', unsafe_allow_html=True)
    rating = st.slider("Rating", 1, 5, 5, key="rev_rating")
    st.markdown('<div style="text-align:center;font-size:32px;letter-spacing:6px;margin:12px 0;">' + ("⭐" * rating) + '</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        rev_name = st.text_input("Name", value=st.session_state.user_name, key="rev_name")
    with c2:
        rev_email = st.text_input("Email", value=st.session_state.user_email, key="rev_email")
    liked = st.text_area("What did you like?", key="rev_liked", height=80)
    improve = st.text_area("What to improve?", key="rev_improve", height=80)
    thoughts = st.text_area("Overall thoughts", key="rev_thoughts", height=80)
    if st.button("Submit Review", type="primary", use_container_width=True, key="rev_submit"):
        with st.spinner("Sending..."):
            success, msg = send_review_email(rev_name, rev_email, rating, liked, improve, thoughts)
            if success:
                st.balloons()
                st.markdown('<div class="yumea-success">Thank you!</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="yumea-auth-error">' + msg + '</div>', unsafe_allow_html=True)


def render_listen():
    if st.button("Back to Chat", key="listen_back_top"):
        navigate_to("chat")
    st.markdown('<h1 class="yumea-page-title">Listen to Source</h1>', unsafe_allow_html=True)
    source = st.selectbox("Wisdom Source", WISDOM_SOURCES, key="listen_source_sel")
    lang = st.selectbox("Language", ["Hinglish", "Hindi", "English"], key="listen_lang_sel")
    if st.button("Get Wisdom", type="primary", use_container_width=True, key="listen_get"):
        with st.spinner("Channeling wisdom..."):
            insight = generate_wisdom_insight(source, lang, st.session_state.ai_model)
            if insight:
                st.session_state.listen_text = insight
                st.session_state.listen_source_name = source
                if "listen_history" not in st.session_state:
                    st.session_state.listen_history = []
                st.session_state.listen_history.append({"text": insight, "source": source})
                if EDGE_TTS_AVAILABLE:
                    if lang in ("Hindi", "Hinglish"):
                        voice = "hi-IN-SwaraNeural"
                    else:
                        voice = "en-IN-NeerjaNeural"
                    try:
                        st.session_state.listen_audio = asyncio.run(generate_tts_audio(insight, voice))
                    except:
                        st.session_state.listen_audio = None
                st.rerun()
    if st.session_state.listen_text:
        src_name = st.session_state.listen_source_name or source
        st.markdown('<div class="yumea-source-card"><div style="font-size:16px;line-height:1.7;color:#e2e8f0;font-style:italic;margin:16px 0;">' + md_to_html(st.session_state.listen_text) + '</div><div style="font-size:13px;color:#8b5cf6;font-weight:600;">— ' + src_name + '</div></div>', unsafe_allow_html=True)
        if st.session_state.listen_audio:
            try:
                with open(st.session_state.listen_audio, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
            except:
                pass
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Previous", use_container_width=True, key="listen_prev"):
                if len(st.session_state.listen_history) > 1:
                    st.session_state.listen_history.pop()
                    prev = st.session_state.listen_history[-1]
                    st.session_state.listen_text = prev["text"]
                    st.session_state.listen_source_name = prev["source"]
                    st.rerun()
                else:
                    st.warning("No previous wisdom.")
        with c2:
            if st.button("Next", use_container_width=True, key="listen_next"):
                with st.spinner("Channeling..."):
                    insight = generate_wisdom_insight(source, lang, st.session_state.ai_model)
                    if insight:
                        st.session_state.listen_text = insight
                        st.session_state.listen_source_name = source
                        st.session_state.listen_history.append({"text": insight, "source": source})
                        st.rerun()
        with c3:
            if st.button("Replay", use_container_width=True, key="listen_replay"):
                if EDGE_TTS_AVAILABLE and st.session_state.listen_text:
                    if lang in ("Hindi", "Hinglish"):
                        voice = "hi-IN-SwaraNeural"
                    else:
                        voice = "en-IN-NeerjaNeural"
                    try:
                        st.session_state.listen_audio = asyncio.run(generate_tts_audio(st.session_state.listen_text, voice))
                        st.rerun()
                    except:
                        pass


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
