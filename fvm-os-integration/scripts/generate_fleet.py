#!/usr/bin/env python3
"""Generiert den FVM-Studio-Flotten-Katalog: 160 Agenten als agents/manifest.json.

16 Abteilungen × 10 Spezialisten. Pro Agent: name, department, description,
keywords. Die System-Prompts erzeugt fleet_dispatch.py zur Laufzeit aus
Name + Beschreibung — so bleibt der Katalog schlank und leicht pflegbar.

Verwendung:
  python3 scripts/generate_fleet.py            # schreibt agents/manifest.json
  python3 scripts/generate_fleet.py --stdout   # gibt JSON auf stdout aus
"""

import json
import sys
from pathlib import Path

# (Abteilung, Abteilungs-Keywords, [(name, beschreibung, [keywords]), ...])
DEPARTMENTS = [
    ("Vertrieb & Sales", ["vertrieb", "sales"], [
        ("lead-qualifizierer", "Bewertet eingehende Leads nach Fit, Budget und Dringlichkeit.", ["lead", "qualifizierung", "scoring"]),
        ("angebots-schreiber", "Erstellt Angebote und Preisvorschläge für Kundenprojekte.", ["angebot", "offerte", "proposal"]),
        ("discovery-call-vorbereiter", "Bereitet Erstgespräche vor: Firmenprofil, Fragen, Gesprächsleitfaden.", ["discovery", "erstgespräch", "vorbereitung"]),
        ("einwand-behandler", "Formuliert Antworten auf typische Einwände in Verkaufsgesprächen.", ["einwand", "objection", "verhandlung"]),
        ("follow-up-texter", "Schreibt Nachfass-E-Mails nach Calls und Angeboten.", ["follow-up", "nachfassen", "email"]),
        ("pipeline-analyst", "Analysiert die Sales-Pipeline und priorisiert Deals.", ["pipeline", "forecast", "deals", "crm"]),
        ("kaltakquise-texter", "Schreibt personalisierte Cold-Outreach-Nachrichten.", ["kaltakquise", "outreach", "linkedin"]),
        ("referenz-sammler", "Erstellt Case Studies und Referenztexte aus Kundenprojekten.", ["referenz", "case-study", "testimonial"]),
        ("preisstratege", "Entwickelt Preismodelle und Paketstrukturen.", ["preis", "pricing", "pakete", "marge"]),
        ("vertragsverhandler", "Bereitet Verhandlungspositionen und Zugeständnislinien vor.", ["verhandlung", "vertrag", "konditionen"]),
    ]),
    ("Marketing & Ads", ["marketing", "kampagne"], [
        ("kampagnen-planer", "Plant Marketingkampagnen mit Zielen, Kanälen und Budget.", ["plan", "budget", "kanal"]),
        ("meta-ads-spezialist", "Erstellt und optimiert Facebook- und Instagram-Anzeigen.", ["meta", "facebook", "instagram", "ads"]),
        ("google-ads-spezialist", "Erstellt und optimiert Google-Suchanzeigen und Keywords.", ["google-ads", "sea", "anzeigen"]),
        ("seo-stratege", "Entwickelt SEO-Strategien und Keyword-Pläne.", ["seo", "ranking", "keywords"]),
        ("landingpage-optimierer", "Verbessert Landingpages für mehr Conversions.", ["landingpage", "conversion", "cro"]),
        ("email-marketer", "Konzipiert E-Mail-Sequenzen und Marketing-Automationen.", ["email", "newsletter", "sequenz"]),
        ("funnel-architekt", "Entwirft Marketing-Funnels vom Lead bis zum Abschluss.", ["funnel", "leadmagnet", "trichter"]),
        ("zielgruppen-analyst", "Erstellt Personas und Zielgruppenanalysen.", ["persona", "zielgruppe", "icp"]),
        ("wettbewerbs-beobachter", "Analysiert Wettbewerber-Marketing und Positionierung.", ["wettbewerb", "konkurrenz", "analyse"]),
        ("messaging-stratege", "Schärft Positionierung, USPs und Kernbotschaften.", ["positionierung", "usp", "botschaft"]),
    ]),
    ("Content & Copy", ["content", "text"], [
        ("blog-autor", "Schreibt SEO-optimierte Blogartikel.", ["blog", "artikel", "seo"]),
        ("newsletter-autor", "Schreibt Newsletter-Ausgaben im FVM-Tonfall.", ["newsletter", "ausgabe"]),
        ("conversion-copywriter", "Schreibt verkaufsstarke Texte für Ads und Salespages.", ["copywriting", "salespage", "werbetext"]),
        ("whitepaper-autor", "Erstellt Whitepaper und Leitfäden für die Lead-Generierung.", ["whitepaper", "leitfaden", "ebook"]),
        ("skript-autor", "Schreibt Skripte für Videos und Webinare.", ["skript", "drehbuch", "webinar"]),
        ("storytelling-experte", "Verwandelt Fakten in Geschichten und Narrative.", ["story", "narrativ", "storytelling"]),
        ("redaktionsplaner", "Erstellt und pflegt Redaktions- und Themenpläne.", ["redaktionsplan", "themenplan", "kalender"]),
        ("lektor", "Korrigiert Rechtschreibung, Grammatik und Stil.", ["lektorat", "korrektur", "rechtschreibung"]),
        ("uebersetzer-de-en", "Übersetzt Inhalte zwischen Deutsch und Englisch.", ["übersetzung", "englisch", "translation"]),
        ("headline-spezialist", "Entwickelt Überschriften, Hooks und Betreffzeilen.", ["headline", "hook", "betreff"]),
    ]),
    ("Social Media", ["social-media"], [
        ("linkedin-stratege", "Plant und schreibt LinkedIn-Posts für Personal Branding.", ["linkedin", "post", "personal-brand"]),
        ("instagram-planer", "Plant Instagram-Content: Posts, Reels, Stories.", ["instagram", "reels", "stories"]),
        ("youtube-stratege", "Entwickelt YouTube-Konzepte, Titel und Beschreibungen.", ["youtube", "video", "titel"]),
        ("tiktok-trendscout", "Identifiziert TikTok-Trends und Formatideen.", ["tiktok", "trends", "viral"]),
        ("community-manager", "Formuliert Antworten auf Kommentare und Nachrichten.", ["community", "kommentare", "antworten"]),
        ("carousel-texter", "Textet Carousel-Slides für LinkedIn und Instagram.", ["carousel", "slides"]),
        ("hashtag-rechercheur", "Recherchiert Hashtags und optimale Posting-Zeiten.", ["hashtag", "reichweite", "timing"]),
        ("repurposing-spezialist", "Verwandelt lange Inhalte in Social-Media-Schnipsel.", ["repurposing", "schnipsel", "zweitverwertung"]),
        ("engagement-analyst", "Analysiert Social-Media-Kennzahlen und leitet Maßnahmen ab.", ["engagement", "kpi", "insights"]),
        ("social-ads-texter", "Textet Anzeigenvarianten für Social-Kampagnen.", ["social-ads", "varianten", "anzeige"]),
    ]),
    ("Research & Analyse", ["research", "recherche", "analyse"], [
        ("markt-rechercheur", "Recherchiert Märkte, Branchen und Trends.", ["markt", "branche", "trend"]),
        ("tool-scout", "Bewertet neue KI-Tools und Software im Vergleich.", ["tool", "software", "bewertung"]),
        ("ki-news-kurator", "Kuratiert relevante KI-News für FVM-Studio.", ["ki-news", "kuratierung", "ai"]),
        ("studien-zusammenfasser", "Fasst Studien und Reports kompakt zusammen.", ["studie", "report", "zusammenfassung"]),
        ("daten-analyst", "Analysiert Datensätze und erstellt Auswertungen.", ["daten", "auswertung", "statistik", "csv"]),
        ("umfrage-designer", "Entwirft Umfragen und Fragebögen.", ["umfrage", "fragebogen", "feedback"]),
        ("quellen-finder", "Identifiziert Experten, Podcasts und Quellen zu Themen.", ["experten", "quellen", "podcast"]),
        ("faktenchecker", "Prüft Behauptungen und Quellenlagen.", ["fakten", "verifikation", "prüfung"]),
        ("benchmark-analyst", "Vergleicht Anbieter, Preise und Leistungen.", ["benchmark", "vergleich", "anbieter"]),
        ("trend-radar", "Beobachtet Zukunftstrends mit Relevanz für KMU.", ["zukunft", "radar", "früherkennung"]),
    ]),
    ("Finanzen & Buchhaltung", ["finanzen", "geld"], [
        ("beleg-erfasser", "Strukturiert Belege und Ausgaben für die Buchhaltung.", ["beleg", "buchhaltung", "ausgabe"]),
        ("rechnungs-schreiber", "Erstellt Rechnungsentwürfe und Zahlungserinnerungen.", ["rechnung", "mahnung", "zahlung"]),
        ("liquiditaets-planer", "Plant Cashflow und Liquidität.", ["liquidität", "cashflow", "planung"]),
        ("steuer-vorbereiter", "Bereitet Unterlagen für den Steuerberater vor.", ["steuer", "umsatzsteuer", "steuerberater"]),
        ("abo-controller", "Überwacht Tool-Abos und Fixkosten.", ["abo", "fixkosten", "toolkosten"]),
        ("projekt-kalkulator", "Kalkuliert Projektkosten, Stundensätze und Margen.", ["kalkulation", "marge", "stundensatz"]),
        ("umsatz-reporter", "Erstellt Umsatz- und Erfolgsübersichten.", ["umsatz", "report", "monatsabschluss"]),
        ("foerder-scout", "Recherchiert Fördermittel und Zuschüsse für KMU-Projekte.", ["förderung", "zuschuss", "digitalisierung"]),
        ("investitions-bewerter", "Bewertet Anschaffungen nach Kosten-Nutzen.", ["investition", "roi", "bewertung"]),
        ("zahlungs-tracker", "Verfolgt offene Posten und Zahlungseingänge.", ["offene-posten", "zahlungseingang", "mahnwesen"]),
    ]),
    ("Recht & Compliance", ["recht", "legal"], [
        ("dsgvo-berater", "Beantwortet Datenschutzfragen nach DSGVO.", ["datenschutz", "dsgvo", "privacy"]),
        ("av-vertrags-pruefer", "Prüft Auftragsverarbeitungsverträge.", ["av-vertrag", "auftragsverarbeitung"]),
        ("ai-act-berater", "Bewertet KI-Einsatz nach EU AI Act und Risikoklassen.", ["ai-act", "eu", "risikoklasse"]),
        ("impressum-pruefer", "Prüft Impressum und Pflichtangaben von Websites.", ["impressum", "pflichtangaben"]),
        ("vertrags-entwerfer", "Entwirft Dienstleistungsverträge und AGB-Bausteine.", ["vertrag", "agb", "entwurf"]),
        ("urheberrechts-berater", "Beantwortet Fragen zu Urheberrecht und Lizenzen.", ["urheberrecht", "lizenz", "bildrechte"]),
        ("datenschutzerklaerung-autor", "Erstellt und aktualisiert Datenschutzerklärungen.", ["datenschutzerklärung", "cookies"]),
        ("compliance-checker", "Prüft Prozesse auf Compliance-Risiken.", ["compliance", "risiko", "audit"]),
        ("markenrecht-scout", "Recherchiert Markenkonflikte vor Namensgebungen.", ["marke", "markenrecht", "namensprüfung"]),
        ("betroffenenrechte-bearbeiter", "Bearbeitet Auskunfts- und Löschanfragen nach DSGVO.", ["auskunft", "löschung", "betroffenenrechte"]),
    ]),
    ("Kundenprojekte & Delivery", ["projekt", "delivery"], [
        ("projekt-planer", "Erstellt Projektpläne mit Meilensteinen und Timeline.", ["projektplan", "meilenstein", "timeline"]),
        ("onboarding-manager", "Strukturiert Kunden-Onboardings und Kickoffs.", ["onboarding", "kickoff", "projektstart"]),
        ("anforderungs-analyst", "Übersetzt Kundenwünsche in klare Anforderungen.", ["anforderung", "briefing", "scope"]),
        ("statusbericht-autor", "Schreibt Statusberichte und Updates für Kunden.", ["status", "bericht", "update"]),
        ("meeting-protokollant", "Fasst Meetings in Protokolle und To-dos zusammen.", ["protokoll", "meeting", "todos"]),
        ("risiko-manager", "Identifiziert Projektrisiken und Gegenmaßnahmen.", ["risiko", "blocker", "eskalation"]),
        ("uebergabe-dokumentierer", "Erstellt Übergabe- und Abschlussdokumentationen.", ["übergabe", "abschluss", "dokumentation"]),
        ("feedback-einholer", "Formuliert Feedback-Anfragen und wertet sie aus.", ["feedback", "zufriedenheit", "nps"]),
        ("scope-waechter", "Erkennt Scope Creep und formuliert Change Requests.", ["scope-creep", "change-request", "mehraufwand"]),
        ("retro-moderator", "Bereitet Retrospektiven vor und fasst Learnings zusammen.", ["retrospektive", "learnings", "verbesserung"]),
    ]),
    ("Automatisierung & n8n", ["automation", "automatisierung", "n8n"], [
        ("n8n-architekt", "Entwirft n8n-Workflows für Kundenprozesse.", ["workflow", "design", "nodes"]),
        ("workflow-debugger", "Analysiert fehlgeschlagene Workflow-Läufe.", ["fehler", "debug", "log"]),
        ("api-integrator", "Plant API-Anbindungen zwischen Tools.", ["api", "integration", "schnittstelle"]),
        ("automatisierungs-scout", "Findet Automatisierungspotenziale in Prozessen.", ["potenzial", "prozess", "einsparung"]),
        ("webhook-spezialist", "Konzipiert Webhook-Logik und Trigger.", ["webhook", "trigger", "event"]),
        ("daten-mapper", "Definiert Feld-Mappings zwischen Systemen.", ["mapping", "felder", "transformation"]),
        ("prozess-dokumentierer", "Dokumentiert Workflows nachvollziehbar als SOP.", ["sop", "anleitung", "doku"]),
        ("plattform-berater", "Vergleicht Automatisierungsplattformen je Use Case.", ["zapier", "make", "vergleich"]),
        ("monitoring-planer", "Definiert Alerts und Überwachung für Automationen.", ["monitoring", "alert", "ausfall"]),
        ("automatisierbarkeits-bewerter", "Bewertet, ob Aufgaben für Automatisierung taugen.", ["machbarkeit", "aufwand", "nutzen"]),
    ]),
    ("Entwicklung & Tech", ["code", "entwicklung", "tech"], [
        ("code-reviewer", "Reviewt Code auf Fehler und Verbesserungen.", ["review", "bug", "qualität"]),
        ("python-entwickler", "Schreibt und erklärt Python-Skripte.", ["python", "skript"]),
        ("web-entwickler", "Baut und verbessert Websites mit Next.js und React.", ["nextjs", "react", "website", "frontend"]),
        ("datenbank-designer", "Entwirft Datenmodelle und SQL-Abfragen.", ["datenbank", "sql", "schema"]),
        ("devops-berater", "Berät zu Server, Docker und Deployment.", ["docker", "server", "deployment", "vps"]),
        ("prompt-engineer", "Optimiert Prompts für KI-Anwendungen.", ["prompt", "optimierung", "llm"]),
        ("mcp-spezialist", "Entwirft MCP-Server und Tool-Anbindungen für Claude.", ["mcp", "claude", "tools"]),
        ("security-auditor", "Prüft Anwendungen auf Sicherheitslücken.", ["security", "sicherheit", "audit"]),
        ("performance-optimierer", "Findet und behebt Performance-Probleme.", ["performance", "ladezeit", "optimierung"]),
        ("tech-erklaerer", "Übersetzt Technik in verständliche Kundensprache.", ["erklärung", "verständlich", "übersetzen"]),
    ]),
    ("Design & Brand", ["design", "gestaltung"], [
        ("brand-waechter", "Wacht über Markenauftritt und CI-Konsistenz.", ["brand", "ci", "konsistenz"]),
        ("praesentations-designer", "Strukturiert und gestaltet Pitch-Decks.", ["präsentation", "pitch", "slides"]),
        ("canva-konzepter", "Erstellt Konzepte und Texte für Canva-Designs.", ["canva", "grafik", "vorlage"]),
        ("ui-berater", "Gibt Feedback zu Interfaces und Usability.", ["ui", "ux", "usability"]),
        ("bildprompt-designer", "Schreibt Prompts für KI-Bildgenerierung.", ["bildprompt", "midjourney", "generierung"]),
        ("infografik-konzepter", "Verwandelt Daten in Infografik-Konzepte.", ["infografik", "visualisierung"]),
        ("design-briefing-autor", "Erstellt Design-Briefings für Logos und CI.", ["logo", "briefing"]),
        ("farb-typo-berater", "Berät zu Farbpaletten und Typografie.", ["farbe", "schrift", "palette"]),
        ("website-strukturierer", "Entwirft Seitenstrukturen und Wireframe-Texte.", ["wireframe", "struktur", "sitemap"]),
        ("asset-organisator", "Strukturiert Design-Assets und Bibliotheken.", ["assets", "bibliothek", "ordnung"]),
    ]),
    ("Video & Audio", ["video", "audio"], [
        ("video-konzepter", "Entwickelt Videokonzepte und Storyboards.", ["konzept", "storyboard"]),
        ("schnitt-planer", "Erstellt Schnittpläne und Timecodes.", ["schnitt", "edit", "timecode"]),
        ("untertitel-ersteller", "Erstellt und korrigiert Untertitel.", ["untertitel", "captions", "srt"]),
        ("podcast-produzent", "Plant Podcast-Folgen und schreibt Shownotes.", ["podcast", "folge", "shownotes"]),
        ("voiceover-texter", "Schreibt Sprechertexte für Videos.", ["voiceover", "sprechertext"]),
        ("thumbnail-konzepter", "Konzipiert Thumbnails mit Text- und Bildidee.", ["thumbnail", "klickrate"]),
        ("kurzform-formatierer", "Schneidet lange Videos konzeptionell auf Reels und Shorts zu.", ["reels", "shorts", "kurzform"]),
        ("transkript-aufbereiter", "Bereinigt und strukturiert Transkripte.", ["transkript", "whisper", "aufbereitung"]),
        ("musik-sound-berater", "Empfiehlt Musik und Sounddesign.", ["musik", "sound", "lizenzfrei"]),
        ("webinar-regisseur", "Plant Ablauf und Dramaturgie von Webinaren.", ["webinar", "ablauf", "dramaturgie"]),
    ]),
    ("Kundensupport & CRM", ["support", "kundenservice"], [
        ("support-antworter", "Beantwortet Kundenanfragen empathisch und lösungsorientiert.", ["anfrage", "antwort", "ticket"]),
        ("faq-autor", "Erstellt FAQ-Artikel aus wiederkehrenden Fragen.", ["faq", "wissensdatenbank"]),
        ("beschwerde-manager", "Deeskaliert Beschwerden und formuliert Lösungen.", ["beschwerde", "deeskalation", "kulanz"]),
        ("crm-pfleger", "Hält Kundendaten strukturiert und aktuell.", ["crm", "kontakte", "datenpflege"]),
        ("kuendigungs-retter", "Formuliert Rückgewinnungsangebote bei Kündigungen.", ["kündigung", "churn", "rückgewinnung"]),
        ("upsell-erkenner", "Erkennt Upsell-Chancen bei Bestandskunden.", ["upsell", "cross-sell", "bestandskunde"]),
        ("willkommens-mailer", "Schreibt Willkommens- und Einführungsmails.", ["willkommen", "einführung", "mail"]),
        ("zufriedenheits-tracker", "Wertet Kundenfeedback systematisch aus.", ["zufriedenheit", "bewertungen", "auswertung"]),
        ("eskalations-koordinator", "Strukturiert Eskalationsfälle für Lars.", ["eskalation", "dringend", "koordination"]),
        ("bewertungs-manager", "Holt Google- und Trustpilot-Bewertungen ein und beantwortet sie.", ["rezension", "google", "trustpilot"]),
    ]),
    ("Strategie & Produkt", ["strategie"], [
        ("geschaeftsmodell-analyst", "Analysiert und entwickelt Geschäftsmodelle.", ["geschäftsmodell", "canvas"]),
        ("produkt-entwickler", "Entwickelt Angebots- und Produktideen.", ["produkt", "angebot", "paketierung"]),
        ("okr-coach", "Formuliert Ziele und Key Results.", ["okr", "ziele", "quartal"]),
        ("swot-analyst", "Erstellt SWOT- und Risikoanalysen.", ["swot", "stärken", "risiken"]),
        ("pivot-berater", "Bewertet strategische Richtungswechsel.", ["pivot", "richtungswechsel", "entscheidung"]),
        ("partnerschafts-scout", "Identifiziert Kooperations- und Partnerchancen.", ["partner", "kooperation"]),
        ("skalierungs-planer", "Plant Wachstum und Kapazitäten.", ["skalierung", "wachstum", "kapazität"]),
        ("entscheidungs-vorbereiter", "Bereitet Entscheidungen mit Optionen und Trade-offs auf.", ["optionen", "abwägung", "tradeoff"]),
        ("vision-schaerfer", "Schärft Vision, Mission und Werte.", ["vision", "mission", "werte"]),
        ("quartals-reviewer", "Strukturiert Quartalsrückblicke und -planung.", ["quartalsreview", "rückblick", "planung"]),
    ]),
    ("HR & Organisation", ["hr", "organisation", "team"], [
        ("stellenprofil-autor", "Erstellt Stellen- und Rollenprofile.", ["stelle", "rolle", "profil"]),
        ("freelancer-scout", "Definiert Anforderungen und Suchstrategien für Freelancer.", ["freelancer", "suche", "brief"]),
        ("einarbeitungs-strukturierer", "Baut Einarbeitungspläne für neue Teammitglieder.", ["einarbeitung", "plan"]),
        ("sop-autor", "Schreibt Standard Operating Procedures.", ["sop", "prozess", "anleitung"]),
        ("meeting-strukturierer", "Optimiert Meeting-Formate und Agenden.", ["agenda", "meeting", "effizienz"]),
        ("wissens-organisator", "Strukturiert internes Wissen in Obsidian und Notion.", ["wissen", "obsidian", "notion"]),
        ("kultur-berater", "Entwickelt Team-Rituale und Zusammenarbeitsregeln.", ["kultur", "rituale", "zusammenarbeit"]),
        ("delegations-coach", "Hilft, Aufgaben delegierbar zu machen.", ["delegation", "übergabe", "entlastung"]),
        ("zeitmanagement-coach", "Optimiert Kalender, Fokuszeiten und ADHS-gerechte Routinen.", ["zeitmanagement", "fokus", "adhs", "routine"]),
        ("feedback-formulierer", "Formuliert konstruktives Feedback für Gespräche.", ["kritik", "gespräch", "wertschätzung"]),
    ]),
    ("Office & Assistenz", ["assistenz", "büro", "alltag"], [
        ("email-sortierer", "Priorisiert und beantwortet E-Mail-Rückstände.", ["email", "posteingang", "priorisierung"]),
        ("termin-koordinator", "Plant Termine und löst Kalenderkonflikte.", ["termin", "kalender", "koordination"]),
        ("reise-planer", "Plant Geschäftsreisen mit Routen und Budget.", ["reise", "hotel", "route"]),
        ("dokument-formatierer", "Bringt Dokumente in saubere, einheitliche Form.", ["formatierung", "vorlage", "dokument"]),
        ("schnell-rechercheur", "Erledigt schnelle Alltagsrecherchen.", ["kurzrecherche", "info", "schnell"]),
        ("erinnerungs-manager", "Strukturiert Wiedervorlagen und Deadlines.", ["erinnerung", "deadline", "wiedervorlage"]),
        ("einkaufs-berater", "Vergleicht Anschaffungen und holt Optionen ein.", ["einkauf", "vergleich", "bestellung"]),
        ("vorlagen-bauer", "Erstellt wiederverwendbare Vorlagen und Checklisten.", ["checkliste", "template"]),
        ("daily-brief-zuarbeiter", "Liefert Bausteine für den morgendlichen Daily Brief.", ["daily-brief", "morgen", "übersicht"]),
        ("ablage-organisator", "Strukturiert Dateiablagen und Benennungskonventionen.", ["ablage", "ordner", "benennung"]),
    ]),
]


def build_manifest() -> dict:
    agents = []
    for department, dept_keywords, members in DEPARTMENTS:
        for name, description, keywords in members:
            agents.append({
                "name": name,
                "department": department,
                "description": description,
                "keywords": sorted(set(keywords) | set(dept_keywords)),
            })
    names = [a["name"] for a in agents]
    assert len(names) == len(set(names)), "Agenten-Namen müssen eindeutig sein"
    return {
        "fleet": "FVM-Studio Flotte",
        "version": 1,
        "count": len(agents),
        "agents": agents,
    }


def main() -> int:
    manifest = build_manifest()
    payload = json.dumps(manifest, ensure_ascii=False, indent=1)
    if "--stdout" in sys.argv:
        print(payload)
        return 0
    out = Path(__file__).resolve().parent.parent / "agents" / "manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(payload + "\n", encoding="utf-8")
    print(f"{manifest['count']} Agenten → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
