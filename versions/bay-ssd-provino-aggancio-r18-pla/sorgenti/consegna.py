"""Audit e archivio R18; richiede prima una revisione visiva effettiva."""
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
 assert abs(geo['root_wall_clearance_mm']-.15)<1e-5 and abs(geo['minimum_stem_wall_clearance_mm']-.05)<1e-5
 assert abs(geo['outward_tip_bias_mm']-.1)<1e-5 and abs(geo['lateral_arm_from_finger_face_mm']-3.1)<1e-5
 assert geo['seated_overlap_mm3']<1e-5 and geo['roof_relief_unchanged_from_R17']
 assert geo['bearing_overlap_after_lift_0_4mm_mm3']>0 and len(geo['insertion_envelopes'])==14
 assert geo['reference_difference_mm3']<1e-5 and geo['previous_hashed_files_preserved']['R17']==46
 assert g.sha(ROOT/j['project'])==j['project_sha256']==r['project_sha256'] and r['all_layer_overviews_reviewed']
 assert g.sha(ROOT/j['geometry_source'])==j['geometry_sha256']
 for name,h in j['profile_hashes'].items():assert g.sha(ROOT/'slicer'/name)==h
 for name,h in r['image_hashes'].items():assert g.sha(ROOT/name)==h
 for name,h in a['outputs'].items():assert g.sha(ROOT/name)==h
 assert set(j['images'])==set(r['image_hashes']) and r['cad_image_hashes']==a['outputs']
 check=validate(ROOT/j['project'],j['items']);assert check['printable_count']==1 and check['modifier_count']==0
 with zipfile.ZipFile(ROOT/j['project']) as z:
  settings=json.loads(z.read('Metadata/project_settings.config'))
  assert 'Centauri Carbon 2' in settings['printer_model']
  expected=dict(nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',
   wall_loops='4',sparse_infill_density='20%',sparse_infill_pattern='gyroid',brim_width='5',filament_max_volumetric_speed=['5'],print_sequence='by layer',
   enable_support='1',support_style='snug',support_on_build_plate_only='0',support_top_z_distance='0.2',fuzzy_skin='disabled_fuzzy')
  for k,v in expected.items():assert settings[k]==v,(k,settings[k],v)
  warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')]
  assert warnings==j['warnings'] and all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings)
 analysis=read('verifiche/slicing/PROVINO/analisi.json')
 assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and analysis['new_wall_islands']['candidate_count']==0
 assert not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations'] and j['support_segments']>0
 j['visual_review_complete']=True;g.save(ROOT/'verifiche/slicing/PROVINO/job.json',j)
 state=dict(revision='R18_PROVINO_AGGANCIO',state='PRONTO_PER_LA_STAMPA_DEL_PROVINO',configuration=g.P['configurazione_stampa'],
  project=j['project'],project_sha256=j['project_sha256'],estimates=j['totals'],slicer_app=j['slicer_app'],slicer_engine=j['slicer_engine'],parts=1,plates=1,
  root_wall_clearance_mm=.15,minimum_stem_wall_clearance_mm=.05,outward_tip_bias_mm=.1,outward_angle_deg=geo['outward_angle_deg'],arm_length_from_finger_face_mm=3.1,
  roof_relief_unchanged_from_R17=True,geometry_verified=True,export_reopened=True,slicing_verified=True,all_layer_overviews_reviewed=True,critical_layers_sampled=True,
  prior_R17_user_fit_observation=g.P['riscontro_R17_utente'],physical_print=False,physical_fit=False,force_validated=False,FEA=False,sent_to_printer=False,full_lid_modified=False,limitations=geo['limitations'])
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state)
 e=j['slicer_estimates'];width=j['items'][0]['bounds_mm'][1][0]-j['items'][0]['bounds_mm'][0][0]
 lines=['# Verifiche R18 — lieve apertura e gioco aletta-parete ridotto','',
  '**Pronto per la stampa del provino. Presa e ritorno della R18 restano da verificare fisicamente.**','',
  'Riscontro utente sulla R17: ora i braccetti entrano bene. Il nuovo chiarimento riguarda il gioco tra aletta verticale e parete interna; il taglio nel tetto rimane identico alla R17.',
  f"Gioco alla radice 0,15 mm anziché 0,30; apertura verso esterno 0,10 mm in 12 mm ({geo['outward_angle_deg']:.4f}°). Gioco minimo del corpo dell’aletta 0,05 mm; sopra il foro, a parete continua, almeno {geo['minimum_clearance_above_window_mm']:.3f} mm. Spessore aletta 1,2 mm e braccetto lungo 3,1 mm. La punta ora supera nominalmente il filo esterno di {geo['outer_protrusion_mm']:.4f} mm, praticamente a filo: il foro e occupato per tutti i 3 mm della parete. Nessun pattino di precarico.",
  'STEP finale confrontato con il sorgente; STL e STEP orientato riaperti: un componente, mm, volume positivo, normali coerenti, mesh chiusa, zero facce degeneri o duplicate. Screening autointersezioni senza coppie rilevate; triangoli con vertici condivisi esclusi dal controllo. Nessuna riparazione della mesh.',
  'Gioco minimo misurato su una fascia del STEP finale fuori dalla larghezza del braccetto; nessuna collisione con entrambe le pareti nella posizione seduta. L’interferenza di ritenuta con alzata campione di 0,4 mm e presente; gioco verticale 0,2 mm. Quattordici inviluppi rigidi di discesa e rilascio senza collisioni, con rientro campione 3,15 mm. Si verifica lo spazio di manovra, senza FEA o prova della corsa elastica.',
  f"Controparte confrontata con STEP scocca R15: differenza {geo['reference_difference_mm3']:.8f} mm³. Revisioni precedenti conservate e rilette tramite hash: {geo['previous_hashed_files_preserved']}.",
  f"3MF nativo riaperto: un oggetto, zero modificatori, unita mm e trasformazioni valide. Ingombro pezzo {width:.3f} x 32 x 15 mm; brim 5 mm verificato sul piatto 256 x 256 e zona esclusa rispettata. App ElegooSlicer {j['slicer_app']}, motore {j['slicer_engine']}. Profili ECC2 Combo, ugello 0,4 mm, PEI testurizzato, PLA BASIC 220/60 °C, strato 0,20 mm, quattro pareti, gyroid 20%, limite 5 mm³/s; supporti snug con interfaccia 0,2 mm. Nessuna Fuzzy Skin o torre.",
  f"Tutti i {j['layers']} strati controllati nella tavola d’insieme; dettagli di entrambe le alette, supporti, radici e primo strato controllati nelle tavole dedicate. Tratti sottili presenti, spazi della radice aperti, supporti sotto i braccetti accessibili lateralmente. Screening nuove isole: zero candidati. Distacco supporti da verificare fisicamente.",
  'Avviso conservato bed_temperature_too_high_than_filament: piano 60 °C rispetto alla soglia software PLA 45 °C. Stampare con sportello anteriore aperto; valori iniziali del profilo compatibile, non calibrazione della bobina. Nessun altro avviso modello.',
  '',f"Stima reale dello slicer: **{e['total filament used [g]']} g, {e['estimated printing time (normal mode)']}**, brim e supporti inclusi.",'',
  'Nessuna stampa avviata. Il tetto completo non e stato modificato; questo provino serve al confronto R17/R18 sulla scocca esistente. Tolleranze, forza e durata non dedotte dal solo modello digitale.','']
 (ROOT/'verifiche/RAPPORTO_VERIFICHE.md').write_text('\n'.join(lines))
 allowed={'sorgenti','slicer','CAD','stampa','anteprime','verifiche'}
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and (p.relative_to(ROOT).parts[0] in allowed or p.name=='README.md')
  and p.name not in {'SHA256.json','.DS_Store'} and '__pycache__' not in p.parts and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R18_PROVINO_AGGANCIO_PLA.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for name in [*hh,'verifiche/SHA256.json']:z.write(ROOT/name,ROOT.name+'/'+name)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and len(z.namelist())==len(hh)+1
  for name,h in hh.items():assert hashlib.sha256(z.read(ROOT.name+'/'+name)).hexdigest()==h
 print(json.dumps(dict(state=state['state'],archive=str(archive),files=len(hh)+1,bytes=archive.stat().st_size,estimates=j['totals'])),flush=True)
if __name__=='__main__':main()
