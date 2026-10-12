# 🌿 Greenstep – Predict When to Go Outside

> A local-first AI app that answers one question: **when should you go outside today, and where?** You give it four numbers. It finds a real place near you and writes one specific action for that window.

🔗 **Live Demo:** `https://greenstep.onrender.com` _(replace after deploy)_
📊 **Repository:** `https://github.com/arpitasi1gh/greenstep`

![Status](https://img.shields.io/badge/Status-Hacktoberfest_Submission-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-000000?style=for-the-badge)
![Gemma](https://img.shields.io/badge/Gemma-Google_AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![SerpApi](https://img.shields.io/badge/SerpApi-Google_Maps-4285F4?style=for-the-badge&logo=googlemaps&logoColor=white)
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
        <li><a href="#-how-it-works">🧠 How It Works</a></li>
        <li><a href="#-local-vs-cloud-ai">🔄 Local vs Cloud AI</a></li>
        <li><a href="#-caching">⚡ Caching</a></li>
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

Every "go outside" reminder tells you the same thing: take a break, get some air, go for a walk. The advice is correct and useless.

You already know you should go outside. The problems are:

- **When?** Nothing tells you *this* is the moment.
- **Where?** "A nearby park" isn't a place. A name and a distance is.
- **What?** "Go for a walk" isn't an action. "Walk to Tartinery, order a filter coffee, sit outside for 20 minutes" is.

**Greenstep answers all three.** You give it four inputs — where you are, how much you slept, how much screen time you've had, and your mood. It:

1. Geocodes your location and fetches real weather
2. Finds real cafes, parks, and walking spots from Google Maps
3. Writes one specific, startable action with a first step and a fallback

The whole thing is short and finishable. No streaks, no badges, no dashboard.

> **What Now?** — you enter energy and minutes, AI picks a task
> **Greenstep** — you enter context, app finds a real place and writes a specific action

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **📍 Real places via SerpApi** | Queries Google Maps for cafes, parks, and walking spots near your coordinates. No invented place names. |
| **🌤️ Live weather** | Geocodes your city with Nominatim and pulls current temperature and conditions from Open-Meteo. No API keys required for either. |
| **✍️ Gemma writes the action** | Combines window, weather, place, and mood into one specific sentence with a first step and a fallback. |
| **🔄 Local-first AI** | Runs Gemma 3 4B through Ollama on your machine by default. Nothing leaves your laptop. |
| **☁️ Cloud fallback** | One env var switches to Google AI Studio's Gemma endpoint — same model family, same prompt, same output. |
| **⚡ Input-keyed cache** | Re-submitting the same inputs returns the cached result instantly. Different inputs recompute. No wasted SerpApi credits. |
| **🌙 Dark-only UI** | Custom dark theme with emerald accents, ambient glow, and a focus state on every input. |
| **📱 Responsive** | Works on desktop and mobile. |

---

## 🧑‍💻 Tech Stack

### **Backend & AI**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[FastAPI](https://fastapi.tiangolo.com/)** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | Async web framework serving HTML and handling form posts. |
| **[Ollama](https://ollama.com/)** | ![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge) | Local inference runtime. Default path. |
| **[Gemma 3 4B](https://ai.google.dev/gemma)** | ![Gemma](https://img.shields.io/badge/Gemma-3_4B-8E75B2?style=for-the-badge) | Open-weight model. Runs locally via Ollama, or in the cloud via Google AI Studio. |
| **[httpx](https://www.python-httpx.org/)** | ![httpx](https://img.shields.io/badge/httpx-Async-2C5BB4?style=for-the-badge) | Async HTTP client for every external call. |
| **[SerpApi](https://serpapi.com/)** | ![SerpApi](https://img.shields.io/badge/SerpApi-Google_Maps-4285F4?style=for-the-badge) | Real place lookup. |

### **External APIs (no keys needed)**

| Service | Used for | Key required? |
| :--- | :--- | :--- |
| **[Nominatim](https://nominatim.openstreetmap.org/)** | Geocoding city names → lat/lon | No |
| **[Open-Meteo](https://open-meteo.com/)** | Current weather by coordinates | No |
| **[SerpApi](https://serpapi.com/)** | Google Maps place search | Yes (100 searches/month free) |
| **[Google AI Studio](https://aistudio.google.com/)** | Cloud Gemma inference | Yes (only in `AI_PROVIDER=api` mode) |

### **Storage & Tooling**

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[SQLite](https://sqlite.org/)** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white) | Input-keyed cache. One file. No migrations, no ORM. |
| **[uv](https://github.com/astral-sh/uv)** | ![uv](https://img.shields.io/badge/uv-Astral-DE5FE9?style=for-the-badge) | Dependency resolution and lockfile management. |
| **[Render](https://render.com/)** | ![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white) | Hosting with auto-deploy from GitHub and env var management. |
| **[Git](https://git-scm.com/) & [GitHub](https://github.com/)** | ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white) | Version control. |

---

## 📂 Project Structure

```text
greenstep/
├── data/
│   └── greenstep.db                  # SQLite cache (gitignored)
├── src/
│   └── greenstep/
│       ├── __init__.py
│       ├── main.py                   # FastAPI app, routes, HTML shell
│       ├── ai_provider.py            # Local Ollama / cloud Google AI switch
│       ├── weather.py                # Nominatim geocoding + Open-Meteo
│       ├── places.py                 # SerpApi Google Maps wrapper
│       ├── cache.py                  # Input-keyed SQLite cache
│       └── static/
│           └── style.css             # Dark-only theme
├── .env                              # API keys (gitignored)
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

The whole app is a single Python package. Templates are inline f-strings — no Jinja2 templating layer, no `templates/` folder, no build step. Static assets live inside the package so paths resolve the same in local and deployed environments.

---

## ⚙️ Quick Start (Local Development)

### 0. Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com) installed (for local mode)

### 1. Clone & Install

```bash
git clone https://github.com/arpitasi1gh/greenstep.git
cd greenstep
uv sync
```

### 2. Pull the Model

```bash
ollama pull gemma3:4b
ollama serve
```

Leave `ollama serve` running in one terminal.

### 3. Set Up `.env`

Create a file called `.env` in the project root:

```
AI_PROVIDER=local
SERPAPI_KEY=your_serpapi_key
GOOGLE_API_KEY=your_google_key
GOOGLE_MODEL=gemma-4-26b-a4b-it
```

Only `SERPAPI_KEY` is strictly required. `GOOGLE_API_KEY` is used only when `AI_PROVIDER=api`.

### 4. Run the Server

```bash
uv run uvicorn greenstep.main:app --reload
```

Server runs at `http://127.0.0.1:8000`.

### 5. Open Your Browser

Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000). You'll see a four-field form. Submit it, and after a few seconds (10–25s on the first call), you'll get a prediction card with a real place, an action, a first step, and a fallback.

---

## 🧠 How It Works

### Request Flow

1. **User submits the form** — location, sleep hours, screen time, mood.
2. **Check the cache** — if the same inputs were submitted before today, return the stored payload instantly. No API calls.
3. **Geocode** — Nominatim converts "Delhi" → latitude, longitude.
4. **Fetch weather** — Open-Meteo returns current temperature and a simplified label (`mild`, `hot`, `cold`, `rainy`).
5. **Find places** — SerpApi queries Google Maps for cafes and parks within a 14-zoom radius of the coordinates.
6. **Write the action** — Gemma receives location, weather, mood, and the top result. It returns a five-field JSON object.
7. **Cache the result** — keyed on the exact inputs. Re-submitting is instant.
8. **Render** — the action card, place chip, and footer are assembled in `main.py` and returned as HTML.

### The Prompt

The system prompt enforces behavior with hard rules:

```text
- NEVER use vague references. Not "a nearby trail", "the river".
- NEVER make the user decide. Bad: "Choose a trail".
- NEVER use these words: might, could, perhaps, simply, just,
  opportunity, movement, wellness, mindful, conducive, stillness.
- duration_minutes between 10 and 45. Default 25.
- You are given "nearest_place" with a real name. Use it.
- first_step must be what you do BEFORE leaving. Shoes, keys, water.
- fallback must be a smaller OUTDOOR action. Never indoor.
```

The banned-words list came from real failures. Gemma 3 4B kept writing "conducive to stillness" and "simply take a walk" until those exact words were named. Small models follow concrete forbiddances better than tone descriptions.

---

## 🔄 Local vs Cloud AI

The entire inference layer is one module (`ai_provider.py`) with one switch:

```python
AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
```

**`local`** — calls Ollama at `http://localhost:11434/api/generate` with `format: "json"`. The model runs on your machine. No data leaves it. First call takes 5–15s (model load into RAM), subsequent calls 2–6s.

**`api`** — calls Google AI Studio's Gemma endpoint. Same prompt, same output schema, same code path downstream. Faster response, but requires a key and sends the context to Google.

Same model family, two runtimes. One env var decides.

### Gemma on the Gemini API has three quirks

These cost real debugging time and are worth documenting:

1. It doesn't accept `system_instruction`. Instructions must be folded into the user message.
2. It doesn't accept `responseMimeType: "application/json"`. There is no JSON mode — the prompt enforces the format, and the parser has to be forgiving.
3. It doesn't accept `thinkingConfig`, even though the model metadata reports `thinking: true`.

The parser (`_parse_json` in `ai_provider.py`) strips markdown fences, cuts preamble before the first `{`, and cuts trailing text after the last `}`. That's what makes a small open model usable for structured output.

---

## ⚡ Caching

Every prediction is keyed on the exact inputs that produced it:

```python
def _key(location, sleep, screen, mood):
    raw = f"{date.today().isoformat()}|{location}|{sleep}|{screen}|{mood}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
```

Stored in SQLite at `data/greenstep.db`.

- **Same inputs, same day** → instant response from cache
- **Different inputs** → recompute (geocode + weather + places + Gemma)
- **Same inputs, next day** → recompute (the date is part of the key, so weather and places are fresh)

This exists because each submission costs one SerpApi search against a 100/month free tier. Without caching, testing burns credits in an hour. With it, only unique input combinations cost a credit.

---

## 🔐 Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `AI_PROVIDER` | `local` | `local` (Ollama) or `api` (Google AI Studio) |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama endpoint |
| `OLLAMA_MODEL` | `gemma3:4b` | Local model name |
| `GOOGLE_API_KEY` | — | Required only when `AI_PROVIDER=api` |
| `GOOGLE_MODEL` | `gemma-4-26b-a4b-it` | Cloud model name |
| `SERPAPI_KEY` | — | Required always (places lookup) |

---

## 🚀 Deployment

Deployed on **Render** with `AI_PROVIDER=api`. Render's free tier has 512 MB RAM and no GPU — Ollama can't run there. The cloud switch is what makes deployment possible without changing the architecture.

### Render Configuration

| Setting | Value |
| :--- | :--- |
| **Runtime** | Python 3 |
| **Build Command** | `pip install uv && uv sync` |
| **Start Command** | `uv run uvicorn greenstep.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

### Environment Variables on Render

Set these in the Render dashboard under **Environment**:

```
AI_PROVIDER=api
GOOGLE_API_KEY=...
GOOGLE_MODEL=gemma-4-26b-a4b-it
SERPAPI_KEY=...
```

### Deploy Steps

1. Push to GitHub:

```bash
git add .
git commit -m "deploy"
git push origin main
```

2. Render → **New +** → **Web Service** → connect the repo.

3. Paste the build and start commands above.

4. Add the four env vars.

5. **Create Web Service.** First build takes ~3 minutes.

---

## 📈 What I Learned

Building **Greenstep** taught me:

1. **Prompt engineering is mostly constraint design.** The hard part wasn't getting Gemma to write well — it was stopping it from writing "a quiet walk might be a gentle way to enjoy the mild weather." Naming banned words worked better than describing a desired tone. Small models follow concrete forbiddances.

2. **Real data beats clever prompts.** Gemma kept inventing "the closest park gate" until SerpApi gave it a real cafe name. Once the context had `nearest_place: {name: "ROOTED GROUNDS CAFE", rating: 5}`, the action became specific automatically. No prompt tweak would have fixed that.

3. **Local-first + cloud fallback is a real architecture, not a hack.** One env var, one branch, same code path. The local-first story stays honest for anyone cloning the repo, and the Render deployment still works.

4. **Gemma on the Gemini API has sharp edges.** Three of them, all documented above. Reading the docs would have saved half a day, but hitting them and writing them down is what makes this README useful to the next person.

5. **Input-keyed caching solves the "why is this expensive" problem.** My first design cached per-day, which meant I had to manually clear it between tests. Keying on inputs means the cache is invisible — it just works, and SerpApi credits last.

6. **Render's free tier has no GPU, and that's fine.** Once the inference layer was abstracted, deployment was just a matter of setting `AI_PROVIDER=api`. The architecture decision made the deployment decision trivial.

7. **Server-rendered HTML was the right call.** No React, no build step, no hydration. The whole app fits in about 400 lines of Python plus one CSS file.

8. **Writing this README clarified the design.** Explaining why the prompt is written the way it is forced me to check whether it actually was — and to cut the parts that weren't true.

---

## 🗺️ Future Improvements

| Phase | Feature | Why |
| :--- | :--- | :--- |
| **Near-term** | "I did it" feedback loop | Log outcomes so the app can reference past behavior in future prompts |
| **Near-term** | Weather-aware fallback | If it's raining, offer an indoor option within the same framework |
| **Mid-term** | TabPFN prediction layer | Predict the best window from a history CSV instead of asking the user |
| **Mid-term** | Weekly summary | Show which windows actually produced outdoor time |
| **Long-term** | Per-user isolation | Cookie-scoped caches so one deployment serves multiple people |
| **Long-term** | Local TabPFN (GPU) | Remove the cloud dependency for prediction too |

The TabPFN layer was planned and cut. Without a real history to train on, it would have been a fake feature. Recording outcomes first is the honest path to it.

---

## 🤝 Connect With Me

Built for the [Hacktoberfest Open-Source AI Challenge: Week 1 — Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05).

- **LinkedIn**: [Arpita Singh](https://linkedin.com/in/arpitasi1gh)
- **GitHub**: [arpitasi1gh](https://github.com/arpitasi1gh)
- **Email**: arpitasi1gh@gmail.com

---

## 📝 License

MIT. See [LICENSE](LICENSE).

---

## ⭐ Show Your Support

If this helped you understand local-first AI design, the Gemma-via-Ollama path, or how to build a small server-rendered app that doesn't need a framework, give it a ⭐.

---

**Built with 🌿 by Arpita Singh**
_"When, where, what. Three answers, one page."_