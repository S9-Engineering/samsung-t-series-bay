"""Coerenza della consegna R12, dopo revisione visiva dei percorsi reali."""
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.optimize import linear_sum_assignment
import genera as g
ROOT=g.ROOT


def duration(seconds):
    h,r=divmod(int(seconds),3600);m,s=divmod(r,60)
    return f"{h} h {m:02d} min {s:02d} s"


def main():
    man=json.loads((ROOT/"verifiche/manifest.json").read_text())
    geo=json.loads((ROOT/"verifiche/geometria.json").read_text())
    slicing=json.loads((ROOT/"verifiche/slicing/riepilogo.json").read_text())
    plates=json.loads((ROOT/"verifiche/piatti.json").read_text())["plates"]
    review=json.loads((ROOT/"verifiche/revisione_visiva.json").read_text())
    previews=json.loads((ROOT/"verifiche/anteprime.json").read_text())
    continuity=json.loads((ROOT/"verifiche/confronto_revisioni.json").read_text())
    assert continuity["base_enclosure_dimensions_unchanged"] and continuity["R05_internal_unchanged"]
    assert continuity["logo_only_addition_verified"] and continuity["body"]["logo_difference_mm3"]<1e-5
    assert continuity["horizontal_vents_and_latches_unchanged"] and continuity["external_radii_zero"]
    assert continuity["body"]["current_sha256"]==g.sha(ROOT/"CAD/scocca_R12.step")
    assert continuity["body"]["internal_difference_mm3"]<1e-5
    assert continuity["lid"]["current_sha256"]==g.sha(ROOT/"CAD/coperchio_R12.step")
    assert continuity["lid"]["functional_region_difference_mm3"]<1e-5
    for part in continuity["identical_parts"]:
        assert part["current_sha256"]==g.sha(ROOT/"CAD"/(part["part"]+"_R12.step"))
        assert part["symmetric_difference_mm3"]<1e-5
    assert geo["result"]=="PASS_DIGITALE_QUOTE_NOMINALI"
    assert geo["sharp_external_edges_verified"]
    assert man["logo_contours_sha256"]==g.sha(ROOT/"sorgenti"/g.P["logo_frontale"]["sorgente"])
    assert geo["logo_verified"]["glyphs"]==2 and geo["logo_verified"]["emboss_mm"]==g.P["logo_frontale"]["rilievo_mm"]
    logos=json.loads((ROOT/'verifiche/provenienza_loghi.json').read_text())['logos']
    for logo in logos:
        assert g.sha(ROOT/logo['source_png'])==logo['source_png_sha256']
        assert g.sha(ROOT/logo['vector_svg'])==logo['vector_svg_sha256']
    assert geo["side_vent_mm"]["horizontal_orientation_verified_on_exported_mesh"]
    assert geo["side_vent_mm"]["angle_degrees"]==0
    assert geo["source_manifest_sha256"]==previews["source_manifest_sha256"]==g.sha(ROOT/"verifiche/manifest.json")
    assert geo["source_parameters_sha256"]==man["parameters_sha256"]==g.sha(ROOT/"sorgenti/parametri.json")
    assert len(man["parts"])==len(geo["export_checks"])==7
    for p,q in zip(man["parts"],geo["export_checks"]):
        assert p["name"]==q["name"]
        assert p["stl_sha256"]==q["stl_sha256"]==g.sha(ROOT/p["stl"])
        assert q["step_sha256"]==g.sha(ROOT/p["step"])
    for p,h in previews["outputs"].items():assert g.sha(ROOT/p)==h
    assert len(plates)==len(slicing["jobs"])==3
    native=[]
    for plate,job in zip(plates,slicing["jobs"]):
        assert plate["name"]==job["name"]
        assert plate["sha256"]==job["geometry_sha256"]==g.sha(ROOT/plate["geometry_3mf"])
        for name,h in job["profile_hashes"].items():assert g.sha(ROOT/"slicer"/name)==h
        path=ROOT/job["project"];assert g.sha(path)==job["project_sha256"]
        r=review["projects"][job["name"]]
        assert r["project_sha256"]==job["project_sha256"] and r["reviewed"]
        for image,h in r["image_hashes"].items():assert g.sha(ROOT/image)==h
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            assert ET.fromstring(z.read("3D/3dmodel.model")).get("unit")=="millimeter"
            settings=json.loads(z.read("Metadata/project_settings.config"))
            assert "Centauri Carbon 2" in settings["printer_model"]
            assert settings["nozzle_diameter"]==["0.4"] and settings["curr_bed_type"]=="Textured PEI Plate"
            assert settings["filament_type"]==["PETG"] and settings["nozzle_temperature"]==["240"]
            assert settings["textured_plate_temp"]==["65"] and settings["layer_height"]=="0.2"
            assert settings["enable_support"]=="0"
            assert len([p for p in z.namelist() if p.endswith(".gcode")])==1
        scene=trimesh.load(path,force="scene")
        assert len(scene.graph.nodes_geometry)==len(plate["items"])
        actual=[]
        for node in scene.graph.nodes_geometry:
            transform,name=scene.graph[node];mesh=scene.geometry[name].copy();mesh.apply_transform(transform)
            assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
            actual.append(mesh.bounds.reshape(-1).tolist())
        expected=np.array([np.array(i["bounds_mm"]).reshape(-1) for i in plate["items"]])
        # Associa i corpi per distanza geometrica, evitando l'ordine instabile di minimi X quasi uguali.
        cost=np.max(np.abs(np.array(actual)[:,None,:]-expected[None,:,:]),axis=2)
        a,b=linear_sum_assignment(cost)
        maximum_deviation=float(cost[a,b].max())
        assert maximum_deviation<.06
        analysis=json.loads((ROOT/"verifiche/slicing"/job["name"]/"analisi.json").read_text())
        assert analysis["all_layers_nonempty"] and analysis["layer_count_matches_header"]
        assert not analysis["out_of_bed_layers"] and not analysis["profile_exclusion_zone_violations"]
        assert analysis["new_wall_islands"]["candidate_count"]==0 and not job["model_warnings"]
        if 'SCOCCA' in job['name']:
            logo_paths=json.loads((ROOT/'verifiche/slicing'/job['name']/'logo_percorsi.json').read_text())
            assert logo_paths['project_sha256']==job['project_sha256'] and logo_paths['both_glyphs_present']
            assert set(logo_paths['glyphs'])=={'S','9'}
        native.append(dict(project=job["project"],sha256=job["project_sha256"],objects=len(actual),
                           maximum_bounds_deviation_mm=maximum_deviation,
                           unit="millimeter",bounds_and_configuration_checked=True))
        job["visual_review_complete"]=True
        g.save(ROOT/"verifiche/slicing"/(job["name"]+"_job.json"),job)
    g.save(ROOT/"verifiche/slicing/riepilogo.json",slicing)
    g.save(ROOT/"verifiche/controllo_3mf_nativi.json",dict(projects=native,pass_=True))
    state=dict(revision="R12",date="2026-10-20",state="PRONTO_PER_LA_STAMPA_DEL_PROTOTIPO_NOMINALE",
        print_first="stampa/progetti_ElegooSlicer/BAY_R12_00_PROVINO_PRIMA_DI_TUTTO_ECC2_PETGPRO.3mf",
        bare_dimensions_mm=man["external_dimensions_mm"],base_enclosure_dimensions_mm=[90,101,86],
        logo=g.P["logo_frontale"],logo_only_addition_verified=True,logo_paths_verified=True,kit_printed_parts=6,kit_unique_parts=4,stl_unique_with_coupons=7,
        screws=0,nuts=0,washers=0,internal_adhesives=False,internal_silicone=False,
        commercial_components=["4 piedini adesivi trasparenti, quote da confermare"],
        configuration=g.P["configurazione_stampa"],slicer=slicing["slicer_version"],
        model_slot_cases=9,assignments=27,geometry_verified=True,export_reopened=True,
        slicing_verified=True,all_layer_overviews_reviewed=True,critical_layers_sampled=True,
        base_enclosure_dimensions_unchanged=True,R05_internal_unchanged=True,horizontal_vents_and_latches_unchanged=True,
        sharp_external_edges_verified=True,
        side_pattern_count_per_panel=man["side_pattern_count_per_panel"],
        side_vents_horizontal_verified=True,
        kit_estimates=slicing["kit_totals"],coupon_estimates=slicing["coupon_totals"],
        snap_force_validated=False,physical_print=False,physical_fit=False,thermal_test=False,sent_to_printer=False,
        open_items=["Misure reali degli SSD","Elasticita e forza degli incastri","Gommini commerciali e luce sotto la base",
                    "Stabilita con cavi collegati","Prova termica dentro/fuori, soprattutto slot centrale"])
    g.save(ROOT/"verifiche/STATO_CONSEGNA.json",state)
    air=json.loads((ROOT/"verifiche/aria.json").read_text())
    lines=["# Verifiche R12","",
        "**Pronto per la stampa del prototipo nominale. Prima il piatto 00 provini.**","",
        "Logo S9 senza sottotitolo integrato sul fronte, in basso a destra, largo 14 mm e in rilievo 0,4 mm. Margini destro 4 mm e inferiore 6 mm. Stesso materiale e colore della scocca. Ingombro massimo con rilievo 90 x 101,4 x 86 mm; scocca base 90 x 101 x 86 mm. Unico corpo stampabile: nessun adesivo o montaggio del logo.",
        "Confronto sui STEP finali: il corpo R11 e integro; aggiunti esclusivamente i due glifi S9. Coperchio, interno R05, feritoie e agganci conservati. Spigoli esterni netti verificati. Tolleranza dei confronti 0,00001 mm³.",
        "Sette STL unici riaperti, un corpo ciascuno, mesh chiuse, normali coerenti, volume positivo; zero facce degeneri o duplicate.",
        "STEP riaperti validi. Screening autointersezioni: zero coppie rilevate; escluse le coppie di triangoli con vertici condivisi. Nessuna riparazione automatica.",
        "Nove abbinamenti modello/slot e 27 assegnazioni nominali senza collisioni statiche; estrazione verticale a quote campionate.",
        "Assieme STEP: nove solidi, inclusi i tre gabarit SSD. Kit stampato: sei pezzi, senza viti, dadi, rondelle o adesivi interni.",
        f"Fondo: {air['floor_net_cm2']:.2f} cm² netti. Tetto: {air['roof_net_cm2']:.2f} cm². Corridoi verticali conservativi, tre T9: {air['continuous_vertical_corridors_three_T9_cm2']:.2f} cm².",
        f"Fianchi: {air['side_pattern_holes_per_panel']} feritoie per lato, circa {air['side_pattern_net_cm2'][0]:.2f} cm² netti per lato; fascia diagonale piena da 8 mm.",
        "Le aree sono geometriche, non portata o potenza dissipabile. Nessuna CFD o prova termica.","",
        f"Slicing reale: ElegooSlicer {slicing['slicer_version']}, ECC2 Combo, 0,4 mm, PEI testurizzato, ELEGOO PETG PRO.",
        "Tre progetti nativi riaperti: 7/5/1 oggetti; unita e trasformazioni verificate, brim 5 mm e zona esclusa rispettati.",
        "Supporti disattivati. Zero avvisi e zero candidati di nuove isole esterne nello screening raster. Tutti gli strati esaminati nelle tavole; campioni delle zone critiche ingranditi.",
        "Verificata la presenza dei percorsi del rilievo per entrambi i glifi S e 9, applicando l'offset estrusore del profilo macchina al confronto con la geometria; dettaglio in logo_percorsi.json e LOGO_FRONTALE.png. La finitura reale del logo rimane da provare.",
        "I segmenti Internal Bridge possono attraversare infill: la loro lunghezza totale non identifica una campata interamente in aria.","",
        "| Piatto | Strati | Filamento | Tempo |","| --- | ---: | ---: | --- |"]
    for j in slicing["jobs"]:
        estimates=j["slicer_estimates"]
        lines.append(f"| {j['name']} | {j['layers']} | {estimates['total filament used [g]']} g | {estimates['estimated printing time (normal mode)']} |")
    lines += ["",f"Kit: {slicing['kit_totals']['filament_g']:.2f} g, {duration(slicing['kit_totals']['printing_seconds'])}.",
              f"Provini: {slicing['coupon_totals']['filament_g']:.2f} g, {duration(slicing['coupon_totals']['printing_seconds'])}.",
              "Stime dello slicer comprensive del brim; senza torre di spurgo e senza cambi colore.","",
              "Elasticita, forza e durata degli scatti non dimostrate dai controlli statici. Prototipo non stampato. Provare prima gli inserti e la chiusura.",
              "Dimensioni dei gommini non confermate; sedi modificabili. La R12 non e un contenitore da trasporto carico. Nessuna stampa avviata.",""]
    (ROOT/"verifiche/RAPPORTO_VERIFICHE.md").write_text("\n".join(lines))
    checks={}
    for path in sorted(ROOT.rglob("*")):
        rel=path.relative_to(ROOT)
        if not path.is_file() or "__pycache__" in rel.parts or path.suffix==".zip" or path.name=="SHA256.json":continue
        checks[str(rel)]=g.sha(path)
    g.save(ROOT/"verifiche/SHA256.json",checks)
    archive=ROOT/"BAY_SSD_R12_CONSEGNA.zip"
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        for rel in [*checks,"verifiche/SHA256.json"]:z.write(ROOT/rel,ROOT.name+"/"+rel)
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print(json.dumps(dict(state=state["state"],archive=str(archive),files=len(checks)+1,
                         bytes=archive.stat().st_size,kit=slicing["kit_totals"])),flush=True)


if __name__=="__main__":main()
