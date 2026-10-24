# Verifiche R21 — perni rigidi a quarto di giro

**Preparazione digitale completata. L’incastro reale deve essere verificato sulla traversa di prova prima del tetto completo.**

Il riscontro utente R19 segnala alette ancora troppo deboli. R21 abbandona i bracci elastici: tetto con due blocchi di ricezione e due perni rimovibili, inseriti orizzontalmente e ruotati di 90 gradi. Nessuna ferramenta. Tutto PLA BASIC, senza supporti di stampa e con riempimento rettilineo pieno al 100%.
Sorgenti ed export riaperti: tre tipi di oggetto, un solido/componente per STL, millimetri, normali coerenti, volume positivo, zero facce degeneri o duplicate e nessuna coppia nello screening autointersezioni (triangoli con vertici condivisi esclusi). Nessuna riparazione automatica.
Scocca esistente R15 non modificata. Verificati sette livelli di discesa del tetto, 23 posizioni di inserimento per lato, rotazione da 0 a 90 gradi ogni 5 gradi e interferenze di ritenuta dei due perni in posizione chiusa. Dopo rotazione il traversino non passa dal foro; alzata del perno contro la finestra e del tetto contro il perno producono le interferenze attese. Sono verifiche cinematiche con parti rigide, non prove di carico o forza.
Nove combinazioni modello SSD/slot controllate. Distanza minima nominale perni-SSD 1.30 mm; distanza minima dagli ingombri USB 20 x 20 x 50 mm 3.30 mm. Supporti del provino e del tetto confrontati geometricamente: identici. Vecchi file conservati: {'R15': 134, 'R18': 47, 'R19': 54, 'R20': 57}.
3MF nativi riaperti indipendentemente: ciascuno un piatto con tre oggetti, unità e trasformazioni valide, brim 5 mm e ingombri entro il volume utile e fuori dalla zona esclusa. App ElegooSlicer 1.5.3.5 / motore 2.4.2; configurazione ECC2 Combo 0,4 mm, PEI testurizzato, ELEGOO PLA BASIC, 220/60 °C, strato 0,20 mm, quattro pareti, 100% rettilineo, limite 5 mm³/s. Parametri iniziali compatibili, non calibrazione della bobina.
Percorsi completi dei due lavori visionati: 88 strati del provino e 145 del tetto, più dettagli di perni, fori nei supporti rigidi, primo strato, chiusure e ponti. Perni stampati piatti con gambo continuo. Ponti dei fori circa 4,8 mm; interni ispezionabili dai due lati. Zero candidati di nuove isole nello screening raster. Assenza di percorsi di supporto confermata.
Avviso conservato bed_temperature_too_high_than_filament (1000C001), piano 60 °C contro soglia software PLA 45 °C: stampare con sportello anteriore aperto. Nessun altro avviso modello. Nessuna Fuzzy Skin o torre di spurgo.

- PROVA: 6.98 g / 25m 1s, brim incluso.
- TETTO: 35.26 g / 1h 56m 12s, brim incluso.

La baionetta non ha un fermo angolare elastico: la posizione chiusa e indicata dalla paletta verticale; per estrarre serve riallinearla orizzontalmente. Cattura geometrica verificata, resistenza a rotazioni accidentali e durata non provate.
Nessuna stampa avviata. Tolleranze, ponte reale, tenuta e cicli di apertura devono passare la verifica fisica sul provino.

Riferimento progettuale consultato: [Formlabs, design degli incastri stampati](https://formlabs.com/eu/blog/designing-3d-printed-snap-fit-enclosures/). La dipendenza dei cantilever da materiale, deformazione e orientamento motiva il cambio di meccanismo; la soluzione a perni e una scelta di questo progetto, non una prestazione certificata dalla fonte.
