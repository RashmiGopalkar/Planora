# Smarty Study Buddy

Smarty is a lightweight browser app for guided study sessions with:
- Friendly check-ins and chat-first session start
- 30/5 study-break timer defaults (customizable)
- Subject progress tracking
- Flashcards + revision prompts
- Points, goals, and character style upgrades
- Timetable/calendar with color-coded event types
- Homework mode with image upload preview
- Voice output/input hooks (browser-dependent)

## Where to preview

### Local preview (fastest)
Run from the project root:

```bash
python3 -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

### Online preview (after deploy)
This repository does not include a fixed public preview URL by default.
After you deploy, preview at one of these:
- GitHub Pages: `https://<your-username>.github.io/<repo-name>/`
- Netlify: URL shown in your site dashboard
- Vercel: URL shown in your project dashboard

## Quick start (local)

### 1) Requirements
- Any modern browser (Chrome/Edge/Safari/Firefox)
- Optional: Python 3 for local static hosting

### 2) Run
From the project root:

```bash
python3 -m http.server 8080
```

Open:

```text
http://localhost:8080
```

> You can also open `index.html` directly, but serving via HTTP is recommended for consistent browser behavior.

## Deploy options

### Option A: GitHub Pages
1. Push this repo to GitHub.
2. In GitHub: **Settings → Pages**.
3. Source: deploy from branch (e.g., `main`), root folder `/`.
4. Save and wait for build.
5. Open the generated `https://<user>.github.io/<repo>/` URL.

### Option B: Netlify (drag and drop)
1. Go to Netlify dashboard.
2. Use **Add new site → Deploy manually**.
3. Drag this folder (must include `index.html`, `styles.css`, `app.js`).
4. Netlify provides a live URL instantly.

### Option C: Vercel
1. Import the repository in Vercel.
2. Framework preset: **Other**.
3. Build command: none.
4. Output directory: project root.
5. Deploy.

## Notes
- Data is stored in `localStorage` under key `smartyState` in the current browser.
- Voice recognition uses `SpeechRecognition` / `webkitSpeechRecognition` and may not be available in all browsers.
- This is currently a client-only app; no backend/database is required.
