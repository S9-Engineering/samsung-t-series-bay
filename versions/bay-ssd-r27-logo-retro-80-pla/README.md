# Bay SSD R27 — logo posteriore all’80%, doppio perno, PLA BASIC

**Pronto per la stampa del prototipo completo.** Progetti nativi ElegooSlicer, esportazioni e percorsi verificati. Il kit R27 completo e il provino a due perni non sono ancora stampati o verificati fisicamente.

## File da usare

- [Kit completo R27 — un unico piatto](stampa/progetti_ElegooSlicer/BAY_R27_02_KIT_COMPLETO_UNICO_PIATTO_ECC2_PLABASIC.3mf): otto pezzi, compresi **due perni identici**.
- [Provino doppio perno R27](stampa/progetti_ElegooSlicer/BAY_R27_01_PROVINO_DOPPIO_PERNO_ECC2_PLABASIC.3mf): quattro pezzi, per controllare i due ricevitori insieme prima del kit completo.
- `stampa/STL/`: sette tipi del kit e due tipi del provino, orientati in mm. Il file del perno va stampato in **due copie** per ogni piatto; i progetti 3MF le contengono già.
- `CAD/`: STEP e STEP orientati. `ASSIEME_R27_NON_STAMPARE.step` include tre SSD di riferimento e serve per consultazione.
- `stampa/GCODE/`: G-code realmente generati dallo slicer, identici a quelli incorporati nei rispettivi progetti. Nessun file inviato alla stampante.

Aprire il 3MF come **progetto**, conservando profili, orientamenti e disposizione. I due 3MF finali includono macchina, materiale, impostazioni per oggetto e slicing. I 3MF in `sorgenti/` sono invece le disposizioni geometriche di ingresso.

| Piatto | PLA stimato | Tempo stimato | Pezzi |
| --- | ---: | --- | ---: |
| PROVINO | 26.15 g | 1h 35m 49s | 4 |
| COMPLETO | 214.07 g | 12h 30m 42s | 8 |

Stime di ElegooSlicer con brim incluso, senza supporti o torre di spurgo. Il provino è separato dal piatto del kit.

## Cosa cambia

Solo il logo posteriore è ridotto all’**80% delle dimensioni lineari** della R26: **32 × 19,77 mm** anziché 40 × 24,72 mm. Mantiene il centro X45 / Z71,5 e il rilievo **0,4 mm**, nello stesso PLA del tetto. Il margine verticale sulla fascia posteriore alta 29 mm passa da circa 2,14 a **4,61 mm** sopra e sotto; ai lati rimangono **29 mm**. Restano il marchio completo S9 ENGINEERING e le proporzioni approvate, senza cambiare font.

Scocca, due perni identici, tre cartucce B, fermo frontale e provino hanno geometria e STL identici alla R26. Tutto il tetto fino alla faccia posteriore Y109 è identico, inclusi guide e ricevitori. L’unica modifica riguarda il rilievo esterno. Il confronto selettivo è in `verifiche/geometria.json`.

Due supporti speculari interni, assi X8,2 / X81,8 e Y96, senza precarico. Chiudere entrambi i perni con un quarto di giro e abbassamento di 1,1 mm. Nessuna vite o colla. Spigoli netti, cavi esterni, aperture inferiori e superiori e pattern laterale conservati; S9 frontale invariato. Ingombro complessivo **90 × 109,8 × 86 mm**, inclusi loghi, esclusi piedini e cavi. Sotto la fascia del logo rimane aperta la zona USB, con spine e cavi che proseguono all’esterno.

## Pezzi del kit

| Pezzo | Copie | Orientamento e impostazioni specifiche |
| --- | ---: | --- |
| SCOCCA_R27_DOPPIO_PERNO | 1 | Dritta sulla base, quattro pareti |
| TETTO_R27_DOPPIO_PERNO | 1 | Capovolto, esterno sul PEI; Arachne |
| PERNO_R27_NASCOSTO | **2** | Disteso, riempimento 100% rettilineo |
| FERMO_CARTUCCE_R27 | 1 | Sul fondo, presa in alto |
| CARTUCCIA_T7_R27 | 1 | Sul piede, sei pareti |
| CARTUCCIA_T7_Shield_R27 | 1 | Sul piede, sei pareti |
| CARTUCCIA_T9_R27 | 1 | Sul piede, sei pareti |

Nel piatto completo le tre cartucce sono in riga, da sinistra T7, T7 Shield e T9. Il perno indicato SX e quello indicato DX nel progetto sono copie identiche, intercambiabili.

## Configurazione di stampa

**ELEGOO Centauri Carbon 2 Combo, ugello 0,4 mm, PEI testurizzato, ELEGOO PLA BASIC, monocolore.** ElegooSlicer 1.5.3.5, motore 2.4.2, profilo specifico `Elegoo Centauri Carbon 2 0.4 nozzle` della Combo. I profili installati sono stati confrontati con le copie incluse; provenienza in `verifiche/provenienza_profili.json`.

Strato 0,20 mm; quattro pareti generali, sei per cartucce, due perni pieni, resto 20% gyroid. Solo tetto e suo provino usano Arachne; altri oggetti con il generatore precedente. Brim esterno 5 mm, distanza 0,1 mm, compensazione piede d'elefante 0,1 mm. Supporti, fuzzy skin, torre di spurgo disattivati; sequenza per strati.

Ugello 220 °C, piano 60 °C, limite volumetrico 5 mm³/s, ponti 25 mm/s, flusso filamento 0,98 / processo 0,97, PA 0,04: valori iniziali ereditati dalla preparazione precedente, senza una nuova calibrazione della bobina. La temperatura ugello coincide con il profilo PLA BASIC ECC2 installato. Unico avviso ammesso: `bed_temperature_too_high_than_filament`, 1000C001, soglia software 45 °C rispetto al piano 60 °C. Per questa preparazione PLA mantenere lo sportello anteriore aperto.

Piano pulito, materiale asciutto, singolo canale CANVAS della bobina effettiva assegnato. Conservare gli orientamenti del 3MF. Lasciare raffreddare prima del distacco; rimuovere brim e fili senza forzare o carteggiare automaticamente gli accoppiamenti. Tutti i pezzi possono essere dello stesso colore: oro e blu delle anteprime servono a riconoscere le parti.

## Provini e riscontro dell'utente

Il **primo provino interni R24 è stato accettato dall'utente** nella conversazione del 23 ottobre 2026 e non va ripetuto per questa modifica. L'utente riferisce che il secondo provino precedente entra; il ciclo completo di rotazione e bloccaggio del perno non è stato esplicitamente confermato. I riscontri non sono misurazioni strumentali e sono registrati in `verifiche/prove_riferite_utente.json`.

Il provino a due perni conserva la geometria della R26 e tutte e due le sedi del kit finale, senza logo e con alleggerimenti simmetrici lontani dai ricevitori. Serve a verificare contemporaneamente i due punti della nuova chiusura prima della stampa lunga. Inserire il tetto dal retro nelle guide, arrivare a battuta, inserire ogni perno dal basso con il traversino più stretto in alto, ruotare di 90° e abbassare di 1,1 mm. Entrambi devono essere azionabili a mano e il tetto deve restare trattenuto. Per aprire sollevare di 1,1 mm, ruotare e sfilare tutti e due i perni, quindi arretrare il tetto. Ripetere senza fare leva o deformare le guide. Se non si assesta, correggere le quote prima del kit.

## Assemblaggio completo

1. Fuori dal case e con cavo scollegato, inserire ciascun SSD da dietro nella propria cartuccia: T7, T7 Shield, T9. Ogni cartuccia ha due cornici chiuse, non alette elastiche. Le aperture dedicate conservano 0,2 mm per lato e 0,5 mm sopra rispetto ai gabarit nominali.
2. Calare ciascuna cartuccia 6 mm più avanti della posizione finale, poi arretrarla sotto i quattro fermi rigidi dello slot. Lo stesso piede entra nei tre slot; per cambiare ordine spostare insieme SSD e cartuccia.
3. Inserire il fermo frontale comune dalla presa alta. Deve appoggiare sul fondo fra il fronte e le battute delle cartucce. Impedisce l'avanzamento del piede; nessun elemento va forzato sotto la T.
4. Collegare i cavi da dietro. Allineare il tetto alle guide e farlo scorrere dal retro fino in posizione. Inserire e bloccare **entrambi i perni da sotto** con la sequenza del provino. I quarti di giro sono speculari; usare il verso che assesta il traversino nella sede, senza forzare.
5. Per smontare, sbloccare e rimuovere entrambi i perni, arretrare e sfilare il tetto. Servono circa 11 cm liberi dietro. Scollegare il cavo del disco da rimuovere, togliere il fermo frontale, avanzare la cartuccia di 6 mm e sollevarla.

Nessuna ferramenta o colla interna da acquistare. Servono soltanto i quattro piedini trasparenti propri dell'utente: sedi Ø10,5 mm profonde 0,65 mm; i piedini devono lasciare almeno 5 mm di aria sotto il fondo. Uso da scrivania in verticale; il fermo cartucce è appoggiato per gravità e non è progettato per trasporto capovolto.

## Controlli e limiti

Nove tipi STEP, STEP orientati e STL riaperti: scala mm, un solido/componente per parte, mesh chiusa, normali coerenti, volume positivo, nessuna faccia degenere o duplicata, zero coppie nello screening autointersezioni. Lo screening esclude facce con vertici condivisi; non è una prova matematica completa di ogni difetto possibile. Nessuna riparazione delle mesh applicata.

Assieme riaperto con undici solidi: otto componenti stampati e tre SSD di riferimento. Otto tipi invariati rispetto alla R26, compresi i due tipi del provino; sei tipi invariati nel kit. Nove abbinamenti SSD/slot verificati con il tetto esportato. Le verifiche cinematiche R26 (171 pose cartucce, 35 pose tetto e 124 pose dei perni) sono conservate per identità geometrica delle superfici funzionali, senza ripeterle. Forza, usura e durata non misurate. Le superfici funzionali del provino corrispondono a quelle del kit.

Entrambi i progetti slicer riaperti per unità, quantità, trasformazioni, volumi, profili, brim, area utile e zona esclusa. Tutti gli strati visualizzati nelle tavole di percorso, con dettagli dei supporti, dei due perni e del logo ridotto. I tredici glifi S9 ENGINEERING risultano presenti nel G-code completo. Nessun supporto o torre; nessuna isola esterna candidata nello screening raster. Nessun G-code inviato alla macchina.

Il kit R27 completo, la calzata simultanea delle due cornici di ogni cartuccia, il gioco residuo, la finitura del logo, i cavi reali e il raffreddamento restano da provare fisicamente. SSD nominali: T7 85 × 57 × 8 mm, Shield 88 × 59 × 13 mm, T9 88 × 60 × 14 mm; cavo/spina modellati con un ingombro generoso 20 × 20 × 50 mm. Nessuna simulazione termica eseguita. Tenere libere le prese inferiori e superiori e confrontare dentro/fuori bay a parità di lavoro, soprattutto per il disco centrale; verificare eventuali deformazioni del PLA nell'uso.

## Sorgenti e riproducibilità

Python 3.11, CadQuery 2.8.0 / OCP 7.9.3.1.1, dipendenze in `sorgenti/requirements.txt`. Nel workspace è disponibile `../bay-ssd-universale-r01/.venv/bin/python`; altrove creare un ambiente e installare le dipendenze. Lo slicing richiede ElegooSlicer installato in `/Applications/ElegooSlicer.app`.

`genera.py` conserva supporti e perni R26 con nomi R27; `geometria_r25.py` conserva il marchio approvato, `geometria_r24.py` le cartucce B, `involucro_r22.py` guide e perno, `base_r15.py` le primitive di base. Quote in `parametri.json`, comprese le sezioni `fermo_nascosto`, `doppio_perno`, `cartucce_b` e `logo_posteriore`. Alcune coordinate dei tagli e delle interfacce sono esplicite nei sorgenti. I loghi PNG/SVG e i contorni approvati sono inclusi.

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/verifica_logo.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Dopo modifiche ripetere la revisione visiva e aggiornare `revisione_visiva.json` prima di `consegna.py`. `CAD/riferimenti_R26/` contiene i soli riferimenti di confronto, non pezzi da stampare. Le revisioni precedenti rimangono conservate. Il pacchetto finale è `BAY_R27_COMPLETO_LOGO_80_PLA_BASIC.zip`, con manifest SHA-256 e verifica di integrità dell'archivio.
