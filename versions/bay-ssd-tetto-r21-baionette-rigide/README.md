# R21 — tetto con due perni rigidi a quarto di giro

**Eliminate le alette elastiche delle revisioni precedenti.** Il tetto ha due supporti pieni e si blocca con due perni laterali rimovibili. Si appoggia dall’alto, si inseriscono i perni nelle finestrelle esistenti e si ruotano di 90°. Nessuna parte deve flettersi durante la chiusura nominale; non servono viti, colla o ferramenta.

**Stato: pronto per la stampa del prototipo, con prova preliminare dell’incastro.** Geometria, cinematica ed entrambi i progetti dello slicer verificati. Tenuta, gioco e durata reali restano da provare: il riscontro negativo sulle alette R19 non viene sostituito da una promessa basata sul solo CAD.

## File da usare

| Progetto ElegooSlicer | Sul piatto | Stima reale dello slicer |
| --- | --- | --- |
| **[01 — Prova sulla scocca esistente](stampa/progetti_ElegooSlicer/BAY_R21_01_PROVA_AGGANCIO_ECC2_PLABASIC.3mf)** | Traversa leggera + 2 perni | **6,98 g / 25 min 01 s** |
| **[02 — Tetto completo](stampa/progetti_ElegooSlicer/BAY_R21_02_TETTO_COMPLETO_ECC2_PLABASIC.3mf)** | Tetto con coda + 2 perni | **35,26 g / 1 h 56 min 12 s** |

Ogni progetto usa un piatto, tre oggetti, PLA BASIC monocolore e brim incluso; nessun supporto o spurgo multicolore. Il test usa le stesse sedi e gli stessi perni del tetto. **Prima verificare la prova leggera sul case reale**, poi stampare il tetto completo. I perni del test sono riutilizzabili; il progetto completo ne contiene già due per comodità.

[Viste del tetto](anteprime/01_R21_TETTO_E_ASSIEME.png) · [Funzionamento del perno](anteprime/02_R21_MECCANISMO.png) · [Prova sul case](anteprime/03_R21_PROVINO.png)

## Come si chiude

1. Rimuovere il brim, soprattutto dal piccolo piano inferiore dei perni. Liberare eventuali fili nei fori dei due supporti senza allargare la sede o assottigliare il gambo. I fori sono accessibili da entrambe le estremità.
2. Appoggiare la traversa di prova sulla scocca vuota, allineata alle finestrelle. La scocca R15 non richiede modifiche. Per il tetto completo allineare anche i riferimenti anteriori e la coda.
3. Tenere la paletta esterna del perno **orizzontale** e inserirlo dall’esterno nella finestrella e nel supporto. Non forzare un perno che non entra: il test serve anche a distinguere il gioco nominale dal risultato della stampa.
4. Ruotare di **90°**, portando la paletta esterna **verticale**. Il traversino interno ruota dietro al supporto e non può più sfilarsi lungo il suo asse. Ripetere sul secondo lato.
5. Verificare la presa trattenendo la scocca e sollevando leggermente la traversa. Controllare che entrambi i lati trattengano e che il gioco sia accettabile; provare alcuni cicli di inserimento, quarto di giro e apertura. La prova riguarda il bloccaggio, non il sollevamento del bay carico dal tetto.
6. Per aprire, riportare le palette in orizzontale, estrarre entrambi i perni e sollevare. Non tirare il tetto con i perni ancora trasversali.

La chiusura ha ritenuta geometrica a 90° e **non ha uno scatto elastico o un arresto angolare automatico**. La posizione verticale della paletta indica il bloccaggio. La resistenza a rotazioni accidentali e il comportamento dopo molti cicli non sono stati misurati.

## Geometria e componenti

Il kit completo contiene un tetto e due perni identici, tutti stampati in PLA BASIC. Gli STL sono separati per tipo e già orientati. Il provino è un terzo tipo di pezzo, alternativo al tetto per il test iniziale.

| Quota nominale | Valore |
| --- | ---: |
| Tetto orientato per stampa | 90 × 109 × 29 mm |
| Traversa di prova orientata | 90 × 21 × 17,5 mm |
| Un perno orientato per stampa | 15,9 × 9 × 2,75 mm |
| Supporto rigido: sezione di attacco al tetto | 6 × 12 mm |
| Centro dei fori sul case | Y50,5 / Z72,5 mm |
| Finestra esistente del case | 9,6 × 3 mm |
| Foro di ingresso nel supporto | 4,8 × 3,2 mm |
| Gambo del perno | Ø2,8 mm, con piccolo piano inferiore |
| Traversino del perno in posizione di ingresso | 4,4 × 2,7 mm |
| Gioco per lato traversino/foro, direzione Y | 0,2 mm |
| Gioco per lato traversino/foro, direzione Z | 0,25 mm |
| Gioco radiale massimo teorico gambo/finestra in altezza | 0,1 mm |
| Separazione assiale traversino/supporto prima della ritenuta | 0,3 mm |
| Ingombro laterale del bay con palette esterne | circa 96,4 mm |

Le due righe di feritoie sopra i nuovi supporti sono accorciate simmetricamente di 7 mm verso il centro, lasciando una fascia esterna di 12 mm: il supporto si attacca a una zona continua del tetto. Restano sedici feritoie orizzontali, spigoli netti, coda posteriore e logo S9 della scocca esistente; nessun taglio di scarico superiore. La coda termina sempre a Z57 e i cavi restano esterni.

I supporti distano 1 mm dalle pareti interne. Nel CAD il minimo fra perni e SSD nominali è 1,3 mm, e fra tetto e ingombri USB prudenziali 20 × 20 × 50 mm è 3,3 mm. Gli spinotti reali e le tolleranze della scocca stampata restano da controllare.

## Stampa

Configurazione confermata: **ELEGOO Centauri Carbon 2 Combo, ugello 0,4 mm, PEI testurizzato, ELEGOO PLA BASIC**. Il profilo installato è denominato `Elegoo Centauri Carbon 2 0.4 nozzle`; non è un profilo della Centauri Carbon di prima generazione. Un solo colore della bobina disponibile; i perni azzurri nelle anteprime servono soltanto a illustrare il meccanismo.

- Tetto e traversa con faccia esterna sul piano; **perni piatti con asse del gambo parallelo al piano**, già orientati. Non stampare i perni in piedi.
- Strato **0,20 mm**, quattro pareti, **riempimento rettilineo 100%**, brim esterno 5 mm con distanza 0,1 mm, stampa per strati.
- **Supporti disabilitati**. I fori nei blocchi richiedono ponti di circa 4,8 mm, controllati nell’anteprima; eventuale cedimento del ponte va valutato sulla prova leggera. Nessuna cavità con supporti da estrarre.
- Ugello 220 °C, piano 60 °C, flusso 0,98, pressure advance 0,04, limite volumetrico 5 mm³/s. Sono valori iniziali conservati dal profilo compatibile; non costituiscono calibrazione della bobina. Nessuna Fuzzy Skin o torre di spurgo.

App ElegooSlicer **1.5.3.5**, motore **2.4.2**. Avviso mantenuto `bed_temperature_too_high_than_filament` (`1000C001`): piano 60 °C rispetto alla soglia software PLA 45 °C. **Stampare con sportello anteriore aperto**, evitando accumulo di calore in camera. Nessun altro avviso modello rilevato.

I 3MF di `stampa/progetti_ElegooSlicer/` sono veri progetti dello slicer con profili, disposizione, materiali, impostazioni e G-code generato dallo slicer incorporati. I 3MF in `sorgenti/` sono i file d’ingresso alla lavorazione. Nessuna stampa è stata avviata.

## Verifiche e stato fisico

STL, STEP e STEP orientati riaperti: tre tipi di oggetto, un componente per STL, scala millimetrica, volume positivo, normali coerenti, mesh chiuse; zero facce degeneri o duplicate e nessuna coppia rilevata nello screening autointersezioni. Il controllo esclude triangoli con vertici condivisi. Nessuna riparazione automatica.

Verificati l’appoggio del tetto, 86 posizioni/casi dei perni per inserimento, rotazione e ritenuta, la corrispondenza delle sedi fra provino e tetto e tutti i nove abbinamenti modello SSD/slot. I corpi si muovono rigidamente, senza richiedere la flessione di pareti o alette. Le interferenze di ritenuta attese sono presenti dopo rotazione e durante il tentativo di alzare il tetto.

Entrambi i 3MF riaperti indipendentemente: un piatto e tre oggetti, unità, trasformazioni, scala, brim e zona esclusa controllati. Tutti gli 88 strati della prova e i 145 del tetto visionati, con ingrandimenti di perni, supporti rigidi, fori e ponti. Zero candidati di nuove isole nello screening raster. Vedi [rapporto](verifiche/RAPPORTO_VERIFICHE.md), [stato](verifiche/STATO_CONSEGNA.json) e [revisione visiva](verifiche/revisione_visiva.json).

**La prova fisica R21 non è stata eseguita:** ingresso, rotazione reale, giochi, tenuta e durata devono passare il test sulla scocca. L’eliminazione delle alette cambia il modo di trattenere il tetto; non autorizza a dichiarare una resistenza mai misurata. Nessuna FEA o prova termica.

La [guida Formlabs sugli incastri stampati](https://formlabs.com/eu/blog/designing-3d-printed-snap-fit-enclosures/) evidenzia la dipendenza dei cantilever da materiale, deformazione e orientamento. La scelta di usare perni rigidi è specifica di questo progetto e non una prestazione certificata da quella guida.

## Sorgenti

Python 3.11, CadQuery 2.8.0 / OCP 7.9.3.1.1; dipendenze in `sorgenti/requirements.txt`. Sorgente `sorgenti/genera.py`, quote in `sorgenti/parametri.json`. Il STEP della scocca in `CAD/riferimenti_NON_STAMPARE/` è solo un riferimento; non compare nei piatti.

Dalla cartella del progetto:

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Per un nuovo ambiente installare i requirements in una venv. Lo slicing usa `/Applications/ElegooSlicer.app/`; il controllo degli hash storici richiede le cartelle sorelle R15/R18/R19/R20. Dopo modifiche rivedere le nuove tavole, registrare gli hash correnti in `verifiche/revisione_visiva.json`, poi eseguire `sorgenti/consegna.py`. Generare immagini non equivale a controllarle.
