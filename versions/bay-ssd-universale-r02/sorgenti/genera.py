"""Bay SSD R02. CAD parametrico in mm; nessun invio alla stampante."""
from pathlib import Path
import json
import math
import hashlib
import importlib.metadata

import cadquery as cq
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "sorgenti/parametri.json").read_text())
W, D, B = P["larghezza"], P["profondita"], P["base"]
SSD_Z = B + P["aria_sotto_ssd"]
ROOF_Z = SSD_Z + P["ssd_nominali"]["T9"]["altezza"] + P["aria_sopra_t9"]


def box(x, y, z, dx, dy, dz):
    assert min(dx, dy, dz) > 0
    return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x, y, z))


def cylinder(x, y, z, radius, length, direction=(0, 0, 1)):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x, y, z), cq.Vector(*direction))


def union(shapes):
    return shapes[0].fuse(*shapes[1:]).clean() if len(shapes) > 1 else shapes[0]


def rounded_box(x, y, z, dx, dy, dz, radius):
    return (cq.Workplane("XY").box(dx, dy, dz, centered=False)
            .edges("|Z").fillet(radius).val().translate((x, y, z)))


def hex_pocket(x, y, z, height):
    return (cq.Workplane("XY").polygon(6, 2 * P["tasca_dado_m3_chiave"] / math.sqrt(3))
            .extrude(height).val().translate((x, y, z)))


def slot_hole(cx, cy, z, length, diameter, height):
    return (cq.Workplane("XY").slot2D(length, diameter).extrude(height)
            .val().translate((cx, cy, z)))


def fixed_features(offset=0):
    x = P["prima_faccia_ssd_x"] + offset
    solids = []
    for y in P["appoggi_y"]:
        # Appoggio largo 8 mm: centro del T9 ancora nel poligono di appoggio.
        solids += [box(x, y - 4, B, 8, 8, SSD_Z - P["spessore_silicone"] - B),
                   box(x - 3, y - 3, B, 2, 6, 20)]
    for y in P["guide_y"]:
        solids.append(box(x + 4.5, y - 1, B, 16, 2, 2))
    solids.append(box(x, P["inizio_ssd_y"] - 3, B, 8, 2, 14))
    return solids


def floor_anchors(offset=0):
    x=P["prima_faccia_ssd_x"]+offset
    return [box(x-3,y-4,0,11,8,B+1) for y in P["appoggi_y"]]


def moving_jaw(aperture=14.2, offset=0):
    x = P["prima_faccia_ssd_x"] + offset + aperture + P["spessore_silicone"]
    solids = [box(x, 12, B, 2, 77, 5), box(x - 6.7, 4, B, 15, 8, 4)]
    for y in P["guide_y"]:
        solids.append(box(x - 4, y - 5, B, 8, 10, 3.8))
    for y in P["appoggi_y"]:
        solids.append(box(x, y - 3, B + 4, 2, 6, 16))
    raw = union(solids)
    cuts = []
    for y in P["guide_y"]:
        cuts.append(box(x - 5, y - 1 - P["gioco_guida_per_lato"], B - 1,
                        10, 2 + 2 * P["gioco_guida_per_lato"],
                        3 + P["gioco_guida_verticale"]))
    travel = P["apertura_massima_fra_tamponi"] - P["apertura_minima_fra_tamponi"]
    cuts.append(slot_hole(x + .8, 8, B - 1, travel + P["foro_m3"], P["foro_m3"], 7))
    return raw.cut(*cuts).clean()


def floor_holes():
    holes = []
    for x, width in [(4.5, 8), (28.5, 9), (52.5, 9), (76.5, 9)]:
        for y0, y1 in [(28, 66), (77, 101)]:
            y1=min(y1,D-4)
            holes.append(rounded_box(x, y0, -1, width, y1 - y0, B + 2, 1))
    return holes


def jaw_nut_holes(offset=0):
    x = P["prima_faccia_ssd_x"] + offset + 13
    return [cylinder(x, 8, -1, P["foro_m3"] / 2, 10), hex_pocket(x, 8, -.1, 2.7)]


def shell():
    outer = rounded_box(0, 0, 0, W, D, ROOF_Z, 3)
    inner = rounded_box(3, 3, B, W - 6, D - 6, ROOF_Z, 1)
    result = outer.cut(inner)
    print("SCOCCA: guscio", result.isValid(), len(result.Solids()), flush=True)
    solids = [result]
    for i in range(3):
        solids += fixed_features(i * P["passo_slot"])
    # Torrette con dado M3 inseribile da una finestra laterale.
    for x in (3, W - 11):
        for y in (3, D - 15):
            left = x < W/2
            wall_x = x if left else x+8
            inside_x = x+8 if left else x
            wire=cq.Wire.makePolygon([
                cq.Vector(wall_x,y,ROOF_Z-20),cq.Vector(wall_x,y,ROOF_Z),
                cq.Vector(inside_x,y,ROOF_Z),cq.Vector(inside_x,y,ROOF_Z-12)],close=True)
            solids.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,12,0)))
    result = union(solids)
    print("SCOCCA: appoggi e guide", result.isValid(), len(result.Solids()), flush=True)
    cuts = floor_holes()
    # Retro completamente aperto sopra la base, senza parete o vano cavi.
    cuts.append(box(3,D-4,B,W-6,6,ROOF_Z))
    for i in range(3):
        cuts += jaw_nut_holes(i * P["passo_slot"])
    for x in (6, W - 6):
        for y in (8, D - 8):
            cuts += [cylinder(x, y, ROOF_Z - 15, P["foro_m3"] / 2, 20),
                     hex_pocket(x, y, ROOF_Z - 6.5, P["tasca_dado_m3_altezza"])]
            start = y if y < D / 2 else y - 8
            cuts.append(box(x - 3.5, start, ROOF_Z - 6.5, 7, 8, P["tasca_dado_m3_altezza"]))
    # Presa inferiore supplementare: ponti di soli 6 mm nelle pareti laterali.
    for x in (-1, W - 4):
        for y in (25, 43, 61, 79, 97):
            if y+6<=D-6:
                cuts.append(rounded_box(x, y, 8, 5, 6, 17, 1))
    result=result.cut(*cuts)
    result=result.fuse(*[s for i in range(3) for s in floor_anchors(i*P["passo_slot"])]).clean()
    # Piazzole piene sotto i piedini posteriori: nessuna presa coperta dal silicone.
    result=result.fuse(*[box(x,D-15,0,10,10,B)for x in (5,W-15)]).clean()
    print("SCOCCA: tagli",result.isValid(),len(result.Solids()),
          [s.Volume() for s in result.Solids()],flush=True)
    return result


def lid():
    result = rounded_box(0, 0, ROOF_Z, W, D, P["tetto"], 3)
    cuts = []
    for x, width in [(4.5, 8), (28.5, 9), (52.5, 9), (76.5, 9)]:
        for y0, y1 in [(18, 40), (43, 64), (67, 88), (91, 104)]:
            if y0>=91 and (x<14 or x>75):
                continue  # piazzole dei due fissaggi posteriori del coperchio
            y1=min(y1,D-4)
            cuts.append(rounded_box(x, y0, ROOF_Z - 1, width, y1 - y0, 5, 1))
    for x in (6, W - 6):
        for y in (8, D - 8):
            cuts.append(cylinder(x, y, ROOF_Z - 1, P["foro_m3"] / 2, 5))
            cuts.append(cq.Solid.makeCone(1.7, 3.3, 1.6,
                        cq.Vector(x, y, ROOF_Z + 1.4), cq.Vector(0, 0, 1)))
    return result.cut(*cuts).clean()


def coupon():
    raw = union([box(9, 0, 0, 31, 106, B)] + fixed_features())
    holes = [box(28.5, y0, -1, 9, y1 - y0, 5) for y0, y1 in [(28, 66), (77, 101)]]
    return raw.cut(*(holes + jaw_nut_holes())).fuse(*floor_anchors()).clean()


def drive(model, slot):
    dims = P["ssd_nominali"][model]
    x = P["prima_faccia_ssd_x"] + slot * P["passo_slot"]
    # Gabarit conservativo: i raccordi reali non sono necessari ai giochi.
    return box(x, P["inizio_ssd_y"], SSD_Z,
               dims["spessore"], dims["lunghezza"], dims["altezza"])


def pads(model, slot):
    dims = P["ssd_nominali"][model]
    x = P["prima_faccia_ssd_x"] + slot * P["passo_slot"]
    jaw_x = x + dims["spessore"] + P["gioco_laterale_nominale_totale"] + 1
    result = []
    for k, y in enumerate(P["appoggi_y"], 1):
        result += [(f"tampone_fisso_{slot+1}_{k}", box(x - 1, y - 3, SSD_Z, 1, 6, 10)),
                   (f"tampone_mobile_{slot+1}_{k}", box(jaw_x - 1, y - 3, SSD_Z, 1, 6, 10)),
                   (f"appoggio_morbido_{slot+1}_{k}", box(x, y - 4, SSD_Z - 1, 8, 8, 1))]
    result.append((f"battuta_morbida_{slot+1}", box(x, 15, SSD_Z, 8, 1, 6)))
    return result


def cable_path(model, slot, n=101):
    d = P["ssd_nominali"][model]
    x0 = P["prima_faccia_ssd_x"] + slot * P["passo_slot"] + d["spessore"] / 2
    y0 = P["inizio_ssd_y"] + d["lunghezza"] + P["cavi"]["tratto_rigido_massimo_dichiarato_utente"]
    z0 = SSD_Z + d["altezza"] / 2
    # Solo tratto illustrativo esterno, senza guidare o raccogliere i cavi.
    return np.c_[np.full(n,x0),np.linspace(y0,y0+45,n),np.full(n,z0)]


def tube(points, radius=2.5):
    edge = cq.Edge.makeSpline([cq.Vector(*p) for p in points])
    path = cq.Wire.assembleEdges([edge])
    p0 = points[0]
    return (cq.Workplane(cq.Plane(origin=cq.Vector(*p0), normal=cq.Vector(0, 1, 0)))
            .circle(radius).sweep(cq.Workplane(obj=path), isFrenet=False).val())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mesh_of(shape):
    verts, faces = shape.tessellate(.06, .12)
    return trimesh.Trimesh(np.array([v.toTuple() for v in verts]), np.array(faces), process=True)


def bounds(shape):
    b = shape.BoundingBox()
    return [[b.xmin, b.ymin, b.zmin], [b.xmax, b.ymax, b.zmax]]


def main():
    for dirname in ("stampa/STL", "stampa/piatti_geometrici", "CAD",
                    "anteprime", "verifiche/mesh_assieme"):
        (ROOT / dirname).mkdir(parents=True, exist_ok=True)
    parts = [
        ("scocca_ventilata_R02", shell(), 1, False, "assieme", "#41474e"),
        ("sponda_regolabile_R02", moving_jaw(), 3, False, "assieme", "#d28b3e"),
        ("coperchio_ventilato_R02", lid(), 1, True, "assieme", "#41474e"),
        ("provino_sede_R02", coupon(), 1, False, "provino", "#64747d")
    ]
    records = []
    for name, shape, qty, flip, role, color in parts:
        assert shape.isValid() and len(shape.Solids()) == 1, (name,shape.isValid(),len(shape.Solids()))
        print("ESPORTO", name, flush=True)
        cq.exporters.export(shape, str(ROOT / "CAD" / (name + ".step")))
        printed = shape.rotate((0, 0, 0), (1, 0, 0), 180) if flip else shape
        bb = printed.BoundingBox()
        printed = printed.translate((-bb.xmin, -bb.ymin, -bb.zmin))
        path = ROOT / "stampa/STL" / (name + ".stl")
        cq.exporters.export(printed, str(path), tolerance=.06, angularTolerance=.12)
        cq.exporters.export(printed, str(ROOT / "CAD" / (name + "_orientato_stampa.step")))
        m = mesh_of(shape)
        assembly_path = ROOT / "verifiche/mesh_assieme" / (name + ".ply")
        m.export(assembly_path)
        records.append(dict(name=name, quantity=qty, role=role, color=color,
                            stl=str(path.relative_to(ROOT)), stl_sha256=sha(path),
                            step="CAD/" + name + ".step", bounds_mm=bounds(shape),
                            volume_mm3=shape.Volume(), print_flip_x_180=flip,
                            print_bounds_mm=bounds(printed),
                            assembly_mesh=str(assembly_path.relative_to(ROOT)),
                            assembly_mesh_sha256=sha(assembly_path)))
    display = []
    assembly = cq.Assembly(name="BAY_SSD_R02_GABARIT_NOMINALI")
    def add(name, shape, color, kind):
        assert shape.isValid(), name
        file = ROOT / "verifiche/mesh_assieme" / (name + ".ply")
        mesh_of(shape).export(file)
        display.append(dict(name=name, mesh=str(file.relative_to(ROOT)), color=color,
                            kind=kind, bounds_mm=bounds(shape)))
        assembly.add(shape, name=name, color=cq.Color(color))
    add(parts[0][0], parts[0][1], parts[0][5], "struttura")
    add(parts[2][0], parts[2][1], parts[2][5], "coperchio")
    models = ["T7", "T7_Shield", "T9"]
    colors = ["#719cb4", "#394b58", "#242c32"]
    for slot, (model, color) in enumerate(zip(models, colors)):
        ap = P["ssd_nominali"][model]["spessore"] + P["gioco_laterale_nominale_totale"]
        add(f"sponda_slot_{slot+1}", moving_jaw(ap, slot * P["passo_slot"]), "#d28b3e", "sponda")
        add(f"SSD_{model}_GABARIT", drive(model, slot), color, "gabarit_ssd")
        for name, shape in pads(model, slot):
            add(name, shape, "#b3b8b5", "silicone_commerciale")
        d = P["ssd_nominali"][model]
        x = P["prima_faccia_ssd_x"] + slot * P["passo_slot"] + d["spessore"] / 2
        y = P["inizio_ssd_y"] + d["lunghezza"]
        z = SSD_Z + d["altezza"] / 2
        cx=P["cavi"]["connettore_gabarit_x"];cz=P["cavi"]["connettore_gabarit_z"]
        add(f"spinotto_{slot+1}_GABARIT", box(x - cx/2, y, z - cz/2, cx,
            P["cavi"]["tratto_rigido_massimo_dichiarato_utente"], cz),
            "#25292e", "gabarit_connettore_non_rilevato")
        add(f"cavo_{slot+1}_GABARIT", cylinder(x,y+P["cavi"]["tratto_rigido_massimo_dichiarato_utente"],
            z,P["cavi"]["diametro_dichiarato_utente"]/2,45,(0,1,0)),
            "#202327", "gabarit_cavo")
    for i, (x, y) in enumerate([(5, 5), (W-15, 5), (5, D-15), (W-15, D-15)], 1):
        add(f"piedino_silicone_{i}", box(x, y, -5, 10, 10, 5), "#24282a", "silicone_commerciale")
    joints = []
    for i in range(3):
        x, y, z = 27 + i * P["passo_slot"], 8, B + 4
        joints.append(dict(name=f"regolazione_{i+1}", xy_mm=[x,y], top_mm=z,
                           length_mm=10, screw="M3x10 testa cilindrica", washer=True,
                           nut_bottom_mm=.2, nut_window="dal fondo"))
    for x in (6, W-6):
        for y in (8, D-8):
            joints.append(dict(name=f"coperchio_{x}_{y}", xy_mm=[x,y], top_mm=ROOF_Z+3,
                               length_mm=12, screw="M3x12 testa svasata DIN 7991", washer=False,
                               nut_bottom_mm=ROOF_Z-6.5, nut_window="verso interno"))
    for j in joints:
        x,y = j["xy_mm"]; top=j["top_mm"]
        if j["washer"]:
            washer = cylinder(x,y,top,3.5,.5).cut(cylinder(x,y,top-.1,1.7,.7))
            add("rondella_"+j["name"],washer,"#a5adb4","ferramenta_commerciale")
            fastener=union([cylinder(x,y,top+.5-j["length_mm"],1.5,j["length_mm"]),
                            cylinder(x,y,top+.5,2.75,3)])
        else:
            fastener=union([cylinder(x,y,top-j["length_mm"],1.5,j["length_mm"]-1.6),
                            cq.Solid.makeCone(1.5,3,1.5,cq.Vector(x,y,top-1.6),cq.Vector(0,0,1))])
        add("vite_"+j["name"],fastener,"#a5adb4","ferramenta_commerciale")
    save(ROOT/"verifiche/ferramenta.json",dict(joints=joints,
         main_bom={"M3x10_cilindrica":3,"M3x12_svasata_DIN7991":4,
                   "dado_M3_standard_chiave_5p5_altezza_2p4":7,"rondella_M3_OD7":3},
         extra_coupon_bom={"M3x10_cilindrica":1,"dado_M3":1,"rondella_M3_OD7":1},
         note="Le viti nel STEP sono gabarit lisci senza filetto; dadi standard commerciali."))
    assembly.save(str(ROOT / "CAD/BAY_SSD_R02_ASSIEME_CON_GABARIT.step"))
    save(ROOT / "verifiche/manifest.json", dict(
        revision="R02", unit="millimeter", parameters_sha256=sha(ROOT/"sorgenti/parametri.json"),
        parts=records, display=display, assembly_models=models,
        external_dimensions_mm=[W, D, ROOF_Z + P["tetto"] + P["piedini_silicone"]],
        unmeasured=["SSD reali", "sezione e posizione esatte delle porte USB",
                    "larghezza/altezza degli spinotti"],
        rear_open=True,cable_compartment=False,cable_clamp=False,
        ssd_rear_projection_mm={name:P["inizio_ssd_y"]+d["lunghezza"]-D
                               for name,d in P["ssd_nominali"].items()},
        measured_by_user_approximately=dict(stiff_cable_length_mm=50, cable_diameter_mm=5),
        physical_print=False, thermal_test=False))
    deps = ["cadquery", "cadquery-ocp", "trimesh", "vtk", "Pillow", "numpy", "scipy", "shapely", "manifold3d", "rtree", "networkx", "lxml"]
    (ROOT / "sorgenti/requirements.txt").write_text(
        "\n".join(f"{n}=={importlib.metadata.version(n)}" for n in deps) + "\n")
    print("CAD E STL COMPLETATI", flush=True)


if __name__ == "__main__":
    main()
