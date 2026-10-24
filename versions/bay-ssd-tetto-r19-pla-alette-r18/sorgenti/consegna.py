"""Audit finale R19 e archivio completo, dopo controllo visivo dei percorsi."""
import json,zipfile,hashlib
import xml.etree.ElementTree as ET
import genera as g
from native_3mf import validate
ROOT=g.ROOT

def read(p):return json.loads((ROOT/p).read_text())
def main():
 m=read('verifiche/manifest.json');geo=read('verifiche/geometria.json');a=read('verifiche/anteprime.json');r=read('verifiche/revisione_visiva.json');j=read('verifiche/slicing/TETTO/job.json')
 assert m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json') and m['latch_parameters_sha256']==g.sha(ROOT/'sorgenti/parametri_aggancio_R18.json')
 assert geo['source_manifest_sha256']==a['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 assert len(m['parts'])==1 and geo['closed'] and geo['winding_consistent'] and geo['components']==1
 assert geo['self_intersections']['intersection_pairs']==0 and geo['degenerate_faces']==geo['duplicate_faces']==0
 p=m['parts'][0]
 for key in ['stl','step','print_step']:assert geo[key+'_sha256']==g.sha(ROOT/p[key])
 for name,h in m['reference_hashes'].items():assert g.sha(ROOT/name)==h
 assert all(c['difference_from_R18_mm3']<1e-5 for c in geo['exact_R18_latch_transfer'])
 assert geo['unchanged_outside_latch_zones_difference_mm3']<1e-5
 assert abs(geo['minimum_stem_wall_clearance_mm']-.05)<1e-5 and geo['seated_overlap_mm3']<1e-5
 assert geo['bearing_overlap_after_lift_0_4mm_mm3']>0 and len(geo['insertion_envelopes'])==14
 assert len(geo['drive_and_usb_checks'])==9 and geo['minimum_usb_clearance_mm']>=3.29
 assert g.sha(ROOT/j['project'])==j['project_sha256']==r['project_sha256']==a['project_sha256']
 assert r['all_layer_overviews_reviewed'] and g.sha(ROOT/j['geometry_source'])==j['geometry_sha256']
 for name,h in j['profile_hashes'].items():assert g.sha(ROOT/'slicer'/name)==h
 for name,h in r['image_hashes'].items():assert g.sha(ROOT/name)==h
 for name,h in a['outputs'].items():assert g.sha(ROOT/name)==h
 assert set(j['images'])==set(r['image_hashes']) and r['cad_image_hashes']==a['outputs']
 check=validate(ROOT/j['project'],j['items']);assert check['printable_count']==1 and check['modifier_count']==0
 with zipfile.ZipFile(ROOT/j['project']) as z:
  settings=json.loads(z.read('Metadata/project_settings.config'))
  assert settings['printer_model']=='Elegoo Centauri Carbon 2' and settings['printer_variant']=='0.4'
  expected=dict(nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',
   wall_loops='4',sparse_infill_density='20%',sparse_infill_pattern='gyroid',brim_width='5',filament_max_volumetric_speed=['5'],print_sequence='by layer',
   enable_support='1',support_style='snug',support_on_build_plate_only='0',support_top_z_distance='0.2',fuzzy_skin='disabled_fuzzy')
  for k,v in expected.items():assert settings[k]==v,(k,settings[k],v)
  warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')]
  assert warnings==j['warnings'] and all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings)
 analysis=read('verifiche/slicing/TETTO/analisi.json')
 assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and analysis['new_wall_islands']['candidate_count']==0
 assert not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations'] and j['support_segments']>0 and j['layers']==145
 j['visual_review_complete']=True;g.save(ROOT/'verifiche/slicing/TETTO/job.json',j)
 state=dict(revision='R19_TETTO_COMPLETO_ALETTE_R18',state='PRONTO_PER_LA_STAMPA_DEL_TETTO_PROTOTIPO',configuration=g.P['configurazione_stampa'],
  project=j['project'],project_sha256=j['project_sha256'],estimates=j['totals'],slicer_app=j['slicer_app'],slicer_engine=j['slicer_engine'],parts=1,plates=1,
  exact_R18_latch_transfer=True,root_wall_clearance_mm=.15,minimum_stem_wall_clearance_mm=.05,outward_tip_bias_mm=.1,arm_length_mm=3.1,
  rear_tail_included=True,geometry_verified=True,export_reopened=True,slicing_verified=True,all_145_layers_reviewed=True,critical_layers_sampled=True,
  physical_print=False,physical_fit=False,thermal_test=False,force_validated=False,FEA=False,sent_to_printer=False,full_lid_modified=True,
  reference_shell='R15 esistente; non inclusa nel piatto',hardware_bom={},limitations=geo['limitations'])
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state)
 e=j['slicer_estimates'];lines=['# Verifiche R19 — tetto completo con alette R18','',
  '**Pronto per la stampa del tetto prototipo. Nessuna stampa avviata; accoppiamento fisico R19 da verificare.**','',
  'Un solo oggetto stampabile e un solo piatto, PLA BASIC. Due agganci, strisce flessibili e scarichi trasferiti dal provino R18. Confronto booleano dei due agganci esportati con il STEP finale R18: differenza zero. Fuori dalle due zone locali la differenza rispetto al tetto STEP R15 e zero: coda, riferimenti anteriori, bordi e tagli delle feritoie conservati.',
  f"Ingombro orientato di stampa 90,083 x 109 x 29 mm, tetto spesso 3 mm, aletta spessa 1,2 mm, braccetto lungo 3,1 mm. Gioco radice 0,15 mm; apertura esterna 0,10 mm su 12 mm, circa 0,4775°. Gioco minimo aletta-parete dal STEP riaperto {geo['minimum_stem_wall_clearance_mm']:.3f} mm, sopra il foro {geo['minimum_gap_above_window_mm']:.3f} mm.",
  f"STL, STEP e STEP orientato riaperti: un solido/componente, scala mm, volume positivo, normali coerenti, mesh chiusa, {geo['faces']} triangoli, zero facce degeneri o duplicate. Screening autointersezioni: zero coppie rilevate; triangoli con vertici condivisi esclusi. Nessuna riparazione automatica della mesh.",
  f"Nessuna interferenza con scocca esistente a riposo. Ritenuta geometrica presente sollevando di 0,4 mm. Quattordici inviluppi rigidi di discesa/rilascio senza collisioni, con rientro campione fino a 3,15 mm: spazio di manovra verificato, nessuna FEA. Nove combinazioni modello/slot senza collisioni con SSD nominali e ingombri USB 20 x 20 x 50 mm. Minima distanza nominale tetto-USB {geo['minimum_usb_clearance_mm']:.2f} mm; la coda termina a quota Z57. Quote reali dei connettori da verificare fisicamente.",
  f"Revisioni precedenti conservate e verificate tramite hash: {geo['previous_hashed_files_preserved']}. La R17 entra bene secondo l’utente; non e stato comunicato un nuovo riscontro fisico R18, e non e dedotta la presa del tetto completo dalla sola geometria del provino.",
  f"3MF nativo riaperto indipendentemente: un oggetto, zero modificatori, unita e trasformazioni valide. Brim 5 mm, ingombro e percorsi entro piano 256 x 256 mm, zona esclusa [246..256] x [0..20] rispettata. G-code generato da ElegooSlicer e incorporato, senza modifica manuale. App {j['slicer_app']} / motore {j['slicer_engine']}. Profilo macchina 'Elegoo Centauri Carbon 2 0.4 nozzle', stessa configurazione ECC2 Combo monocolore delle revisioni precedenti; nessun riuso di profilo Centauri Carbon di prima generazione.",
  'PEI testurizzato, ELEGOO PLA BASIC 220/60 °C, strato 0,20 mm, quattro pareti, gyroid 20%, limite 5 mm³/s. Supporti normali snug sotto i braccetti, interfaccia 0,2 mm, abilitati anche sopra il modello; nessun supporto aggiunto alla coda. Nessuna Fuzzy Skin o torre. Parametri iniziali del profilo compatibile, non calibrazione della bobina.',
  f"Tutti i {j['layers']} strati visti nelle due tavole d’insieme. Dettagli di entrambe le alette, radici, primo strato, coda e ponti piu lunghi visionati. Supporti presenti sotto i braccetti, accessibili lateralmente; elementi sottili presenti e scarichi aperti. Zero candidati di nuove isole nello screening raster. Distacco effettivo dei supporti e forza degli agganci da verificare sulla stampa.",
  'Avviso conservato bed_temperature_too_high_than_filament (1000C001): piano 60 °C rispetto alla soglia software PLA 45 °C. Stampare con sportello anteriore aperto. Nessun altro avviso modello rilevato.',
  '',f"Stima dello slicing: **{e['total filament used [g]']} g / {e['estimated printing time (normal mode)']}**, brim e supporti inclusi.",'',
  'Esito limitato alla preparazione digitale del tetto. Nessuna validazione fisica, termica, della forza o della durata.','']
 (ROOT/'verifiche/RAPPORTO_VERIFICHE.md').write_text('\n'.join(lines))
 allowed={'sorgenti','slicer','CAD','stampa','anteprime','verifiche'}
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and (p.relative_to(ROOT).parts[0] in allowed or p.name=='README.md')
  and p.name not in {'SHA256.json','.DS_Store'} and '__pycache__' not in p.parts and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R19_TETTO_COMPLETO_PLA_BASIC.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for name in [*hh,'verifiche/SHA256.json']:z.write(ROOT/name,ROOT.name+'/'+name)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and len(z.namelist())==len(hh)+1
  for name,h in hh.items():assert hashlib.sha256(z.read(ROOT.name+'/'+name)).hexdigest()==h
 print(json.dumps(dict(state=state['state'],project=j['project'],archive=str(archive),files=len(hh)+1,bytes=archive.stat().st_size,estimates=j['totals'])),flush=True)
if __name__=='__main__':main()
