import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from database import init_db, get_moods, clear_moods

st.set_page_config(page_title="Mood Tracker", page_icon="📈")
init_db()

st.title("📈 My Mood Tracker")
st.caption("Only your mood scores and times are saved, never your messages. "
           "The data stays on this computer.")

rows = get_moods()
if not rows:
    st.info("No mood data yet. Chat with the bot first, then come back here. 🌼")
    st.stop()

df = pd.DataFrame(rows, columns=["timestamp", "emotion", "sentiment", "mood_score"])
df["timestamp"] = pd.to_datetime(df["timestamp"])

c1, c2, c3 = st.columns(3)
c1.metric("Check-ins", len(df))
c2.metric("Average mood", f"{df['mood_score'].mean():+.2f}")
c3.metric("Most common emotion", df["emotion"].mode()[0].capitalize())

fig = px.line(df, x="timestamp", y="mood_score", markers=True,
              title="Mood over time (-1 = very low, +1 = very positive)",
              range_y=[-1.1, 1.1])
fig.add_hline(y=0, line_dash="dot")
st.plotly_chart(fig)

counts = df["emotion"].value_counts().reset_index()
counts.columns = ["emotion", "count"]
fig2 = px.bar(counts, x="emotion", y="count", color="emotion",
              title="Emotion breakdown")
st.plotly_chart(fig2)

st.markdown("---")
if st.button("🗑️ Delete all my mood data"):
    clear_moods()
    st.rerun()