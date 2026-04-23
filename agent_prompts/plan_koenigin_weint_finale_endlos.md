# Technischer Ausführungsplan: Endless Color Fade Finale

**Skript-ID:** `koenigin_weint_finale_endlos`  
**Datum:** 2026-04-01  
**Szene:** Königin Weint – Übergang von Starkregen-Chaos zu hypnotischem Farbmorphing

---

## Ziel
Sanfter, unterbrechungsfreier Übergang aus der chaotischen Starkregen-Blitz-Phase in einen endlosen, hypnotischen Farbfade-Loop. Keine Abblende, kein Blackout.

---

## Ausführungsreihenfolge

### Phase 1 – Sequenziell (Vorbereitung)
1. **Chaos stoppen:** `script.kiga_chaos_regen_final` + `script.einzeltropfen` via `script.turn_off` beenden → keine neuen Zufallsblitze mehr.
2. **Regler zurücksetzen:** `input_number.regen_tempo` und `input_number.regen_aktuell` auf `0` setzen.

### Phase 2 – Parallel (zwei gleichzeitige Äste)

#### Branch A – Endlose Farbmorphing-Schleife (läuft bis manueller Stop)
- `repeat` mit `while: true`
- Pro Iteration: Jedes Licht (`light.l1`–`light.l5`) bekommt eine neue Zufalls-RGB-Farbe
- **Zigbee-Schutz:** 150 ms Pause zwischen jedem `light.turn_on`-Befehl (5 Lampen × 150 ms = 750 ms Spread)
- `transition: 7` Sekunden → weiches Schmelzen der Farben
- `brightness_pct: 80` → Bühnengerechte Helligkeit
- `delay: 7` Sekunden am Ende der Iteration → Farben können vollständig ankommen, bevor neue gesetzt werden
- **Gesamtdauer pro Loop:** ~7,75 Sekunden

#### Branch B – Musik-Ausblende-Sequenz (20 Sekunden, einmalig)
- Startlautstärke aus `state_attr()` auslesen (`variables`-Schritt)
- `repeat count: 20` mit `media_player.volume_set` → lineare Abblende von `start_volume` auf `0.0`
- 1 Sekunde Pause zwischen jedem Schritt → 20 Sekunden Gesamtdauer
- Nach der Schleife: `media_player.media_stop`

---

## Entitäten
| Entität | Verwendung |
|---|---|
| `light.l1` – `light.l5` | Bühnenlichter |
| `script.kiga_chaos_regen_final` | Starkregen-Hauptskript (zu stoppen) |
| `script.einzeltropfen` | Einzeltropfen-Instanzen (zu stoppen) |
| `input_number.regen_tempo` | Regen-Zielgeschwindigkeit (Reset auf 0) |
| `input_number.regen_aktuell` | Regen-Ist-Geschwindigkeit (Reset auf 0) |
| `media_player.DEIN_LAUTSPRECHER` | Bühnenmusik (**Anpassen!**) |

---

## Timing-Überlegungen
- Zigbee-Mesh-Schutz durch 150 ms Versatz zwischen Lampen-Befehlen
- Transition-Zeit (7 s) = Delay-Zeit (7 s) → Farben immer synchron
- Musik-Fade (20 s) läuft parallel → Szene endet musikalisch nach 20 s, visuell erst bei manuellem Stop

---

## HA-Syntax-Konventionen
- `action:` statt `service:` (HA 2024+)
- `action:`, `target:`, `data:` auf gleicher Einrückungsebene (Projektstandard)
- `while: '{{ true }}'` für Endlosschleifen (Projektstandard)
