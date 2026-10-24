# Verifiche R15 PLA BASIC

**Pronto per la stampa del prototipo nominale. Verifiche digitali completate; tenuta reale e rigidezza da verificare sulla nuova stampa.**

Scocca R14 invariata: confronto sui STEP riaperti con differenza simmetrica inferiore a 0,00001 mm³. Anche tetto esterno e griglia conservati. Tutti i file hashati della consegna R14 verificati e conservati.
Alette da 8 a 9 mm: gioco di 0,3 mm a ciascuna estremita della finestra larga 9,6 mm. Pattini con interferenza nominale di 0,15 mm per lato verso la parete interna. La forma libera interseca intenzionalmente la scocca soltanto nei due pattini. Inviluppo con linguette traslate all’interno di 0,15 mm privo di collisioni: controllo geometrico, non simulazione della deformazione o della forza.
Culle a U bilaterali per T7 e Shield, due per modello. Due collari pieni collegati da una base: il dispositivo entra fra le sponde. Scasso centrale attorno alle guide R14, con 0,3 mm di gioco per lato in X e Y; nessuna lamina sottile tra Shield e guida. Base 1,2 mm, collari profondi 3,7 mm, pareti minime Shield 2,5 mm. Appoggio inferiore geometrico 115,2 mm² per culla. Le culle calzano dall’alto senza viti o adesivi; non promettono un bloccaggio elastico o resistenza agli urti.
Culle e SSD T7/Shield centrati rispetto alla sede. Aperture 9 e 13,6 mm: giochi totali nominali sui dischi rispettivamente 1 e 0,6 mm. T9 direttamente nelle guide da 15 mm. Base culle alza T7 e Shield di 1,2 mm; bordo inferiore coda da quota 56 a 57 mm per conservare almeno 3 mm sopra l’ingombro USB nominale.
Quattro STL e otto STEP singoli riaperti. Solido unico valido, scala millimetrica, mesh chiuse, normali coerenti, volumi positivi; nessuna faccia degenere/duplicata e nessuna coppia rilevata dallo screening di autointersezioni, che esclude triangoli con vertici condivisi. Nessuna riparazione automatica.
Nove casi modello/slot, 27 disposizioni nominali, estrazione SSD e culle a quote campionate senza collisioni. Assieme STEP di nove solidi compresi tre gabarit non stampabili. Interferenza intenzionale dei soli pattini documentata separatamente.
Ingombro chiuso 90 × 109,4 × 86 mm. Nove ingombri USB 20 × 20 × 50 mm senza collisioni; margine minimo sopra USB 3.3 mm. Posizione centrale e dimensioni spinotti nominali, non misurate. Gioco assiale dietro Shield/T9 2 mm.
Aree geometriche: fondo 30.17 cm², tetto 37.91 cm², corridoi verticali conservativi con tre T9 15.19 cm². Fianchi 6.96 cm² ciascuno; retro aperto 43.68 cm² senza spine. Non sono portate d’aria o potenze dissipabili.
Corridoi verticali con SSD e culle installate: controllate tutte le 27 disposizioni; minimo 14.51 cm². Valutazione geometrica in proiezione, senza misura di portata.
Due progetti alternativi: RICAMBI con cinque pezzi su un piatto, KIT_COMPLETO con sei pezzi su un piatto. Non occorre stampare entrambi. ElegooSlicer app 1.5.3.5 / motore 2.4.2, ECC2 Combo, ugello 0,4, PEI testurizzato, PLA BASIC, 220/60 °C, strati 0,2 mm, quattro pareti, gyroid 20%, limite 5 mm³/s, brim 5 mm, supporti disattivati. Fuzzy disattivata; S9 0,4 mm invariato; nessun provino.
3MF nativi riaperti per ID e percorsi XML; geometria, profili e G-code dello slicer incorporati verificati. Unita millimetriche, trasformazioni, ingombri con brim e zona esclusa controllati. Tutti gli strati nelle tavole d’insieme e dettagli funzionali esaminati; screening di nuove isole registrato nelle analisi. Piccoli ponti su sedi piedini, feritoie e agganci controllati. Percorsi S e 9 verificati nel kit completo, compensando offset estrusore Y 1,5 mm.
Avviso mantenuto: bed_temperature_too_high_than_filament (1000C001), confronto piano 60 °C / soglia software PLA 45 °C. Preparazione: sportello anteriore aperto, evitare calore accumulato in camera. Profilo compatibile e dati del produttore archiviati; valori iniziali non calibrati sulla bobina.

| Alternativa | Strati | PLA stimato | Tempo stimato |
| --- | ---: | ---: | --- |
| BAY_R15_01_RICAMBI | 145 | 34.78 g | 2h 7m 8s |
| BAY_R15_02_KIT_COMPLETO | 415 | 145.20 g | 8h 24m 36s |

Stime dello slicer con brim; alternative da non sommare. Nessun invio alla stampante.

La segnalazione dell’utente descrive scarsa pressione del tetto e flessione degli inserti precedenti. Questa revisione risponde con nuove geometrie; nessuna prova fisica R15, misura della forza, verifica di fatica/creep o test termico e stata eseguita. SSD/cavi/piedini reali non misurati. Non si dichiara risolto fisicamente il problema prima di provare i ricambi.
