import random

import streamlit as st

st.set_page_config(page_title="Calm Tools", page_icon="🌿")

st.title("🌿 Calm Tools")
st.caption("Simple exercises to help you feel steadier. Nothing you type here is saved.")

BREATH_HTML = """
<style>
.breath-box {position: relative; height: 340px; display: flex; align-items: center; justify-content: center;}
.breath-circle {
    width: 140px; height: 140px; border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #d9f2ff, #7ec8e3);
    box-shadow: 0 0 40px rgba(126, 200, 227, 0.6);
    animation: breathe 12s ease-in-out infinite;
}
@keyframes breathe {
    0% {transform: scale(1);}
    33% {transform: scale(1.8);}
    66% {transform: scale(1.8);}
    100% {transform: scale(1);}
}
.breath-label {
    position: absolute; bottom: 8px; width: 100%; text-align: center;
    font-size: 1.6rem; font-weight: 700; color: #3b6e8f; opacity: 0;
}
.b1 {animation: show1 12s infinite;}
.b2 {animation: show2 12s infinite;}
.b3 {animation: show3 12s infinite;}
@keyframes show1 {0%, 32% {opacity: 1;} 34%, 100% {opacity: 0;}}
@keyframes show2 {0%, 32% {opacity: 0;} 34%, 65% {opacity: 1;} 67%, 100% {opacity: 0;}}
@keyframes show3 {0%, 65% {opacity: 0;} 67%, 99% {opacity: 1;} 100% {opacity: 0;}}
</style>
<div class="breath-box">
<div class="breath-circle"></div>
<div class="breath-label b1">Breathe in... 🌬️</div>
<div class="breath-label b2">Hold... ✨</div>
<div class="breath-label b3">Breathe out... 😌</div>
</div>
"""

PROMPTS = [
    "What is one thing that went okay today, even if the day was hard?",
    "What is weighing on your mind right now? Write it out without editing.",
    "Who is someone that makes you feel supported? What would you like to tell them?",
    "What is one small thing you can do for yourself in the next hour?",
    "What are three things you are grateful for today?",
    "If a friend felt the way you do, what would you say to them?",
]

SENSES = [
    (5, "things you can SEE 👀"),
    (4, "things you can TOUCH ✋"),
    (3, "things you can HEAR 👂"),
    (2, "things you can SMELL 👃"),
    (1, "thing you can TASTE 👅"),
]

tab1, tab2, tab3 = st.tabs(["🌬️ Breathing", "🖐️ 5-4-3-2-1 Grounding", "📓 Journal"])

# ---------- Breathing ----------
with tab1:
    st.write("Follow the circle: breathe in as it grows, hold, then breathe out as it shrinks. "
             "Do about 5 rounds (one minute).")
    st.markdown(BREATH_HTML, unsafe_allow_html=True)

# ---------- Grounding ----------
with tab2:
    st.write("This helps when your mind is racing. Take your time and type "
             "one thing in each box.")
    run = st.session_state.setdefault("ground_run", 0)
    filled = 0
    for n, label in SENSES:
        st.markdown(f"**{n} {label}**")
        for i in range(n):
            v = st.text_input(f"{label} #{i + 1}", key=f"g{run}_{n}_{i}",
                              label_visibility="collapsed", placeholder=f"{i + 1}...")
            if v.strip():
                filled += 1
    st.progress(filled / 15)
    if filled == 15:
        st.success("Well done! 🌟 Notice how your body feels now. Take one slow breath.")
    if st.button("Start over"):
        st.session_state.ground_run = run + 1
        st.rerun()

# ---------- Journal ----------
with tab3:
    if "journal_prompt" not in st.session_state:
        st.session_state.journal_prompt = random.choice(PROMPTS)
    st.info(st.session_state.journal_prompt)
    st.text_area("Write here. This is only for you and is never saved.", height=200)
    if st.button("🔄 New prompt"):
        st.session_state.journal_prompt = random.choice(PROMPTS)
        st.rerun()