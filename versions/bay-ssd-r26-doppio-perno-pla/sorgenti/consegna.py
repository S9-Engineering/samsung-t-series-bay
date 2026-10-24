"""Audit finale R26: corrispondenza CAD, STL, progetti slicer e immagini revisionate."""
import json,zipfile,hashlib
from pathlib import Path
import genera as g
from native_3mf import validate
ROOT=g.ROOT
def read(n):return json.loads((ROOT/n).read_text())
def main():
 m=read('verifiche/manifest.json');geo=read('verifiche/geometria.json');a=read('verifiche/anteprime.json');r=read('verifiche/revisione_visiva.json');jobs=read('verifiche/slicing/riepilogo.json')['jobs']
 assert m['source_sha256']==g.sha(ROOT/'sorgenti/genera.py') and m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 assert all(g.sha(ROOT/'sorgenti'/n)==h for n,h in m['geometry_dependencies'].items())
 assert geo['manifest_sha256']==a['manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json') and len(geo['parts'])==9 and len(geo['unchanged_types'])==5
 assert len(geo['changes'])==2 and all(q['added_only'] and q['original_removed_mm3']==0 for q in geo['changes'])
 assert len(geo['ssd_checks'])==9 and len(geo['roof_paths'])==35 and len(geo['key_paths'])==124 and len(geo['pin_retention'])==2
 assert geo['pins_identical_printable'] and geo['coupon_functional_surfaces_match']
 assert geo['assembly_sha256']==g.sha(ROOT/'CAD/ASSIEME_R26_NON_STAMPARE.step') and geo['assembly_solids']==11
 parts={p['name']:p for p in m['parts']}
 for p in m['parts']:
  q=next(q for q in geo['parts'] if q['name']==p['name']);assert q['single_valid_solid'] and q['mesh_closed'] and q['winding'] and q['self_intersections']['intersection_pairs']==0
  for k in ['stl','step','print_step']:assert g.sha(ROOT/p[k])==q[k+'_sha256']
 assert r['all_images_opened_and_reviewed'] and a['outputs']==r['cad_image_hashes'] and len(a['outputs'])==5
 for n,h in a['outputs'].items():assert g.sha(ROOT/n)==h
 for j in jobs:
  assert g.sha(ROOT/j['project'])==j['project_sha256']==r['projects'][j['mode']]
  assert g.sha(ROOT/j['gcode'])==j['gcode_sha256'] and g.sha(ROOT/j['geometry_source'])==j['geometry_sha256']
  for n,h in j['profiles'].items():assert g.sha(ROOT/'slicer'/n)==h
  native=validate(ROOT/j['project'],j['items']);assert native['printable_count']==(4 if j['mode']=='PROVINO' else 8) and native['modifier_count']==0
  assert sum(it['part']=='PERNO_R26_NASCOSTO' for it in j['items'])==2
  for p in native['parts']:
   it=next(it for it in j['items'] if it['name']==p['name']);q=next(q for q in geo['parts'] if q['name']==it['part']);assert abs(p['volume_mm3']/q['volume_mm3']-1)<1e-4
  for n,h in r['image_hashes'][j['mode']].items():assert g.sha(ROOT/n)==h
  assert set(j['images'])==set(r['image_hashes'][j['mode']])
  analysis=read('verifiche/slicing/'+j['mode']+'/analisi.json');assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations'] and analysis['new_wall_islands']['candidate_count']==0
  if j['mode']=='COMPLETO':
   logo=read('verifiche/slicing/COMPLETO/logo.json');assert logo['source_gcode_sha256']==j['gcode_sha256'] and len(logo['glyphs'])==13 and all(q['layers']>=5 for q in logo['glyphs'])
  with zipfile.ZipFile(ROOT/j['project']) as z:
   member=next(n for n in z.namelist() if n.endswith('.gcode'));assert hashlib.sha256(z.read(member)).hexdigest()==j['gcode_sha256']
   s=json.loads(z.read('Metadata/project_settings.config'))
   for k,v in dict(printer_model='Elegoo Centauri Carbon 2',nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',wall_loops='4',sparse_infill_density='20%',brim_width='5',enable_support='0',fuzzy_skin='disabled_fuzzy',filament_max_volumetric_speed=['5']).items():assert s[k]==v
  roofname='PROVINO_GUIDE_TETTO_R26' if j['mode']=='PROVINO' else 'TETTO_R26_DOPPIO_PERNO'
  assert j['object_config'][roofname]['wall_generator']=='arachne'
  assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in j['warnings'])
  j['visual_review_complete']=True;g.save(ROOT/'verifiche/slicing'/j['mode']/'job.json',j)
 origin=read('verifiche/provenienza_profili.json')
 for q in origin['profiles'].values():assert g.sha(ROOT/q['snapshot'])==q['sha256'];assert g.sha(Path(q['installed_path']))==q['sha256']
 old=read('verifiche/riferimenti_R25.json');oldroot=Path(old['baseline_root']);preserved=None
 if oldroot.exists():
  assert all(g.sha(oldroot/n)==h for n,h in old['baseline_files'].items());preserved=len(old['baseline_files'])
 state=dict(revision=m['revision'],state='PRONTO_PER_LA_STAMPA',scope='Preparazione digitale del prototipo completo e del provino a due perni; esito fisico R26 da verificare.',configuration=g.P['configurazione_stampa'],full_kit_parts=8,full_kit_unique_types=7,pin_quantity=2,pins_identical=True,changed_parts=['SCOCCA_R26_DOPPIO_PERNO','TETTO_R26_DOPPIO_PERNO'],unchanged_types=geo['unchanged_types'],external_dimensions_mm=[90,109.8,86],projects={j['mode']:dict(path=j['project'],sha256=j['project_sha256'],estimates=j['totals']) for j in jobs},export_reopened=True,slicing_verified=True,all_layers_reviewed=True,physical_reports=read('verifiche/prove_riferite_utente.json'),physical_full_kit_print=False,physical_double_pin_test=False,physical_strength_validated=False,thermal_test=False,physical_logo_finish=False,sent_to_printer=False,hardware_bom={},R25_files_preserved=preserved)
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state);g.save(ROOT/'verifiche/slicing/riepilogo.json',dict(jobs=jobs))
 table='\n'.join(f"| {j['mode']} | {j['slicer_estimates']['total filament used [g]']} g | {j['slicer_estimates']['estimated printing time (normal mode)']} | {len(j['items'])} |" for j in jobs)
 readme=(ROOT/'sorgenti/README_modello.md').read_text().replace('{{TABELLA_STIME}}',table).replace('{{APP}}',jobs[0]['slicer_app']).replace('{{MOTORE}}',jobs[0]['slicer_engine'])
 (ROOT/'README.md').write_text(readme)
 g.save(ROOT/'verifiche/RAPPORTO_VERIFICHE.json',dict(state=state['state'],parts_reopened=9,full_kit_parts=8,pins=2,cad_images_reviewed=5,toolpath_images_reviewed=sum(len(j['images']) for j in jobs),layers_reviewed=sum(j['layers'] for j in jobs),ssd_cases=9,roof_poses=35,key_poses=124,cartridge_poses=171,logo_glyphs_present=13,R25_files_preserved=preserved,physical_full_kit_print=False))
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['SHA256.json','.DS_Store'] and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R26_COMPLETO_DOPPIO_PERNO_PLA_BASIC.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for n in [*hh,'verifiche/SHA256.json']:z.write(ROOT/n,ROOT.name+'/'+n)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and all(hashlib.sha256(z.read(ROOT.name+'/'+n)).hexdigest()==h for n,h in hh.items())
 print(json.dumps(dict(state=state['state'],archive_bytes=archive.stat().st_size,files=len(hh)+1,projects=state['projects'])),flush=True)
if __name__=='__main__':main()
