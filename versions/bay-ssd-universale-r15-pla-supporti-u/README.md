# Bay SSD S9 — R15, PLA BASIC

**Revisione da stampare per correggere tetto e inserti della R14.** Scocca R14 riutilizzabile, verificata identica nel CAD. Esterno monolitico, spigoli netti, feritoie orizzontali e S9 in rilievo conservati.

**Stato: pronto per la stampa del prototipo nominale.** Export e slicing verificati; presa delle nuove alette, rigidezza delle culle e temperature restano da provare fisicamente. Nessuna stampa avviata.

## Apri questo file se hai già la scocca

[**BAY_R15_01_RICAMBI_ECC2_PLABASIC.3mf**](stampa/progetti_ElegooSlicer/BAY_R15_01_RICAMBI_ECC2_PLABASIC.3mf): **un piatto, cinque pezzi** — tetto con coda, due culle T7 e due culle Shield. Stima reale dello slicer **34,78 g, 2 h 07 min 08 s**, brim incluso.

Se devi ristampare anche il corpo, usa invece [BAY_R15_02_KIT_COMPLETO_ECC2_PLABASIC.3mf](stampa/progetti_ElegooSlicer/BAY_R15_02_KIT_COMPLETO_ECC2_PLABASIC.3mf): **un piatto, sei pezzi**, **145,20 g, 8 h 24 min 36 s**. Sono due alternative, non due piatti necessari: **non stampare entrambi**.

I 3MF sono veri progetti ElegooSlicer: geometria, profili, disposizione e G-code generato dallo slicer incorporato. Sono riaperti e controllati. Non sono stati inviati alla macchina. Non aggiungere STL o altri oggetti al progetto prima della stampa se vuoi conservare il controllo di questa disposizione.

## Modifiche rispetto alla R14

- **Alette:** larghezza da 8 a 9 mm, con 0,3 mm liberi per estremità nelle finestre esistenti da 9,6 mm. Due piccoli pattini sporgono nominalmente di **0,15 mm per lato** rispetto alla parete interna: sono le zone destinate a dare pressione. Radice da 1,2 mm e lunghezza da 12 mm conservate. Il dente mantiene la ritenuta nella finestra.
- **Inserti a U:** due collari pieni con sponde bilaterali, collegati da un fondo comune. Il disco entra nella U. La parte centrale libera le guide della scocca esistente: nessuna lamina sottile sul fianco dello Shield. Pareti minime Shield 2,5 mm; fondo 1,2 mm. Gli inserti calzano sulle sedi dall’alto con 0,3 mm di gioco per lato; la stabilità è affidata alla forma e all’appoggio, senza viti o adesivi.
- **Coda posteriore:** bordo inferiore alzato di 1 mm, da Z56 a Z57, per compensare il fondo delle culle che alza T7/Shield di 1,2 mm. Ingombro esterno massimo invariato. Cavi esterni all’enclosure.

Il precarico è una quota di progetto, non una forza misurata. La forma libera del coperchio interseca intenzionalmente il case solo nei due pattini; il controllo con linguette traslate verso l’interno di 0,15 mm verifica un inviluppo geometrico. Non simula la flessione effettiva, il ritorno elastico o la durata del PLA. La correzione risponde al difetto segnalato, ma il risultato fisico della R15 non è ancora verificato.

## Componenti e quote

| Pezzo | Quantità kit | Nei ricambi | Orientamento salvato |
| --- | ---: | ---: | --- |
| scocca_R15 | 1 | 0 | Fondo sul piano, apertura in alto |
| coperchio_R15 | 1 | 1 | Faccia esterna del tetto sul piano, alette/coda verso l’alto |
| inserto_T7_R15 | 2 | 2 | Fondo della U sul piano, sponde verso l’alto |
| inserto_Shield_R15 | 2 | 2 | Fondo della U sul piano, sponde verso l’alto |

Ingombro chiuso **90 × 109,4 × 86 mm**, logo compreso, piedini esclusi. Scocca profonda 101 mm, tetto 109 mm. Le sedi restano universali: T9 diretto nelle guide da 15 mm; T7 con due culle da 9 mm; Shield con due culle da 13,6 mm. Giochi totali nominali sui dischi: 1 / 0,6 / 1 mm rispettivamente T7 / Shield / T9. Tutti i modelli possono occupare ognuno dei tre slot.

SSD nominali, non misurati sui dispositivi dell’utente: T7 85 × 57 × 8 mm; Shield 88 × 59 × 13 mm; T9 88 × 60 × 14 mm. Port USB al centro nominale della faccia corta. Ingombro riservato spinotto **20 × 20 × 50 mm**, non uno standard certificato o una misura del cavo. Margine verticale minimo **3,3 mm** sopra questo ingombro, 2 mm dietro la fine di Shield/T9. Inserire i cavi dal retro aperto; scollegarli prima di estrarre i dischi.

Nessuna ferramenta e nessun adesivo interno. Restano quattro sedi per piedini commerciali in gomma trasparente, Ø10,5 mm profonde 0,65 mm; piedini non inclusi, dimensioni da confermare. Per ottenere 5 mm liberi sotto il fondo servono piedini che sporgano di 5 mm dalla scocca (altezza totale almeno 5,65 mm se inseriti fino al fondo della sede).

## Stampa

Configurazione confermata dall’utente: **ELEGOO Centauri Carbon 2 Combo, ugello 0,4 mm, PEI testurizzato, ELEGOO PLA BASIC**. Un solo filamento; colore non specificato. Colori delle culle nelle anteprime solo esplicativi. Fuzzy Skin disattivata; nessun provino. S9 invariato, largo 14 mm e in rilievo di 0,4 mm.

Profili compatibili ECC2 inclusi e verificati nel 3MF: **strato 0,20 mm, quattro pareti, gyroid 20%, brim esterno 5 mm, supporti disattivati, stampa per strato**, nessuna torre di spurgo. PLA a **220 °C, piano 60 °C**, portata limitata a **5 mm³/s**. Valori iniziali del profilo, non una calibrazione della bobina. Gli orientamenti sono già salvati e il brim è compreso nelle verifiche di ingombro.

ElegooSlicer **app 1.5.3.5 / motore 2.4.2**. Il profilo conserva l’avviso `bed_temperature_too_high_than_filament` (1000C001): piano a 60 °C rispetto alla soglia software PLA a 45 °C. **Stampare con sportello anteriore aperto**, evitando accumulo di calore nella camera. Soglia originale mantenuta; non eliminata per nascondere l’avviso. Riferimento filamento: [scheda ufficiale ELEGOO PLA BASIC](https://www.elegoo.com/products/pla-basic-filament-1-75mm-colored-1kg), parametri archiviati dal profilo specifico.

Dopo il raffreddamento del piano rimuovere il brim e solo le bave eventuali sul bordo inferiore. Non carteggiare i pattini di precarico prima di provare il coperchio. Le culle si stampano dritte sulla loro base: non sono gli spessori capovolti della R14.

## Montaggio e prova

1. Togliere il coperchio e i precedenti inserti. Conservare la scocca.
2. Calzare due culle del modello corretto sulle due guide della sede prescelta: il vano centrale delle culle circonda le guide esistenti. Fondo appoggiato sulla seduta. La U rimane aperta verso l’alto.
3. Inserire T7/Shield tra le due sponde; T9 resta diretto nelle sue guide. I dischi devono rimanere verticali con gioco, senza serraggio.
4. Collegare manualmente i cavi da dietro. Posare il tetto e premere sopra gli agganci fino alla presa. Per rimuoverlo, flettere con delicatezza le due alette verso l’interno dalle finestre laterali e sollevare il tetto.
5. Verificare che le culle non si ribaltino, che il tetto non balli e che si sganci senza forzare. Eventuali scostamenti della stampa richiedono la correzione dei parametri e una nuova esportazione, non una promessa di presa già dimostrata.

Confrontare poi l’uso dentro/fuori dal bay nelle condizioni reali, specialmente sul disco centrale e agli appoggi in PLA. I corridoi verticali geometrici restano aperti in tutte le 27 disposizioni nominali, con minimo 14,51 cm² includendo le culle (15,19 cm² con tre T9 diretti). Aperture conservate e geometria libera non certificano dissipazione, temperature o deformazione nel tempo.

## Anteprime e verifiche

- [Culle a U, isolate e sulla guida R14](anteprime/10_R15_CULLE_U.png)
- [Sezione delle alette con precarico](anteprime/11_R15_ALETTE.png)
- [Interno con tre dispositivi](anteprime/02_R15_INTERNO.png)
- [Piatto dei cinque ricambi](anteprime/04_R15_PIATTI.png)
- [Rapporto delle verifiche](verifiche/RAPPORTO_VERIFICHE.md)
- [Stato della consegna](verifiche/STATO_CONSEGNA.json)

Quattro STL e otto STEP singoli riaperti, oltre all’assieme con tre gabarit SSD non stampabili. Controlli su solidi/componenti, scala, mesh chiuse, normali, volume, facce degeneri/duplicate e screening autointersezioni. Nove abbinamenti modello/slot, 27 disposizioni nominali, estrazione verticale campionata di SSD e culle. Il precarico intenzionale è distinto dalle collisioni indesiderate. 3MF verificati per unità, componenti, trasformazioni, profili e ingombri; slicing reale con controllo dei percorsi di tutti gli strati e ingrandimenti funzionali. Limiti dettagliati nel rapporto: nessuna prova fisica R15, simulazione elastica o misura termica.

## Sorgenti e rigenerazione

CAD parametrico CadQuery 2.8.0 / OCP 7.9.3.1.1, Python 3.11; dipendenze in `sorgenti/requirements.txt`. Parametri separati per scocca, slot, culle a U, precarico, aria e coda in `sorgenti/parametri.json`. Loghi approvati PNG/SVG in root. I percorsi sono relativi alla cartella del progetto.

Dalla cartella R15, con il runtime dedicato già disponibile nel workspace:

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/confronta_revisioni.py
"$PYTHON" -B -u sorgenti/stampa.py --slice
"$PYTHON" -B -u sorgenti/anteprime.py
"$PYTHON" -B -u sorgenti/revisiona_percorsi.py
```

Il confronto richiede la consegna R14, conservata separatamente. Per un ambiente nuovo creare una venv Python 3.11 e installare i requirements. Dopo una rigenerazione, rivedere le nuove tavole dei percorsi e registrare hash e riscontro in `verifiche/revisione_visiva.json`; solo allora eseguire `sorgenti/consegna.py`. Generare le immagini non equivale a controllarle. L’archivio finale contiene sorgenti, STEP, STL, progetti nativi, anteprime, report e manifest SHA256; tutte le revisioni precedenti sono conservate.
