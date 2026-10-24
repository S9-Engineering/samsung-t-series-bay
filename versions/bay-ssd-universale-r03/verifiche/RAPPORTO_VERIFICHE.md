# Riscontri di consegna — R03

**Pronto per la stampa del prototipo nominale. Stampare prima il provino.**

Configurazione confermata: ELEGOO Centauri Carbon 2 Combo, ugello 0,4 mm, PEI testurizzato, ELEGOO PETG PRO.
Slicing reale: ElegooSlicer 2.4.2. Nessun avvio della stampante.

## Geometria

- Quattro STL unici riaperti: corpo unico, mesh chiusa, normali coerenti e volume positivo; nessuna faccia degenere o duplicata.
- STEP riaperti e validi. Scostamento dei box entro 0,06 mm, coerente con la tessellazione; differenza volumetrica STL/STEP sotto 0,5%.
- Screening autointersezioni: zero coppie rilevate. Coppie con vertici condivisi escluse dal metodo.
- Nove abbinamenti e 27 assegnazioni nominali verificati; estrazione e accesso utensile controllati a posizioni campionate.
- Spinotti e cavi esterni al volume dell'enclosure in tutti i nove abbinamenti; T7 a filo, Shield/T9 sporgenti 3 mm.
- Quattro piazzole del coperchio con materiale sotto la testa della vite, controllate geometricamente.
- 3MF geometrici e nativi riaperti, millimetri e trasformazioni controllati; 2/5 corpi nei due piatti.
- Passaggio verticale continuo nei quattro corridoi T9: 11.28 cm², tramite proiezione conservativa delle mesh inclusi tamponi e ferramenta. Nessuna CFD o misura termica.
- Fondo e tetto con otto coppie di feritoie a capsula 38,4 x 6,4 mm; nervature e spina centrale 3,2 mm. Bordo laterale del coperchio 5 mm. Guide, appoggi, battute e piedini hanno fondazioni piene.

## Slicing e stime

| Piatto | Strati | Filamento | Tempo |
| --- | ---: | ---: | --- |
| BAY_R03_00_PROVINO_PRIMA_DI_TUTTO | 125 | 15.55 g | 1h 5m 7s |
| BAY_R03_01_KIT_RETRO_APERTO | 415 | 135.30 g | 7h 39m 56s |

**Kit completo:** 135.30 g; 7 h 39 min 56 s.
**Provino separato:** 15.55 g; 1 h 05 min 07 s.

Le stime includono brim e impostazioni dei piatti; supporti disattivati, nessuna torre o cambio colore.
Zero avvisi di modello, zero percorsi fuori piano o nella zona esclusa e zero candidati di nuove isole esterne dallo screening raster.
Rassegna di tutti gli strati e approfondimenti delle zone critiche registrati in revisione_visiva.json.
Le etichette Internal Bridge possono attraversare l'infill: la lunghezza totale del segmento non equivale a una campata in aria.

## Limiti rimasti

Prototipo non stampato. Dimensioni SSD nominali; 50 mm rigidi e cavo 5 mm sono indicazioni approssimative dell'utente. Porte e sezioni degli spinotti non rilevate.
Provare sede, silicone, viti e stabilita con i cavi esterni. Nessuna garanzia termica, di resistenza, precisione, stabilita o assenza di throttling ricavata dal CAD.
Le temperature vanno confrontate con e senza bay; prima provino, poi prova del kit, con priorita al disco centrale.
