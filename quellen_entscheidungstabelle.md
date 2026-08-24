# Entscheidungstabelle: Quellenbewertung & -auswahl

Stand 24.08.2026. Das hier sind Vorschläge zur Diskussion, keine Festlegung — Quellenwahl
ist laut Ausschreibung explizit eure Entscheidung ("Welche Quellen ihr nehmt und warum").
Empfehlungen sind markiert, aber bitte gegenlesen und anpassen.

---

## 1. Themenblöcke (Vorschlag zur Kategorisierung)

Ziel: über die Woche eine Mischung erzwingen, statt jeden Tag dieselbe Themenart
(direkte Konsequenz aus Kriterium 1 — "klingt nicht nach Schablone").

| Block | Beispiel | Anteil/Woche (Vorschlag) |
|---|---|---|
| **Neue Modelle & Releases** | GPT-5.6, Claude-Updates, Benchmarks | max. 40% der Themen — sonst wird's zur Versions-Liturgie |
| **Tools & Alltag** | Neue Features in ChatGPT/Consumer-Apps, "was kann ich morgen nutzen" | kein Limit, das ist der Kern für Alltagsuser |
| **Kosten & Zugang** | Preisänderungen, Freetier-Kürzungen/-Erweiterungen | opportunistisch, wenn's passiert |
| **Gesellschaft & Kontroversen** | KI-Slop, Urheberrecht, Jobs, Überwachung, Deepfakes | mind. 1x/Woche fest einplanen |
| **Forschung & Ausblick** | Paper, technische Durchbrüche | dosiert, leicht erklärt |
| **Unternehmen & Markt** | Finanzierungsrunden, Wettbewerb zwischen Labs | opportunistisch |

**Empfehlung:** als weiche Regel in die Auswahl-Rubrik aufnehmen ("nicht mehr als 2 Themen
aus demselben Block pro Folge"), nicht als harte Quote — sonst zwingt man an manchen Tagen
Themen rein, die nicht da sind.

---

## 2. Zielgruppen-Typen (zur Einordnung, wo "Alltagsuser" steht)

| Typ | Merkmale | Passt zu unseren Quellen? |
|---|---|---|
| KI-Neuling | Erklärbedarf, wenig Jargon, "was heißt das für mich" | ✓ Ben's Bites, The Verge |
| **KI-Alltagsuser** *(eure Wahl)* | Kennt ChatGPT & Co., will kompakt auf dem Laufenden bleiben, kein Fachjargon nötig | ✓ passt zum aktuellen Feed-Mix |
| KI-Enthusiast/Poweruser | Verfolgt das Feld schon, will Tempo statt Erklärung | teilweise — Simon Willison, Hacker News |
| KI-Manager/Business | Kosten-Nutzen, Wettbewerbsblick, "was heißt das fürs Unternehmen" | ✗ aktiv rausgenommen (VentureBeat entfernt) |
| Entwickler/Techniker | Technische Tiefe, Tools, Benchmarks im Detail | ✗ zu tief für die Zielgruppe |

**Beobachtung:** "One Useful Thing" (Ethan Mollick) liegt leicht in Richtung Business/Manager,
nicht rein Alltagsuser — bewusst drin lassen (gute Substanz) oder rausnehmen?

---

## 3. Alter der Quellen (min–max) — **aktuell nicht technisch durchgesetzt, siehe unten**

| Format | Max. Alter | Begründung |
|---|---|---|
| Tagesfolge (Di–Fr) | **48 Stunden** | Genug Puffer für seltener aktualisierte Feeds (Simon Willison, Wired), noch "heute" |
| Montag-Rückblick | 72 Stunden | Deckt Freitagabend + Wochenende ab |
| Freitag-Wochenüberblick | 7 Tage | Zusammenfassung der Woche, keine neuen Einzelmeldungen |
| Fortsetzungsthemen | irrelevant | Nur das *neue* Update muss frisch sein, nicht das Ursprungsthema |

**Wichtig:** Das Erscheinungsdatum wird dem Aufbereitungs-Agenten aktuell **nicht** mitgegeben
— die "Aktualität"-Bewertung ist reine Texteinschätzung. Das ist ein Bug, den ich als
Erstes fixen sollte, bevor diese Tabelle überhaupt technisch wirkt.

---

## 4. Anzahl Berichte pro Thema (Quellenbreite)

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

## 5. Quellen jenseits von RSS — Vorschläge

| Option | Aufwand | Nutzen | Empfehlung |
|---|---|---|---|
| **Exa/Tavily aktiv als Suchquelle** (nicht nur Cross-Check) | niedrig, API schon vorbereitet | findet Themen, die in keinem der 8 Feeds auftauchen | ✅ naheliegendste Erweiterung, gleiche Infrastruktur wie Cross-Check |
| **Anbieter-Changelogs** (OpenAI/Anthropic/Google Release-Notes) | niedrig, oft eigene RSS-Feeds | verlässliche Primärquelle für "1 Quelle akzeptabel"-Fälle | ✅ leicht nachrüstbar, in `quellen.md` schon als Bonus gelistet |
| **Newsletter-Postfach** (The Rundown AI, TLDR AI — aus `quellen.md`, kein RSS) | hoch (eigene Mail-Adresse, IMAP-Auslesen, HTML-Parsing) | Einordnung/Kontext, den reine RSS-Teaser nicht liefern | ⚠️ nur wenn Zeit reicht, größerer Umbau |
| **Reddit** (z. B. r/artificial, r/ChatGPT, hat RSS) | niedrig | "was bewegt echte Nutzer" — passt gut zu Alltagsuser | Kür, gute Ergänzung |
| **Web-Recherche-Agent** (laut Ausschreibung explizit erwähnt) | hoch, teurer pro Lauf | findet auch Unbekanntes, keine feste Quellenliste nötig | ❌ bewusst verworfen (Kap. 4) — Zeit-/Kostenrisiko für den Sprint zu hoch |

---

*Nächster Schritt (morgen): Erscheinungsdatum in den Aufbereitungs-Prompt aufnehmen, dann
diese Tabelle Punkt für Punkt durchgehen und festlegen, was übernommen wird.*
