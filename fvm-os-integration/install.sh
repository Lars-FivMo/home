#!/usr/bin/env bash
# Harry × FVM-OS — One-Shot-Installer
#
# Auf dem VPS ausführen (Pfade ggf. anpassen):
#   curl -fsSL https://raw.githubusercontent.com/Lars-FivMo/home/claude/harry-160-agents-collab-j0uu4a/fvm-os-integration/install.sh \
#     | bash -s -- /pfad/zu/fvm-studio-aios /pfad/zu/fvm-os
#
# Argumente:
#   $1 = Checkout von fvm-studio-aios   (Default: aktuelles Verzeichnis)
#   $2 = Checkout/Installation von FVM-OS, dort liegen die 160 Agenten (Default: /opt/fvm-os)
#
# Schritte: Dateien installieren → .env → CLAUDE.md → commander.py patchen
# (mit Backup) → Registry-Smoke-Test → Harry neu starten. Idempotent.
set -euo pipefail

BRANCH="claude/harry-160-agents-collab-j0uu4a"
RAW="https://raw.githubusercontent.com/Lars-FivMo/home/${BRANCH}/fvm-os-integration"
TARGET="${1:-$PWD}"
FVM_OS="${2:-/opt/fvm-os}"

if [ ! -f "$TARGET/scripts/commander.py" ] && [ ! -f "$TARGET/CLAUDE.md" ]; then
  echo "✗ $TARGET sieht nicht nach einem fvm-studio-aios-Checkout aus (scripts/commander.py fehlt)."
  echo "  Aufruf: install.sh /pfad/zu/fvm-studio-aios [/pfad/zu/fvm-os]"
  exit 1
fi
cd "$TARGET"
echo "→ Installiere Harrys Team-Integration nach: $TARGET"
echo "→ FVM-OS (160 Agenten) erwartet unter:      $FVM_OS"

# 0) FVM-OS noch nicht auf dem Server? Von GitHub klonen. Privates Repo —
#    darum zuerst die Remote-URL des fvm-studio-aios-Checkouts wiederverwenden
#    (enthält bereits funktionierende Credentials/Token), dann SSH, dann HTTPS.
if [ ! -d "$FVM_OS" ]; then
  echo "→ FVM-OS fehlt unter $FVM_OS — klone von GitHub …"
  DERIVED_URL=""
  if git -C "$TARGET" remote get-url origin >/dev/null 2>&1; then
    DERIVED_URL="$(git -C "$TARGET" remote get-url origin | sed 's#[^/]*$#FVM-OS.git#')"
  fi
  { [ -n "$DERIVED_URL" ] && git clone "$DERIVED_URL" "$FVM_OS" 2>/dev/null; } \
    || git clone git@github.com:Lars-FivMo/FVM-OS.git "$FVM_OS" 2>/dev/null \
    || git clone https://github.com/Lars-FivMo/FVM-OS.git "$FVM_OS" \
    || { echo "✗ Klonen fehlgeschlagen — der VPS hat keinen Git-Zugriff auf das private Repo FVM-OS."
         echo "  Lösung: Deploy-Key/Token für Lars-FivMo/FVM-OS hinterlegen oder manuell klonen:"
         echo "  git clone <url-mit-zugriff> $FVM_OS  — danach diesen Installer erneut ausführen."
         exit 1; }
  echo "  ✓ FVM-OS geklont nach $FVM_OS"
fi

# 1) Dateien installieren — lokale Kopie bevorzugt, sonst Download von GitHub
SRC="$(cd "$(dirname "${BASH_SOURCE[0]:-/nonexistent}")" 2>/dev/null && pwd || true)"
fetch() {
  if [ -n "$SRC" ] && [ -f "$SRC/$1" ]; then cp "$SRC/$1" "$1"; else curl -fsSL "$RAW/$1" -o "$1"; fi
  echo "  ✓ $1"
}
mkdir -p scripts context
fetch scripts/fleet_registry.py
fetch scripts/fleet_dispatch.py
fetch context/harry-team.md

# 2) .env — FVM_OS_PATH setzen (nur wenn noch nicht vorhanden)
if grep -qs '^FVM_OS_PATH=' .env; then
  echo "  ✓ .env: FVM_OS_PATH bereits gesetzt"
else
  echo "FVM_OS_PATH=$FVM_OS" >> .env
  echo "  ✓ .env: FVM_OS_PATH=$FVM_OS ergänzt"
fi

# 3) CLAUDE.md — Team-Abschnitt ergänzen (idempotent über Marker harry-team.md)
if grep -qs 'harry-team.md' CLAUDE.md; then
  echo "  ✓ CLAUDE.md: Team-Abschnitt bereits vorhanden"
else
  cat >> CLAUDE.md <<'EOF'

**Harrys Team:** Die 160 Agenten der FVM-OS-Flotte (`context/harry-team.md`).
Jede Aufgabe zuerst gegen die Flotte matchen (`scripts/fleet_registry.py`),
bei Treffer delegieren (`scripts/fleet_dispatch.py`), Ergebnisse synthetisieren.
Harry arbeitet nur selbst, wenn kein Agent passt.
EOF
  echo "  ✓ CLAUDE.md: Team-Abschnitt ergänzt"
fi

# 4) commander.py patchen — Flotte als Fallback, Backup in commander.py.bak.
#    Der Fallback ist komplett in try/except gekapselt: schlägt irgendetwas
#    fehl, verhält sich commander.py exakt wie vorher (return []).
python3 - <<'PYEOF'
import pathlib, sys

p = pathlib.Path("scripts/commander.py")
if not p.exists():
    print("  ! scripts/commander.py nicht gefunden — Patch übersprungen"); sys.exit(0)
src = p.read_text(encoding="utf-8")
if "fleet_registry" in src:
    print("  ✓ commander.py bereits gepatcht"); sys.exit(0)
anchor = "        return []  # Harry alleine, kein Fleet-Dispatch"
if anchor not in src:
    print("  ! Anker in commander.py nicht gefunden — bitte manuell patchen (PATCH-commander.md)")
    sys.exit(0)
block = """        # Harrys Team: FVM-OS-Flotte (160 Agenten) als Fallback
        try:
            from fleet_registry import match as _fleet_match
            from fleet_dispatch import dispatch as _fleet_dispatch
            _team = _fleet_match(task, top_n=3)
            if _team:
                return _fleet_dispatch(task, _team)
        except Exception as _err:
            print(f"[fleet] Fallback fehlgeschlagen: {_err}")
        return []  # Harry alleine, kein Fleet-Dispatch"""
pathlib.Path("scripts/commander.py.bak").write_text(src, encoding="utf-8")
p.write_text(src.replace(anchor, block, 1), encoding="utf-8")
print("  ✓ commander.py gepatcht (Backup: scripts/commander.py.bak)")
PYEOF

# 5) Smoke-Test: lädt die Registry die Flotte?
echo "→ Smoke-Test der Fleet-Registry:"
if FVM_OS_PATH="$FVM_OS" python3 scripts/fleet_registry.py list 2>&1 | head -5; then
  true
else
  echo "  ! Registry-Test fehlgeschlagen — liegt FVM-OS wirklich unter $FVM_OS ?"
  echo "    Pfad korrigieren: FVM_OS_PATH in .env anpassen, dann erneut testen."
fi

# 6) Harry neu starten — docker compose, sonst passenden systemd-Service suchen
if command -v docker >/dev/null 2>&1 && ls docker-compose.y*ml compose.y*ml >/dev/null 2>&1; then
  docker compose restart harry scheduler && echo "  ✓ Harry + Scheduler neu gestartet" \
    || echo "  ! Neustart fehlgeschlagen — manuell: docker compose restart harry scheduler"
elif command -v systemctl >/dev/null 2>&1; then
  # Harrys Bot läuft auf dem VPS als command-bot.service ("FVM Command Bot (Harry)")
  if systemctl list-units --all --no-legend --plain 'command-bot.service' 2>/dev/null | grep -q command-bot; then
    UNIT="command-bot.service"
  else
    UNIT="$(systemctl list-units --all --no-legend --plain '*harry*' 2>/dev/null | awk '{print $1}' | head -1)"
  fi
  if [ -n "$UNIT" ]; then
    systemctl restart "$UNIT" && echo "  ✓ systemd-Service $UNIT neu gestartet" \
      || echo "  ! Neustart von $UNIT fehlgeschlagen — manuell prüfen: systemctl status $UNIT"
  else
    echo "  → Kein Harry-Service gefunden — Harry manuell neu starten."
  fi
else
  echo "  → Kein docker compose gefunden — Harry manuell neu starten."
fi

echo ""
echo "✓ Fertig. Test in Telegram: «team status» — Harry sollte die Flotten-Größe melden."
