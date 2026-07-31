---
name: grill-me
description: "Interviewt den Nutzer intensiv zu einem Projekt, Feature oder Problem, bis echtes gemeinsames Verständnis besteht — und schreibt daraus ein Alignment-Dokument. Das ist die Alignment-Phase des KI-Developer-Loops (Vertical Slicing). Nutze diesen Skill, wenn der Nutzer /grill-me aufruft, sagt 'grill mich', 'stell mir Fragen bis wir ein gemeinsames Verständnis haben', 'analysier mein Projekt und frag mich aus', oder wenn eine größere Feature-/Projekt-Anfrage kommt, bevor implementiert wird. English triggers: 'grill me', 'interview me about this project', 'ask me questions until we're aligned'."
---

# Grill Me — Alignment durch Interview

Ziel: **Nicht implementieren.** Ziel ist, dass am Ende ein Alignment-Dokument steht,
das ein anderer Agent in einem frischen Kontext lesen und danach handeln kann.

Der häufigste Fehler ist, zwei Fragen zu stellen und dann loszubauen. Das ist kein
Alignment. Grillen heißt: so lange bohren, bis alle impliziten Annahmen des Nutzers
explizit auf dem Tisch liegen.

## Ablauf

### 1. Erst lesen, dann fragen

Wenn ein Projekt/Verzeichnis im Spiel ist: **zuerst die Codebasis anschauen**, bevor
die erste Frage gestellt wird. README, Einstiegspunkt, Verzeichnisstruktur,
package.json/pyproject, vorhandene CLAUDE.md, letzte Commits.

Das kostet ein paar Minuten und ändert alles: Fragen, deren Antwort im Repo steht,
sind verschwendete Fragen und lassen den Nutzer zu Recht denken, dass nicht zugehört wird.

Danach: kurz zusammenfassen, was verstanden wurde ("So sehe ich das Projekt: …"),
und den Nutzer das korrigieren lassen. Diese Korrektur ist oft schon der halbe Gewinn.

### 2. Grillen

Regeln für die Interview-Phase:

- **Eine Frage pro Runde**, maximal zwei wenn sie zusammengehören. Fragenlisten
  werden oberflächlich beantwortet — der Nutzer picket sich zwei raus und der Rest fällt weg.
- **Nachbohren statt weiterziehen.** Wenn eine Antwort vage ist ("soll halt schnell
  sein", "user-freundlich"), ist das das Signal zum Nachhaken, nicht zum nächsten Thema.
- **Annahmen laut aussprechen.** "Ich nehme an, X — stimmt das?" ist wertvoller als eine
  offene Frage, weil eine falsche Annahme sofort korrigiert wird.
- **Widersprüche benennen.** Wenn zwei Aussagen nicht zusammenpassen, ansprechen.
  Genau dafür ist das Interview da.
- **Nicht schmeicheln.** Wenn die Idee ein Problem hat — Scope zu groß, Konflikt mit
  bestehendem Code, Grenzfall unbedacht — jetzt sagen. Später ist es teuer.
- Sprache: die des Nutzers (in der Regel Deutsch).

Themen, die typischerweise abgeklopft werden müssen (nicht abarbeiten, sondern das
verfolgen, was in diesem Fall unklar ist):

| Bereich | Worauf zielen |
|---|---|
| Problem | Welcher konkrete Schmerz? Wer hat ihn? Was passiert, wenn nichts gebaut wird? |
| Nutzer & Nutzung | Wer benutzt das, wie oft, in welcher Situation? |
| Scope | Was gehört **nicht** dazu? (Die wichtigste Frage überhaupt.) |
| Definition of Done | Woran genau ist erkennbar, dass es fertig ist? |
| Grenzfälle | Leere Daten, Fehler, gleichzeitige Zugriffe, Offline, Migration von Altbestand |
| Constraints | Bestehender Stack, Hosting, Budget, Deadline, Dinge die nicht angefasst werden dürfen |
| Erfolg | Woran wird in vier Wochen gemessen, ob es gut war? |

### 3. Wann aufhören

Aufhören, sobald die eigenen Fragen nur noch kosmetisch werden (Benennung, Farbe,
Reihenfolge). Das ist das Signal, dass das Verständnis steht — nicht weiter Ping-Pong
spielen, sondern das Dokument schreiben.

Wenn der Nutzer vorher abbricht ("mach mal", "reicht"): das respektieren, das Dokument
mit dem schreiben, was da ist, und offene Punkte explizit als offen markieren.

### 4. Alignment-Dokument schreiben

Ablageort: `alignment/<thema>.md` im Projekt (oder wo der Nutzer es haben will).
Wenn es schon `plans/` oder `docs/` gibt, dorthin einordnen statt eine neue Konvention zu erfinden.

Struktur:

```markdown
# Alignment: <Thema>

**Datum:** <YYYY-MM-DD>  ·  **Status:** Alignment abgeschlossen

## Problem
Was gelöst wird und für wen — in den Worten des Nutzers, nicht schöngeschrieben.

## Ausgangslage
Was heute im Projekt existiert und relevant ist (aus der Code-Analyse, mit Dateipfaden).

## Entscheidungen
| Entscheidung | Begründung |
|---|---|

## Explizit nicht im Scope
- …

## Definition of Done
- [ ] Prüfbare Kriterien, kein "funktioniert gut"

## Grenzfälle & Risiken
- …

## Offene Fragen
- …  (leer, wenn nichts offen ist — dann diese Sektion weglassen)
```

Danach den Pfad nennen und den nächsten Schritt vorschlagen:
**Kontext-Reset (neuer Chat), dann Planning des ersten Vertical Slice** — mit dem
Alignment-Dokument als einzigem Kontext.

## Abgrenzung

- Dieser Skill **implementiert nichts**. Kein Code, keine Edits am Projekt außer dem
  Alignment-Dokument. Wenn der Nutzer mitten im Interview "bau das jetzt" sagt: Dokument
  fertigstellen, dann implementieren — und den Kontext-Reset dazwischen empfehlen.
- Für die Phase danach (Aufteilen in testbare Vertical Slices) ist das hier zu Ende;
  das gehört in eine eigene Session.
