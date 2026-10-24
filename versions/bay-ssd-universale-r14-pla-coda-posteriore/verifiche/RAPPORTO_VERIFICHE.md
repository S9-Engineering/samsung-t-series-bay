# Verifiche R14 PLA BASIC

**Pronto per la stampa del prototipo nominale. Controlli digitali completati; nessuna prova fisica o termica.**

Tutte le sei parti del kit in PLA BASIC. Fuzzy Skin disattivata, nessun modificatore, nessun provino. S9 integrato nella scocca: larghezza 14 mm, rilievo 0,4 mm, margini destro 4 mm e inferiore 6 mm. Un solo materiale e colore.
Quattro STL e otto STEP singoli, nei riferimenti di assieme e stampa, riaperti. Scala millimetrica, solido unico valido, mesh chiusa, normali coerenti e volume positivo. Nessuna faccia degenere o duplicata; zero coppie rilevate nello screening delle autointersezioni, che esclude le coppie con vertici condivisi. Nessuna riparazione automatica.
Confronto con la R13: scocca e due tipi di inserto identici, differenza simmetrica inferiore a 0,00001 mm³. Coperchio con sola aggiunta nella regione posteriore: tetto prolungato di 8 mm, pannello e due corti risvolti fino a quota 56 mm. Regione originale, feritoie e agganci conservati. R13 verificata e conservata.
Nove combinazioni modello/slot e 27 disposizioni nominali senza collisioni statiche; estrazione verticale campionata, con coperchio rimosso e cavi scollegati. Assieme STEP valido: nove solidi, compresi tre gabarit SSD non stampabili.
Scocca base profonda 101 mm, coperchio profondo 109 mm; ingombro chiuso con S9 90 × 109,4 × 86 mm. Shield e T9 terminano a Y104; parete posteriore interna a Y106: gioco assiale 2 mm. Coda in un solo pezzo con il tetto, spessore 3 mm e luce 0,3 mm dalle estremita posteriori della scocca.
Nove ingombri USB nominali senza collisioni con scocca, coperchio e inserti. Spazio riservato 20 mm di larghezza × 20 mm di altezza × 50 mm in uscita, centrato sulla faccia corta del gabarit SSD. Bordo inferiore del retro a quota 56 mm: margine sopra lo spinotto 3 mm per T9, 3,5 mm per Shield, 4,5 mm per T7. Sono ipotesi generose richieste dall’utente, non dimensioni standard certificate o misure dei suoi cavi.
Aree geometriche: fondo 30.17 cm², tetto 37.91 cm², corridoi verticali conservativi con tre T9 15.19 cm². Ogni fianco: 108 feritoie orizzontali, 6.96 cm². Non sono misure di portata o potenza dissipabile.
Apertura posteriore sotto la coda: 42.84 cm², sezione geometrica senza gli spinotti. Il passaggio inferiore, il tetto e i fianchi restano ventilati; nessuna simulazione o misura di portata.
Slicing reale con ElegooSlicer, app 1.5.3.5 / motore 2.4.2. Profili ECC2, ugello 0,4, PEI testurizzato, PLA BASIC 220/60 °C. Limite volumetrico 5 mm³/s. Un progetto nativo con sei pezzi nello stesso piatto, geometria, impostazioni e G-code dello slicer incorporato. Stampa per strato, orientamenti invariati.
Riaperto il 3MF per ID dei componenti e relativi percorsi XML: sei oggetti stampabili, zero modificatori. Unita e trasformazioni verificate; ingombro conservativo complessivo con brim 220 × 143 mm sul piano 256 × 256 mm. Brim da 5 mm separati, esclusione macchina rispettata. Coperchio con faccia esterna sul piano: la coda cresce verticalmente da esso, senza supporti.
Tutti gli strati esaminati nelle tavole d’insieme; campioni critici ingranditi. Zero candidati di nuove isole esterne nello screening raster. Verificati i percorsi di entrambi i glifi S e 9, con compensazione dell’offset estrusore del profilo. Supporti disattivati; piccoli ponti su sedi piedini, feritoie e agganci controllati nelle anteprime. I segmenti Internal Bridge possono attraversare il riempimento: la loro lunghezza totale non equivale alla campata libera.
Avviso presente nel progetto: bed_temperature_too_high_than_filament (1000C001), dovuto al confronto fra piano a 60 °C e soglia software PLA a 45 °C. Soglia conservata. Preparazione indicata: sportello anteriore aperto, evitare accumulo di calore nella camera; non e un errore geometrico risolto modificando i limiti.

| Piatto | Strati | PLA stimato | Tempo stimato |
| --- | ---: | ---: | --- |
| BAY_R14_01_KIT_COMPLETO | 415 | 142.38 g | 8h 5m 34s |

**Kit: 142.38 g, 8 h 05 min 34 s.** Stime dello slicer con brim, senza torre o cambi colore.

Forza e durata degli incastri, stabilita, finitura, adesione e idoneita termica del PLA restano da verificare sul pezzo. Quote delle porte USB e degli spinotti reali non misurate: spazio generoso parametrico. Non sono state misurate temperature reali degli SSD o degli appoggi. Nessuna simulazione termica, calibrazione della bobina, prova fisica o stampa avviata. Nessun provino aggiunto, come richiesto.
