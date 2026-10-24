# R06 — studio esterno «monolite»

Proposta estetica richiesta il 20 ottobre 2026: ritorno a una scocca compatta in grafite, con tetto dello stesso colore, fronte pieno e raccordi più contenuti. Il colore è illustrativo, da abbinare al filamento disponibile.

L'ingombro della scocca resta **90 × 101 × 86 mm**, esclusi SSD sporgenti dietro, cavi e gommini commerciali. Gli angoli verticali esterni passano da R4,5 a **R3 mm**; i raccordi dei bordi diventano **0,4 mm** (bordo inferiore del tetto 0,2 mm). Nessuna decorazione aggiunta.

Sedi, inserti, incastri del coperchio, feritoie, retro aperto e quattro sedi dei gommini rimangono quelli della R05. Nessuna vite e nessun adesivo interno. Gli SSD nei render sono ingombri nominali schematizzati.

## Stato

**Studio estetico**, separato dalla R05 già preparata. Non è una nuova consegna pronta per la stampa: mancano STL, progetto dello slicer e revisione dei percorsi di questa variante. Nessuna prova fisica o termica. Le viste sono ottenute dal CAD STEP esportato e riaperto.

`verifiche/studio.json` riporta dimensioni, solidi, controlli di base delle mesh, assenza di sovrapposizione scocca/tetto e confronto geometrico con la R05 nel volume interno. Non comprende un controllo completo delle autointersezioni. Il controllo dei file della R05 conferma che la revisione precedente non è stata modificata.

## Contenuti e rigenerazione

- `anteprime/01_R06_MONOLITE.png`: tavola frontale e tre quarti.
- `anteprime/02_R06_FRONTE.png`, `03_R06_TRE_QUARTI.png`, `04_R06_ALTO.png`: viste singole.
- `CAD_studio/`: scocca, coperchio e assieme STEP di studio, in millimetri.
- `sorgenti/parametri.json`: quote e palette modificabili; `genera.py` contiene la geometria derivata dalla R05.
- `sorgenti/studio.py`: esportazione, verifiche dello studio e render.

Dipendenze bloccate in `sorgenti/requirements.txt`. Eseguire con Python 3.11:

```sh
python sorgenti/studio.py
```

È necessario conservare la cartella sorella `bay-ssd-universale-r05-incastri` per il confronto con i STEP e l'audit dei suoi file. Il modello R06 si genera dai propri parametri e sorgenti. Il render usa VTK e i caratteri Arial di sistema macOS.
