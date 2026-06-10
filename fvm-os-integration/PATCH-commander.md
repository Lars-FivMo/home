# Verdrahtung: commander.py + CLAUDE.md

> Anzuwenden im `fvm-studio-aios`-Checkout, nachdem `fleet_registry.py` und
> `fleet_dispatch.py` nach `scripts/` kopiert wurden (siehe README).

## 1. `scripts/commander.py`

### Imports ergänzen (oben bei den anderen Imports)

```python
from fleet_registry import match as fleet_match
from fleet_dispatch import dispatch as fleet_dispatch
```

### Routing erweitern

`commander.py` hat heute den Fall: *keine Spezialisten-Scores → „Harry alleine,
kein Fleet-Dispatch"*. Genau diese Stelle wird ersetzt — statt aufzugeben,
fragt der Commander die 160er-Flotte:

```python
# Vorher:
if not scores:
    return []  # Harry alleine, kein Fleet-Dispatch

# Nachher:
if not scores:
    kandidaten = fleet_match(task, top_n=3)
    if not kandidaten:
        return []  # wirklich niemand — Harry übernimmt selbst
    results = fleet_dispatch(task, kandidaten)
    return [r for r in results if r["ok"]] or results
```

Optional (empfohlen): Auch bei Treffern der alten 13er-Spezialisten zusätzlich
`fleet_match` aufrufen und die Scores vergleichen — so wandern Aufgaben
schrittweise auf die größere Flotte, ohne die bewährten Spezialisten abzuschalten.

### Ergebnis-Format

`fleet_dispatch` liefert `[{"agent": str, "ok": bool, "output": str}]` — das
entspricht dem, was `_format_result(results, task)` bereits konsumiert
(Agent-Name + Text). Falls `_format_result` zusätzliche Felder erwartet,
dort einmalig mappen.

## 2. `CLAUDE.md` (Workspace-Root von fvm-studio-aios)

Im Abschnitt zu Harrys Team/CommandOS ergänzen:

```markdown
**Harrys Team:** Die 160 Agenten der FVM-OS-Flotte (`context/harry-team.md`).
Jede Aufgabe zuerst gegen die Flotte matchen (`scripts/fleet_registry.py`),
bei Treffer delegieren (`scripts/fleet_dispatch.py`), Ergebnisse synthetisieren.
Harry arbeitet nur selbst, wenn kein Agent passt.
```

## 3. `.env`

```bash
FVM_OS_PATH=/opt/fvm-os        # Checkout/Installationspfad von FVM-OS
# FLEET_BACKEND=cli            # optional: claude CLI statt API
# FLEET_MODEL=...              # optional: Modell-Override für Flotten-Calls
# FLEET_MAX_PARALLEL=5         # optional: paralleler Fan-out-Deckel
```

## 4. Smoke-Test

```bash
python3 scripts/fleet_registry.py list            # erwartet: "160 Agenten geladen"
python3 scripts/fleet_registry.py match "Erstelle einen Content-Plan für Juli"
python3 scripts/fleet_dispatch.py "Sag in einem Satz hallo" <ein-agent-name>
docker compose restart harry scheduler
```

Danach in Telegram: `team status` → Harry meldet die Flotten-Größe.
