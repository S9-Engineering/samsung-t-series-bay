"""3MF geometrici e veri progetti ElegooSlicer. Nessun avvio di stampa."""
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

import numpy as np
import trimesh
from shapely.geometry import box as rect

import genera as g
from slicer_utils import run_cli,parse_gcode,render_layers,screen_new_wall_islands,estimate_totals

ROOT=g.ROOT
NS="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("",NS)
def tag(n):return "{"+NS+"}"+n


def export_plate(path,items,meshes):
    model=ET.Element(tag("model"),unit="millimeter",**{"xml:lang":"it-IT"})
    ET.SubElement(model,tag("metadata"),name="Title").text="BAY SSD R05 - sola geometria; profili assenti"
    resources=ET.SubElement(model,tag("resources"));build=ET.SubElement(model,tag("build"))
    for idx,item in enumerate(items,1):
        m=meshes[item["part"]].copy()
        m.apply_translation(-m.bounds[0]);m.apply_translation([*item["xy"],0])
        item["bounds_mm"]=m.bounds.tolist()
        obj=ET.SubElement(resources,tag("object"),id=str(idx),type="model",name=item["name"])
        mesh=ET.SubElement(obj,tag("mesh"));vs=ET.SubElement(mesh,tag("vertices"));ts=ET.SubElement(mesh,tag("triangles"))
        for v in m.vertices:
            ET.SubElement(vs,tag("vertex"),**{a:f"{value:.7f}"for a,value in zip("xyz",v)})
        for f in m.faces:
            ET.SubElement(ts,tag("triangle"),**{f"v{i+1}":str(int(x))for i,x in enumerate(f)})
        ET.SubElement(build,tag("item"),objectid=str(idx))
    types='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED)as z:
        for name,data in [("[Content_Types].xml",types),("_rels/.rels",rels),("3D/3dmodel.model",ET.tostring(model,encoding="utf-8",xml_declaration=True))]:
            entry=zipfile.ZipInfo(name,date_time=(2026,10,20,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(entry,data)


def check_3mf(path,expected,brim=5):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        root=ET.fromstring(z.read("3D/3dmodel.model"));assert root.get("unit")=="millimeter"
        obs=root.findall(tag("resources")+"/"+tag("object"));build=root.findall(tag("build")+"/"+tag("item"))
        assert len(obs)==len(build)==expected
        boxes=[]
        for obj,item in zip(obs,build):
            assert item.get("objectid")==obj.get("id")
            assert item.get("transform","1 0 0 0 1 0 0 0 1 0 0 0")=="1 0 0 0 1 0 0 0 1 0 0 0"
            vs=np.array([[float(v.get(a))for a in "xyz"]for v in obj.findall(".//"+tag("vertex"))])
            fs=np.array([[int(t.get(a))for a in ("v1","v2","v3")]for t in obj.findall(".//"+tag("triangle"))])
            m=trimesh.Trimesh(vs,fs,process=True)
            assert m.is_watertight and m.volume>0 and m.is_winding_consistent
            assert np.min(m.bounds[0,:2]-brim)>=0 and np.max(m.bounds[1,:2]+brim)<=256
            footprint=rect(*[m.bounds[0,0]-brim,m.bounds[0,1]-brim,m.bounds[1,0]+brim,m.bounds[1,1]+brim])
            assert footprint.intersection(rect(246,0,256,20)).area==0
            for previous in boxes:assert footprint.intersection(previous).area==0
            boxes.append(footprint)
    return dict(objects=expected,units="millimeter",identity_transforms=True,brim_clearance_mm=brim,
                nominal_bed_mm=[256,256],exclusion_zone_mm=[[246,0],[256,20]],pass_=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--slice",action="store_true")
    ap.add_argument("--slicer",type=Path,default=Path("/private/tmp/stampe3d-slicer/ElegooSlicer.app/Contents/MacOS/ElegooSlicer"))
    args=ap.parse_args()
    manifest=json.loads((ROOT/"verifiche/manifest.json").read_text())
    assert manifest["parameters_sha256"]==g.sha(ROOT/"sorgenti/parametri.json")
    geometric_checks=json.loads((ROOT/"verifiche/geometria.json").read_text())
    assert geometric_checks["result"].startswith("PASS")
    assert geometric_checks["source_manifest_sha256"]==g.sha(ROOT/"verifiche/manifest.json")
    assert geometric_checks["source_parameters_sha256"]==manifest["parameters_sha256"]
    def item(part,name,x,y):return dict(part=part,name=name,xy=[x,y])
    plates=[
        dict(name="BAY_R05_00_PROVINO_PRIMA_DI_TUTTO",group="provino",items=[
            item("provino_sede_R05","provino_sede",20,28),
            item("inserto_T7_R05","inserto_T7_1",65,28),item("inserto_T7_R05","inserto_T7_2",85,28),
            item("inserto_Shield_R05","inserto_Shield_1",65,60),item("inserto_Shield_R05","inserto_Shield_2",85,60),
            item("provino_chiusura_femmina_R05","chiusura_femmina",115,28),
            item("provino_chiusura_maschio_R05","chiusura_maschio",140,28)]),
        dict(name="BAY_R05_01_SCOCCA_INSERTI",group="kit",items=[
            item("scocca_R05","scocca",20,28),
            item("inserto_T7_R05","inserto_T7_1",135,28),item("inserto_T7_R05","inserto_T7_2",155,28),
            item("inserto_Shield_R05","inserto_Shield_1",135,60),item("inserto_Shield_R05","inserto_Shield_2",155,60)]),
        dict(name="BAY_R05_02_COPERCHIO",group="kit",items=[item("coperchio_R05","coperchio_capovolto",30,30)])
    ]
    meshes={p["name"]:trimesh.load_mesh(ROOT/p["stl"],process=True)for p in manifest["parts"]}
    for plate in plates:
        path=ROOT/"stampa/piatti_geometrici"/(plate["name"]+"_GEOMETRIA.3mf")
        path.parent.mkdir(parents=True,exist_ok=True)
        export_plate(path,plate["items"],meshes)
        plate["geometry_3mf"]=str(path.relative_to(ROOT))
        plate["sha256"]=g.sha(path)
        plate["geometry_check"]=check_3mf(path,len(plate["items"]))
    g.save(ROOT/"verifiche/piatti.json",dict(plates=plates,geometry_only=True))
    if not args.slice:return
    assert g.P["configurazione_stampa"]["confermata_utente"]
    machine,process,filament=[ROOT/"slicer"/n for n in ("machine.json","process.json","filament.json")]
    machine_settings=json.loads(machine.read_text())
    assert "Centauri Carbon 2" in machine_settings["name"]
    assert machine_settings["nozzle_diameter"]==["0.4"]
    plist=args.slicer.parents[1]/"Info.plist"
    if plist.exists():
        version=plistlib.loads(plist.read_bytes())["CFBundleShortVersionString"]
    else:
        result=subprocess.run([str(args.slicer),"--help"],text=True,capture_output=True,check=True)
        version=re.search(r"ElegooSlicer-([0-9.]+)",result.stdout).group(1)
    qa=ROOT/"verifiche/slicing";qa.mkdir(exist_ok=True)
    output=ROOT/"stampa/progetti_ElegooSlicer";output.mkdir(exist_ok=True)
    jobs=[]
    for plate in plates:
        name=plate["name"];report=qa/(name+"_job.json")
        target=output/(name+"_ECC2_PETGPRO.3mf")
        profile_hashes={p.name:g.sha(p)for p in (machine,process,filament)}
        if report.exists():
            old=json.loads(report.read_text())
            if old["geometry_sha256"]==plate["sha256"] and old["profile_hashes"]==profile_hashes and target.exists() and old["project_sha256"]==g.sha(target):
                jobs.append(old);continue
        with tempfile.TemporaryDirectory(prefix="bay-r05-slicer-")as td:
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
                assert not warnings,warnings
                settings=json.loads(z.read("Metadata/project_settings.config"))
                assert settings["nozzle_diameter"]==["0.4"] and settings["curr_bed_type"]=="Textured PEI Plate"
                assert settings["layer_height"]=="0.2" and settings["filament_type"]==["PETG"]
                assert settings["enable_support"]=="0"
                members=[n for n in z.namelist()if n.endswith(".gcode")];assert len(members)==1
                import hashlib
                assert hashlib.sha256(z.read(members[0])).hexdigest()==g.sha(gcodes[0])
                # Riapertura indipendente della geometria del progetto nativo.
                scene=trimesh.load(project,force="scene")
                assert len(scene.graph.nodes_geometry)==len(plate["items"])
                assert ET.fromstring(z.read("3D/3dmodel.model")).get("unit")=="millimeter"
                actual=[]
                for node in scene.graph.nodes_geometry:
                    transform,geometry_name=scene.graph[node]
                    mesh=scene.geometry[geometry_name].copy();mesh.apply_transform(transform)
                    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
                    actual.append(mesh.extents.tolist())
                expected=[meshes[i["part"]].extents.tolist()for i in plate["items"]]
                assert np.max(np.abs(np.array(sorted(actual))-np.array(sorted(expected))))<.06
            shutil.copy2(project,target)
            job=dict(name=name,group=plate["group"],geometry_sha256=plate["sha256"],profile_hashes=profile_hashes,
                     slicer_version=version,configuration_confirmed=True,project=str(target.relative_to(ROOT)),
                     project_sha256=g.sha(target),layers=len(layers),slicer_estimates=analysis["slicer_estimates"],
                     previews=previews,model_warnings=warnings,cli=cli,
                     new_wall_island_candidates=analysis["new_wall_islands"]["candidate_count"],
                     visual_review_complete=False,supports=False,sent_to_printer=False)
            g.save(report,job);jobs.append(job)
        g.save(qa/"riepilogo.json",dict(jobs=jobs,kit_totals=estimate_totals([j for j in jobs if j["group"]=="kit"]),
                   coupon_totals=estimate_totals([j for j in jobs if j["group"]=="provino"]),slicer_version=version,
                   sent_to_printer=False))
    g.save(qa/"riepilogo.json",dict(jobs=jobs,kit_totals=estimate_totals([j for j in jobs if j["group"]=="kit"]),
               coupon_totals=estimate_totals([j for j in jobs if j["group"]=="provino"]),slicer_version=version,
               sent_to_printer=False))
    print(json.dumps(dict(plates=len(jobs),kit=estimate_totals([j for j in jobs if j["group"]=="kit"]),
                          coupon=estimate_totals([j for j in jobs if j["group"]=="provino"]))),flush=True)


if __name__=="__main__":
    main()
