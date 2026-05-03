import random
from datetime import date, datetime, timedelta

import streamlit as st

st.set_page_config(page_title="Smarty Study Buddy", page_icon="✨", layout="wide")

if "state" not in st.session_state:
    st.session_state.state = {
        "points": 0,
        "subjects": [],
        "flashcards": [],
        "events": [],
        "history": [],
        "goal_points": 200,
        "style": "Classic Buddy",
        "mode": "Study",
    }

SLOGANS = [
    "Tiny steps, giant glow-up 🚀",
    "Brains loading... almost legendary 🧠",
    "You + effort = unstoppable 🔥",
]
UPGRADES = [
    {"name": "Neon Hero", "cost": 120},
    {"name": "Cyber Friend", "cost": 250},
    {"name": "Anime Mentor", "cost": 400},
]

def ensure_default_events():
    state = st.session_state.state
    for i in range(14):
        d = date.today() + timedelta(days=i)
        key = d.isoformat()
        exists = any(e["date"] == key and e["title"] == "Default Study Session" for e in state["events"])
        if not exists:
            state["events"].append(
                {"title": "Default Study Session (90m incl breaks)", "date": key, "type": "Study"}
            )

def add_history(note: str, pts: int):
    st.session_state.state["history"].insert(
        0,
        {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": note,
            "pts": pts,
        },
    )

ensure_default_events()
state = st.session_state.state

st.markdown(
    """
    <style>
    .stApp {background: linear-gradient(120deg, #0e1428 0%, #241a4f 100%);}    
    [data-testid="stMetric"] {background: rgba(255,255,255,0.07); border-radius: 14px; padding: 12px;}
    .glass {background: rgba(255,255,255,0.07); padding: 1rem; border-radius: 14px; backdrop-filter: blur(8px);} 
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("✨ Smarty Study Buddy")
st.caption("A modern Python UI for focused study sessions.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Points", state["points"])
left = max(state["goal_points"] - state["points"], 0)
c2.metric("Goal", state["goal_points"])
c3.metric("To Goal", left)
c4.metric("Mode", state["mode"])

left_col, right_col = st.columns([1.2, 1], gap="large")

with left_col:
    st.subheader("Buddy Chat")
    if "chat" not in st.session_state:
        plans = [f"{e['title']} ({e['type']})" for e in state["events"] if e["date"] == date.today().isoformat()]
        today_plan = ", ".join(plans) if plans else "Default study 90 min"
        st.session_state.chat = [
            f"Hey friend! Today's plan: {today_plan}. Want to add anything else?",
            "Quick check-in: energy level 1-5 and what topic feels hardest today?",
        ]

    for msg in st.session_state.chat:
        st.markdown(f"- {msg}")

    user_msg = st.text_input("Type your answer or ask for explanation")
    if st.button("Send", use_container_width=True) and user_msg.strip():
        txt = user_msg.strip()
        st.session_state.chat.append(f"You: {txt}")
        if "explain" in txt.lower():
            st.session_state.chat.append("Got it! I can explain in a quick and fun way. Tell me the exact topic.")
        elif "check answer" in txt.lower():
            st.session_state.chat.append("Sure! Paste your answer and the correct one, and I will compare it quickly.")
        else:
            st.session_state.chat.append("Love that! " + random.choice(SLOGANS))
        st.rerun()

    st.subheader("Study Timer")
    t1, t2, t3 = st.columns(3)
    study_min = t1.number_input("Study (min)", min_value=5, value=30)
    break_min = t2.number_input("Break (min)", min_value=1, value=5)
    session_min = t3.number_input("Session (min)", min_value=20, value=90)

    cstart, cdone, cearly = st.columns(3)
    if cstart.button("Complete Session", use_container_width=True):
        state["points"] += 40
        add_history(f"Completed session {study_min}/{break_min} for {session_min} min", +40)
        st.success("Session complete! +40 points")
    if cdone.button("Motivation", use_container_width=True):
        st.info(random.choice(SLOGANS))
    if cearly.button("End Early", use_container_width=True):
        state["points"] = max(0, state["points"] - 20)
        add_history("Ended early", -20)
        st.warning("Session ended early, -20 points. Restart when ready.")

with right_col:
    st.subheader("Modes")
    m1, m2 = st.columns(2)
    if m1.button("Study Mode", use_container_width=True):
        state["mode"] = "Study"
    if m2.button("Homework Mode", use_container_width=True):
        state["mode"] = "Homework"

    st.subheader("Subjects + Progress")
    s_name = st.text_input("Subject name")
    if st.button("Add Subject") and s_name.strip():
        state["subjects"].append({"name": s_name.strip(), "progress": 0})

    for i, sub in enumerate(state["subjects"]):
        cols = st.columns([2, 3])
        cols[0].write(sub["name"])
        sub["progress"] = cols[1].slider(
            f"{sub['name']} progress", min_value=0, max_value=100, value=sub["progress"], key=f"prog_{i}"
        )

    st.subheader("Flashcards")
    f1, f2 = st.columns(2)
    front = f1.text_input("Front")
    back = f2.text_input("Back")
    if st.button("Add Flashcard") and front.strip() and back.strip():
        state["flashcards"].append({"front": front.strip(), "back": back.strip()})

    for card in state["flashcards"]:
        with st.expander(card["front"]):
            st.write(card["back"])

st.divider()
col_a, col_b, col_c = st.columns([1.2, 1.4, 1])

with col_a:
    st.subheader("Timetable + Calendar")
    ev_title = st.text_input("Event")
    ev_date = st.date_input("Date", value=date.today())
    ev_type = st.selectbox("Type", ["Study", "School", "Homework", "Special"])
    if st.button("Add Event") and ev_title.strip():
        state["events"].append({"title": ev_title.strip(), "date": ev_date.isoformat(), "type": ev_type})

    for ev in sorted(state["events"], key=lambda x: x["date"])[:20]:
        st.write(f"{ev['date']} • {ev['title']} ({ev['type']})")

with col_b:
    st.subheader("Store + Character Upgrade")
    st.write(f"Current style: **{state['style']}**")
    for up in UPGRADES:
        if st.button(f"{up['name']} ({up['cost']} pts)", key=up["name"]):
            if state["points"] >= up["cost"]:
                state["points"] -= up["cost"]
                state["style"] = up["name"]
                add_history(f"Bought style: {up['name']}", 0)
                st.success(f"Style upgraded to {up['name']}!")
            else:
                st.error("Not enough points yet.")

with col_c:
    st.subheader("Settings & History")
    state["goal_points"] = st.number_input("Goal points", min_value=50, value=state["goal_points"])
    st.caption(f"{max(state['goal_points'] - state['points'], 0)} points to reach goal")
    for h in state["history"][:12]:
        sign = "+" if h["pts"] > 0 else ""
        st.write(f"{h['date']}: {h['note']} ({sign}{h['pts']} pts)")
