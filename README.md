# A2UI Code Review Agent

A demo showcasing [A2UI (Agent-to-UI)](https://a2ui.org) — a Google protocol that lets AI agents generate rich, interactive UIs through declarative JSON. No client-side code generation, no iframes, no sandboxing. The agent describes *what* the UI should be, and the client renders it natively.

This demo implements a GitHub PR code review agent. You paste a PR URL, the agent fetches the diff, analyzes it with an LLM, and renders an interactive review dashboard with severity-colored findings, diff blocks, and action buttons — all generated as A2UI JSON by the model.

## What it demonstrates

- **Declarative UI from an LLM** — the model outputs structured JSON, not code
- **Interactive components** — buttons trigger actions that flow back to the agent
- **Data binding** — UI components bind to a data model, templates repeat over collections
- **Streaming status** — real-time progress updates during multi-step agent work
- **Multi-surface rendering** — follow-up responses render alongside the original review
- **A2A protocol** — agent-to-agent communication with A2UI as an extension

## Architecture

```
Browser (Lit + @a2ui/lit)  ←→  A2A Protocol  ←→  Python Agent (Google ADK + LiteLLM)  →  GitHub API
```

The server is a Python A2A agent that calls `fetch_pr_diff` to get PR data, sends it to a Gemini model with the A2UI schema in the system prompt, validates the returned JSON, and streams it back. The client is a Lit web app that renders A2UI surfaces and dispatches user actions back to the agent.

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Bun](https://bun.sh/) (or Node.js — npm works too)
- A [Gemini API key](https://aistudio.google.com/apikey)
- A [GitHub personal access token](https://github.com/settings/tokens) (for reading PR diffs and optionally posting reviews)

### Configure environment

```bash
cp server/.env.example server/.env
```

Edit `server/.env`:

```
GEMINI_API_KEY=your-gemini-api-key
LITELLM_MODEL=gemini/gemini-2.5-flash
GITHUB_TOKEN=your-github-token
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Gemini API key from AI Studio |
| `LITELLM_MODEL` | No | Model to use (default: `gemini/gemini-2.5-flash`) |
| `GITHUB_TOKEN` | Yes | GitHub PAT — needs `repo` scope for private repos, or just public access for public repos. Also required for posting reviews. |

### Install dependencies

```bash
# Server
cd server && uv sync

# Client
cd client && bun install
```

### Run

Start both in separate terminals:

```bash
# Terminal 1 — server (port 10002)
cd server && uv run .

# Terminal 2 — client (port 5173)
cd client && bunx --bun vite
```

Open http://localhost:5173, paste a GitHub PR URL, and click **Review**.

## License

MIT
