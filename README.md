# home

Personal dotfiles and projects for macOS.

## Contents

| File | Description |
|------|-------------|
| `.zshrc` | Zsh config — nvm, pipx, Homebrew, aliases |
| `.zprofile` | Zsh login profile |
| `.gitconfig` | Git user config |
| `CLAUDE.md` | Guidance for Claude Code when working in this repo |
| `.claude/settings.json` | Claude Code settings |
| `projects/n8n-mcp-server/` | MCP server exposing n8n workflows to Claude |

## n8n MCP Server

Exposes n8n workflow automation as tools (`list_workflows`, `get_workflow`, `execute_workflow`) to Claude via the Model Context Protocol.

```bash
cd projects/n8n-mcp-server && npm install
claude mcp add n8n --scope user \
  -e N8N_BASE_URL=http://localhost:5678 \
  -e N8N_API_KEY=<your-key> \
  -- node /path/to/projects/n8n-mcp-server/server.js
```

## License

[Apache 2.0](LICENSE)
