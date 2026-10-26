import json
import os
import httpx
from pathlib import Path
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
TONES_FILE = Path("tone.json")

# --- AI LOGIC ---
AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it:generateContent"
OLLAMA_URL = "http://localhost:11434/api/generate"

def get_tones():
    if TONES_FILE.exists():
        return "\n".join(json.loads(TONES_FILE.read_text()))
    return "Standard professional tone."

def save_tone(text):
    tones = json.loads(TONES_FILE.read_text()) if TONES_FILE.exists() else []
    tones.append(text)
    TONES_FILE.write_text(json.dumps(tones))

async def generate_replies(email: str):
    prompt = f"""You are a ghostwriter. Draft replies in the user's exact tone.
Past examples of user's tone:
{get_tones()}

Incoming email: "{email}"

Return ONLY JSON: {{"short": "1 sentence", "polite": "corporate", "pushback": "firm"}}"""
    
    if AI_PROVIDER == "api" and GOOGLE_API_KEY:
        async with httpx.AsyncClient() as client:
            r = await client.post(GOOGLE_URL, json={"contents": [{"role": "user", "parts": [{"text": prompt}]}]}, headers={"x-goog-api-key": GOOGLE_API_KEY})
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(OLLAMA_URL, json={"model": "gemma3:4b", "prompt": prompt, "stream": False, "format": "json"}, timeout=60.0)
                raw = r.json()["response"]
        except Exception:
            # Fallback to Google if Ollama fails
            async with httpx.AsyncClient() as client:
                r = await client.post(GOOGLE_URL, json={"contents": [{"role": "user", "parts": [{"text": prompt}]}]}, headers={"x-goog-api-key": GOOGLE_API_KEY})
                raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]

    if "```" in raw: raw = raw.split("```")[1].replace("json", "")
    return json.loads(raw.strip())

# --- WEB UI ---
def page(content):
    return f"""<!DOCTYPE html><html><head><title>Inbox Sloth</title><script src="https://unpkg.com/htmx.org@1.9.12"></script>
    <style>body{{background:#0e0e11;color:#e8e8ec;font-family:system-ui;max-width:800px;margin:3rem auto;padding:1rem}}
    .card{{background:#17171c;border:1px solid #24242c;padding:1.5rem;border-radius:12px;margin-bottom:1rem}}
    textarea{{width:100%;background:#0e0e11;color:#fff;border:1px solid #2e2e38;padding:1rem;border-radius:8px;margin:0.5rem 0}}
    button{{background:#7c6cf0;color:#fff;padding:0.8rem 1.5rem;border:none;border-radius:8px;cursor:pointer;font-weight:bold;width:100%}}
    .grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem}} h3{{color:#7c6cf0;margin-top:0}}
    </style></head><body><h1>🦥 Inbox Sloth</h1><p>Paste a stressful email. Get 3 replies.</p>{content}</body></html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return page("""
    <div class="card"><form hx-post="/generate" hx-target="#out" hx-swap="innerHTML">
    <textarea name="email" rows="5" required placeholder="Paste the email here..."></textarea>
    <button type="submit">Draft Replies</button></form></div><div id="out"></div>
    <details style="margin-top:2rem"><summary>Teach AI your tone</summary>
    <div class="card"><form hx-post="/teach" hx-target="#msg">
    <textarea name="tone" rows="3" required placeholder="Paste a past email you wrote..."></textarea>
    <button type="submit">Save Tone</button><p id="msg" style="color:#7c6cf0"></p>
    </form></div></details>""")

@app.post("/generate", response_class=HTMLResponse)
async def generate(email: str = Form(...)):
    try:
        d = await generate_replies(email)
        return f"""<div class="grid"><div class="card"><h3>Short</h3><p>{d.get('short','')}</p></div>
        <div class="card"><h3>Polite</h3><p>{d.get('polite','')}</p></div>
        <div class="card"><h3>Pushback</h3><p>{d.get('pushback','')}</p></div></div>"""
    except Exception as e:
        return f"<div class='card'>Error: {e}</div>"

@app.post("/teach", response_class=HTMLResponse)
def teach(tone: str = Form(...)):
    save_tone(tone)
    return "✅ Saved!"