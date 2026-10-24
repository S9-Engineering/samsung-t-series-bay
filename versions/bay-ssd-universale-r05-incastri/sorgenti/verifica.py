"""Controlli sui file R05 esportati e sull'assieme statico nominale."""
import itertools,json
import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT;P=g.P


def overlap(a,b):
    ba,bb=np.array(g.bounds(a)),np.array(g.bounds(b))
    if np.any(np.minimum(ba[1],bb[1])-np.maximum(ba[0],bb[0])<=1e-6):return 0.
    return sum(s.Volume() for s in a.intersect(b).Solids())


def section(mesh,z):
    cut=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    out=Polygon()
    if cut:
        for loop in cut.discrete:
            if len(loop)>=4 and np.linalg.norm(loop[0]-loop[-1])<1e-4:
                p=Polygon(loop[:,:2]);out=out.symmetric_difference(p if p.is_valid else p.buffer(0))
    return out


def shadow(mesh,domain):
    triangles=mesh.triangles[:,:,:2]
    a,b=triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]
    cross=a[:,0]*b[:,1]-a[:,1]*b[:,0]
    return unary_union([Polygon(t) for t in triangles[np.abs(cross)>1e-8]]).intersection(domain)


def main():
    man=json.loads((ROOT/"verifiche/manifest.json").read_text())
    assert man["parameters_sha256"]==g.sha(ROOT/"sorgenti/parametri.json")
    shapes={};rows=[];cache_path=ROOT/"verifiche/cache_autointersezioni.json"
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    for part in man["parts"]:
        print("CONTROLLO",part["name"],flush=True)
        m=trimesh.load_mesh(ROOT/part["stl"],process=True)
        si=cache.get(part["stl_sha256"])
        if si is None:
            si=self_intersections_fast(m);cache[part["stl_sha256"]]=si;g.save(cache_path,cache)
        assert g.sha(ROOT/part["stl"])==part["stl_sha256"]
        source=cq.importers.importStep(str(ROOT/part["step"])).val()
        printed=cq.importers.importStep(str(ROOT/"CAD"/(part["name"]+"_orientato_stampa.step"))).val()
        assert source.isValid() and printed.isValid()
        assert len(source.Solids())==len(printed.Solids())==1
        assert m.is_watertight and m.is_winding_consistent and m.volume>0
        assert len(m.split())==m.body_count==1
        assert not np.any(m.area_faces<1e-10)
        assert len(np.unique(np.sort(m.faces,axis=1),axis=0))==len(m.faces)
        assert si["intersection_pairs"]==0,(part["name"],si)
        assert abs(m.volume/source.Volume()-1)<.005
        assert np.max(np.abs(m.bounds-np.array(g.bounds(printed))))<.06
        shapes[part["name"]]=source
        rows.append(dict(name=part["name"],stl_sha256=part["stl_sha256"],step_sha256=g.sha(ROOT/part["step"]),
            mesh_closed=True,winding_consistent=True,volume_positive_mm3=m.volume,
            components=1,step_valid=True,degenerate_faces=0,duplicate_faces=0,
            self_intersections=si,print_bounds_mm=m.bounds.tolist()))
    shell,lid=shapes["scocca_R05"],shapes["coperchio_R05"]
    assert overlap(shell,lid)<1e-5
    cases=[]
    for slot in range(3):
        for model,d in P["ssd_nominali"].items():
            ssd=g.drive(model,slot)
            inserts=[] if model=="T9" else [g.adapter(model,y,slot) for y in g.S["centri_y"]]
            solids=[shell,lid,*inserts]
            values=[overlap(ssd,s) for s in solids]
            assert max(values)<1e-5,(slot,model,values)
            for insert in inserts:
                assert overlap(insert,shell)<1e-5 and overlap(insert,lid)<1e-5,(slot,model,"inserto")
            lifts=[]
            for dz in (1,5,10,20,40,90):
                v=sum(overlap(g.drive(model,slot,dz),s) for s in [shell,*inserts])
                assert v<1e-5,(slot,model,"estrazione",dz,v)
                lifts.append(dict(lift_mm=dz,intersections_mm3=v))
            cases.append(dict(slot=slot+1,model=model,adapters=len(inserts),
                aperture_mm=g.S["larghezze_adattate"][model],total_thickness_clearance_mm=g.S["larghezze_adattate"][model]-d["spessore"],
                static_intersections_mm3=values,extraction_samples=lifts))
    assignments=[]
    for models in itertools.product(P["ssd_nominali"],repeat=3):
        solids=[]
        for slot,model in enumerate(models):
            solids += [g.drive(model,slot)]
            if model!="T9":solids += [g.adapter(model,y,slot) for y in g.S["centri_y"]]
        for a,b in itertools.combinations(solids,2):assert overlap(a,b)<1e-5,models
        assignments.append(list(models))
    assert overlap(shapes["provino_chiusura_femmina_R05"],shapes["provino_chiusura_maschio_R05"])<1e-5
    assert overlap(shapes["provino_sede_R05"],g.adapter("T7"))<1e-5
    assert overlap(shapes["provino_sede_R05"],g.adapter("T7_Shield"))<1e-5
    ass=cq.importers.importStep(str(ROOT/"CAD/BAY_R05_ASSIEME_GABARIT.step")).val()
    assert ass.isValid() and len(ass.Solids())==len(man["display"])==9
    # Le quattro tasche hanno fondo pieno; la verifica non determina il piedino commerciale.
    feet=[]
    for x,y in P["piedini"]["centri_xy"]:
        probe=g.cylinder(x,y,.8,5,.2);fraction=overlap(probe,shell)/probe.Volume()
        assert fraction>.999;feet.append(dict(x=x,y=y,solid_floor_fraction=fraction))
    mesh_shell=g.mesh_of(shell);mesh_lid=g.mesh_of(lid)
    roi=box(3,12,87,101)
    domain=unary_union([box(a,18,b,101) for a,b in ((3,14),(28,38),(52,62),(76,87))])
    obstacles=[mesh_shell,mesh_lid,*[g.mesh_of(g.drive("T9",i)) for i in range(3)]]
    free=domain.difference(unary_union([shadow(m,domain) for m in obstacles]))
    air=dict(floor_net_cm2=roi.difference(section(mesh_shell,2.5)).area/100,
             roof_net_cm2=roi.difference(section(mesh_lid,84.5)).area/100,
             continuous_vertical_corridors_three_T9_cm2=free.area/100,
             method="Aree sulle mesh esportate; corridoi verticali conservativi dalla proiezione di tutti i solidi, tre T9 senza inserti.",
             cfd=False,thermal_test=False)
    assert air["continuous_vertical_corridors_three_T9_cm2"]>0
    g.save(ROOT/"verifiche/aria.json",air)
    g.save(ROOT/"verifiche/geometria.json",dict(result="PASS_DIGITALE_QUOTE_NOMINALI",
        source_manifest_sha256=g.sha(ROOT/"verifiche/manifest.json"),source_parameters_sha256=man["parameters_sha256"],
        export_checks=rows,model_slot_cases=cases,assignments_checked=len(assignments),
        assignment_cases=assignments,assembly_step_solids=9,kit_parts=6,feet=feet,
        body_lid_static_overlap_mm3=overlap(shell,lid),hardware_components=0,internal_adhesives=False,
        guide_channel_mm=15,adapters_channels_mm=dict(T7=9,Shield=13.6),
        guide_height_above_seat_mm=18,printed_adapter_inner_plate_min_mm=1.1,
        lid_snap_finger_mm=dict(thickness=1.2,width=8,length=12,engagement=.6),
        adapter_hook_engagement_mm=.2,
        limitations=["Quote nominali, SSD e gommini reali non misurati.",
            "Agganci verificati staticamente: deformazione, forza di montaggio ed elasticita non validate.",
            "Screening autointersezioni esclude triangoli con vertici condivisi.",
            "Estrazione verificata a quote campionate con coperchio rimosso e cavi scollegati.",
            "Assenza di serraggio: i dischi sono guidati e appoggiati, il retro rimane aperto.",
            "Nessuna prova fisica o termica."],
        physical_fit=False,physical_print=False,thermal_test=False))
    print(json.dumps(dict(exports=len(rows),model_slot_cases=len(cases),assignments=len(assignments),air=air)),flush=True)


if __name__=="__main__":main()
