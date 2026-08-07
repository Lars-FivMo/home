# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**GitHub:** https://github.com/Lars-FivMo/home

## Projects

All projects live in `~/projects/`:

| Project | Repo |
|---------|------|
| `n8n-mcp-server` | https://github.com/Lars-FivMo/n8n-mcp-server |
| `profile-readme` | https://github.com/Lars-FivMo/Lars-FivMo |
| `MoodTracker` | https://github.com/Lars-FivMo/MoodTracker |
| `Stimmunsbarometer` | https://github.com/Lars-FivMo/Stimmunsbarometer |
| `moltbot` | https://github.com/Lars-FivMo/moltbot |
| `OmniRoute` | https://github.com/diegosouzapw/omniroute |

## Global Skills (`~/.claude/skills/`)

Skills stored here are user-scope — available in every project, not just this repo.

| Skill | Purpose |
|-------|---------|
| `grill-me` | Interviews the user about a project/feature until real alignment exists, then writes an alignment document. Alignment phase of the KI-Developer-Loop. |

## Environment

- **Node.js**: managed via `nvm` (sourced in `.zshrc`)
- **Python**: venvs stored in `~/venvs/` — activate whisper env with `whisperenv` alias
- **Homebrew**: available at `/opt/homebrew/bin/brew`

## n8n MCP Server (`~/projects/n8n-mcp-server/` — [GitHub](https://github.com/Lars-FivMo/n8n-mcp-server))

A Model Context Protocol (MCP) server that exposes n8n workflow automation as tools for Claude. Entry point: `server.js`.

**Configuration (environment variables):**
- `N8N_API_KEY` — n8n API key
- `N8N_BASE_URL` — defaults to `http://localhost:5678`

**Note:** The `claude.ai n8n` marketplace connector (HTTP transport) cannot be removed via CLI — use claude.ai → Settings → Integrations to disconnect it.

**Registered in Claude (user scope):**
```bash
claude mcp add n8n --scope user \
  -e N8N_BASE_URL=http://localhost:5678 \
  -e N8N_API_KEY=<your-key> \
  -- node /Users/larsfvm/projects/n8n-mcp-server/server.js
```

**Run manually:**
```bash
cd ~/projects/n8n-mcp-server && npm install
node ~/projects/n8n-mcp-server/server.js
```

**Exposed tools:** `list_workflows`, `get_workflow`, `execute_workflow` — all communicate with the n8n REST API (`/api/v1/workflows`).

**Stack:** ESM (`"type": "module"`), `@modelcontextprotocol/sdk` for MCP transport over stdio, `axios` for HTTP.

## OmniRoute (`~/projects/OmniRoute/` — [GitHub](https://github.com/diegosouzapw/omniroute))

Third-party, self-hosted AI proxy/router (npm package `omniroute`) — unifies 290+ LLM providers behind
one OpenAI-compatible endpoint, with auto-fallback, an MCP server, an A2A server, and an Electron
desktop app. Author: `diegosouzapw` (not an Anthropic or FivMo project — not yet installed or run
anywhere).

**⚠️ Before installing/running, review:**
- It provisions its own secrets (`JWT_SECRET`, `API_KEY_SECRET`) and an admin login
  (`INITIAL_PASSWORD`, defaults to `CHANGEME` — must be changed before first use).
- It installs TLS certificates into the system NSS database to act as a local MITM proxy
  (`src/mitm/cert/install.ts`) — a deliberate system-level change, not a side effect.
- `npm install` runs `scripts/postinstall.mjs` — read it before running on a machine with real
  provider API keys, since all LLM traffic would route through this third-party code.

**Setup (once reviewed and approved):**
```bash
cd ~/projects && git clone https://github.com/diegosouzapw/omniroute OmniRoute
cd OmniRoute && npm install        # runs postinstall.mjs — review first
cp .env.example .env
# generate secrets before first run:
openssl rand -base64 48   # -> JWT_SECRET
openssl rand -hex 32      # -> API_KEY_SECRET
npm run dev                # dev server at http://localhost:20128
```

**MCP server entry:** `bin/mcp-server.mjs` (resolves `dist/open-sse/mcp-server/server.js` or the
TS source). Register with Claude similarly to n8n-mcp-server once the app itself has been reviewed
and configured:
```bash
claude mcp add omniroute --scope user -- node /Users/larsfvm/projects/OmniRoute/bin/mcp-server.mjs
```

**Stack:** Next.js 16 (App Router), TypeScript, SQLite (via `src/lib/db/`), MCP + A2A (JSON-RPC 2.0)
servers, Electron desktop shell.
