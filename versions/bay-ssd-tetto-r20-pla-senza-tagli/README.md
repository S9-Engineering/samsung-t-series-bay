# R20 — ritirata; ripristinata R19

**[Usare il tetto completo R19 in PLA BASIC](../bay-ssd-tetto-r19-pla-alette-r18/stampa/progetti_ElegooSlicer/BAY_R19_TETTO_COMPLETO_ALETTE_R18_ECC2_PLABASIC.3mf).**

**R20 RITIRATA — NON STAMPARE.** È stata ripristinata la R19 con gli scarichi nel tetto, su richiesta dell’utente per il rischio di rottura del nuovo attacco interno. I controlli digitali storici sotto riportati non costituiscono una validazione meccanica. I tagli superiori attorno alle alette sono eliminati: dall’alto restano le sole feritoie orizzontali originali. Il pattern sui fianchi della scocca resta invariato. Nessuna stampa avviata.

**File R20 conservato soltanto come storico; non usare per la stampa.** — **28,94 g / 1 h 35 min 03 s** stimati dallo slicer, brim e supporti inclusi. Un piatto, un pezzo, 145 strati, ELEGOO PLA BASIC monocolore.

[Viste del tetto](anteprime/01_TETTO_R20.png) · [Montato sulla scocca](anteprime/02_ASSIEME_R20.png) · [Piatto e primo strato](anteprime/03_PIATTO_R20.png)

## Modifica dell’aggancio

La funzione dei tagli precedenti era lasciare libero il tratto flessibile nel piano del tetto. Nella R20 quel tratto è spostato **sotto il tetto**, separato dalla lastra da un gioco verticale di **3 mm**, e collegato alla lastra da un ancoraggio anteriore. Il tetto torna integro attorno alle feritoie di ventilazione; non vengono introdotte altre aperture esterne.

Il tratto libero conserva lunghezza 18 mm e sezione 1,2 × 3 mm della R18, traslate verso il basso di 6 mm. La parte inferiore verticale e il braccetto conservano la posizione della R18 nel foro esistente. **L’attacco al tetto è nuovo:** la corrispondenza delle quote non dimostra che forza, ritorno e durata siano gli stessi della R18/R19.

| Quota nominale | R20 |
| --- | ---: |
| Ingombro del pezzo orientato per stampa | **90,083 × 109 × 29 mm** |
| Spessore tetto / coda | 3 / 3 mm |
| Coda: quota inferiore sul case | Z57 mm |
| Tratto flessibile interno: lunghezza libera / sezione | 18 mm / 1,2 × 3 mm |
| Quote Z del tratto flessibile | 77–80 mm |
| Gioco verticale fra tratto flessibile e lastra | **3 mm** |
| Ancoraggio anteriore: posizione Y | 25–28 mm |
| Lunghezza del braccetto dal fianco dell’aletta | **3,1 mm** |
| Larghezza braccetto / finestrella esistente | 8,4 / 9,6 mm |
| Gioco per estremità nella larghezza del foro | 0,6 mm |
| Gioco verticale della spalla sotto il bordo superiore del foro | 0,2 mm |
| Inclinazione verso l’esterno della porzione verticale | circa 0,48° |
| Gioco minimo aletta-parete | **0,05 mm** |
| Gioco minimo sopra la finestrella, a parete continua | 0,075 mm |

La punta del braccetto resta praticamente a filo esterno, nominalmente circa 0,042 mm oltre. Il residuo gioco evita interferenze nominali con la parete; le quote fisiche dipendono dalla stampa. Bordi netti, coda posteriore e riferimenti anteriori sono conservati. Scocca e supporti a U esistenti non sono sul piatto e non vengono modificati.

## Stampa

Configurazione già confermata: **ELEGOO Centauri Carbon 2 Combo**, ugello **0,4 mm**, **PEI testurizzato**, **ELEGOO PLA BASIC**. Profilo installato `Elegoo Centauri Carbon 2 0.4 nozzle`, già usato per la ECC2 Combo nelle revisioni precedenti. Un solo colore della bobina disponibile dell’utente; colore non comunicato.

Orientamento già salvato: **faccia esterna del tetto sul piano**, alette e coda verso l’alto. Stampare una copia. La faccia esterna prende la finitura del PEI; nessuna Fuzzy Skin.

Strato **0,20 mm**, quattro pareti, gyroid 20%, brim esterno 5 mm con distanza 0,1 mm. Ingombro con brim circa 100,083 × 119 mm, verificato entro il piatto 256 × 256 mm e fuori dalla zona esclusa. Ugello 220 °C, piano 60 °C, flusso 0,98, pressure advance 0,04 e portata massima 5 mm³/s. Sono valori iniziali conservati dal profilo compatibile; la bobina non è stata calibrata in questa revisione.

**Supporti necessari sotto i braccetti e fra i tratti flessibili interni e il tetto**, già presenti nel 3MF: normali automatici `snug`, anche sopra il modello, con distanze superiore/inferiore 0,2 mm, due strati di interfaccia e distanza XY 0,35 mm. L’accesso ai supporti sotto le flessure avviene dal lato interno attraverso il gioco di 3 mm. La loro effettiva rimozione è da provare fisicamente; non lasciare materiale di supporto fra flessura e lastra. La coda e i riferimenti anteriori crescono direttamente dal tetto. Nessuna torre o cambio filamento.

Il 3MF nella cartella `stampa/progetti_ElegooSlicer/` è un **vero progetto ElegooSlicer** con geometria, disposizione, profili, impostazioni e G-code generato dallo slicer incorporati. App **1.5.3.5 / motore 2.4.2**. Il 3MF in `sorgenti/` è invece il file d’ingresso alla lavorazione.

Avviso mantenuto `bed_temperature_too_high_than_filament` (`1000C001`): piano 60 °C rispetto alla soglia software PLA 45 °C. **Stampare con sportello anteriore aperto**, evitando accumulo di calore in camera. Nessun altro avviso modello rilevato.

## Pulizia e montaggio

1. Lasciare raffreddare. Rimuovere brim e supporti dai braccetti e **dal gioco tra flessure e tetto**. Agire dal lato aperto verso l’interno del case, sostenendo il tratto flessibile vicino al punto di distacco. Evitare di tirare il supporto facendo leva sulla punta; non assottigliare il braccetto.
2. Controllare che il gioco di 3 mm sia libero e che entrambe le alette possano rientrare e tornare verso l’esterno. Il supporto rimasto nel gioco irrigidirebbe l’aggancio.
3. Fare la prima prova sul case vuoto. Allineare riferimenti anteriori e coda, accompagnare il rientro delle alette e premere vicino agli agganci fino all’appoggio sul bordo del case.
4. Controllare che entrambi i braccetti tornino verso l’esterno e che il tetto si sieda senza allargare visibilmente le pareti. Trattenere il case e sollevare leggermente per verificare la presa di entrambe le spalle.
5. Per sganciare premere i braccetti dall’esterno verso l’interno, poi sollevare il tetto. Verificare infine SSD e connettori reali: rispetto agli ingombri prudenziali USB 20 × 20 × 50 mm restano almeno **3,3 mm nominali** sotto la coda.

Non occorrono viti o adesivi interni. Forza, ritorno, durata e rimozione dei supporti della nuova radice non sono stati verificati fisicamente; il tetto completo è un prototipo. Nessuna prova termica eseguita.

## Verifiche

STL, STEP e STEP orientato riaperti: millimetri, un solido/componente, volume positivo, mesh chiusa e normali coerenti; zero facce degeneri o duplicate e nessuna coppia rilevata nello screening autointersezioni. Il controllo esclude triangoli con vertici condivisi. Nessuna riparazione automatica della mesh.

La lastra superiore coincide con quella originale R15, con differenza geometrica zero: nessun taglio di scarico aggiuntivo. Porzione inferiore dell’aletta e braccetto coincidono con la R18; il tratto libero conserva la sua sezione, traslata sotto il tetto. Verificato il gioco verticale di 3 mm senza materiale fra flessura e lastra. Nessuna interferenza nominale con la scocca o nei nove abbinamenti SSD/slot con relativi ingombri USB. Verificata l’interferenza di ritenuta sollevando di 0,4 mm e controllati 14 inviluppi di discesa/rilascio con rientro fino a 3,15 mm. Questi sono controlli geometrici con traslazioni rigide, **non una simulazione elastica**.

3MF finale riletto indipendentemente: un oggetto, zero modificatori, unità, trasformazioni e ingombri validi. Tutti i **145 strati** controllati nelle due tavole d’insieme e nei dettagli di alette, nuove radici, supporti, primo strato, coda e ponti. Supporti rilevati sotto entrambi i tratti liberi interni; zero candidati di nuove isole nello screening raster. Revisioni R15, R18 e R19 conservate e verificate tramite hash.

Vedi [rapporto](verifiche/RAPPORTO_VERIFICHE.md), [riscontro visivo](verifiche/revisione_visiva.json) e [stato di consegna](verifiche/STATO_CONSEGNA.json). La preparazione digitale non dimostra il buon esito meccanico o termico del pezzo stampato.

## Sorgenti e rigenerazione

Sorgente `sorgenti/genera.py`, quote del tetto e della nuova radice in `sorgenti/parametri.json`. `agganci_r18.py` e `parametri_aggancio_R18.json` conservano le funzioni e le quote storiche della R18, riusate per braccetto e tratto flessibile; i vecchi tagli di quel provino non sono usati per generare il tetto R20. I file in `CAD/riferimenti_NON_STAMPARE/` servono solo ai confronti e non sono sul piatto.

Python 3.11, CadQuery 2.8.0 / OCP 7.9.3.1.1; dipendenze in `sorgenti/requirements.txt`. Dalla cartella del progetto:

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Per un nuovo ambiente installare i requirements in una venv. Lo slicing usa `/Applications/ElegooSlicer.app/`; il controllo degli hash precedenti richiede le cartelle sorelle R15/R18/R19. Dopo modifiche controllare le nuove tavole e registrare la revisione visiva con gli hash correnti in `verifiche/revisione_visiva.json`, poi eseguire `sorgenti/consegna.py`. La sola generazione delle immagini non equivale a una revisione visiva.
