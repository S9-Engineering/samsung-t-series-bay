"""Audit e pacchetto R16: soli provini diagnostici, nessun invio alla macchina."""
import json,zipfile,hashlib
import xml.etree.ElementTree as ET
import genera as g
from native_3mf import validate
ROOT=g.ROOT

def read(path):return json.loads((ROOT/path).read_text())
def main():
 man=read('verifiche/manifest.json');geo=read('verifiche/geometria.json');preview=read('verifiche/anteprime.json');review=read('verifiche/revisione_visiva.json')
 assert man['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 assert geo['source_manifest_sha256']==preview['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 assert geo['result']=='PASS_GEOMETRIA_NOMINALE' and len(geo['parts'])==len(man['parts'])==3
 assert geo['baseline_left_latch_difference_mm3']<1e-5 and geo['reference_window_difference_mm3']<1e-5
 for p,c in zip(man['parts'],geo['parts']):
  assert p['stl_sha256']==c['stl_sha256']==g.sha(ROOT/p['stl'])
  assert c['step_sha256']==g.sha(ROOT/p['step']) and c['closed'] and c['winding'] and c['one_solid']
  assert c['self_intersections']['intersection_pairs']==0 and c['translated_envelope_collisions_mm3']==0
 for path,h in preview['outputs'].items():assert g.sha(ROOT/path)==h
 jobs=[]
 for mode,count in [('RAPIDO',1),('CONFRONTO',3)]:
  job=read(f'verifiche/slicing/{mode}/job.json');assert g.sha(ROOT/job['project'])==job['project_sha256']
  assert g.sha(ROOT/job['geometry_source'])==job['geometry_sha256']
  for n,h in job['profile_hashes'].items():assert g.sha(ROOT/'slicer'/n)==h
  native=validate(ROOT/job['project'],job['items']);assert native['printable_count']==count and native['modifier_count']==0
  with zipfile.ZipFile(ROOT/job['project']) as z:
   s=json.loads(z.read('Metadata/project_settings.config'))
   expected=dict(nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],
    layer_height='0.2',wall_loops='4',sparse_infill_density='20%',sparse_infill_pattern='gyroid',brim_width='5',filament_max_volumetric_speed=['5'],
    fuzzy_skin='disabled_fuzzy',print_sequence='by layer',enable_support='1',support_style='snug',support_on_build_plate_only='0',support_top_z_distance='0.2')
   assert 'Centauri Carbon 2' in s['printer_model']
   for k,v in expected.items():assert s[k]==v,(k,s[k],v)
   warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')]
   assert warnings==job['warnings'] and all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings)
  a=read(f'verifiche/slicing/{mode}/analisi.json')
  assert a['all_layers_nonempty'] and a['layer_count_matches_header'] and a['new_wall_islands']['candidate_count']==0
  assert not a['out_of_bed_layers'] and not a['profile_exclusion_zone_violations']
  assert job['support_segments']>0 and job['support_z_range_mm'][1]>=12
  r=review['projects'][mode];assert r['project_sha256']==job['project_sha256'] and r['all_layers_overview_reviewed']
  for p,h in r['image_hashes'].items():assert g.sha(ROOT/p)==h
  assert f'verifiche/slicing/{mode}/TUTTI_STRATI.png' in r['image_hashes']
  job['visual_review_complete']=True;g.save(ROOT/f'verifiche/slicing/{mode}/job.json',job);jobs.append(job)
 state=dict(revision='R16_PROVINI',state='PRONTO_PER_LA_STAMPA_DEL_PROVINO',configuration=g.P['configurazione_stampa'],
  default_project=jobs[0]['project'],default_estimates=jobs[0]['totals'],comparison_project=jobs[1]['project'],comparison_estimates=jobs[1]['totals'],
  models=3,native_projects=2,plates_per_project=1,alternative_projects_not_additive=True,slicer_app=jobs[0]['slicer_app'],slicer_engine=jobs[0]['slicer_engine'],
  geometry_verified=True,export_reopened=True,slicing_verified=True,all_layer_overviews_reviewed=True,critical_layers_sampled=True,
  observed_problem='Utente conferma dente poco sporgente nella finestrella; prova R15 non soddisfacente',
  default_change='Sporgenza nominale 0,6 -> 1,0 mm per lato, dente con spalla di ritenuta, lunghezza aletta invariata',
  physical_print=False,physical_fit=False,force_validated=False,FEA=False,full_lid_modified=False,sent_to_printer=False,
  limitations=geo['limitations'],warning_preparation=jobs[0]['warning_preparation'])
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state)
 lines=['# Verifiche R16 — provini aggancio','',
  '**Pronto per la stampa del provino. Misure, elasticita, presa e durata sul pezzo reale ancora da verificare.**','',
  'Tre STL chiusi, normali coerenti, un componente per pezzo, volume positivo; nessuna faccia degenere/duplicata e nessuna coppia rilevata nello screening autointersezioni (escluse coppie con vertici condivisi). Scala millimetrica e confronto STEP/STL orientati verificati. Sei STEP singoli dei provini e due STEP di riferimento delle pareti riaperti.',
  f"Linguetta I confrontata con il STEP finale R15 nella regione dell’aggancio: differenza {geo['baseline_left_latch_difference_mm3']:.8f} mm³. Finestra confrontata sulla scocca R15: differenza {geo['reference_window_difference_mm3']:.8f} mm³. Verificati e conservati {geo['R15_hashed_files_preserved']} file hashati R15.",
  'Sporgenza nominale I 0,6 mm; II/III 1,0 mm. Larghezza alette 9 mm nelle finestre 9,6 mm: 0,3 mm per estremita. Interferenza intenzionale 0,15 mm solo sui pattini; inviluppo traslato verso interno privo di altre collisioni. Penetrazione laterale nell’inviluppo 0,45 / 0,85 / 0,85 mm; gioco verticale 0,55 / 0,39 / 0,20 mm. Nessun calcolo della forza o della deformazione elastica.',
  'Traversa con due alette alla distanza della scocca reale, stesso orientamento di stampa e radici della R15. Traversa piena piu rigida del tetto: prova locale di misure e ritenuta, non validazione meccanica del tetto completo. Scocca da usare come controparte; non fornita una nuova porzione stampabile di case.',
  'Due alternative native ElegooSlicer, un piatto ciascuna: solo III oppure confronto I/II/III. Riapertura per ID e percorsi XML; unita, trasformazioni, quantita e ingombri con brim 5 mm e zona esclusa verificati. Stampante ECC2 Combo / ugello 0,4 / PEI testurizzato / PLA BASIC 220/60 °C, strati 0,2 mm, quattro pareti, gyroid 20%, massimo 5 mm³/s. Nessuna torre o Fuzzy Skin.',
  'Supporti abilitati soltanto sul III, verificati sia nelle impostazioni per oggetto sia nei percorsi effettivi. Colonne accanto alle alette fino a Z12 mm in stampa; spalla a partire da Z12,2 mm. Interfaccia a 0,2 mm, due strati; accesso laterale libero per rimuoverli. Rimovibilita e finitura fisiche non provate.',
  'Tutti i 75 strati di ciascuna alternativa esaminati nelle tavole d’insieme; dettagli ingranditi di primo strato, radici, denti e supporti. Zero candidati di nuove isole esterne nello screening raster, nessuna violazione di piano/zona esclusa. Piccoli ponti da 1 mm sulle tacche incise presenti nel primo millimetro.',
  'Avviso mantenuto bed_temperature_too_high_than_filament: piano a 60 °C rispetto alla soglia software PLA 45 °C. Preparazione indicata: sportello anteriore aperto. Nessun altro avviso modello. Parametri da profilo compatibile, non da calibrazione fisica della bobina.','',
  '| Alternativa | Oggetti | Strati | PLA stimato | Tempo stimato |','| --- | ---: | ---: | ---: | --- |']
 for job in jobs:
  e=job['slicer_estimates'];lines.append(f"| {job['name']} | {len(job['items'])} | {job['layers']} | {e['total filament used [g]']} g | {e['estimated printing time (normal mode)']} |")
 lines+=['','Stime effettive dello slicer con brim e supporti; alternative da non sommare. Nessuna stampa fisica o invio alla macchina. Il tetto completo R15 non e stato modificato.','']
 (ROOT/'verifiche/RAPPORTO_VERIFICHE.md').write_text('\n'.join(lines))
 folders={'sorgenti','slicer','CAD','stampa','anteprime','verifiche'}
 hashes={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and (p.relative_to(ROOT).parts[0] in folders or p.name=='README.md')
  and p.name not in {'SHA256.json','.DS_Store'} and '__pycache__' not in p.parts and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hashes)
 archive=ROOT/'BAY_R16_PROVINI_AGGANCIO_PLA.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in [*hashes,'verifiche/SHA256.json']:z.write(ROOT/p,ROOT.name+'/'+p)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and len(z.namelist())==len(hashes)+1
  for p,h in hashes.items():assert hashlib.sha256(z.read(ROOT.name+'/'+p)).hexdigest()==h
 print(json.dumps(dict(state=state['state'],archive=str(archive),files=len(hashes)+1,bytes=archive.stat().st_size,quick_estimate=jobs[0]['totals'])),flush=True)
if __name__=='__main__':main()
