#!/usr/bin/env python3
"""FVM-OS Fleet Dispatch — parallele Ausführung von Aufgaben durch Harrys Team.

Backends:
  api (Default) — Anthropic Messages API, System-Prompt = Agenten-Definition.
                  Braucht ANTHROPIC_API_KEY (aus .env / Umgebung).
  cli           — `claude -p` Subprozess; nutzt die lokale Claude-Code-Installation.
                  Auswahl über FLEET_BACKEND=cli.

Verwendung (commander.py):
  from fleet_registry import match
  from fleet_dispatch import dispatch

  kandidaten = match(task, top_n=3)
  ergebnisse = dispatch(task, kandidaten)   # list[{"agent", "ok", "output"}]

CLI-Test:
  python3 scripts/fleet_dispatch.py "Aufgabe..." agent-name-1 agent-name-2
"""

import json
import os
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

from fleet_registry import load_fleet, match  # noqa: F401  (Re-Export für commander.py)

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("FLEET_MODEL", "claude-sonnet-4-6")
BACKEND = os.environ.get("FLEET_BACKEND", "api")
MAX_TOKENS = int(os.environ.get("FLEET_MAX_TOKENS", "2048"))
TIMEOUT_S = int(os.environ.get("FLEET_TIMEOUT_S", "120"))
MAX_PARALLEL = int(os.environ.get("FLEET_MAX_PARALLEL", "5"))

# Diese Dateien (relativ zum aios-Workspace) bekommt jeder Flotten-Agent als
# Briefing über FVM-Studio mit — so kennt die Flotte Firma, Angebot und Stack.
CONTEXT_FILES = os.environ.get(
    "FLEET_CONTEXT_FILES", "context/fvm-studio.md,context/business-info.md"
)
CONTEXT_MAX_CHARS = int(os.environ.get("FLEET_CONTEXT_MAX_CHARS", "6000"))


@lru_cache(maxsize=1)
def _studio_briefing() -> str:
    parts = []
    for rel in CONTEXT_FILES.split(","):
        path = Path(rel.strip())
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8", errors="ignore").strip())
    return "\n\n".join(parts)[:CONTEXT_MAX_CHARS]


def _system_prompt(agent) -> str:
    base = agent.prompt or (
        f"Du bist {agent.name}, Spezialist im FVM-Studio-Team von Harry (COO). "
        f"Dein Fachgebiet: {agent.description or 'siehe Aufgabenstellung'}. "
        "Antworte präzise, auf Deutsch, ohne Füllwörter — dein Ergebnis geht an "
        "Harry zur Synthese, nicht direkt an Lars."
    )
    briefing = _studio_briefing()
    if briefing:
        base += (
            "\n\n## Über FVM-Studio (dein Auftraggeber)\n"
            "Nutze diesen Kontext für alle Antworten:\n\n" + briefing
        )
    return base


def _call_api(agent, task: str) -> str:
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": _system_prompt(agent),
        "messages": [{"role": "user", "content": task}],
    }).encode("utf-8")
    request = urllib.request.Request(API_URL, data=payload, method="POST", headers={
        "content-type": "application/json",
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
    })
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        data = json.loads(response.read().decode("utf-8"))
    return "".join(block.get("text", "") for block in data.get("content", []))


def _call_cli(agent, task: str) -> str:
    prompt = f"{_system_prompt(agent)}\n\n---\n\nAufgabe:\n{task}"
    result = subprocess.run(
        ["claude", "-p", prompt, "--max-turns", "1"],
        capture_output=True, text=True, timeout=TIMEOUT_S,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"claude CLI Exit {result.returncode}")
    return result.stdout.strip()


def _run_one(agent, task: str) -> dict:
    try:
        call = _call_cli if BACKEND == "cli" else _call_api
        return {"agent": agent.name, "ok": True, "output": call(agent, task)}
    except Exception as error:  # ein gescheiterter Agent darf den Dispatch nicht kippen
        return {"agent": agent.name, "ok": False, "output": f"FEHLER: {error}"}


def dispatch(task: str, agents: list) -> list:
    """Aufgabe parallel an mehrere Agenten geben, Ergebnisse einsammeln."""
    if not agents:
        return []
    workers = min(len(agents), MAX_PARALLEL)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda agent: _run_one(agent, task), agents))


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    task, names = sys.argv[1], set(sys.argv[2:])
    fleet = {agent.name: agent for agent in load_fleet()}
    unknown = names - fleet.keys()
    if unknown:
        print(f"Unbekannte Agenten: {', '.join(sorted(unknown))}")
        return 1
    for result in dispatch(task, [fleet[name] for name in names]):
        marker = "✓" if result["ok"] else "✗"
        print(f"\n{marker} {result['agent']}\n{result['output']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
