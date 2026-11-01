# 🪦 Repo Necromancer – The Ghost in the Codebase

> A local-first AI tool that channels the ghost of an abandoned GitHub repository and forces it to speak its final eulogy.

🔗 **Live Demo:** [https://repo-necromancer.onrender.com](https://repo-necromancer.onrender.com)  
📊 **Repository:** [https://github.com/arpitasi1gh/hacktoberfest/tree/main/repo-necromancer](https://github.com/arpitasi1gh/hacktoberfest/tree/main/repo-necromancer)

![Status](https://img.shields.io/badge/Status-Hacktoberfest_Submission-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-000000?style=for-the-badge)
![Gemma](https://img.shields.io/badge/Gemma-Google_AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)

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
        <li><a href="#-what-i-learned">📈 What I Learned</a></li>
      </ul>
    </td>
    <td width="33%">
      <ul>
        <li><a href="#%EF%B8%8F-future-improvements">🗺️ Future Improvements</a></li>
        <li><a href="#-connect-with-me">🤝 Connect With Me</a></li>
        <li><a href="#-license">📝 License</a></li>
      </ul>
    </td>
  </tr>
</table>

---

## 💡 The Problem I Solved

Every developer has a graveyard of abandoned side projects. Repos with names like `todo-app-final-v2`, dormant since 2022, holding half-finished auth systems and a single `TODO: fix this` comment. 

**Repo Necromancer** is an AI that channels the ghost of these dead codebases. You paste a GitHub URL. The app uses the GitHub API to fetch the repository's last commits, description, and age. Then, it uses **Gemma** to generate a dramatic, melancholic eulogy spoken from the perspective of the project itself.

It laments the features it never got, the bugs it still carries, and the developer who abandoned it for a shiny new framework. It is a humorous, slightly eerie commentary on the "Ghost in the Machine" theme.

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🪦 Ghost Generation** | Uses the GitHub API to extract real commit messages and generates a first-person eulogy. |
| **🧠 Context-Aware** | The AI reads the repo's last few commit messages to use as the "final words" of the project. |
| **🔒 Local-First** | Designed to run Gemma 3 4B locally via Ollama for uncensored, creative generation. |
| **🔄 Auto-Fallback** | Seamlessly falls back to Google AI Studio if a local model is unavailable. |
| **📱 HTMX UI** | A minimalist, eerie terminal-style interface with no client-side React. |

---

## 🧑‍💻 Tech Stack

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[FastAPI](https://fastapi.tiangolo.com/)** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | Async web framework serving the HTML and handling API calls. |
| **[Ollama](https://ollama.com/)** | ![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge) | Local inference runtime. |
| **[Gemma 3 4B](https://ai.google.dev/gemma)** | ![Gemma](https://img.shields.io/badge/Gemma-3_4B-8E75B2?style=for-the-badge) | Open-weight model used for creative generation. |
| **[GitHub API](https://docs.github.com/en/rest)** | Built-in | Used to fetch the repository's final commits and metadata. |
| **[HTMX](https://htmx.org/)** | ![HTMX](https://img.shields.io/badge/HTMX-336699?style=for-the-badge) | Handles form submissions without full page reloads. |

---

## 📂 Project Structure

```text
repo-necromancer/
├── main.py              # The entire FastAPI app, UI, and AI logic
├── .env                 # API keys (gitignored)
├── requirements.txt
└── README.md
```

This project uses a **single-file architecture** (`main.py`) with HTML and CSS rendered via Python f-strings. This makes it incredibly portable and easy to deploy without any build steps.

---

## ⚙️ Quick Start (Local Development)

### 0. Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com) installed (Optional, but recommended for local privacy)

### 1. Clone & Install
```bash
git clone https://github.com/arpitasi1gh/repo-necromancer.git
cd repo-necromancer
uv sync
```

### 2. Set Up `.env`
Create a file called `.env` in the project root:
```env
AI_PROVIDER=local
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Run the Server
```bash
uv run uvicorn main:app --reload
```

### 4. Open Your Browser
Navigate to `http://127.0.0.1:8000`. Paste the URL of a dead repo (e.g., `https://github.com/your-username/abandoned-project`) and click "Summon Ghost".

---

## 🧠 How It Works

1. **Data Fetch:** The app parses the GitHub URL and sends a request to the GitHub REST API to get the repository's description, last push date, and the last 3 commit messages.
2. **Prompting:** A strict prompt is constructed: *"You are the ghost of this repository. Your last commit messages were [commits]. Write a 3-paragraph eulogy speaking in the first person."*
3. **Generation:** Gemma generates the eulogy.
4. **Rendering:** HTMX injects the response into the UI.

---

## 🔄 Local vs Cloud AI

The inference layer has a built-in fallback to ensure the app never crashes:

```python
try:
    # Try to use local Ollama (uncensored, private)
    return await _call_ollama(prompt)
except Exception:
    # If Ollama is offline, fallback to Google AI Studio
    return await _call_google(prompt)
```

This means you can run the app completely offline, but if you deploy it to Render, it will still work via the Google API.

---

## 📈 What I Learned

1. **Open models are better for creative fiction.** Closed APIs have heavy safety filters that ruin creative roleplay. Open-source models like Gemma allow for melancholic, weird, and genuinely artistic generation.
2. **The GitHub API is powerful.** Just three commit messages are enough to infer the entire "story" of a failed project.
3. **HTMX + FastAPI is the ultimate hackathon stack.** No build step, no React, just pure Python and HTML.

---

## 🗺️ Future Improvements

- **Repo Comparison:** Generate a dialogue between two abandoned repos arguing over who had the better tech stack.
- **Code Graveyard:** A leaderboard of the oldest, most abandoned repos submitted by users.
- **Voice Generation:** Use ElevenLabs to have the eulogy spoken aloud by a ghostly voice.

---

## 🤝 Connect With Me

- **GitHub**: [arpitasi1gh](https://github.com/arpitasi1gh)
- **LinkedIn**: [Arpita Singh](https://linkedin.com/in/arpitasi1gh)

---

## 📝 License

MIT. See [LICENSE](LICENSE).
