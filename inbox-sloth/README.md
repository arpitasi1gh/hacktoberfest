# 🦥 Inbox Sloth – The Local-First AI Ghostwriter

> A local-first AI tool that drafts replies to your most stressful emails in your exact voice. No cloud, no generic corporate fluff.

🔗 **Repository:** [`https://github.com/arpitasi1gh/hacktoberfest/edit/main/inbox-sloth](https://github.com/arpitasi1gh/hacktoberfest/edit/main/inbox-sloth`

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

We all have that one email we've been avoiding. The passive-aggressive client, the boss asking for a weekend update, the vendor asking for a meeting that could have been an email. Writing a reply takes 5 minutes. Avoiding it takes 3 days of low-grade anxiety.

ChatGPT doesn't fix this. It drafts generic corporate fluff that sounds like a robot. 

**Inbox Sloth fixes this.** You paste the incoming email, and it generates three distinct options:
1. **Short:** A 1-sentence reply to end the thread.
2. **Polite:** A standard professional response.
3. **Pushback:** A firm decline or boundary-setting.

But the magic is the **Tone Profile**. You can paste a past email you wrote. Inbox Sloth saves it to your local database. Next time you generate a reply, it uses your past writing as context so the drafts actually sound like *you*—not a customer service bot.

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🎭 Tone Profiling** | Uses few-shot prompting to learn from your past emails and mimic your writing style. |
| **⚡ 3 Reply Styles** | Instantly generates Short, Polite, and Pushback variations. |
| **🔒 Local-First** | Emails are sent to local Ollama (Gemma 3 4B) by default. Your data never leaves your laptop. |
| **🔄 Auto-Fallback** | If Ollama isn't running, it seamlessly falls back to Google AI Studio. |
| **📱 HTMX UI** | Zero React, zero build step. Instant asynchronous updates with minimal JavaScript. |

---

## 🧑‍💻 Tech Stack

| Technology | Badge | Purpose |
| :--- | :--- | :--- |
| **[FastAPI](https://fastapi.tiangolo.com/)** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | Async web framework serving the HTML and handling API calls. |
| **[Ollama](https://ollama.com/)** | ![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge) | Local inference runtime. |
| **[Gemma 3 4B](https://ai.google.dev/gemma)** | ![Gemma](https://img.shields.io/badge/Gemma-3_4B-8E75B2?style=for-the-badge) | Open-weight model used for generating the drafts. |
| **[HTMX](https://htmx.org/)** | ![HTMX](https://img.shields.io/badge/HTMX-336699?style=for-the-badge) | Handles form submissions without full page reloads. |
| **Local JSON** | Built-in | Lightweight storage for the Tone Profile (zero database setup). |

---

## 📂 Project Structure

```text
inbox-sloth/
├── main.py              # The entire FastAPI app, UI, and AI logic
├── tone.json            # Local storage for your past emails (gitignored)
├── .env                 # API keys (gitignored)
├── pyproject.toml
└── README.md
```

To save time and keep the app entirely portable, this project uses a **single-file architecture** (`main.py`) with HTML and CSS rendered via f-strings.

---

## ⚙️ Quick Start (Local Development)

### 0. Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com) installed

### 1. Clone & Install
```bash
git clone https://github.com/arpitasi1gh/inbox-sloth.git
cd inbox-sloth
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
Navigate to `http://127.0.0.1:8000`.

---

## 🧠 How It Works

1. **Tone Profiling:** When you save a past email, it is appended to `tone.json`.
2. **The Prompt:** When you paste a stressful email, the backend reads `tone.json` and injects it into the system prompt as "Few-Shot Examples".
3. **Strict JSON:** The AI is forced to return a JSON object with exactly three keys (`short`, `polite`, `pushback`).
4. **Rendering:** HTMX takes the response and displays the three drafts in a grid.

---

## 🔄 Local vs Cloud AI

The inference layer has a built-in fallback to ensure the app never crashes:

```python
try:
    # Try to use local Ollama
    return await _call_ollama(prompt)
except Exception:
    # If Ollama is offline, fallback to Google AI Studio
    return await _call_google(prompt)
```

This means you can run the app completely offline for privacy, but if you deploy it to the web, it will still work via the Google API.

---

## 📈 What I Learned

1. **Prompt Fatigue is real.** I built this because I was tired of manually typing "act like me and write a polite response." Automating the few-shot prompt chain makes the AI feel like a real tool, not a chat toy.
2. **Strict JSON parsing is essential.** Gemma often tries to output its internal reasoning before the answer. I had to use `format: "json"` in Ollama and write a Python parser that extracts only the valid JSON block from the output.
3. **HTMX is incredible for single-file apps.** I built a fully interactive three-column grid layout without writing a single `useState` hook or setting up Vite.

---

## 🗺️ Future Improvements

- **Browser Extension:** A Chrome extension that injects an "Inbox Sloth" button directly into Gmail.
- **Multi-Account:** Store different Tone Profiles for different contexts (e.g., "Work Tone" vs. "Freelance Tone").
- **MongoDB Integration:** Migrate `tone.json` to a cloud MongoDB cluster so user profiles persist across devices.

---

## 🤝 Connect With Me

- **GitHub**: [arpitasi1gh](https://github.com/arpitasi1gh)
- **LinkedIn**: [Arpita Singh](https://linkedin.com/in/arpitasi1gh)

---

## 📝 License

MIT. See [LICENSE](LICENSE).
