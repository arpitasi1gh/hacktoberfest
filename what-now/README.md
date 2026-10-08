# ❀ What Now? – Local-First AI Next-Action Coach

> A local-first AI assistant that turns your energy, available time, and task list into **one concrete next action**. No hosted AI, API keys, or cloud model calls.

🔗 **Repo:** [https://github.com/arpitasi1gh/hacktoberfest/tree/main/what-now](https://github.com/arpitasi1gh/hacktoberfest/tree/main/what-now)   
📝 **DEV Post:** [Hacktoberfest 2026 Weekend Challenge Submission - 1](https://dev.to/arpitasi1gh/what-now-a-local-first-ai-next-action-coach-for-a-tired-college-student-2ec6)

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
        <li><a href="#-why-local">🔒 Why Local</a></li>
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

## 💡 The Problem I Solved

A friend of mine — a 20-year-old CS student — had a schedule that looked fine on paper and fell apart every evening.

She knew what mattered. A DBMS assignment due tomorrow. Placement prep she was behind on. A gym she paid for and didn't visit. A real need to rest. But at 7:30 PM, after a full day of college, the gap between *knowing* and *starting* is where the evening disappeared. One reel became ten. "I'll start after this episode" became three.

The problem wasn't her priorities. It was **deciding what to start**. Every planner she'd tried handed her a list of twelve things and called it clarity — which is the same problem wearing a nicer font.

**What Now? is my solution.** It takes her current context (energy, minutes available, her tasks) and returns exactly **one action** — with a reason, a two-minute first step, a timebox, and a fallback. She acts on it, marks it done/skip/blocked, and the app remembers.

> **Core hypothesis:** Better context → better next-action decision → lower initiation friction → more execution.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🌿 Local-First AI** | Powered by Gemma 3 4B via Ollama. No cloud, no API keys, no usage bills. |
| **🎯 One Action, Not a List** | The model is constrained to return exactly one task with a startable first step. |
| **⚡ Context-Aware** | Respects energy level (1–5), available minutes, deadlines, and task energy cost. |
| **🔐 Private by Default** | Tasks, deadlines, and history stay local; public URLs in notes are fetched to read linked references. |
| **📝 Task Notes & Links** | Add specific context and public links; readable page text is extracted locally to ground suggestions. |
| **🔁 Feedback Loop** | Done / Skip / Blocked outcomes are logged and shown in a live activity panel. |
| **📚 Progress-Aware References** | Linked-page excerpts prioritize the next named section or the section after a completed milestone, with source and excerpt shown on the suggestion card. |
| **📊 Today's Stats** | Real-time counters for done, skipped, and blocked actions. |
| **🌱 Rest-Aware** | If energy is low or the list is empty, it suggests rest — not fabricated work. |
| **🔁 Swappable Models** | One env var swaps Gemma for Qwen, Llama, or any Ollama-compatible model. |
| **🧾 Account-Scoped** | Passwords hashed with PBKDF2-HMAC-SHA256, sessions via signed HTTP-only cookies. |

---

## 🧑‍💻 Tech Stack

### **Backend & AI**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[Python 3.13](https://www.python.org/)** | ![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white) | Core language. |
| **[FastAPI](https://fastapi.tiangolo.com/)** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | Async web framework with clean routing and dependency injection. |
| **[Ollama](https://ollama.com/)** | ![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge) | Local inference runtime. Exposes a plain HTTP API. |
| **[Gemma 3 4B](https://ai.google.dev/gemma)** | ![Gemma](https://img.shields.io/badge/Gemma-3_4B-4285F4?style=for-the-badge&logo=google&logoColor=white) | Open-weight instruction model. Default engine. |
| **[httpx](https://www.python-httpx.org/)** | ![httpx](https://img.shields.io/badge/httpx-Async_Client-2C5BB4?style=for-the-badge) | Async HTTP client for calling Ollama. |

### **Frontend & Templating**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[Jinja2](https://jinja.palletsprojects.com/)** | ![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge) | Server-rendered templates. No SPA build step. |
| **Browser Fetch API** | Server-rendered updates without navigating away from the dashboard. |
| **[Uvicorn](https://www.uvicorn.org/)** | ![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=for-the-badge) | ASGI server with hot reload. |

### **Storage & Tooling**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[SQLite](https://sqlite.org/)** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white) | Zero-config embedded database. One file. |
| **[uv](https://github.com/astral-sh/uv)** | ![uv](https://img.shields.io/badge/uv-Dependency_Manager-DE5FE9?style=for-the-badge) | Fast dependency resolution and lockfile management. |
| **[Git](https://git-scm.com/) & [GitHub](https://github.com/)** | ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white) | Version control and hosting. |

---

## 📂 Project Structure

```text
what-now/
├── data/
│   └── whatnow.db                    # SQLite database (gitignored)
├── src/
│   └── what_now/
│       ├── __init__.py
│       ├── main.py                   # FastAPI app + startup
│       ├── config.py                 # Environment-driven settings
│       ├── database.py               # Schema + queries
│       ├── dependencies.py           # Auth & DB dependencies
│       ├── prompts.py                # System prompt + user prompt builder
│       ├── agent.py                  # Ollama call + JSON parsing
│       ├── web_context.py             # Safe, bounded extraction of linked page text
│       ├── auth.py                   # Password hashing, session cookies
│       ├── web.py                    # Shared template/static helpers
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── pages.py              # Dashboard and theme/history actions
│       │   ├── tasks.py              # /tasks/*
│       │   ├── suggestions.py        # /checkin, /feedback
│       │   └── accounts.py           # /login, /signup, /logout
│       ├── templates/
│       │   ├── index.html            # Main page
│       │   ├── auth.html             # Login / signup
│       │   ├── _action_card.html     # AI suggestion fragment
│       │   ├── _history.html         # Recent activity panel
│       │   ├── _stats.html           # Today's stats strip
│       │   └── _task_list.html       # Task list fragment
│       └── static/
│           ├── css/style.css
│           └── images/botanical.svg
├── tests/
│   └── __init__.py
├── pyproject.toml
├── uv.lock
└── README.md
```

This is a single Python package: routers, Jinja templates, and static assets live together under `src/what_now`. The signed-in interface is one dashboard. Task, suggestion, theme, and history endpoints are form handlers—not separate task pages—and dashboard forms use the browser Fetch API to replace rendered content without a full-page navigation. Login and signup remain separate account pages.

---

## ⚙️ Quick Start (Local Development)

### 0. Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com) installed

### 1. Clone & Pull the Model

```bash
git clone https://github.com/arpitasi1gh/what-now.git
cd what-now

ollama pull gemma3:4b
ollama serve
```

Leave `ollama serve` running in one terminal.

### 2. Install Dependencies

In another terminal, from the project root:

```bash
uv sync
```

### 3. Run the App

```bash
uv run uvicorn what_now.main:app --reload
```

The server starts at <http://127.0.0.1:8000>.

### 4. Create an Account

Sign up with a valid email and password. Tasks and suggestions are scoped to your account.

### 5. Swap the Model (Optional)

```bash
WHATNOW_MODEL=qwen2.5:7b uv run uvicorn what_now.main:app --reload
```

Any model available via `ollama list` will work.

---

## 🧠 How It Works

### Request Flow

1. User opens the app and sets **energy** (1–5) and **minutes available**.
2. Server pulls the user's **active tasks** from SQLite.
3. Server builds a context JSON: current time, energy, minutes, task list.
4. `agent.get_next_action()` POSTs to Ollama's `/api/generate` with `format: "json"`.
5. Gemma returns one structured action with its rationale, first step, timebox, and fallback; the server sets the displayed timebox to the user's available minutes.
6. Server logs the action and returns the rendered action card.
7. User clicks **Done / Skip / Blocked**. The form submits in the background and the dashboard content updates in place.

### Why This Reduces Friction

The model isn't asked to be smart. It's asked to **pick one thing and phrase it**:

- One task. Never a list.
- One timebox. Exactly the duration the user says they have.
- One first step. Under 2 minutes.
- One fallback. In case energy drops further.

The intelligence lives in the **context**, not the model.

---

## 🎯 The Prompt

The system prompt (`prompts.py`) enforces the behavior with hard rules:

```text
- Pick exactly ONE task. Never list options.
- If a task has notes, use a specific detail from them in the action or first_step.
  Analyze the title, notes, progress, deadline, and available context together.
- Do not invent a file format or arbitrarily choose between options in task notes.
- Prefer the next unfinished milestone supported by the task notes and readable source.
- Match energy_cost to energy. If energy <= 2, do not pick energy_cost=high
  tasks unless the deadline is within 24 hours.
- The displayed timebox is set by the server to exactly the user's available time.
- If no tasks exist, or energy=1 and available_minutes < 10, return a rest
  action: walk, water, food, sleep. Do not invent work.
- Tone: peer, not coach. No "let's", no "you got this", no exclamation marks.
```

The model is also constrained at the sampler level via Ollama's `format: "json"`, which eliminates markdown fences and preamble from the output.

### Evaluating context and feedback changes

Run the offline suggestion-quality regression tests from the project directory:

```bash
uv run python -m unittest discover -s tests -v
```

These tests cover representative linked-study material, continuation after a completed section, source visibility, and a revised action after blocked feedback. They mock Ollama, so they verify the app's context and retry behavior—not the quality or variability of a particular installed model.

---

## 📊 Database Schema

### Entity Relationship

```text
┌───────┐         ┌──────────┐         ┌──────────┐
│ User  │ 1 ─── * │   Task   │ 1 ─── * │  Action  │
└───────┘         └──────────┘         └──────────┘
```

### `tasks` Table

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY | Auto-increment ID |
| `title` | TEXT | NOT NULL | Short task name |
| `notes` | TEXT | NOT NULL for new or edited tasks | Goal details and useful context |
| `deadline` | TEXT | NOT NULL for new or edited tasks | ISO 8601 datetime for the goal |
| `estimated_minutes` | INTEGER | NOT NULL | Daily time commitment in minutes |
| `energy_cost` | TEXT | CHECK (low/medium/high) | Mental or physical load |
| `importance` | INTEGER | CHECK (1–5) | Subjective priority |
| `progress` | INTEGER | 0–100 | Percent complete; 100% completes the task |
| `created_at` | TEXT | DEFAULT now | Timestamp |
| `completed_at` | TEXT | NULLABLE | Set when marked done |

### `actions` Table

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY | Auto-increment ID |
| `task_id` | INTEGER | FK → tasks(id) ON DELETE SET NULL | Linked task (null for rest actions) |
| `action` | TEXT | NOT NULL | Suggested action text |
| `why` | TEXT | NOT NULL | Model's reasoning |
| `first_step` | TEXT | NOT NULL | 2-minute micro-start |
| `timebox_minutes` | INTEGER | NOT NULL | Session duration |
| `fallback` | TEXT | NOT NULL | Lower-effort alternative |
| `outcome` | TEXT | CHECK (done/skip/blocked) | User's response |
| `created_at` | TEXT | DEFAULT now | Timestamp |

**Relationships**: One user owns many tasks. One task may have many suggested actions. Deleting a task preserves its action history (`ON DELETE SET NULL`).

---

## 🔒 Why Local

My friend's task list contains her exam schedule, placement prep, and personal goals. A closed API would mean shipping that to a server, paying per call, and trusting a vendor's logs.

Running Gemma locally via Ollama means task details and model prompts stay on the machine. If a task note contains a public HTTP(S) link, the app makes a bounded request to that site and passes the extracted page text to local Ollama; it does not send the task notes to the linked site.

- **No task details are sent to a cloud AI service.**
- **No API bills. No rate limits.**
- **Full auditability.** Every prompt is in the repo.
- **Model swappability.** When a better open model ships, she changes one env var.

Only public pages on standard HTTP(S) ports are read. URL reading is limited to four links per suggestion, follows only a few redirects, and caps page size and extracted text. The linked site will receive the normal page request and can observe its URL and the network address of the app host.

---

## 🔐 Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `WHATNOW_MODEL` | `gemma3:4b` | Ollama model name |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama endpoint |
| `WHATNOW_SECRET_KEY` | auto-generated | Session signing key |
| `WHATNOW_HTTPS_ONLY` | `false` | Set `true` behind HTTPS |

If `WHATNOW_SECRET_KEY` is not set, the app generates a local secret at `data/.session-secret` on first run. This file is gitignored.

---

## 📈 What I Learned

Building **What Now?** taught me:

1. **Prompt engineering is mostly constraint design.** The hard part wasn't getting the model to be smart — it was stopping it from being clever. Rules like "pick exactly one task" and "never ask a follow-up" did more for output quality than any temperature tuning.

2. **`format: "json"` is the single highest-leverage line in the codebase.** Before using Ollama's JSON mode, the model wrapped responses in markdown fences 1 in 5 times. After, zero across hundreds of calls.

3. **Keeping the server-rendered dashboard in place** gives the task list, suggestion, and stats one consistent update without a separate frontend build.

4. **Local inference has real costs.** First call after a cold start takes 5–15 seconds while the model loads into memory. Subsequent calls are 2–4 seconds. This shaped the entire UX: the check-in button disables itself, a "Thinking..." indicator appears, and users can't double-submit.

5. **SQLite is enough.** For a single-user local app, SQLite with `PRAGMA foreign_keys = ON` beats spinning up Postgres. The whole database is one file, and the schema fits in 40 lines.

6. **Context beats model size.** A 4B model with a well-structured context and a tight prompt produces more useful output than a 70B model with a vague ask. The intelligence lives in what you send, not what you use.

7. **Small models sometimes drop fields.** Even with explicit instructions, Gemma occasionally omits one of the five fields. The right fix was validation in `agent.py` (raise if fields are missing) rather than prompt tweaking.

8. **Writing the README clarified the design.** Explaining why the prompt is written the way it is forced me to check whether it actually was — and to fix the places where it wasn't.

---

## 🗺️ Future Improvements

- **Goal layer.** Group tasks under long-term goals (DSA, placement prep, core subjects) so the AI can prioritize by *which goal is falling behind*, not just which deadline is closest.
- **Feedback loop into the context.** Pass the last N outcomes back to the model so it can deprioritize tasks skipped twice and avoid re-suggesting tasks already done today.
- **Multi-user with shared goals.** Account support exists, but collaboration doesn't.
- **Streaming responses.** Show the model's tokens appearing live instead of waiting for the full JSON.
- **Electron wrapper.** Ship it as a double-clickable desktop app for non-developers.

---

## 🤝 Connect With Me

I built this for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01).

- **LinkedIn**: [Arpita Singh](https://linkedin.com/in/arpitasi1gh)
- **GitHub**: [arpitasi1gh](https://github.com/arpitasi1gh)
- **Email**: arpitasi1gh@gmail.com

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## ⭐ Show Your Support

If you found this useful, or if you're also a student fighting the "I know what I should do, I just can't start" problem — please give it a ⭐ on GitHub. It helps more than you'd think.

---

**Built with 🌿 by Arpita Singh**  
*"One action. Right now. Small enough to start."*
