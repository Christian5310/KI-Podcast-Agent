# Strategie- & Projektübersicht: KI-News-Podcast

**Stand:** 24.08.2026 · **Status:** [ ] Idee &nbsp; [ ] Recherche läuft &nbsp; [x] Entscheidungsgrundlage &nbsp; [ ] Umsetzung &nbsp; [ ] Live
**Projekttyp:** [x] Build-Projekt (eigenes System wird gebaut) &nbsp; [ ] Rollout-/Adoptions-Projekt
**Projektverantwortlich:** Christian · **Entscheider:** Christian (+ Teampartner, sobald an Bord)
**Quellen/Grundlage:** `podcast_Handbuch.pdf` (Ausschreibung „Der Podcast", FBS Future Education UG, Kurs KI-Manager) · Recherche-Chat vom 24.08.2026 · öffentliche Startseite podpresso.ai/app.podpresso.ai · Anbieter-Recherche EUrouter/Tavily/Exa/TTS

> *Dieses Dokument ist die Antwort auf die FBS-Ausschreibung „Der Podcast". Es ist die gemeinsame Entscheidungsgrundlage, bevor der Bau beginnt — noch kein Code, keine Prompts, keine Architektur-Entscheidung ist hier schon final umgesetzt.*

> **Kalender-Hinweis:** Die Ausschreibung datiert exakt auf heute (Montag, 24.08.2026) und beschreibt selbst den Ablauf „Montag und Dienstag baut ihr, am Mittwoch hören wir uns an". Das heißt: **wir stehen bereits an Tag 1 von 3.** Kriterium 7 verlangt zusätzlich, dass das System spätestens Dienstag produktiv läuft, damit am Mittwoch zwei Podcasts von zwei verschiedenen Tagen vorliegen. Der Phasenplan (Kapitel 5) ist entsprechend eng getaktet.

---

## Systemarchitektur im Überblick

Die Ausschreibung gibt die Grundstruktur bereits vor: **zwei entkoppelte Takte**, die bewusst nicht in einem einzigen Morgenlauf vermischt werden dürfen — sonst beginnt das System erst um sieben Uhr zu suchen und hofft, bis acht fertig zu werden.

**Takt 1 — Sammeln & Aufbereiten** *(nicht zeitkritisch, läuft beliebig oft über den Tag)*

1. **Quellen** — mehrere Quellentypen liefern Rohnachrichten (Auswahl in Kapitel 4).
2. **Aufbereitung** — beantwortet pro Rohnachricht drei Fragen: *Haben wir das schon?* (Dedupe über Formulierungen hinweg) · *Stimmt das überhaupt?* (Cross-Check mehrerer Quellen) · *Gehört das zu etwas Laufendem?* (Fortsetzung, mit explizitem „was ist neu").
3. **Datenbank** — das Gedächtnis: vorbereitete Themen mit Quelle, Datum, Status und Verlaufs-Referenz.

**Takt 2 — Morgenlauf** *(zeitkritisch, einmal täglich, muss vor 8:00 Uhr fertig sein)*

4. **Auswahl** — nimmt ausschließlich, was in der Datenbank bereitliegt. Keine Live-Recherche mehr.
5. **Manuskript** — ca. 1.400–1.600 Wörter, im festgelegten Ton (siehe Kapitel 3), knüpft bei Fortsetzungsthemen am letzten Stand an.
6. **Produktion** — Text-to-Speech, fertige Audiodatei + Manuskript werden abgelegt.

Vor Schritt 6 steht ein **Qualitäts-Gate**: ein zweites Modell prüft jede Zahl und jeden Eigennamen im Manuskript gegen die Quellen (Kriterium 5). Erst danach wird ausgeliefert.

**Agent vs. Code:** Jeder der sechs Kästen wird einzeln entschieden — kostet er bei jedem Lauf Geld und trifft eine inhaltliche Entscheidung (→ LLM-Agent), oder ist er deterministischer Code (→ kostenlos, entscheidet nichts)? Diese Zuordnung steht in Kapitel 3 je Anforderung und wird am Mittwoch abgefragt (Kriterium 6).

---

## 1. Ausgangslage & Scope

**Warum jetzt?**
Die FBS Future Education UG schreibt im Kurs KI-Manager einen dreitägigen Wettbewerb aus: Ein Zweierteam-System soll den bisherigen Kurs-Podcast podpresso.ai ablösen. Podpresso wird konkret dafür kritisiert, Themen ohne neuen Inhalt zu wiederholen, keine erkennbare Kontinuität zu zeigen und nach kurzer Zeit vorhersehbar zu wirken. Der Gewinner-Podcast ersetzt podpresso ab der Entscheidung im Unterricht; die FBS übernimmt dann die laufenden Schnittstellenkosten.

**Geklärter Umfang** (abgestimmt am 24.08.2026):

| Bereich | Im Scope? |
|---|---|
| Vollautomatischer Morgenlauf Mo–Fr, fertig vor 8:00 Uhr | ✅ Ja |
| Mind. 4 Themen/Folge, je mit aufrufbarer Quelle | ✅ Ja |
| Themen-Gedächtnis (Dedupe, Cross-Check, Fortsetzungserkennung) | ✅ Ja |
| Fakten-/Zahlenabgleich gegen Quellen vor Auslieferung | ✅ Ja |
| Kosten-/Modell-Logging pro Lauf | ✅ Ja |
| Montag-Sonderformat (Wochenend-Rückblick) | ✅ Ja |
| Freitag-Sonderformat (Wochenüberblick, keine Wiederholung) | ✅ Ja |
| Zwei-Stimmen-Dialog als Manuskriptform | ✅ Ja |
| Backfill: nachträgliche Erzeugung für vergangene Tage | ✅ Ja |
| Minimale Zustellung (Audiodatei öffentlich erreichbar + Tages-/Archiv-Liste mit Quellen) | ✅ Ja — ohne das ist der Podcast nicht „live"-fähig, auch wenn die 7 Kriterien technisch erfüllt sind |
| Ausgebaute Web-Oberfläche (eigener Player, Design, Suche/Filter) | ⚠️ Kür — nur wenn danach noch Zeit bleibt |
| Personalisierung pro einzelnem Hörer (wie podpresso Cappuccino/Doppio) | ❌ Nein — ein gemeinsamer Podcast für den ganzen Kurs |
| Mehrsprachigkeit (DE + EN) | ❌ Nein — nur Deutsch, Zielgruppe deutsche KI-Manager/Mittelstand |
| Live-Websuche im Morgenlauf selbst | ❌ Nein — Takt 2 recherchiert laut Vorgabe nicht mehr selbst |

**Nutzerkreis:** Hörer sind die Teilnehmer:innen des Kurses KI-Manager (Publikum, kein Login, keine Rollen). Bauteam: Christian + Teampartner (aktuell offen, siehe Kapitel 8). Kein Rechte-/Rollenkonzept nötig.

**Eingangskanäle/Datenquellen:** Noch nicht final festgelegt — Empfehlung und Optionsvergleich in Kapitel 4. Grundsätzlich vorgesehen: Kombination aus kostenlosen RSS-Feeds und einer Such-API für Tiefe/Cross-Check.

**Vorhandene Bausteine:** EUrouter-Zugang über den Kurs (LLM-Gateway). Christian hat zusätzlich eigene API-Keys bei mindestens einem weiteren Anbieter (welche genau ist offen, siehe Kapitel 8). GitHub-Account vorhanden, das Projekt-Repository selbst existiert noch nicht.

**Erkannte Lücke(n) im Referenzprodukt:** podpresso.ai wiederholt Themen ohne erkennbaren neuen Inhalt, macht Kontinuität zwischen Folgen nicht sichtbar, verlinkt Quellen nicht öffentlich nachvollziehbar und ist auf Breite („100+ Quellen", alle KI-Themen) statt auf Tiefe für deutsche Unternehmen/KI-Manager optimiert. Genau hier soll unser System ansetzen.

---

## 2. Referenz-/Marktanalyse — Lernen von den Besten

*Umfang bewusst schlank gehalten (3-Tage-Sprint): Fokus auf den einen echten Konkurrenten, den es zu schlagen gilt.*

### 2.1 podpresso.ai — der zu schlagende Kurs-Podcast

**Aufbau:** Laut eigener öffentlicher Startseite (app-interner Bereich ist login-pflichtig, dort war ich nicht — Registrierung ist eine Ausnahme-Handlung, die ich nicht ungefragt vornehme): Über 100 Quellen (Blogs, Papers/arXiv, Social Media, Newsletter, offizielle Firmen-Ankündigungen) werden morgens gescannt, gefiltert/gewichtet und zu einem Audio-Briefing verarbeitet — im Kern dieselbe Zwei-Phasen-Logik wie in der Ausschreibung gefordert.

**Kernfunktionen:**
- Ø 15 Minuten/Folge, „Deep Dives" zu Hauptthemen + „Quickfire-Runde" für kurze News
- 6 wählbare Stile: Casual Talk, Business Briefing, Deep Dive, Comedy, Satire, News Anchor
- Zwei-Stimmen-Dialog per TTS, laut FAQ bewusst als „klingt nicht wie KI" beworben
- Personalisierung, die „mit dir mitlernt" (nur in bezahlten Stufen: 19€/Monat wöchentlich personalisiert, 49€/Monat täglich personalisiert)
- Kostenlose Stufe „Espresso": 1 fester Stil (Casual Talk), keine Personalisierung, nur Deutsch

**Was wir übernehmen:** Die Grundstruktur „viele Quellen → filtern/gewichten → TTS"; den Mix aus 1–2 vertieften Themen plus einer kürzeren Nachrichtenrunde als Manuskript-Formmuster; klare Datierung jeder Folge.

**Warum nicht 1:1 als Vorbild:** Kein nach außen sichtbares Themen-Gedächtnis (genau der im Handbuch benannte Schwachpunkt), keine öffentlich nachvollziehbaren Quellenlinks in der kostenlosen Stufe, nicht redaktionell auf „was bedeutet das für ein deutsches Unternehmen" zugeschnitten, sondern auf Nutzer-Personalisierung statt auf eine gemeinsame Redaktionslinie ausgelegt.

### 2.2 Weiterer Marktüberblick (kurz)

Eine grobe Websuche zu vergleichbaren täglichen KI-News-Podcasts (u. a. Techpresso, Handelsblatt KI-Briefing) bestätigt vor allem eines: Ein tägliches automatisiertes Nachrichtenformat im 10–15-Minuten-Bereich ist ein etablierter, aber anspruchsvoll durchzuhaltender Standard — das Handelsblatt-Format wurde laut Suchtreffern zwischenzeitlich sogar eingestellt. Das war eine bewusst knappe Prüfung (keine tiefe Funktionsanalyse dieser Formate, da podpresso.ai der einzige Wettbewerber ist, an dem wir gemessen werden) — sie bestätigt nur, dass unser Format-Ansatz (Länge, Tageskadenz) marktüblich ist.

### 2.3 Fazit der Analyse

| Muster | podpresso.ai | Ausschreibungsvorgabe | → Für unser Projekt |
|---|---|---|---|
| Viele Quellen bündeln & gewichten | ✅ | ✅ (Takt 1) | Übernehmen |
| Kontinuität/Gedächtnis sichtbar machen | ❌ nicht erkennbar | ✅ Pflicht (Kriterium 2+3) | **Unser Differenzierungsmerkmal** |
| Quellen transparent & aufrufbar | ❌ nicht öffentlich sichtbar | ✅ Pflicht (Kriterium 4+5) | **Unser Differenzierungsmerkmal** |
| Deep-Dive + Quickfire-Mix im Manuskript | ✅ | offen, Team entscheidet | Als Formmuster übernehmen |
| Personalisierung pro Hörer | ✅ (nur bezahlt) | nicht gefordert | Bewusst nicht dabei (Anti-Scope) |
| Kostentransparenz/Modellwahl-Nachweis | ❌ nicht kommuniziert | ✅ Pflicht (Kriterium 6) | **Unser Differenzierungsmerkmal** |

Unser Ansatz übernimmt die bewährten Format-Bausteine von podpresso (Quellenbreite, Deep-Dive+Quickfire-Mix, natürlicher Zwei-Stimmen-Dialog), unterscheidet sich aber gezielt genau an den Stellen, die das Handbuch als Schwäche des Vorbilds benennt: Gedächtnis, sichtbare Quellen, Kostentransparenz.

---

## 3. Anforderungskatalog (Pflicht/Kür, nach Modulen)

*Pflicht = ohne das ist es keine Erfüllung der Abnahmekriterien. Kür = sinnvoll, aber nur wenn nach der Pflicht noch Zeit bleibt. Spalte „Agent/Code" zeigt die in der Ausschreibung geforderte bewusste Trennung.*

### Modul A — Quellen & Aufbereitung (Takt 1)

| # | Funktion | Priorität | Agent/Code |
|---|---|---|---|
| A1 | Anbindung an mind. 2 unabhängige Quellentypen | Pflicht | Code (Anbindung) |
| A2 | Themen-Dedupe: LLM-Vergleich Titel+Kurzfassung gegen offene/gelaufene Themen der letzten 14 Tage, mit Schwellwert-Regel für „gleiches Thema" | Pflicht | Agent (inhaltlicher Vergleich) |
| A3 | Cross-Referenzierung bei aufnahmewürdigen Themen („stimmt das überhaupt") | Pflicht | Agent |
| A4 | Fortsetzungserkennung mit explizitem „was ist neu dazugekommen" | Pflicht | Agent |
| A5 | DB-Schema: Thema, Quelle(n)-URL, Datum, Status, Vorgänger-Referenz | Pflicht | Code |
| A6 | Zusätzliche Quellen (Newsletter, Anbieter-Changelogs, Foren) | Kür | Code (Anbindung) |
| A7 | Fester Redaktionsschluss für Takt 1 vor dem Morgenlauf (Vorschlag: 23:00 Uhr Vorabend) — sonst startet Takt 2 mit undefiniertem Datenstand | Pflicht | Code |

### Modul B — Auswahl & Manuskript (Takt 2, Kernstück)

| # | Funktion | Priorität | Agent/Code |
|---|---|---|---|
| B1 | Auswahlregeln dokumentiert (Rubrik unten), mind. 4 Themen/Folge | Pflicht | Agent (Bewertung) + Code (Filter) |
| B2 | Manuskript im festgelegten Ton: **Zwei-Stimmen-Dialog**, ~1.400–1.600 Wörter | Pflicht | Agent |
| B3 | Fortsetzungsthemen knüpfen am letzten Stand an, statt neu zu erzählen | Pflicht | Agent |
| B4 | Montag-Sonderformat: Wochenend-Rückblick | Pflicht | Agent (eigener Prompt) |
| B5 | Freitag-Sonderformat: Wochenüberblick mit Linie statt Wiederholung | Pflicht | Agent (eigener Prompt) |
| B6 | Grounding-/Faktencheck-Gate: zweites Modell prüft Zahlen/Namen gegen Quellen | Pflicht | Agent |
| B7 | Definiertes Verhalten bei Faktencheck-Fehlschlag (Retry-Grenze, dann Abbruch statt Senden) | Pflicht | Code (Regel) + Agent (Retry) |
| B8 | Manuskript-Ablage, versioniert/abrufbar | Pflicht | Code |
| B9 | A/B-testbare Prompt-Varianten für den Ton | Kür | Code |

**Auswahl-Rubrik (Vorschlag zu B1 — vom Team zu bestätigen/anzupassen, das ist eure Entscheidung, nicht meine):**

| Kriterium | Gewicht | Leitfrage |
|---|---|---|
| Mittelstands-/KI-Manager-Relevanz | hoch ×3 | Was bedeutet das konkret für ein deutsches Unternehmen? |
| Neuheitswert | hoch ×3 | Komplett neu, echte Fortsetzung mit neuem Fakt, oder reine Wiederholung (→ 0 Punkte, fällt raus)? |
| Quellen-Breite | mittel ×2 | Wie viele unabhängige Quellen bestätigen das? |
| Aktualität | mittel ×2 | Wie frisch ist die Meldung? |
| Handlungs-/Tool-Bezug | niedrig ×1 | Betrifft es Tools/Entscheidungen, die Hörer wirklich nutzen? |

Score 0–10 je Kriterium × Gewicht, Summe je Thema, Top 4–6 je nach Zeitbudget. Deckelung: max. 2 reine Ankündigungs-Themen pro Folge, um Hype-Lastigkeit zu vermeiden — siehe Redaktions-Grundsatz.

**Redaktions-Grundsatz (inhaltlich, nicht technisch):** Hype-Skepsis statt PR-Übernahme. Jede Ankündigung wird im Manuskript um „was heißt das konkret" ergänzt, statt sie unkommentiert weiterzureichen — feste Prompt-Instruktion in B2. Das ist der eigentliche inhaltliche Unterschied zu podpressos Breite-statt-Tiefe-Ansatz (Kap. 2), nicht nur ein technisches Merkmal.

### Modul C — Produktion & Zustellung

| # | Funktion | Priorität | Agent/Code |
|---|---|---|---|
| C1 | TTS-Produktion mit zwei unterschiedlichen Stimmen | Pflicht | Code (Anbindung) |
| C2 | Audiodatei-Ablage mit Datum/Metadaten, öffentlich unter stabiler URL erreichbar | Pflicht | Code |
| C3 | Minimale Zustellung: RSS-Feed oder einfache Tages-/Archiv-Übersicht mit Links auf aktuelle + vergangene Folgen inkl. Quellen | Pflicht | Code |
| C4 | Rückwärts-Zeitplan bis 8:00 Uhr inkl. Fallback bei Verzug | Pflicht | Code |
| C5 | Ausgebaute Web-Oberfläche (eigener Player, Design, Suche/Filter) | Kür | Code |

### Modul D — Betrieb & Nachweis (Kriterium 6 + 7)

| # | Funktion | Priorität | Agent/Code |
|---|---|---|---|
| D1 | Kosten-/Tokenlogging pro Lauf (Modell, Tokens, Kosten in €) | Pflicht | Code |
| D2 | Modellwahl je Teilaufgabe bewusst dokumentiert (nicht überall das teuerste Modell) | Pflicht | Code (Konfiguration) |
| D3 | Geplanter täglicher Trigger, spätestens ab Dienstag 25.08. produktiv | Pflicht | Code |
| D4 | Backfill-Funktion: manuell ausgelöst bei (a) Lauf-Ausfall oder (b) gezielt für die Mittwoch-Vorführung; Kosten-Hinweis: jeder Backfill-Tag verursacht denselben Aufwand wie ein regulärer Takt-2-Lauf (fließt in D1 mit ein) | Pflicht | Code |
| D5 | Monitoring/Alarmierung bei Lauf-Fehlschlag | Kür | Code |
| D6 | Kosten-Dashboard über mehrere Tage | Kür | Code |
| D7 | Wiederholungs-Metrik über die letzten 7 Folgen (einfacher Titel-/Themen-Overlap-Wert) als leichtgewichtiger Nachweis für Kriterium 2/3 | Pflicht | Code |

**Fehler-Matrix (global, nicht nur fürs Faktencheck-Gate):**

| Komponente/Fehlerfall | Verhalten |
|---|---|
| Einzelne Quelle nicht erreichbar (Takt 1) | Lauf überspringt diese Quelle, loggt Warnung, läuft mit den übrigen weiter — unkritisch, da Takt 1 nicht zeitkritisch ist |
| TTS-API-Fehler | 1× Retry mit Backoff, danach Fallback-Anbieter falls eingerichtet, sonst Abbruch des Laufs |
| Datenbank nicht erreichbar/korrupt | Takt 2 bricht sofort ab (kein Senden ohne Gedächtnis) — Vortagesfolge bleibt online, manuelle Prüfung nötig |
| Faktencheck-Gate schlägt fehl | siehe B6/B7 — Retry-Grenze, danach kein Versand |
| Lauf insgesamt nicht fertig bis 7:50 Uhr | Not-Aus: Vortagesfolge bleibt online statt einer halbfertigen Folge; verspätete Nachlieferung optional, sobald fertig |

### Modul E — Recht & Quellenintegrität

| # | Funktion | Priorität | Agent/Code |
|---|---|---|---|
| E1 | Keine Volltext-Übernahme urheberrechtlich geschützter Artikeltexte — nur Zusammenfassung mit Quellenlink | Pflicht | Agent (Formulierung) |
| E2 | Sorgfalt bei Namensnennung realer Personen (Zahlen/Zitate nur mit Quellenbeleg, siehe B6) | Pflicht | Agent |
| E3 | API-Keys/Secrets nicht im Repository (auch bei privatem Repo) | Pflicht | Code |
| E4 | Kurzer Hinweis, falls ein genutzter Anbieter außerhalb der EU verarbeitet (Datenfluss-Transparenz) | Kür | Doku |

**Bewusst nicht dabei (Anti-Scope):** Keine Personalisierung pro einzelnem Hörer (kein Profil-/Login-System wie podpressos Cappuccino/Doppio) · keine Mehrsprachigkeit · kein Live-Recherche-Agent innerhalb des Morgenlaufs · keine mobile App · keine Kommentar-/Community-Funktion auf der optionalen Web-Seite.

---

## 4. Technik-/Lösungsoptionen & Entscheidung

| | Option A: Schlank & kostenlos | Option B: Qualität priorisiert | Option C: Web-Recherche-Agent |
|---|---|---|---|
| Beschreibung | RSS-first + Exa nur als Ergänzung; ausschließlich EUrouter-Modelle; Azure/OpenAI TTS wegen Freetier; GitHub Actions als Scheduler | Exa als Hauptquelle statt fester RSS-Liste; stärkstes verfügbares Modell für Manuskript + Faktencheck (über eigene Keys); ElevenLabs für Stimmqualität | Ein LLM-Agent mit freiem Web-Zugriff sucht selbst statt fester Quellenliste |
| Passung zu Kap. 3 | Erfüllt Pflicht, aber Themenbreite/-tiefe (A2–A4) hängt stark an Feed-Qualität | Beste Passung — mehr Tiefe für Cross-Check (A3) und höhere Manuskript-Qualität (B2) | Findet ggf. „was andere nicht kennen", aber schwer kontrollierbar (A2–A5) |
| Aufwand bis nutzbar | Niedrig | Mittel | Hoch (Agent-Verhalten ist schwerer vorhersehbar in 2 Tagen) |
| Laufende Kosten | Sehr niedrig (Freetier-first) | Niedrig–mittel, gezielt nur wo Qualität zählt | Am höchsten (jeder Suchschritt ist ein Agent-Aufruf) |
| Datenschutz/Recht | EUrouter = EU-Datenresidenz durchgängig | Mischung EU (EUrouter) + ggf. Nicht-EU-Anbieter, siehe E4 | Abhängig vom Such-Backend des Agents, am wenigsten kontrollierbar |
| Lerneffekt/Eigentum | Hoch (alles selbst zusammengesetzt) | Hoch | Mittel (Agent-Verhalten ist eine Black Box) |
| Risiko | Themenabdeckung evtl. zu schmal für „alle KI-Manager-relevanten Themen" | Geringstes Risiko für die 7 Abnahmekriterien | Zeit- und Kostenrisiko in einem 2-Tage-Sprint am höchsten |

**Entscheidung:** ✅ Empfehlung: **Hybrid aus Option B als Grundrichtung, mit gezielten A-Elementen** — Begründung: Kriterium 6 verlangt ausdrücklich, dass *nicht* überall das teuerste Modell läuft. Deshalb: EUrouter mit einem günstigen Modell für die hochfrequenten, nicht-kreativen Takt-1-Schritte (Dedupe A2, einfache Cross-Checks A3); ein stärkeres Modell (über einen der vorhandenen eigenen Keys) ausschließlich für die zwei Schritte, an denen Qualität wirklich entscheidet — Manuskript (B2) und Faktencheck-Gate (B6). Als Quellen-Basis RSS + Exa kombiniert (Exas Freetier ist mit 20.000 Requests/Monat deutlich großzügiger als Tavilys 1.000 Credits/Monat). TTS: ElevenLabs für den Dialog-Stil, sofern Christians vorhandener Key das abdeckt — sonst Azure/OpenAI TTS als Alternative, an kurzen Ausschnitten getestet (Kontingente vorher prüfen, wie im Handbuch empfohlen). **Status: empfohlen, noch nicht endgültig entschieden** — hängt an der konkreten Klärung, welche Keys Christian bereits hat (siehe Kapitel 8). Option C (freier Web-Agent) wird verworfen: zu hohes Zeit-/Kostenrisiko für einen 2-Tage-Bau, passt schlecht zu Kriterium 6.

**Budget-/Kostenrahmen:** Kein expliziter Euro-Rahmen von der FBS vorgegeben. Angenommene Leitplanke (zu bestätigen): Freetier-first, kostenpflichtige Calls gezielt nur dort, wo Kriterium 1/5 wirklich davon abhängen (Manuskript-Qualität, Faktencheck) — das ist zugleich die verlangte Kostentransparenz-Story für Mittwoch („wir haben bewusst nicht überall das teuerste Modell genommen").

---

## 5. Umsetzungsplan (Phasen)

*Angepasst an den realen Ausschreibungs-Kalender: Montag = Tag 1, Dienstag = Tag 2 (muss produktiv laufen), Mittwoch = Vorstellung. Kein generischer Wochenplan — die drei Tage sind fix.*

> **Leitprinzip (nach Team-Feedback): erst die dünnste Kette komplett, dann anreichern.** Dedupe, Cross-Check und Exa sind unbegrenzt verbesserbar und können den ganzen Sprint verschlingen. Deshalb steht eine radikal einfache End-to-End-Kette als Meilenstein 1, *bevor* irgendetwas daran verfeinert wird. Worst Case ab diesem Meilenstein: „einfacher Podcast, aber er läuft" statt „perfekte Pipeline, keine Folge". Zeitbudgets unten sind Platzhalter — an eure tatsächliche Verfügbarkeit anpassen.

**Phase 0 — Entscheiden & Recherche abschließen** *(Mo 24.08., jetzt · Budget: bis Mittag)*
Dieses Dokument, Freigabe durch Christian, Teampartner finden, GitHub-Repo anlegen und teilen, konkrete API-Keys bestätigen. → *Ergebnis:* freigegebene Strategie-Übersicht, startklares Repo.
*Entscheidung nötig:* Freigabe dieses Dokuments — ohne dieses Go beginnt laut Auftrag kein Bau.

**Phase 1 — Thinnest Slice: die komplette Kette, roh** *(Mo nachmittags · Budget: bis 18:00 Uhr, harte Abbruchregel: läuft es dann nicht komplett durch, wird weiter vereinfacht statt neue Features zu ergänzen)*
2–3 RSS-Feeds (noch kein Exa, noch kein Scoring) → regelbasierte Platzhalter-Auswahl (z. B. „neueste 4–6 Einträge") → Manuskript-Rohversion → TTS → MP3-Ablage. Bewusst noch ohne Dedupe, Cross-Check, Faktencheck-Gate. → *Ergebnis:* eine hörbare, inhaltlich noch grobe Roh-Folge existiert als Datei.

**Phase 2 — Qualitäts-Kern nachrüsten** *(Mo abend – Di früh · Budget: bis Di 10:00 Uhr)*
Auf der laufenden Kette aufbauen: Dedupe (A2), Cross-Check (A3), Fortsetzungserkennung (A4), Redaktionsschluss (A7), Auswahl-Rubrik (Kap. 3) statt Platzhalter-Regel, Faktencheck-Gate (B6/B7), zweite Quellart Exa ergänzen. → *Ergebnis:* Manuskript-Qualität und Quellenbindung erfüllen Kriterium 1/2/3/5 inhaltlich.
*Entscheidung nötig:* Manuskript-Ton nach dem ersten Hörtest bestätigen oder nachschärfen — laut Ausschreibung eine Team-, keine Claude-Code-Entscheidung.

**Phase 3 — Sonderformate, Fehler-Matrix, Zustellung** *(Di vormittags · Budget: bis 16:00 Uhr, sonst Sonderformate auf Minimalversion vereinfachen)*
Montag-/Freitag-Sonderformate fertigstellen, Fehler-Matrix (Kap. 3) umsetzen, minimale Zustellung (C3: RSS/Index) live schalten, Kostenlogging (D1/D2/D7), Backfill (D4). → *Ergebnis:* System erfüllt alle 7 Abnahmekriterien inhaltlich und ist öffentlich erreichbar.

**Phase 4 — Automatisierung & erster Produktivlauf** *(spätestens Di abend · Budget: bis 20:00 Uhr)*
Scheduler produktiv. **UTC-Falle:** GitHub-Actions-Cron läuft in UTC — im August (Sommerzeit/MESZ, UTC+2) entspricht 8:00 Uhr lokal 06:00 UTC. Empfehlung: Lauf-Start bereits 05:30–06:00 Uhr lokal (≈ 03:30–04:00 UTC) ansetzen, das lässt gut zwei Stunden Puffer für Retries vor der 8-Uhr-Deadline. Für den Dauerbetrieb über den Sprint hinaus: Ende Oktober wechselt Deutschland auf Winterzeit (MEZ, UTC+1) — dann entspricht 8:00 Uhr lokal 07:00 UTC, der Cron-Wert müsste nachgezogen werden. Fallback bei Verzug: siehe Fehler-Matrix (Vortagesfolge bleibt online). → *Ergebnis:* mindestens ein echter automatischer Lauf ohne manuellen Eingriff, für Dienstag oder rückwirkend per Backfill erzeugt.

**Phase 5 — Zweiter Tag, Politur & Vorstellung** *(Mi früh, vor der Präsentation)*
Zweiten Podcast (anderer Tag) sicherstellen, beide Folgen nebeneinander hören (macht Kriterium 2+3 hörbar), Pitch vorbereiten (Aufbau, technische Entscheidungen, auch verworfene Wege), optionale ausgebaute Web-UI (C5) falls Zeit übrig. → *Ergebnis:* zwei Podcasts von zwei verschiedenen Tagen + Manuskripte + Kostenzahlen + Pitch bereit.

---

## 6. Entscheidungs- & Recherche-Log *(lebendes Dokument — hier laufend ergänzen)*

| # | Frage/Entscheidung | Warum entscheidend | Status | Antwort/Entscheidung (Datum) | Konsequenz für die Vorlage |
|---|---|---|---|---|---|
| 1 | Format/Ton des Podcasts | Bestimmt Manuskript-Prompt-Architektur & TTS-Wahl | ✅ Erledigt | Zwei-Stimmen-Dialog, 24.08.2026 | Kap. 3 (B2), Kap. 4 (TTS) |
| 2 | podpresso.ai-Wettbewerbsanalyse | Differenzierungs-Basis | ✅ Erledigt | Öffentliche Startseite ausgewertet, App-Login-Bereich bewusst nicht betreten, 24.08.2026 | Kap. 2 |
| 3 | EUrouter-Fähigkeiten (Kosten-Tracking, Modellwahl, keine Websuche) | Grundlage für Kap. 4 + Kriterium 6 | ✅ Erledigt | Öffentliche Produktinfo recherchiert, 24.08.2026 | Kap. 4 |
| 4 | Team-Partner & GitHub-Repo | Ohne Repo kein gemeinsamer Bau-Start | 🔲 Offen | | Blockiert Phase 0/1 |
| 5 | Welche konkreten API-Keys bereits vorhanden | Bestimmt Feinwahl in Kap. 4 | 🔲 Offen | Christian: „eigene Keys vorhanden", Details ausstehend | Kap. 4 Feinwahl |
| 6 | Quellen-Strategie im Detail (welche RSS-Feeds konkret, Exa vs. Tavily final) | Kernstück Takt 1 | 🔲 Offen | Empfehlung in Kap. 4 vorgeschlagen | Kap. 3 Modul A |
| 7 | Budget-/Kostenrahmen für den Sprint | Steuert Anbieterwahl | 🔲 Offen | Kein expliziter Rahmen genannt, Annahme: Freetier-first | Kap. 4 |
| 8 | Scheduler-Technologie (GitHub Actions vs. eigener Rechner/Server) | Zuverlässigkeit der 8-Uhr-Deadline | 🔲 Offen | UTC/Zeitzonen-Falle geklärt (Kap. 5 Phase 4), Grundsatzwahl Actions vs. eigener Server weiter offen | Kap. 5 Phase 4 |
| 9 | Zustellung: minimale Web-Präsenz Pflicht oder Kür? | Ohne Zustellmechanismus ist der Podcast nicht „live"-fähig | ✅ Erledigt | Team-Feedback 24.08.2026: minimale Zustellung (C3) auf Pflicht hochgestuft, ausgebaute UI (C5) bleibt Kür | Kap. 1, Kap. 3 Modul C |
| 10 | Auswahl-Rubrik (konkrete Gewichtungskriterien) | Ohne Rubrik entscheidet das Modell jedes Mal anders | ✅ Vorschlag erstellt | 5-Kriterien-Rubrik vorgeschlagen 24.08.2026, Team-Bestätigung/Anpassung noch offen | Kap. 3 Modul B |
| 11 | Dedupe-Methode konkretisiert | A2 war Black Box | ✅ Erledigt | LLM-Vergleich gegen 14-Tage-Fenster + Wiederholungs-Metrik (D7), 24.08.2026 | Kap. 3 Modul A + D |
| 12 | Fehler-Matrix je Komponente | Retry gab es nur beim Faktencheck-Gate | ✅ Erledigt | Globale Fehler-Matrix ergänzt, 24.08.2026 | Kap. 3 Modul D |
| 13 | UTC-Falle bei GitHub Actions | 8 Uhr lokal ≠ 8 Uhr UTC, Sommer-/Winterzeit unterschiedlich | ✅ Erledigt | August = MESZ = UTC+2, Start-Empfehlung 05:30–06:00 Uhr lokal mit Puffer, 24.08.2026 | Kap. 5 Phase 4 |
| 14 | Letzter Sammellauf vor dem Morgenlauf | Takt 1 „läuft beliebig oft" war ohne Cutoff undefiniert | ✅ Erledigt | Fester Redaktionsschluss 23:00 Uhr Vorabend (A7), 24.08.2026 | Kap. 3 Modul A |
| 15 | Solo-Fallback-Pfad falls kein Teampartner gefunden wird | Dokument hing komplett an der offenen Team-Frage | ✅ Erledigt | Scope-Reduktionspfad in Kap. 7 ergänzt, 24.08.2026 — Zulässigkeit von Solo-Teilnahme bei der FBS bleibt offen (Kap. 8, Frage 6) | Kap. 7 |
| 16 | Backfill-Trigger & Kosten | War nicht definiert, wann/was er kostet | ✅ Erledigt | Manuell bei Ausfall oder gezielt für Mittwoch, kostet wie ein regulärer Lauf (D4), 24.08.2026 | Kap. 3 Modul D |
| 17 | Reihenfolge des Bauens: alles parallel oder Kette zuerst? | Dedupe/Cross-Check/Exa sind unbegrenzt verbesserbar, Risiko: Sprint verschlungen ohne lauffähige Folge | ✅ Erledigt | „Thinnest Slice" als Meilenstein 1 vor jeder Anreicherung, 24.08.2026 | Kap. 5 |

---

## 7. Risiken & Guardrails

| Risiko | Mitigation |
|---|---|
| Beide Takte werden doch in einem Morgenlauf vermischt → Zeitüberschreitung vor 8 Uhr | Strikte Trennung von Anfang an: Takt 2 greift ausschließlich auf die Datenbank zu, keine Live-Recherche im Morgenlauf |
| System läuft erstmals erst Mittwochfrüh → nur 1 statt 2 Podcasts vorführbar (Kriterium 7 verfehlt) | Harte interne Deadline „spätestens Dienstag produktiv" (Phase 4) + Backfill-Funktion als Sicherheitsnetz |
| Faktencheck/Quellenbindung lückenhaft → Kriterium 5 verfehlt | Grounding-Gate ist Pflichtbaustein (B6/B7); bei Fehlschlag wird nicht gesendet, statt „irgendwie" auszuliefern |
| TTS-/Search-Kontingente während der Testphase aufgebraucht | An kurzen Ausschnitten testen statt volle 10-Minuten-Läufe (Handbuch-Empfehlung), Kontingente vorher prüfen, Alternativ-Anbieter vorher kennen |
| Ohne Teampartner bleibt Arbeitslast/Perspektive einseitig, Ausschreibung verlangt aber Zweierteam + Redepflicht über jede Entscheidung | Teampartner-Suche priorisieren (Phase 0); dieses Dokument als gemeinsame Gesprächsgrundlage nutzen, sobald Partner an Bord ist. **Solo-Fallback, falls bis Phase 1 niemand gefunden ist:** zuerst bei der FBS klären, ob Solo-Teilnahme überhaupt zulässig ist oder ob der Kurs einen Partner vermittelt (Kap. 8, Frage 6). Scope-Reduktion für den Alleinbau-Fall: Modul A6/B9/C5/D5/D6 (alle Kür-Punkte) sofort streichen, Thinnest-Slice-Meilenstein (Kap. 5 Phase 1) noch strikter einhalten, Sonderformate (B4/B5) im Zweifel auf eine vereinfachte Version reduzieren statt sie ganz zu verfehlen |
| Prompts werden einmal geschrieben und nicht mehr angehört/iteriert → klingt „wie alle anderen" (explizite Handbuch-Warnung) | Feste Team-Regel: jede Prompt-Änderung wird laut vorgelesen getestet, bevor sie übernommen wird |
| Datenfluss bei Nicht-EU-Anbietern (z. B. bestimmte Search-/TTS-Anbieter) unklar dokumentiert | Kurze Datenfluss-Notiz führen (Modul E4); bei rein öffentlichen KI-News laut Handbuch unkritisch, aber dokumentieren |

---

## 8. Offene Fragen an Christian

| # | Frage | Antwort (wird nachgetragen) |
|---|---|---|
| 1 | Wer wird Teampartner, bis wann steht das gemeinsame GitHub-Repo? | |
| 2 | Welche konkreten API-Keys/Accounts sind bereits vorhanden (Anthropic direkt? OpenAI? ElevenLabs? Tavily? Exa? Google/Gemini? sonstige)? | |
| 3 | Gibt es einen harten Kostenrahmen für den Sprint, oder ist „so günstig wie bei gleicher Qualität möglich" (Kriterium 6) die einzige Leitplanke? | |
| 4 | Soll die ausgebaute Web-Oberfläche (C5, eigener Player/Design/Suche) versucht werden, oder bewusst zugunsten von mehr Zeit für Kernpipeline/Qualitätssicherung weggelassen werden? Die minimale Zustellung (C3) ist inzwischen Pflicht, hier geht es nur um die Komfort-Variante. | |
| 5 | Wo/wie soll der tägliche Morgenlauf technisch ausgelöst werden — GitHub Actions (kostenlos, UTC-Umrechnung siehe Kap. 5 Phase 4) oder ein eigener Rechner/Server, der zuverlässiger zur Zielzeit startet? | |
| 6 | Ist Solo-Teilnahme laut FBS-Kursregeln überhaupt zulässig, falls kein Teampartner gefunden wird, oder vermittelt der Kurs in dem Fall einen Partner? | |

---

*Quellen: Recherche-Chat vom 24.08.2026 · `podcast_Handbuch.pdf` (FBS Future Education UG) · öffentliche Startseite podpresso.ai (App-Bereich login-pflichtig, nicht eingesehen) · Web-Recherche zu EUrouter, Tavily, Exa, ElevenLabs, Azure TTS, OpenAI TTS (siehe Kapitel 6, Belege in der Chat-Historie)*
