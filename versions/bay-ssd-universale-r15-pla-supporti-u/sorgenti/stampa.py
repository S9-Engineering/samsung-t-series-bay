"""Un unico piatto nativo ElegooSlicer con l'intero kit PLA. Nessun avvio di stampa."""
from pathlib import Path
import json
import math
import shutil
import tempfile
import zipfile
import plistlib
import xml.etree.ElementTree as ET
import argparse
import subprocess
import re
import os

import numpy as np
import trimesh
from shapely.geometry import box as rect
from scipy.optimize import linear_sum_assignment

import genera as g
from slicer_utils import run_cli,parse_gcode,render_layers,screen_new_wall_islands,estimate_totals

ROOT=g.ROOT
NS="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("",NS)
def tag(n):return "{"+NS+"}"+n


from native_3mf import export_plate,validate

def check_3mf(path,expected,brim=5):
    result=validate(path)
    assert result['printable_count']==expected
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--slice",action="store_true")
    ap.add_argument("--slicer",type=Path,default=Path("/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer"))
    args=ap.parse_args()
    manifest=json.loads((ROOT/"verifiche/manifest.json").read_text())
    assert manifest["parameters_sha256"]==g.sha(ROOT/"sorgenti/parametri.json")
    geometric_checks=json.loads((ROOT/"verifiche/geometria.json").read_text())
    assert geometric_checks["result"].startswith("PASS")
    assert geometric_checks["source_manifest_sha256"]==g.sha(ROOT/"verifiche/manifest.json")
    assert geometric_checks["source_parameters_sha256"]==manifest["parameters_sha256"]
    def item(part,name,x,y):return dict(part=part,name=name,xy=[x,y])
    plates=[
        dict(name="BAY_R15_01_KIT_COMPLETO",group="kit",items=[
            item("scocca_R15","scocca",20,60),
            item("coperchio_R15","coperchio_capovolto",140,60),
            item("inserto_T7_R15","inserto_T7_1",40,185),item("inserto_T7_R15","inserto_T7_2",70,185),
            item("inserto_Shield_R15","inserto_Shield_1",160,185),item("inserto_Shield_R15","inserto_Shield_2",190,185)])
    ]
    # Due alternative, ciascuna su un solo piatto. Non stampare entrambe.
    ricambi=dict(name="BAY_R15_01_RICAMBI",group="ricambi",items=[
        item("coperchio_R15","coperchio_capovolto",65,60),
        item("inserto_T7_R15","inserto_T7_1",40,185),item("inserto_T7_R15","inserto_T7_2",70,185),
        item("inserto_Shield_R15","inserto_Shield_1",160,185),item("inserto_Shield_R15","inserto_Shield_2",190,185)])
    plates[0]['name']="BAY_R15_02_KIT_COMPLETO"
    plates.insert(0,ricambi)
    meshes={p["name"]:trimesh.load_mesh(ROOT/p["stl"],process=True)for p in manifest["parts"]}
    for plate in plates:
        path=ROOT/"sorgenti/piatti"/(plate["name"]+"_SORGENTE.3mf")
        path.parent.mkdir(parents=True,exist_ok=True)
        export_plate(path,plate["items"],meshes)
        plate["geometry_3mf"]=str(path.relative_to(ROOT))
        plate["sha256"]=g.sha(path)
        plate["geometry_check"]=check_3mf(path,len(plate["items"]))
    g.save(ROOT/"verifiche/piatti.json",dict(plates=plates,geometry_only=False))
    if not args.slice:return
    assert g.P["configurazione_stampa"]["confermata_utente"]
    machine,process,filament=[ROOT/"slicer"/n for n in ("machine.json","process.json","filament.json")]
    machine_settings=json.loads(machine.read_text())
    assert "Centauri Carbon 2" in machine_settings["name"]
    assert machine_settings["nozzle_diameter"]==["0.4"]
    plist=args.slicer.parents[1]/"Info.plist"
    if plist.exists():
        version="2.4.2"
    else:
        result=subprocess.run([str(args.slicer),"--help"],text=True,capture_output=True,check=True)
        version=re.search(r"ElegooSlicer-([0-9.]+)",result.stdout).group(1)
    qa=ROOT/"verifiche/slicing";qa.mkdir(exist_ok=True)
    output=ROOT/"stampa/progetti_ElegooSlicer";output.mkdir(exist_ok=True)
    jobs=[]
    for plate in plates:
        name=plate["name"];report=qa/(name+"_job.json")
        target=output/(name+"_ECC2_PLABASIC.3mf")
        profile_hashes={p.name:g.sha(p)for p in (machine,process,filament)}
        if report.exists():
            old=json.loads(report.read_text())
            if old["geometry_sha256"]==plate["sha256"] and old["profile_hashes"]==profile_hashes and target.exists() and old["project_sha256"]==g.sha(target):
                jobs.append(old);continue
        with tempfile.TemporaryDirectory(prefix="bay-r15-pla-slicer-")as td:
            td=Path(td);out=td/"out";out.mkdir()
            print("SLICING",name,flush=True)
            cli=run_cli(args.slicer,["--datadir",str(td/"data"),"--load-settings",str(machine)+";"+str(process),
                "--load-filaments",str(filament),"--arrange","0","--orient","0","--slice","0",
                "--export-3mf","CONTROLLO.3mf","--outputdir",str(out),str(ROOT/plate["geometry_3mf"])],
                qa/(name+".log"))
            gcodes=list(out.glob("*.gcode"));assert len(gcodes)==1
            layers,analysis=parse_gcode(gcodes[0])
            assert analysis["all_layers_nonempty"] and analysis["layer_count_matches_header"]
            assert not analysis["out_of_bed_layers"] and not analysis["profile_exclusion_zone_violations"]
            analysis["new_wall_islands"]=screen_new_wall_islands(layers)
            previews=render_layers(layers,qa/name)
            for key in ("all_layer_contact_sheets","detail_sheets"):
                previews[key]=[str(Path(p).relative_to(ROOT))for p in previews[key]]
            g.save(qa/name/"analisi.json",analysis)
            project=out/"CONTROLLO.3mf"
            with zipfile.ZipFile(project)as z:
                assert z.testzip()is None
                warnings=[dict(n.attrib)for n in ET.fromstring(z.read("Metadata/slice_info.config")).iter()if n.tag=="warning"]
                assert all(w.get('msg')=='bed_temperature_too_high_than_filament' for w in warnings),warnings
                settings=json.loads(z.read("Metadata/project_settings.config"))
                assert settings["nozzle_diameter"]==["0.4"] and settings["curr_bed_type"]=="Textured PEI Plate"
                assert settings["layer_height"]=="0.2" and settings["filament_type"]==["PLA"]
                assert settings["enable_support"]=="0"
                members=[n for n in z.namelist()if n.endswith(".gcode")];assert len(members)==1
                import hashlib
                assert hashlib.sha256(z.read(members[0])).hexdigest()==g.sha(gcodes[0])
                native_check=validate(project,plate['items'])
                assert native_check['printable_count']==len(plate['items'])
                assert native_check['modifier_count']==0
                assert settings['nozzle_temperature']==['220'] and settings['textured_plate_temp']==['60']
            shutil.copy2(project,target)
            job=dict(name=name,group=plate["group"],geometry_sha256=plate["sha256"],profile_hashes=profile_hashes,
                     slicer_version=version,configuration_confirmed=True,project=str(target.relative_to(ROOT)),
                     project_sha256=g.sha(target),layers=len(layers),slicer_estimates=analysis["slicer_estimates"],
                     previews=previews,model_warnings=warnings,warning_resolution='Sportello anteriore aperto durante la stampa PLA; soglia software del profilo conservata.',cli=cli,
                     new_wall_island_candidates=analysis["new_wall_islands"]["candidate_count"],
                     visual_review_complete=False,supports=False,sent_to_printer=False)
            g.save(report,job);jobs.append(job)
        g.save(qa/"riepilogo.json",dict(jobs=jobs,kit_totals=estimate_totals([j for j in jobs if j["group"]=="kit"]),
                   replacement_totals=estimate_totals([j for j in jobs if j["group"]=="ricambi"]),slicer_version=version,
                   sent_to_printer=False))
    g.save(qa/"riepilogo.json",dict(jobs=jobs,kit_totals=estimate_totals([j for j in jobs if j["group"]=="kit"]),
               replacement_totals=estimate_totals([j for j in jobs if j["group"]=="ricambi"]),slicer_version=version,
               sent_to_printer=False))
    print(json.dumps(dict(plates=len(jobs),kit=estimate_totals([j for j in jobs if j["group"]=="kit"]),
                          ricambi=estimate_totals([j for j in jobs if j["group"]=="ricambi"]))),flush=True)


if __name__=="__main__":
    os.chdir(ROOT)
    main()
