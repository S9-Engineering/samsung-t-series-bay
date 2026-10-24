"""Sezioni, ombre geometriche verticali e limiti della ventilazione passiva."""
import json
import math
from pathlib import Path
import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
import genera as g
from verifica import section

ROOT=g.ROOT


def shadow(mesh, domain):
    triangles=mesh.triangles[:,:,:2]
    cross=(triangles[:,1,0]-triangles[:,0,0])*(triangles[:,2,1]-triangles[:,0,1])-(triangles[:,1,1]-triangles[:,0,1])*(triangles[:,2,0]-triangles[:,0,0])
    polygons=[]
    x0,y0,x1,y1=domain.bounds
    for points in triangles[np.abs(cross)>1e-8]:
        if points[:,0].max()<x0 or points[:,0].min()>x1 or points[:,1].max()<y0 or points[:,1].min()>y1:
            continue
        polygons.append(Polygon(points))
    return unary_union(polygons).intersection(domain)


def evaluate(folder):
    manifest=json.loads((folder/"verifiche/manifest.json").read_text())
    shells={row["kind"]:trimesh.load_mesh(folder/row["mesh"],process=True)
            for row in manifest["display"] if row["kind"] in ("struttura","coperchio")}
    domain=unary_union([box(a,18,b,101) for a,b in [(3,14),(28,38),(52,62),(76,87)]])
    # Sponde e tamponi a ingombro T9 in tutti e tre gli slot; le sedi sono identiche fra R02 e R03.
    obstacles=list(shells.values())
    for slot in range(3):
        obstacles += [g.mesh_of(g.moving_jaw(14.2,24*slot)),g.mesh_of(g.drive("T9",slot))]
        obstacles += [g.mesh_of(shape) for _,shape in g.pads("T9",slot)]
    obstacles += [trimesh.load_mesh(folder/row["mesh"],process=True)
                  for row in manifest["display"] if row["kind"]=="ferramenta_commerciale"]
    projected=unary_union([shadow(mesh,domain) for mesh in obstacles])
    clear=domain.difference(projected)
    roi=box(3,12,87,101)
    for x in (6,84):roi=roi.difference(Point(x,93).buffer(3.5))
    floor=roi.difference(section(shells["struttura"],2.5))
    roof=roi.difference(section(shells["coperchio"],84.5))
    # Sezione rettangolare YZ delle due pareti laterali: gli altri solidi sono lontani.
    side_area=2*4*6*17
    result=dict(revision=manifest["revision"],
        floor_net_vent_cm2=floor.area/100,roof_net_vent_cm2=roof.area/100,
        side_rectangular_upper_bound_cm2=side_area/100,
        continuous_vertical_clear_cm2=clear.area/100,
        corridor_areas_cm2=[clear.intersection(box(a,18,b,101)).area/100
                            for a,b in [(3,14),(28,38),(52,62),(76,87)]],
        method="Proiezione XY di tutte le facce triangolari dei solidi, sottratta ai quattro corridoi T9; area libera lungo l'intera altezza, entro la tessellazione. Fondo e tetto misurati sulle sezioni delle mesh esportate, esclusi i fori vite.",
        manifest_sha256=g.sha(folder/"verifiche/manifest.json"))
    return result


def main():
    current=evaluate(ROOT)
    previous_folder=ROOT.parent/"bay-ssd-universale-r02"
    reference=ROOT/"verifiche/r02_riferimento_aria.json"
    if (previous_folder/"verifiche/manifest.json").exists():
        previous=evaluate(previous_folder)
        g.save(reference,previous)
    else:
        previous=json.loads(reference.read_text())
    v=g.P["ventilazione"]
    shell=cq.importers.importStep(str(ROOT/"CAD/scocca_ventilata_R03.step")).val()
    lid=cq.importers.importStep(str(ROOT/"CAD/coperchio_ventilato_R03.step")).val()
    foundations=[]
    checks=[(f"piedino_{x}_{y}",shell,g.box(x,y,0,10,10,5))
            for x in (5,75) for y in (5,86)]
    checks += [(f"fondazione_slot_{i+1}_{k+1}",shell,s)
               for i in range(3) for k,s in enumerate(g.floor_anchors(i*24))]
    checks += [("spina_coperchio",lid,g.box(43.4,0,83,3.2,101,3))]
    for name,solid,probe in checks:
        fraction=sum(s.Volume() for s in solid.intersect(probe).Solids())/probe.Volume()
        assert fraction>.999,(name,fraction)
        foundations.append(dict(name=name,material_fraction=fraction))
    report=dict(revision="R03",current=current,comparison_R02=previous,
        changes_percent={key:100*(current[key]/previous[key]-1) for key in
                         ("floor_net_vent_cm2","roof_net_vent_cm2","continuous_vertical_clear_cm2")},
        geometry=dict(case_mm=[90,101,91],bottom_air_mm=8,top_air_mm=10,
                      face_gap_three_T9_mm=10,feet_mm=5,
                      top_slits=2*len(v["feritoie_centri_y"]),slit_rows=len(v["feritoie_centri_y"]),
                      slit_mm=[(v["feritoia_lunghezza"]-v["spina_centrale"])/2,v["feritoia_larghezza"]],
                      center_spine_mm=v["spina_centrale"],
                      solid_rib_mm=3.2,roof_thickness_mm=3,base_thickness_mm=5,
                      lid_side_rail_mm=(90-v["feritoia_lunghezza"])/2,
                      under_desktop_perimeter_gross_cm2=2*(90+101)*5/100),
        interpretation="Per uso intermittente il raffreddamento passivo e una scelta progettuale plausibile. Retro aperto, prese basse e tetto forato riducono il confinamento. Nessuna portata o temperatura calcolata: mancano potenze reali, condizioni ambiente e coefficienti di scambio. Il retro permette anche moti laterali; il percorso fondo-tetto non e obbligato.",
        buoyancy_sensitivity=dict(formula="delta_p = rho * g * H * delta_T / T0",
            assumptions=dict(rho_kg_m3=1.18,H_m=.08,T0_K=298,g_m_s2=9.81),
            illustrative_delta_T_K=[5,10,20],
            ideal_delta_p_Pa=[1.18*9.81*.08*dt/298 for dt in (5,10,20)],
            note="Solo ordine di grandezza della spinta per un canale ideale. Non e una simulazione della bay aperta, ne una stima di temperatura o di portata; delta_T assunto per sensibilita."),
        structural_assessment="Guscio unico con pareti 3 mm e fondo 5 mm; coperchio 3 mm con nervature e spina centrale da 3.2 mm, bordo laterale 5 mm, quattro viti su piazzole piene. Le feritoie sono divise in due banchi: luce di ciascuna apertura 38.4 mm. Materiale ripristinato sotto guide/appoggi, battute e piedini. Nessuna FEA o prova di carico: rigidezza, creep e stabilita da verificare fisicamente.",
        solid_foundations=foundations,
        fan=dict(present=False,mounting_interface_designed=False,
                 note="Solo feritoie inferiori. Futuro adattatore e interasse ventola non progettati."),
        thermal_test=False,cfd=False,
        test_protocol=["SSD fuori/dentro il bay nello stesso orientamento, ambiente e carico; registrare temperatura ambiente.",
                       "Provare uno, due e tre SSD; ripetere con il T9 centrale e coperchio montato.",
                       "Fasi: scollegato; collegato inattivo 30 min; carico intermittente rappresentativo; trasferimento sostenuto almeno 60 min e fino a stabilizzazione.",
                       "Usare un volume di prova: registrare temperatura via sensore se disponibile, temperatura esterna e velocita; verificare assenza di disconnessioni.",
                       "Se la bay alza sensibilmente la temperatura o anticipa un calo di prestazioni rispetto alla stessa prova all'aperto, aumentare aperture/distanze prima di dichiarare riuscita la soluzione passiva.",
                       "Temperatura di superficie, sensore interno e intervallo ambiente ammesso dal produttore sono grandezze diverse."],
        sources=[dict(title="COMSOL: natural convection, buoyancy and Boussinesq approximation",url="https://www.comsol.com/blogs/introduction-to-modeling-natural-convection-in-comsol-multiphysics/",accessed="2026-10-20"),
                 dict(title="nVent HOFFMAN: prese alte e basse",url="https://www.nvent.com/en-se/hoffman/products/encuav01",accessed="2026-10-20")])
    g.save(ROOT/"verifiche/valutazione_aria.json",report)
    print(json.dumps(dict(current=current,changes=report["changes_percent"])),flush=True)


if __name__=="__main__":main()
