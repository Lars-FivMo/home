#!/usr/bin/env python3
"""FVM-OS Fleet Registry — lädt die 160-Agenten-Flotte als Harrys Team.

Quellen (die erste existierende gewinnt):
  1. $FVM_OS_PATH/agents/manifest.json   — Liste von {name, description, keywords?, tools?, prompt?}
  2. $FVM_OS_PATH/.claude/agents/**/*.md — Claude-Code-Agenten mit YAML-Frontmatter
  3. $FVM_OS_PATH/agents/**/*.md         — Markdown-Definitionen mit YAML-Frontmatter

Verwendung:
  python3 scripts/fleet_registry.py list
  python3 scripts/fleet_registry.py match "Schreibe einen Blogpost über KI im Handwerk"

Als Modul (commander.py):
  from fleet_registry import load_fleet, match
  kandidaten = match("Aufgabe...", top_n=3)
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

FVM_OS_PATH = Path(os.environ.get("FVM_OS_PATH", "/opt/fvm-os"))

_SOURCES = [
    ("manifest", "agents/manifest.json"),
    ("claude-agents", ".claude/agents"),
    ("agents-md", "agents"),
]

# Wörter ohne Routing-Signal (Deutsch + Englisch, bewusst klein gehalten)
_STOPWORDS = {
    "der", "die", "das", "ein", "eine", "einen", "und", "oder", "für", "mit",
    "von", "aus", "auf", "über", "bitte", "mal", "mir", "uns", "ich", "du",
    "the", "a", "an", "and", "or", "for", "with", "from", "about", "please",
    "schreibe", "erstelle", "mach", "mache", "kannst",
}


@dataclass
class AgentSpec:
    name: str
    description: str = ""
    keywords: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    prompt: str = ""
    source: str = ""

    def routing_text(self) -> str:
        return " ".join([self.name.replace("-", " "), self.description, " ".join(self.keywords)]).lower()


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Sehr kleiner YAML-Frontmatter-Parser (key: value, key: [a, b])."""
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", text, re.DOTALL)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip("\"'")
        if value.startswith("[") and value.endswith("]"):
            meta[key.strip()] = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
        else:
            meta[key.strip()] = value
    return meta, m.group(2)


def _from_manifest(path: Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("agents", data) if isinstance(data, dict) else data
    fleet = []
    for entry in entries:
        fleet.append(AgentSpec(
            name=entry.get("name", "unbenannt"),
            description=entry.get("description", ""),
            keywords=entry.get("keywords", []),
            tools=entry.get("tools", []),
            prompt=entry.get("prompt", entry.get("system_prompt", "")),
            source=str(path),
        ))
    return fleet


def _from_markdown_dir(root: Path) -> list:
    fleet = []
    for md in sorted(root.rglob("*.md")):
        if md.name.upper() in ("README.MD", "INDEX.MD"):
            continue
        meta, body = _parse_frontmatter(md.read_text(encoding="utf-8"))
        tools = meta.get("tools", [])
        if isinstance(tools, str):
            tools = [t.strip() for t in tools.split(",") if t.strip()]
        fleet.append(AgentSpec(
            name=meta.get("name", md.stem),
            description=meta.get("description", body.strip().splitlines()[0] if body.strip() else ""),
            keywords=meta.get("keywords", []) if isinstance(meta.get("keywords"), list) else [],
            tools=tools,
            prompt=body.strip(),
            source=str(md),
        ))
    return fleet


def load_fleet(root: Path = None) -> list:
    root = root or FVM_OS_PATH
    if not root.exists():
        raise FileNotFoundError(
            f"FVM-OS nicht gefunden unter {root} — FVM_OS_PATH in .env setzen."
        )
    for kind, rel in _SOURCES:
        candidate = root / rel
        if kind == "manifest" and candidate.is_file():
            return _from_manifest(candidate)
        if kind != "manifest" and candidate.is_dir():
            fleet = _from_markdown_dir(candidate)
            if fleet:
                return fleet
    raise FileNotFoundError(
        f"Keine Agenten-Definitionen unter {root} gefunden (geprüft: "
        + ", ".join(rel for _, rel in _SOURCES) + ")."
    )


def _tokens(text: str) -> set:
    return {t for t in re.findall(r"[a-zäöüß0-9]{3,}", text.lower()) if t not in _STOPWORDS}


def match(task: str, fleet: list = None, top_n: int = 3) -> list:
    """Top-N Agenten für eine Aufgabe — Wortüberlappung mit Name/Beschreibung/Keywords."""
    fleet = fleet if fleet is not None else load_fleet()
    task_tokens = _tokens(task)
    scored = []
    for agent in fleet:
        agent_tokens = _tokens(agent.routing_text())
        overlap = task_tokens & agent_tokens
        if not overlap:
            continue
        # Keyword-Treffer zählen doppelt — sie sind die explizite Routing-Absicht
        keyword_hits = task_tokens & _tokens(" ".join(agent.keywords))
        scored.append((len(overlap) + len(keyword_hits), agent))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [agent for _, agent in scored[:top_n]]


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        fleet = load_fleet()
        print(f"{len(fleet)} Agenten geladen aus {FVM_OS_PATH}")
        for agent in fleet:
            print(f"  {agent.name:<30} {agent.description[:70]}")
    elif cmd == "match" and len(sys.argv) > 2:
        task = " ".join(sys.argv[2:])
        hits = match(task)
        if not hits:
            print("Kein passender Agent — Harry übernimmt selbst.")
        for agent in hits:
            print(f"  {agent.name:<30} {agent.description[:70]}")
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
