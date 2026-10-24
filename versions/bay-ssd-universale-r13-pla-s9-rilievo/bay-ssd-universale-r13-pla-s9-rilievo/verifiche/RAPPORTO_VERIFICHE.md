# Verifiche R13 PLA BASIC

**Pronto per la stampa del prototipo nominale. Controlli digitali completati; nessuna prova fisica o termica.**

Tutte le sei parti del kit in PLA BASIC. Fuzzy Skin disattivata, nessun modificatore, nessun provino. S9 integrato nella scocca: larghezza 14 mm, rilievo 0,4 mm, margini destro 4 mm e inferiore 6 mm. Un solo materiale e colore.
Quattro STL e otto STEP singoli, nei riferimenti di assieme e stampa, riaperti. Scala millimetrica, solido unico valido, mesh chiusa, normali coerenti e volume positivo. Nessuna faccia degenere o duplicata; zero coppie rilevate nello screening delle autointersezioni, che esclude le coppie con vertici condivisi. Nessuna riparazione automatica.
Confronto dei quattro STEP con la R12: differenza simmetrica inferiore a 0,00001 mm³. Esterno, S9, feritoie, coperchio e interno R05 conservati. Cambiati i profili per il PLA; R12 conservata.
Nove combinazioni modello/slot e 27 disposizioni nominali senza collisioni statiche; estrazione verticale campionata, con coperchio rimosso e cavi scollegati. Assieme STEP valido: nove solidi, compresi tre gabarit SSD non stampabili.
Scocca base 90 × 101 × 86 mm; ingombro con S9 90 × 101,4 × 86 mm. I dischi Shield e T9 sporgono di 3 mm dal retro: con SSD inseriti la profondita nominale e 104,4 mm, prima degli spinotti esterni e dei piedini.
Aree geometriche: fondo 30.17 cm², tetto 37.91 cm², corridoi verticali conservativi con tre T9 15.19 cm². Ogni fianco: 108 feritoie orizzontali, 6.96 cm². Non sono misure di portata o potenza dissipabile.
Slicing reale con ElegooSlicer, app 1.5.3.5 / motore 2.4.2. Profili ECC2, ugello 0,4, PEI testurizzato, PLA BASIC 220/60 °C. Limite volumetrico 5 mm³/s. Due progetti nativi con geometria, impostazioni e G-code dello slicer incorporato.
Riaperti i 3MF per ID dei componenti e relativi percorsi XML: 5 e 1 oggetti stampabili, zero modificatori. Unita e trasformazioni verificate; brim da 5 mm incluso negli ingombri, esclusione macchina rispettata.
Tutti gli strati esaminati nelle tavole d’insieme; campioni critici ingranditi. Zero candidati di nuove isole esterne nello screening raster. Verificati i percorsi di entrambi i glifi S e 9, con compensazione dell’offset estrusore del profilo. Supporti disattivati; piccoli ponti su sedi piedini, feritoie e agganci controllati nelle anteprime. I segmenti Internal Bridge possono attraversare il riempimento: la loro lunghezza totale non equivale alla campata libera.
Avviso presente in entrambi i progetti: bed_temperature_too_high_than_filament (1000C001), dovuto al confronto fra piano a 60 °C e soglia software PLA a 45 °C. Soglia conservata. Preparazione indicata: sportello anteriore aperto, evitare accumulo di calore nella camera; non e un errore geometrico risolto modificando i limiti.

| Piatto | Strati | PLA stimato | Tempo stimato |
| --- | ---: | ---: | --- |
| BAY_R13_01_SCOCCA_INSERTI | 415 | 114.21 g | 6h 34m 4s |
| BAY_R13_02_COPERCHIO | 75 | 17.47 g | 1h 1m 27s |

**Kit: 131.68 g, 7 h 35 min 31 s.** Stime dello slicer con brim, senza torre o cambi colore.

Forza e durata degli incastri, stabilita, finitura, adesione e idoneita termica del PLA restano da verificare sul pezzo. Non sono state misurate temperature reali degli SSD o degli appoggi. Nessuna simulazione termica, calibrazione della bobina, prova fisica o stampa avviata. Nessun provino aggiunto, come richiesto.
