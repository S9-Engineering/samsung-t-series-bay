# Bay SSD R22 — tetto scorrevole, fermo nascosto

La R22 mantiene il volume monolitico, gli spigoli netti, il piccolo S9 in rilievo e il pattern laterale orizzontale. Il tetto entra dal retro su due guide interne continue. Un solo perno rigido, azionato sotto la coda posteriore, impedisce al tetto di arretrare. Non ci sono linguette elastiche, palette esterne, viti, colla o magneti.

**Stato: pronto per la stampa del prototipo, con prova preliminare delle guide e del fermo.** Export, cinematica nominale e slicing controllati; scorrimento, accesso manuale, tenuta e durata reali sono ancora da provare. **Occorre ristampare la scocca:** il tetto R22 non è compatibile con la scocca R15. Gli inserti a U T7 e Shield restano geometricamente identici e sono riutilizzabili.

## File da stampare

| Progetto nativo ElegooSlicer | Contenuto del singolo piatto | Stima effettiva dello slicer |
| --- | --- | --- |
| [01 — Provino delle guide e del fermo](stampa/progetti_ElegooSlicer/BAY_R22_01_PROVINO_GUIDE_E_FERMO_ECC2_PLABASIC.3mf) | Scocca di prova + tetto di prova + perno | **22,70 g / 1 h 19 min 32 s** |
| [02 — Kit completo su un unico piatto](stampa/progetti_ElegooSlicer/BAY_R22_02_KIT_COMPLETO_UNICO_PIATTO_ECC2_PLABASIC.3mf) | Scocca + tetto + perno + 2 inserti T7 + 2 inserti Shield | **159,67 g / 9 h 10 min 40 s** |

Il provino viene prima del kit completo. Le quote funzionali di guide, ricevitore e perno sono le stesse; la lunghezza delle guide del provino è 20 mm invece di 82 mm. Il provino ha una finestra centrale e una coda alleggerita lontano dal comando: consente di verificare la calzata locale, non dimostra da solo l'attrito delle guide complete o l'accesso con tutti i cavi collegati.

Il kit contiene tutti i pezzi per un T7, un T7 Shield e un T9. Se gli inserti R15 sono già disponibili, disabilitare i quattro oggetti `INSERTO_*` nello slicer e risliciare: la stima della tabella riguarda il piatto completo originale. Gli STL separati e già orientati sono in [stampa/STL](stampa/STL/). Il perno del provino è riutilizzabile; il progetto completo ne include uno per comodità.

[Viste esterne](anteprime/01_R22_SILHOUETTE.png) · [Guide e fermo](anteprime/02_R22_GUIDE_E_FERMO.png) · [Retro e provino](anteprime/03_R22_RETRO_E_PROVINO.png) · [Piatto completo](anteprime/04_R22_PIATTO_UNICO.png)

## Chiusura e apertura

1. Rimuovere brim e fili residui. Controllare le superfici inclinate delle guide e le aperture del fermo. Non assottigliare il perno o forzare un pezzo che non scorre.
2. Sul provino vuoto, infilare il tetto da dietro, mantenendolo parallelo alla scocca. Allineare i bordi anteriori del provino e i fori del fermo. Sul case completo le battute anteriori definiscono la posizione chiusa.
3. Inserire il perno **da sotto**: impugnatura e traversino devono essere orientati da sinistra a destra. Spingere fino a portare il traversino nella camera sopra il ricevitore.
4. Girare di **90°**, quindi abbassare il perno di **1,1 mm** nella sede trasversale. L'impugnatura sarà orientata da davanti a dietro. La sede impedisce la rotazione libera; il gambo impedisce l'arretramento del tetto. Le guide trattengono il tetto verso l'alto.
5. Per aprire, alzare il perno di circa **1,1 mm**, ruotarlo indietro di 90° e sfilarlo verso il basso. Arretrare il tetto di circa 101 mm per liberare le guide, quindi sollevarlo. Lasciare circa 11 cm liberi dietro al case.

Il perno è rimovibile, non è una cerniera o un pulsante a molla. Non va ruotato mentre è abbassato nella sede. Il meccanismo è destinato all'apertura ordinaria su una scrivania: non è stato provato per trasportare il bay tenendolo dal tetto.

## Geometria e giochi

| Quota nominale, in mm | Valore |
| --- | ---: |
| Assieme chiuso, esclusi cavi e piedini | **90 × 109,4 × 86** |
| Scocca orientata sul piatto, incluso S9 | 90 × 101,4 × 83 |
| Tetto orientato sul piatto | 90 × 109 × 29 |
| Perno orientato sul piatto | 8 × 26,5 × 3,5 |
| Guide continue, ciascun lato | 82 di lunghezza |
| Radice di ciascuna guida del tetto | 3 di spessore |
| Rampa delle guide | 45° |
| Gioco orizzontale parete/punta e guida/montante | 0,4 per lato |
| Separazione verticale fra le due diagonali | 0,4, circa 0,28 normale alla diagonale |
| Gambo del perno | Ø3,6 con piano di stampa, altezza stampata 3,5 |
| Traversino di ingresso / foro | 6,8 × 3,4 / 7,2 × 4,0 |
| Gioco traversino/foro | 0,2 per lato in X; 0,3 per lato in Y |
| Sede trasversale / profondità | 3,8 × 7,2 / 0,8 |
| Scocca: supporto posteriore sotto il ricevitore | 5 di spessore alla sommità, con rampa inferiore |
| Ricevitore del tetto: pianetto inferiore | 4, con sede profonda 0,8 |

Il tetto appoggia sul bordo superiore della scocca: è una superficie di scorrimento intenzionale. Le superfici di cattura delle guide hanno gioco positivo. Le quote sono parametriche, non calibrate sulla stampa fisica. Le finestrelle dei vecchi ganci sono chiuse nella nuova scocca.

Le sedici feritoie superiori rimangono orizzontali; i margini laterali passano a 12 mm per lasciare una zona continua sopra le guide. La superficie aperta nominale del solo tetto è circa **3.075 mm²**, il 31% del rettangolo superiore. Le aperture inferiori, le sedi dei piedini e il pattern laterale restano invariati. Le guide si trovano sopra il bordo superiore degli SSD; i due canali d'aria fra i dischi restano liberi. Il piccolo supporto del fermo occupa localmente l'angolo posteriore sinistro.

Il comando resta sotto la coda e dentro i 90 mm di larghezza. È visibile guardando nell'apertura posteriore inferiore, senza sporgenze dal fronte, dai lati o dal tetto. Nessun LED o vano cavi interno.

## SSD, cavi e piedini

Ogni sede accetta i tre modelli nominali: T7 85 × 57 × 8; Shield 88 × 59 × 13; T9 88 × 60 × 14. T9 entra direttamente; T7 e Shield usano due collari a U per disco. I due appoggi sono distanziati lungo il bordo lungo. Nessuna pressione sulle facce per mantenere il disco in piedi.

Gli ingombri USB di controllo sono **20 × 20 × 50 mm**, con porta al centro nominale della faccia posteriore. Sono ipotesi prudenti, non misure dei cavi reali. Sono stati controllati tutti i nove abbinamenti modello/slot e l'azionamento del perno; la distanza minima nominale perno/ingombro USB campionata è **1,38 mm**. Sul case completo verificare anche lo spazio per le dita, l'effettiva posizione delle porte e la curva dei cavi.

Sono previste soltanto quattro sedi **Ø10,5 mm, profonde 0,65 mm** per i propri piedini trasparenti. Materiale commerciale aggiuntivo: solo gli eventuali quattro piedini, scelti per ottenere **almeno 5 mm effettivi di luce sotto la base** dopo montaggio e compressione. Nessun adesivo dentro il case. Le feritoie inferiori non devono appoggiare direttamente sulla scrivania.

## Stampa in ELEGOO PLA BASIC

Configurazione confermata: **ELEGOO Centauri Carbon 2 Combo, ugello 0,4 mm, piano PEI testurizzato, ELEGOO PLA BASIC monocolore**. Colore della bobina non comunicato; i colori ocra e azzurro nelle tavole spiegano il montaggio e non richiedono stampa multicolore.

- **Scocca e inserti in piedi sulla base; tetto con faccia esterna sul piatto; perno piatto con asse parallelo al piano.** Gli STL sono già orientati. Non stampare il perno verticalmente.
- Strato **0,20 mm**, quattro pareti, infill **20% gyroid**. Sul solo perno override **100% rettilineo** salvato nel progetto.
- Brim esterno **5 mm**, separazione **0,1 mm**, compensazione piede d'elefante **0,1 mm**; stampa per strati.
- **Nessun supporto**: le guide crescono a 45°. La camera del fermo e i fori hanno ponti brevi; le pareti della camera sono aperte sui lati per ispezione. Nessuna cavità con supporti intrappolati.
- Ugello **220 °C**, piano **60 °C**, flusso **0,98**, pressure advance **0,04**, limite volumetrico **5 mm³/s**. Valori iniziali del profilo compatibile già utilizzato, non calibrazione della singola bobina. Nessuna Fuzzy Skin e nessuna torre di spurgo.

App **ElegooSlicer 1.5.3.5**, motore **2.4.2**. Profilo installato `Elegoo Centauri Carbon 2 0.4 nozzle`, macchina `Elegoo Centauri Carbon 2`, compatibile con la configurazione Combo monocolore usata qui. Non è un profilo della Centauri Carbon di prima generazione.

Avviso conservato: `bed_temperature_too_high_than_filament` (`1000C001`), piano 60 °C rispetto alla soglia software PLA 45 °C. **Stampare con sportello anteriore aperto**, come preparazione PLA del profilo. Non sono stati rilevati altri avvisi modello.

I 3MF in `stampa/progetti_ElegooSlicer/` sono veri progetti dello slicer: geometria, orientamento, disposizione, profili, impostazioni e G-code generato dallo slicer incorporato. Quelli in `sorgenti/` sono gli ingressi geometrici del processo. Nessuna stampa è stata avviata o inviata alla macchina.

## Prova fisica da eseguire

Prima del kit completo, verificare sul provino:

1. Scorrimento sulle due guide senza allargare le pareti o premere forte; nessuna cricca o delaminazione.
2. Inserimento del perno, quarto di giro, abbassamento completo e necessità di rialzarlo per riaprire.
3. Tenuta verso l'alto e contro l'arretramento, trattenendo la scocca di prova. Controllare il gioco, senza caricare o trasportare il bay dal tetto.
4. Almeno dieci cicli, annotando se il gioco aumenta o compaiono segni bianchi, schegge o difficoltà.

Il test breve non sostituisce il controllo delle guide lunghe sulla scocca completa. Dopo l'assemblaggio verificare tutti e tre gli SSD, gli inserti, i cavi e la raggiungibilità del comando. Successivamente confrontare temperature e comportamento degli SSD dentro/fuori dal bay nello stesso carico, soprattutto al centro. **Nessuna verifica termica o di deformazione del PLA nel tempo è stata eseguita.**

## Verifiche digitali e sorgenti

Sette tipi di pezzo esportati e riaperti in STEP, STEP orientato e STL: un solido/componente ciascuno, scala millimetrica, mesh chiuse, normali coerenti, volume positivo, zero facce degeneri o duplicate e nessuna coppia nello screening autointersezioni. Questo screening esclude facce con vertici condivisi e non è una certificazione matematica di assenza di ogni difetto possibile. Nessuna riparazione automatica della mesh.

Verificati 35 offset del tetto, 62 posizioni/fasi del perno, battuta anteriore e interferenze di ritenuta attese; controlli discreti su corpi rigidi, senza analisi delle forze. Le superfici funzionali del provino sono confrontate con quelle del kit completo. I file delle revisioni precedenti sono conservati. R19/R20/R21 non sono i file da stampare per questa chiusura.

Entrambi i progetti riaperti indipendentemente: unità, trasformazioni, quantità, scala, margini del brim e zona esclusa verificati. Percorsi di tutti i **145 strati del provino e 415 del kit** esaminati, con dettagli delle guide, del perno, del fermo, dei ponti e del primo strato. Vedi [rapporto](verifiche/RAPPORTO_VERIFICHE.md), [stato](verifiche/STATO_CONSEGNA.json) e [riscontro visivo](verifiche/revisione_visiva.json).

Python 3.11, CadQuery 2.8.0 / OCP 7.9.3.1.1. Dipendenze riproducibili in `sorgenti/requirements.txt`. `base_r15.py` conserva le funzioni della scocca, del logo e degli inserti già approvati; `genera.py` sostituisce il coperchio e aggiunge le guide e il fermo. Parametri separati in `sorgenti/parametri.json`; aumentando il gioco delle guide occorre rigenerare e ricontrollare tutti i derivati. Loghi e contorni sono inclusi nell'archivio.

Dalla cartella del progetto, con l'ambiente CadQuery già disponibile:

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Per un ambiente nuovo installare i requirements in una venv. Lo slicing richiede `/Applications/ElegooSlicer.app/`; il confronto degli hash storici richiede le cartelle sorelle R15/R19/R20/R21. Dopo ogni modifica rivedere le tavole e i percorsi, registrare i loro hash in `verifiche/revisione_visiva.json` e solo allora eseguire `sorgenti/consegna.py`. Generare un'immagine non equivale a verificarla.
