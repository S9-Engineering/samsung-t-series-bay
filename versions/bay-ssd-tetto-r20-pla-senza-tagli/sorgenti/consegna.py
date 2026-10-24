"""Audit finale R20 e archivio completo, dopo controllo visivo dei percorsi."""
import json,zipfile,hashlib
import xml.etree.ElementTree as ET
import genera as g
from native_3mf import validate
ROOT=g.ROOT

def read(p):return json.loads((ROOT/p).read_text())
def main():
 if (ROOT/'verifiche/RITIRO_R20.json').exists():
  raise SystemExit('R20 ritirata: non riconsegnare come pronta per la stampa. Usare la R19; vedere verifiche/RITIRO_R20.json.')
 m=read('verifiche/manifest.json');geo=read('verifiche/geometria.json');a=read('verifiche/anteprime.json');r=read('verifiche/revisione_visiva.json');j=read('verifiche/slicing/TETTO/job.json')
 assert m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json') and m['latch_parameters_sha256']==g.sha(ROOT/'sorgenti/parametri_aggancio_R18.json')
 assert geo['source_manifest_sha256']==a['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 assert len(m['parts'])==1 and geo['closed'] and geo['winding_consistent'] and geo['components']==1
 assert geo['self_intersections']['intersection_pairs']==0 and geo['degenerate_faces']==geo['duplicate_faces']==0
 p=m['parts'][0]
 for key in ['stl','step','print_step']:assert geo[key+'_sha256']==g.sha(ROOT/p[key])
 for name,h in m['reference_hashes'].items():assert g.sha(ROOT/name)==h
 assert geo['no_top_release_slots'] and geo['top_roof_difference_R15_mm3']<1e-5
 assert all(c['lower_finger_and_peg_difference_R18_mm3']<1e-5 and c['free_beam_difference_after_translation_mm3']<1e-5 for c in geo['lower_latch_R18_and_hidden_spring_checks'])
 assert geo['unchanged_remainder_difference_mm3']<1e-5
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
 assert all(j['hidden_flexure_support_segments'][side]>0 for side in ['left','right'])
 j['visual_review_complete']=True;g.save(ROOT/'verifiche/slicing/TETTO/job.json',j)
 state=dict(revision='R20_TETTO_SENZA_TAGLI_SUPERIORI',state='PRONTO_PER_LA_STAMPA_DEL_TETTO_PROTOTIPO',configuration=g.P['configurazione_stampa'],
  project=j['project'],project_sha256=j['project_sha256'],estimates=j['totals'],slicer_app=j['slicer_app'],slicer_engine=j['slicer_engine'],parts=1,plates=1,
  top_release_slots_removed=True,lower_R18_peg_position_preserved=True,new_hidden_flexure=True,hidden_beam_section_mm=[1.2,3],hidden_beam_free_length_mm=18,roof_gap_mm=3,minimum_stem_wall_clearance_mm=.05,arm_length_mm=3.1,
  rear_tail_included=True,geometry_verified=True,export_reopened=True,slicing_verified=True,all_145_layers_reviewed=True,critical_layers_sampled=True,
  physical_print=False,physical_fit=False,thermal_test=False,force_validated=False,FEA=False,sent_to_printer=False,full_lid_modified=True,
  reference_shell='R15 esistente; non inclusa nel piatto',hardware_bom={},limitations=geo['limitations'])
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state)
 e=j['slicer_estimates'];lines=['# Verifiche R20 — tetto senza tagli attorno alle alette','',
  '**Pronto per la stampa del tetto prototipo; attacco interno nuovo, ancora da provare fisicamente.**','',
  'Tagli di scarico eliminati dalla lastra superiore. Lastra e feritoie orizzontali confrontate con il STEP R15: differenza zero. Pattern sui fianchi del case conservato, scocca di riferimento immutata e non inclusa nel piatto.',
  'Flessura spostata sotto il tetto, a Z77..80, con 3 mm liberi fino alla superficie interna Z83. Tratto libero 18 mm, sezione 1,2 x 3 mm, come il tratto della R18 ma traslato di 6 mm verso il basso. Ancoraggio anteriore nuovo, collegato alla lastra. Porzione inferiore dell’aletta e braccetto coincidono con la R18 nelle zone confrontate. L’attacco e differente e non si assume la stessa forza o durata.',
  f"Ingombro orientato 90,083 x 109 x 29 mm. Braccetto lungo 3,1 mm, inclinazione esterna della porzione verticale circa 0,4775°. Gioco minimo aletta-parete {geo['minimum_stem_wall_clearance_mm']:.3f} mm e, sopra la finestrella, {geo['minimum_gap_above_window_mm']:.3f} mm. Assenza di materiale nel gioco da 3 mm sopra il tratto libero verificata dal STEP esportato.",
  f"STL, STEP e STEP orientato riaperti: un solido/componente, millimetri, volume positivo, normali coerenti, mesh chiusa, {geo['faces']} triangoli; zero facce degeneri o duplicate. Screening autointersezioni senza coppie rilevate; triangoli con vertici condivisi esclusi. Nessuna riparazione automatica.",
  f"Nessuna collisione nominale a riposo con la scocca. Interferenza di ritenuta presente alzando di 0,4 mm. Quattordici inviluppi rigidi di discesa/rilascio controllati senza collisioni, con rientro campione fino a 3,15 mm: non simulano la flessione. Nove abbinamenti SSD/slot e relativi ingombri USB 20 x 20 x 50 mm senza collisioni. Distanza minima nominale dal coperchio agli ingombri USB {geo['minimum_usb_clearance_mm']:.2f} mm.",
  f"Revisioni precedenti conservate e verificate tramite hash: {geo['previous_hashed_files_preserved']}. Scocca, coda e riferimenti anteriori conservati fuori dalle zone locali degli agganci.",
  f"3MF nativo riaperto indipendentemente: un oggetto, zero modificatori, unità e trasformazioni valide. Brim 5 mm, ingombri e percorsi entro 256 x 256 mm e fuori dalla zona esclusa. App ElegooSlicer {j['slicer_app']}, motore {j['slicer_engine']}; G-code dello slicer incorporato senza modifica manuale. ECC2 Combo, ugello 0,4 mm, PEI testurizzato, PLA BASIC 220/60 °C, strato 0,20 mm, quattro pareti, gyroid 20%, 5 mm³/s.",
  f"Tutti i 145 strati visionati e dettagli di entrambe le alette, primo strato, attacchi interni, coda e ponti controllati. Supporti snug sotto i braccetti e nel gioco fra tetto e flessure; rilevati supporti sotto entrambi i tratti liberi: {j['hidden_flexure_support_segments']}. Supporti accessibili dal lato interno, con gioco nominale 3 mm. Rimozione fisica ancora da verificare. Nessuna isola involontaria osservata, zero candidati nello screening raster. La coda cresce senza supporti.",
  'Avviso mantenuto bed_temperature_too_high_than_filament (1000C001): piano 60 °C rispetto alla soglia software PLA 45 °C. Stampare con sportello anteriore aperto. Nessun altro avviso modello. Parametri iniziali del profilo compatibile, non calibrazione della bobina.',
  '',f"Stima reale dello slicer: **{e['total filament used [g]']} g / {e['estimated printing time (normal mode)']}**, supporti e brim inclusi.",'',
  'Nessuna stampa avviata. Forza, ritorno, durata, tolleranze reali e distacco dei supporti della nuova radice interna non verificati fisicamente. Nessuna prova termica.','']
 (ROOT/'verifiche/RAPPORTO_VERIFICHE.md').write_text('\n'.join(lines))
 allowed={'sorgenti','slicer','CAD','stampa','anteprime','verifiche'}
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and (p.relative_to(ROOT).parts[0] in allowed or p.name=='README.md')
  and p.name not in {'SHA256.json','.DS_Store'} and '__pycache__' not in p.parts and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R20_TETTO_SENZA_TAGLI_PLA_BASIC.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for name in [*hh,'verifiche/SHA256.json']:z.write(ROOT/name,ROOT.name+'/'+name)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and len(z.namelist())==len(hh)+1
  for name,h in hh.items():assert hashlib.sha256(z.read(ROOT.name+'/'+name)).hexdigest()==h
 print(json.dumps(dict(state=state['state'],project=j['project'],archive=str(archive),files=len(hh)+1,bytes=archive.stat().st_size,estimates=j['totals'])),flush=True)
if __name__=='__main__':main()
