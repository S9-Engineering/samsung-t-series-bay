# Verifiche — provini R02 PLA BASIC

Data: **21 ottobre 2026**. Variante dei provini R01 in PETG PRO, preparata per **ELEGOO PLA BASIC** confermato dall'utente. Hardware: Centauri Carbon 2 Combo, ugello 0,4 mm, piano PEI testurizzato. Nessuna prova fisica né invio alla stampante.

## Geometrie e confronto con PETG

Cinque STEP stampabili e cinque STL esportati e riaperti: quattro pannelli 36 × 14 × 32 mm e una piastrina PEI 36 × 24 × 3 mm. Ogni pezzo ha un solido, mesh chiusa, normali coerenti, volume positivo, nessuna faccia degenere o duplicata. Screening delle autointersezioni superato. L'algoritmo esclude coppie di triangoli con vertici condivisi e non è una dimostrazione matematica completa; si aggiunge al controllo della validità dei solidi CAD. Nessuna riparazione automatica.

**I cinque STL coincidono byte per byte con quelli R01 PETG.** Sono uguali anche parametri geometrici, logo, campioni, posizioni sul piatto, impostazioni Fuzzy Skin e profilo macchina. Il processo differisce solo nel nome. Il materiale usa temperatura, raffreddamento e pressure advance del proprio profilo. I 45 file del manifesto originale R01 PETG sono conservati, con hash verificati.

S9 è largo 14 mm, margine destro 4 mm, margine inferiore 6 mm, **rilievo nominale zero**. La Fuzzy Skin è nei percorsi, non negli STL. I modificatori sono esclusi dalla quantità dei pezzi stampabili.

## Profilo materiale

Catena di ereditarietà ufficiale locale, inclusa nel pacchetto: `fdm_filament_common` → `fdm_filament_pla` → `Elegoo PLA @base` → **`Elegoo PLA Basic @ECC2`**. Il profilo include esplicitamente la macchina `Elegoo Centauri Carbon 2 0.4 nozzle`.

Ugello 220 °C, piano testurizzato 60 °C, strato 0,20 mm, 4 pareti, riempimento 20% gyroid, brim 5 mm, supporti e torre disattivati. Limite di portata ridotto dal valore ufficiale 21 a **5 mm³/s**, uguale alla R01 PETG per un confronto a velocità comparabili. Temperature entro i valori ELEGOO PLA BASIC, 190–230 °C ugello e 35–65 °C piano. Nessuna calibrazione della singola bobina o del suo colore.

## Slicing e avviso PLA

Slicer installato: `/Applications/ElegooSlicer.app`, firma del bundle verificata valida. Versione CLI/motore **2.4.2**, versione bundle **1.5.3.5**. Il tentativo iniziale con una vecchia copia temporanea non si avviava; la consegna usa lo slicing completato con l'installazione verificata.

**160 strati, 23,30 g e 1 h 18 min 21 s** stimati dallo slicer con brim; densità del profilo 1,25 g/cm³. Queste stime coincidono con la R01 perché geometria, limite di portata e densità dei profili coincidono. Non sono tempi o pesi misurati.

Rimane un avviso nativo **`bed_temperature_too_high_than_filament`**, codice `1000C001`. Il profilo PLA conserva la propria soglia software di 45 °C; con piano a 60 °C lo slicer raccomanda di ventilare la camera per limitare il rischio di intasamento. **Preparazione documentata: sportello anteriore aperto durante la stampa PLA.** La soglia non è stata alterata per eliminare l'avviso. Non vi sono avvisi geometrici o altri avvisi nativi inattesi. Riferimento: [documentazione OrcaSlicer della soglia](https://github.com/OrcaSlicer/OrcaSlicer/wiki/material_basic_information).

Sono stati controllati i setpoint effettivi del G-code esportato: ugello 220 °C durante la stampa e piano 60 °C, senza residui dei 240/65 °C PETG. Il setpoint intermedio ugello 140 °C appartiene alla preparazione del profilo macchina; 0 °C allo spegnimento finale. G-code prodotto esclusivamente dallo slicer e conservato nel progetto e nel riscontro di controllo, mai scritto a mano.

## File finali e percorsi

3MF finale riaperto con lettura XML indipendente per percorso, `objectid`, ruolo e trasformazioni: unità millimetri, **5 oggetti stampabili e 3 modificatori**, corpi stampabili confrontati con gli STL, trasformazioni rigide e corretta posizione sul piano. Ogni maschera contiene due componenti intenzionali, fondo e isola interna al 9; non aggiunge materiale. Il caricatore generico trimesh non è usato per contare i corpi multipart del 3MF, perché concatena le mesh contenute nello stesso file.

Ingombri con brim entro il piano del profilo 256 × 256 mm e fuori dalla zona esclusa 246…256 × 0…20 mm. Cinque basi separate al primo strato. Nessuna invasione del piano o della zona esclusa. Tutti i 160 strati hanno estrusioni; conteggio dichiarato concordante. Screening raster dei nuovi contorni senza candidati a isole sospese; controllo approssimato a 0,5 mm, non una prova di sostegno di ogni dettaglio.

I segmenti `Internal Bridge` attraversano il riempimento. Il confronto con una copertura idealizzata dei cordoni dello strato precedente stima tratti scoperti fino a circa **4,55 mm**: il segmento lungo 37,27 mm non è una campata libera. Non è una simulazione del cedimento del PLA.

Fuzzy Skin: scostamenti massimi digitali 0,06 / 0,08 / 0,10 mm, coerenti con i modificatori. Zone interne ai glifi S e 9 controllate su 32 strati ciascuna; scostamento residuo digitale inferiore a 0,001 mm. Retro e controllo 00 restano lisci. Coordinate confrontate rispettando l'offset estrusore del profilo Y=-1,5 mm. Queste cifre descrivono i percorsi, non l'accuratezza fisica della stampante.

## Revisione visiva e stato

Esaminate le quattro tavole di tutti gli strati 1–40, 41–80, 81–120 e 121–160 e le due immagini di dettaglio. Controllati primo strato, brim, tacche, passaggio dal piede al pannello, chiusure sopra infill, ultimo strato e percorsi frontali ingranditi. La revisione è registrata con hash delle immagini e del progetto in `revisione_visiva.json`.

La figura dei quattro fronti è uno schema delle zone di finitura, non un render ottico del PLA. I grafici derivano dai percorsi effettivi, con deviazioni amplificate per renderle visibili.

Stato: **pronto per la stampa dei provini**, con la preparazione PLA indicata nelle istruzioni. Lucentezza, rugosità e qualità della stampa non sono state misurate. La prova non valida incastri, temperature d'esercizio, fit o dissipazione del bay completo. Il confronto fisico PLA/PETG è ancora da eseguire.
