from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

from src.github_service import fetch_repo_data
from src.ai_service import analyze_repo

from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def format_date(date_str):
    if date_str == "Unknown" or not date_str: return date_str
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except:
        return date_str
    
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, repo_url: str = Form(...)):
    try:
        parts = repo_url.strip().rstrip('/').split('/')
        if len(parts) < 2: raise Exception("Invalid URL")
        owner = parts[-2]
        repo = parts[-1].removesuffix('.git')
        
        data = await fetch_repo_data(owner, repo)
        report = await analyze_repo(data)
        
        # Format the dates nicely
        first_date = format_date(data.get("first_commit_date", "Unknown"))
        last_date = format_date(data.get("last_commit_date", "Unknown"))
        
        return templates.TemplateResponse(
            request,
            "dashboard.html", 
            {
                "report": report, 
                "repo_name": f"{owner}/{repo}",
                "first_commit_date": first_date,
                "last_commit_date": last_date,
                "first_commit_msg": data.get("first_commit_msg", "Unknown"),
                "last_commit_msg": data.get("last_commit_msg", "Unknown")
            }
        )
    except Exception as e:
        return f"<div class='error'><strong>Error:</strong> {str(e)}</div>"