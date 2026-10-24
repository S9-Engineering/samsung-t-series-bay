# Bay SSD R25 — logo posteriore S9 Engineering

**Pronto per la stampa del prototipo con prova preliminare. Stampa e finitura non ancora verificate fisicamente.** Questa revisione aggiunge soltanto il logo completo approvato alla faccia esterna posteriore del tetto R24. S9 frontale, scocca, tre cartucce B, fermo frontale, chiusura e aperture sono conservati. Il confronto geometrico con R24 e riportato in `verifiche/geometria.json`.

## File da usare

- [Solo tetto con logo — 3MF](stampa/progetti_ElegooSlicer/BAY_R25_01_SOLO_TETTO_LOGO_ENGINEERING_ECC2_PLABASIC.3mf): per sostituire il tetto se il resto del kit R24 e gia disponibile.
- [Kit completo — 3MF, unico piatto](stampa/progetti_ElegooSlicer/BAY_R25_02_KIT_COMPLETO_UNICO_PIATTO_ECC2_PLABASIC.3mf): sette pezzi, una copia di ciascuno.
- `stampa/STL/`: sette STL orientati in mm. `CAD/`: STEP e STEP orientati; l'assieme contiene anche tre gabarit SSD ed e solo di consultazione.
- `stampa/GCODE/`: G-code effettivamente generati da ElegooSlicer e confrontati con quelli incorporati nei progetti. Nessun file inviato alla stampante.

I due 3MF sopra sono progetti nativi con macchina, filamento, impostazioni, oggetti separati e slicing. I 3MF in `sorgenti/` sono invece le disposizioni geometriche di ingresso.

| Piatto | Materiale stimato | Tempo stimato | Pezzi |
| --- | ---: | --- | ---: |
| TETTO | 38.64 g | 2h 10m 17s | 1 |
| COMPLETO | 211.54 g | 12h 19m 57s | 7 |

Stime dello slicer con brim incluso, senza supporti o torre di spurgo. Non sono misurazioni fisiche.

## Logo

Stesso marchio approvato: S9 sopra e ENGINEERING sotto, senza cambiare proporzioni o font. **40 × 24,72 mm**, centrato a X45 / Z71,5 sulla faccia posteriore 90 × 29 mm (compreso il bordo del tetto), con margini verticali circa 2,14 mm. Rilievo **0,4 mm**, nello stesso PLA del tetto; sovrapposizione nella parete 0,15 mm. Il testo e leggibile guardando il retro da +Y. Nessun pezzo, adesivo o cambio colore aggiuntivo.

Ingombro del bay chiuso: **90 × 109,8 × 86 mm**, incluso S9 frontale e nuovo rilievo posteriore, esclusi cavi e piedini. L'aggiunta e tutta all'esterno; nessuna parte del tetto originale e stata sottratta. Non cambiano connettori, ventilazione o superfici di chiusura. Il tetto R25 puo sostituire quello R24 senza ristampare gli altri sei pezzi.

## Stampa

ELEGOO Centauri Carbon 2 Combo, ugello **0,4 mm**, **PEI testurizzato**, **ELEGOO PLA BASIC**, monocolore. ElegooSlicer 1.5.3.5, motore 2.4.2, profilo macchina specifico `Elegoo Centauri Carbon 2 0.4 nozzle` della Combo.

Strato 0,20 mm; quattro pareti generali, sei per cartucce, perno 100% rettilineo e resto 20% gyroid. Brim esterno 5 mm, gap 0,1 mm, compensazione piede d'elefante 0,1 mm. Supporti, fuzzy skin e torre disattivati; sequenza per strati. **Solo il tetto usa Arachne** per conservare i tratti sottili del sottotitolo; gli altri oggetti mantengono il generatore precedente.

Ugello 220 °C, piano 60 °C, limite volumetrico 5 mm³/s, ponti 25 mm/s, flusso filamento 0,98 / processo 0,97, PA 0,04: stessi valori iniziali R24, non una calibrazione della bobina. Unico avviso: `bed_temperature_too_high_than_filament`, 1000C001, soglia software PLA 45 °C rispetto al piano 60 °C. Per questa preparazione mantenere lo sportello anteriore aperto. Piano pulito, materiale asciutto e canale CANVAS della bobina correttamente assegnato. Il colore grafite delle anteprime e indicativo.

Conservare gli orientamenti salvati: scocca sulla base, cartucce sui piedi, tetto capovolto con esterno sul PEI, perno piatto e fermo sul fondo. Rimuovere brim e fili dopo il raffreddamento, senza forzare o carteggiare automaticamente gli accoppiamenti. Il logo viene stampato insieme al tetto: non va incollato.

## Prove e assemblaggio

I provini R24 invariati sono inclusi in `stampa/provini_R24_invariati/`. Se non sono gia stati verificati fisicamente, provare prima piede, fermo, aperture per i tre SSD e chiusura. Il nuovo logo non richiede una nuova prova di accoppiamento. La finitura reale delle scritte rimane da vedere sul primo tetto stampato.

Ogni cartuccia e dedicata a T7, T7 Shield o T9, con lo stesso piede nei tre slot. T7 85 × 57 × 8 mm, Shield 88 × 59 × 13 mm, T9 88 × 60 × 14 mm sono gabarit nominali. Canali rispettivamente 8,4 × 57,5, 13,4 × 59,5, 14,4 × 60,5 mm: 0,2 mm di gioco per lato e 0,5 sopra; piede 0,2 mm per lato e 0,2 verticali sulle rampe. Queste quote restano da provare sui dispositivi reali.

Caricare il disco da dietro nella cartuccia estratta, con cavo scollegato. Calare la cartuccia 6 mm piu avanti, arretrarla sotto i fermi, inserire il fermo frontale comune dalla presa alta. Collegare i cavi, inserire il tetto dal retro e bloccare il perno da sotto: gira 90° e abbassalo 1,1 mm nella sede. Per aprire alza, ruota e sfila il perno, poi arretra il tetto (circa 11 cm liberi dietro). Togli il fermo frontale, avanza la cartuccia di 6 mm e sollevala, senza fare leva sulle cornici. Uso verticale sulla scrivania; nessun serraggio per trasporto capovolto.

Nessuna ferramenta o colla interna. Servono i quattro piedini trasparenti propri: sedi Ø10,5 profonde 0,65 mm, con almeno 5 mm di aria sotto il fondo. Non ostruire feritoie inferiori/superiori. Raffreddamento passivo, stabilita, durata del PLA e temperature degli SSD (soprattutto il centrale) rimangono da verificare sul primo kit. Nessuna CFD o prova fisica dichiarata.

## Controlli e sorgenti

Sette parti STEP/STL riaperte: scala mm, solido unico, mesh chiusa, normali coerenti, volume positivo, assenza di facce degeneri/duplicate e screening autointersezioni (esclude facce con vertici condivisi). Sei parti e tutte le superfici originali del tetto identiche a R24. Solo i tredici glifi sono aggiunti all'esterno. Assieme riaperto: dieci solidi inclusi i tre SSD di riferimento. Verificati gli ingombri con i nove abbinamenti modello/slot; la cinematica R24 e conservata per identita geometrica delle superfici funzionali.

Entrambi i progetti riaperti e verificati per unita, trasformazioni, profili, override, quantita, brim e area utile. Percorsi e primi strati visionati; tutti i tredici glifi risultano nel G-code di ciascun progetto, con proiezione di controllo in `verifiche/slicing/*/LOGO_PERCORSI.png`. Questo non prova la leggibilita o la finitura del pezzo reale.

Python 3.11, CadQuery 2.8.0 / OCP 7.9.3.1.1; dipendenze in `sorgenti/requirements.txt`. `genera.py` aggiunge il logo; `geometria_r24.py`, `involucro_r22.py` e `base_r15.py` conservano le funzioni parametriche precedenti. Parametri del marchio in `logo_posteriore`; gli altri valori sono quelli della R24. Asset e contorni approvati inclusi, con hash.

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/verifica_logo.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Lo slicing richiede l'app ElegooSlicer installata. Dopo modifiche rigenerare tutti i derivati e ripetere la revisione visiva prima di eseguire `consegna.py`. `CAD/riferimenti_R24/` contiene solo riferimenti di confronto, non file da stampare. Il pacchetto finale e `BAY_R25_LOGO_ENGINEERING_PLA_BASIC.zip`.
