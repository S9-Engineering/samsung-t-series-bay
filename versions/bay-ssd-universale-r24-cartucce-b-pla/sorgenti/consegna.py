"""Audit consegna R24: richiede prove geometriche, slicing e revisione visiva."""
import json,zipfile,hashlib
from pathlib import Path
import genera as g
from native_3mf import validate
ROOT=g.ROOT
def read(n):return json.loads((ROOT/n).read_text())
def main():
 m=read('verifiche/manifest.json');geo=read('verifiche/geometria.json');a=read('verifiche/anteprime.json');r=read('verifiche/revisione_visiva.json');jobs=read('verifiche/slicing/riepilogo.json')['jobs']
 assert m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json') and m['source_sha256']==g.sha(ROOT/'sorgenti/genera.py')
 assert geo['source_manifest_sha256']==a['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 assert len(m['parts'])==15 and m['complete_kit_parts']==7 and not m['elastic_latch']
 for p in m['parts']:
  q=next(q for q in geo['parts'] if q['name']==p['name']);assert q['closed'] and q['components']==1 and q['winding'] and q['positive_volume']
  assert q['degenerate_faces']==q['duplicate_faces']==q['self_intersections']['intersection_pairs']==0
  for k in ['stl','step','print_step']:assert g.sha(ROOT/p[k])==q[k+'_sha256']
 assert len(geo['ssd_checks'])==len(geo['cartridge_retention'])==9 and len(geo['cartridge_paths'])==171
 assert len(geo['roof_paths'])==35 and len(geo['key_paths'])==62 and geo['roof_R22_geometrically_unchanged'] and geo['coupon_functional_surfaces_match']
 assert all(v>0 for q in geo['cartridge_retention'] for v in q['blocking_overlap_mm3'].values())
 assert geo['assembly']['sha256']==g.sha(ROOT/'CAD/ASSIEME_R24_NON_STAMPARE.step') and geo['assembly']['solids']==10
 assert len(a['outputs'])==6 and a['outputs']==r['cad_image_hashes']
 for n,h in a['outputs'].items():assert g.sha(ROOT/n)==h
 for j in jobs:
  mode=j['mode'];assert g.sha(ROOT/j['project'])==j['project_sha256']==r['projects'][mode]
  assert g.sha(ROOT/j['geometry_source'])==j['geometry_sha256'] and g.sha(ROOT/j['gcode'])==j['gcode_sha256']
  for n,h in j['profile_hashes'].items():assert g.sha(ROOT/'slicer'/n)==h
  check=validate(ROOT/j['project'],j['items']);assert check['printable_count']==dict(INTERNI=6,TETTO=3,COMPLETO=7)[mode] and check['modifier_count']==0
  for it in j['items']:
   native=next(q for q in check['parts'] if q['name']==it['name']);source=next(q for q in geo['parts'] if q['name']==it['part']);assert abs(native['volume_mm3']/source['volume_mm3']-1)<1e-4
  assert set(j['images'])==set(r['image_hashes'][mode])
  for n,h in r['image_hashes'][mode].items():assert g.sha(ROOT/n)==h
  analysis=read(f'verifiche/slicing/{mode}/analisi.json');assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations'] and analysis['new_wall_islands']['candidate_count']==0
  with zipfile.ZipFile(ROOT/j['project']) as z:
   settings=json.loads(z.read('Metadata/project_settings.config'))
   for k,v in dict(printer_model='Elegoo Centauri Carbon 2',nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',wall_loops='4',sparse_infill_density='20%',sparse_infill_pattern='gyroid',brim_width='5',filament_max_volumetric_speed=['5'],print_sequence='by layer',enable_support='0',fuzzy_skin='disabled_fuzzy',bridge_speed='25').items():assert settings[k]==v,(k,settings[k],v)
   member=next(n for n in z.namelist() if n.endswith('.gcode'));assert hashlib.sha256(z.read(member)).hexdigest()==j['gcode_sha256']
  assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in j['warnings'])
  j['visual_review_complete']=True;g.save(ROOT/f'verifiche/slicing/{mode}/job.json',j)
 previous=read('verifiche/precedenti_immutati_snapshot.json');preserved={}
 for name,snapshot in previous.items():
  old=Path(snapshot['root'])
  if old.exists():
   for n,h in snapshot['files'].items():assert g.sha(old/n)==h,(name,n)
   preserved[name]=dict(checked=True,files=len(snapshot['files']))
  else:preserved[name]=dict(checked=False,reason='Revisione storica non presente in questa postazione')
 g.save(ROOT/'verifiche/precedenti_conservati.json',preserved)
 spans=read('verifiche/slicing/COMPLETO/campate_basamento.json');assert spans['max_approx_free_span_mm']<15
 assert spans['source_gcode_sha256']==next(j['gcode_sha256'] for j in jobs if j['mode']=='COMPLETO')
 bridge_frames=read('verifiche/slicing/COMPLETO/cornici_ponti_gcode.json');assert bridge_frames['source_gcode_sha256']==spans['source_gcode_sha256'] and len(bridge_frames['cornici'])==6
 state=dict(revision='R24_CARTUCCE_B_PLA_BASIC',state='PRONTO_PER_LA_STAMPA_DEL_PROTOTIPO_CON_PROVA_PRELIMINARE',configuration=g.P['configurazione_stampa'],projects={j['mode']:dict(path=j['project'],sha256=j['project_sha256'],estimates=j['totals']) for j in jobs},parts_full_kit=7,body_reprint_required=True,old_carriers_reusable=False,roof_geometry_unchanged_from_R22=True,roof_and_key_already_printed_R22_reusable_if_fit_verified=True,external_dimensions_mm=[90,109.4,86],side_protrusions=False,elastic_arms=False,export_reopened=True,kinematics_verified=True,slicing_verified=True,all_layers_reviewed=True,physical_fit=False,physical_print=False,force_validated=False,thermal_test=False,sent_to_printer=False,hardware_bom={},commercial_components=['4 piedini trasparenti propri; sole sedi incluse'],prerequisite='Prima il provino interni R24. Provino del tetto solo se guide e perno R22 non sono ancora stati verificati sul pezzo reale.',limitations=geo['limitations'])
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state);g.save(ROOT/'verifiche/slicing/riepilogo.json',dict(jobs=jobs,note=state['prerequisite']))
 table='\n'.join(f"| {j['mode']} | {j['slicer_estimates']['total filament used [g]']} g | {j['slicer_estimates']['estimated printing time (normal mode)']} | {len(j['items'])} | {j['layers']} |" for j in jobs)
 readme=f'''# Bay SSD R24 — cartucce B, ELEGOO PLA BASIC

**Pronto per la stampa del prototipo con prova preliminare. Non stampato o verificato fisicamente.** R24 è la revisione da usare per i nuovi interni; il kit completo R22 rimane sospeso. La sagoma monolitica, il logo S9 e il tetto scorrevole R22 sono conservati. Nuova scocca necessaria: le vecchie alette e i precedenti inserti non sono riutilizzabili.

## Aprire e stampare

- [01 — Provino interni](stampa/progetti_ElegooSlicer/BAY_R24_01_PROVINO_INTERNI_ECC2_PLABASIC.3mf): prima di impegnare il case completo.
- [02 — Provino tetto](stampa/progetti_ElegooSlicer/BAY_R24_02_PROVINO_TETTO_ECC2_PLABASIC.3mf): serve solo se non hai ancora provato fisicamente guide e perno R22. La geometria del tetto e del perno è identica.
- [03 — Kit completo, un solo piatto](stampa/progetti_ElegooSlicer/BAY_R24_03_KIT_COMPLETO_UNICO_PIATTO_ECC2_PLABASIC.3mf): dopo la verifica dei provini pertinenti.

Sono progetti nativi ElegooSlicer con profili macchina, materiale, impostazioni, oggetti separati e slicing salvato. I 3MF in `sorgenti/` sono invece le disposizioni geometriche di ingresso. Gli STL sono separati e orientati in `stampa/STL/`; non usare il STEP dell'assieme per la stampa. G-code effettivamente generati da ElegooSlicer e confrontati con quelli incorporati nei progetti, in `stampa/GCODE/`. Nessun file inviato alla stampante.

| Piatto | Materiale stimato | Tempo stimato | Pezzi | Strati |
| --- | ---: | --- | ---: | ---: |
{table}

Stime dello slicer con brim e impostazioni salvate. I provini non fanno parte del kit finale e non vanno aggiunti al suo piatto. Nelle due disposizioni con cornici/cartucce, i tre modelli sono in riga, da sinistra: T7, T7 Shield, T9.

## Parti e funzionamento

Il kit contiene **sette pezzi**: scocca, tetto, perno nascosto del tetto, un fermo frontale comune e tre cartucce monolitiche, una per T7, una per T7 Shield e una per T9. Nessuna vite, magnete, colla o tampone interno da acquistare. Rimangono soltanto i quattro piedini trasparenti propri dell'utente: sono presenti le sedi Ø10,5 mm profonde 0,65 mm. Usare piedini che mantengano almeno 5 mm di aria sotto la base.

Ogni cartuccia ha due cornici chiuse profonde 12 mm, sponde da 3 mm, ponte alto da 2,4 mm e inviti da 0,6 mm alle bocche. Gli angoli esterni superiori rientrano di 1 mm per passare accanto alle guide del tetto: qui la sponda è circa 2 mm, con minimi locali di circa 1,4 mm alle bocche invitate. Si carica l'SSD da dietro, fuori dal case e con il cavo scollegato. Le cartucce hanno aperture dedicate ma lo stesso piede: ciascuna entra in tutti e tre gli slot. Per cambiare ordine sposta SSD e cartuccia insieme; per cambiare modello sostituisci la cartuccia.

Il piede largo 20,8 mm si cala in posizione avanzata di 6 mm, poi scorre indietro sotto quattro brevi fermi rigidi. Le superfici a 45° trattengono il piede verso l'alto; il fermo frontale comune impedisce il ritorno avanti. Il fermo si appoggia per gravità fra il fronte e le battute delle cartucce: il progetto è per uso sulla scrivania in posizione verticale. Una presa centrale sale a Z79 mm, vicino all'apertura superiore; non serve raggiungere il fondo con le dita. Non è un aggancio destinato al trasporto capovolto. Il disco non viene serrato e non si deve far leva sulle cornici.

## Sequenza e prova preliminare

1. Nel provino interni, rimuovi solo brim e fili residui. Prova il piede nella base: cala 6 mm più avanti, arretra, inserisci il piccolo fermo. Deve arrivare a battuta a mano e restare trattenuto senza sollevarsi liberamente. Togli il fermo, avanza di 6 mm e solleva. Non correggere un incastro duro con pressione sulle sponde.
2. Prova ciascun SSD nella sua cornice da 4 mm. Fai scorrere il corpo lungo tutta la lunghezza utile per verificare anche le parti gommate. Deve scorrere a mano senza incastrarsi o richiedere flessione della cornice. Questi gabarit verificano l'apertura, non la rigidità o l'attrito delle due cornici complete. Il fermo del provino è basso per risparmiare materiale: riproduce le battute, senza la presa alta del pezzo completo.
3. Se guide e perno del tetto non sono già stati verificati fisicamente, usa il provino tetto. Inserisci il tetto da dietro; infila il perno da sotto, ruota 90° e abbassalo di 1,1 mm nella sede. Per aprire, alza, ruota e sfila il perno. Non forzare le guide con un montaggio verticale del tetto.
4. Dopo l'esito positivo, stampa il kit completo. Rimuovi brim e fili, senza carteggiare automaticamente le superfici funzionali. Infila ogni disco nella sua cartuccia fuori dal case. Cala le cartucce, arretrale di 6 mm e aggiungi il fermo frontale comune. Collega i cavi da dietro; richiudi il tetto scorrendo dal retro e blocca il perno. Per estrarre una cartuccia scollega prima il suo cavo. Servono circa 11 cm liberi dietro per sfilare interamente il tetto.
5. Controlla sul primo kit il gioco residuo, la presa del fermo con le dita, l'accesso ai cavi e tutti i nove abbinamenti cartuccia/slot. Confronta poi gli SSD dentro e fuori dal bay nello stesso carico di lavoro e ambiente, soprattutto quello centrale. Non coprire fondo o tetto e verifica eventuali deformazioni del PLA.

I giochi sono iniziali, da verificare con i pezzi reali. Se il provino è troppo duro o troppo lasco, correggere i parametri e rigenerare prima della stampa completa. Non dichiarato un esito fisico dei provini.

## Quote e aria

Ingombro chiuso nominale **90 × 109,4 × 86 mm**, incluso S9, esclusi piedini e cavi. I modelli SSD sono gabarit rettangolari nominali, non scansioni: T7 85 × 57 × 8 mm, Shield 88 × 59 × 13 mm, T9 88 × 60 × 14 mm. Seduta Z13 mm e interasse 24 mm; due T9 lasciano 10 mm fra le facce libere. Due fasce a Y28–40 e Y76–88 lasciano 36 mm centrali scoperti. Fra due cartucce T9 la luce scende localmente a 3,6 mm nelle due fasce; fuori dalle cornici restano 10 mm fra le facce dei dischi.

Canali: T7 **8,4 × 57,5 mm**, Shield **13,4 × 59,5 mm**, T9 **14,4 × 60,5 mm**. Gioco laterale SSD **0,4 mm totale = 0,2 per lato**; sopra **0,5 mm**. Il piede ha **0,2 mm per lato** nel basamento e **0,2 mm verticali** rispetto alle guide inclinate (circa **0,141 mm normali** alla faccia a 45°). Il fermo ha 0,2 mm davanti e 0,2 dietro; le superfici orizzontali di seduta sono contatti intenzionali. Nessun cuneo montato in pressione e nessuna deformazione nominale richiesta.

Fondo e tetto restano ventilati. Piccole costole da 2,4 mm sotto le fasce portanti accorciano le campate sopra le prese inferiori; le finestre centrali e gli spazi fra SSD rimangono aperti. La copertura locale delle cornici riduce l'area esposta sulle facce; non è stata eseguita CFD o una prova termica. Cavi esterni, ingombro nominale generoso di ciascuna spina 20 × 20 × 50 mm, posizione USB da verificare con i dispositivi reali.

## Impostazioni salvate

ElegooSlicer **{jobs[0]['slicer_app']}**, motore **{jobs[0]['slicer_engine']}**, profilo specifico **Elegoo Centauri Carbon 2 0.4 nozzle** della Combo, verificato contro le risorse installate. PEI testurizzato, ELEGOO PLA BASIC, monocolore, strato 0,20 mm, quattro pareti generali; cartucce, cornici di prova e piede di prova con sei pareti. 20% gyroid; perno con override 100% rettilineo. Brim esterno 5 mm, distanza 0,1 mm; compensazione piede d'elefante 0,1 mm. Supporti disattivati, fuzzy skin disattivata, nessuna torre di spurgo. Sequenza per strati.

Ugello 220 °C, piano 60 °C, limite volumetrico 5 mm³/s, ponti 25 mm/s; flusso filamento 0,98, flusso processo 0,97 e PA 0,04 ereditati dal lavoro precedente. Sono valori iniziali, non una calibrazione della bobina. L'ugello 220 °C coincide con il profilo installato PLA BASIC ECC2 e rientra nell'intervallo [ELEGOO PLA 190–230 °C](https://us.elegoo.com/products/pla-filament-1-75mm-colored-1kg). Piano 60 °C deriva dal profilo risolto. Il profilo comprende i macro macchina originali, senza G-code scritto a mano.

Unico avviso ammesso: `bed_temperature_too_high_than_filament`, 1000C001, soglia software PLA 45 °C rispetto al piano 60 °C. Mantieni ventilata la camera durante questa stampa PLA; per questa preparazione è previsto lo sportello anteriore aperto. Usa una singola bobina PLA BASIC disponibile e assegna il canale CANVAS corretto: il colore antracite delle anteprime è indicativo. Piano pulito, ugello 0,4 mm installato, materiale asciutto; lascia raffreddare prima del distacco. Nessun colore della bobina è stato inventato come confermato.

Scocca dritta sulla base; tetto capovolto con esterno sul PEI; perno piatto con asse parallelo al piano. Cartucce dritte sul piede, cornici di prova sulla propria traversa inferiore, fermo sul fondo. Conserva questi orientamenti: nei progetti gli oggetti sono già disposti con il brim e lontani dalla zona esclusa del profilo. Il kit completo occupa un solo piatto senza sovrapposizioni.

## Verifiche e limiti

Riaperti 15 tipi STEP, STEP orientati e STL: un solido/componente per parte, scala mm, volume positivo, mesh chiuse e coerenti, zero facce degeneri/duplicate e nessuna coppia nello screening delle autointersezioni, che esclude triangoli con vertici condivisi. Assieme STEP riaperto: dieci solidi, inclusi i tre SSD di riferimento, non stampabile come oggetto unico.

Nove abbinamenti SSD/slot, 171 pose di ingresso e scorrimento delle cartucce, combinazioni adiacenti, ritenuta geometrica in alto/davanti/dietro/lati, ingresso del fermo, 35 pose del tetto e 62 del perno. Ponti e guide controllati nello slicing; nessuna isola esterna candidata nello screening raster. I tre progetti sono stati riaperti e controllati per unità, trasformazioni, quantità, profili, override, brim, area utilizzabile e G-code incorporato. Tutti i {sum(j['layers'] for j in jobs)} strati sono nelle tavole di percorso visionate, con ingrandimenti dei particolari.

Questi controlli dimostrano la preparazione digitale, non assenza di gioco, resistenza, durata o buon esito fisico. Servono ancora stampa e prova: calzata con le superfici reali degli SSD, attrito complessivo delle due cornici, deformazione del PLA nel tempo, rimozione manuale dei fermi, cavi e raffreddamento. Stato e report in `verifiche/`.

## Sorgenti e rigenerazione

Python 3.11, CadQuery 2.8.0 / OCP 7.9.3.1.1; dipendenze bloccate in `sorgenti/requirements.txt`. Nel workspace usare `../bay-ssd-universale-r01/.venv/bin/python`, oppure creare un ambiente e installare le dipendenze. `genera.py` definisce il nuovo interno; `involucro_r22.py` conserva il tetto e il perno; `base_r15.py` fornisce primitive, ventilazioni e logo, senza generare le vecchie sedi. Le sezioni legacy dei parametri sono riferimenti storici; i giochi e le quote principali delle nuove cartucce sono in `cartucce_b`; le coordinate dettagliate dell’interfaccia sono nel sorgente.

```sh
PYTHON=../bay-ssd-universale-r01/.venv/bin/python
"$PYTHON" -B -u sorgenti/genera.py
"$PYTHON" -B -u sorgenti/verifica.py
"$PYTHON" -B -u sorgenti/stampa.py
"$PYTHON" -B -u sorgenti/campate.py
"$PYTHON" -B -u sorgenti/anteprime.py
```

Lo slicing richiede l'app ElegooSlicer installata. Dopo una modifica rigenerare tutti i derivati e ripetere la revisione visiva: `consegna.py` rifiuta immagini o progetti con hash diversi da quelli visionati. I riferimenti STEP R22 sono inclusi solo per verificare l'identità del tetto/perno. Le revisioni precedenti non vengono sovrascritte. Il pacchetto completo è `BAY_R24_COMPLETO_CARTUCCE_B_PLA_BASIC.zip`.
'''
 (ROOT/'README.md').write_text(readme)
 report=dict(state=state['state'],parts_reopened=len(geo['parts']),geometry_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),slicing_layers_reviewed=sum(j['layers'] for j in jobs),cad_images_reviewed=len(a['outputs']),toolpath_images_reviewed=sum(len(j['images']) for j in jobs),base_bridge_screen=spans,history_preserved=preserved,physical_print=False,physical_fit=False,thermal_test=False)
 g.save(ROOT/'verifiche/RAPPORTO_VERIFICHE.json',report)
 allowed={'sorgenti','slicer','CAD','stampa','anteprime','verifiche'}
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and (p.relative_to(ROOT).parts[0] in allowed or p.name in ['README.md','logo_S9.png','logo_S9.svg']) and p.name not in ['SHA256.json','.DS_Store'] and '__pycache__' not in p.parts and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R24_COMPLETO_CARTUCCE_B_PLA_BASIC.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for n in [*hh,'verifiche/SHA256.json']:z.write(ROOT/n,ROOT.name+'/'+n)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for n,h in hh.items():assert hashlib.sha256(z.read(ROOT.name+'/'+n)).hexdigest()==h
 print(json.dumps(dict(state=state['state'],files=len(hh)+1,archive_bytes=archive.stat().st_size,projects=state['projects'])),flush=True)
if __name__=='__main__':main()
