# 🎙️ Rehearse – The Universal AI Interview Coach

> A local-first AI interviewer that forces you to practice out loud, pushes back on vague answers, and gives you a strict, actionable report card. Works for any role, from Software Engineers to Marketers to Nutritionists.

🔗 **Live Demo:** ``
📊 **Repository:** `https://github.com/arpitasi1gh/hacktoberfest/tree/main/rehearse`

![Status](https://img.shields.io/badge/Status-Hacktoberfest_Submission-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-000000?style=for-the-badge)
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

Interview preparation is broken. We read lists of questions, watch YouTube videos, and ask ChatGPT for answers. 

But reading is passive. And when you talk to ChatGPT, it acts like a cheerleader. It gives you a wall of text, says "Great answer!", and doesn't push you to be specific. A real interviewer is adversarial. They interrupt rambling, they ask "What was *your* contribution?", and they demand metrics.

**Rehearse fixes this.** It is a voice-enabled, mock-interview coach. You speak your answers out loud, and the AI listens, challenges you, and forces you to use the CARL/STAR method. At the end, you get a strict score and a breakdown of exactly how a 10/10 candidate would have answered.

Crucially, **it is not just for engineers.** You can input "Marketing Manager" or "Clinical Nutritionist", pick a focus, and the AI adapts its persona, tone, and questions to that exact domain.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🎙️ Voice In & Out** | Uses the browser's Web Speech API to transcribe your spoken answers and read the interviewer's questions aloud using the system TTS. |
| **🧠 Universal Domains** | Adapts to Software Engineering, MBA, Healthcare, Design, and more. Prompting rules ensure it grounds questions in your provided job description. |
| **🔥 Stress Mode** | Switch the interviewer's tone from "Standard" to "Stress Test" to simulate a hostile, rapid-fire interview. |
| **🛑 CARL/STAR Enforcement** | The prompt explicitly forces the AI to demand measurable Results and Lessons Learned. It will not accept vague answers. |
| **📊 Competency Breakdown** | At the end of the interview, the AI scores you on Structure, Depth, and Clarity. |
| **🪞 The "Weakest Moment"** | The feedback quotes your worst answer and shows you exactly how an ideal candidate would have responded. |
| **🔄 Local-First Fallback** | Runs Gemma 3 4B locally via Ollama by default. If Ollama isn't running, it automatically falls back to the Google Gemini API so the app never crashes. |
| **🌙 Dark-only UI** | A custom dark theme with emerald accents, focus states, and HTMX-driven state management. |

---

## 🧑‍💻 Tech Stack

### **Backend & AI**
| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[FastAPI](https://fastapi.tiangolo.com/)** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | Async web framework serving HTML and handling form posts. |
| **[Ollama](https://ollama.com/)** | ![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge) | Local inference runtime. Default path. |
| **[Gemma 3 4B](https://ai.google.dev/gemma)** | ![Gemma](https://img.shields.io/badge/Gemma-3_4B-8E75B2?style=for-the-badge) | Open-weight model. Runs locally via Ollama, or in the cloud. |
| **[HTMX](https://htmx.org/)** | ![HTMX](https://img.shields.io/badge/HTMX-336699?style=for-the-badge) | Handles form submissions and swaps chat bubbles without a full page reload. |

### **Browser APIs**
| Technology | Purpose |
| :--- | :--- |
| **Web Speech API** | `webkitSpeechRecognition` for dictating the user's spoken answers. |
| **SpeechSynthesis** | Used by the browser to read the AI's text responses aloud. |

---

## 📂 Project Structure

```text
rehearse/
├── src/
│   └── rehearse/
│       ├── __init__.py
│       ├── main.py                   # FastAPI app, routes, HTML shell
│       ├── ai_provider.py            # Prompt engineering, Ollama/Gemini fallback
│       └── static/
│           ├── style.css             # Dark-only theme
│           └── voice.js              # Browser mic and TTS logic
├── .env                              # API keys (gitignored)
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## ⚙️ Quick Start (Local Development)

### 0. Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com) installed (optional, falls back to Google API)

### 1. Clone & Install
```bash
git clone https://github.com/arpitasi1gh/rehearse.git
cd rehearse
uv sync
```

### 2. Set Up `.env`
Create a file called `.env` in the project root:
```
AI_PROVIDER=local
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemma-4-26b-a4b-it
```
*(Get a free Google AI Studio key at [aistudio.google.com](https://aistudio.google.com))*

### 3. Run the Server
```bash
uv run uvicorn rehearse.main:app --reload
```

### 4. Open Your Browser
Navigate to `http://127.0.0.1:8000`. **Use Google Chrome or Microsoft Edge**, as Safari does not support the Web Speech API for the microphone.

---

## 🧠 How It Works

1. **Setup:** You enter a role, difficulty, focus area, and paste a job description.
2. **AI Prompting:** The system prompt tells the AI to act as a Senior Manager. It uses *TCCo (Task, Context, Constraints)* and *DO-AVOID-INCLUDE-RETURN* frameworks to generate one question at a time.
3. **The Loop:** You answer. HTMX sends the conversation history to the server. The AI reads the history and generates a follow-up, pushing on the weakest part of your answer.
4. **The Report Card:** When you click "End Interview", the transcript is sent to the AI with a separate prompt that forces it to output a JSON object containing scores and critiques.

---

## 🔄 Local vs Cloud AI

The inference layer (`ai_provider.py`) has a unique fallback mechanism:

```python
# If AI_PROVIDER is local, it tries Ollama first.
# If Ollama is not running, it automatically catches the error and falls back to the Google API.
try:
    return await _call_ollama(system_prompt, context)
except Exception:
    return await _call_google(system_prompt, context)
```

This means:
- **Locally:** You don't *have* to run `ollama serve`. If you forget, the app still works via the cloud API.
- **On Render:** The environment variable `AI_PROVIDER=api` forces it to skip the local check and go straight to the cloud, avoiding timeout delays.

---

## 🔐 Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `AI_PROVIDER` | `local` | `local` (tries Ollama, falls back to API) or `api` (skips local) |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama endpoint |
| `OLLAMA_MODEL` | `gemma3:4b` | Local model name |
| `GOOGLE_API_KEY` | — | Required for the API fallback and Render deployment |
| `GOOGLE_MODEL` | `gemma-4-26b-a4b-it` | Cloud model name |

---

## 🚀 Deployment

Deployed on **Render** with `AI_PROVIDER=api`.

| Setting | Value |
| :--- | :--- |
| **Build Command** | `pip install uv && uv sync` |
| **Start Command** | `uv run uvicorn rehearse.main:app --host 0.0.0.0 --port $PORT` |
| **Env Vars** | `AI_PROVIDER=api`, `GOOGLE_API_KEY=...`, `GOOGLE_MODEL=...` |

---

## 📈 What I Learned

1. **Prompt engineering is the product.** The difference between a helpful AI and an interrogating AI comes down to hard constraints: "Never say 'great'", "Ask one question at a time", "If they say 'I don't know', do not switch topics."
2. **HTMX requires thinking differently about state.** Handling the audio playback on HTMX swaps required using `htmx:afterSwap` event listeners rather than relying on DOM load.
3. **Browser APIs are powerful but quirky.** The Web Speech API for dictation and SpeechSynthesis for TTS work flawlessly in Chrome but are blocked by autoplay policies or missing support in Safari. 
4. **Fallbacks prevent demo disasters.** Realizing that Ollama might not be running during a local demo, I built a `try/except` block that instantly drops to the Google API. The app never crashes.

---

## 🗺️ Future Improvements

- **Resume Parsing:** Allow users to upload a PDF resume so the AI can ask specific questions about their listed projects.
- **Video Analysis:** Use the webcam to analyze facial expressions and eye contact.
- **Live Transcription:** Show the user's spoken words appearing on screen in real-time as they talk.
- **Saved History:** Store past interview scores in a local SQLite database to track improvement over time.

---

## 🤝 Connect With Me

- **LinkedIn**: [Arpita Singh](https://linkedin.com/in/arpitasi1gh)
- **GitHub**: [arpitasi1gh](https://github.com/arpitasi1gh)
- **Email**: arpitasi1gh@gmail.com

---

## 📝 License

MIT. See [LICENSE](LICENSE).

---

**Built with 🎙️ by Arpita Singh**
_"Stop reading answers. Start speaking them."_