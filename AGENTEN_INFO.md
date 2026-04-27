# Onboarding: Home Assistant / Theater-Automatisierung

Kurzreferenz für neue KI-Agents, die in diesem Repository arbeiten. Ergänzt `promt.md` (Dramaturgie) und `Promt.txt` (technische Stück-Referenz).

## 1. Projektkontext

- **Zweck:** Regie- und Effektbeleuchtung für das Stück bzw. Projekt *„Malwida und die Farben“* (Kindergarten / Theater).
- **Kern:** **12 unabhängige Lampen** (Theater-Bühne, Rigging-Logik), **Timing und Synchronisation** sind die kritischsten Faktoren.
- **Weitere Medien (laut Projektrichtlinien):** Beamer, Musik (Audio-Engine), Tablet UI. Bei Aktionen, die den Beamer betreffen: Erreichbarkeit prüfen (siehe unten), nicht blind kommandieren.

## 2. Laufzeitumgebung

| Aspekt | Stand |
|--------|--------|
| Plattform | Home Assistant (u. a. auf Raspberry Pi, LAN) |
| Lampen-Integration | **Local Tuya** (lokale Ansteuerung, geringe Latenz) |
| Hardware-Lampen | 12× LEDVANCE SMART+ Wi-Fi |
| Entitäts-Schema | `light.l1` … `light.l12` (immer diese IDs verwenden) |

`README.md` im Config-Root nennt das Projekt kurz *KindergartenHA*.

## 3. Physisches Layout & Gruppen

**Raster 3×4 (vorne → hinten, links → rechts):**

- Reihe vorne (Zuschauer): L1, L2, L3, L4  
- Reihe Mitte: L5, L6, L7, L8  
- Reihe hinten (Regie): L9, L10, L11, L12  

**Gruppen** in `configuration.yaml` (für Szenen / zeilenweise Aktionen): `group.theater_al`, `theater_ml`, `theater_mr`, `theater_ar` (je 3 Lampen pro Spalte).

## 4. Wichtigste Dateien (Config-Root `config/`)

| Datei / Ordner | Inhalt |
|----------------|--------|
| `configuration.yaml` | Einstieg: `default_config`, Logger, Inkludierungen, `group`, `input_*` Theater-Helper, `shell_command` (optional ADB/Beamer-Keyevents), `lovelace` Dashboard *Alle Skripte* |
| `scripts.yaml` | **Hauptlogik** der Theater-Skripte; viele Aliase `script.alt_*` (u. a. v2-Varianten) |
| `automations.yaml` | Automationen (kann leer oder minimal sein) |
| `scenes.yaml` | Szenen (derzeit ggf. leer) |
| `dashboards/alle_skripte.yaml` | Lovelace-Dashboard „Alle Skripte“ – schneller Überblick startbarer `script.alt_*` |
| `agent_prompts/` | **Technische Ausführungspläne** neuer, timing-relevanter Abläufe (siehe Workflow) |
| `.cursorrules` | Rollen- und Arbeitsregeln speziell für dieses Theater-Repository |

## 5. Zentrale Helper (Auszug)

- **`input_number.theater_master_brightness`:** Helligkeit; Skalierung in v2-Logik typischerweise **Wert/10** für `brightness_pct` (oberes Limit beachten).
- **`input_number.theater_master_speed`:** Tempo (Übergänge, Blitze) – in Skripten **dynamisch** einbinden, nicht hart auf einen festen Wert pinnen.
- **`input_number.theater_streit_phase`:** Phasen für die Streit-Sequenz.
- **`input_text.theater_farbe_*`:** RGB-Strings wie `R,G,B` für Farben (neutral, blau, rot, gelb, grau, giftgelb, …).
- Weitere interne Helfer (Streit, Tränen, Regen, Finale, …) siehe `configuration.yaml` – vor Änderungen prüfen, was bereits von Skripten gelesen wird.

## 6. Konventionen in den Skripten

- Viele **alias-Namen** beginnen mit `Theater:` oder hängen an **`alt_`**-Präfixen; Dashboard verweist explizit auf `script.alt_*`.
- **Stop / Blackout:** es gibt u. a. `script.alt_theater_master_stop_v2`, `script.alt_theater_blackout_v2` u. ä. – laufende Loops beenden, nicht nur Helligkeit 0, wenn sequenzielle oder Wiederholungs-Logik aktiv ist.
- **Mesh / WLAN schonen:** viele Abläufe nutzen **Verzögerungen** (z. B. 150–500 ms) zwischen Befehlen; bei neuen Abläufen abwägen: **parallel** vs. **leicht versetzt**, um Tuya/WiFi nicht zu fluten.
- **Lovelace:** Buttons sollen laut Projekt-Regel eher `tap_action: perform-action` + direktes Skript nutzen, keine unnötigen Pop-ups.

## 7. Workflow für neue Theater-Sequenzen (verbindlich laut `.cursorrules`)

1. **Zuerst** einen **technischen Ausführungsplan** in **`agent_prompts/`** ablegen (Markdown), analog zu vorhandenen Plänen (Ziel, Phasen, Entitäten, Timing, Zigbee/Parallelität).
2. Dann implementieren (Skripte, ggf. Dashboard).
3. Bei timing-kritischem, komplexen Timing die Projektnotiz: **konsistente logische Abläufe** (Projekt nennt u. a. Claude 3.5 Sonnet – als Orientierung, nicht als Zwang im Editor).

Zusätzliche **Meta-Checkliste** (aus Projektrichtlinien):

- Sollen Lichtbefehle **parallel** gehen oder **sequenziell mit kleinen Offsets** (Mesh-Überlastung vermeiden)?
- Kurze **Szenen-Parameter:** `brightness_pct` und `transition` pro Szene klar setzen.
- **Beamer / „Film starten“:** vor sensiblen Befehlen **Erreichbarkeit** prüfen (Ping/Binary Sensor o. ä.), sofern im System vorhanden.

## 8. Optionale Beamer-Steuerung

In `configuration.yaml` sind **optional** `shell_command`-Einträge für **ADB-Keyevents** hinterlegt (z. B. `beamer_keyevent_2099`). Die sind nur sinnvoll, wenn ADB am HA-Host funktioniert und der Projektor erreichbar ist. Nicht voraussetzen, dass das in jeder Installation aktiv ist.

## 9. Sprache & Doku-Set

- Nutzer bevorzugt **Deutsch** in der Kommunikation.
- **Dramaturgie & Tabelle:** `promt.md`  
- **Technische Stück-Referenz (Layout, Helper, Coding-Regeln):** `Promt.txt`  
- **Agent-spezifisch (dieses Dokument):** `AGENTEN_INFO.md` / `AGENTEN_INFO.txt`  

Bei Widersprüchen zwischen alten Beispielwerten in Texten (z. B. Prozent-Angaben) und tatsächlicher `configuration.yaml` / `scripts.yaml` gewinnen **die YAML-Dateien**.

---
*Datei-Version: für neue Agents; bitte bei größeren Architekturänderungen anpassen.*
