"""Rehearse: practice hard conversations with an AI interviewer."""

import uuid
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .ai_provider import interviewer_turn, generate_feedback

app = FastAPI(title="Rehearse")

BASE = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

SESSIONS: dict[str, dict] = {}

def _page(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rehearse</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🎙️</text></svg>">
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
      <form method="post" action="/start" class="home-form">
        <label>Role
          <input type="text" name="role" placeholder="e.g. Backend Engineer" required>
        </label>
        
        <label>Interview Focus
          <select name="focus">
            <option value="Behavioral">Behavioral (STAR method)</option>
            <option value="Technical">Technical (Concepts & Architecture)</option>
            <option value="System Design">System Design</option>
            <option value="Mixed" selected>Mixed</option>
          </select>
        </label>

        <label>Difficulty
          <select name="difficulty">
            <option value="junior">Junior</option>
            <option value="mid" selected>Mid-level</option>
            <option value="senior">Senior</option>
          </select>
        </label>

        <label>Interviewer Tone
          <select name="tone">
            <option value="Standard" selected>Standard (Professional)</option>
            <option value="Stress">Stress Test (Hostile & Rapid-fire)</option>
          </select>
        </label>

        <label>Job Description / Context (Optional)
          <textarea name="job_desc" rows="4" placeholder="Paste the job description here. The AI will ground its questions in this text."></textarea>
        </label>

        <button type="submit" class="primary">Start interview</button>
      </form>
    </section>
    """)


@app.post("/start", response_class=HTMLResponse)
async def start(
    role: str = Form(...), 
    focus: str = Form(...), 
    difficulty: str = Form(...),
    tone: str = Form("Standard"),
    job_desc: str = Form("")
):
    session_id = str(uuid.uuid4())
    try:
        opening = await interviewer_turn([], role, focus, difficulty, job_desc, tone)
    except Exception as exc:
        return _page(f"""
        <header><h1>Rehearse</h1></header>
        <div class="error"><h2>Could not start</h2><pre>{type(exc).__name__}: {exc}</pre></div>
        <a href="/" class="back-link">← Back</a>
        """)

    SESSIONS[session_id] = {
        "role": role,
        "focus": focus,
        "difficulty": difficulty,
        "tone": tone,
        "job_desc": job_desc,
        "history": [{"role": "interviewer", "text": opening}],
    }
    return _page(_conversation_body(session_id))


@app.post("/reply", response_class=HTMLResponse)
async def reply(session_id: str = Form(...), answer: str = Form(...)):
    session = SESSIONS.get(session_id)
    if not session:
        return _page("<p>Session lost.</p><a href='/'>Start over</a>")

    session["history"].append({"role": "candidate", "text": answer})

    try:
        next_line = await interviewer_turn(
            session["history"], session["role"], session["focus"], 
            session["difficulty"], session["job_desc"], session["tone"]
        )
    except Exception as exc:
        return _page(f"<div class='error'>Error: {exc}</div>")

    session["history"].append({"role": "interviewer", "text": next_line})
    return _page(_conversation_body(session_id))


@app.post("/feedback", response_class=HTMLResponse)
async def feedback(session_id: str = Form(...)):
    session = SESSIONS.get(session_id)
    if not session:
        return _page("<p>Session lost.</p><a href='/'>Start over</a>")

    try:
        transcript = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in session["history"]])
        report = await generate_feedback(transcript, session["role"], session["focus"])
    except Exception as exc:
        return _page(f"<div class='error'>Error generating feedback: {exc}</div>")

    return _page(f"""
    <header>
      <h1>Interview Report</h1>
      <p class="tagline">{session['role']} · {session['focus']}</p>
    </header>
    <section class="card">
      <h2 style="margin-top:0; color: #7c6cf0;">Score: {report.get('score', 'N/A')} / 10</h2>
      <p style="font-size:1.05rem; line-height:1.6;">{report.get('summary', '')}</p>
      <h3 style="margin-bottom: 0.5rem; color: #e8e8ec;">What to improve:</h3>
      <ul style="color: #b8b8c2; line-height: 1.6;">
        <li>{report.get('improvement_1', '')}</li>
        <li>{report.get('improvement_2', '')}</li>
        <li>{report.get('improvement_3', '')}</li>
      </ul>
    </section>
    <a href="/" class="back-link">← Practice again</a>
    """)


def _conversation_body(session_id: str) -> str:
    session = SESSIONS[session_id]
    turns = ""
    for i, msg in enumerate(session["history"]):
        css = "interviewer" if msg["role"] == "interviewer" else "candidate"
        # Only the very last message autoplays, and only if it's the interviewer
        is_latest = (msg["role"] == "interviewer" and i == len(session["history"]) - 1)
        autoplay = "true" if is_latest else "false"
        
        # Clean the text for the HTML attribute (escape quotes, remove newlines)
        clean_text = msg["text"].replace('"', '&quot;').replace('\n', ' ')
        
        turns += f'<div class="turn {css}" data-autoplay="{autoplay}" data-text="{clean_text}">{msg["text"]}</div>'

    return f"""
    <header>
      <h1>Rehearse</h1>
      <p class="tagline">{session['role']} · {session['focus']} · {session['difficulty']}</p>
    </header>
    <section class="card conversation">{turns}</section>
    
    <section class="card">
      <form method="post" action="/reply"
            hx-post="/reply" hx-target="body" hx-swap="innerHTML"
            hx-disabled-elt="find button" hx-indicator="#thinking">
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