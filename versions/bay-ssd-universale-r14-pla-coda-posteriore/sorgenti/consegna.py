"""Audit e archivio finale R14 PLA: quattro parti uniche su un piatto, S9 in rilievo."""
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
    assert continuity['result']=='PASS' and continuity['body_and_inserts_identical'] and continuity['R05_internal_unchanged']
    assert continuity['horizontal_vents_and_latches_unchanged'] and continuity['external_radii_zero']
    for row in continuity['parts']:
        assert row['current_sha256']==g.sha(ROOT/'CAD'/f"{row['part']}_R14.step")
        assert row['symmetric_difference_mm3']<1e-5
    assert continuity['lid']['current_sha256']==g.sha(ROOT/'CAD/coperchio_R14.step')
    assert continuity['lid']['removed_material_mm3']<1e-5 and continuity['lid']['original_region_difference_mm3']<1e-5
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
    assert len(previews['outputs'])==9
    assert len(plates)==len(slicing['jobs'])==1 and len(plates[0]['items'])==6
    assert len(geo['usb_cases'])==9 and all(c['intersections_mm3']<1e-5 and c['vertical_clearance_mm']>=3 for c in geo['usb_cases'])
    assert geo['assignments_include_nominal_usb_keepouts']
    assert geo['rear_tail']['parameters']==g.P['retro_coperchio']
    assert geo['rear_tail']['axial_clearance_mm']==2 and geo['rear_tail']['minimum_nominal_usb_clearance_mm']==3
    assert not any('PROVINO' in p.name.upper() for p in (ROOT/'stampa').rglob('*'))
    native=[]
    for plate,job in zip(plates,slicing['jobs']):
        assert plate['name']==job['name'] and job['group']=='kit'
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
        if any(i['part']=='scocca_R14' for i in plate['items']):
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
    state=dict(revision='R14',date='2026-10-21',state='PRONTO_PER_LA_STAMPA_DEL_PROTOTIPO_NOMINALE',
        configuration=g.P['configurazione_stampa'],slicer_engine=slicing['slicer_version'],slicer_app='1.5.3.5',
        bare_dimensions_mm=man['external_dimensions_mm'],base_enclosure_dimensions_mm=[90,101,86],
        rear_tail=g.P['retro_coperchio'],usb_keepouts_checked=9,minimum_nominal_usb_clearance_mm=3,
        kit_printed_parts=6,unique_printable_parts=4,native_projects=1,plates=1,print_sequence='by layer',coupons_included=False,
        fuzzy_skin=False,logo=g.P['logo_frontale'],logo_paths_verified=True,
        R05_internal_unchanged=True,sharp_external_edges_verified=True,geometry_verified=True,
        export_reopened=True,slicing_verified=True,all_layer_overviews_reviewed=True,critical_layers_sampled=True,
        model_slot_cases=9,assignments=27,screws=0,nuts=0,washers=0,internal_adhesives=False,
        commercial_components=['4 piedini trasparenti in gomma, quote da confermare'],
        kit_estimates=slicing['kit_totals'],model_warnings=[j['model_warnings'] for j in slicing['jobs']],
        warning_resolution='Sportello anteriore aperto per la stampa PLA.',
        physical_print=False,physical_fit=False,snap_force_validated=False,thermal_test=False,sent_to_printer=False,
        open_items=['Misure effettive SSD, posizione USB, spinotti e gommini','Forza e durata degli incastri in PLA',
            'Stabilita con i cavi collegati','Temperature dentro/fuori dal bay e agli appoggi PLA, soprattutto SSD centrale'])
    g.save(ROOT/'verifiche/STATO_CONSEGNA.json',state)
    air=read('verifiche/aria.json')
    lines=['# Verifiche R14 PLA BASIC','',
        '**Pronto per la stampa del prototipo nominale. Controlli digitali completati; nessuna prova fisica o termica.**','',
        'Tutte le sei parti del kit in PLA BASIC. Fuzzy Skin disattivata, nessun modificatore, nessun provino. S9 integrato nella scocca: larghezza 14 mm, rilievo 0,4 mm, margini destro 4 mm e inferiore 6 mm. Un solo materiale e colore.',
        'Quattro STL e otto STEP singoli, nei riferimenti di assieme e stampa, riaperti. Scala millimetrica, solido unico valido, mesh chiusa, normali coerenti e volume positivo. Nessuna faccia degenere o duplicata; zero coppie rilevate nello screening delle autointersezioni, che esclude le coppie con vertici condivisi. Nessuna riparazione automatica.',
        'Confronto con la R13: scocca e due tipi di inserto identici, differenza simmetrica inferiore a 0,00001 mm³. Coperchio con sola aggiunta nella regione posteriore: tetto prolungato di 8 mm, pannello e due corti risvolti fino a quota 56 mm. Regione originale, feritoie e agganci conservati. R13 verificata e conservata.',
        'Nove combinazioni modello/slot e 27 disposizioni nominali senza collisioni statiche; estrazione verticale campionata, con coperchio rimosso e cavi scollegati. Assieme STEP valido: nove solidi, compresi tre gabarit SSD non stampabili.',
        'Scocca base profonda 101 mm, coperchio profondo 109 mm; ingombro chiuso con S9 90 × 109,4 × 86 mm. Shield e T9 terminano a Y104; parete posteriore interna a Y106: gioco assiale 2 mm. Coda in un solo pezzo con il tetto, spessore 3 mm e luce 0,3 mm dalle estremita posteriori della scocca.',
        'Nove ingombri USB nominali senza collisioni con scocca, coperchio e inserti. Spazio riservato 20 mm di larghezza × 20 mm di altezza × 50 mm in uscita, centrato sulla faccia corta del gabarit SSD. Bordo inferiore del retro a quota 56 mm: margine sopra lo spinotto 3 mm per T9, 3,5 mm per Shield, 4,5 mm per T7. Sono ipotesi generose richieste dall’utente, non dimensioni standard certificate o misure dei suoi cavi.',
        f"Aree geometriche: fondo {air['floor_net_cm2']:.2f} cm², tetto {air['roof_net_cm2']:.2f} cm², corridoi verticali conservativi con tre T9 {air['continuous_vertical_corridors_three_T9_cm2']:.2f} cm². Ogni fianco: {air['side_pattern_holes_per_panel']} feritoie orizzontali, {air['side_pattern_net_cm2'][0]:.2f} cm². Non sono misure di portata o potenza dissipabile.",
        f"Apertura posteriore sotto la coda: {air['rear_open_below_tail_cm2']:.2f} cm², sezione geometrica senza gli spinotti. Il passaggio inferiore, il tetto e i fianchi restano ventilati; nessuna simulazione o misura di portata.",
        'Slicing reale con ElegooSlicer, app 1.5.3.5 / motore 2.4.2. Profili ECC2, ugello 0,4, PEI testurizzato, PLA BASIC 220/60 °C. Limite volumetrico 5 mm³/s. Un progetto nativo con sei pezzi nello stesso piatto, geometria, impostazioni e G-code dello slicer incorporato. Stampa per strato, orientamenti invariati.',
        'Riaperto il 3MF per ID dei componenti e relativi percorsi XML: sei oggetti stampabili, zero modificatori. Unita e trasformazioni verificate; ingombro conservativo complessivo con brim 220 × 143 mm sul piano 256 × 256 mm. Brim da 5 mm separati, esclusione macchina rispettata. Coperchio con faccia esterna sul piano: la coda cresce verticalmente da esso, senza supporti.',
        'Tutti gli strati esaminati nelle tavole d’insieme; campioni critici ingranditi. Zero candidati di nuove isole esterne nello screening raster. Verificati i percorsi di entrambi i glifi S e 9, con compensazione dell’offset estrusore del profilo. Supporti disattivati; piccoli ponti su sedi piedini, feritoie e agganci controllati nelle anteprime. I segmenti Internal Bridge possono attraversare il riempimento: la loro lunghezza totale non equivale alla campata libera.',
        'Avviso presente nel progetto: bed_temperature_too_high_than_filament (1000C001), dovuto al confronto fra piano a 60 °C e soglia software PLA a 45 °C. Soglia conservata. Preparazione indicata: sportello anteriore aperto, evitare accumulo di calore nella camera; non e un errore geometrico risolto modificando i limiti.',
        '', '| Piatto | Strati | PLA stimato | Tempo stimato |','| --- | ---: | ---: | --- |']
    for j in slicing['jobs']:
        e=j['slicer_estimates'];lines.append(f"| {j['name']} | {j['layers']} | {e['total filament used [g]']} g | {e['estimated printing time (normal mode)']} |")
    lines += ['',f"**Kit: {slicing['kit_totals']['filament_g']:.2f} g, {duration(slicing['kit_totals']['printing_seconds'])}.** Stime dello slicer con brim, senza torre o cambi colore.",'',
        'Forza e durata degli incastri, stabilita, finitura, adesione e idoneita termica del PLA restano da verificare sul pezzo. Quote delle porte USB e degli spinotti reali non misurate: spazio generoso parametrico. Non sono state misurate temperature reali degli SSD o degli appoggi. Nessuna simulazione termica, calibrazione della bobina, prova fisica o stampa avviata. Nessun provino aggiunto, come richiesto.','']
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
    archive=ROOT/'BAY_SSD_R14_PLA_BASIC_CONSEGNA.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for rel in [*checks,'verifiche/SHA256.json']:z.write(ROOT/rel,ROOT.name+'/'+rel)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==len(checks)+1
        for rel,h in checks.items():assert hashlib.sha256(z.read(ROOT.name+'/'+rel)).hexdigest()==h
    print(json.dumps(dict(state=state['state'],archive=str(archive),files=len(checks)+1,
        bytes=archive.stat().st_size,kit=slicing['kit_totals'])),flush=True)

if __name__=='__main__':main()
