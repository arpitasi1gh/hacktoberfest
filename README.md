# 🌟 Hacktoberfest 2026 – Open-Source AI Portfolio

This repository contains my submissions for the **Hacktoberfest 2026 Open-Source AI Challenges**. 

Instead of just submitting PRs to existing projects, I took on the DEV Community weekly challenges and built **five full-stack AI applications from scratch** in four weeks. Everything is built with open-weight models, local-first architecture, and deployed with cloud fallbacks.

---

## 🚀 The Projects

Here is a quick overview of what I built. Click any project name to see its code, specific README, and setup instructions.

| Project | Description | Stack | Challenge Theme |
| :--- | :--- | :--- | :--- |
| **[What Now?](./what-now)** | A local-first AI that picks exactly one concrete next action based on your energy, available time, and task list. Includes HTMX OOB updates and custom sliders. | Python, FastAPI, HTMX, SQLite, Ollama | Weekend: Build for a Friend |
| **[Greenstep](./greenstep)** | Predicts the best 30-minute window to go outside based on sleep, screen time, mood, and live weather, then finds a real cafe nearby using SerpApi. | Python, FastAPI, HTMX, SerpApi, Open-Meteo | Week 1: Touch Grass |
| **[Rehearse](./rehearse)** | A voice-enabled AI interviewer that pushes back on your answers. Uses browser speech APIs and enforces the CARL/STAR method. | Python, FastAPI, HTMX, Browser Speech API | Week 2: Side Hustle |
| **[Inbox Sloth](./inbox-sloth)** | An AI ghostwriter that drafts replies to stressful emails in your exact tone. Saves your past emails locally to use as few-shot prompts. | Python, FastAPI, HTMX, Local JSON | Week 3: Slow and Steady |
| **[Repo Necromancer](./repo-necromancer)** | Analyzes abandoned GitHub repos via the GitHub API and generates a deep forensic report and a technical eulogy for why the project died. | Python, FastAPI, HTMX, GitHub API | Week 4: Ghost in the Machine |

---

## ⚠️ A Note on Live Demos & Render Limits

You will notice live links in the individual project READMEs. They are deployed on **Render's Free Tier**. 

If a link takes 50+ seconds to load or shows a 502 Bad Gateway, it is simply waking up from sleep (cold start). If an AI action fails, it might be because the free-tier API limit (Google AI Studio) was temporarily exhausted.

**If the deployed links are slow or fail, the local setups are the intended way to experience these apps.** They are designed to run 100% offline using Ollama and local SQLite, ensuring zero latency and complete privacy. Setup instructions are in each project's folder.

---

## 🛠 The Core Architecture

Across all five projects, I consistently used the same core philosophy: **local-first, with cloud fallbacks for sharing.**

- **Backend:** FastAPI + Uvicorn
- **Frontend:** Jinja2 + HTMX (No React, no build step)
- **Storage:** SQLite (Local, zero config)
- **AI Engine:** Ollama (Gemma 3 4B) running locally. If Ollama is offline, the app seamlessly falls back to Google AI Studio (Gemini).

---

## 🤝 Open to Code Reviews & Contributions

These projects were built rapidly under hackathon deadlines. While they are fully functional and deployed, I am absolutely open to **code reviews, pull requests, and feedback from anyone.**

Whether you are a fellow student, a hiring manager, or a seasoned engineer, I welcome different perspectives. If you spot areas for improvement (especially regarding FastAPI patterns, prompt injection risks, or frontend accessibility), please feel free to open an issue, submit a PR, or just drop me a message. 

I am always eager to learn, collaborate, and improve the technical foundation of these tools.

---

## 🔗 Connect With Me

If you want to chat about local-first AI, prompt engineering, or building fast with FastAPI and HTMX, let's connect!

- **LinkedIn**: [Arpita Singh](https://linkedin.com/in/arpitasi1gh)
- **DEV.to**: [@arpitasi1gh](https://dev.to/arpitasi1gh)
- **GitHub**: [@arpitasi1gh](https://github.com/arpitasi1gh)
