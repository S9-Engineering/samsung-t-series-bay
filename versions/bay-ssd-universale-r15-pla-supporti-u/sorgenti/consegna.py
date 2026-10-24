"""Audit e archivio finale R15 PLA: quattro parti uniche su un piatto, S9 in rilievo."""
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
import genera as g
from native_3mf import validate
ROOT=g.ROOT

def read(path):return json.loads((ROOT/path).read_text())
def duration(seconds):
    h,r=divmod(int(seconds),3600);m,s=divmod(r,60)
    return f'{h} h {m:02d} min {s:02d} s'

def main():
    man=read('verifiche/manifest.json');geo=read('verifiche/geometria.json')
    continuity=read('verifiche/confronto_revisioni.json');previews=read('verifiche/anteprime.json')
    slicing=read('verifiche/slicing/riepilogo.json');review=read('verifiche/revisione_visiva.json')
    plates=read('verifiche/piatti.json')['plates']
    assert continuity['result']=='PASS' and continuity['body_identical']
    assert continuity['body_symmetric_difference_mm3']<1e-5 and continuity['roof_and_grille_difference_mm3']<1e-5
    assert continuity['body_step_sha256']==g.sha(ROOT/'CAD/scocca_R15.step')
    assert continuity['lid_step_sha256']==g.sha(ROOT/'CAD/coperchio_R15.step')
    assert geo['lid_preload']['intended_contact_solids']==2 and geo['lid_preload']['envelope_intersection_mm3']<1e-5
    assert geo['lid_preload']['per_side_mm']==.15 and geo['U_cradles']['wall_min_mm']>=2.4
    assert geo['result']=='PASS_DIGITALE_QUOTE_NOMINALI' and geo['sharp_external_edges_verified']
    assert geo['source_manifest_sha256']==previews['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
    assert geo['source_parameters_sha256']==man['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
    assert len(man['parts'])==len(geo['export_checks'])==4 and man['kit_printed_parts']==6
    assert len(geo['model_slot_cases'])==9 and geo['assignments_checked']==27
    assert geo['logo_verified']['emboss_mm']==.4 and geo['logo_verified']['fused_with_shell']
    assert man['logo_contours_sha256']==g.sha(ROOT/'sorgenti'/g.P['logo_frontale']['sorgente'])
    for p,q in zip(man['parts'],geo['export_checks']):
        assert p['name']==q['name']
        assert p['stl_sha256']==q['stl_sha256']==g.sha(ROOT/p['stl'])
        assert q['step_sha256']==g.sha(ROOT/p['step'])
        assert q['mesh_closed'] and q['winding_consistent'] and q['components']==1
        assert q['self_intersections']['intersection_pairs']==0
    for logo in read('verifiche/provenienza_loghi.json')['logos']:
        assert g.sha(ROOT/logo['source_png'])==logo['source_png_sha256']
        assert g.sha(ROOT/logo['vector_svg'])==logo['vector_svg_sha256']
    for p,h in previews['outputs'].items():assert g.sha(ROOT/p)==h
    assert len(previews['outputs'])==11
    assert len(plates)==len(slicing['jobs'])==2 and [len(p['items']) for p in plates]==[5,6]
    assert len(geo['usb_cases'])==9 and all(c['intersections_mm3']<1e-5 and c['vertical_clearance_mm']>=3 for c in geo['usb_cases'])
    assert geo['assignments_include_nominal_usb_keepouts']
    assert geo['rear_tail']['parameters']==g.P['retro_coperchio']
    assert geo['rear_tail']['axial_clearance_mm']==2 and geo['rear_tail']['minimum_nominal_usb_clearance_mm']>=3
    assert not any('PROVINO' in p.name.upper() for p in (ROOT/'stampa').rglob('*'))
    native=[]
    for plate,job in zip(plates,slicing['jobs']):
        assert plate['name']==job['name'] and job['group'] in ('kit','ricambi')
        assert plate['sha256']==job['geometry_sha256']==g.sha(ROOT/plate['geometry_3mf'])
        for n,h in job['profile_hashes'].items():assert g.sha(ROOT/'slicer'/n)==h
        path=ROOT/job['project'];assert g.sha(path)==job['project_sha256']
        r=review['projects'][job['name']]
        assert r['project_sha256']==job['project_sha256'] and r['reviewed']
        for p,h in r['image_hashes'].items():assert g.sha(ROOT/p)==h
        detail=read(f"verifiche/slicing/{job['name']}/tavole_revisione.json")
        assert set(detail['all_layers_zoom']).issubset(r['image_hashes'])
        check=validate(path,plate['items'])
        assert check['printable_count']==len(plate['items']) and check['modifier_count']==0
        with zipfile.ZipFile(path) as z:
            settings=json.loads(z.read('Metadata/project_settings.config'))
            assert 'Centauri Carbon 2' in settings['printer_model']
            expected=dict(nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],
                nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',wall_loops='4',
                sparse_infill_density='20%',sparse_infill_pattern='gyroid',brim_width='5',
                filament_max_volumetric_speed=['5'],enable_support='0',fuzzy_skin='disabled_fuzzy',print_sequence='by layer')
            for k,v in expected.items():assert settings[k]==v,(k,settings[k],v)
            config=ET.fromstring(z.read('Metadata/model_settings.config'))
            assert all(e.get('value')=='disabled_fuzzy' for e in config.iter('metadata') if e.get('key')=='fuzzy_skin')
            warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')]
            assert warnings==job['model_warnings']
            assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings)
            assert len([p for p in z.namelist() if p.endswith('.gcode')])==1
        analysis=read(f"verifiche/slicing/{job['name']}/analisi.json")
        assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header']
        assert not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations']
        assert analysis['new_wall_islands']['candidate_count']==0
        if any(i['part']=='scocca_R15' for i in plate['items']):
            logo=read(f"verifiche/slicing/{job['name']}/logo_percorsi.json")
            assert logo['project_sha256']==job['project_sha256'] and logo['both_glyphs_present']
            assert set(logo['glyphs'])=={'S','9'}
        native.append(dict(project=job['project'],sha256=job['project_sha256'],**check,
            configuration_checked=True,fuzzy_skin=False,model_warnings=warnings,
            warning_resolution='Stampare il PLA a sportello anteriore aperto; soglia software originale conservata.'))
        job['visual_review_complete']=True
        g.save(ROOT/'verifiche/slicing'/(job['name']+'_job.json'),job)
    g.save(ROOT/'verifiche/slicing/riepilogo.json',slicing)
    g.save(ROOT/'verifiche/controllo_3mf_nativi.json',dict(result='PASS',projects=native))
    state=dict(revision='R15',date='2026-10-22',state='PRONTO_PER_LA_STAMPA_DEL_PROTOTIPO_NOMINALE',
        configuration=g.P['configurazione_stampa'],slicer_engine=slicing['slicer_version'],slicer_app='1.5.3.5',
        bare_dimensions_mm=man['external_dimensions_mm'],base_enclosure_dimensions_mm=[90,101,86],
        rear_tail=g.P['retro_coperchio'],usb_keepouts_checked=9,minimum_nominal_usb_clearance_mm=geo["rear_tail"]["minimum_nominal_usb_clearance_mm"],
        kit_printed_parts=6,unique_printable_parts=4,native_projects=2,plates_per_project=1,replacement_parts=5,print_sequence='by layer',coupons_included=False,
        fuzzy_skin=False,logo=g.P['logo_frontale'],logo_paths_verified=True,
        R14_body_unchanged=True,U_cradles=geo["U_cradles"],lid_preload=geo["lid_preload"],sharp_external_edges_verified=True,geometry_verified=True,
        export_reopened=True,slicing_verified=True,all_layer_overviews_reviewed=True,critical_layers_sampled=True,
        model_slot_cases=9,assignments=27,screws=0,nuts=0,washers=0,internal_adhesives=False,
        commercial_components=['4 piedini trasparenti in gomma, quote da confermare'],
        kit_estimates=slicing['kit_totals'],replacement_estimates=slicing['replacement_totals'],model_warnings=[j['model_warnings'] for j in slicing['jobs']],
        warning_resolution='Sportello anteriore aperto per la stampa PLA.',
        physical_print=False,physical_fit=False,snap_force_validated=False,thermal_test=False,sent_to_printer=False,
        open_items=['Misure effettive SSD, posizione USB, spinotti e gommini','Forza e durata degli incastri in PLA',
            'Stabilita con i cavi collegati','Temperature dentro/fuori dal bay e agli appoggi PLA, soprattutto SSD centrale'])
    g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state)
    air=read('verifiche/aria.json')
    assert len(air['assignments_with_U_cradles'])==27 and air['minimum_vertical_corridors_all_assignments_cm2']>0
    lines=['# Verifiche R15 PLA BASIC','',
        '**Pronto per la stampa del prototipo nominale. Verifiche digitali completate; tenuta reale e rigidezza da verificare sulla nuova stampa.**','',
        'Scocca R14 invariata: confronto sui STEP riaperti con differenza simmetrica inferiore a 0,00001 mm³. Anche tetto esterno e griglia conservati. Tutti i file hashati della consegna R14 verificati e conservati.',
        'Alette da 8 a 9 mm: gioco di 0,3 mm a ciascuna estremita della finestra larga 9,6 mm. Pattini con interferenza nominale di 0,15 mm per lato verso la parete interna. La forma libera interseca intenzionalmente la scocca soltanto nei due pattini. Inviluppo con linguette traslate all’interno di 0,15 mm privo di collisioni: controllo geometrico, non simulazione della deformazione o della forza.',
        'Culle a U bilaterali per T7 e Shield, due per modello. Due collari pieni collegati da una base: il dispositivo entra fra le sponde. Scasso centrale attorno alle guide R14, con 0,3 mm di gioco per lato in X e Y; nessuna lamina sottile tra Shield e guida. Base 1,2 mm, collari profondi 3,7 mm, pareti minime Shield 2,5 mm. Appoggio inferiore geometrico 115,2 mm² per culla. Le culle calzano dall’alto senza viti o adesivi; non promettono un bloccaggio elastico o resistenza agli urti.',
        'Culle e SSD T7/Shield centrati rispetto alla sede. Aperture 9 e 13,6 mm: giochi totali nominali sui dischi rispettivamente 1 e 0,6 mm. T9 direttamente nelle guide da 15 mm. Base culle alza T7 e Shield di 1,2 mm; bordo inferiore coda da quota 56 a 57 mm per conservare almeno 3 mm sopra l’ingombro USB nominale.',
        'Quattro STL e otto STEP singoli riaperti. Solido unico valido, scala millimetrica, mesh chiuse, normali coerenti, volumi positivi; nessuna faccia degenere/duplicata e nessuna coppia rilevata dallo screening di autointersezioni, che esclude triangoli con vertici condivisi. Nessuna riparazione automatica.',
        'Nove casi modello/slot, 27 disposizioni nominali, estrazione SSD e culle a quote campionate senza collisioni. Assieme STEP di nove solidi compresi tre gabarit non stampabili. Interferenza intenzionale dei soli pattini documentata separatamente.',
        f"Ingombro chiuso 90 × 109,4 × 86 mm. Nove ingombri USB 20 × 20 × 50 mm senza collisioni; margine minimo sopra USB {geo['rear_tail']['minimum_nominal_usb_clearance_mm']:.1f} mm. Posizione centrale e dimensioni spinotti nominali, non misurate. Gioco assiale dietro Shield/T9 2 mm.",
        f"Aree geometriche: fondo {air['floor_net_cm2']:.2f} cm², tetto {air['roof_net_cm2']:.2f} cm², corridoi verticali conservativi con tre T9 {air['continuous_vertical_corridors_three_T9_cm2']:.2f} cm². Fianchi {air['side_pattern_net_cm2'][0]:.2f} cm² ciascuno; retro aperto {air['rear_open_below_tail_cm2']:.2f} cm² senza spine. Non sono portate d’aria o potenze dissipabili.",
        f"Corridoi verticali con SSD e culle installate: controllate tutte le 27 disposizioni; minimo {air['minimum_vertical_corridors_all_assignments_cm2']:.2f} cm². Valutazione geometrica in proiezione, senza misura di portata.",
        'Due progetti alternativi: RICAMBI con cinque pezzi su un piatto, KIT_COMPLETO con sei pezzi su un piatto. Non occorre stampare entrambi. ElegooSlicer app 1.5.3.5 / motore 2.4.2, ECC2 Combo, ugello 0,4, PEI testurizzato, PLA BASIC, 220/60 °C, strati 0,2 mm, quattro pareti, gyroid 20%, limite 5 mm³/s, brim 5 mm, supporti disattivati. Fuzzy disattivata; S9 0,4 mm invariato; nessun provino.',
        '3MF nativi riaperti per ID e percorsi XML; geometria, profili e G-code dello slicer incorporati verificati. Unita millimetriche, trasformazioni, ingombri con brim e zona esclusa controllati. Tutti gli strati nelle tavole d’insieme e dettagli funzionali esaminati; screening di nuove isole registrato nelle analisi. Piccoli ponti su sedi piedini, feritoie e agganci controllati. Percorsi S e 9 verificati nel kit completo, compensando offset estrusore Y 1,5 mm.',
        'Avviso mantenuto: bed_temperature_too_high_than_filament (1000C001), confronto piano 60 °C / soglia software PLA 45 °C. Preparazione: sportello anteriore aperto, evitare calore accumulato in camera. Profilo compatibile e dati del produttore archiviati; valori iniziali non calibrati sulla bobina.',
        '', '| Alternativa | Strati | PLA stimato | Tempo stimato |','| --- | ---: | ---: | --- |']
    for j in slicing['jobs']:
        e=j['slicer_estimates'];lines.append(f"| {j['name']} | {j['layers']} | {e['total filament used [g]']} g | {e['estimated printing time (normal mode)']} |")
    lines+=['','Stime dello slicer con brim; alternative da non sommare. Nessun invio alla stampante.','',
        'La segnalazione dell’utente descrive scarsa pressione del tetto e flessione degli inserti precedenti. Questa revisione risponde con nuove geometrie; nessuna prova fisica R15, misura della forza, verifica di fatica/creep o test termico e stata eseguita. SSD/cavi/piedini reali non misurati. Non si dichiara risolto fisicamente il problema prima di provare i ricambi.','']
    (ROOT/'verifiche/RAPPORTO_VERIFICHE.md').write_text('\n'.join(lines))
    assert (ROOT/'README.md').exists()
    # Enumera soltanto i contenuti del progetto; conserva fuori dal pacchetto
    # archivi storici, eventuali copie estratte dall'utente e log temporanei del programma.
    folders={'CAD','anteprime','stampa','sorgenti','slicer','verifiche'}
    root_files={'README.md','logo_S9.png','logo_S9.svg','logo_S9_Engineering.png','logo_S9_Engineering.svg'}
    checks={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file()
        and (p.relative_to(ROOT).parts[0] in folders or str(p.relative_to(ROOT)) in root_files)
        and '__pycache__' not in p.parts and p.suffix!='.zip' and p.name not in {'SHA256.json','.DS_Store'}}
    g.save(ROOT/'verifiche/SHA256.json',checks)
    archive=ROOT/'BAY_SSD_R15_PLA_BASIC_CONSEGNA.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for rel in [*checks,'verifiche/SHA256.json']:z.write(ROOT/rel,ROOT.name+'/'+rel)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==len(checks)+1
        for rel,h in checks.items():assert hashlib.sha256(z.read(ROOT.name+'/'+rel)).hexdigest()==h
    print(json.dumps(dict(state=state['state'],archive=str(archive),files=len(checks)+1,
        bytes=archive.stat().st_size,kit=slicing['kit_totals'])),flush=True)

if __name__=='__main__':main()
