# R23 — confronto fra tre nuove sedi interne

**Studio comparativo per scegliere l'architettura. Non è un kit pronto per lo slicer o per la stampa.** Le vecchie alette e i precedenti inserti non sono la base dei nuovi alloggi. Tutte le alternative sono pensate in ELEGOO PLA BASIC, senza viti, colla o pezzi commerciali aggiuntivi.

Il riscontro dell'utente riguarda flessione delle alette e instabilità delle soluzioni con inserti/colonnine. La R22 riutilizzava le sedi R15: il suo piatto completo è ora segnato come da rivedere. La chiusura scorrevole del tetto rimane un sottoprogetto separato; il suo provino non prova la stabilità degli SSD.

## Guardare prima queste tavole

- [01 — Tre alternative, con e senza SSD](anteprime/01_CONFRONTO_A_B_C.png)
- [02 — Le tre alternative dentro il case, con T7, Shield e T9](anteprime/02_NEL_CASE.png)
- [03 — Come si carica e si monta la cartuccia B](anteprime/03_USO_SOLUZIONE_B.png)

Le immagini provengono dai modelli CAD e rappresentano quote nominali. Colori diversi distinguono SSD, culle, basamento e guida superiore; la stampa proposta resta monocolore. La scocca nella seconda tavola è tagliata per mostrare l'interno.

## Il cambiamento comune

Occorre distinguere due movimenti: il gioco del disco nella propria sede e il gioco dell'intera culla sul basamento. Rendere più stretta la prima interfaccia non risolve una seconda interfaccia che si muove o si piega.

Per questo tutte le alternative hanno una **base unica e larga**, con due appoggi distanziati e una finestra centrale. Questa base è trattenuta da guide basse e corti fermi del nuovo basamento. Il basamento è previsto solidale alla scocca nella revisione finale; nei STEP dello studio è separato per rendere leggibili i componenti.

L'interfaccia proposta si monta dall'alto in posizione avanzata di 6 mm, poi scorre indietro sotto due coppie di fermi rigidi. Le superfici a cuneo mettono in appoggio la base senza caricare alette alte o appoggi liberi. La geometria nominale entra senza interferenze nei campioni di moto verificati. **La presa del cuneo, il gioco residuo e la forza di estrazione devono essere calibrati sul provino della soluzione scelta.** Non sono proprietà dimostrate dal CAD.

Il disco resta libero nella culla. È la base della culla che deve essere localizzata e trattenuta sul case. Il T9 avrà anch'esso una propria cartuccia: nessun modello userà più direttamente le vecchie alette. L'interfaccia al basamento è identica nei tre slot; si cambia la cartuccia quando si cambia modello di SSD.

Il basamento è finestrato davanti, al centro e dietro. Gli appoggi pieni sono concentrati sotto le due fasce di sostegno, evitando una piastra piena sotto tutta la lunghezza del disco. Le aperture non costituiscono una validazione del raffreddamento passivo.

## A — Culla aperta alta

Un solo pezzo per disco: due U alte, spesse 3 mm, collegate alla stessa base. Le radici sono allargate e il carico passa nel basamento. La guida attiva è alta 32 mm, con 2 mm di invito in ingresso.

Il disco si inserisce e si sfila dall'alto una volta aperto il tetto. La fascia centrale della faccia rimane libera; sopra la culla non c'è un ponte.

È la soluzione più immediata da usare e lascia invariato il tetto R22. Il compromesso è che la parte alta del disco resta libera: un eventuale gioco laterale della sede produce ancora un certo dondolio in alto. Aumentare la rigidità della culla non elimina questo gioco geometrico.

## B — Cartuccia con due cornici chiuse

Un solo pezzo per disco: due cornici rettangolari complete, collegate dalla stessa base. Le sponde sono spesse 3 mm; solo gli angoli esterni superiori rientrano fino a circa 2 mm per passare accanto alle guide del tetto R22. Il ponte superiore è spesso 2,4 mm.

Il disco si infila **da dietro nella cartuccia fuori dal case**, con il cavo scollegato; poi si cala la cartuccia completa dall'alto e la si assesta nel basamento. Le due cornici guidano il corpo lungo quasi tutta l'altezza e collegano fra loro le due sponde. La porta USB resta libera, dietro l'ultima cornice. Il disco non viene serrato e rimane sfilabile assialmente quando si rimuove la cartuccia.

È la mia candidata preferita per il requisito di un sostegno rigido con pochi pezzi: la geometria controlla la parte alta del disco senza richiedere altri elementi nel tetto. Occorre accettare il gesto di caricamento fuori dal case. Le due fasce coprono più superficie del disco rispetto ad A; i ponti superiori e l'orientamento di stampa andranno controllati nello slicing del prototipo.

## C — Guida bassa e guida superiore

Due pezzi per disco: una culla inferiore con guida attiva alta 10 mm e un elemento sotto il tetto che accompagna gli ultimi 7 mm del corpo dell'SSD. I due punti di guida sono lontani in altezza, per limitare la leva della parte superiore.

Si apre il tetto, si inserisce il disco dall'alto nella culla bassa e si richiude facendo scorrere la guida superiore sul bordo lungo del disco. La posizione e il canale della guida alta dipendono dal modello: cambiando SSD in uno slot si devono abbinare sia la culla sia la guida del tetto.

Le zone coperte sulle facce sono piccole, ma aumentano pezzi, accoppiamenti e necessità di allineamento durante la chiusura. **Il fissaggio delle guide superiori al tetto e il raccordo con le feritoie non sono finalizzati.** Nei modelli sono rappresentati gli ingombri e la funzione della guida; non un aggancio pronto da stampare. A tetto aperto il disco è guidato soltanto in basso.

## Confronto pratico

| | A — U aperte alte | B — Cornici chiuse | C — Basso + alto |
| --- | --- | --- | --- |
| Componenti specifici per disco | 1 | 1 | 2 |
| Inserimento dell'SSD | Dall'alto nel case | Da dietro nella cartuccia rimossa | Dall'alto, poi chiusura tetto |
| Controllo della parte alta | Indiretto, dalla culla inferiore | Diretto, attraverso le cornici | Diretto quando il tetto è chiuso |
| Tetto R22 | Conservato | Conservato | Richiede sviluppo interno |
| Facce libere | Ampie zone centrali e superiori | Due fasce verticali coperte | Piccole zone sopra e sotto |
| Compromesso principale | Più sensibilità al gioco della sede | Caricamento meno immediato | Più pezzi e allineamenti |

**Partirei da B se è accettabile caricare l'SSD nella cartuccia fuori dal case.** A è la scelta più pratica se l'inserimento diretto dall'alto è prioritario. C resta un'alternativa da considerare se si vuole il doppio riferimento alto/basso accettando un ulteriore sviluppo del tetto.

Questa è una preferenza progettuale, non una classifica di resistenza misurata. Non ci sono prove di carico o FEA delle tre soluzioni.

## Quote iniziali e verifiche

Gli SSD sono gabarit rettangolari nominali: T7 85 × 57 × 8 mm, Shield 88 × 59 × 13 mm, T9 88 × 60 × 14 mm. Tutti sono appoggiati a Z13 mm, con USB verso il retro. Interasse dei tre slot 24 mm: due T9 lasciano 10 mm fra le facce. Le cornici sono profonde 12 mm e centrate a Y34 e Y82; fra le due rimane un tratto libero di 36 mm.

Il gioco del disco nello studio è **0,4 mm totale, cioè 0,2 mm per lato**, non 0,4 per lato. B lascia anche 0,5 mm sopra il gabarit. Questi numeri rendono il confronto coerente e sono modificabili per modello: non sostituiscono le misure dei dispositivi reali, incluse le parti gommate. La [guida Prusa sulle tolleranze](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135) spiega che il gioco necessario dipende da geometria, materiale, orientamento e calibrazione; non esiste un valore universale trasferibile alla nostra stampante.

Controllati i 15 componenti CAD esportati e riaperti, i tre assiemi e le mesh di anteprima: solidi validi, scala millimetrica, mesh chiuse e coerenti, volume positivo, nessuna faccia degenere o duplicata, nessuna coppia nello screening delle autointersezioni (che esclude facce con vertici condivisi). Non sono esportazioni STL di stampa.

Sono state verificate **27 combinazioni**: ogni SSD in ogni slot per ognuna delle tre alternative. Controllati ingombri della scocca, tetto R22, connettori nominali, inserimento SSD, ingresso e scorrimento della base e assenza di collisioni tra modelli diversi in slot adiacenti. I movimenti sono campionati, non una verifica continua certificata. Vedi [report dei controlli](verifiche/controlli_studio.json).

Le grandi aperture fra le fasce mantengono percorsi possibili per l'aria. Non sono state eseguite CFD, prove termiche, prove di tenuta o di durata. La scelta definitiva andrà sviluppata con gli inviti e gli accoppiamenti reali, seguita da un piccolo provino, quindi dal progetto completo e dallo slicing in ElegooSlicer. Non sono indicati tempi o consumi di stampa per questo studio.

## Sorgenti e CAD

`CAD_STUDIO_NON_STAMPARE/` contiene componenti e assiemi STEP per il confronto. Gli assiemi includono i gabarit SSD e parti separate intenzionali; non vanno inviati allo slicer come oggetti unici.

`sorgenti/genera.py` definisce le tre alternative, `parametri.json` le quote e i giochi; `involucro_r22.py` e `base_r15.py` conservano le funzioni geometriche di riferimento. Python 3.11, CadQuery 2.8.0 / OCP 7.9.3.1.1, dipendenze in `requirements.txt`.

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Lo stato corrente e gli hash sono in `verifiche/`. Nessun G-code o 3MF di stampa è stato generato per le alternative, e nessuna stampa è stata avviata.
