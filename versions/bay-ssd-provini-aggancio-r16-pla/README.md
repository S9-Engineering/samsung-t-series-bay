# R16 — provino rapido per l’aggancio del tetto

**Pronto per la stampa del provino.** Il problema confermato dall’utente è la scarsa sporgenza del dente nella finestrella. Non viene ristampato né modificato il tetto completo: si prova una traversa con due alette direttamente sulla scocca esistente.

## Prima prova: solo III

Aprire **[BAY_R16_01_PROVINO_III_ECC2_PLABASIC.3mf](stampa/progetti_ElegooSlicer/BAY_R16_01_PROVINO_III_ECC2_PLABASIC.3mf)**.

Un solo pezzo su un piatto, **4,61 g di PLA BASIC, 18 min 03 s stimati dallo slicer**, brim e supporti compresi. Sul pezzo sono incise tre tacche `III`.

Il dente passa da **0,6 a 1,0 mm di sporgenza nominale per lato**. La parte superiore diventa una **spalla orizzontale di ritenuta**; la rampa inferiore facilita l’ingresso. Lunghezza e radice dell’aletta restano quelle della R15. Il dente triangolare precedente ha anche una rampa di uscita: questa prova serve a distinguere la sola maggiore sporgenza da un aggancio con spalla.

**Prima del montaggio rimuovere il brim e i due piccoli supporti accanto alle alette**, senza assottigliare i denti o arrotondare la spalla. I supporti sono già impostati nel progetto; crescono dalla traversa e sono accessibili dai lati. La rimozione reale e la finitura della spalla restano da verificare sulla stampa.

## Confronto facoltativo

[BAY_R16_02_CONFRONTO_ECC2_PLABASIC.3mf](stampa/progetti_ElegooSlicer/BAY_R16_02_CONFRONTO_ECC2_PLABASIC.3mf) contiene tutti e tre i provini sullo stesso piatto: **12,56 g, 42 min 57 s** stimati, brim e supporti inclusi. Include già il III; non serve stampare entrambi i progetti.

| Tacche incise | Profilo del dente | Sporgenza per lato | Distanza nominale fra punte dei denti | Gioco verticale nell’inviluppo geometrico |
| --- | --- | ---: | ---: | ---: |
| I | Triangolare, riferimento R15 | 0,60 mm | 85,20 mm | 0,55 mm |
| II | Triangolare più sporgente | 1,00 mm | 86,00 mm | 0,39 mm |
| III | Spalla di ritenuta | 1,00 mm | 86,00 mm | 0,20 mm |

Le quantità sono **una copia per variante**. I e II non richiedono supporti; III ha supporti normali aderenti al profilo (`snug`), due strati di interfaccia e distacco verticale da 0,2 mm. Il progetto contiene le impostazioni specifiche per oggetto. Se si importa soltanto lo STL del III, occorre reimpostare i supporti; per questa prova usare il 3MF salvato.

## Quote da controllare

- Traversa: **90 × 14 × 3 mm**; ingombro orientato per stampa **90 × 14 × 15 mm**.
- Due alette: **lunghe 12 mm, larghe 9 mm, spesse 1,2 mm**, con lo stesso interasse e le stesse radici del tetto R15.
- Scocca nominale: pareti 3 mm, spazio interno fra pareti 84 mm; finestrelle **9,6 × 3 mm**, bordo superiore 9 mm sotto l’appoggio del tetto.
- III: spalla 9,2 mm sotto l’appoggio; gioco verticale nominale 0,2 mm. Fra le punte dei denti: **86 mm**, da misurare sotto la traversa, alla quota dei denti.
- Pattini di precarico conservati: 0,15 mm nominali per lato. La distanza libera fra le estremità dei pattini è 84,3 mm.

L’inviluppo con alette traslate di 0,15 mm verso l’interno lascia una penetrazione laterale geometrica di 0,45 mm per I e 0,85 mm per II/III. Queste sono quote del CAD, **non forza misurata né simulazione della flessione**. Le misure reali della scocca e dei provini vanno confrontate dopo la stampa.

## Come provarlo

1. Usare la scocca vuota, senza tetto. Posizionare la traversa sopra le due finestrelle laterali, come nell’[anteprima di montaggio](anteprime/03_R16_MONTAGGIO.png).
2. Premere vicino alle estremità finché la traversa appoggia al bordo del case. Controllare che entrambi i denti raggiungano le finestrelle e scattino verso l’esterno.
3. Trattenere il case e tirare leggermente la traversa verso l’alto. Annotare se si sfila subito, se tiene da un solo lato oppure se rimane agganciata su entrambi i lati. Il III deve poi potersi togliere premendo le due alette verso l’interno, senza fare leva forzata sul case.
4. Ripetere qualche apertura e chiusura; osservare gioco, ritorno delle alette e segni di deformazione. Confrontare I/II/III solo se serve capire quale modifica produce la presa.

Se un dente non entra nella finestra, annotare se rimane sopra o sotto il foro e quale lato è interessato: è un problema di posizione o appoggio diverso dalla sola sporgenza. Se il III aggancia e si sgancia correttamente, la geometria potrà essere trasferita al tetto completo in una revisione successiva.

La traversa piena è più rigida della griglia del tetto. Riproduce radici, distanza e orientamento delle alette e consente una prova locale sul case reale; **non certifica la forza di estrazione o la durata del tetto intero**. Non è stata eseguita una prova fisica R16 e non è stata avviata alcuna stampa.

## Stampa e file

Configurazione già confermata: **ELEGOO Centauri Carbon 2 Combo, ugello 0,4 mm, PEI testurizzato, ELEGOO PLA BASIC**, un colore disponibile. Colori delle anteprime solo esplicativi. Fuzzy Skin disattivata.

Orientamento già salvato: faccia esterna della traversa sul piano, alette verso l’alto, come il tetto R15. Profilo **0,20 mm, quattro pareti, gyroid 20%, brim 5 mm, 220/60 °C, portata massima 5 mm³/s**, stampa per strato, nessuna torre. Sono parametri iniziali del profilo compatibile, non una calibrazione della bobina.

Slicing effettivo con **ElegooSlicer app 1.5.3.5 / motore 2.4.2**, 75 strati per ciascuna alternativa. I due 3MF sono progetti nativi con geometria, profili, impostazioni per oggetto e G-code generato dallo slicer incorporato. Controllati riapertura, unità, trasformazioni, ingombri, primo strato e percorsi. Avviso conservato `bed_temperature_too_high_than_filament` (piano 60 °C, soglia software PLA 45 °C): **stampare con sportello anteriore aperto**, evitando accumulo di calore in camera.

- [Tre varianti](anteprime/01_R16_PROVINI.png)
- [Sezioni dei denti e quote](anteprime/02_R16_SEZIONI.png)
- [Montaggio sulla scocca](anteprime/03_R16_MONTAGGIO.png)
- [Rapporto digitale](verifiche/RAPPORTO_VERIFICHE.md)

`stampa/STL/` contiene i tre pezzi singoli già orientati; `CAD/` i STEP di assieme e stampa. I due STEP `RIFERIMENTO_PARETE_*_NON_STAMPARE` servono soltanto a documentare le finestre e non sono sul piatto. Sorgenti parametrico e dipendenze in `sorgenti/`. R14/R15 e tutti i loro file sono conservati.

## Rigenerazione

Python 3.11, CadQuery 2.8.0 / OCP 7.9.3.1.1, dipendenze esatte in `sorgenti/requirements.txt`. Dalla cartella di questo progetto:

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py --solo-iii
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Su un ambiente nuovo creare una venv e installare i requirements. Il confronto con la R15 usa i file finali nella cartella sorella quando disponibili; il modello può essere generato autonomamente dai parametri. Dopo una rigenerazione rivedere le nuove immagini dei percorsi, registrare gli hash e la revisione in `verifiche/revisione_visiva.json`, quindi eseguire `sorgenti/consegna.py`. La generazione delle immagini non costituisce la loro revisione.
