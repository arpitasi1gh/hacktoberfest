# 🪦 Repo Necromancer – The Ghost in the Codebase

> A local-first AI tool that performs a deep forensic archaeology on any GitHub repository. It maps the architecture, extracts critical issues, and generates a dramatic eulogy from the ghost of the abandoned code.

🔗 **Live Demo:** [https://repo-necromancer.onrender.com](https://repo-necromancer.onrender.com)  
📊 **Repository:** [https://github.com/arpitasi1gh/hacktoberfest/tree/main/repo-necromancer](https://github.com/arpitasi1gh/hacktoberfest/tree/main/repo-necromancer)

![Status](https://img.shields.io/badge/Status-Hacktoberfest_Submission-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-000000?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-Google_AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Render](https://img.shields.io/badge/Deployment-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

---

## 📌 Table of Contents

<table width="100%" border="0">
  <tr>
    <td width="33%">
      <ul>
        <li><a href="#-the-problem-i-solved">💡 The Problem I Solved</a></li>
        <li><a href="#-key-features">🚀 Key Features</a></li>
        <li><a href="#-tech-stack">🧑‍💻 Tech Stack</a></li>
        <li><a href="#-project-structure">📂 Project Structure</a></li>
        <li><a href="#-quick-start-local-development">⚙️ Quick Start</a></li>
      </ul>
    </td>
    <td width="33%">
      <ul>
        <li><a href="#-how-it-works">🧠 How It Works</a></li>
        <li><a href="#-local-vs-cloud-ai">🔄 Local vs Cloud AI</a></li>
        <li><a href="#-environment-variables">🔐 Environment Variables</a></li>
        <li><a href="#-deployment">🚀 Deployment</a></li>
      </ul>
    </td>
    <td width="33%">
      <ul>
        <li><a href="#-what-i-learned">📈 What I Learned</a></li>
        <li><a href="#%EF%B8%8F-future-improvements">🗺️ Future Improvements</a></li>
        <li><a href="#-connect-with-me">🤝 Connect With Me</a></li>
        <li><a href="#-license">📝 License</a></li>
        <li><a href="#-show-your-support">⭐ Show Your Support</a></li>
      </ul>
    </td>
  </tr>
</table>

---

## 💡 The Problem I Solved

Every developer has a graveyard of abandoned side projects or has had to onboard onto a massive, undocumented legacy codebase. 

When you look at an old repository, you are faced with a wall of folders. You don't know which sub-projects are still alive, what the tech stack actually is, or where the previous developer gave up. Reading through hundreds of files just to understand the architecture is exhausting.

**Repo Necromancer fixes this.** You paste a GitHub URL. The AI acts as a Senior Principal Engineer performing a forensic autopsy. It:
1. Analyzes the full file tree, commits, and configuration files.
2. Breaks down **every single sub-folder** (monorepo support) with its specific tech stack and entry point.
3. Lists the **critical issues** and missing tests.
4. Presents the actual **lifespan** (first and last commit dates).
5. Generates a technical eulogy lamenting the abandoned code.

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🏗️ Deep Sub-Project Analysis** | Detects monorepos and analyzes every top-level folder separately (e.g., `frontend/`, `backend/`). |
| **🪦 Actual Lifespan** | Extracts the exact first and last commit dates and messages to show you the repo's true timeline. |
| **📉 Abandonment Evidence** | Forces the AI to find technical proof of death (missing tests, deprecated dependencies, broken configs). |
| **🔒 Local-First AI** | Runs Gemma 3 4B locally via Ollama. Your private repositories never leave your machine. |
| **☁️ Cloud Fallback** | Seamlessly falls back to Google AI Studio (Gemini) if Ollama is offline or the context window is too large. |
| **🚫 Anti-Hallucination Prompting** | Strict JSON constraints and folder-checklists prevent the AI from inventing files that don't exist. |

---

## 🧑‍💻 Tech Stack

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[FastAPI](https://fastapi.tiangolo.com/)** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | Async web framework handling the backend and API routes. |
| **[Jinja2](https://jinja.palletsprojects.com/)** | ![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge) | Server-side HTML templating. |
| **[HTMX](https://htmx.org/)** | ![HTMX](https://img.shields.io/badge/HTMX-336699?style=for-the-badge) | Handles form submissions and loading states without React. |
| **[Ollama](https://ollama.com/)** | ![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge) | Local inference runtime (default). |
| **[Google AI Studio](https://aistudio.google.com/)** | ![Gemini](https://img.shields.io/badge/Gemini-Google_AI-8E75B2?style=for-the-badge) | Cloud inference fallback (used for Render deployment). |
| **[GitHub API](https://docs.github.com/en/rest)** | Built-in | Fetches repository trees, commits, and file contents. |

---

## 📂 Project Structure

```text
repo-necromancer/
├── main.py                  # FastAPI app and route definitions
├── src/
│   ├── github_service.py    # Fetches tree, commits, and lifespan from GitHub
│   ├── ai_service.py        # Handles Ollama/Gemini logic and JSON parsing
│   └── prompts.py           # The strict forensic analysis prompt
├── templates/
│   ├── index.html           # Homepage with loading state
│   └── dashboard.html       # The forensic report UI
├── static/
│   └── style.css            # Dark theme styling
├── .env                     # API keys (gitignored)
├── requirements.txt
└── README.md
```

---

## ⚙️ Quick Start (Local Development)

### 0. Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com) installed (Optional, but recommended for privacy)

### 1. Clone & Install
```bash
git clone https://github.com/arpitasi1gh/hacktoberfest.git
cd hacktoberfest/repo-necromancer
uv sync
```

### 2. Set Up `.env`
Create a file called `.env` in the project root:
```env
AI_PROVIDER=local
OLLAMA_MODEL=gemma3:4b
GOOGLE_MODEL=gemini-2.5-flash
GITHUB_TOKEN=your_github_personal_access_token
GOOGLE_API_KEY=your_google_api_key
```
*(The `GITHUB_TOKEN` is highly recommended to avoid hitting the 60 requests/hour API limit).*

### 3. Run the Server
```bash
uv run uvicorn main:app --reload
```

### 4. Open Your Browser
Navigate to `http://127.0.0.1:8000`. Paste any public GitHub URL (e.g., `https://github.com/arpitasi1gh/hacktoberfest`) and click **Perform Autopsy**.

---

## 🧠 How It Works

1. **Data Extraction:** The backend calls the GitHub API to fetch the repository's metadata, the full recursive file tree, the first and last commits, and specific evidence files (`package.json`, `requirements.txt`, etc.).
2. **The Prompt:** A strict prompt is constructed. It forces the AI to look *only* at the provided folders, explicitly bans hallucinated tech stacks, and requires it to output a strict JSON schema.
3. **AI Generation:** The model (local Ollama or Gemini) analyzes the data and generates the JSON report.
4. **Rendering:** HTMX takes the JSON response and dynamically builds the UI, mapping out the sub-projects, the lifespan, and the ghost's testimony.

---

## 🔄 Local vs Cloud AI

The app has a built-in fallback mechanism to ensure it never crashes:

```python
try:
    # 1. Try to use local Ollama (private, runs on your laptop)
    return await _call_ollama(prompt)
except Exception:
    # 2. If Ollama is offline or out of memory, fallback to Gemini API
    return await _call_google(prompt)
```

This makes the app **local-first** for sensitive/private repos, but fully **cloud-ready** for deployment on Render's free tier (which cannot run a 4GB local model).

---

## 🔐 Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `AI_PROVIDER` | `local` | Set to `local` (tries Ollama first) or `api` (forces Gemini). |
| `OLLAMA_MODEL` | `gemma3:4b` | The local model to use. |
| `GOOGLE_MODEL` | `gemini-2.5-flash` | The cloud model to use. |
| `GITHUB_TOKEN` | — | Required to avoid GitHub rate limits. |
| `GOOGLE_API_KEY` | — | Required for the cloud fallback. |

---

## 🚀 Deployment

Deployed on **Render** with `AI_PROVIDER=api` (since Render cannot host a local LLM). 

### Render Configuration
| Setting | Value |
| :--- | :--- |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Env Vars** | `AI_PROVIDER=api`, `GOOGLE_API_KEY`, `GOOGLE_MODEL=gemini-2.5-flash`, `GITHUB_TOKEN` |

---

## 📈 What I Learned

1. **LLMs struggle with large context JSON.** Sending a massive file tree to a small local model (`gemma3:4b`) caused it to hallucinate invalid JSON. The solution was enforcing a strict JSON schema and building a bulletproof Python parser that extracts the JSON block even if the model writes markdown around it.
2. **Monorepos require checklists.** To stop the AI from skipping sub-folders, I had to programmatically extract the `top_level_folders` from the GitHub API and inject them into the prompt as a mandatory checklist.
3. **Local-first is hard but worth it.** Running local models is great for privacy, but context window limits are a real constraint. Building the seamless fallback to Gemini made the app infinitely more reliable.
4. **HTMX is perfect for AI.** The ability to send a form, show a loading spinner ("Summoning the ghost..."), and swap the resulting HTML without a page reload creates a snappy, modern UX with zero JavaScript.

---

## 🗺️ Future Improvements

- **File-by-File Breakdown:** Allow users to click on a specific file in the UI to see a localized explanation of what it does.
- **Dependency Graph:** Use static analysis to generate a visual graph of how the sub-projects import each other.
- **Code Search:** Add a feature to search for `TODO:` or `FIXME:` comments across the entire repo and display them in the "Abandonment Evidence" section.

---

## 🤝 Connect With Me

- **GitHub**: [arpitasi1gh](https://github.com/arpitasi1gh)
- **LinkedIn**: [Arpita Singh](https://linkedin.com/in/arpitasi1gh)

---

## 📝 License

MIT. See [LICENSE](LICENSE).

---

**Built with 🪦 by Arpita Singh**  
*"Every dead repo has a story. The AI just tells it."*
