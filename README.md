# 🤖 Mistral OpsCommander

> **Hackathon Demo** · Autonomous AI SRE Agent powered by Mistral AI

[![Mistral AI](https://img.shields.io/badge/Powered%20by-Mistral%20AI-orange?style=for-the-badge)](https://mistral.ai)
[![Discord](https://img.shields.io/badge/Discord%20Bot-Ready-5865F2?style=for-the-badge&logo=discord)](https://discord.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Dashboard-61DAFB?style=for-the-badge&logo=react)](https://react.dev)

---

## 🎯 What is OpsCommander?

**Mistral OpsCommander** is an autonomous Site Reliability Engineering (SRE) agent that monitors, diagnoses, and **resolves** software incidents in real-time — all orchestrated by Mistral AI models.

When a developer reports a bug via Discord with a GitHub link, OpsCommander springs into action:

```
🔔 Discord: "Hey, there's a bug in our repo: https://github.com/org/repo"
        ↓
🧠 Magistral (Brain) reasons through the incident
        ↓
📦 Clones the GitHub repository locally
        ↓
🔍 Explores the codebase and identifies the root cause
        ↓
⚡ Devstral (Coder) generates a production-quality patch
        ↓
🚀 Commits + Pushes branch + Opens real Pull Request
        ↓
✅ Discord reply: "PR created → https://github.com/org/repo/pull/42"
```

Meanwhile, a **live cyberpunk dashboard** streams every thought, tool call, and decision in real-time.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Magistral Brain** | `mistral-large-latest` orchestrates diagnosis and tool use |
| 💻 **Devstral Coder** | `codestral-latest` generates code patches with 256k context |
| 🤖 **Discord Integration** | Bot listens for GitHub URLs in bug reports |
| 📡 **Live Dashboard** | Real-time SSE stream of agent thoughts & tool calls |
| 🔀 **Real GitHub PRs** | Pushes fix branch and opens actual Pull Requests via GitHub API |
| 📺 **Multi-client Streaming** | LogBroker pub/sub so Dashboard and Discord both get live updates |

---

## 🏗️ Architecture

```
Discord Message
     │
     ▼
┌─────────────┐   POST /api/trigger   ┌─────────────────────┐
│ Discord Bot │ ──────────────────── ▶│   FastAPI Backend   │
│ discord.py  │                       │   src/main.py       │
└─────────────┘                       └─────────┬───────────┘
                                                │ asyncio.create_task
                                                ▼
                                       ┌─────────────────┐
                                       │  OpsCommander   │
                                       │  orchestrator   │◀── Magistral (Brain)
                                       └────────┬────────┘
                                                │ tool calls
                                   ┌────────────┼─────────────┐
                                   ▼            ▼             ▼
                             clone_repo   trigger_patch  create_pull_request
                                   │            │             │
                                   │        Devstral      GitHub REST API
                                   │        (Coder)           │
                                   └────────────┴─────────────┘
                                                │
                                         LogBroker (pub/sub)
                                          /              \
                               SSE /api/stream        Discord reply
                                    │
                               React Dashboard
                              (live cyberpunk UI)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Mistral AI API key → [console.mistral.ai](https://console.mistral.ai)
- A Discord Bot Token → [discord.com/developers](https://discord.com/developers)
- A GitHub Personal Access Token (with `repo` scope)

### 1. Clone & Install Python Dependencies

```bash
git clone https://github.com/YOUR_USERNAME/mistral-ops-commander.git
cd mistral-ops-commander

python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
DISCORD_TOKEN=your_discord_bot_token_here
GITHUB_TOKEN=your_github_personal_access_token_here
```

### 3. Start the Backend

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

This starts:
- ✅ FastAPI server on `http://localhost:8001`
- ✅ SSE stream at `http://localhost:8001/api/stream`
- ✅ Discord bot (connects automatically on startup)

### 4. Start the Dashboard

```bash
cd webapp
npm install
npm run dev
```

Open `http://localhost:5173` to see the live cyberpunk dashboard.

### 5. Invite the Discord Bot

In your Discord developer portal, generate an invite URL with `Send Messages` + `Read Message History` permissions and invite it to your server.

---

## 💬 Usage

### Via Discord

Post a message in any channel your bot has access to:

```
Hey OpsCommander, there's a bug in our repo! The matrix multiply is wrong.
Please fix it: https://github.com/your-org/your-repo
```

The bot will:
1. Reply with an acknowledgment
2. Stream progress to the dashboard in real-time
3. Create a Pull Request on GitHub
4. Reply with the PR link

### Via Dashboard Button

Click **"Trigger Critical Incident"** on the dashboard to run the agent against a built-in demo scenario (auth service memory leak).

---

## 🗂️ Project Structure

```
mistral-ops-commander/
├── src/
│   ├── main.py                  # FastAPI app, SSE stream, LogBroker, Discord startup
│   ├── config.py                # Model names, env vars
│   ├── agent/
│   │   ├── orchestrator.py      # OpsCommander agent loop (Magistral)
│   │   ├── coder.py             # Devstral code patch generator
│   │   ├── tools.py             # All agent tools (clone, patch, PR, etc.)
│   │   └── prompts.py           # System prompts for Magistral + Devstral
│   ├── bot/
│   │   └── discord_bot.py       # Discord event handler
│   ├── mcp_tools/
│   │   ├── logs_tool.py         # Mock log fetcher (Grafana simulation)
│   │   └── github_tool.py       # GitHub issue reader
│   └── demo/
│       └── auth.py              # Vulnerable demo service for local incident demos
├── webapp/                      # React + Vite cyberpunk dashboard
│   ├── src/
│   │   ├── App.tsx              # Main dashboard component
│   │   └── index.css            # Cyberpunk theme
│   └── package.json
├── requirements.txt
└── .env.example
```

---

## 🔧 Agent Tools

| Tool | Description |
|------|-------------|
| `clone_repo(url)` | Clones a GitHub repo to a unique local temp directory |
| `list_files(dir)` | Lists files in a directory |
| `read_file(path)` | Reads full file content |
| `write_file(path, content)` | Overwrites a file with new content |
| `trigger_patch(file, context)` | Calls Devstral to generate + write a code fix |
| `create_pull_request(...)` | Creates branch, commits, pushes, opens real PR |
| `fetch_logs(service)` | Fetches mock service logs |
| `report_status(message)` | Voice status broadcast (Voxtral placeholder) |

---

## 🤖 AI Models Used

| Role | Model | Purpose |
|------|-------|---------|
| **Orchestrator** | `mistral-large-latest` | Reasoning, diagnosis, tool orchestration |
| **Coder** | `codestral-latest` | Code analysis, patch generation (256k context) |
| **Vision** *(planned)* | `pixtral-large-latest` | Grafana dashboard screenshot analysis |
| **Voice** *(planned)* | Voxtral Realtime | Live voice incident briefing |

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/trigger` | Trigger a new incident (accepts JSON payload) |
| `GET` | `/api/stream` | SSE stream of agent events |

### Trigger Payload Example

```json
{
  "alert_id": "ALT-9082",
  "title": "Memory leak in auth service",
  "severity": "CRITICAL",
  "service": "auth-service",
  "repository": "https://github.com/org/repo"
}
```

---

## 🏆 Hackathon Notes

This project was built for the **Mistral AI Hackathon** (Agents Track).

**Key demo flow:**
1. Open the [live dashboard](http://localhost:5173)
2. Post a bug report in Discord with any GitHub link
3. Watch Magistral think, Devstral code, and a real PR appear on GitHub — live on the dashboard

**What makes it special:**
- Real multi-model orchestration (Mistral Large → Codestral pipeline)
- Live SSE streaming to multiple simultaneous clients
- Actual GitHub API integration (real PRs, not mocks)
- Seamless Discord-native interface

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
