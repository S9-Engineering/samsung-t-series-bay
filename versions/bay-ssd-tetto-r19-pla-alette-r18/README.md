# R19 — tetto completo con le alette della R18

**Pronto per la stampa del tetto prototipo**, con geometria, esportazioni e slicing verificati. Sul piatto è presente **soltanto il tetto completo**, in un unico pezzo con coda posteriore e due agganci; si monta sulla scocca R15 esistente. Nessuna stampa avviata.

**[Apri il 3MF ElegooSlicer pronto](stampa/progetti_ElegooSlicer/BAY_R19_TETTO_COMPLETO_ALETTE_R18_ECC2_PLABASIC.3mf)** — **28,00 g / 1 h 31 min 02 s** stimati dallo slicer, brim e supporti inclusi. Un piatto, un oggetto, 145 strati, un colore di ELEGOO PLA BASIC.

[Anteprima del tetto](anteprime/01_TETTO_R19.png) · [Assieme sulla scocca](anteprime/02_ASSIEME_R19.png) · [Piatto e primo strato](anteprime/03_PIATTO_R19.png)

## Geometria

Il tetto conserva bordi netti, tagli orizzontali di ventilazione, due riferimenti anteriori e coda posteriore della R15. I due agganci laterali e gli scarichi alla radice sono quelli della R18: differenza geometrica zero nelle due zone confrontate con il STEP del provino. Fuori dalle zone modificate, il confronto con il tetto R15 restituisce differenza zero. Scocca e supporti a U non richiedono ristampa per questo aggiornamento del tetto.

| Quota nominale | R19 |
| --- | ---: |
| Ingombro del pezzo orientato per stampa | **90,083 × 109 × 29 mm** |
| Spessore tetto / coda | 3 / 3 mm |
| Quota inferiore della coda sul case | Z57 mm |
| Aletta: altezza × larghezza × spessore orizzontale | 12 × 9 × 1,2 mm |
| Lunghezza del braccetto dal fianco dell’aletta | **3,1 mm** |
| Apertura della punta verso l’esterno, per lato | **0,10 mm**, circa 0,48° |
| Gioco aletta-parete alla radice, per lato | **0,15 mm** |
| Gioco minimo aletta-parete | **0,05 mm** |
| Gioco minimo sopra la finestrella, a parete continua | 0,075 mm |
| Larghezza braccetto / finestrella esistente | 8,4 / 9,6 mm |
| Gioco per estremità nella larghezza del foro | 0,6 mm |
| Gioco verticale della spalla sotto il bordo superiore del foro | 0,2 mm |
| Tratto flessibile nel piano del tetto, prima dell’aletta | 18 mm |

Il braccetto occupa tutti i 3 mm della parete; la punta è nominalmente circa 0,042 mm oltre il filo esterno. Il piccolo gioco residuo evita interferenze nominali a riposo: non corrisponde a una forza o a un precarico misurato. I tagli di scarico conservano lo spazio per il rientro laterale; in tre righe per lato comunicano con le feritoie originali.

## Configurazione e stampa

- Macchina: **ELEGOO Centauri Carbon 2 Combo**, ugello **0,4 mm**, **PEI testurizzato**, **ELEGOO PLA BASIC**, già confermati dall’utente. Il profilo installato è denominato `Elegoo Centauri Carbon 2 0.4 nozzle`, lo stesso ramo ECC2 usato nelle revisioni precedenti. Un solo filamento; colore della bobina non comunicato.
- Orientamento già impostato: **faccia esterna del tetto sul piano**, alette e coda verso l’alto. Stampare **una copia**. La superficie esterna assume la finitura del piano PEI; nessuna Fuzzy Skin.
- Strato **0,20 mm**, quattro pareti, gyroid 20%, brim esterno 5 mm con distanza 0,1 mm. Ingombro con brim circa 100,083 × 119 mm, entro il piatto 256 × 256 e fuori dalla zona esclusa del profilo.
- Ugello 220 °C, piano 60 °C, flusso 0,98, pressure advance 0,04, limite volumetrico 5 mm³/s. Valori iniziali conservati dal profilo compatibile: la bobina non è stata calibrata in questa revisione. Impostazioni complete nei JSON di `slicer/` e nel 3MF.
- Supporti normali automatici `snug`, anche sopra il modello, con interfaccia superiore/inferiore 0,2 mm, due strati di interfaccia e distanza XY 0,35 mm. Lo slicing genera supporti sotto i braccetti; coda e riferimenti anteriori crescono direttamente dal tetto. Nessuna torre di spurgo o cambio colore.

Il 3MF finale è un **vero progetto ElegooSlicer**, con geometria, disposizione, profili, impostazioni e G-code generato dallo slicer incorporati. App **1.5.3.5 / motore 2.4.2**. `sorgenti/TETTO_R19_SORGENTE.3mf` è il file di ingresso alla lavorazione: usare per la stampa il progetto nella cartella `stampa/progetti_ElegooSlicer/`.

Avviso mantenuto `bed_temperature_too_high_than_filament` (`1000C001`): piano 60 °C rispetto alla soglia software PLA 45 °C. **Stampare con sportello anteriore aperto**, evitando accumulo di calore in camera. Nessun altro avviso modello rilevato.

## Pulizia e montaggio

1. Lasciare raffreddare, quindi togliere brim e supporti sotto i braccetti. Rimuoverli lateralmente, senza usare l’aletta come leva, senza assottigliare la spalla. Liberare gli scarichi e controllare che non restino fili o supporti.
2. Fare la prima prova sul case vuoto. Allineare i riferimenti anteriori e la coda; accompagnare il rientro delle alette in corrispondenza delle finestrelle, premendo vicino agli agganci fino all’appoggio del tetto sul bordo.
3. Controllare che entrambi i braccetti tornino verso l’esterno e arrivino circa a filo. Il tetto deve sedersi senza allargare visibilmente le pareti; il gioco da 0,05 mm è nominale e dipende dalla stampa.
4. Trattenere il case e sollevare leggermente il tetto per verificare che prendano entrambe le spalle. Per aprire, premere i due braccetti dall’esterno verso l’interno e poi sollevare il tetto.
5. Verificare infine i tre SSD e i cavi reali, lasciati all’esterno. La coda ha almeno **3,3 mm nominali** rispetto agli ingombri USB prudenziali di **20 × 20 × 50 mm**; le dimensioni reali degli spinotti non sono state misurate.

Non occorrono viti, adesivi interni o altri componenti per questo tetto. I piedi e gli inserti del corpo esistente non fanno parte del piatto R19.

## Verifiche e limiti

STL, STEP e STEP orientato riaperti e confrontati: millimetri, un solido/componente, mesh chiusa, normali coerenti, volume positivo; zero facce degeneri o duplicate e nessuna coppia rilevata nello screening autointersezioni. Quest’ultimo esclude triangoli con vertici condivisi. Nessuna riparazione automatica della mesh.

Il confronto con i file finali R18 conferma il trasferimento di entrambi gli agganci e delle radici; il confronto con R15 conferma che il resto del tetto è conservato. Nessuna collisione nominale con la scocca, con i tre modelli SSD nei tre slot o con gli ingombri USB previsti. Verificata l’interferenza di ritenuta alzando il tetto di 0,4 mm. Controllati 14 inviluppi di discesa/rilascio, traslando le parti mobili fino a 3,15 mm: sono controlli dello spazio disponibile, **non una simulazione elastica**.

3MF finale riletto indipendentemente: quantità, unità, trasformazioni, ingombri con brim e zona esclusa verificati. Tutti i **145 strati** esaminati nelle due tavole d’insieme e nei dettagli di radici, alette, supporti, primo strato, coda e ponti. Vedi il [rapporto](verifiche/RAPPORTO_VERIFICHE.md), il [riscontro visivo](verifiche/revisione_visiva.json) e lo [stato di consegna](verifiche/STATO_CONSEGNA.json).

La R17 entra bene secondo il riscontro dell’utente. Non è stato comunicato un nuovo esito fisico della R18: forza, ritorno, durata e accoppiamento del tetto completo R19 restano da verificare sulla stampa. La verifica geometrica non dimostra il comportamento elastico o termico del pezzo. Nessuna prova termica eseguita e nessuna stampa avviata.

## Sorgenti e rigenerazione

Sorgente principale `sorgenti/genera.py`; funzioni dell’aggancio `sorgenti/agganci_r18.py` e quote in `sorgenti/parametri_aggancio_R18.json`, copiate dalla R18. Le altre quote sono in `sorgenti/parametri.json`. STEP scocca R15, vecchio tetto R15 e provino R18 conservati in `CAD/riferimenti_NON_STAMPARE/`: servono solo alle verifiche e non sono sul piatto. Il pacchetto può rigenerarsi senza modificare le cartelle precedenti.

Python 3.11, CadQuery 2.8.0 / OCP 7.9.3.1.1; dipendenze in `sorgenti/requirements.txt`. Dalla cartella del progetto:

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Per un nuovo ambiente installare i requirements in una venv. Lo slicing usa l’app in `/Applications/ElegooSlicer.app/`; il confronto con gli hash R15/R18 richiede le relative cartelle sorelle. Dopo modifiche rieseguire i controlli, visionare le nuove tavole e registrare gli hash correnti in `verifiche/revisione_visiva.json`; poi eseguire `sorgenti/consegna.py` per audit e ZIP. La generazione di una tavola non sostituisce il controllo visivo.
