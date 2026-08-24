# Entscheidungstabelle: Quellenbewertung & -auswahl

Stand 24.08.2026, **entschieden von Christian am 24.08.2026 abends**. Umsetzung folgt morgen.

---

## 1. Themenblöcke — ✅ entschieden

Ziel: über die Woche eine Mischung erzwingen, statt jeden Tag dieselbe Themenart
(direkte Konsequenz aus Kriterium 1 — "klingt nicht nach Schablone").

| Block | Beispiel | Anteil/Woche |
|---|---|---|
| **Neue Modelle & Releases** | GPT-5.6, Claude-Updates, Benchmarks | **max. 30%** der Themen |
| **Tools & Alltag** | Neue Features in ChatGPT/Consumer-Apps, "was kann ich morgen nutzen" | kein Limit, das ist der Kern für Alltagsuser |
| **Kosten & Zugang** | Preisänderungen, Freetier-Kürzungen/-Erweiterungen | opportunistisch, wenn's passiert |
| **Gesellschaft & Kontroversen** | KI-Slop, Urheberrecht, Jobs, Überwachung, Deepfakes | **mind. 2–3x/Woche fest einplanen** |
| **Forschung & Ausblick** | Paper, technische Durchbrüche | dosiert, leicht erklärt |
| **Unternehmen & Markt** | Finanzierungsrunden, Wettbewerb zwischen Labs | opportunistisch |

**Entschieden:** weiche Regel, keine harte Quote — sonst zwingt man an manchen Tagen Themen
rein, die nicht da sind. Umsetzung: Themenblock-Feld im Aufbereitungs-Agenten ergänzen,
dann in `select.py` als weiche Gewichtung (nicht harter Filter) einbauen.

---

## 2. Zielgruppen-Typen (zur Einordnung, wo "Alltagsuser" steht)

| Typ | Merkmale | Passt zu unseren Quellen? |
|---|---|---|
| KI-Neuling | Erklärbedarf, wenig Jargon, "was heißt das für mich" | ✓ Ben's Bites, The Verge |
| **KI-Alltagsuser** *(eure Wahl)* | Kennt ChatGPT & Co., will kompakt auf dem Laufenden bleiben, kein Fachjargon nötig | ✓ passt zum aktuellen Feed-Mix |
| KI-Enthusiast/Poweruser | Verfolgt das Feld schon, will Tempo statt Erklärung | teilweise — Simon Willison, Hacker News |
| KI-Manager/Business | Kosten-Nutzen, Wettbewerbsblick, "was heißt das fürs Unternehmen" | ✗ aktiv rausgenommen (VentureBeat entfernt) |
| Entwickler/Techniker | Technische Tiefe, Tools, Benchmarks im Detail | ✗ zu tief für die Zielgruppe |

**Entschieden:** "One Useful Thing" bleibt drin (gute Substanz wichtiger als reine
Zielgruppen-Passung).

---

## 3. Alter der Quellen — ✅ entschieden

| Format | Max. Alter | Begründung |
|---|---|---|
| Tagesfolge + Montag-Rückblick | **72 Stunden** (einheitlich) | Genug Puffer für seltener aktualisierte Feeds, deckt auch übers Wochenende |
| Freitag-Wochenüberblick | 7 Tage | Zusammenfassung der Woche, keine neuen Einzelmeldungen — strukturell anderer Fall, keine "frische Meldung" |
| Fortsetzungsthemen | irrelevant | Nur das *neue* Update muss frisch sein, nicht das Ursprungsthema |

**Wichtig:** Das Erscheinungsdatum wird dem Aufbereitungs-Agenten aktuell **nicht** mitgegeben
— die "Aktualität"-Bewertung ist reine Texteinschätzung. Das ist ein Bug, den ich als
Erstes fixen sollte, bevor diese Tabelle überhaupt technisch wirkt.

---

## 4. Anzahl Berichte pro Thema (Quellenbreite) — ✅ entschieden wie vorgeschlagen

| Anzahl unabhängiger Quellen | Einstufung | Konsequenz |
|---|---|---|
| 1 Quelle, offizieller Anbieter-Blog (Primärquelle für eigene Ankündigung) | akzeptabel | normal aufnehmen |
| 1 Quelle, sonst | **Achtung** | nur mit Cross-Check-Bestätigung (Exa) aufnehmen, sonst als "unbestätigt" kennzeichnen oder weglassen |
| 2 Quellen | Standard | normal aufnehmen |
| 3+ Quellen | hohe Priorität | tendenziell in die Top-Auswahl |

**Vorschlag für die Score-Skala (Quellenbreite 0–10):** 1 Quelle ohne Primärquellen-Status
→ 2–3 Punkte, 2 Quellen → 5–6, 3+ Quellen → 8–10.

**Aktuelle Lücke:** Der Aufbereitungs-Agent bewertet jeden Rohartikel einzeln und sieht nicht,
ob andere Artikel im selben Sammellauf dasselbe Thema behandeln — "Quellenbreite" ist
aktuell eine Schätzung aus dem Text, kein echter Abgleich mehrerer Artikel. Für echte
Quellenbreite bräuchte es einen Clustering-Schritt vor der Bewertung (Themen erst gruppieren,
dann pro Gruppe die Anzahl zählen).

---

## 5. Quellen jenseits von RSS — ✅ entschieden

| Option | Aufwand | Nutzen | Status |
|---|---|---|---|
| **Reddit** (r/artificial, r/ChatGPT, hat RSS) | niedrig | "was bewegt echte Nutzer" — passt gut zu Alltagsuser | ✅ **wird aufgenommen** |
| **Exa/Tavily aktiv als Suchquelle** (nicht nur Cross-Check) | niedrig, API schon vorbereitet | findet Themen, die in keinem Feed auftauchen | offen, gleiche Infrastruktur wie Cross-Check |
| **Anbieter-Changelogs** (OpenAI/Anthropic/Google Release-Notes) | niedrig, oft eigene RSS-Feeds | verlässliche Primärquelle für "1 Quelle akzeptabel"-Fälle | offen |
| **Newsletter-Postfach** (The Rundown AI, TLDR AI — kein RSS) | hoch (eigene Mail-Adresse, IMAP, HTML-Parsing) | Einordnung/Kontext, den RSS-Teaser nicht liefern | zurückgestellt |
| **Web-Recherche-Agent** | hoch, teurer pro Lauf | findet auch Unbekanntes | ❌ verworfen (Kap. 4) — Zeit-/Kostenrisiko zu hoch |

---

## Umsetzung morgen (Reihenfolge)

1. Erscheinungsdatum in den Aufbereitungs-Prompt aufnehmen (Bugfix, Voraussetzung für Punkt 3)
2. 72-Stunden-Filter technisch durchsetzen
3. Themenblock-Feld im Aufbereitungs-Agenten ergänzen + weiche 30%/2-3x-Regel in `select.py`
4. Reddit-Feeds suchen, verifizieren, in `config.py` aufnehmen
