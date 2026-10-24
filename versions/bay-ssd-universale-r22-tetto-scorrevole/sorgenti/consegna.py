"""Audit finale R22; rifiuta una consegna senza riscontro visivo sugli hash correnti."""
import json,zipfile,hashlib
import cadquery as cq
import numpy as np
import genera as g
from native_3mf import validate
ROOT=g.ROOT
def read(p):return json.loads((ROOT/p).read_text())
def main():
 if (ROOT/'verifiche/REVISIONE_SEDI_INTERNE.json').exists():raise SystemExit('Kit R22 sospeso: rivedere le sedi interne prima di qualificare una nuova consegna. Il provino tetto resta una prova separata.')
 m=read('verifiche/manifest.json');geo=read('verifiche/geometria.json');a=read('verifiche/anteprime.json');r=read('verifiche/revisione_visiva.json');jobs=read('verifiche/slicing/riepilogo.json')['jobs']
 assert m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 assert geo['source_manifest_sha256']==a['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 assert len(m['parts'])==7 and m['complete_kit_parts']==7 and not m['elastic_latch']
 for p in m['parts']:
  q=next(q for q in geo['parts'] if q['name']==p['name']);assert q['closed'] and q['components']==1 and q['winding'] and q['positive_volume']
  assert q['degenerate_faces']==q['duplicate_faces']==q['self_intersections']['intersection_pairs']==0
  for k in ['stl','step','print_step']:assert g.sha(ROOT/p[k])==q[k+'_sha256']
 assert len(geo['roof_paths'])==35 and len(geo['key_paths'])==62 and len(geo['ssd_checks'])==9
 assert all(q['usb_min_key_sweep_distance_mm']>1.38 for q in geo['ssd_checks']) and all(v>0 for v in geo['retention'].values())
 assert len(a['outputs'])==4 and a['outputs']==r['cad_image_hashes']
 for n,h in a['outputs'].items():assert g.sha(ROOT/n)==h
 asm_path=ROOT/'CAD/ASSIEME_R22_NON_STAMPARE.step';asm=cq.importers.importStep(str(asm_path)).val()
 assert len(asm.Solids())==10 and asm.isValid() and all(s.Volume()>0 for s in asm.Solids())
 b=np.array(g.bounds(asm));assert np.allclose(b,[[0,-.4,0],[90,109,86]],atol=.001)
 for model in ['T7','T7_Shield']:
  for slot in range(3):
   d=g.drive(model,slot)
   for y in g.P['slot']['centri_y']:assert sum(s.Volume() for s in g.adapter(model,y,slot).intersect(d).Solids())<1e-5
 g.save(ROOT/'verifiche/assieme_STEP.json',dict(result='PASS',step_sha256=g.sha(asm_path),solids=10,bounds_mm=b.tolist(),printable_assembly=False,adapters_drive_interference_mm3=0))
 for j in jobs:
  mode=j['mode'];live=read(f'verifiche/slicing/{mode}/job.json');assert live['project_sha256']==j['project_sha256']==r['projects'][mode]
  assert g.sha(ROOT/j['project'])==j['project_sha256'] and g.sha(ROOT/j['geometry_source'])==j['geometry_sha256']
  for n,h in j['profile_hashes'].items():assert g.sha(ROOT/'slicer'/n)==h
  check=validate(ROOT/j['project'],j['items']);assert check['printable_count']==(3 if mode=='PROVA' else 7) and check['modifier_count']==0
  for item in j['items']:
   native_part=next(p for p in check['parts'] if p['name']==item['name'])
   source_part=next(p for p in geo['parts'] if p['name']==item['part'])
   assert abs(native_part['volume_mm3']/source_part['volume_mm3']-1)<.0001
  assert set(j['images'])==set(r['image_hashes'][mode])
  for n,h in r['image_hashes'][mode].items():assert g.sha(ROOT/n)==h
  analysis=read(f'verifiche/slicing/{mode}/analisi.json');assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations'] and analysis['new_wall_islands']['candidate_count']==0
  with zipfile.ZipFile(ROOT/j['project']) as z:
   s=json.loads(z.read('Metadata/project_settings.config'))
   expected=dict(printer_model='Elegoo Centauri Carbon 2',nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',wall_loops='4',sparse_infill_density='20%',sparse_infill_pattern='gyroid',brim_width='5',filament_max_volumetric_speed=['5'],print_sequence='by layer',enable_support='0',fuzzy_skin='disabled_fuzzy')
   for k,v in expected.items():assert s[k]==v,(k,s[k],v)
  assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in j['warnings'])
  j['visual_review_complete']=True;g.save(ROOT/f'verifiche/slicing/{mode}/job.json',j)
 g.save(ROOT/'verifiche/slicing/riepilogo.json',dict(jobs=jobs,note='Provino prima del kit completo. Kit in un piatto, sette pezzi. Perno e inserti gia disponibili sono riutilizzabili.'))
 state=dict(revision='R22_SCORREVOLE_NASCOSTO',state='PRONTO_PER_LA_STAMPA_DEL_PROTOTIPO_CON_PROVA_PRELIMINARE',configuration=g.P['configurazione_stampa'],projects={j['mode']:dict(path=j['project'],sha256=j['project_sha256'],estimates=j['totals']) for j in jobs},parts_full_kit=7,types_full_kit=5,body_reprint_required=True,external_dimensions_mm=[90,109.4,86],side_protrusions=False,elastic_arms=False,kinematics_verified=True,export_reopened=True,slicing_verified=True,all_layers_reviewed=True,physical_fit=False,physical_print=False,force_validated=False,thermal_test=False,sent_to_printer=False,hardware_bom={},commercial_components_optional=['4 piedini trasparenti propri; sole sedi incluse'],prerequisite='Stampare e verificare guide e fermo del provino R22 prima della nuova scocca completa.',limitations=geo['limitations'])
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state)
 lines=['# Verifiche R22 — guide interne e fermo nascosto','',
  '**Pronto per la stampa del prototipo con prova preliminare. Non stampato o verificato fisicamente.**','',
  'Nuova scocca necessaria; il tetto scorre da dietro su due guide lunghe 82 mm, radice 3 mm e rampe 45 gradi. Il perno rigido si inserisce da sotto, ruota di 90 gradi e si abbassa 1,1 mm nella sede trasversale. Nessuna molla, linguetta o paletta esterna. Il perno non puo ruotare nominalmente finche non viene rialzato.',
  'Sagoma nominale chiusa 90 x 109,4 x 86 mm, incluso S9, esclusi cavi e piedini. Nessun componente supera i lati X0/90. Pattern laterale e spigoli R15 conservati; chiuse le finestrelle dei vecchi ganci. Feritoie superiori accorciate ai lati per lasciare margini 12 mm sopra le guide.',
  'Sette tipi STEP, STEP orientati e STL riaperti: un solido/componente ciascuno, scala millimetrica, volume positivo, normali coerenti, mesh chiuse, zero facce degeneri e duplicate, nessuna coppia nello screening autointersezioni che esclude triangoli con vertici condivisi. Nessuna riparazione automatica. Assieme STEP riaperto: dieci solidi, incluse le tre sagome SSD non stampabili e quattro inserti.',
  'Cinematica nominale con corpi rigidi: 35 offset del tetto da 101 a 0 mm; 31 posizioni di ingresso del perno, 19 angoli e 12 quote di assestamento. Verificate le interferenze attese alla battuta anteriore, durante il tentativo di sollevamento, arretramento, estrazione e rotazione del perno abbassato. Il moto e campionato: non e una dimostrazione continua o una prova di forze e durata.',
  'Provino con guide da 20 mm, stessa larghezza e stesse superfici funzionali; confronto geometrico passato. La finestra centrale e la coda alleggerita riducono il consumo lontano dal fermo. La prova non dimostra l attrito delle guide lunghe o la manovrabilita con tutti i dispositivi collegati.',
  'Nove abbinamenti SSD/slot verificati, scorrimento del tetto e azionamento del perno con ingombri USB nominali 20 x 20 x 50 mm. Distanza minima campionata perno/USB 1,388 mm. Gli inserti T7 e Shield conservano la geometria R15; assenza di interferenze nominali con SSD e scocca. Quote porte e connettori reali ancora da misurare o provare.',
  f"File precedenti conservati e controllati con gli hash: {geo['previous_files_preserved']}.",
  'Progetti nativi ElegooSlicer app 1.5.3.5 / motore 2.4.2. Entrambi su un piatto: provino tre oggetti, kit completo sette. Controllati mm, scale, trasformazioni, componenti, normale orientamento, brim 5 mm, distanze e zona esclusa. Configurazione ECC2 Combo monocolore, ugello 0,4, PEI testurizzato, ELEGOO PLA BASIC, 220/60 C, strato 0,20, quattro pareti, 20% gyroid con override perno 100% rettilineo, limite 5 mm3/s. Valori di partenza, non calibrazione fisica.',
  'Tutti i 145 strati del provino e 415 del kit visionati, oltre a ingrandimenti di guide, camera, perno, primo strato e ponti. Perno piatto con asse parallelo al piano, sezioni continue. Guide a crescita progressiva senza isole nuove rilevate (screening raster). Nessun percorso di supporto. Camera aperta lateralmente, apertura 8 mm; fori da controllare sul provino.',
  'Le maggiori lunghezze registrate come Internal Bridge comprendono superfici sopra il gyroid: una linea lunga non equivale a una campata libera della stessa lunghezza. Visionati strato sottostante e chiusura; i ponti delle sedi piedini appartengono alla geometria precedente conservata.',
  'Unico avviso: bed_temperature_too_high_than_filament, 1000C001 (piano 60 C rispetto a soglia software PLA 45 C). Preparazione: sportello anteriore aperto. Nessuna Fuzzy Skin o torre di spurgo.','']
 for j in jobs:lines.append(f"- {j['mode']}: {j['slicer_estimates']['total filament used [g]']} g / {j['slicer_estimates']['estimated printing time (normal mode)']}, brim incluso.")
 lines+=['','Nessuna stampa inviata alla macchina. Devono ancora essere verificati calzata e attrito, accesso alle dita, tenuta, durata, comportamento dei ponti reali, cavi, temperature SSD e comportamento del PLA nel tempo. La scelta di guide rigide elimina la flessione nominale delle vecchie alette; non costituisce una certificazione di resistenza.','']
 (ROOT/'verifiche/RAPPORTO_VERIFICHE.md').write_text('\n'.join(lines))
 allowed={'sorgenti','slicer','CAD','stampa','anteprime','verifiche'}
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and (p.relative_to(ROOT).parts[0] in allowed or p.name in ['README.md','logo_S9.png','logo_S9.svg']) and p.name not in ['SHA256.json','.DS_Store'] and '__pycache__' not in p.parts and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R22_SCORREVOLE_NASCOSTO_PLA_BASIC.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for n in [*hh,'verifiche/SHA256.json']:z.write(ROOT/n,ROOT.name+'/'+n)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for n,h in hh.items():assert hashlib.sha256(z.read(ROOT.name+'/'+n)).hexdigest()==h
 print(json.dumps(dict(state=state['state'],archive=str(archive),files=len(hh)+1,projects=state['projects'])),flush=True)
if __name__=='__main__':main()
