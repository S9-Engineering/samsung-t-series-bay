# Stato aggiornato — kit completo R22 sospeso

Le sedi interne richiedono riprogettazione dopo il nuovo riscontro utente. Il rapporto seguente conserva le verifiche digitali precedenti e non qualifica il kit completo per una nuova stampa. Il provino riguarda il solo tetto. Vedi REVISIONE_SEDI_INTERNE.json.

---

# Verifiche R22 — guide interne e fermo nascosto

**Pronto per la stampa del prototipo con prova preliminare. Non stampato o verificato fisicamente.**

Nuova scocca necessaria; il tetto scorre da dietro su due guide lunghe 82 mm, radice 3 mm e rampe 45 gradi. Il perno rigido si inserisce da sotto, ruota di 90 gradi e si abbassa 1,1 mm nella sede trasversale. Nessuna molla, linguetta o paletta esterna. Il perno non puo ruotare nominalmente finche non viene rialzato.
Sagoma nominale chiusa 90 x 109,4 x 86 mm, incluso S9, esclusi cavi e piedini. Nessun componente supera i lati X0/90. Pattern laterale e spigoli R15 conservati; chiuse le finestrelle dei vecchi ganci. Feritoie superiori accorciate ai lati per lasciare margini 12 mm sopra le guide.
Sette tipi STEP, STEP orientati e STL riaperti: un solido/componente ciascuno, scala millimetrica, volume positivo, normali coerenti, mesh chiuse, zero facce degeneri e duplicate, nessuna coppia nello screening autointersezioni che esclude triangoli con vertici condivisi. Nessuna riparazione automatica. Assieme STEP riaperto: dieci solidi, incluse le tre sagome SSD non stampabili e quattro inserti.
Cinematica nominale con corpi rigidi: 35 offset del tetto da 101 a 0 mm; 31 posizioni di ingresso del perno, 19 angoli e 12 quote di assestamento. Verificate le interferenze attese alla battuta anteriore, durante il tentativo di sollevamento, arretramento, estrazione e rotazione del perno abbassato. Il moto e campionato: non e una dimostrazione continua o una prova di forze e durata.
Provino con guide da 20 mm, stessa larghezza e stesse superfici funzionali; confronto geometrico passato. La finestra centrale e la coda alleggerita riducono il consumo lontano dal fermo. La prova non dimostra l attrito delle guide lunghe o la manovrabilita con tutti i dispositivi collegati.
Nove abbinamenti SSD/slot verificati, scorrimento del tetto e azionamento del perno con ingombri USB nominali 20 x 20 x 50 mm. Distanza minima campionata perno/USB 1,388 mm. Gli inserti T7 e Shield conservano la geometria R15; assenza di interferenze nominali con SSD e scocca. Quote porte e connettori reali ancora da misurare o provare.
File precedenti conservati e controllati con gli hash: {'bay-ssd-universale-r15-pla-supporti-u': 134, 'bay-ssd-tetto-r19-pla-alette-r18': 54, 'bay-ssd-tetto-r20-pla-senza-tagli': 57, 'bay-ssd-tetto-r21-baionette-rigide': 69}.
Progetti nativi ElegooSlicer app 1.5.3.5 / motore 2.4.2. Entrambi su un piatto: provino tre oggetti, kit completo sette. Controllati mm, scale, trasformazioni, componenti, normale orientamento, brim 5 mm, distanze e zona esclusa. Configurazione ECC2 Combo monocolore, ugello 0,4, PEI testurizzato, ELEGOO PLA BASIC, 220/60 C, strato 0,20, quattro pareti, 20% gyroid con override perno 100% rettilineo, limite 5 mm3/s. Valori di partenza, non calibrazione fisica.
Tutti i 145 strati del provino e 415 del kit visionati, oltre a ingrandimenti di guide, camera, perno, primo strato e ponti. Perno piatto con asse parallelo al piano, sezioni continue. Guide a crescita progressiva senza isole nuove rilevate (screening raster). Nessun percorso di supporto. Camera aperta lateralmente, apertura 8 mm; fori da controllare sul provino.
Le maggiori lunghezze registrate come Internal Bridge comprendono superfici sopra il gyroid: una linea lunga non equivale a una campata libera della stessa lunghezza. Visionati strato sottostante e chiusura; i ponti delle sedi piedini appartengono alla geometria precedente conservata.
Unico avviso: bed_temperature_too_high_than_filament, 1000C001 (piano 60 C rispetto a soglia software PLA 45 C). Preparazione: sportello anteriore aperto. Nessuna Fuzzy Skin o torre di spurgo.

- PROVA: 22.70 g / 1h 19m 32s, brim incluso.
- COMPLETO: 159.67 g / 9h 10m 40s, brim incluso.

Nessuna stampa inviata alla macchina. Devono ancora essere verificati calzata e attrito, accesso alle dita, tenuta, durata, comportamento dei ponti reali, cavi, temperature SSD e comportamento del PLA nel tempo. La scelta di guide rigide elimina la flessione nominale delle vecchie alette; non costituisce una certificazione di resistenza.
