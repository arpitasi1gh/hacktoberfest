# 🌿 Greenstep – Passive Outdoor Habit Predictor

> A full-stack AI application that predicts the **best window for you to go outside** based on your past behavior, finds a **real place nearby**, and writes a **specific action** — no forms, no queries, no friction.

🔗 **Live Demo:** `https://greenstep.onrender.com` _(replace after deploy)_
📊 **Repository:** `https://github.com/arpitasi1gh/greenstep`

![Status](https://img.shields.io/badge/Status-Hacktoberfest_Submission-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![TabPFN](https://img.shields.io/badge/TabPFN-Prior_Labs-7C3AED?style=for-the-badge)
![SerpApi](https://img.shields.io/badge/SerpApi-Google_Maps-4285F4?style=for-the-badge&logo=googlemaps&logoColor=white)
![Gemma](https://img.shields.io/badge/Gemma-Google_AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Deployment](https://img.shields.io/badge/Deployment-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

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
        <li><a href="#-api-endpoints">📡 API Endpoints</a></li>
        <li><a href="#-testing-locally">🧪 Testing Locally</a></li>
        <li><a href="#%EF%B8%8F-system-design">🏗️ System Design</a></li>
        <li><a href="#-data-schema">📊 Data Schema</a></li>
        <li><a href="#-deployment">🚀 Deployment</a></li>
      </ul>
    </td>
    <td width="33%">
      <ul>
        <li><a href="#-environment-variables">🔐 Environment Variables</a></li>
        <li><a href="#-what-i-learned">📈 What I Learned</a></li>
        <li><a href="#%EF%B8%8F-future-improvements">🗺️ Future Improvements</a></li>
        <li><a href="#-connect-with-me">🤝 Connect With Me</a></li>
        <li><a href="#-license">📝 License</a></li>
      </ul>
    </td>
  </tr>
</table>

---

## 💡 The Problem I Solved

Every "go outside" app asks the same question:

> _"How much energy do you have? How many minutes? What do you want to do?"_

And every time, the user has to **stop, think, and fill in a form** — which is exactly the friction that stops people from going outside in the first place.

**Greenstep flips this.**

Instead of asking, it **predicts**. It reads your past behavior — sleep, screen time, mood, weather, when you actually went out — and predicts the window today when you're most likely to go outside. Then it finds a real park or cafe near you, and writes one specific action.

No form. No query. No decision fatigue.

**The differentiator:** This is a **passive prediction** app, not an active query app. Every "I did it" tap makes tomorrow's prediction smarter.

> **What Now?** — user enters energy + minutes → AI suggests one task
> **Greenstep** — app reads history → TabPFN predicts best window → SerpApi finds real place → Gemma writes the action

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🧠 TabPFN Prediction** | Reads your 30-day history CSV and predicts the probability of going outside for each evening window today. |
| **📍 Real Places via SerpApi** | Fetches actual parks and cafes within walking distance using Google Maps engine. |
| **✍️ Gemma Action Writer** | Combines window + place + weather into one specific, gentle, actionable sentence. |
| **📊 Window Probability Chart** | Visual bar chart showing all candidate hours, with the best window highlighted. |
| **🔄 Self-Improving Loop** | "I did it" appends a new row to `history.csv` — tomorrow's prediction gets better. |
| **🌙 Dark Mode Only** | A carefully tuned dark UI with emerald accents, ambient glow, and reduced-motion support. |
| **📱 Fully Responsive** | Works on desktop, tablet, and mobile — tuned breakpoint at 420px. |
| **⚡ Zero Form Filling** | Open the app. See one action. That's the whole flow. |

---

## 🧑‍💻 Tech Stack

### **Backend**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[FastAPI](https://fastapi.tiangolo.com/)** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | Lightweight async web framework serving HTML + handling the `/done` POST. |
| **[Jinja2](https://jinja.palletsprojects.com/)** | ![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja&logoColor=white) | Server-side templating for the prediction and action cards. |
| **[TabPFN](https://priorlabs.ai/)** | ![TabPFN](https://img.shields.io/badge/TabPFN-Prior_Labs-7C3AED?style=for-the-badge) | Tabular foundation model that predicts the best outdoor window from history. |
| **[SerpApi](https://serpapi.com/)** | ![SerpApi](https://img.shields.io/badge/SerpApi-Google_Maps-4285F4?style=for-the-badge) | Fetches real parks and cafes via the Google Maps engine. |
| **[Gemma](https://ai.google.dev/gemma)** | ![Gemma](https://img.shields.io/badge/Gemma-Google_AI-8E75B2?style=for-the-badge) | Writes the final one-sentence action combining window, place, and weather. |
| **[Pandas](https://pandas.pydata.org/)** | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) | CSV loading and feature engineering for TabPFN input. |

### **Frontend**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[Jinja2 Templates](https://jinja.palletsprojects.com/)** | ![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge) | Server-rendered HTML — no client-side JS framework needed. |
| **[Custom CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)** | ![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) | Hand-written dark theme with CSS variables, ambient glow, and mobile breakpoints. |
| **[SVG Icons](https://heroicons.com/)** | ![SVG](https://img.shields.io/badge/SVG-Inline-FFB13B?style=for-the-badge&logo=svg&logoColor=white) | Inline SVG icons — no icon font, no extra dependency. |

### **DevOps & Tooling**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[uv](https://github.com/astral-sh/uv)** | ![uv](https://img.shields.io/badge/uv-Astral-DE5FE9?style=for-the-badge) | Ultra-fast Python package manager and virtualenv tool. |
| **[Render](https://render.com/)** | ![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white) | Backend hosting with auto-deploy from GitHub and env var management. |
| **[Git](https://git-scm.com/) & [GitHub](https://github.com/)** | ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white) | Version control and CI/CD triggers. |
| **[Environment Variables](https://12factor.net/config)** | ![Env](https://img.shields.io/badge/Env-Vars-ECD53F?style=for-the-badge) | Secure handling of API keys (never committed). |

---

## 📂 Project Structure

```text
greenstep/
├── data/
│   └── history.csv               # 30-day training data (generated by seed script)
├── scripts/
│   └── seed_history.py           # Generates plausible outdoor history CSV
├── src/
│   └── greenstep/
│       ├── __init__.py
│       ├── main.py               # FastAPI app + routes + static mount
│       ├── predictor.py          # TabPFN wrapper (predicts best window)
│       ├── places.py             # SerpApi Google Maps wrapper
│       ├── ai_provider.py        # Gemma action writer
│       └── history.py            # CSV read/write helpers
├── static/
│   └── css/
│       └── style.css             # Dark mode only, custom CSS
├── templates/
│   ├── base.html                 # Base layout
│   ├── index.html                # Main page (prediction + action)
│   └── _action_card.html         # Reusable action card partial
├── .env                          # Local keys (gitignored) — or export in shell
├── .gitignore
├── pyproject.toml                # uv-managed dependencies
└── README.md                     # This file
```

## ⚙️ Quick Start (Local Development)

### 0. Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- API keys for TabPFN, SerpApi, and Google AI Studio

### 1. Clone & Install

```bash
git clone https://github.com/arpitasi1gh/greenstep.git
cd greenstep
uv sync
```

### 2. Set API Keys (choose one)

**Option A — Export in terminal (recommended):**

```bash
export TABPFN_API_KEY="your_tabpfn_key"
export SERPAPI_API_KEY="your_serpapi_key"
export GOOGLE_API_KEY="your_google_key"
```

**Option B — Inline one-liner:**

```bash
TABPFN_API_KEY="xxx" SERPAPI_API_KEY="yyy" GOOGLE_API_KEY="zzz" \
  uv run uvicorn src.greenstep.main:app --reload
 ```

**Option C — Shell profile (persistent):**

```bash
echo 'export TABPFN_API_KEY="your_key"' >> ~/.zshrc
echo 'export SERPAPI_API_KEY="your_key"' >> ~/.zshrc
echo 'export GOOGLE_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Generate Training Data

```bash
uv run python scripts/seed_history.py
# Writes 150 rows to data/history.csv
```

### 4. Run the Server
```bash
uv run uvicorn src.greenstep.main:app --reload
```

Server runs at `http://localhost:8000`.

### 5. Open Your Browser

Navigate to [http://localhost:8000](http://localhost:8000). You should see:

- TabPFN's predicted best window (e.g., `18:00`, 78%)
- A real nearby place from SerpApi
- A Gemma-written action sentence
- An "I did it" button that appends to `history.csv`

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | Renders the home page with prediction, place, and action | ❌ |
| **POST** | `/done` | Appends the current prediction to `history.csv` as `went_outside=1` | ❌ |
| **GET** | `/static/css/style.css` | Serves the dark mode stylesheet | ❌ |

> Greenstep is intentionally **sessionless and formless**. There is no login, no signup, no database — just a CSV that grows with every "I did it" tap.

---

## 🧪 Testing Locally

### 1. Verify the CSV was generated

```bash
head -5 data/history.csv
wc -l data/history.csv
```

Expected: 5 sample rows + 151 lines total (150 rows + header).

### 2. Verify TabPFN auth

```bash
python -c "import os; print('OK' if os.getenv('TABPFN_API_KEY') else 'MISSING')"
```

Expected: `OK`.

### 3. Hit the home route

```bash
curl -s http://localhost:8000 | grep -o 'Best window today'
```

Expected: `Best window today`.

### 4. Hit the done route

```bash
curl -X POST http://localhost:8000/done -i
# Expect: HTTP/1.1 303 See Other
```

Then check `data/history.csv` grew by one row.

### 5. Test TabPFN directly

```bash
uv run python -c "
from src.greenstep.predictor import predict_best_window
result = predict_best_window(sleep_hours=7.2, screen_time_hours=4.5, mood=4, weather='mild')
print(result)
"
```

Expected: a dict with `hour`, `probability`, and `all_windows`.

---

## 🏗️ System Design

### High-level Architecture

```text
┌──────────────────────────────────┐       ┌────────────────────────────────────┐
│         Browser (User)           │       │      FastAPI (Render)              │
│                                  │       │                                    │
│  ┌────────────────────────────┐  │ HTTPS │  ┌──────────────────────────────┐  │
│  │   Jinja2 Rendered HTML     │◄─┼───────┼─►│      GET /  (home)           │  │
│  │   • Prediction card        │  │       │  │      POST /done (append)     │  │
│  │   • Action card            │  │       │  └──────────────┬───────────────┘  │
│  │   • I did it button        │  │       │                 ▼                  │
│  └────────────────────────────┘  │       │  ┌──────────────────────────────┐  │
│                                  │       │  │       predictor.py           │  │
│  • Dark mode only                │       │  │   (TabPFN + history.csv)     │  │
│  • Responsive (420px break)      │       │  └──────────────┬───────────────┘  │
│  • SVG icons, custom CSS         │       │                 ▼                  │
│                                  │       │  ┌──────────────────────────────┐  │
└──────────────────────────────────┘       │  │        places.py             │  │
                                           │  │   (SerpApi Google Maps)      │  │
                                           │  └──────────────┬───────────────┘  │
                                           │                 ▼                  │
                                           │  ┌──────────────────────────────┐  │
                                           │  │      ai_provider.py          │  │
                                           │  │   (Gemma action writer)      │  │
                                           │  └──────────────────────────────┘  │
                                           └────────────────────────────────────┘
                                                            │
                                                            ▼
                                           ┌────────────────────────────────────┐
                                           │       External APIs (HTTPS)        │
                                           │  • TabPFN Cloud (priorlabs.ai)     │
                                           │  • SerpApi (serpapi.com)           │
                                           │  • Google AI (aistudio.google)     │
                                           └────────────────────────────────────┘
```

### Request Flow (Home Page)

1. **Browser** → `GET /`
2. **FastAPI** → `predict_best_window(sleep, screen, mood, weather)`
3. **predictor.py** → loads `history.csv` → encodes features → calls TabPFN cloud → returns best hour + probability
4. **places.py** → calls SerpApi Google Maps → returns nearest parks/cafes
5. **ai_provider.py** → sends window + place + weather to Gemma → returns one action sentence
6. **Jinja2** → renders `index.html` with prediction, place, and action
7. **Browser** → user reads the action, clicks "I did it"
8. **POST /done** → appends a row to `history.csv` → tomorrow's prediction improves

### Why This Design

- **No database** — a 30-row CSV is TabPFN's training set. Adding Postgres would be overkill for a habit tracker.
- **Server-rendered** — no React, no build step, no state hydration. The whole app fits in ~400 lines of Python.
- **Single external call per provider** — TabPFN: 1 call. SerpApi: 1 call. Gemma: 1 call. Free tiers cover hundreds of sessions.
- **Failure-tolerant** — every provider has a fallback (TabPFN returns `18:00 / 50%`, SerpApi returns "Riverside Park", Gemma returns a templated sentence).

---

## 📊 Data Schema

Greenstep uses a **flat CSV** instead of a relational database. This keeps the ML pipeline simple and the deployment footprint tiny.

### `data/history.csv`

| Column | Type | Range / Values | Description |
| :--- | :--- | :--- | :--- |
| `date` | ISO string | `YYYY-MM-DD` | The day this observation belongs to |
| `hour` | int | `16, 17, 18, 19, 20` | Evening window (24-hour) |
| `sleep_hours` | float | `4.0 – 10.0` | Hours slept the night before |
| `screen_time_hours` | float | `1.0 – 12.0` | Total screen time that day |
| `mood` | int | `1 – 5` | Self-reported mood (1 = bad, 5 = great) |
| `weather` | string | `mild`, `hot`, `cold`, `rainy` | Weather category |
| `went_outside` | int | `0` or `1` | **Target variable** — did the user go outside? |

### How TabPFN Uses It

```python
# Features (X)
X = [
    [hour, sleep_hours, screen_time_hours, mood, weather_encoded, weekday]
    for row in history
]

# Target (y)
y = [went_outside for row in history]

# Predict probability of going outside for each candidate hour today
model = TabPFNClassifier()
model.fit(X, y)
probs = model.predict_proba(today_candidates)
```

TabPFN treats this as **binary classification** — the natural fit for a yes/no outcome. It works well with small tabular datasets (30–300 rows), which is exactly what a personal habit log looks like.

### Relationship to Relational Design

| HuntTrack (relational) | Greenstep (flat CSV) |
| :--- | :--- |
| `User` → `Application` (1:many) | `date` → `hour` (1:many, implicit) |
| Postgres + Prisma ORM | CSV + Pandas |
| Multi-user, sessions, JWT | Single-user, sessionless |
| Indexes, foreign keys, migrations | Header row, gitignored |

The CSV is intentionally **gitignored** so each user's behavior stays local. The seed script generates a fresh 30-day file on first run.

---

## 🚀 Deployment

- **Host**: [Render](https://render.com) — connected to GitHub, auto-deploys on `main` push.
- **Runtime**: Python 3.11 with `uv` for fast installs.
- **Static files**: Served by FastAPI via `app.mount("/static", ...)`.
- **Persistence**: Render's free tier has an **ephemeral filesystem** — `data/history.csv` resets on each deploy. For a hackathon submission this is fine; for production, mount a [Render Disk](https://render.com/docs/disks) or swap CSV for SQLite.

### Render Configuration

| Setting | Value |
| :--- | :--- |
| **Runtime** | Python |
| **Build Command** | `pip install uv && uv sync` |
| **Start Command** | `uv run uvicorn src.greenstep.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

### `render.yaml` (optional, for blueprint deploys)

```yaml
services:
  - type: web
    name: greenstep
    runtime: python
    buildCommand: pip install uv && uv sync
    startCommand: uv run uvicorn src.greenstep.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: TABPFN_API_KEY
        sync: false
      - key: SERPAPI_API_KEY
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
```

### Deploy Steps

1. Push your code to GitHub:

```bash
git add .
git commit -m "Greenstep ready for deployment"
git push origin main
```

2. Go to [render.com](https://render.com) → **New +** → **Web Service** → connect your repo.

3. Use the build and start commands from the table above.

4. Add the three env vars in the **Environment** tab.

5. Click **Create Web Service**. First build takes ~3 minutes.

6. Once live, hit the URL. You should see the same page you saw locally.

---

## 🔐 Environment Variables

### Development (Terminal)

```bash
export TABPFN_API_KEY="your_tabpfn_key"
export SERPAPI_API_KEY="your_serpapi_key"
export GOOGLE_API_KEY="your_google_key"
```

Or inline:

```bash
TABPFN_API_KEY="xxx" SERPAPI_API_KEY="yyy" GOOGLE_API_KEY="zzz" \
  uv run uvicorn src.greenstep.main:app --reload
```

### Production (Render Dashboard)

| Variable | Value | Where to Set |
| :--- | :--- | :--- |
| `TABPFN_API_KEY` | From [platform.priorlabs.ai](https://platform.priorlabs.ai) | Render → Environment |
| `SERPAPI_API_KEY` | From [serpapi.com/manage-api-key](https://serpapi.com/manage-api-key) | Render → Environment |
| `GOOGLE_API_KEY` | From [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Render → Environment |

### Getting Each Key

| Provider | Sign-up URL | Free Tier |
| :--- | :--- | :--- |
| **TabPFN** | [platform.priorlabs.ai](https://platform.priorlabs.ai) | Free tier for `tabpfn-client` |
| **SerpApi** | [serpapi.com/users/sign_up](https://serpapi.com/users/sign_up?plan=free) | 100 searches / month |
| **Google AI (Gemma)** | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Free with rate limits |

### `.gitignore`

```gitignore
__pycache__/
*.pyc
.env
.venv/
uv.lock
data/history.csv
```

---

## 📈 What I Learned

Building **Greenstep** taught me:

1. **TabPFN is genuinely useful for small tabular data**: I'd only used tree-based models (XGBoost, Random Forest) before. TabPFN's in-context learning on a 150-row CSV produced sensible probability curves without any hyperparameter tuning. It's the right tool for a personal habit log.

2. **The architecture is the product**: The shift from "user fills a form" to "app reads history" wasn't a UI change — it changed what the app *is*. What Now? is a query tool. Greenstep is a prediction tool. Same AI stack, completely different product.

3. **Every external API needs a fallback**: TabPFN, SerpApi, and Gemma all fail sometimes (network, rate limits, auth). Every provider in Greenstep has a hardcoded fallback so the page never crashes — it just degrades gracefully.

4. **Server-rendered HTML is underrated**: For a 3-card layout with no client-side state, Jinja2 + custom CSS beat React + Tailwind on every axis: fewer dependencies, faster cold starts, simpler deployment.

5. **CSV as a database is fine for single-user apps**: I resisted the urge to add Postgres. A 150-row CSV loads in microseconds, trains TabPFN instantly, and is trivially inspectable with `head`. The right database is often no database.

6. **Dark mode is a design constraint, not a toggle**: Building dark-only forced me to think about contrast, ambient glow, and color hierarchy from the start. The result reads better than a bolted-on dark theme.

7. **Deployment is where the real challenges begin**: Render's ephemeral filesystem, static file mounting, and env var injection all required debugging. I learned to test in a production-like environment early, not after writing all the code.

8. **Hacktoberfest values clarity over cleverness**: A submission with 8 small, well-named files beats a monolith. Reviewers can read `predictor.py`, `places.py`, and `ai_provider.py` independently and understand the pipeline in five minutes.

---

## 🗺️ Future Improvements

| Phase | Feature | Why |
| :--- | :--- | :--- |
| **Near-term** | Swap CSV for SQLite | Persist across Render deploys |
| **Near-term** | Real weather API (OpenWeatherMap) | Replace the hardcoded `weather` field |
| **Near-term** | Manual "didn't go" logging | Give TabPFN negative samples too |
| **Mid-term** | Per-user CSV via cookies | Let multiple users share one deployment |
| **Mid-term** | Push notifications at predicted window | Nudge the user at the right moment |
| **Mid-term** | Weekly summary chart | Show prediction accuracy over time |
| **Long-term** | Local TabPFN (GPU) | Remove the cloud dependency |
| **Long-term** | On-device fine-tuning | Personalize the model per user |
| **Long-term** | "Hunt" phase — multi-day planning | Predict the best *day* of the week, not just the hour |

---

## 🤝 Connect With Me

I built this to explore the intersection of **tabular ML** and **everyday habit design**. If you're working on TabPFN, Gemma, or passive prediction apps, let's connect.

- **LinkedIn**: [Arpita Singh](https://linkedin.com/in/arpitasi1gh)
- **GitHub**: [arpitasi1gh](https://github.com/arpitasi1gh)
- **Email**: arpitasi1gh@gmail.com

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## ⭐ Show Your Support

If this project helped you understand TabPFN, SerpApi + LLM integration, or how to design a passive-prediction app, please consider giving it a ⭐ on GitHub — it means a lot and helps others discover it.

---

**Built with ❤️ by Arpita Singh**
_"Predict the window. Find the place. Write the step."_