import httpx
import os
import json
import re
from dotenv import load_dotenv
from .prompts import PROMPT_TEMPLATE

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MODEL = "gemini-3.8-flash" 
GOOGLE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GOOGLE_MODEL}:generateContent"

def clean_and_parse_json(raw_text: str) -> dict:
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    start = raw_text.find('{')
    end = raw_text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(raw_text[start:end+1])
        except Exception as e:
            print(f"❌ JSON Decode Error: {e}")
            print("❌ FAILED JSON STRING:", raw_text[start:end+1])
    else:
        print("❌ RAW FAILED OUTPUT:", raw_text)
        
    return {
        "repo_overview": "Failed to parse AI response.",
        "global_tech_stack": "Unknown",
        "projects": [],
        "ghost_testimony": {
            "poetic_eulogy": "The ghost is silent.",
            "abandonment_evidence": ["Failed to parse AI response."],
            "ghost_commit": "fix: gave up on JSON"
        }
    }

async def analyze_repo(data: dict) -> dict:
    key_files_str = ""
    for path, content in data.get('key_files', {}).items():
        key_files_str += f"--- {path} ---\n{content}\n\n"

    prompt = PROMPT_TEMPLATE.format(
        description=data.get('description', 'None'),
        first_commit_date=data.get('first_commit_date', 'Unknown'),
        last_commit_date=data.get('last_commit_date', 'Unknown'),
        top_level_folders=", ".join(data.get('top_level_folders', [])),
        tree=", ".join(data.get('tree', [])[:150]), # Reduced for local models
        commits="\n".join(data.get('commits', [])),
        key_files=key_files_str
    )
    
    raw_text = ""
    active_provider = AI_PROVIDER
    
    if active_provider == "local":
        try:
            payload = {
                "model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                "format": "json", 
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 8192
                }
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(OLLAMA_URL, json=payload)
                res.raise_for_status()
                raw_text = res.json().get("response", "")
                print("✅ Used Local Ollama.")
        except Exception as e:
            print(f"⚠️ Ollama failed. Falling back to API...")
            active_provider = "api"

    if active_provider == "api":
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }
        headers = {"x-goog-api-key": GOOGLE_API_KEY}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(GOOGLE_URL, json=payload, headers=headers)
            if res.status_code != 200:
                print(f"🚨 GOOGLE API ERROR (URL: {GOOGLE_URL}):", res.text)
                raise Exception(f"Google API Error {res.status_code}")
            raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            print("✅ Used Google API.")

    return clean_and_parse_json(raw_text)