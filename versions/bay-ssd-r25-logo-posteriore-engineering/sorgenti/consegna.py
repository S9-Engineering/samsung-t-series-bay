"""Audit R25: file, progetto slicer, percorsi del marchio e revisione visiva."""
import json,zipfile,hashlib
from pathlib import Path
import genera as g
from native_3mf import validate
ROOT=g.ROOT
def read(n):return json.loads((ROOT/n).read_text())
def main():
 m=read('verifiche/manifest.json');geo=read('verifiche/geometria.json');a=read('verifiche/anteprime.json');r=read('verifiche/revisione_visiva.json');jobs=read('verifiche/slicing/riepilogo.json')['jobs']
 assert m['source_sha256']==g.sha(ROOT/'sorgenti/genera.py') and m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 assert geo['manifest_sha256']==a['manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json') and len(geo['parts'])==7 and geo['unchanged_printable_parts']==6
 assert len(geo['changes'])==1 and geo['changes'][0]['glyphs']==13 and geo['changes'][0]['added_only']
 assert geo['assembly_sha256']==g.sha(ROOT/'CAD/ASSIEME_R25_NON_STAMPARE.step') and geo['assembly_solids']==10
 for p in m['parts']:
  q=next(q for q in geo['parts'] if q['name']==p['name']);assert q['single_valid_solid'] and q['mesh_closed'] and q['winding'] and q['self_intersections']['intersection_pairs']==0
  for k in ['stl','step','print_step']:assert g.sha(ROOT/p[k])==q[k+'_sha256']
 assert a['outputs']==r['cad_image_hashes'] and len(a['outputs'])==4
 for n,h in a['outputs'].items():assert g.sha(ROOT/n)==h
 for j in jobs:
  assert g.sha(ROOT/j['project'])==j['project_sha256']==r['projects'][j['mode']]
  assert g.sha(ROOT/j['gcode'])==j['gcode_sha256'] and g.sha(ROOT/j['geometry_source'])==j['geometry_sha256']
  for n,h in j['profiles'].items():assert g.sha(ROOT/'slicer'/n)==h
  native=validate(ROOT/j['project'],j['items']);assert native['printable_count']==(1 if j['mode']=='TETTO' else 7) and native['modifier_count']==0
  for p in native['parts']:
   q=next(q for q in geo['parts'] if q['name']==p['name']);assert abs(p['volume_mm3']/q['volume_mm3']-1)<1e-4
  for n,h in r['image_hashes'][j['mode']].items():assert g.sha(ROOT/n)==h
  assert set(j['images'])==set(r['image_hashes'][j['mode']])
  analysis=read('verifiche/slicing/'+j['mode']+'/analisi.json');assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations'] and analysis['new_wall_islands']['candidate_count']==0
  logo=read('verifiche/slicing/'+j['mode']+'/logo.json');assert logo['source_gcode_sha256']==j['gcode_sha256'] and len(logo['glyphs'])==13 and all(q['layers']>=5 for q in logo['glyphs'])
  with zipfile.ZipFile(ROOT/j['project']) as z:
   member=next(n for n in z.namelist() if n.endswith('.gcode'));assert hashlib.sha256(z.read(member)).hexdigest()==j['gcode_sha256']
   s=json.loads(z.read('Metadata/project_settings.config'))
   for k,v in dict(printer_model='Elegoo Centauri Carbon 2',nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',wall_loops='4',sparse_infill_density='20%',brim_width='5',enable_support='0',fuzzy_skin='disabled_fuzzy',filament_max_volumetric_speed=['5']).items():assert s[k]==v
  assert j['object_config']['TETTO_R25_LOGO_ENGINEERING']['wall_generator']=='arachne'
  assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in j['warnings'])
  j['visual_review_complete']=True;g.save(ROOT/'verifiche/slicing'/j['mode']/'job.json',j)
 old=read('verifiche/riferimenti_R24.json');oldroot=Path(old['baseline_root'])
 preserved=None
 if oldroot.exists():
  assert all(g.sha(oldroot/n)==h for n,h in old['baseline_files'].items());preserved=len(old['baseline_files'])
 for p in (ROOT/'stampa/provini_R24_invariati').glob('*.3mf'):
  assert g.sha(p)==old['baseline_files']['stampa/progetti_ElegooSlicer/'+p.name]
 state=dict(revision=m['revision'],state='PRONTO_PER_LA_STAMPA_DEL_PROTOTIPO_CON_PROVA_PRELIMINARE',configuration=g.P['configurazione_stampa'],full_kit_parts=7,changed_parts=['TETTO_R25_LOGO_ENGINEERING'],unchanged_parts=6,logo=dict(text='S9 ENGINEERING',width_mm=40,height_mm=40*.6179337231968811,relief_mm=.4,center_x_mm=45,center_z_mm=71.5,visible_from='+Y',glyphs_present_in_both_gcodes=13),external_dimensions_mm=[90,109.8,86],projects={j['mode']:dict(path=j['project'],sha256=j['project_sha256'],estimates=j['totals']) for j in jobs},export_reopened=True,slicing_verified=True,all_layers_reviewed=True,physical_print=False,physical_fit=False,thermal_test=False,physical_logo_finish=False,sent_to_printer=False,hardware_bom={},prerequisite='I provini interni e chiusura R24 restano validi e necessari se non ancora verificati fisicamente; nessun nuovo provino per il solo logo.',R24_files_preserved=preserved)
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state);g.save(ROOT/'verifiche/slicing/riepilogo.json',dict(jobs=jobs))
 table='\n'.join(f"| {j['mode']} | {j['slicer_estimates']['total filament used [g]']} g | {j['slicer_estimates']['estimated printing time (normal mode)']} | {len(j['items'])} |" for j in jobs)
 readme=f'''# Bay SSD R25 — logo posteriore S9 Engineering

**Pronto per la stampa del prototipo con prova preliminare. Stampa e finitura non ancora verificate fisicamente.** Questa revisione aggiunge soltanto il logo completo approvato alla faccia esterna posteriore del tetto R24. S9 frontale, scocca, tre cartucce B, fermo frontale, chiusura e aperture sono conservati. Il confronto geometrico con R24 e riportato in `verifiche/geometria.json`.

## File da usare

- [Solo tetto con logo — 3MF](stampa/progetti_ElegooSlicer/BAY_R25_01_SOLO_TETTO_LOGO_ENGINEERING_ECC2_PLABASIC.3mf): per sostituire il tetto se il resto del kit R24 e gia disponibile.
- [Kit completo — 3MF, unico piatto](stampa/progetti_ElegooSlicer/BAY_R25_02_KIT_COMPLETO_UNICO_PIATTO_ECC2_PLABASIC.3mf): sette pezzi, una copia di ciascuno.
- `stampa/STL/`: sette STL orientati in mm. `CAD/`: STEP e STEP orientati; l'assieme contiene anche tre gabarit SSD ed e solo di consultazione.
- `stampa/GCODE/`: G-code effettivamente generati da ElegooSlicer e confrontati con quelli incorporati nei progetti. Nessun file inviato alla stampante.

I due 3MF sopra sono progetti nativi con macchina, filamento, impostazioni, oggetti separati e slicing. I 3MF in `sorgenti/` sono invece le disposizioni geometriche di ingresso.

| Piatto | Materiale stimato | Tempo stimato | Pezzi |
| --- | ---: | --- | ---: |
{table}

Stime dello slicer con brim incluso, senza supporti o torre di spurgo. Non sono misurazioni fisiche.

## Logo

Stesso marchio approvato: S9 sopra e ENGINEERING sotto, senza cambiare proporzioni o font. **40 × 24,72 mm**, centrato a X45 / Z71,5 sulla faccia posteriore 90 × 29 mm (compreso il bordo del tetto), con margini verticali circa 2,14 mm. Rilievo **0,4 mm**, nello stesso PLA del tetto; sovrapposizione nella parete 0,15 mm. Il testo e leggibile guardando il retro da +Y. Nessun pezzo, adesivo o cambio colore aggiuntivo.

Ingombro del bay chiuso: **90 × 109,8 × 86 mm**, incluso S9 frontale e nuovo rilievo posteriore, esclusi cavi e piedini. L'aggiunta e tutta all'esterno; nessuna parte del tetto originale e stata sottratta. Non cambiano connettori, ventilazione o superfici di chiusura. Il tetto R25 puo sostituire quello R24 senza ristampare gli altri sei pezzi.

## Stampa

ELEGOO Centauri Carbon 2 Combo, ugello **0,4 mm**, **PEI testurizzato**, **ELEGOO PLA BASIC**, monocolore. ElegooSlicer {jobs[0]['slicer_app']}, motore {jobs[0]['slicer_engine']}, profilo macchina specifico `Elegoo Centauri Carbon 2 0.4 nozzle` della Combo.

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
'''
 (ROOT/'README.md').write_text(readme)
 g.save(ROOT/'verifiche/RAPPORTO_VERIFICHE.json',dict(state=state['state'],parts_reopened=7,cad_images_reviewed=4,toolpath_images_reviewed=sum(len(j['images']) for j in jobs),layers_reviewed=sum(j['layers'] for j in jobs),logo_present_in_both_gcodes=13,R24_files_preserved=preserved,physical_print=False))
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['SHA256.json','.DS_Store'] and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R25_LOGO_ENGINEERING_PLA_BASIC.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for n in [*hh,'verifiche/SHA256.json']:z.write(ROOT/n,ROOT.name+'/'+n)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and all(hashlib.sha256(z.read(ROOT.name+'/'+n)).hexdigest()==h for n,h in hh.items())
 print(json.dumps(dict(state=state['state'],archive_bytes=archive.stat().st_size,files=len(hh)+1,projects=state['projects'])),flush=True)
if __name__=='__main__':main()
