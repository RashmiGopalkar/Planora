import random
from datetime import date, datetime, timedelta

import streamlit as st

st.set_page_config(page_title="Planora", page_icon="✨", layout="wide")

# -------------------- State --------------------
if "planora" not in st.session_state:
    st.session_state.planora = {
        "points": 0,
        "goal_points": 250,
        "style": "Nova Buddy",
        "mode": "Study",
        "subjects": [],
        "flashcards": [],
        "events": [],
        "history": [],
        "syllabus": "",
        "quiz_bank": [],
        "session": {
            "study_min": 30,
            "break_min": 5,
            "total_min": 90,
            "running": False,
            "phase": "Study",
            "remaining_sec": 30 * 60,
            "total_remaining_sec": 90 * 60,
        },
    }

if "chat" not in st.session_state:
    st.session_state.chat = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

state = st.session_state.planora

MOTTO = [
    "Tiny steps. Big wins. Let's gooo 🚀",
    "Plot twist: you're stronger than this hard topic 💥",
    "Break it down, level it up, own it 🎮",
    "You are 1 focused sprint away from feeling proud ✨",
]

UPGRADES = [
    ("Nova Buddy", 0),
    ("Neon Pulse", 120),
    ("Cyber Bloom", 250),
    ("Holo Mentor", 400),
    ("Aurora Legend", 700),
]

TYPE_COLORS = {
    "Study": "#79d0ff",
    "School": "#ffc857",
    "Homework": "#ff7b72",
    "Special": "#9bff6f",
}


def add_history(note: str, pts: int = 0):
    state["history"].insert(
        0,
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "note": note,
            "pts": pts,
        },
    )


def ensure_default_timetable():
    today = date.today()
    for i in range(14):
        d = today + timedelta(days=i)
        key = d.isoformat()
        if not any(e["date"] == key and e["title"] == "Default Study Session" for e in state["events"]):
            state["events"].append(
                {
                    "title": "Default Study Session (90m incl breaks)",
                    "date": key,
                    "type": "Study",
                    "duration": 90,
                }
            )


def open_chat_intro():
    today = date.today().isoformat()
    todays = [f"{e['title']} ({e['type']})" for e in state["events"] if e["date"] == today]
    planned = ", ".join(todays[:4]) if todays else "Default Study Session"
    if not st.session_state.chat:
        st.session_state.chat.extend(
            [
                f"Hey bestie! 💛 Today's plan: {planned}. Want me to add anything else?",
                "Quick check-in: energy 1-5 and what topic feels hardest today?",
            ]
        )


def make_quiz_from_progress():
    hard = [s for s in state["subjects"] if s["progress"] < 50]
    medium = [s for s in state["subjects"] if 50 <= s["progress"] < 80]
    easy = [s for s in state["subjects"] if s["progress"] >= 80]

    picks = []
    picks.extend(hard[:2])
    picks.extend(medium[:2])
    if not picks and easy:
        picks.extend(easy[:2])

    quiz = []
    for s in picks:
        quiz.append(
            {
                "subject": s["name"],
                "q": f"In 1 line: what's the core idea of {s['name']} today?",
                "level": "focus" if s["progress"] < 50 else "revision",
            }
        )
    state["quiz_bank"] = quiz


def timer_tick_block():
    sess = state["session"]
    st.markdown("#### ⏱ Session Timer")
    c1, c2, c3 = st.columns(3)
    sess["study_min"] = c1.number_input("Study (min)", min_value=5, value=int(sess["study_min"]))
    sess["break_min"] = c2.number_input("Break (min)", min_value=1, value=int(sess["break_min"]))
    sess["total_min"] = c3.number_input("Total (min)", min_value=20, value=int(sess["total_min"]))

    if st.button("Reset Timer", use_container_width=True):
        sess["phase"] = "Study"
        sess["remaining_sec"] = int(sess["study_min"] * 60)
        sess["total_remaining_sec"] = int(sess["total_min"] * 60)

    m, s = divmod(int(sess["remaining_sec"]), 60)
    st.write(f"**Phase:** {sess['phase']} | **Time Left:** {m:02}:{s:02}")

    b1, b2, b3 = st.columns(3)
    if b1.button("+1 min tick", use_container_width=True):
        # simulate time passing in Streamlit's stateless cycle
        sess["remaining_sec"] = max(0, sess["remaining_sec"] - 60)
        sess["total_remaining_sec"] = max(0, sess["total_remaining_sec"] - 60)

        if sess["phase"] == "Study" and sess["remaining_sec"] <= 0:
            hard_topics = [x for x in state["subjects"] if x["progress"] < 40]
            early_break = bool(hard_topics and random.random() > 0.5)
            if early_break:
                sess["phase"] = "Break"
                sess["remaining_sec"] = 3 * 60
                st.info("Focus was intense 🔥 Taking a smart early 3-min break.")
            else:
                sess["phase"] = "Break"
                sess["remaining_sec"] = int(sess["break_min"] * 60)
                st.info("Break time 🌈 Water + stretch + breathe.")

        elif sess["phase"] == "Break" and sess["remaining_sec"] <= 0:
            sess["phase"] = "Study"
            sess["remaining_sec"] = int(sess["study_min"] * 60)
            st.success("Back in! Next sprint, let's cook ⚡")

        if sess["total_remaining_sec"] <= 0:
            state["points"] += 40
            add_history("Completed full session", 40)
            st.balloons()
            st.success("Session complete! +40 points. Proud of you 💛")
            sess["phase"] = "Study"
            sess["remaining_sec"] = int(sess["study_min"] * 60)
            sess["total_remaining_sec"] = int(sess["total_min"] * 60)

    if b2.button("End Early", use_container_width=True):
        state["points"] = max(0, state["points"] - 20)
        add_history("Ended early", -20)
        st.warning(f"No stress — we reset and try again. -20 points. {random.choice(MOTTO)}")

    if b3.button("Funny Motivation", use_container_width=True):
        st.info(random.choice(MOTTO))


def add_event_ui():
    st.markdown("#### 📅 Timetable & Calendar")
    e1, e2, e3, e4 = st.columns([2, 1, 1, 1])
    title = e1.text_input("Event", key="ev_title")
    d = e2.date_input("Date", value=date.today(), key="ev_date")
    typ = e3.selectbox("Type", ["Study", "School", "Homework", "Special"], key="ev_type")
    duration = e4.number_input("Min", min_value=5, value=60, key="ev_dur")
    if st.button("Add timetable event") and title.strip():
        state["events"].append({"title": title.strip(), "date": d.isoformat(), "type": typ, "duration": int(duration)})

    for ev in sorted(state["events"], key=lambda x: (x["date"], x.get("type", "")))[:40]:
        col = TYPE_COLORS.get(ev["type"], "#ddd")
        st.markdown(
            f"<div style='padding:8px;margin:5px 0;border-radius:10px;background:{col}20;border-left:6px solid {col};'>"
            f"<b>{ev['date']}</b> — {ev['title']} ({ev['type']}, {ev.get('duration', 0)}m)</div>",
            unsafe_allow_html=True,
        )


ensure_default_timetable()
open_chat_intro()

st.markdown(
    """
    <style>
    .stApp {background: linear-gradient(120deg,#101426,#2a1d52); color: #f3f5ff;}
    [data-testid="stMetric"] {background: rgba(255,255,255,0.10); padding: 12px; border-radius: 12px;}
    .small {opacity: .85; font-size: .95rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("✨ Planora — Your Friendly Study Buddy")
st.caption("Quick, vibrant, fun. No boring lectures. Just focused support 💫")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Points", state["points"])
m2.metric("Goal", state["goal_points"])
m3.metric("Remaining", max(state["goal_points"] - state["points"], 0))
m4.metric("Mode", state["mode"])

left, right = st.columns([1.2, 1], gap="large")

with left:
    st.subheader("💬 Warm Start Chat")
    for line in st.session_state.chat[-8:]:
        st.markdown(f"- {line}")

    msg = st.text_input("Talk to Planora")
    csend, ccheck = st.columns(2)
    if csend.button("Send", use_container_width=True) and msg.strip():
        low = msg.lower().strip()
        st.session_state.chat.append(f"You: {msg}")
        if "explain" in low:
            st.session_state.chat.append("Got you — send exact topic and I’ll keep it short + clear.")
        elif "check answer" in low:
            st.session_state.chat.append("Perfect, paste your answer and expected answer — I’ll compare quickly.")
        elif "give up" in low or "tired" in low:
            st.session_state.chat.append(random.choice(MOTTO))
        else:
            st.session_state.chat.append("Love it. Want a 60-sec quiz now or after one timer tick?")

    answer = ccheck.text_input("Check answer quick", key="ans_check")
    expected = ccheck.text_input("Expected answer", key="ans_expected")
    if st.button("Check Answers") and answer.strip() and expected.strip():
        a = answer.lower().split()
        e = expected.lower().split()
        overlap = len(set(a).intersection(e)) / max(1, len(set(e)))
        if overlap > 0.7:
            st.success("Great job! Very close to expected answer 👏")
        elif overlap > 0.4:
            st.info("Good attempt! Add 1-2 key terms to make it stronger 💡")
        else:
            st.warning("Let’s refine it together — keep it short with the core concept first.")

    timer_tick_block()

with right:
    st.subheader("🎯 Modes")
    a, b = st.columns(2)
    if a.button("Study Mode", use_container_width=True):
        state["mode"] = "Study"
    if b.button("Homework Mode", use_container_width=True):
        state["mode"] = "Homework"

    if state["mode"] == "Homework":
        st.markdown("**Homework mode:** Upload image, ask questions, and race against timer.")
        img = st.file_uploader("Upload homework image", type=["png", "jpg", "jpeg"])
        if img:
            st.image(img, caption="Homework image")
            st.info("Image received ✅ Ask your question and I’ll keep it short and timed.")

    st.subheader("📚 Subjects & Progress")
    sn = st.text_input("Subject name")
    if st.button("Add Subject") and sn.strip():
        state["subjects"].append({"name": sn.strip(), "progress": 0})

    for i, sub in enumerate(state["subjects"]):
        c1, c2 = st.columns([2, 3])
        c1.write(sub["name"])
        sub["progress"] = c2.slider("Progress", 0, 100, sub["progress"], key=f"sub_{i}")

    st.markdown("#### 🃏 Flashcards")
    f1, f2 = st.columns(2)
    front = f1.text_input("Front")
    back = f2.text_input("Back")
    if st.button("Create Flashcard") and front.strip() and back.strip():
        state["flashcards"].append({"front": front.strip(), "back": back.strip()})
    for fc in state["flashcards"][-12:]:
        with st.expander(fc["front"]):
            st.write(fc["back"])

st.divider()
q1, q2, q3 = st.columns([1.3, 1.2, 1])

with q1:
    add_event_ui()

with q2:
    st.markdown("#### 🧠 Revision + Quick Quiz")
    state["syllabus"] = st.text_area("Paste syllabus / topics", value=state["syllabus"], height=120)
    if st.button("Generate Quiz from Progress"):
        make_quiz_from_progress()

    if state["quiz_bank"]:
        for i, q in enumerate(state["quiz_bank"], start=1):
            st.write(f"Q{i} ({q['subject']} • {q['level']}): {q['q']}")

with q3:
    st.markdown("#### 🛍 Store, Goals & Settings")
    state["goal_points"] = st.number_input("Goal points", min_value=50, value=state["goal_points"])
    st.caption(f"{max(state['goal_points']-state['points'],0)} points to goal")

    st.write(f"Current style: **{state['style']}**")
    for name, cost in UPGRADES:
        if st.button(f"{name} ({cost})", key=f"up_{name}"):
            if state["points"] >= cost:
                state["points"] -= cost
                state["style"] = name
                add_history(f"Style upgraded to {name}", 0)
                st.success("Style upgraded! Looking amazing 😎")
            else:
                st.error("Not enough points yet — one more session maybe?")

    st.markdown("**Session history**")
    for h in state["history"][:12]:
        sign = "+" if h["pts"] > 0 else ""
        st.write(f"{h['time']}: {h['note']} ({sign}{h['pts']} pts)")

st.markdown("<p class='small'>Voice note: app has warm friendly style; full speech I/O in Streamlit may depend on browser/runtime integrations.</p>", unsafe_allow_html=True)
