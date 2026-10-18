"""Rehearse: practice hard conversations with an AI interviewer."""

import uuid
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .ai_provider import interviewer_turn

app = FastAPI(title="Rehearse")

BASE = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

# In-memory sessions. Lost on restart. Fine for now.
SESSIONS: dict[str, dict] = {}


def _page(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rehearse</title>
  <link rel="stylesheet" href="/static/style.css">
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <script src="/static/voice.js"></script>
</head>
<body>
  <main class="container">
    {body}
  </main>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return _page("""
    <header>
      <h1>Rehearse</h1>
      <p class="tagline">Practice the conversation before it happens.</p>
    </header>
    <section class="card">
      <form method="post" action="/start">
        <label>Role you're interviewing for
          <input type="text" name="role" value="Backend Engineer" required>
        </label>
        <label>Difficulty
          <select name="difficulty">
            <option value="junior">Junior</option>
            <option value="mid" selected>Mid-level</option>
            <option value="senior">Senior</option>
          </select>
        </label>
        <button type="submit" class="primary">Start interview</button>
      </form>
    </section>
    """)


@app.post("/start", response_class=HTMLResponse)
async def start(role: str = Form(...), difficulty: str = Form(...)):
    session_id = str(uuid.uuid4())
    try:
        opening = await interviewer_turn([], role, difficulty)
    except Exception as exc:
        return _page(f"""
        <header><h1>Rehearse</h1></header>
        <div class="error"><h2>Could not start</h2><pre>{type(exc).__name__}: {exc}</pre></div>
        <a href="/" class="back-link">← Back</a>
        """)

    SESSIONS[session_id] = {
        "role": role,
        "difficulty": difficulty,
        "history": [{"role": "interviewer", "text": opening}],
    }
    return _page(_conversation_body(session_id))


@app.post("/reply", response_class=HTMLResponse)
async def reply(session_id: str = Form(...), answer: str = Form(...)):
    session = SESSIONS.get(session_id)
    if not session:
        return _page("""
        <header><h1>Rehearse</h1></header>
        <div class="error"><h2>Session lost</h2><p>Start a new interview.</p></div>
        <a href="/" class="back-link">← Back</a>
        """)

    session["history"].append({"role": "candidate", "text": answer})

    try:
        next_line = await interviewer_turn(
            session["history"], session["role"], session["difficulty"]
        )
    except Exception as exc:
        return _page(f"""
        <header><h1>Rehearse</h1></header>
        <div class="error"><h2>Could not respond</h2><pre>{type(exc).__name__}: {exc}</pre></div>
        <a href="/" class="back-link">← Back</a>
        """)

    session["history"].append({"role": "interviewer", "text": next_line})
    return _page(_conversation_body(session_id))


def _conversation_body(session_id: str) -> str:
    session = SESSIONS[session_id]
    turns = ""
    for msg in session["history"]:
        css = "interviewer" if msg["role"] == "interviewer" else "candidate"
        
        # Only the latest interviewer message needs to auto-play
        is_latest_interviewer = (msg["role"] == "interviewer" and msg == session["history"][-1])
        autoplay = "true" if is_latest_interviewer else "false"
        
        # Clean the text for the HTML attribute (escape quotes, remove newlines)
        clean_text = msg["text"].replace('"', '&quot;').replace('\n', ' ')
        
        turns += f'<div class="turn {css}" data-autoplay="{autoplay}" data-text="{clean_text}">{msg["text"]}</div>'

    return f"""
    <header>
      <h1>Rehearse</h1>
      <p class="tagline">{session['role']} · {session['difficulty']}</p>
    </header>

    <section class="card conversation">
      {turns}
    </section>

    <section class="card">
      <form method="post" action="/reply"
            hx-post="/reply"
            hx-target="body"
            hx-swap="innerHTML"
            hx-disabled-elt="find button"
            hx-indicator="#thinking">
        <input type="hidden" name="session_id" value="{session_id}">
        
        <label>Your answer
          <div class="input-group">
            <textarea id="answer-box" name="answer" rows="3" required></textarea>
            <button type="button" id="mic-btn" class="mic-btn" onclick="startDictation()">🎤</button>
          </div>
        </label>
        
        <button type="submit" class="primary">Send answer</button>
        <div id="thinking" class="htmx-indicator">Interviewer is thinking…</div>
      </form>
    </section>

        <form method="post" action="/feedback" style="margin-top: 1rem;">
      <input type="hidden" name="session_id" value="{session_id}">
      <button type="submit" class="primary" style="background: #2e2e38; border: 1px solid #4a4a5a;">End Interview & Get Report</button>
    </form>

    <a href="/" class="back-link">← Abandon interview</a>
    """

@app.post("/feedback", response_class=HTMLResponse)
async def feedback(session_id: str = Form(...)):
    session = SESSIONS.get(session_id)
    if not session:
        return _page("<p>Session lost.</p><a href='/'>Start over</a>")

    try:
        # We will pass the transcript back to Gemma
        transcript = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in session["history"]])
        
        from .ai_provider import generate_feedback
        report = await generate_feedback(transcript, session["role"])
        
    except Exception as exc:
        return _page(f"<div class='error'>Error generating feedback: {exc}</div>")

    return _page(f"""
    <header>
      <h1>Interview Report</h1>
      <p class="tagline">{session['role']} · {session['difficulty']}</p>
    </header>

    <section class="card">
      <h2 style="margin-top:0; color: #7c6cf0;">Score: {report['score']} / 10</h2>
      <p style="font-size:1.1rem; line-height:1.6;">{report['summary']}</p>
      
      <h3 style="margin-bottom: 0.5rem; color: #e8e8ec;">What to improve:</h3>
      <ul style="color: #b8b8c2; line-height: 1.6;">
        <li>{report['improvement_1']}</li>
        <li>{report['improvement_2']}</li>
        <li>{report['improvement_3']}</li>
      </ul>
    </section>

    <a href="/" class="back-link">← Practice again</a>
    """)