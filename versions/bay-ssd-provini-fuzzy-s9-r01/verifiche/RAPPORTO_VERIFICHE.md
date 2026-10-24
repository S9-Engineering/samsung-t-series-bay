# Verifiche — provini Fuzzy Skin e S9 a filo R01

Data: 20 ottobre 2026. Stato: **pronto per la stampa dei provini**, non stampato. Nessun invio alla macchina. Progetto del case R12 conservato: confronto di tutti i 144 file del suo manifesto SHA-256 superato.

## Geometria esportata

Cinque pezzi stampabili, tutti già orientati sul piano: quattro pannelli 36 × 14 × 32 mm e un riferimento PEI 36 × 24 × 3 mm. Cinque STL, cinque STEP stampabili e uno STEP della maschera non stampabile. STEP riaperti, solidi validi; STL riaperti, scala in mm e dimensioni controllate. Ogni pezzo stampabile ha un solo componente, volume positivo, normali coerenti e mesh chiusa. Nessuna faccia degenere o duplicata.

Lo screening delle autointersezioni confronta coppie di triangoli senza vertici condivisi: zero intersezioni rilevate. Le coppie che condividono vertici non sono coperte da questo algoritmo; non è una prova matematica completa di assenza di autointersezioni. La validità dei solidi CAD e il riutilizzo di superfici piane semplici forniscono controlli aggiuntivi. Nessuna riparazione automatica delle mesh.

La maschera contiene due componenti intenzionali: fondo intorno a S9 e isola che riempie il vuoto interno al 9. Non costituisce materiale stampato. Il fronte del corpo resta sul piano nominale Y=0 e **il logo non ha rilievo**. La parete ha spessore 3 mm; la Fuzzy Skin può scostare il solo cordone esterno fino a 0,10 mm nei campioni. Piede 2,4 mm, tacche 1,6 × 1,2 mm, margine liscio intorno al campo ruvido. Nessun incastro o accoppiamento in questi provini.

## 3MF finale

Il progetto nativo è stato riaperto come archivio e analizzato per ID dei corpi, riferimenti a file e trasformazioni del modello. Unità `millimeter`, 5 oggetti stampabili, 3 volumi modificatori, trasformazioni rigide; corpi chiusi con volumi positivi e quantità attese. Dimensioni, posizione e volume dei corpi stampabili coincidono con gli STL entro le tolleranze numeriche riportate nello script. I cinque ingombri con brim 5 mm sono interamente nel piano del profilo e separati fra loro; zona esclusa 246…256 × 0…20 mm rispettata.

Nota sullo strumento di lettura: il caricatore 3MF generico di trimesh concatena i corpi contenuti nello stesso file multipart, e non è stato usato per approvare i conteggi. La lettura XML indipendente seleziona invece ogni `objectid` nel file corretto e compone le trasformazioni di `build` e `component`.

## Slicing effettivo e percorsi

ElegooSlicer **2.4.2**, macchina **Elegoo Centauri Carbon 2 0.4 nozzle** del progetto ECC2 Combo, piano PEI testurizzato, ELEGOO PETG PRO. Materiale e configurazione hardware già confermati dall'utente. Profili macchina e filamento derivati dalla R12; temperature effettive 240 °C ugello e 65 °C piano, portata massima 5 mm³/s. Processo a 0,20 mm, 4 pareti, 20% gyroid, brim esterno 5 mm, supporti e torre disattivati, un solo materiale. Nessuna modifica ai macro macchina.

**160 strati; stime slicer 23,30 g e 1 h 18 min 21 s, con brim.** Zero avvisi CLI e zero avvisi modello. Tutti gli strati contengono estrusioni, conteggio dichiarato e letto concordanti. Percorsi entro il piano e fuori dalla zona esclusa. Screening raster dei nuovi contorni: zero candidati a isola sospesa. La risoluzione raster è 0,5 mm con dilatazione dello strato precedente: non dimostra il sostegno di ogni dettaglio submillimetrico.

I segmenti classificati `Internal Bridge` negli strati 8 e 11 attraversano il riempimento. Il segmento più lungo è 37,27 mm, ma non rappresenta una campata libera: sottraendo la copertura idealizzata dei cordoni precedenti restano tratti stimati al massimo di circa **4,55 mm**. È un controllo geometrico, non una simulazione del cedimento del PETG. Le chiusure sopra il riempimento sono state ispezionate nelle anteprime.

Il profilo eredita `extruder_offset = 0x1.5`. Per confrontare i percorsi con la geometria è stata rispettata la correzione Y=-1,5 mm; nessuna compensazione arbitraria è stata aggiunta.

## Selettività della Fuzzy Skin e del logo

Confronto dei percorsi estrusi reali nel campo frontale: scostamento massimo rispettivamente **0,06 / 0,08 / 0,10 mm**, coerente con i tre modificatori. Il controllo liscio resta rettilineo. Il retro resta liscio. Campionando l'interno dei due glifi con margine eroso di 0,20 mm, ciascun glifo è coperto in 32 strati controllati; lo scostamento residuo massimo è inferiore a **0,001 mm** nei percorsi. Queste cifre descrivono il file digitale e non l'accuratezza fisica della stampante.

La tolleranza di semplificazione dei percorsi è stata ridotta da 0,012 a 0,001 mm: con la tolleranza iniziale alcune transizioni invadevano leggermente la zona liscia. Lo slicing finale è stato ricalcolato e i controlli ripetuti. La texture è nel progetto dello slicer, non nei triangoli degli STL.

## Revisione visiva

Effettivamente aperte e ispezionate le quattro tavole degli strati 1–40, 41–80, 81–120 e 121–160, oltre alle due immagini di dettaglio. Controllati: primo strato e separazione dei brim, tacche di identificazione, passaggio dal piede al pannello, chiusure sopra infill, ultimo strato e percorsi frontali ingranditi. Immagini e progetto sono legati tramite hash in `revisione_visiva.json`.

L'immagine dei quattro fronti è uno **schema delle zone di finitura**, con grana illustrativa uguale nei tre riquadri. I grafici sottostanti vengono dai percorsi reali e mostrano le diverse ampiezze; non sono fotografie né previsioni del riflesso del materiale.

## Limiti aperti

Non sono stati stampati campioni, non è stata misurata rugosità o lucentezza. Il PETG liscio conserva le righe degli strati e non equivale a una lucidatura a specchio. La scelta finale richiede confronto fisico con la stessa bobina e illuminazione. I risultati non validano incastri, dispositivi reali, dissipazione termica o resistenza del bay completo.
