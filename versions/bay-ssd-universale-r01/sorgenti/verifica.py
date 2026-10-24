"""Riapertura export, interferenze BREP e sezioni geometriche dell'aria."""
from pathlib import Path
import itertools
import json
import math

import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import Polygon, box as rectangle
from shapely.ops import unary_union

import genera as g
from verifica_intersezioni_mesh import self_intersections_fast

ROOT, P = g.ROOT, g.P


def overlap(a, b):
    ba, bb = np.array(g.bounds(a)), np.array(g.bounds(b))
    if np.any(np.minimum(ba[1], bb[1]) - np.maximum(ba[0], bb[0]) <= 1e-6):
        return 0.0
    common = a.intersect(b)
    return sum(s.Volume() for s in common.Solids())


def section(mesh, z):
    cut = mesh.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
    result = Polygon()
    if cut is None:
        return result
    for loop in cut.discrete:
        if len(loop) >= 4 and np.linalg.norm(loop[0]-loop[-1]) < 1e-4:
            p = Polygon(loop[:,:2])
            if not p.is_valid:
                p = p.buffer(0)
            result = result.symmetric_difference(p)
    return result


def main():
    manifest = json.loads((ROOT/"verifiche/manifest.json").read_text())
    assert manifest["parameters_sha256"] == g.sha(ROOT/"sorgenti/parametri.json")
    rows = []
    shapes, meshes = {}, {}
    cache_path = ROOT/"verifiche/cache_autointersezioni.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    for p in manifest["parts"]:
        print("CONTROLLO EXPORT", p["name"], flush=True)
        path = ROOT/p["stl"]
        assert g.sha(path) == p["stl_sha256"]
        m = trimesh.load_mesh(path, process=True)
        si = cache.get(p["stl_sha256"])
        if si is None:
            si = self_intersections_fast(m)
            cache[p["stl_sha256"]] = si
            g.save(cache_path, cache)
        source = cq.importers.importStep(str(ROOT/p["step"])).val()
        print_step = cq.importers.importStep(
            str(ROOT/"CAD"/(p["name"]+"_orientato_stampa.step"))).val()
        assert source.isValid() and print_step.isValid()
        assert len(source.Solids()) == len(print_step.Solids()) == 1
        assert m.is_watertight and m.is_winding_consistent and m.volume > 0
        assert len(m.split()) == 1
        assert m.body_count == 1
        assert not np.any(m.area_faces < 1e-10)
        assert len(np.unique(np.sort(m.faces,axis=1),axis=0)) == len(m.faces)
        assert si["intersection_pairs"] == 0, (p["name"], si)
        size = np.array(p["print_bounds_mm"])[1] - np.array(p["print_bounds_mm"])[0]
        # I box BREP delle superfici raccordate includono le tolleranze OCC;
        # la differenza deve restare sotto la deviazione di tessellazione.
        assert np.max(np.abs(m.extents-size)) < .06
        assert abs(m.volume/source.Volume()-1) < .005
        assert np.max(np.abs(np.array(g.bounds(print_step)) - m.bounds)) < .06
        rows.append(dict(name=p["name"], faces=len(m.faces), size_mm=m.extents.tolist(),
                         stl_sha256=p["stl_sha256"], step_sha256=g.sha(ROOT/p["step"]),
                         watertight=True, winding_consistent=True, positive_volume_mm3=m.volume,
                         connected_components=1, surface_bodies=1, degenerate_faces=0,
                         duplicate_faces=0, step_valid=True, step_solids=1,
                         step_volume_mm3=source.Volume(), self_intersections=si))
        shapes[p["name"]] = source
        meshes[p["name"]] = trimesh.load_mesh(ROOT/p["assembly_mesh"],process=True)
    shell, lid, cap = [shapes[n] for n in ("scocca_ventilata_R01","coperchio_ventilato_R01","cappello_fermacavi_R01")]
    cases = []
    all_shapes = [shell,lid,cap]
    for slot in range(3):
        for model, d in P["ssd_nominali"].items():
            ap = d["spessore"] + P["gioco_laterale_nominale_totale"]
            jaw = g.moving_jaw(ap, slot*P["passo_slot"])
            ssd = g.drive(model,slot)
            obstruction = {n:overlap(ssd,s) for n,s in [("scocca",shell),("coperchio",lid),("fermacavi",cap),("sponda",jaw)]}
            for name,value in obstruction.items():
                assert value < 1e-5,(model,slot,name,value)
            assert overlap(jaw,shell) < 1e-5,(model,slot,"sponda contro scocca")
            lifts = []
            for dz in (1,5,15,30,60,90):
                lifted = ssd.translate((0,0,dz))
                value = overlap(lifted,shell) + overlap(lifted,jaw)
                assert value < 1e-5,(model,slot,"estrazione",dz,value)
                lifts.append(dict(lift_mm=dz, rigid_collision_mm3=value))
            # Accesso utensile dopo rimozione del coperchio.
            tool = g.cylinder(27+slot*P["passo_slot"],8,P["base"]+7,3.5,90)
            assert overlap(tool,shell) < 1e-5 and overlap(tool,ssd) < 1e-5
            # Inviluppo dello spinotto: sezione provvisoria, lunghezza utente.
            x=P["prima_faccia_ssd_x"]+slot*P["passo_slot"]+d["spessore"]/2
            z=g.SSD_Z+d["altezza"]/2
            cx=P["cavi"]["connettore_gabarit_x"];cz=P["cavi"]["connettore_gabarit_z"]
            stiff=P["cavi"]["tratto_rigido_massimo_dichiarato_utente"]
            plug=g.box(x-cx/2,P["inizio_ssd_y"]+d["lunghezza"],z-cz/2,cx,stiff,cz)
            assert sum(overlap(plug,s) for s in (shell,lid,jaw,cap)) < 1e-5
            displacement=np.linalg.norm([P["cavi"]["centri_uscita_x"][slot]-x,
                                         P["cavi"]["centro_uscita_z"]-z])
            dy=P["cavi"]["fermacavi_y"]-7-(P["inizio_ssd_y"]+d["lunghezza"]+stiff)
            radius=math.inf if displacement < 1e-8 else 2*dy**2/(displacement*math.pi**2)
            assert radius >= P["cavi"]["raggio_curva_di_progetto"]
            cases.append(dict(model=model,slot=slot+1,aperture_mm=ap,
                              rigid_intersections_mm3=obstruction,vertical_extraction=lifts,
                              driver_diameter_mm=7,driver_access=True,
                              connector_envelope_mm=[cx,stiff,cz],connector_envelope_collision=False,
                              min_radius_of_designed_cable_centerline_mm=radius))
        # Estremi meccanici della corsa, indipendenti dai modelli nominali.
        for ap in (P["apertura_minima_fra_tamponi"],P["apertura_massima_fra_tamponi"]):
            assert overlap(g.moving_jaw(ap,slot*24),shell) < 1e-5
    for slot in range(3):
        all_shapes.append(g.moving_jaw(14.2,slot*24))
    rigid_pairs = []
    for (i,a),(j,b) in itertools.combinations(enumerate(all_shapes),2):
        v=overlap(a,b)
        assert v<1e-5,(i,j,v)
        rigid_pairs.append(dict(parts=[i,j],intersection_mm3=v))
    # Tutte le 27 assegnazioni per urti fra sponde adiacenti e fra cavi.
    combinations = []
    for models in itertools.product(P["ssd_nominali"],repeat=3):
        jaws=[g.moving_jaw(P["ssd_nominali"][m]["spessore"]+.2,i*24) for i,m in enumerate(models)]
        for a,b in itertools.combinations(jaws,2):
            assert overlap(a,b)<1e-5
        paths=[g.cable_path(m,i,201) for i,m in enumerate(models)]
        # Tutte le ascisse restano ordinate: distanza minima trasversale a Y uguale.
        ys=np.linspace(max(p[0,1] for p in paths),P["profondita"],400)
        spans=[]
        for a,b in zip(paths[:-1],paths[1:]):
            dx=np.interp(ys,b[:,1],b[:,0])-np.interp(ys,a[:,1],a[:,0])
            dz=np.interp(ys,b[:,1],b[:,2])-np.interp(ys,a[:,1],a[:,2])
            clearance=np.min(np.sqrt(dx*dx+dz*dz))-P["cavi"]["diametro_dichiarato_utente"]
            assert clearance>0
            spans.append(float(clearance))
        combinations.append(dict(models=models,jaw_collisions=False,
                                 cable_same_y_surface_clearance_mm=spans,
                                 note="Sezioni a Y uguale; non distanza globale minima fra curve."))
    assembly_step=cq.importers.importStep(str(ROOT/"CAD/BAY_SSD_R01_ASSIEME_CON_GABARIT.step")).val()
    assert assembly_step.isValid()
    assert len(assembly_step.Solids())==len(manifest["display"])
    # Aria: misura di passaggi geometrici verticali, senza simulazione di calore.
    domain=unary_union([rectangle(a,18,b,104) for a,b in [(3,14),(28,38),(52,62),(76,87)]])
    air_meshes=[meshes["scocca_ventilata_R01"],meshes["coperchio_ventilato_R01"]]
    air_meshes += [g.mesh_of(s) for s in all_shapes[3:]]
    sections=[]; common=domain
    for z in (2.5,5.1,6.5,7.5,10,12,14,20,26,40,65,75,g.ROOF_Z+1.5):
        occupied=unary_union([section(m,z) for m in air_meshes if m.bounds[0,2]<z<m.bounds[1,2]])
        free=domain.difference(occupied)
        common=common.intersection(free)
        sections.append(dict(z_mm=z,open_cm2=free.area/100))
    assert common.area>0
    g.save(ROOT/"verifiche/geometria.json",dict(
        result="PASS_DIGITALE_QUOTE_NOMINALI",export_checks=rows,model_slot_cases=cases,
        assignments_checked=len(combinations),assignment_cases=combinations,
        rigid_assembly_intersections=rigid_pairs,assembly_step_valid=True,
        assembly_step_solids=len(assembly_step.Solids()),
        minimum_nominal_t9_face_gap_mm=10,outer_face_to_wall_mm=[11,11],
        under_ssd_mm=8,above_t9_mm=10,feet_mm=5,
        guide_clearance_per_side_mm=.3,guide_vertical_clearance_mm=.4,
        critical_sections_mm=dict(sliding_guide_roof=1.4,slider_side_fingers=2,
                                  main_shell_wall=3,lid_panel=3,
                                  nut_ceiling_under_jaw=P["base"]-2.6,
                                  cable_cap_crown=4),
        limitations=["Gabarit SSD nominali: nessuna misura al calibro",
                     "Sezioni e posizione reale delle porte e degli spinotti non rilevate",
                     "Verifica estrazione a posizioni campionate con cavi scollegati e coperchio rimosso",
                     "Screening triangoli esclude coppie con vertici condivisi",
                     "Nessuna prova fisica di accoppiamento, resistenza, serraggio o stabilita",
                     "Raggio 25 mm scelto per il progetto, non certificato dal produttore dei cavi"],
        mesh_repairs="Nessuna riparazione; sola unione dei vertici coincidenti durante lettura trimesh.",
        physical_print=False,thermal_test=False))
    g.save(ROOT/"verifiche/aria.json",dict(
        sections=sections,common_vertical_open_cm2=common.area/100,
        note="Sezioni di soli quattro corridoi fra SSD T9. Area geometrica campionata, non portata, CFD o garanzia termica.",
        test_plan="Confrontare stesso SSD, carico e ambiente dentro/fuori dal bay; poi tre unita insieme, almeno 60 minuti e fino a stabilizzazione. Registrare temperatura disponibile, throughput e disconnessioni. Nessuna scrittura su dati esistenti senza un volume di prova.",
        central_slot_priority=True,thermal_test=False))
    print(json.dumps(dict(exports=len(rows),model_slot_cases=len(cases),assignments=len(combinations),
                          vertical_open_cm2=common.area/100)),flush=True)


if __name__=="__main__":
    main()
