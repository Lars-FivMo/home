# Harry × FVM-OS — Integration der 160-Agenten-Flotte

> Deploy-Paket: Harry (COO, `fvm-studio-aios`) arbeitet ab sofort mit den 160
> Agenten aus `FVM-OS` als seinem Team. Dieses Paket wurde im `home`-Repo
> vorbereitet, weil die Claude-Session keinen Schreibzugriff auf
> `fvm-studio-aios`/`FVM-OS` hatte — es ist so gebaut, dass es per Copy
> direkt im Zielsystem installiert werden kann.

## Zielbild

```
Lars → Telegram/Claude Code/Voice
         → Harry (COO)
             → Commander (commander.py, Schicht 2)
                 → Fleet-Registry  ← lädt die 160 Agenten aus FVM-OS
                 → Fleet-Dispatch  → parallele Ausführung → Synthese → Harry
```

## Paket-Inhalt

| Datei | Zweck | Zielort in `fvm-studio-aios` |
|-------|-------|------------------------------|
| `context/harry-team.md` | Harrys neues Team-Verständnis (Systemkontext) | `context/harry-team.md` |
| `scripts/fleet_registry.py` | Lädt & matcht die 160 FVM-OS-Agenten | `scripts/fleet_registry.py` |
| `scripts/fleet_dispatch.py` | Paralleler Dispatch an die Flotte | `scripts/fleet_dispatch.py` |
| `PATCH-commander.md` | Verdrahtung in `commander.py` + `CLAUDE.md` | manuell anwenden |

## Installation (auf dem VPS, im `fvm-studio-aios`-Checkout)

```bash
# 1. Paket kopieren (HOME_REPO = Checkout dieses home-Repos)
cp $HOME_REPO/fvm-os-integration/scripts/fleet_registry.py  scripts/
cp $HOME_REPO/fvm-os-integration/scripts/fleet_dispatch.py  scripts/
cp $HOME_REPO/fvm-os-integration/context/harry-team.md      context/

# 2. FVM-OS-Pfad setzen (dort liegen die 160 Agenten)
echo 'FVM_OS_PATH=/opt/fvm-os' >> .env   # Pfad ggf. anpassen

# 3. Registry testen
python3 scripts/fleet_registry.py list | head -20
python3 scripts/fleet_registry.py match "Schreibe einen Blogpost über KI im Handwerk"

# 4. commander.py verdrahten → siehe PATCH-commander.md

# 5. Harry neu starten
docker compose restart harry scheduler
```

## Annahmen (im Zielsystem verifizieren)

- Die 160 Agenten liegen in `FVM-OS` entweder als `agents/manifest.json`
  oder als Markdown-Definitionen mit YAML-Frontmatter
  (`.claude/agents/*.md` bzw. `agents/**/*.md`). Die Registry probiert
  alle drei Quellen automatisch durch — liegt die Flotte woanders,
  reicht es, `FVM_OS_PATH` bzw. `_SOURCES` in `fleet_registry.py` anzupassen.
- Dispatch läuft per Anthropic Messages API (`ANTHROPIC_API_KEY` aus `.env`),
  alternativ per `claude` CLI (`FLEET_BACKEND=cli`).
