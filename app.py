import html
import random
import sys
from datetime import date
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).parent / "src"))

from safety import check_crisis, crisis_response
from emotion_model import predict_emotion, MOOD_SCORE
from response import get_reply
from llm import generate_reply
from database import init_db, log_mood

st.set_page_config(page_title="Mental Health Support Chatbot", page_icon="🧠")
init_db()

# emotion -> (emoji, chip background, chip text colour)
EMOTION_META = {
    "joy":      ("😊", "#fff3c4", "#7a5b00"),
    "sadness":  ("😢", "#dbe8fb", "#25508f"),
    "fear":     ("😟", "#e6e3fa", "#4a3f8f"),
    "anger":    ("😠", "#fddedb", "#9c342b"),
    "love":     ("❤️", "#fde8d7", "#9a4a12"),
    "surprise": ("😮", "#d8f3e6", "#1d6f47"),
}

QUICK_STARTS = [
    ("😟 I'm feeling stressed", "I'm feeling stressed about my studies"),
    ("😊 I had a good day", "I had a really good day today"),
    ("😢 I feel low", "I've been feeling low lately"),
    ("😠 I'm frustrated", "I'm really frustrated with something"),
]

TIPS = [
    "Small steps still count as progress. 🌱",
    "Drink some water and stretch your shoulders. 💧",
    "You don't have to be perfect to be worthy. 💛",
    "Take 3 slow breaths. You've got this. 🌬️",
    "Talking to someone you trust can lighten the load. 🤝",
    "Rest is productive too. 😴",
    "A short walk can change your whole mood. 🚶",
]

CHEERS = [
    "You showed up today, and that already takes strength. 💪",
    "Bad days end. You've survived every one of yours so far. 🌅",
    "Be as kind to yourself as you would be to a friend. 🤝",
    "Even the sun needs to set to rise again. ☀️",
    "You're doing better than you think. 📈",
    "One tiny win today is enough. 🏆",
]

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp, .stMarkdown, .stMarkdown p, textarea, button {
    font-family: 'Inter', sans-serif;
}
.stApp { background: linear-gradient(160deg, #eef3f8 0%, #e3edf1 100%); }
[data-testid="stHeader"] { background: transparent; }

/* ---------- Hero banner ---------- */
.hero {
    position: relative; overflow: hidden;
    padding: 1.7rem 1.9rem; margin-bottom: 1.2rem;
    border-radius: 18px; color: #fff;
    background: linear-gradient(135deg, #162a54 0%, #1a5f7a 60%, #128c96 100%);
    box-shadow: 0 10px 28px rgba(22, 42, 84, 0.28);
}
.hero::before, .hero::after {
    content: ""; position: absolute; border-radius: 50%;
    background: rgba(255, 255, 255, 0.07);
}
.hero::before { width: 230px; height: 230px; top: -80px; right: -50px; }
.hero::after { width: 140px; height: 140px; bottom: -60px; right: 130px; }
.hero-title { font-size: 1.75rem; font-weight: 800; line-height: 1.2; position: relative; }
.hero-sub { margin-top: .45rem; font-size: 1rem; opacity: .92; position: relative; }
.hero-note {
    display: inline-block; margin-top: .9rem; padding: .28rem .85rem; position: relative;
    background: rgba(255,255,255,.16); border-radius: 8px; font-size: .8rem;
}

/* ---------- Chat bubbles ---------- */
[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #dde5ee;
    border-radius: 16px 16px 16px 4px;
    padding: .9rem 1.1rem;
    margin-right: 10%;
    box-shadow: 0 2px 10px rgba(22, 42, 84, 0.07);
    animation: pop .3s ease;
}
[data-testid="stChatMessage"]:has(.u-mark) {
    background: linear-gradient(135deg, #1a5f7a, #128c96);
    border: none;
    border-radius: 16px 16px 4px 16px;
    margin-right: 0; margin-left: 15%;
    flex-direction: row-reverse;
}
.u-mark { color: #fff; font-weight: 600; text-align: right; }
@keyframes pop {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: none; }
}

/* ---------- Chips and cards ---------- */
.chip {
    display: inline-block; padding: .15rem .7rem; margin: .5rem .35rem 0 0;
    border-radius: 8px; font-size: .78rem; font-weight: 600;
}
.chip-grey { background: #eef1f5; color: #4b5563; }
.tool-card {
    margin-top: .8rem; padding: .8rem 1rem; border-radius: 10px;
    background: #eaf6f7; border-left: 4px solid #128c96;
}
.side-card {
    padding: .9rem 1rem; margin-bottom: .6rem; border-radius: 12px;
    background: #ffffff; border: 1px solid #dde5ee;
    box-shadow: 0 2px 8px rgba(22, 42, 84, 0.06); text-align: center;
}
.vibe-emoji { font-size: 2.4rem; line-height: 1.1; }

/* ---------- Buttons, sidebar, input ---------- */
[data-testid="stSidebar"] { background: rgba(255, 255, 255, 0.72); }
.stButton > button {
    border-radius: 10px; border: 1px solid #c5d3e0;
    background: #ffffff; color: #1f3a5f; font-weight: 600;
    transition: all .15s ease;
}
.stButton > button:hover {
    transform: translateY(-1px); border-color: #128c96; color: #128c96;
    box-shadow: 0 4px 12px rgba(18, 140, 150, .2);
}
[data-testid="stChatInput"] { border-radius: 14px; }
</style>
"""

# Plain style used right after a crisis message
CALM_CSS = """
<style>
.stApp { background: #eef2f6; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stChatMessage"] { background: #ffffff; border-radius: 12px; }
[data-testid="stChatMessage"]:has(.u-mark) { background: #dfe7ef; }
.u-mark { color: #2b2b2b; }
</style>
"""

HERO_HTML = """<div class="hero"><div class="hero-title">Smart Mental Health Support Chatbot</div><div class="hero-sub">A private space to talk, check in with yourself and feel a little steadier.</div><div class="hero-note">🛡️ A support tool, not a therapist. In a crisis, please contact a helpline.</div></div>"""

# ---------- State ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hi there! I'm here to listen, with no judgement. "
                    "How are you feeling today?"}
    ]

crisis_mode = st.session_state.messages[-1].get("crisis", False)
st.markdown(CALM_CSS if crisis_mode else MAIN_CSS, unsafe_allow_html=True)


def set_quick(text):
    st.session_state.quick = text


# ---------- Header ----------
if crisis_mode:
    st.title("Smart Mental Health Support Chatbot")
    st.caption("This is a support tool, not a therapist. "
               "If you are in crisis, please contact a helpline or emergency services.")
else:
    st.markdown(HERO_HTML, unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")
    country = st.selectbox("Country (for helplines)", ["IN", "US", "UK"])
    show_analysis = st.checkbox("Show emotion analysis", value=True)
    if st.button("🧹 Clear chat"):
        for k in ("messages", "last_emotion", "cheer"):
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown("---")
    last = st.session_state.get("last_emotion")
    v_emoji = EMOTION_META[last][0] if last else "🧠"
    v_label = last.capitalize() if last else "Waiting to hear from you"
    st.markdown(
        f'<div class="side-card"><div class="vibe-emoji">{v_emoji}</div>'
        f'<div>Current mood</div><b>{v_label}</b></div>',
        unsafe_allow_html=True,
    )
    tip = TIPS[date.today().toordinal() % len(TIPS)]
    st.markdown(f'<div class="side-card">💡 <b>Tip of the day</b><br>{tip}</div>',
                unsafe_allow_html=True)

    if st.button("⚡ Give me a boost"):
        st.session_state.cheer = random.choice(CHEERS)
    if st.session_state.get("cheer"):
        st.markdown(f'<div class="side-card">{st.session_state.cheer}</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Privacy:** your messages are not saved. "
                "The AI runs locally, so nothing is sent online.")

# ---------- Chat history ----------
for m in st.session_state.messages:
    if m["role"] == "user":
        avatar = "👤"
    elif m.get("crisis"):
        avatar = None            # plain default icon in crisis mode
    else:
        avatar = "🧠"

    with st.chat_message(m["role"], avatar=avatar):
        if m["role"] == "user":
            st.markdown(f'<div class="u-mark">{html.escape(m["content"])}</div>',
                        unsafe_allow_html=True)
        elif m.get("crisis"):
            st.info(m["content"])
        else:
            st.markdown(m["content"])

        if show_analysis and m.get("crisis"):
            st.caption("Safety layer triggered")
        elif show_analysis and m.get("emotion"):
            emo = m["emotion"]
            emoji, bg, fg = EMOTION_META[emo]
            st.markdown(
                f'<span class="chip" style="background:{bg};color:{fg}">'
                f'{emoji} {emo} {m["conf"]:.0%}</span>'
                f'<span class="chip chip-grey">Sentiment: {m["sentiment"]}</span>'
                f'<span class="chip chip-grey">Reply: {m["source"]}</span>',
                unsafe_allow_html=True,
            )

        if m.get("tool"):
            name, instruction = m["tool"]
            st.markdown(
                f'<div class="tool-card">🧘 <b>Try this: {html.escape(name)}</b><br>'
                f'{html.escape(instruction)}</div>',
                unsafe_allow_html=True,
            )

if st.session_state.pop("celebrate", False):
    st.toast("Great to hear that! 🎉")

# ---------- Quick-start buttons (only at the start of a chat) ----------
if len(st.session_state.messages) == 1:
    st.write("Not sure what to say? Tap one:")
    cols = st.columns(2)
    for i, (label, text) in enumerate(QUICK_STARTS):
        cols[i % 2].button(label, on_click=set_quick, args=(text,), key=f"quick{i}")

# ---------- Handle a new message ----------
prompt = st.chat_input("Type how you're feeling...")
if not prompt and "quick" in st.session_state:
    prompt = st.session_state.pop("quick")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 1. Safety layer runs FIRST and overrides everything else
    if check_crisis(prompt):
        st.session_state.messages.append({
            "role": "assistant",
            "content": crisis_response(country),
            "crisis": True,
        })
    else:
        with st.spinner("Listening carefully..."):
            emotion, conf, sentiment, _ = predict_emotion(prompt)
            template_reply, tool = get_reply(emotion, conf)
            llm_reply = generate_reply(st.session_state.messages, emotion, conf)

        st.session_state.last_emotion = emotion
        if conf >= 0.5:
            log_mood(emotion, sentiment, MOOD_SCORE[emotion])
        st.session_state.messages.append({
            "role": "assistant",
            "content": llm_reply or template_reply,
            "tool": tool,
            "emotion": emotion,
            "conf": conf,
            "sentiment": sentiment,
            "source": "LLM" if llm_reply else "template",
        })
        if emotion == "joy" and conf >= 0.8:
            st.session_state.celebrate = True

    st.rerun()