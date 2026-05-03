# Planora (Python + Streamlit)

Planora is a vibrant, friendly study buddy app with progress-aware quizzes, session pacing, flashcards, timetable/calendar, goals, and character upgrades.

## What it now includes
- Warm startup chat with daily plan and check-in questions.
- Default daily 90-minute study session (with breaks) auto-added to timetable.
- Study timer defaults: 30 min study + 5 min break, configurable.
- Session flow features:
  - Early-break logic when hard topics are detected.
  - Motivation prompts when you feel like giving up.
  - +40 points for completed full session; -20 points for ending early.
- Subjects + progress tracking from the start.
- Progress-based quiz generation.
- Study mode + Homework mode (image upload + guided completion workflow).
- Flashcard creation while studying.
- Timetable/calendar with Study/School/Homework/Special color coding.
- Store for character upgrades with points and goals.
- Settings/history area for session tracking.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
