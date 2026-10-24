# Riscontri di consegna — R01

**Pronto per la stampa del prototipo nominale. Stampare prima il provino.**

Configurazione confermata: ELEGOO Centauri Carbon 2 Combo, ugello 0,4 mm, PEI testurizzato, ELEGOO PETG PRO.
Slicing reale: ElegooSlicer 2.4.2. Nessun avvio della stampante.

## Geometria

- Cinque STL unici riaperti: corpo unico, mesh chiusa, normali coerenti e volume positivo; nessuna faccia degenere o duplicata.
- STEP riaperti e validi. Scostamento dei box entro 0,06 mm, coerente con la tessellazione; differenza volumetrica STL/STEP sotto 0,5%.
- Screening autointersezioni: zero coppie rilevate. Coppie con vertici condivisi escluse dal metodo.
- Nove abbinamenti e 27 assegnazioni nominali verificati; estrazione e accesso utensile controllati a posizioni campionate.
- 3MF geometrici e nativi riaperti, millimetri e trasformazioni controllati; 2/5/1 corpi nei tre piatti.
- Passaggio verticale comune nei corridoi campionati: circa 15,02 cm². Nessuna CFD o misura termica.

## Slicing e stime

| Piatto | Strati | Filamento | Tempo |
| --- | ---: | ---: | --- |
| BAY_R01_00_PROVINO_PRIMA_DI_TUTTO | 125 | 15.55 g | 1h 5m 7s |
| BAY_R01_01_SCOCCA_E_TRE_SPONDE | 415 | 245.93 g | 13h 0m 46s |
| BAY_R01_02_COPERCHIO | 190 | 46.69 g | 2h 48m 28s |

**Kit completo:** 292.62 g; 15 h 49 min 14 s.
**Provino separato:** 15.55 g; 1 h 05 min 07 s.

Le stime includono brim e impostazioni dei piatti; supporti disattivati, nessuna torre o cambio colore.
Zero avvisi di modello, zero percorsi fuori piano o nella zona esclusa e zero candidati di nuove isole esterne dallo screening raster.
Rassegna di tutti gli strati e approfondimenti delle zone critiche registrati in revisione_visiva.json.
Le etichette Internal Bridge possono attraversare l'infill: la lunghezza totale del segmento non equivale a una campata in aria.

## Limiti rimasti

Prototipo non stampato. Dimensioni SSD nominali; 50 mm rigidi e cavo 5 mm sono indicazioni approssimative dell'utente. Porte e sezioni degli spinotti non rilevate.
Provare sede, silicone, viti e fermacavi reali. Nessuna garanzia termica, di resistenza, precisione, stabilita o assenza di throttling ricavata dal CAD.
Le temperature vanno confrontate con e senza bay; prima provino, poi prova del kit, con priorita al disco centrale.
