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
| `Buddy` | https://github.com/Lars-FivMo/buddy |

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
