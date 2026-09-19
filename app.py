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

st.set_page_config(page_title="Mental Health Support Chatbot", page_icon="🌼")
init_db()

# emotion -> (emoji, chip background, chip text colour)
EMOTION_META = {
    "joy":      ("😊", "#fff3b0", "#8a6d00"),
    "sadness":  ("😢", "#d6e6ff", "#2b5aa6"),
    "fear":     ("😟", "#e8dcff", "#5b3fa0"),
    "anger":    ("😠", "#ffd9d6", "#a63a30"),
    "love":     ("💖", "#ffd6ec", "#a3306f"),
    "surprise": ("😮", "#d5f5e3", "#1e7a4a"),
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
    "Be as kind to yourself as you would be to a friend. 🫶",
    "Even the sun needs to set to rise again. ☀️",
    "You're doing better than you think. 🌈",
    "One tiny win today is enough. 🏆",
]

HAPPY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
html, body, .stApp, .stMarkdown, .stMarkdown p, textarea, button {
    font-family: 'Nunito', sans-serif;
}
.stApp {
    background: linear-gradient(120deg, #ffe0d1, #ffd6ec, #e0d9ff, #d3ecff, #d5f5e3, #fff3b0);
    background-size: 300% 300%;
    animation: drift 20s ease infinite;
}
@keyframes drift {
    0% {background-position: 0% 50%}
    50% {background-position: 100% 50%}
    100% {background-position: 0% 50%}
}
[data-testid="stHeader"] { background: transparent; }

/* ---------- Hero banner ---------- */
.hero {
    position: relative; overflow: hidden;
    padding: 1.6rem 1.8rem; margin-bottom: 1.2rem;
    border-radius: 28px; color: #fff;
    background: linear-gradient(135deg, #ff9a8b 0%, #ff6a88 50%, #ff99ac 100%);
    box-shadow: 0 10px 30px rgba(255, 106, 136, 0.35);
}
.hero-title { font-size: 1.9rem; font-weight: 800; line-height: 1.2; }
.hero-sub { margin-top: .4rem; font-size: 1.05rem; opacity: .97; }
.hero-note {
    display: inline-block; margin-top: .8rem; padding: .25rem .8rem;
    background: rgba(255,255,255,.25); border-radius: 999px; font-size: .82rem;
}
.hero .float { position: absolute; font-size: 1.9rem; animation: bob 4s ease-in-out infinite; }
.f1 { top: 10%; right: 6%; }
.f2 { top: 52%; right: 18%; animation-delay: 1s !important; }
.f3 { top: 14%; right: 30%; animation-delay: 2s !important; }
@keyframes bob {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(8deg); }
}
.wave { display: inline-block; animation: wave 2.2s infinite; transform-origin: 70% 70%; }
@keyframes wave {
    0%, 60%, 100% { transform: rotate(0deg); }
    10%, 30% { transform: rotate(16deg); }
    20% { transform: rotate(-8deg); }
    40% { transform: rotate(-4deg); }
    50% { transform: rotate(10deg); }
}

/* ---------- Chat bubbles ---------- */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #ffffff;
    border-radius: 22px 22px 22px 6px;
    padding: .9rem 1.1rem;
    margin-right: 10%;
    box-shadow: 0 4px 14px rgba(255, 120, 150, 0.18);
    animation: pop .35s ease;
}
[data-testid="stChatMessage"]:has(.u-mark) {
    background: linear-gradient(135deg, #ffb199, #ff7eb3);
    border-radius: 22px 22px 6px 22px;
    margin-right: 0; margin-left: 15%;
    flex-direction: row-reverse;
}
.u-mark { color: #fff; font-weight: 700; text-align: right; }
@keyframes pop {
    from { opacity: 0; transform: translateY(10px) scale(.97); }
    to { opacity: 1; transform: none; }
}

/* ---------- Chips and cards ---------- */
.chip {
    display: inline-block; padding: .15rem .75rem; margin: .5rem .35rem 0 0;
    border-radius: 999px; font-size: .8rem; font-weight: 700;
}
.chip-grey { background: #eef0f3; color: #555; }
.tool-card {
    margin-top: .8rem; padding: .8rem 1rem; border-radius: 16px;
    background: linear-gradient(135deg, #e3fbe9, #d9f2ff);
    border-left: 5px solid #5bc98a;
}
.side-card {
    padding: .9rem 1rem; margin-bottom: .6rem; border-radius: 18px;
    background: linear-gradient(135deg, #fff6d6, #ffe3ef);
    box-shadow: 0 3px 10px rgba(255,150,120,.15); text-align: center;
}
.vibe-emoji { font-size: 2.6rem; line-height: 1.1; }

/* ---------- Buttons, sidebar, input ---------- */
[data-testid="stSidebar"] { background: rgba(255, 255, 255, 0.6); }
.stButton > button {
    border-radius: 999px; border: 1px solid #f7b89c;
    background: #ffffff; color: #5a3e36; font-weight: 700;
    transition: all .15s ease;
}
.stButton > button:hover {
    transform: translateY(-2px); border-color: #ff8a65; color: #ff6f47;
    box-shadow: 0 6px 14px rgba(255,138,101,.25);
}
[data-testid="stChatInput"] { border-radius: 28px; }
</style>
"""

# Calm, plain style used right after a crisis message
CALM_CSS = """
<style>
.stApp { background: #eef2f6; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stChatMessage"] { background: #ffffff; border-radius: 12px; }
[data-testid="stChatMessage"]:has(.u-mark) { background: #dfe7ef; }
.u-mark { color: #2b2b2b; }
</style>
"""

HERO_HTML = """<div class="hero"><span class="float f1">🌈</span><span class="float f2">✨</span><span class="float f3">🦋</span><div class="hero-title">Smart Mental Health Support Chatbot</div><div class="hero-sub"><span class="wave">👋</span> Your friendly space to talk, breathe and feel a little lighter.</div><div class="hero-note">🛡️ A support tool, not a therapist. In a crisis, please contact a helpline.</div></div>"""

# ---------- State ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hi there! 🌼 I'm so glad you stopped by. I'm here to listen, "
                    "with no judgement. How are you feeling today?"}
    ]

crisis_mode = st.session_state.messages[-1].get("crisis", False)
st.markdown(CALM_CSS if crisis_mode else HAPPY_CSS, unsafe_allow_html=True)


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
    v_emoji = EMOTION_META[last][0] if last else "🌼"
    v_label = last.capitalize() if last else "Waiting to hear from you"
    st.markdown(
        f'<div class="side-card"><div class="vibe-emoji">{v_emoji}</div>'
        f'<div>Current vibe</div><b>{v_label}</b></div>',
        unsafe_allow_html=True,
    )
    tip = TIPS[date.today().toordinal() % len(TIPS)]
    st.markdown(f'<div class="side-card">✨ <b>Tip of the day</b><br>{tip}</div>',
                unsafe_allow_html=True)

    if st.button("🎈 Cheer me up"):
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
        avatar = "🙂"
    elif m.get("crisis"):
        avatar = None            # plain default icon, no emoji in crisis mode
    else:
        avatar = "🌼"

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
                f'<div class="tool-card">🌿 <b>Try this: {html.escape(name)}</b><br>'
                f'{html.escape(instruction)}</div>',
                unsafe_allow_html=True,
            )

if st.session_state.pop("celebrate", False):
    st.balloons()

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
        with st.spinner("Listening carefully 💭"):
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