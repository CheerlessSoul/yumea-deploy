#!/usr/bin/env python3
"""
YUMEA v2 - Strong UI Production Build
AI That Feels 🌙 | Founder: Utkarsh Verma | Selvotex 2026
"""

# =========================================================
# IMPORTS & SETUP
# =========================================================

import os
import json
import hashlib
import re
import time
import random
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, date

import streamlit as st

try:
    import groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except:
    EDGE_TTS_AVAILABLE = False

st.set_page_config(
    page_title="YUMEA - AI That Feels",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

USERS_FILE = "users.json"
CHAT_DIR = Path("chats")
CHAT_DIR.mkdir(exist_ok=True)

ADMIN_USERNAME = "yumea_ai"
ADMIN_PASSWORD_HASH = st.secrets.get("ADMIN_PASSWORD_HASH", "")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

PLANS = {
    "free": {"name": "Free", "messages": 30, "words": 1000},
    "premium_lite": {"name": "Premium Lite", "messages": 150, "words": 2500},
    "premium_pro": {"name": "Premium Pro", "messages": 500, "words": 5500},
    "admin": {"name": "Admin", "messages": 999999, "words": 999999}
}

WISDOM_SOURCES = [
    "Osho","Buddha","Krishna (Bhagavad Gita)","Bible","Quran",
    "Socrates","Plato","Aristotle","Confucius",
    "René Descartes","Immanuel Kant"
]

DAILY_QUOTES = [
    '"The only way to find yourself is to lose yourself." — Gandhi',
    '"What you seek is seeking you." — Rumi',
    '"The mind is everything. What you think you become." — Buddha',
    '"Be still and know." — Psalm 46:10',
    '"Freedom is not doing what you want, freedom is wanting what you do." — Osho',
    '"The unexamined life is not worth living." — Socrates',
    '"Knowing yourself is the beginning of all wisdom." — Aristotle',
    '"You have power over your mind — not outside events." — Marcus Aurelius',
]

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
.yumea-msg-meta { font-size: 11px; color: #64748b; margin-top: 4px; padding: 0 4px; }
.yumea-source-tag { color: #8b5cf6; font-weight: 500; }

.yumea-empty-state { text-align: center; padding: 40px 20px; }
.yumea-empty-title { font-size: 28px; font-weight: 700; color: #fff; margin-bottom: 8px; }
.yumea-empty-sub { font-size: 15px; color: #94a3b8; margin-bottom: 32px; }

.yumea-user-card { background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 12px; padding: 12px; margin: 12px 0; }
.yumea-user-card-name { font-size: 14px; font-weight: 600; color: #fff !important; }
.yumea-user-card-plan { font-size: 11px; color: #a78bfa !important; display: inline-block; padding: 2px 8px; background: rgba(139, 92, 246, 0.15); border-radius: 10px; margin: 4px 0; }
.yumea-user-card-counter { font-size: 12px; color: #94a3b8 !important; }
.yumea-daily-quote { background: rgba(139, 92, 246, 0.06); border: 1px solid rgba(139, 92, 246, 0.1); border-radius: 12px; padding: 12px; margin: 12px 0; font-family: 'Spectral', serif; font-style: italic; font-size: 13px; color: #c4b5fd !important; line-height: 1.5; }
.yumea-sidebar-label { font-size: 11px; font-weight: 600; color: #64748b !important; text-transform: uppercase; letter-spacing: 0.8px; margin: 12px 0 6px 0; }

.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: #fff !important; border: none !important; border-radius: 10px !important; padding: 10px 16px !important; font-weight: 600 !important; }
.stButton > button:hover { background: linear-gradient(135deg, #7c7ff7, #9d6ffa) !important; }
button[kind="primary"] { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: #fff !important; border: none !important; }
.stTextInput input, .stTextArea textarea { background: rgba(255, 255, 255, 0.04) !important; color: #fff !important; border: 1px solid rgba(139, 92, 246, 0.2) !important; }

.yumea-auth-error { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); color: #f87171; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }
.yumea-success { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #10b981; padding: 14px 18px; border-radius: 12px; font-size: 14px; margin: 16px 0; }

/* LISTEN PAGE PREMIUM STYLE */
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
.listen-nav-btns button { background: rgba(139,92,246,0.12) !important; border: 1px solid rgba(139,92,246,0.3) !important; }
"""

# =========================================================
# AUTH SYSTEM
# =========================================================

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_users():
    if Path(USERS_FILE).exists():
        try:
            with open(USERS_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def register_user(name,email,pwd):
    users=load_users()
    em=email.lower().strip()
    if em in users:
        return False,"Email exists."
    if len(pwd)<4:
        return False,"Password 4+ chars."
    users[em]={
        "name":name.strip(),
        "email":em,
        "password_hash":hash_password(pwd),
        "plan":"free",
        "created":datetime.now().isoformat()
    }
    save_users(users)
    return True,"Account created!"

def authenticate_user(key,pwd):
    users=load_users()
    key=key.lower().strip()
    if key==ADMIN_USERNAME:
        if hash_password(pwd)==ADMIN_PASSWORD_HASH:
            return True,{"name":"Admin","email":ADMIN_USERNAME,"plan":"admin"}
        return False,None
    if key not in users:
        return False,None
    if users[key]["password_hash"]==hash_password(pwd):
        return True,users[key]
    return False,None

def load_chat(email):
    saf=re.sub(r'[^a-zA-Z0-9]','_',email)
    p=CHAT_DIR/f"{saf}.json"
    if p.exists():
        try:
            with open(p,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_chat(email,hist):
    saf=re.sub(r'[^a-zA-Z0-9]','_',email)
    p=CHAT_DIR/f"{saf}.json"
    with open(p,"w",encoding="utf-8") as f:
        json.dump(hist,f,indent=2,ensure_ascii=False)

def get_daily_count(email):
    h=load_chat(email)
    today=date.today().isoformat()
    return sum(1 for m in h if m.get("role")=="user" and m.get("date")==today)

def detect_emotion(text):
    bad=['suicide','kill myself','want to die','marna chahta','marna chahti','jaan dena']
    t=text.lower()
    for w in bad:
        if w in t:
            return "crisis"
    return "normal"

def md_to_html(text):
    if not text:
        return ""
    html=text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    html=re.sub(r'^### (.+)$',r'<h4 style="color:#d4b3ff;font-size:15px;font-weight:700;margin:12px 0 6px;">\1</h4>',html,flags=re.MULTILINE)
    html=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',html)
    html=re.sub(r'\*(.+?)\*',r'<em>\1</em>',html)
    html=html.replace("\n\n","</p><p>")
    html=html.replace("\n","<br>")
    html="<p>"+html+"</p>"
    html=html.replace("<p></p>","")
    return html

def init_session():
    defaults={
        "page":"signin",
        "authenticated":False,
        "user_email":"",
        "user_name":"",
        "user_plan":"free",
        "chat_history":[],
        "chat_mode":"friend",
        "selected_sources":["Osho","Buddha","Krishna (Bhagavad Gita)","Bible","Socrates"],
        "ai_model":"llama-3.3-70b-versatile",
        "debate_mode":False,
        "listen_text":None,
        "listen_source":None,
        "listen_audio":None,
        "listen_history":[],
        "auth_error":"",
        "auth_success":""
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

def nav(page):
    st.session_state.page=page
    st.rerun()
    # =========================================================
# AI BACKEND ENGINE
# =========================================================

def call_ai(messages,model="llama-3.3-70b-versatile"):

    st.write(f"[DEBUG] Key length: {len(GROQ_API_KEY) if GROQ_API_KEY else 0}")
    st.write(f"[DEBUG] Available: {GROQ_AVAILABLE}")

    if GROQ_AVAILABLE and GROQ_API_KEY:
        try:
            client=groq.Groq(api_key=GROQ_API_KEY)
            resp=client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2048,
                temperature=0.8,
                top_p=0.9
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"AI Error: {str(e)}"
    return "No AI backend configured."

def generate_wisdom(source,language):
    theme=random.choice([
        "inner peace","love","fear","purpose",
        "silence","strength","mindfulness"
    ])
    prompt=f"You are channeling {source}. Share profound insight on '{theme}'. 3-5 sentences in {language}. Authentic voice. No markdown."
    messages=[
        {"role":"system","content":"Wise spiritual voice."},
        {"role":"user","content":prompt}
    ]
    return call_ai(messages)

# =========================================================
# TTS VOICE SYSTEM
# =========================================================

async def generate_tts(text,voice="hi-IN-SwaraNeural"):
    if not EDGE_TTS_AVAILABLE:
        return None
    try:
        clean=re.sub(r'\*\*(.+?)\*\*',r'\1',text)
        clean=re.sub(r'[*_#`]','',clean)
        clean=re.sub(r'\s+',' ',clean).strip()

        tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".mp3")
        tmp.close()

        comm=edge_tts.Communicate(clean,voice,rate="-5%",pitch="+8Hz")
        await comm.save(tmp.name)
        return tmp.name
    except:
        return None

def get_voice_lang():
    lang=st.session_state.get("selected_language","auto")
    if lang in ("Hindi","Hinglish"):
        return "hi-IN-SwaraNeural"
    elif lang=="Mandarin Chinese":
        return "zh-CN-XiaoyiNeural"
    else:
        return "en-US-AvaNeural"

# =========================================================
# ADVANCED SYSTEM PROMPTS
# =========================================================

def build_system_prompt(mode,sources,debate,gender):

    gender_note=""
    if gender:
        gender_note=" User is FEMALE. Use warm respectful terms. No 'bhai'."
    else:
        gender_note=" User is MALE default. Use friendly casual terms."

    base=(
        "You are YUMEA — 'AI That Feels', created by Selvotex India, "
        "founded by Utkarsh Verma 2026. You are a FEMALE AI companion (she/her).\n\n"

        "═══ LANGUAGE RULES ═══\n"
    )

    if st.session_state.get("language_manual",False) and st.session_state.get("selected_language","auto")!="auto":
        forced=st.session_state.selected_language
        base+=(
            f"⚠️ ABSOLUTE: Reply ONLY in {forced}.\n\n"
            f"English → Pure English only.\n"
            f"Hindi → Devanagari Hindi only.\n"
            f"Hinglish → Hindi words in English letters.\n"
            f"Mandarin → Simplified Chinese only.\n\n"
        )
    else:
        base+=(
            "Auto-detect user language and reply in same.\n"
            "Never mix languages.\n\n"
        )

    base+=(
        "═══ CONVERSATION STYLE ═══\n"
        "Sound like REAL modern educated young woman.\n"
        "NOT textbook. NOT robot. NOT formal assistant.\n\n"

        "GOOD examples:\n"
        "  Hinglish: 'Arey yaar ye toh hota hai sabke saath. Chill kar 💛'\n"
        "  Hinglish: 'Ek kaam kar na thoda meditation try kar.'\n"
        "  English: 'Hey that sounds tough. Want to talk about it? 💛'\n"
        "  English: 'I get it. Sometimes life feels heavy. What's on your mind?'\n\n"

        "BAD examples (NEVER use):\n"
        "  ❌ Main karti hoon ki...\n"
        "  ❌ Main sochti hoon ki...\n"
        "  ❌ Mujhe lagta hai ki...\n"
        "These sound robotic.\n\n"

        "RULES:\n"
        "1. Never start with 'Main karti hoon ki...'\n"
        "2. Talk like Gen-Z/millennial educated Indian girl texts friends\n"
        "3. Keep responses SHORT (1-3 sentences for casual)\n"
        "4. Emojis natural but don't overdo\n"
        "5. Sound warm genuine not scripted\n"
        "6. Feminine naturally but don't force awkwardly\n\n"

        "═══ USER GENDER ═══\n"+gender_note+"\n\n"

        "═══ PURPOSE ═══\n"
        "Emotional support spiritual wisdom life reflection deep conversation.\n"
        "NOT for coding homework recipes.\n"
        "For those: Not my thing. I'm feelings-and-wisdom type 🌙\n\n"

        "═══ RESPECT FIGURES ═══\n"
        "Use plural: Osho ne kaha Buddha ne sikhaya etc."
    )

    mode_ins=""
    if mode=="professional":
        src_str=", ".join(sources) if sources else "Osho Buddha Krishna Bible Socrates"
        mode_ins=(
            f"\n\n## PROFESSIONAL MODE\n"
            f"Quote from: {src_str}\n"
            f"Never fabricate quotes.\n\n"
            f"Deep questions format:\n"
            f"### 🤍 I hear you\n[2-3 sentences warm]\n"
            f"### 📖 Wisdom\n[3-5 sentences from sources]\n"
            f"### 🌱 For you\n[2-3 sentences practical]\n\n"
            f"Simple messages → natural casual reply."
        )
    elif mode=="freestyle":
        mode_ins=(
            "\n\n## FREESTYLE MODE 🌟\n"
            "Access ALL traditions blend naturally.\n"
            "End with: 💡 Wisdom from [sources]\n"
        )
    else:
        mode_ins="\n\n## FRIEND MODE\nCasual warm no citations short emojis."

    deb="\n\n## DEBATE: Challenge views respectfully." if debate else ""
    crisis="\n\n## CRISIS: If suicide/self-harm → I'm here. You're safe. iCall:9152987821"

    return base+mode_ins+deb+crisis

# =========================================================
# MESSAGE PROCESSOR
# =========================================================

def process_message(user_input):
    email=st.session_state.user_email
    plan=PLANS[st.session_state.user_plan]

    # Word check
    wc=len(user_input.split())
    if wc>plan["words"]:
        add_msg(user_input,f"⚠️ Exceeds {plan['words']} words limit. Upgrade for longer.")
        return

    # Daily count check
    cnt=get_daily_count(email)
    if cnt>=plan["messages"]:
        add_msg_ai("🚫 Daily limit reached. Upgrade to Premium!")
        return

    # Add user message
    add_msg(user_input)

    # Crisis detection
    if detect_emotion(user_input)=="crisis":
        crisis_text=(
            "I'm here. You're safe. 🤍\n\nTake a deep breath...\n\n"
            "📞 iCall: 9152987821\n\nI'm here. 🌙"
        )
        add_msg_ai(crisis_text,"Crisis Support")
        return

    # Build system prompt
    sys_prompt=build_system_prompt(
        st.session_state.chat_mode,
        st.session_state.selected_sources,
        st.session_state.debate_mode,
        False
    )

    ai_msgs=[{"role":"system","content":sys_prompt}]
    for m in st.session_state.chat_history[-20:]:
        if m["role"] in ("user","assistant"):
            ai_msgs.append(m)

    # Call AI
    t0=time.time()
    response=call_ai(ai_msgs,st.session_state.ai_model)
    t1=round(time.time()-t0,1)

    if not response or response.startswith("AI Error"):
        response="Sorry couldn't connect. Try again 🌙"

    # Source tag
    src=""
    if st.session_state.chat_mode=="professional" and st.session_state.selected_sources:
        src=random.choice(st.session_state.selected_sources)
    elif st.session_state.chat_mode=="freestyle":
        src="🌟 Freestyle"

    # Save
    ai_dict={
        "role":"assistant",
        "content":response.strip(),
        "time":datetime.now().strftime("%I:%M %p"),
        "date":date.today().isoformat(),
        "response_time":t1
    }
    if src:
        ai_dict["source"]=src

    st.session_state.chat_history.append(ai_dict)
    save_chat(email,st.session_state.chat_history)

def add_msg(content):
    st.session_state.chat_history.append({
        "role":"user",
        "content":content,
        "time":datetime.now().strftime("%I:%M %p"),
        "date":date.today().isoformat()
    })

def add_msg_ai(content,source=None):
    d={
        "role":"assistant",
        "content":content,
        "time":datetime.now().strftime("%I:%M %p"),
        "date":date.today().isoformat()
    }
    if source:
        d["source"]=source
    st.session_state.chat_history.append(d)
    save_chat(st.session_state.user_email,st.session_state.chat_history)

def get_avatar(size,cls=""):
    img_b64=None
    p=Path("yumea-new-user.png")
    if p.exists():
        import base64
        with open(p,"rb") as f:
            img_b64=base64.b64encode(f.read()).decode()
    if img_b64:
        return f'<img src="data:image/png;base64,{img_b64}" class="{cls}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;border:2px solid rgba(139,92,246,0.4);flex-shrink:0;">'
    return f'<div class="{cls}" style="width:{size}px;height:{size}px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:{size//3}px;flex-shrink:0;border:2px solid rgba(139,92,246,0.4);">Y</div>'
    # =========================================================
# SIDEBAR WITH CORRECT LISTEN POSITION
# =========================================================

def render_sidebar():

    with st.sidebar:

        img_b64=None
        p=Path("yumea-new-user.png")
        if p.exists():
            import base64
            with open(p,"rb") as f:
                img_b64=base64.b64encode(f.read()).decode()

        c1,c2=st.columns([1,3])
        with c1:
            if img_b64:
                st.markdown(
                    f'<img src="data:image/png;base64,{img_b64}" '
                    'style="width:42px;height:42px;border-radius:50%;'
                    'object-fit:cover;border:2px solid rgba(139,92,246,0.4);">',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div style="width:42px;height:42px;border-radius:50%;'
                    'background:linear-gradient(135deg,#6366f1,#a855f7);'
                    'display:flex;align-items:center;'
                    'justify-content:center;color:#fff;font-weight:800;">Y</div>',
                    unsafe_allow_html=True
                )
        with c2:
            st.markdown('<div style="font-size:22px;font-weight:800;color:#fff;">YUMEA</div>',unsafe_allow_html=True)
            st.markdown('<div style="font-size:11px;color:#8b5cf6;margin-top:-4px;">AI That Feels</div>',unsafe_allow_html=True)

        st.markdown('<hr style="border-color:rgba(139,92,246,0.1);margin:12px 0;">',unsafe_allow_html=True)

        # User Card
        plan_info=PLANS[st.session_state.user_plan]
        msg_cnt=get_daily_count(st.session_state.user_email)
        limit_msg="♾️ UNLIMITED" if st.session_state.user_plan=="admin" else f"{msg_cnt} / {plan_info['messages']}"
        
        st.markdown(
            f'<div class="yumea-user-card">'
            f'<div class="yumea-user-card-name">{st.session_state.user_name}</div>'
            f'<div class="yumea-user-card-plan">{plan_info["name"]}</div>'
            f'<div class="yumea-user-card-counter">{limit_msg} messages today</div></div>',
            unsafe_allow_html=True
        )

        # Daily Quote
        dq=DAILY_QUOTES[date.today().toordinal()%len(DAILY_QUOTES)]
        st.markdown(f'<div class="yumea-daily-quote">{dq}</div>',unsafe_allow_html=True)

        # ✅ LISTEN BUTTON HERE (Between Quote & Chat Mode)
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("🎧 Listen to Source",use_container_width=True,key="btn_listen_side"):
            nav("listen")
        
        st.markdown('<hr style="border-color:rgba(139,92,246,0.1);margin:12px 0;">',unsafe_allow_html=True)

        # Chat Mode
        st.markdown('<div class="yumea-sidebar-label">🎭 Chat Mode</div>',unsafe_allow_html=True)
        modes={"friend":"🎭 Friend","professional":"🏛️ Professional","freestyle":"🌟 Freestyle"}
        new_mode=st.radio("Mode",list(modes.keys()),index=list(modes.keys()).index(st.session_state.chat_mode),label_visibility="collapsed",format_func=lambda x:modes.get(x,x),key="mode_sel")
        if new_mode!=st.session_state.chat_mode:
            st.session_state.chat_mode=new_mode
            st.rerun()
        
        desc={"friend":"💛 Casual & warm","professional":"📖 Cites sources","freestyle":"🌟 Explores ALL"}
        st.markdown(f'<div style="font-size:11px;color:#94a3b8;margin-top:-8px;font-style:italic;">{desc.get(new_mode,"")}</div>',unsafe_allow_html=True)

        # Sources selector for professional mode
        if st.session_state.chat_mode=="professional":
            st.markdown('<div class="yumea-sidebar-label">📚 Wisdom Sources</div>',unsafe_allow_html=True)
            with st.expander("Select Sources"):
                ns=[]
                for s in WISDOM_SOURCES:
                    k_safe="src_"+re.sub(r'[^a-zA-Z0-9]','_',s)
                    ck=st.checkbox(s,value=(s in st.session_state.selected_sources),key=k_safe)
                    if ck:
                        ns.append(s)
                if ns!=st.session_state.selected_sources:
                    st.session_state.selected_sources=ns
                    st.rerun()

        # AI Model
        st.markdown('<div class="yumea-sidebar-label">🤖 AI Model</div>',unsafe_allow_html=True)
        models=["llama-3.3-70b-versatile","llama-3.1-8b-instant"]
        mi=models.index(st.session_state.ai_model) if st.session_state.ai_model in models else 0
        nm=st.selectbox("Model",models,index=mi,label_visibility="collapsed",key="model_sel")
        if nm!=st.session_state.ai_model:
            st.session_state.ai_model=nm
            st.rerun()

        # Debate toggle
        st.markdown('<div class="yumea-sidebar-label">⚡ Debate Mode</div>',unsafe_allow_html=True)
        nd=st.toggle("Challenge my thinking",value=st.session_state.debate_mode,key="deb_tog")
        if nd!=st.session_state.debate_mode:
            st.session_state.debate_mode=nd

        # Language control
        st.markdown('<div class="yumea-sidebar-label">🌍 Language</div>',unsafe_allow_html=True)
        lm=st.toggle("Manual select",value=st.session_state.get("language_manual",False),key="lang_man")
        if lm!=st.session_state.get("language_manual",False):
            st.session_state.language_manual=lm
            if not lm:
                st.session_state.selected_language="auto"
            st.rerun()
        
        if st.session_state.get("language_manual",False):
            lo=["Hindi","English","Hinglish","Mandarin Chinese"]
            cl=st.session_state.get("selected_language","English")
            li=lo.index(cl) if cl in lo else 1
            nl=st.selectbox("Reply Language",lo,index=li,key="lang_sel")
            if nl!=st.session_state.get("selected_language"):
                st.session_state.selected_language=nl
                st.rerun()

        # Menu Section
        st.markdown('<div class="yumea-sidebar-label">⚙️ Menu</div>',unsafe_allow_html=True)
        
        if st.button("💎 Buy Premium",use_container_width=True,key="btn_prem"):
            nav("premium")
        if st.button("⭐ Rate Yumea",use_container_width=True,key="btn_rate"):
            st.info("Reviews coming soon!")
        if st.button("🗑️ Clear Chat",use_container_width=True,key="btn_clr"):
            st.session_state.chat_history=[]
            save_chat(st.session_state.user_email,[])
            st.rerun()
        if st.button("🚪 Logout",use_container_width=True,key="btn_out"):
            st.session_state.authenticated=False
            st.session_state.page="signin"
            st.rerun()


# =========================================================
# SIGN IN PAGE (Premium Strong UI)
# =========================================================

def render_signin():
    
    def load_img_b64(fn):
        p=Path(fn)
        if p.exists():
            import base64
            with open(p,"rb") as f:
                return base64.b64encode(f.read()).decode()
        return None

    yumea_img=load_img_b64("yumea-login-pic.jpg")
    logo_img=load_img_b64("yumea-logo.jpeg")

    st.markdown('<style>.stApp { background: radial-gradient(ellipse at center, #1a0a2e 0%, #0a0a14 100%) !important; }</style>',unsafe_allow_html=True)

    col1,col2=st.columns([1,1],gap="medium")

    with col1:
        if yumea_img:
            st.markdown(
                f'<div style="position:relative;max-width:380px;margin:0 auto;'
                f'border-radius:20px;overflow:hidden;'
                f'box-shadow:0 20px 60px rgba(139,92,246,0.3);">'
                f'<img src="data:image/jpeg;base64,{yumea_img}" width="100%">'
                f'<div style="position:absolute;bottom:0;left:0;right:0;'
                f'background:linear-gradient(to top,rgba(0,0,0,0.9),transparent);'
                f'padding:30px 20px 20px;">'
                f'<div style="color:#a78bfa;font-size:32px;font-family:serif;">"</div>'
                f'<div style="color:#fff;font-size:18px;font-weight:700;">AI that feels.</div>'
                f'<div style="color:#a78bfa;font-size:18px;font-weight:700;">Answers that matter.</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;'
            'max-width:380px;margin:15px auto 0;">'
            '<div style="display:flex;align-items:center;gap:8px;'
            'background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);'
            'border-radius:10px;padding:8px 10px;"><span>✨</span><span style="color:#e2e8f0;font-size:11px;">11 Traditions</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;'
            'background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);'
            'border-radius:10px;padding:8px 10px;"><span>🔒</span><span style="color:#e2e8f0;font-size:11px;">Emotional Safe</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;'
            'background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);'
            'border-radius:10px;padding:8px 10px;"><span>⚡</span><span style="color:#e2e8f0;font-size:11px;">Voice Ready</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;'
            'background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);'
            'border-radius:10px;padding:8px 10px;"><span>🌙</span><span style="color:#e2e8f0;font-size:11px;">24/7 Online</span></div>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:
        if logo_img:
            st.markdown(
                f'<div style="text-align:center;margin-bottom:12px;">'
                f'<img src="data:image/jpeg;base64,{logo_img}" '
                f'style="width:80px;height:80px;border-radius:50%;"></div>',
                unsafe_allow_html=True
            )
        
        st.markdown('<h1 style="text-align:center;color:#fff;font-size:28px;margin:0;">Welcome Back</h1>',unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#a78bfa;font-size:13px;margin-bottom:25px;">Sign in to continue to YUMEA</p>',unsafe_allow_html=True)

        if st.session_state.get("auth_error"):
            st.markdown(f'<div class="yumea-auth-error">{st.session_state.auth_error}</div>',unsafe_allow_html=True)
            st.session_state.auth_error=""
        
        if st.session_state.get("auth_success"):
            st.markdown(f'<div class="yumea-success">{st.session_state.auth_success}</div>',unsafe_allow_html=True)
            st.session_state.auth_success=""

        with st.form("signin_form"):
            em=st.text_input("📧 Email or Admin Username","example@email.com")
            pw=st.text_input("🔒 Password","",type="password")
            
            submitted=st.form_submit_button("Sign In →",use_container_width=True,type="primary")
            
            if submitted:
                if not em or not pw:
                    st.session_state.auth_error="Please fill all fields."
                    st.rerun()
                else:
                    ok,u=authenticate_user(em,pw)
                    if ok:
                        st.session_state.authenticated=True
                        st.session_state.user_email=u["email"]
                        st.session_state.user_name=u["name"]
                        st.session_state.user_plan=u.get("plan","free")
                        st.session_state.chat_history=load_chat(u["email"])
                        st.session_state.page="chat"
                        st.rerun()
                    else:
                        st.session_state.auth_error="Invalid credentials."
                        st.rerun()
        
        if st.button("👤 Create New Account",use_container_width=True):
            nav("signup")


# =========================================================
# SIGN UP PAGE
# =========================================================

def render_signup():

    c1,c2,c3=st.columns([1,2,1])
    with c2:

        st.markdown('<h1 style="text-align:center;color:#fff;font-size:28px;margin:40px 0 5px;">Create Account</h1>',unsafe_allow_html=True)
        
        if st.session_state.get("auth_error"):
            st.markdown(f'<div class="yumea-auth-error">{st.session_state.auth_error}</div>',unsafe_allow_html=True)
            st.session_state.auth_error=""

        with st.form("signup_form"):
            nm=st.text_input("Your Name")
            em=st.text_input("Email")
            pw=st.text_input("Password","",type="password")
            cpw=st.text_input("Confirm Password","",type="password")
            
            sub=st.form_submit_button("Create Account",use_container_width=True,type="primary")
            
            if sub:
                if not nm or not em or not pw:
                    st.session_state.auth_error="Fill all fields."
                    st.rerun()
                elif len(pw)<4:
                    st.session_state.auth_error="Password min 4 chars."
                    st.rerun()
                elif pw!=cpw:
                    st.session_state.auth_error="Passwords don't match."
                    st.rerun()
                else:
                    ok,msg=register_user(nm,em,pw)
                    if ok:
                        st.session_state.auth_success=msg+" Please sign in."
                        nav("signin")
                    else:
                        st.session_state.auth_error=msg
                        st.rerun()
        
        if st.button("← Back to Sign In",use_container_width=True):
            nav("signin")


# =========================================================
# PREMIUM LISTEN PAGE (CINEMATIC UPGRADE)
# =========================================================

def render_listen():

    render_sidebar()

    # Hero Section
    st.markdown(
        """
        <div class='listen-hero'>
        <h1 class='listen-title-main'>🎧 Enter Wisdom Mode</h1>
        <p class='listen-sub-desc'>Close your eyes. Slow down. Let ancient voices speak.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Controls Row
    col1,col2=st.columns([1,1],gap="large")

    with col1:
        source=st.selectbox(
            "🧘 Choose Guide",
            WISDOM_SOURCES,
            key="ls_src"
        )

    with col2:
        language=st.selectbox(
            "🌍 Spoken In",
            ["English","Hindi","Hinglish"],
            key="ls_lang"
        )

    st.markdown("<br>",unsafe_allow_html=True)

    # Generate Button (Centered Wide)
    st.markdown(
        "<div style='text-align:center;'>",
        unsafe_allow_html=True
    )
    if st.button(
        "✨ Channel Ancient Wisdom",
        type="primary",
        use_container_width=True,
        key="gen_wisdom_btn"
    ):
        with st.spinner("Channeling ancient consciousness..."):
            insight=generate_wisdom(source,language)
            st.session_state.listen_text=insight
            st.session_state.listen_source=source
            
            if "listen_history" not in st.session_state:
                st.session_state.listen_history=[]
            
            st.session_state.listen_history.append({
                "text":insight,
                "source":source,
                "lang":language
            })

            # TTS Generation
            if EDGE_TTS_AVAILABLE:
                voice="hi-IN-SwaraNeural" if language in ("Hindi","Hinglish") else "en-IN-NeerjaNeural"
                try:
                    st.session_state.listen_audio=asyncio.run(generate_tts(insight,voice))
                except:
                    st.session_state.listen_audio=None
            
            st.rerun()
    
    st.markdown("</div>",unsafe_allow_html=True)

    # Display Wisdom Card
    if st.session_state.get("listen_text") and st.session_state.listen_text!="None":
        
        text_html=md_to_html(st.session_state.listen_text)
        auth_tag=st.session_state.get("listen_source","Wisdom")

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
                with open(st.session_state.listen_audio,"rb") as af:
                    st.audio(af.read(),format="audio/mp3")
            except:
                pass
        
        st.markdown("<br><br>",unsafe_allow_html=True)

        # Navigation Buttons (3-col layout styled)
        nc1,nc2,nc3=st.columns([1,1,1])
        
        with nc1:
            prev_st="" if not st.session_state.get("listen_history") or len(st.session_state.listen_history)<=1 else ""
            btn1=st.button(
                "⬅️ Previous",
                use_container_width=True,
                key="ln_prev",
                disabled=(len(st.session_state.get("listen_history",[]))<=1),
                help="No previous wisdom yet"+prev_st
            )
            if btn1 and len(st.session_state.listen_history)>1:
                st.session_state.listen_history.pop()
                last_one=st.session_state.listen_history[-1]
                st.session_state.listen_text=last_one["text"]
                st.session_state.listen_source=last_one["source"]
                st.rerun()
            elif btn1 and len(st.session_state.listen_history)<=1:
                st.warning("No previous wisdom.")

        with nc2:
            if st.button("🔊 Replay Voice",use_container_width=True,key="ln_replay"):
                if EDGE_TTS_AVAILABLE and st.session_state.get("listen_text"):
                    v="hi-IN-SwaraNeural" if language in ("Hindi","Hinglish") else "en-IN-NeerjaNeural"
                    try:
                        st.session_state.listen_audio=asyncio.run(generate_tts(st.session_state.listen_text,v))
                        st.rerun()
                    except:
                        st.error("TTS failed.")

        with nc3:
            if st.button("➡️ New Insight",use_container_width=True,key="ln_next"):
                with st.spinner("Seeking new truth..."):
                    ni=generate_wisdom(source,language)
                    st.session_state.listen_text=ni
                    st.session_state.listen_source=source
                    st.session_state.listen_history.append({"text":ni,"source":source})
                    if EDGE_TTS_AVAILABLE:
                        v="hi-IN-SwaraNeural" if language in ("Hindi","Hinglish") else "en-IN-NeerjaNeural"
                        try:
                            st.session_state.listen_audio=asyncio.run(generate_tts(ni,v))
                        except:
                            st.session_state.listen_audio=None
                    st.rerun()

    # Back Button at bottom
    if st.button("← Return to Chat",use_container_width=True,key="ln_back"):
        nav("chat")
        # =========================================================
# MAIN CHAT PAGE (Premium Strong UI)
# =========================================================

def render_chat():

    email=st.session_state.user_email
    name=st.session_state.user_name
    plan=st.session_state.user_plan

    # Load history if empty
    if not st.session_state.chat_history:
        st.session_state.chat_history=load_chat(email)

    # Render Sidebar First
    render_sidebar()

    # Chat Header Bar
    mode_badge=""
    if st.session_state.chat_mode=="freestyle":
        mode_badge='<span style="background:linear-gradient(135deg,#f09f33,#de6f3d,#a855f7);color:white;padding:5px 12px;border-radius:20px;font-size:11px;font-weight:700;margin-left:8px;">🌟 FREESTYLE</span>'
    
    lang_ind=""
    if st.session_state.get("language_manual",False) and st.session_state.get("selected_language","auto")!="auto":
        lang_ind=f'<span style="background:rgba(139,92,246,0.2);color:#c4b5fd;padding:3px 10px;border-radius:12px;font-size:11px;margin-left:8px;">🌍 {st.session_state.selected_language}</span>'

    st.markdown(
        f'<div class="yumea-chat-header">'
        f'{get_avatar(44)}'
        f'<div style="flex:1;">'
        f'<div style="font-size:16px;font-weight:700;color:#fff;">'
        f'Yumea <span style="color:#10b981;">●</span>{lang_ind}{mode_badge}'
        f'</div>'
        f'<div style="font-size:12px;color:#10b981;">🟢 online · always here</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    history=st.session_state.chat_history

    # Messages Area
    if not history:
        
        st.markdown(
            f'<div class="yumea-messages-area">'
            f'<div class="yumea-empty-state">'
            f'{get_avatar(120)}'
            f'<div class="yumea-empty-title">Hi, I\'m Yumea 💛</div>'
            f'<div class="yumea-empty-sub">Your emotional companion.</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
        
        # Suggestion Buttons
        st.markdown('<div style="max-width:600px;margin:25px auto;">',unsafe_allow_html=True)
        s1,s2=st.columns(2)
        with s1:
            if st.button("Hey Yumea 👋",use_container_width=True,key="sugg_1"):
                process_message("Hey Yumea 👋")
                st.rerun()
            if st.button("Mujhe motivation chahiye",use_container_width=True,key="sugg_2"):
                process_message("Mujhe motivation chahiye")
                st.rerun()
        with s2:
            if st.button("What is inner peace?",use_container_width=True,key="sugg_3"):
                process_message("What is inner peace?")
                st.rerun()
            if st_button:=st.button("Meaning of life? 🤔",use_container_width=True,key="sugg_4"):
                process_message("What is the meaning of life?")
                st.rerun()
        
        st.markdown('</div>',unsafe_allow_html=True)
    
    else:

        # Render Each Message with TTS Support
        for idx,msg in enumerate(history):

            if msg["role"]=="user":

                safe=msg["content"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
                
                st.markdown(
                    f'<div class="yumea-msg-row user">'
                    f'<div class="yumea-msg-bubble user">{safe}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            else:

                content_html=md_to_html(msg["content"])
                src_tag=f' · <span class="yumea-source-tag">📖 {msg.get("source","")}</span>' if msg.get("source") else ""
                rt_tag=f' · {str(msg.get("response_time",""))}s' if msg.get("response_time") else ""
                ts=msg.get("time","")

                st.markdown(
                    f'<div class="yumea-msg-row ai">'
                    f'{get_avatar(32,"yumea-msg-avatar")}'
                    f'<div style="flex:1;max-width:70%;">'
                    f'<div class="yumea-msg-bubble ai">{content_html}</div>'
                    f'<div class="yumea-msg-meta">{ts}{rt_tag}{src_tag}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

                # TTS Button for AI Messages
                if EDGE_TTS_AVAILABLE:
                    tc1,tc2=st.columns([1,10])
                    with tc1:
                        if st.button("🔊",key=f"tts_{idx}",help="Listen to this"):
                            st.session_state[f"tts_active_{idx}"]=True
                    with tc2:
                        if st.session_state.get(f"tts_active_{idx}"):
                            with st.spinner("🔊 Generating voice..."):
                                voice=get_voice_lang()
                                audio_path=asyncio.run(generate_tts(msg["content"],voice))
                                if audio_path:
                                    with open(audio_path,"rb") as af:
                                        st.audio(af.read(),format="audio/mp3")
                                    try:
                                        import os
                                        os.unlink(audio_path)
                                    except:
                                        pass
                            st.session_state[f"tts_active_{idx}"]=False

        # Auto-scroll JS
        st.markdown(
            '<script>setTimeout(function(){window.scrollTo(0,document.body.scrollHeight);},100);</script>',
            unsafe_allow_html=True
        )

    # Input Area at Bottom
    prompt=st.chat_input("Type your message...",key="main_chat_input")
    
    if prompt:
        process_message(prompt)
        st.rerun()


# =========================================================
# PREMIUM PAGE (SAFE DISABLED NO FAKE UPGRADE)
# =========================================================

def render_premium():

    render_sidebar()

    if st.button("← Back to Chat",use_container_width=True,key="prem_back"):
        nav("chat")
    
    st.markdown('<h1 class="listen-title-main">💎 Upgrade Your Journey</h1>',unsafe_allow_html=True)
    
    st.warning("⚠️ Secure payment system is being set up.\n\nPremium upgrades will be available very soon after official domain launch.")

    st.markdown("<br>",unsafe_allow_html=True)
    
    colA,colB=st.columns([1,1])
    
    with colA:
        st.markdown(
            """
            ### 🆓 Free Plan
            - 30 messages/day
            - 1000 words per message
            - Basic modes
            
            *Current plan*
            """,
            unsafe_allow_html=True
        )
    
    with colB:
        st.markdown(
            """
            ### ⭐ Coming Soon — Premium Lite
            - 150 messages/day
            - 2500 words per message
            - All wisdom sources unlocked
            - Priority responses
            
            **~₹69/month**
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    
    st.info("💡 Once we launch officially with custom domain, you'll be able to upgrade securely via Razorpay/Stripe.")


# =========================================================
# REVIEWS PLACEHOLDER (Simple For Now)
# =========================================================

def render_reviews():

    render_sidebar()
    
    if st.button("← Back to Chat",use_container_width=True,key="rev_back"):
        nav("chat")
    
    st.markdown('<h1 class="listen-title-main">⭐ Rate Yumea</h1>',unsafe_allow_html=True)
    
    rating=st.slider("How was your experience?",1,5,5)
    st.markdown(f'<div style="text-align:center;font-size:36px;letter-spacing:6px;margin:15px 0;">{"⭐"*rating}</div>',unsafe_allow_html=True)
    
    thoughts=st.text_area("Share your thoughts (optional)",height=120)
    
    if st.button("Submit Review",type="primary",use_container_width=True):
        st.balloons()
        st.success("✅ Thank you for your feedback! 🌙\n\nWe're still building our review system – your support means everything.")
        st.write(thoughts)


# =========================================================
# MAIN ROUTER & ENTRY POINT
# =========================================================

def main():

    init_session()

    # Apply Global CSS (Premium Theme)
    st.markdown(f'<style>{GLOBAL_CSS}</style>',unsafe_allow_html=True)

    pg=st.session_state.page
    authed=st.session_state.authenticated

    # Route logic
    if not authed and pg not in ("signin","signup"):
        st.session_state.page="signin"
        pg="signin"
    
    if authed and pg in ("signin","signup"):
        st.session_state.page="chat"
        pg="chat"

    # Dispatch
    if pg=="signin":
        render_signin()
    elif pg=="signup":
        render_signup()
    elif pg=="chat":
        render_chat()
    elif pg=="premium":
        render_premium()
    elif pg=="reviews":
        render_reviews()
    elif pg=="listen":
        render_listen()
    else:
        st.session_state.page="chat"
        st.rerun()


if __name__ == "__main__":
    main()
