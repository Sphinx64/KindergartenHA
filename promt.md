# **🎭 Theater-Script: Malwida und die Farben**

Dieses Dokument enthält die vollständige Dramaturgie und die technischen Licht-Anweisungen für das Stück.

## **📋 Das Regie-Script**

| Szene / Licht | Personen | Requisiten / Handlung | Gefühl | Bewegung | Musik / Rap | Licht-Notiz / Dauer |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **LANGEWEILE** | Malwida, Olivia | iPad: Schloss gezeichnet | Langeweile | Langsam | Slow River | 1'20 \- Neutralweiß |
| **BLAU** | Malwida | Ame **schreibt** BLAU auf 1 Paket | Panikvögel, leicht, unbeschwert, lustig | Weich, wie im Traum / Wasser | 1\. Slow River, 2\. Rap, 3\. Slow River | 1' / 1' / 1' \- Blau (v. links n. rechts) |
| **ROT** | Ame | Ame **schreibt** ROT auf 1 Paket | Ungeduldig, wütend, aggressiv | Wild, rüttelnd, klauend | 1\. Rap, 2\. Black Betty | '33 / 1'07 \- Rot (plötzlich v. rechts) |
| **GELB** | Malwida | iPad: **schreibt** GELB | Fröhlich, frech, warm, strahlend | Quirlig, spritzig, schnell | 1\. Earlsten, 2\. Rap, 3\. Tango | 30 / 1' / 1' \- Gold-Gelb (stabil) |
| **STREIT** | Ame, Malwida | iPad: **schreibt** STREIT | Chaos, Streit | Schnell, heftig, wild, hastig | Raps Mix (durcheinander) | 30 \- Blitze (Phasen 1-4) |
| **GRAU** | Ame | Ame geht weg, Malwida **verdreckt** | Still, leer, depressiv, schwer | Hängende Schultern, Schlamm-Gang | Never take off the mask | 1'09 \- Kaltes Grau (Lilastich) |
| **STILLE** | Malwida | Erschöpft, sinkt zu Boden | \- | \- | \- | 1'25 \- Gedimmt |
| **TRÄNEN** | Malwida | Malwida weint am Boden | Traurig, erschöpft | Am Boden liegend | Mund-Geräusche | 1'30 \- **Sequenz:** Blau \-\> Rot \-\> Gelb |
| **FARBEN ERWACHEN** | Malwida | "Wand beginnt sich zu bewegen" | Frisch, leicht, froh | Köpfe/Arme heben, weich | Mothership | 2'05 \- **Chaos:** Komplett zufällig |
| **ALLE WINDE** | Malwida | Berührt Kinder, Tanztücher | Magisch, neugierig | Kinder stehen nacheinander auf | 7\. Handpan Harp | 2'30 \- 3:00 \- Sanfte Wechsel |
| **BEGEGNUNG** | Emil | iPad: gezeichnet | \- | Kinder bewegen Tücher | \- | \- |
| **PAUSE** | Alle | \- | \- | Alle sitzen am Boden | The wind that shakes the corn | 2:00 |
| **SCHLUSS** | Alle | Farben, Tücher, Bänder | Gemeinsamkeit, Freude | Alle tanzen im Kreis | The Irish Dance | 2:13 \- Finale (Regenbogen) |
| **VIDEO** | Alle | Bänder-Tücher-Tanz | \- | \- | Waka Waka | Begleitlicht |

## **🛠️ Technische Programmier-Logik**

### **Licht-Mapping (L1 \- L12)**

* **Reihe 1 (Vorne):** light.l1, light.l2, light.l3, light.l4  
* **Reihe 2 (Mitte):** light.l5, light.l6, light.l7, light.l8  
* **Reihe 3 (Hinten):** light.l9, light.l10, light.l11, light.l12

### **Spezial-Logik "Tränen & Erwachen"**

1. **Tränen (Sequenz):** Alle 12 Lampen schalten nacheinander auf Blau um, dann alle auf Rot, dann alle auf Gelb.  
2. **Erwachen (Zufall):** Jede der 12 Lampen wählt unabhängig voneinander eine völlig zufällige Farbe aus dem RGB-Spektrum.

### **Master-Helper**

* Helligkeit: input\_number.theater\_master\_brightness (10-1000)  
* Tempo: input\_number.theater\_master\_speed (beeinflusst transition und Blitz-Frequenz)