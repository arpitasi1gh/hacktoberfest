from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .storage import get_tones, save_tone
from .ai_service import generate_replies

app = FastAPI(title="Inbox Sloth")

BASE = Path(__file__).resolve().parent.parent.parent
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE / "templates"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, email: str = Form(...)):
    try:
        data = await generate_replies(email, get_tones())
    except Exception as e:
        return f"<div class='error'>Failed to parse AI response: {e}</div>"

    return f"""
    <div class="grid">
        <div class="card">
            <h3>Short <button class="copy-btn" onclick="copyText(this)">Copy</button></h3>
            <p class="reply-text">{data.get('short', '')}</p>
        </div>
        <div class="card">
            <h3>Polite <button class="copy-btn" onclick="copyText(this)">Copy</button></h3>
            <p class="reply-text">{data.get('polite', '')}</p>
        </div>
        <div class="card">
            <h3>Pushback <button class="copy-btn" onclick="copyText(this)">Copy</button></h3>
            <p class="reply-text">{data.get('pushback', '')}</p>
        </div>
    </div>
    """

@app.post("/teach", response_class=HTMLResponse)
async def teach(tone: str = Form(...)):
    save_tone(tone)
    return "✅ Saved! The AI will mimic this tone next time."