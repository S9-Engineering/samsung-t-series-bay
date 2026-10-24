"""Audit R21: cinematica, sorgenti, export, due piatti e revisione visiva effettiva."""
import json,zipfile,hashlib
import genera as g
from native_3mf import validate
ROOT=g.ROOT

def read(p):return json.loads((ROOT/p).read_text())
def main():
 m=read('verifiche/manifest.json');geo=read('verifiche/geometria.json');a=read('verifiche/anteprime.json');r=read('verifiche/revisione_visiva.json');jobs=read('verifiche/slicing/riepilogo.json')['jobs']
 assert m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 assert geo['source_manifest_sha256']==a['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 assert len(m['parts'])==3 and not m['elastic_latch'] and geo['without_elastic_installation']
 for p in m['parts']:
  q=next(q for q in geo['parts'] if q['name']==p['name']);assert q['closed'] and q['components']==1 and q['winding'] and q['positive_volume']
  assert q['degenerate_faces']==q['duplicate_faces']==q['self_intersections']['intersection_pairs']==0
  for k in ['stl','step','print_step']:assert g.sha(ROOT/p[k])==q[k+'_sha256']
 assert len(geo['key_paths'])==86 and len(geo['ssd_checks'])==9
 assert geo['minimum_pin_drive_distance_mm']>1.29 and geo['minimum_usb_distance_mm']>3.29
 assert a['outputs']==r['cad_image_hashes']
 for n,h in a['outputs'].items():assert g.sha(ROOT/n)==h
 for j in jobs:
  mode=j['mode'];live=read(f'verifiche/slicing/{mode}/job.json');assert live['project_sha256']==j['project_sha256']==r['projects'][mode]
  assert g.sha(ROOT/j['project'])==j['project_sha256'] and g.sha(ROOT/j['geometry_source'])==j['geometry_sha256']
  for n,h in j['profile_hashes'].items():assert g.sha(ROOT/'slicer'/n)==h
  check=validate(ROOT/j['project'],j['items']);assert check['printable_count']==3 and check['modifier_count']==0
  assert set(j['images'])==set(r['image_hashes'][mode])
  for n,h in r['image_hashes'][mode].items():assert g.sha(ROOT/n)==h
  analysis=read(f'verifiche/slicing/{mode}/analisi.json');assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations'] and analysis['new_wall_islands']['candidate_count']==0
  with zipfile.ZipFile(ROOT/j['project']) as z:
   s=json.loads(z.read('Metadata/project_settings.config'))
   expected=dict(printer_model='Elegoo Centauri Carbon 2',nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',wall_loops='4',sparse_infill_density='100%',sparse_infill_pattern='rectilinear',brim_width='5',filament_max_volumetric_speed=['5'],print_sequence='by layer',enable_support='0',fuzzy_skin='disabled_fuzzy')
   for k,v in expected.items():assert s[k]==v,(k,s[k],v)
  assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in j['warnings'])
  j['visual_review_complete']=True;g.save(ROOT/f'verifiche/slicing/{mode}/job.json',j)
 g.save(ROOT/'verifiche/slicing/riepilogo.json',dict(jobs=jobs,note='I due progetti sono alternativi: provino per la verifica iniziale e tetto completo. I perni sono identici e riutilizzabili.'))
 state=dict(revision='R21_BAIONETTE_RIGIDE',state='PRONTO_PER_LA_STAMPA_DEL_PROTOTIPO_CON_PROVA_PRELIMINARE',configuration=g.P['configurazione_stampa'],projects={j['mode']:dict(path=j['project'],sha256=j['project_sha256'],estimates=j['totals']) for j in jobs},parts_full_kit=3,types_full_kit=2,elastic_arms=False,kinematics_verified=True,export_reopened=True,slicing_verified=True,all_layers_reviewed=True,physical_fit=False,physical_print=False,force_validated=False,thermal_test=False,sent_to_printer=False,hardware_bom={},prerequisite='Verificare sulla scocca esistente il provino R21 e i due perni prima della stampa completa.',limitations=geo['limitations'])
 g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state)
 lines=['# Verifiche R21 — perni rigidi a quarto di giro','',
  '**Preparazione digitale completata. L’incastro reale deve essere verificato sulla traversa di prova prima del tetto completo.**','',
  'Il riscontro utente R19 segnala alette ancora troppo deboli. R21 abbandona i bracci elastici: tetto con due blocchi di ricezione e due perni rimovibili, inseriti orizzontalmente e ruotati di 90 gradi. Nessuna ferramenta. Tutto PLA BASIC, senza supporti di stampa e con riempimento rettilineo pieno al 100%.',
  'Sorgenti ed export riaperti: tre tipi di oggetto, un solido/componente per STL, millimetri, normali coerenti, volume positivo, zero facce degeneri o duplicate e nessuna coppia nello screening autointersezioni (triangoli con vertici condivisi esclusi). Nessuna riparazione automatica.',
  'Scocca esistente R15 non modificata. Verificati sette livelli di discesa del tetto, 23 posizioni di inserimento per lato, rotazione da 0 a 90 gradi ogni 5 gradi e interferenze di ritenuta dei due perni in posizione chiusa. Dopo rotazione il traversino non passa dal foro; alzata del perno contro la finestra e del tetto contro il perno producono le interferenze attese. Sono verifiche cinematiche con parti rigide, non prove di carico o forza.',
  f"Nove combinazioni modello SSD/slot controllate. Distanza minima nominale perni-SSD {geo['minimum_pin_drive_distance_mm']:.2f} mm; distanza minima dagli ingombri USB 20 x 20 x 50 mm {geo['minimum_usb_distance_mm']:.2f} mm. Supporti del provino e del tetto confrontati geometricamente: identici. Vecchi file conservati: {geo['previous_files_preserved']}.",
  '3MF nativi riaperti indipendentemente: ciascuno un piatto con tre oggetti, unità e trasformazioni valide, brim 5 mm e ingombri entro il volume utile e fuori dalla zona esclusa. App ElegooSlicer 1.5.3.5 / motore 2.4.2; configurazione ECC2 Combo 0,4 mm, PEI testurizzato, ELEGOO PLA BASIC, 220/60 °C, strato 0,20 mm, quattro pareti, 100% rettilineo, limite 5 mm³/s. Parametri iniziali compatibili, non calibrazione della bobina.',
  'Percorsi completi dei due lavori visionati: 88 strati del provino e 145 del tetto, più dettagli di perni, fori nei supporti rigidi, primo strato, chiusure e ponti. Perni stampati piatti con gambo continuo. Ponti dei fori circa 4,8 mm; interni ispezionabili dai due lati. Zero candidati di nuove isole nello screening raster. Assenza di percorsi di supporto confermata.',
  'Avviso conservato bed_temperature_too_high_than_filament (1000C001), piano 60 °C contro soglia software PLA 45 °C: stampare con sportello anteriore aperto. Nessun altro avviso modello. Nessuna Fuzzy Skin o torre di spurgo.','']
 for j in jobs:lines.append(f"- {j['mode']}: {j['slicer_estimates']['total filament used [g]']} g / {j['slicer_estimates']['estimated printing time (normal mode)']}, brim incluso.")
 lines+=['','La baionetta non ha un fermo angolare elastico: la posizione chiusa e indicata dalla paletta verticale; per estrarre serve riallinearla orizzontalmente. Cattura geometrica verificata, resistenza a rotazioni accidentali e durata non provate.','Nessuna stampa avviata. Tolleranze, ponte reale, tenuta e cicli di apertura devono passare la verifica fisica sul provino.',
  '', 'Riferimento progettuale consultato: [Formlabs, design degli incastri stampati](https://formlabs.com/eu/blog/designing-3d-printed-snap-fit-enclosures/). La dipendenza dei cantilever da materiale, deformazione e orientamento motiva il cambio di meccanismo; la soluzione a perni e una scelta di questo progetto, non una prestazione certificata dalla fonte.','']
 (ROOT/'verifiche/RAPPORTO_VERIFICHE.md').write_text('\n'.join(lines))
 allowed={'sorgenti','slicer','CAD','stampa','anteprime','verifiche'}
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and (p.relative_to(ROOT).parts[0] in allowed or p.name=='README.md') and p.name not in ['SHA256.json','.DS_Store'] and '__pycache__' not in p.parts and p.suffix!='.zip'}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R21_PERNI_RIGIDI_PLA_BASIC.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for n in [*hh,'verifiche/SHA256.json']:z.write(ROOT/n,ROOT.name+'/'+n)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for n,h in hh.items():assert hashlib.sha256(z.read(ROOT.name+'/'+n)).hexdigest()==h
 print(json.dumps(dict(state=state['state'],archive=str(archive),files=len(hh)+1,projects=state['projects'])),flush=True)
if __name__=='__main__':main()
