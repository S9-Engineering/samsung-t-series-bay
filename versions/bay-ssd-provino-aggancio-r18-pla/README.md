# R18 — alette appena aperte e vicine al case

**Pronto per la stampa del provino**, con esportazioni e slicing verificati. La R17 entra bene secondo la prova dell’utente; la R18 affina la posizione delle alette e resta da provare fisicamente. Un solo pezzo per la scocca esistente; il tetto completo non è stato aggiornato.

**[Progetto ElegooSlicer R18](stampa/progetti_ElegooSlicer/BAY_R18_PROVINO_AGGANCIO_ECC2_PLABASIC.3mf)** — un piatto, un oggetto, **6,18 g / 23 min 32 s** stimati dallo slicer, brim e supporti inclusi. Nessuna stampa avviata.

## Modifiche rispetto alla R17

Il chiarimento dell’utente riguarda il gioco tra aletta verticale e parete interna del case. Il taglio nel piano del tetto, con tratto libero lungo 18 mm, rimane identico alla R17.

| Quota nominale | R17 | R18 |
| --- | ---: | ---: |
| Gioco aletta-parete alla radice, per lato | 0,30 mm | **0,15 mm** |
| Apertura della punta verso l’esterno, per lato | 0 | **0,10 mm** |
| Altezza aletta | 12 mm | 12 mm |
| Inclinazione verso l’esterno | 0° | circa **0,48°** |
| Gioco minimo del corpo dell’aletta verso la parete | 0,30 mm | **0,05 mm** |
| Spessore orizzontale dell’aletta | 1,2 mm | 1,2 mm |
| Braccetto dal fianco dell’aletta alla punta | **3,1 mm** | **3,1 mm** |
| Larghezza braccetto / finestra | 8,4 / 9,6 mm | 8,4 / 9,6 mm |
| Gioco verticale sotto il bordo superiore del foro | 0,2 mm | 0,2 mm |

Il gioco residuo impedisce una collisione nominale a riposo: sopra la finestrella, dove la parete è continua, rimangono almeno 0,075 mm. Non è un precarico misurato. L’avvicinamento dell’aletta e la lieve inclinazione portano la punta praticamente a filo esterno, nominalmente 0,042 mm oltre; il braccetto conserva la lunghezza provata sulla R17 e attraversa tutti i 3 mm della parete. La quota fisica dipenderà dalla stampa.

Ingombro nominale del provino: **90,083 × 32 × 15 mm** nell’orientamento di stampa, compresa la minima sporgenza dei braccetti. Traversa spessa 3 mm. Nessuna vite o parte da acquistare.

[Vista e sezione R18](anteprime/01_R18_AGGANCIO.png) · [Montaggio](anteprime/02_R18_MONTAGGIO.png) · [Confronto R17/R18](anteprime/03_R17_R18_CONFRONTO.png)

## Stampa e prova

Usare il progetto 3MF nativo salvato, che comprende geometria, profili, impostazioni e G-code generato dallo slicer. Configurazione confermata: **ELEGOO Centauri Carbon 2 Combo, ugello 0,4 mm, PEI testurizzato, ELEGOO PLA BASIC**, un solo colore disponibile dell’utente; colore della bobina non comunicato.

Faccia esterna della traversa sul piano, alette verso l’alto, orientamento già salvato. Strato 0,20 mm, quattro pareti, gyroid 20%, brim esterno 5 mm con distanza 0,1 mm; 220 °C ugello / 60 °C piano, flusso 0,98, pressure advance 0,04 e portata massima 5 mm³/s. Supporti normali automatici `snug`, anche sopra l’oggetto, interfaccia superiore e inferiore 0,2 mm, due strati di interfaccia e distanza XY 0,35 mm. Nessuna Fuzzy Skin o torre di spurgo. Sono valori iniziali del profilo compatibile, non una calibrazione della bobina; le altre impostazioni sono conservate nel 3MF e nei JSON di `slicer/`.

1. Lasciare raffreddare; rimuovere brim e supporti dalle spalle dei braccetti senza assottigliarle o usarle come leva. Nessuna carteggiatura prevista delle superfici di aggancio.
2. Provare sulla scocca vuota, allineando la traversa alle finestrelle. Accompagnare il rientro delle alette durante l’inserimento e verificare il ritorno verso l’esterno.
3. Controllare entrambi i lati: il provino deve sedersi senza allargare visibilmente le pareti; le punte devono arrivare circa a filo. Il gioco da 0,05 mm è nominale: residui o imprecisioni di stampa possono annullarlo.
4. Trattenere il case e sollevare leggermente la traversa: entrambe le spalle devono prendere sotto il bordo del foro. Per sganciare premere le punte dall’esterno verso l’interno, poi sollevare. Confrontare il ritorno e la presa con la R17.

Il test discrimina l’effetto della lieve apertura e del gioco ridotto. Forza, ritorno elastico, durata e rimozione effettiva dei supporti della R18 non sono stati verificati fisicamente. La traversa ha rigidezza diversa dal tetto completo: prima della consegna del tetto andranno trasferiti e ricontrollati anche gli scarichi.

ElegooSlicer **1.5.3.5 / motore 2.4.2**. Avviso conservato `bed_temperature_too_high_than_filament`: piano 60 °C rispetto alla soglia software PLA 45 °C. **Stampare con sportello anteriore aperto**, evitando accumulo di calore in camera. Nessun altro avviso modello rilevato.

## Verifiche e rigenerazione

STL, STEP singolo, STEP orientato e due STEP di riferimento delle pareti riaperti. Millimetri, un solido e un componente stampabile, mesh chiusa con normali coerenti e volume positivo; zero facce degeneri/duplicate e nessuna coppia rilevata nello screening autointersezioni. Il controllo esclude triangoli con vertici condivisi. Nessuna riparazione della mesh. Le pareti `NON_STAMPARE` sono soltanto riferimenti e non compaiono sul piatto.

Verificati giochi dal STEP finale, assenza di interferenza a riposo, ritenuta geometrica alzando di 0,4 mm e 14 inviluppi di discesa/rilascio con rientro fino a 3,15 mm. Questi inviluppi sono traslazioni rigide delle parti mobili: **non sono una simulazione della deformazione elastica o una misura della forza**. Controparte confrontata con il STEP della scocca R15; R15, R16 e R17 conservate e verificate tramite hash.

3MF nativo riletto indipendentemente: unità, trasformazioni, quantità e ingombri con brim controllati sul piatto 256 × 256 mm e sulla zona esclusa del profilo. Tutti i 75 strati esaminati nella tavola d’insieme, con dettagli di radici, primo strato, supporti e braccetti di entrambi i lati. Vedi il [rapporto completo](verifiche/RAPPORTO_VERIFICHE.md).

Sorgente parametrico `sorgenti/genera.py`, quote `sorgenti/parametri.json`; Python 3.11 / CadQuery 2.8.0 / OCP 7.9.3.1.1, dipendenze in `sorgenti/requirements.txt`. Dalla cartella del progetto:

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

In un ambiente nuovo installare i requirements in una venv. `stampa.py` richiede ElegooSlicer nel percorso macOS indicato nel sorgente; `anteprime.py` usa anche la R17 per il confronto. Dopo qualunque modifica controllare le nuove tavole e registrare la revisione con gli hash correnti in `verifiche/revisione_visiva.json`; soltanto dopo eseguire `sorgenti/consegna.py` per audit e ZIP. Generare immagini non equivale a controllarle.
