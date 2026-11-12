# ❀ What Now? – Local-First AI Next-Action Coach

> A local-first AI assistant that turns your energy, available time, and task list into **one concrete next action**. No hosted AI, API keys, or cloud model calls required to run it.

🔗 **Live Demo:** [https://what-now-g8eg.onrender.com](https://what-now-g8eg.onrender.com)  
📊 **Repository:** [https://github.com/arpitasi1gh/hacktoberfest/tree/main/what-now](https://github.com/arpitasi1gh/hacktoberfest/tree/main/what-now)   
✍️ **DEV Write-up:** [Hacktoberfest 2026 Weekend Challenge Submission](https://dev.to/arpitasi1gh/what-now-a-local-first-ai-next-action-coach-for-a-tired-college-student-2ec6)

![Status](https://img.shields.io/badge/Status-Working-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-000000?style=for-the-badge)
![Gemma](https://img.shields.io/badge/Gemma-3_4B-4285F4?style=for-the-badge&logo=google&logoColor=white)

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
        <li><a href="#-database-schema">📊 Database Schema</a></li>
        <li><a href="#-the-prompt">🎯 The Prompt</a></li>
        <li><a href="#-local-vs-cloud-ai">🔄 Local vs Cloud AI</a></li>
        <li><a href="#-environment-variables">🔐 Environment Variables</a></li>
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

<table>
  <tr>
    <td>
      <p align="center"><b>Demo Image 01</b></p>
      <img width="1470" height="878" alt="1-a" src="https://github.com/user-attachments/assets/797b9243-20c8-4bd5-a90e-624c246243c4" />
    </td>
    <td>
      <p align="center"><b>Demo Image 02</b></p>
      <img width="1470" height="912" alt="1-b" src="https://github.com/user-attachments/assets/f9a234b5-48b4-44ad-b6a1-d04e86388c6e" />
    <td>
      <p align="center"><b>Demo Image 03</b></p>
      <img width="1470" height="956" alt="1-c" src="https://github.com/user-attachments/assets/6281faae-4aaf-4759-b49f-687c9dbb5ee3" />
    </td>
    <td>
      <p align="center"><b>Demo Image 04</b></p>
      <img width="1470" height="917" alt="1-d" src="https://github.com/user-attachments/assets/52e3f125-51f3-4067-8f46-ab561e2e7e5f" />
    </td>
  </tr>
</table>

---

## 💡 The Problem I Solved

A friend of mine — a 20-year-old CS student — had a schedule that looked fine on paper and fell apart every evening.

She knew what mattered. A DBMS assignment due tomorrow. Placement prep she was behind on. A gym she paid for and didn't visit. A real need to rest. But at 7:30 PM, after a full day of college, the gap between *knowing* and *starting* is where the evening disappeared. One reel became ten. "I'll start after this episode" became three.

The problem wasn't her priorities. It was **deciding what to start**. Every planner she'd tried handed her a list of twelve things and called it clarity — which is the same problem wearing a nicer font.

**What Now? is my solution.** It takes her current context (energy, minutes available, her tasks) and returns exactly **one action** — with a reason, a two-minute first step, a timebox, and a fallback.

> **Core hypothesis:** Better context → better next-action decision → lower initiation friction → more execution.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🌿 Local-First AI** | Powered by Gemma 3 4B via Ollama by default. No cloud, no API keys, no usage bills. |
| **🎯 One Action, Not a List** | The model is constrained to return exactly one task with a startable first step. |
| **⚡ Context-Aware** | Respects energy level (1–5), available minutes, deadlines, and task energy cost. |
| **📝 Inline Task Editing** | Update details, deadlines, daily time commitments, and progress directly in the UI via HTMX. |
| **📊 Progress Sliders** | Drag the progress slider to 100%. The task instantly turns gray, gets a strikethrough, and moves to the bottom. |
| **📈 Daily Reset Stats** | Real-time counters for done, skipped, and blocked actions. Resets automatically at midnight local time. |
| **🔄 Auto-Fallback** | If Ollama isn't running, the app seamlessly falls back to Google AI Studio so it never crashes. |

---

## 🧑‍💻 Tech Stack

### **Backend & AI**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[Python 3.13](https://www.python.org/)** | ![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white) | Core language. |
| **[FastAPI](https://fastapi.tiangolo.com/)** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | Async web framework with clean routing. |
| **[Ollama](https://ollama.com/)** | ![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge) | Local inference runtime. |
| **[Gemma 3 4B](https://ai.google.dev/gemma)** | ![Gemma](https://img.shields.io/badge/Gemma-3_4B-4285F4?style=for-the-badge&logo=google&logoColor=white) | Open-weight instruction model. Default engine. |
| **[httpx](https://www.python-httpx.org/)** | ![httpx](https://img.shields.io/badge/httpx-Async_Client-2C5BB4?style=for-the-badge) | Async HTTP client for calling Ollama / Google AI. |

### **Frontend & Templating**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[Jinja2](https://jinja.palletsprojects.com/)** | ![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge) | Server-rendered templates. No SPA build step. |
| **[HTMX](https://htmx.org/)** | ![HTMX](https://img.shields.io/badge/HTMX-336699?style=for-the-badge) | Handles form submissions, OOB swaps, and inline editing without React. |
| **[Uvicorn](https://www.uvicorn.org/)** | ![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=for-the-badge) | ASGI server with hot reload. |

### **Storage & Tooling**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[SQLite](https://sqlite.org/)** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white) | Zero-config embedded database. One file. |
| **[uv](https://github.com/astral-sh/uv)** | ![uv](https://img.shields.io/badge/uv-Dependency_Manager-DE5FE9?style=for-the-badge) | Fast dependency resolution and lockfile management. |

---

## 📂 Project Structure

```text
what-now/
├── src/
│   └── what_now/
│       ├── __init__.py
│       ├── main.py                   # FastAPI app, routes, HTMX rendering
│       ├── db.py                     # SQLite schema and queries
│       ├── ai_service.py             # Ollama/Gemini logic and JSON parsing
│       ├── prompts.py                # System prompt for the AI
│       ├── templates/                # Jinja2 HTML templates
│       │   ├── index.html            # Dashboard
│       │   ├── _task_list.html       # Task list fragment
│       │   ├── _edit_task.html       # Inline edit form fragment
│       │   ├── _action_card.html     # AI suggestion fragment
│       │   ├── _task_progress.html   # Progress slider fragment
│       │   └── _stats.html           # Today's stats strip
│       └── static/
│           ├── style.css             # Botanical theme styling
│           └── images/botanical.svg
├── data/
│   └── whatnow.db                    # SQLite database (gitignored)
├── .env                              # API keys and settings (gitignored)
├── pyproject.toml
└── README.md
```

The project uses a modular structure but avoids over-engineering. It splits the database (`db.py`), AI logic (`ai_service.py`), and the web routes (`main.py`) while keeping the UI server-rendered with HTMX.

---

## ⚙️ Quick Start (Local Development)

### 0. Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com) installed

### 1. Clone & Pull the Model

```bash
git clone https://github.com/arpitasi1gh/hacktoberfest.git
cd hacktoberfest/what-now

ollama pull gemma3:4b
ollama serve
```
*(Leave `ollama serve` running in a separate terminal.)*

### 2. Install Dependencies

```bash
uv sync
```

### 3. Set Up `.env`
Create a `.env` file in the root:
```env
AI_PROVIDER=local
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-2.5-flash
```

### 4. Run the App

```bash
uv run uvicorn src.what_now.main:app --reload
```

The server starts at <http://127.0.0.1:8000>. There is no login. Just add a task and use the slider.

---

## 🧠 How It Works

1. **Check-in:** You set your current energy (1–5) and available minutes.
2. **Context:** The server pulls your active tasks from SQLite.
3. **Inference:** The context is sent to Ollama (or Gemini) with strict JSON constraints.
4. **Action:** The AI returns one action with a reason, a first step, a timebox, and a fallback.
5. **Feedback:** 
   - If you click "Done", it logs the action and increments the task's progress by 10%.
   - If you drag the task slider to 100%, it marks the task as completed. The UI instantly grays it out, strikes it through, and moves it to the bottom of the list.

### Why This Reduces Friction

The model isn't asked to be smart. It's asked to **pick one thing and phrase it**:

- One task. Never a list.
- One timebox. The duration you say you have.
- One first step. Under 2 minutes.
- One fallback. In case energy drops further.

The intelligence lives in the **context**, not the model.

---

## 🎯 The Prompt

The system prompt (`prompts.py`) enforces the behavior with hard rules:

```text
- Pick exactly ONE task. Never list options.
- If a task has notes, use a specific detail from them in the action or first_step.
- Prefer tasks with near deadlines over high-importance distant ones.
- Match energy_cost to energy. If energy <= 2, do not pick energy_cost=high tasks unless the deadline is within 24 hours.
- timebox_minutes must be <= the task's estimated_minutes (daily commitment).
- If no tasks exist, or energy=1 and available_minutes < 10, return a rest action: walk, water, food, sleep. Do not invent work.
- Tone: peer, not coach. No "let's", no "you got this", no exclamation marks.
- You MUST return the exact 'task_title' of the task you chose in the JSON response.
```

---

## 📊 Database Schema

We use two tables: `tasks` and `actions`.

### `tasks` Table
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary key |
| `title` | TEXT | Short task name |
| `notes` | TEXT | Context and goal details |
| `deadline` | TEXT | ISO 8601 datetime |
| `estimated_minutes` | INTEGER | Daily time commitment |
| `energy_cost` | TEXT | `low`, `medium`, or `high` |
| `importance` | INTEGER | Subjective priority (1–5) |
| `progress` | INTEGER | 0–100. Hitting 100 sets `completed_at`. |
| `completed_at` | TEXT | Timestamp when task hit 100% |

### `actions` Table
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary key |
| `task_id` | INTEGER | FK to `tasks` |
| `action` | TEXT | Suggested action text |
| `why` | TEXT | Model's reasoning |
| `first_step` | TEXT | 2-minute micro-start |
| `timebox_minutes` | INTEGER | Session duration |
| `fallback` | TEXT | Lower-effort alternative |
| `outcome` | TEXT | `done`, `skip`, or `blocked` |
| `created_at` | TEXT | Saved with `localtime` so stats reset at midnight. |

---

## 🔄 Local vs Cloud AI

The inference layer (`ai_service.py`) has a built-in fallback to ensure the app never crashes:

```python
try:
    # Try to use local Ollama
    return await _call_ollama(prompt)
except Exception:
    # If Ollama is offline, fallback to Google AI Studio
    return await _call_google(prompt)
```

This means you can run the app completely offline for privacy, but if you deploy it to the web, it will still work via the Google API. The frontend uses HTMX out-of-band (OOB) swaps to update the task list, counters, and AI card simultaneously without full page reloads.

---

## 🔐 Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `AI_PROVIDER` | `local` | `local` (tries Ollama) or `api` (skips local) |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama endpoint |
| `OLLAMA_MODEL` | `gemma3:4b` | Local model name |
| `GOOGLE_API_KEY` | — | Required for the API fallback |
| `GOOGLE_MODEL` | `gemini-2.5-flash` | Cloud model name |

---

## 📈 What I Learned

1. **Prompt engineering is mostly constraint design.** The hard part wasn't getting the model to be smart — it was stopping it from being clever. Rules like "pick exactly one task" did more for output quality than any temperature tuning.
2. **`format: "json"` is the single highest-leverage line in the codebase.** Before using Ollama's JSON mode, the model wrapped responses in markdown fences 1 in 5 times. After, zero across hundreds of calls.
3. **HTMX OOB swaps are incredibly powerful.** I was able to update the task list, the "Open" count badge, the stats, and the disabled state of the generate button all in a single response without writing complex JavaScript.
4. **Local inference has real costs.** First call after a cold start takes 5–15 seconds while the model loads into memory. This shaped the entire UX: the check-in button disables itself, a "Thinking..." indicator appears, and users can't double-submit.
5. **SQLite is enough.** For a single-user local app, SQLite with `PRAGMA foreign_keys = ON` beats spinning up Postgres.

---

## 🗺️ Future Improvements

- **Goal layer:** Group tasks under long-term goals (DSA, placement prep) so the AI prioritizes by *which goal is falling behind*.
- **Feedback loop into context:** Pass the last 3 outcomes back to the model so it can deprioritize tasks skipped twice.
- **Electron wrapper:** Ship it as a double-clickable desktop app for non-developers.
- **Streaming responses:** Show the model's tokens appearing live instead of waiting for the full JSON.

---

## 🤝 Connect With Me

I built this for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01).

- **LinkedIn**: [Arpita Singh](https://linkedin.com/in/arpitasi1gh)
- **GitHub**: [arpitasi1gh](https://github.com/arpitasi1gh)

---

## 📝 License

MIT. See [LICENSE](LICENSE).

---

**Built with 🌿 by Arpita Singh**  
*"One action. Right now. Small enough to start."*
