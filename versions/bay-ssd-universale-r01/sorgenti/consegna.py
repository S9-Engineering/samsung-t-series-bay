"""Controllo coerenza e archivio, dopo revisione visiva registrata sugli hash."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
import platform
import numpy as np
import trimesh
import genera as g

ROOT=g.ROOT


def duration(seconds):
    h,r=divmod(int(seconds),3600);m,s=divmod(r,60)
    return f"{h} h {m:02d} min {s:02d} s"


def main():
    manifest=json.loads((ROOT/"verifiche/manifest.json").read_text())
    geom=json.loads((ROOT/"verifiche/geometria.json").read_text())
    slicing=json.loads((ROOT/"verifiche/slicing/riepilogo.json").read_text())
    plates=json.loads((ROOT/"verifiche/piatti.json").read_text())["plates"]
    review=json.loads((ROOT/"verifiche/revisione_visiva.json").read_text())
    assert manifest["parameters_sha256"]==g.sha(ROOT/"sorgenti/parametri.json")
    assert geom["result"]=="PASS_DIGITALE_QUOTE_NOMINALI"
    for p,q in zip(manifest["parts"],geom["export_checks"]):
        assert p["name"]==q["name"] and p["stl_sha256"]==q["stl_sha256"]==g.sha(ROOT/p["stl"])
        assert g.sha(ROOT/p["step"])==q["step_sha256"]
    assert len(slicing["jobs"])==len(plates)==3
    native=[]
    for job,plate in zip(slicing["jobs"],plates):
        assert job["name"]==plate["name"]
        assert job["geometry_sha256"]==plate["sha256"]==g.sha(ROOT/plate["geometry_3mf"])
        for name,h in job["profile_hashes"].items():assert g.sha(ROOT/"slicer"/name)==h
        path=ROOT/job["project"];assert g.sha(path)==job["project_sha256"]
        approved=review["projects"][job["name"]]
        assert approved["project_sha256"]==job["project_sha256"] and approved["reviewed"]
        for image,h in approved["image_hashes"].items():assert g.sha(ROOT/image)==h
        scene=trimesh.load(path,force="scene")
        assert len(scene.graph.nodes_geometry)==len(plate["items"])
        actual=[]
        for node in scene.graph.nodes_geometry:
            transform,name=scene.graph[node];m=scene.geometry[name].copy();m.apply_transform(transform)
            assert m.is_watertight and m.is_winding_consistent and m.volume>0
            actual.append(m.bounds.reshape(-1).tolist())
        expected=[np.array(i["bounds_mm"]).reshape(-1).tolist()for i in plate["items"]]
        assert np.max(np.abs(np.array(sorted(actual))-np.array(sorted(expected))))<.06
        with zipfile.ZipFile(path)as z:
            assert z.testzip()is None
            root=ET.fromstring(z.read("3D/3dmodel.model"));assert root.get("unit")=="millimeter"
            settings=json.loads(z.read("Metadata/project_settings.config"))
            assert "Centauri Carbon 2" in settings["printer_model"]
            assert settings["nozzle_diameter"]==["0.4"] and settings["curr_bed_type"]=="Textured PEI Plate"
            assert settings["filament_type"]==["PETG"] and settings["nozzle_temperature"]==["240"]
            assert settings["textured_plate_temp"]==["65"] and settings["layer_height"]=="0.2"
            assert settings["enable_support"]=="0" and len([n for n in z.namelist()if n.endswith(".gcode")])==1
        analysis=json.loads((ROOT/"verifiche/slicing"/job["name"]/"analisi.json").read_text())
        assert analysis["all_layers_nonempty"] and analysis["layer_count_matches_header"]
        assert not analysis["out_of_bed_layers"] and not analysis["profile_exclusion_zone_violations"]
        assert analysis["new_wall_islands"]["candidate_count"]==0 and not job["model_warnings"]
        job["visual_review_complete"]=True
        g.save(ROOT/"verifiche/slicing"/(job["name"]+"_job.json"),job)
        native.append(dict(project=job["project"],sha256=job["project_sha256"],
                           bodies=len(actual),unit="millimeter",transforms_and_dimensions_checked=True,
                           configuration_checked=True,layers=job["layers"]))
    g.save(ROOT/"verifiche/slicing/riepilogo.json",slicing)
    g.save(ROOT/"verifiche/controllo_3mf_nativi.json",dict(projects=native,pass_=True))
    state=dict(revision="R01",date="2026-10-20",
        state="PRONTO_PER_LA_STAMPA_DEL_PROTOTIPO_NOMINALE",
        print_first="stampa/progetti_ElegooSlicer/BAY_R01_00_PROVINO_PRIMA_DI_TUTTO_ECC2_PETGPRO.3mf",
        dimensions_mm=manifest["external_dimensions_mm"],configuration=g.P["configurazione_stampa"],
        geometry=True,export_reopened=True,stl_unique_parts=5,kit_printed_parts=6,
        nominal_model_slot_pairs=9,nominal_assignments=27,slicer=slicing["slicer_version"],
        slicing=True,all_layer_overviews_reviewed=True,critical_layers_sampled=True,
        source_manifest_sha256=g.sha(ROOT/"verifiche/manifest.json"),
        geometry_report_sha256=g.sha(ROOT/"verifiche/geometria.json"),
        kit_estimates=slicing["kit_totals"],coupon_estimates=slicing["coupon_totals"],
        physical_fit=False,physical_print=False,thermal_test=False,sent_to_printer=False,
        open_items=manifest["unmeasured"]+["Accoppiamento, serraggio e stabilita reali",
            "Rigidita effettiva e fissaggio dei cavi","Temperatura e comportamento del disco centrale"],
        python=platform.python_version())
    g.save(ROOT/"verifiche/STATO_CONSEGNA.json",state)
    lines=["# Riscontri di consegna — R01","",
           "**Pronto per la stampa del prototipo nominale. Stampare prima il provino.**","",
           "Configurazione confermata: ELEGOO Centauri Carbon 2 Combo, ugello 0,4 mm, PEI testurizzato, ELEGOO PETG PRO.",
           f"Slicing reale: ElegooSlicer {slicing['slicer_version']}. Nessun avvio della stampante.","",
           "## Geometria","",
           "- Cinque STL unici riaperti: corpo unico, mesh chiusa, normali coerenti e volume positivo; nessuna faccia degenere o duplicata.",
           "- STEP riaperti e validi. Scostamento dei box entro 0,06 mm, coerente con la tessellazione; differenza volumetrica STL/STEP sotto 0,5%.",
           "- Screening autointersezioni: zero coppie rilevate. Coppie con vertici condivisi escluse dal metodo.",
           "- Nove abbinamenti e 27 assegnazioni nominali verificati; estrazione e accesso utensile controllati a posizioni campionate.",
           "- 3MF geometrici e nativi riaperti, millimetri e trasformazioni controllati; 2/5/1 corpi nei tre piatti.",
           "- Passaggio verticale comune nei corridoi campionati: circa 15,02 cm². Nessuna CFD o misura termica.","",
           "## Slicing e stime","",
           "| Piatto | Strati | Filamento | Tempo |","| --- | ---: | ---: | --- |"]
    for job in slicing["jobs"]:
        import re
        grams=job["slicer_estimates"]["total filament used [g]"]
        time=job["slicer_estimates"]["estimated printing time (normal mode)"]
        lines.append(f"| {job['name']} | {job['layers']} | {grams} g | {time} |")
    lines += ["",f"**Kit completo:** {slicing['kit_totals']['filament_g']:.2f} g; {duration(slicing['kit_totals']['printing_seconds'])}.",
              f"**Provino separato:** {slicing['coupon_totals']['filament_g']:.2f} g; {duration(slicing['coupon_totals']['printing_seconds'])}.","",
              "Le stime includono brim e impostazioni dei piatti; supporti disattivati, nessuna torre o cambio colore.",
              "Zero avvisi di modello, zero percorsi fuori piano o nella zona esclusa e zero candidati di nuove isole esterne dallo screening raster.",
              "Rassegna di tutti gli strati e approfondimenti delle zone critiche registrati in revisione_visiva.json.",
              "Le etichette Internal Bridge possono attraversare l'infill: la lunghezza totale del segmento non equivale a una campata in aria.","",
              "## Limiti rimasti","",
              "Prototipo non stampato. Dimensioni SSD nominali; 50 mm rigidi e cavo 5 mm sono indicazioni approssimative dell'utente. Porte e sezioni degli spinotti non rilevate.",
              "Provare sede, silicone, viti e fermacavi reali. Nessuna garanzia termica, di resistenza, precisione, stabilita o assenza di throttling ricavata dal CAD.",
              "Le temperature vanno confrontate con e senza bay; prima provino, poi prova del kit, con priorita al disco centrale.",""]
    (ROOT/"verifiche/RAPPORTO_VERIFICHE.md").write_text("\n".join(lines))
    checksums={}
    for p in sorted(ROOT.rglob("*")):
        rel=p.relative_to(ROOT)
        if not p.is_file()or any(x in rel.parts for x in (".venv","__pycache__"))or p.suffix==".zip"or rel.name=="SHA256.json":
            continue
        checksums[str(rel)]=g.sha(p)
    g.save(ROOT/"verifiche/SHA256.json",checksums)
    archive=ROOT/"BAY_SSD_R01_CONSEGNA.zip"
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED)as z:
        for rel in [*checksums,"verifiche/SHA256.json"]:
            z.write(ROOT/rel,ROOT.name+"/"+rel)
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None
        assert not any("/.venv/"in n or n.endswith(".gcode") for n in z.namelist())
        entries=len(z.namelist())
    print(json.dumps(dict(state=state["state"],archive=str(archive),files=entries,
                          archive_bytes=archive.stat().st_size,kit=state["kit_estimates"])),flush=True)


if __name__=="__main__":
    main()
