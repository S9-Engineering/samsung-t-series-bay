# R17 — provino del braccetto laterale quasi passante

**Questo è il provino corretto per la lunghezza del braccetto. Sostituisce la R16 per questa prova.** Un solo pezzo da provare sulla scocca già stampata; il tetto completo resta da aggiornare dopo il test.

**[Apri il progetto ElegooSlicer R17](stampa/progetti_ElegooSlicer/BAY_R17_PROVINO_BRACCETTO_PASSANTE_ECC2_PLABASIC.3mf)** — **6,17 g di ELEGOO PLA BASIC, 23 min 31 s** stimati dallo slicer, brim e supporti inclusi. Un piatto, un oggetto, 75 strati. Nessuna stampa avviata.

**Stato: pronto per la stampa del provino**, con geometria, export e slicing controllati. La tenuta e il ritorno elastico si verificano fisicamente sul case.

## La quota corretta

| Quota nominale | R17 |
| --- | ---: |
| Spessore parete / profondità del foro | 3,0 mm |
| Penetrazione del braccetto nella parete | **2,8 mm** |
| Distanza della punta dal filo esterno | **0,2 mm** |
| Lunghezza dal fianco dell’aletta alla punta | **3,1 mm** |
| Distanza fra le punte dei due braccetti | 89,6 mm |
| Larghezza del braccetto / della finestra | 8,4 / 9,6 mm |
| Gioco per estremità nella larghezza del foro | 0,6 mm |
| Gioco verticale della spalla sotto il bordo del foro | 0,2 mm |

Il braccetto occupa quindi circa il **93% dei 3 mm** della parete. La spalla si appoggia sotto il bordo superiore della finestrella quando si tira verso l’alto. Non è il piccolo dente da 1 mm della R16.

Per consentire la corsa laterale di questo braccetto più lungo, la radice ha uno scarico nel piano della traversa: il tratto libero è lungo 18 mm. L’aletta verticale resta all’altezza del foro esistente. I pattini di precarico della R15/R16 non sono presenti in questo provino. Traversa alleggerita **90 × 32 × 3 mm**, alta **15 mm** nell’orientamento di stampa.

[Sezione e vista del provino](anteprime/01_R17_BRACCETTO_PASSANTE.png) · [Montaggio sul case](anteprime/02_R17_MONTAGGIO.png)

## Stampa e prova

Usare il 3MF salvato: ECC2 Combo, ugello 0,4 mm, PEI testurizzato, ELEGOO PLA BASIC; faccia esterna della traversa sul piano e alette verso l’alto. Strati 0,20 mm, quattro pareti, gyroid 20%, brim 5 mm, 220/60 °C, limite 5 mm³/s. Supporti normali `snug` sotto i braccetti, già impostati, con interfaccia a 0,2 mm. Sono valori iniziali del profilo compatibile, non una calibrazione della bobina. Nessuna Fuzzy Skin o torre di spurgo.

1. Rimuovere brim e supporti a stampa raffreddata, senza assottigliare i braccetti. I supporti sono accessibili dai lati; evitare di tirarli facendo leva sull’aletta.
2. Usare il case vuoto. Centrare la traversa sulle due finestrelle laterali e premere vicino alle alette fino all’appoggio sul bordo del case. Le punte devono rientrare durante la discesa e tornare verso l’esterno nei fori.
3. Dall’esterno verificare che entrambe le punte arrivino quasi a filo: rimangono nominalmente 0,2 mm.
4. Trattenere il case e sollevare leggermente la traversa: la spalla deve prendere sul bordo del foro. Per aprire, premere i braccetti verso l’interno attraverso le finestrelle e poi sollevare. Gli scarichi superiori restano accessibili per accompagnare il movimento.

Annotare se entrambi i lati arrivano a filo, trattengono e tornano nella posizione iniziale. Queste prove determinano l’esito; non è stata misurata la forza. La traversa ha una rigidezza diversa dal tetto completo: dopo il test andranno trasferiti e ricontrollati anche gli scarichi di radice.

ElegooSlicer **1.5.3.5 / motore 2.4.2**. Avviso mantenuto `bed_temperature_too_high_than_filament`: piano 60 °C rispetto alla soglia software PLA 45 °C. **Stampare con sportello anteriore aperto**, evitando accumulo di calore in camera.

## Controlli e sorgenti

STL e STEP singolo, STEP orientato e due STEP di riferimento delle pareti riaperti; scala in mm, un componente, mesh chiusa, normali coerenti, volume positivo, nessuna faccia degenere/duplicata o coppia rilevata nello screening autointersezioni. I riferimenti `NON_STAMPARE` non sono sul piatto. Unità, trasformazioni, ingombri con brim e percorsi del 3MF nativo controllati. Tutti i 75 strati esaminati e dettagli ingranditi di braccetti, supporti e scarichi. Vedi il [rapporto](verifiche/RAPPORTO_VERIFICHE.md).

Nel CAD la posizione seduta non interseca il case; l’alzata di 0,4 mm incontra il bordo superiore. Controllate 14 posizioni degli inviluppi di inserimento/rilascio, con spostamento laterale fino a 3 mm. Sono controlli geometrici, **non simulazione elastica, prova della corsa effettiva o misura della forza**. Nessuna prova fisica R17. R15/R16 e relativi file sono conservati.

Sorgente parametrico in `sorgenti/genera.py`, quote in `sorgenti/parametri.json`, dipendenze Python 3.11 / CadQuery 2.8.0 / OCP 7.9.3.1.1 in `sorgenti/requirements.txt`. Dalla cartella del progetto:

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Per un ambiente nuovo installare i requirements in una venv. Il confronto del case usa la R15 se presente. Dopo una modifica rivedere le nuove tavole, registrare hash e riscontro in `verifiche/revisione_visiva.json` ed eseguire `sorgenti/consegna.py`; generare immagini non equivale a controllarle.
