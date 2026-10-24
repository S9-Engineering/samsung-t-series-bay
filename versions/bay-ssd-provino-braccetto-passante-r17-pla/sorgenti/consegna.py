"""Audit del singolo provino R17 con braccetti quasi passanti."""
import json,zipfile,hashlib
import xml.etree.ElementTree as ET
import genera as g
from native_3mf import validate
ROOT=g.ROOT

def read(p):return json.loads((ROOT/p).read_text())
def main():
 m=read('verifiche/manifest.json');geo=read('verifiche/geometria.json');a=read('verifiche/anteprime.json');r=read('verifiche/revisione_visiva.json');j=read('verifiche/slicing/PROVINO/job.json')
 assert m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 assert geo['source_manifest_sha256']==a['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 assert len(m['parts'])==1 and geo['closed'] and geo['winding_consistent'] and geo['components']==1
 assert geo['self_intersections']['intersection_pairs']==0 and geo['degenerate_faces']==geo['duplicate_faces']==0
 p=m['parts'][0]
 assert geo['stl_sha256']==g.sha(ROOT/p['stl']) and geo['step_sha256']==g.sha(ROOT/p['step']) and geo['print_step_sha256']==g.sha(ROOT/p['print_step'])
 assert abs(geo['penetration_in_wall_mm']-2.8)<1e-5 and abs(geo['outer_recess_mm']-.2)<1e-5 and geo['seated_overlap_mm3']==0
 assert geo['bearing_overlap_after_lift_0_4mm_mm3']>0 and len(geo['insertion_envelopes'])==14
 assert geo['reference_difference_mm3']<1e-5
 assert g.sha(ROOT/j['project'])==j['project_sha256']==r['project_sha256'] and r['all_layer_overviews_reviewed']
 assert g.sha(ROOT/j['geometry_source'])==j['geometry_sha256']
 for name,h in j['profile_hashes'].items():assert g.sha(ROOT/'slicer'/name)==h
 for name,h in r['image_hashes'].items():assert g.sha(ROOT/name)==h
 for name,h in a['outputs'].items():assert g.sha(ROOT/name)==h
 assert set(j['images'])==set(r['image_hashes'])
 check=validate(ROOT/j['project'],j['items']);assert check['printable_count']==1 and check['modifier_count']==0
 with zipfile.ZipFile(ROOT/j['project']) as z:
  s=json.loads(z.read('Metadata/project_settings.config'))
  assert 'Centauri Carbon 2' in s['printer_model']
  expected=dict(nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',
   wall_loops='4',sparse_infill_density='20%',sparse_infill_pattern='gyroid',brim_width='5',filament_max_volumetric_speed=['5'],print_sequence='by layer',
   enable_support='1',support_style='snug',support_on_build_plate_only='0',support_top_z_distance='0.2',fuzzy_skin='disabled_fuzzy')
  for k,v in expected.items():assert s[k]==v,(k,s[k],v)
  warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')]
  assert warnings==j['warnings'] and all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings)
 analysis=read('verifiche/slicing/PROVINO/analisi.json')
 assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and analysis['new_wall_islands']['candidate_count']==0
 assert not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations'] and j['support_segments']>0
 j['visual_review_complete']=True;g.save(ROOT/'verifiche/slicing/PROVINO/job.json',j)
 state=dict(revision='R17_PROVINO_PASSANTE',state='PRONTO_PER_LA_STAMPA_DEL_PROVINO',configuration=g.P['configurazione_stampa'],
  project=j['project'],project_sha256=j['project_sha256'],estimates=j['totals'],slicer_app=j['slicer_app'],slicer_engine=j['slicer_engine'],parts=1,plates=1,
  wall_mm=3,penetration_mm=2.8,outer_recess_mm=.2,arm_length_from_finger_face_mm=3.1,root_release_slot=g.P['scarico_radice'],
  geometry_verified=True,export_reopened=True,slicing_verified=True,all_layer_overviews_reviewed=True,critical_layers_sampled=True,
  replaces_R16_coupon_for_this_test=True,physical_print=False,physical_fit=False,force_validated=False,FEA=False,sent_to_printer=False,full_lid_modified=False,limitations=geo['limitations'])
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state)
 e=j['slicer_estimates']
 lines=['# Verifiche R17 — braccetto quasi passante','',
  '**Pronto per la stampa del provino. Forza, corsa elastica e presa fisiche ancora da verificare.**','',
  'Un solo provino, un solo piatto, PLA BASIC. Penetrazione misurata sul CAD riaperto 2,8 mm nei 3 mm della parete; punta arretrata di 0,2 mm dal filo esterno. Lunghezza dal fianco dell’aletta 3,1 mm, distanza fra punte 89,6 mm. Braccetto largo 8,4 mm nel foro largo 9,6: 0,6 mm per estremita. Gioco verticale sotto il bordo superiore 0,2 mm.',
  'Scarico alla radice nel piano della traversa, tratto libero lungo 18 mm; serve a predisporre spazio per la corsa laterale maggiore. Nessuna simulazione della deformazione o misura del ritorno/forza. Pattini di precarico delle revisioni precedenti assenti.',
  'STL, STEP singolo, STEP orientato e due riferimenti parete riaperti. Scala millimetrica, un componente stampabile, mesh chiusa, normali coerenti, volume positivo. Nessuna faccia degenere o duplicata e nessuna coppia rilevata nello screening autointersezioni, che esclude triangoli con vertici condivisi. Nessuna riparazione automatica.',
  'Posizione seduta senza collisioni; spalla incontra il bordo superiore dopo 0,2 mm nominali. Verificata interferenza di ritenuta con un’alzata campione di 0,4 mm. Quattordici inviluppi campionati senza collisioni durante discesa e rilascio, traslando le parti mobili fino a 3 mm verso interno. Questo non dimostra che il PLA compia quella corsa elasticamente.',
  f"Finestre confrontate con il STEP della scocca R15: differenza {geo['reference_difference_mm3']:.8f} mm³. File precedenti verificati e conservati: {geo['previous_hashed_files_preserved']}.",
  '3MF nativo ElegooSlicer riaperto: un oggetto, zero modificatori, unità mm e trasformazioni valide. Ingombro con brim 100 x 42 mm entro il piano 256 x 256 mm, zona esclusa rispettata. Geometria, profili e G-code dello slicer incorporati. App 1.5.3.5 / motore 2.4.2; macchina ECC2 Combo, ugello 0,4, PEI testurizzato, PLA BASIC 220/60 °C, strato 0,20 mm, quattro pareti, gyroid 20%, 5 mm³/s, brim 5 mm, supporti snug e interfaccia 0,2 mm, nessuna Fuzzy Skin o torre.',
  'Tutti i 75 strati esaminati nelle tavole d’insieme; ingrandimenti di braccetti sinistro/destro, supporti, primo strato e scarichi di radice. Tratti della radice presenti e liberi dalle pareti degli scarichi; supporti sotto le spalle presenti e accessibili lateralmente. Zero candidati di nuove isole nello screening raster. Piccolo ponte da 1 mm sull’incisione identificativa. Distacco effettivo dei supporti e finitura da provare.',
  'Avviso conservato bed_temperature_too_high_than_filament: piano 60 °C rispetto a soglia software PLA 45 °C. Preparazione indicata: sportello anteriore aperto. Nessun altro avviso modello. Valori iniziali da profilo compatibile, non una calibrazione della bobina.',
  '',f"Stima reale dello slicer: **{e['total filament used [g]']} g, {e['estimated printing time (normal mode)']}**, brim e supporti inclusi.",'',
  'Questo provino sostituisce la R16 per la prova della penetrazione del braccetto. Il tetto completo non e stato modificato; dopo il test occorre trasferire e ricontrollare anche gli scarichi. Nessuna prova fisica o stampa avviata.','']
 (ROOT/'verifiche/RAPPORTO_VERIFICHE.md').write_text('\n'.join(lines))
 allowed={'sorgenti','slicer','CAD','stampa','anteprime','verifiche'}
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and (p.relative_to(ROOT).parts[0] in allowed or p.name=='README.md')
  and p.name not in {'SHA256.json','.DS_Store'} and '__pycache__' not in p.parts and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R17_PROVINO_BRACCETTO_PASSANTE_PLA.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for name in [*hh,'verifiche/SHA256.json']:z.write(ROOT/name,ROOT.name+'/'+name)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and len(z.namelist())==len(hh)+1
  for name,h in hh.items():assert hashlib.sha256(z.read(ROOT.name+'/'+name)).hexdigest()==h
 print(json.dumps(dict(state=state['state'],archive=str(archive),files=len(hh)+1,bytes=archive.stat().st_size,estimates=j['totals'])),flush=True)
if __name__=='__main__':main()
