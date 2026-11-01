import json
import os
import httpx
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it:generateContent"

def page(content):
    return f"""<!DOCTYPE html><html><head><title>Repo Necromancer</title><script src="https://unpkg.com/htmx.org@1.9.12"></script>
    <style>body{{background:#0a0a0c;color:#c9c9d1;font-family:monospace;max-width:700px;margin:4rem auto;padding:1rem;text-align:center}}
    h1{{color:#ff3366;letter-spacing:2px}} input{{width:100%;padding:1rem;background:#141418;color:#fff;border:1px solid #333;margin-bottom:1rem}}
    button{{background:#ff3366;color:#fff;padding:1rem 2rem;border:none;cursor:pointer;font-weight:bold}}
    .card{{background:#141418;border:1px solid #333;padding:2rem;margin-top:2rem;text-align:left;line-height:1.8;font-size:1.1rem}}
    </style></head><body><h1>🪦 REPO NECROMANCER</h1><p>Summon the ghost of a dead codebase.</p>{content}</body></html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return page("""<form hx-post="/eulogy" hx-target="#out" hx-swap="innerHTML">
    <input type="text" name="repo_url" placeholder="https://github.com/owner/dead-repo" required>
    <button type="submit">Summon Ghost</button></form><div id="out"></div>""")

@app.post("/eulogy", response_class=HTMLResponse)
async def eulogy(repo_url: str = Form(...)):
    try:
        # Extract owner/repo from URL
        parts = repo_url.rstrip('/').split('/')
        if len(parts) < 2: return page("<div class='card'>Invalid URL</div>")
        owner, repo = parts[-2], parts[-1]
        
        async with httpx.AsyncClient() as client:
            # Fetch repo data
            r = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
            if r.status_code != 200: return page("<div class='card'>Repo not found or API limit reached.</div>")
            data = r.json()
            
            # Fetch last commits
            c = await client.get(f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=3")
            commits = [x['commit']['message'] for x in c.json()] if c.status_code == 200 else []

        prompt = f"""You are the ghost of a dead code repository.
Repo: {owner}/{repo}
Description: {data.get('description', 'None')}
Last pushed: {data.get('pushed_at')}
Stars: {data.get('stargazers_count')}

Your final commit messages were:
{json.dumps(commits, indent=2)}

Write a dramatic, melancholic 3-paragraph eulogy speaking in the first person (e.g., 'I was meant to be...').
Lament your abandoned features, the bugs you never fixed, and the developer who left you for a new project.
Keep it under 150 words. Return ONLY the eulogy text."""

        # Call API
        async with httpx.AsyncClient() as client:
            res = await client.post(GOOGLE_URL, json={"contents": [{"role": "user", "parts": [{"text": prompt}]}]}, headers={"x-goog-api-key": GOOGLE_API_KEY})
            ghost_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]

        return f"<div class='card'>{ghost_text}</div>"
    except Exception as e:
        return f"<div class='card'>The spirit world is unreachable: {e}</div>"