"""R08: tre sedi passive, adattatori a clip e coperchio a due agganci."""
from pathlib import Path
import json,hashlib,importlib.metadata
import cadquery as cq
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/"sorgenti/parametri.json").read_text())
W,D,B=P["larghezza"],P["profondita"],P["base"]
Z=P["quota_seduta"];TOP=P["quota_tetto"];S=P["slot"]


def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cylinder(x,y,z,r,h):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
def union(shapes):return shapes[0].fuse(*shapes[1:]).clean() if len(shapes)>1 else shapes[0]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
def bounds(shape):
    b=shape.BoundingBox()
    return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]
def rounded(x,y,z,dx,dy,dz,r):
    return cq.Workplane("XY").box(dx,dy,dz,centered=False).edges("|Z").fillet(r).val().translate((x,y,z))
def mesh_of(shape):
    vs,fs=shape.tessellate(.045,.09)
    return trimesh.Trimesh(np.array([v.toTuple() for v in vs]),np.array(fs),process=True)
def outer_fillet(shape,z,r):
    edges=[]
    for e in shape.Edges():
        b=e.BoundingBox()
        if abs(b.zmin-z)<1e-5 and abs(b.zmax-z)<1e-5 and min(abs(b.xmin),abs(b.xmax-W),abs(b.ymin),abs(b.ymax-D))<1e-5:
            edges.append(e)
    return shape.Solids()[0].fillet(r,edges).clean()
def profile(points,y,width):
    wire=cq.Wire.makePolygon([cq.Vector(x,y,z) for x,z in points],close=True)
    return cq.Solid.extrudeLinear(wire,[],cq.Vector(0,width,0))
def left(slot=0):return S["primo_centro_x"]+slot*S["passo"]-S["larghezza_libera"]/2
def right(slot=0):return left(slot)+S["larghezza_libera"]


def saddle(y,slot=0):
    lo,hi=left(slot),right(slot);t=S["spessore_guide"];dy=S["larghezza_appoggio_y"]
    riser=box(lo-t,y-dy/2,0,S["larghezza_libera"]+2*t,dy,Z)
    fins=[]
    for x in (lo-t,hi):
        fin=box(x,y-dy/2,Z,t,dy,S["altezza_guide"])
        edges=[e for e in fin.Edges() if abs(e.BoundingBox().zmin-31)<1e-6 and abs(e.BoundingBox().zmax-31)<1e-6]
        fins.append(fin.fillet(.25,edges))
    shape=union([riser,*fins])
    # Piccola cava sull'esterno della guida destra: trattiene solo l'inserto.
    return shape.cut(box(hi+t-.35,y-dy/2-.1,21.4,.5,dy+.2,1.4)).clean()


def front_stop(slot=0):
    return box(left(slot),13.5,0,S["larghezza_libera"],2,20)


def adapter(model,y=36,slot=0):
    assert model in ("T7","T7_Shield")
    lo,hi=left(slot),right(slot);t=S["spessore_guide"]
    contact=lo+S["larghezze_adattate"][model]
    inside=hi-S["gioco_esterno_inserto"]
    outer=hi+t+S["gioco_esterno_inserto"]
    cap_z=Z+S["altezza_guide"]+S["gioco_sopra_guida"]
    dy=S["larghezza_appoggio_y"];yy=y-dy/2
    shapes=[box(contact,yy,Z+.2,inside-contact,dy,cap_z-Z-.2),
            box(contact,yy,cap_z,outer+S["parete_gancio_inserto"]-contact,dy,S["altezza_cap_inserto"]),
            box(outer,yy,20.8,S["parete_gancio_inserto"],dy,cap_z-20.8),
            profile([(outer,21.4),(outer-.5,22.0),(outer,22.6)],yy,dy)]
    return union(shapes)


def vent_holes(z,height):
    v=P["ventilazione"];length=(v["lunghezza_campo"]-v["spina"])/2
    offset=(length+v["spina"])/2
    return [cq.Workplane("XY").slot2D(length,v["larghezza"]).extrude(height).val().translate((45+dx,y,z))
            for y in v["centri_y"] for dx in (-offset,offset)]


def roof_holes(z,height):
    t=P["tetto_forato"];x0,y0=t["primo_centro"]
    return [cylinder(x0+i*t["passo"],y0+j*t["passo"],z,t["diametro_fori"]/2,height)
            for i in range(t["colonne"]) for j in range(t["righe"])]


def shell():
    outer=rounded(0,0,0,W,D,TOP,P["raggio_esterno"])
    outer=outer_fillet(outer,0,P["raccordo_bordi"])
    inner=rounded(3,3,B,W-6,D-6,TOP,1.2)
    shape=outer.cut(inner)
    cuts=vent_holes(-1,B+1.01)
    cuts += [box(3,D-4,B,W-6,6,TOP)]
    for x in (-.2,W-3.2):
        cuts.append(box(x,45.7,71,3.4,9.6,3))
    for x in (-1,W-4):
        for y in (25,43,61,79):
            cuts.append(rounded(x,y,8,5,6,17,1))
    shape=shape.cut(*cuts)
    shapes=[shape]
    for slot in range(3):
        shapes += [saddle(y,slot) for y in S["centri_y"]]
        shapes += [front_stop(slot)]
    for x,y in P["piedini"]["centri_xy"]:
        shapes.append(cylinder(x,y,0,P["piedini"]["piazzole_diametro"]/2,B))
    shape=union(shapes)
    holes=[cylinder(x,y,-.1,P["piedini"]["sedi_diametro"]/2,P["piedini"]["sedi_profondita"]+.1)
           for x,y in P["piedini"]["centri_xy"]]
    return shape.cut(*holes).clean()


def lid_latch(side):
    c=P["coperchio"];x=3+c["gioco_laterale"]
    finger=box(x,46.5,TOP-c["lunghezza_linguetta"],c["spessore_linguetta"],8,c["lunghezza_linguetta"])
    tooth=profile([(3.4,72.0),(2.4,73.0),(3.4,74.0)],46.5,8)
    result=union([finger,tooth])
    return result if side=="left" else result.mirror("YZ",(45,0,0))


def lid():
    shape=rounded(0,0,TOP,W,D,3,P["raggio_esterno"])
    shape=outer_fillet(shape,TOP+3,P["raccordo_tetto_superiore"])
    shape=outer_fillet(shape,TOP,P["raccordo_tetto_inferiore"])
    shape=shape.cut(*roof_holes(TOP-1,5)).clean()
    locators=[box(x,3.3,80,8,1.6,3) for x in (19,63)]
    return union([shape,lid_latch("left"),lid_latch("right"),*locators])


def drive(model,slot=0,dz=0):
    d=P["ssd_nominali"][model]
    width=S["larghezze_adattate"][model]
    x=left(slot)+(width-d["spessore"])/2
    return box(x,S["inizio_ssd_y"],Z+dz,d["spessore"],d["lunghezza"],d["altezza"])


def coupon_slot():
    raw=box(10.5,5,0,23,96,B).cut(*vent_holes(-1,B+1.01))
    rails=[box(x,5,0,2,96,B) for x in (10.5,31.5)]
    return union([raw,*rails,front_stop(),*[saddle(y) for y in S["centri_y"]]])


def coupon_latch_female():
    wall=box(0,45,68,3,11,15).cut(box(-.1,45.7,71,3.2,9.6,3))
    raw=union([wall,box(0,44,68,8,13,3)])
    return raw.translate((0,-44,-68))


def coupon_latch_male():
    return union([box(0,45,83,8,11,3),lid_latch("left")]).translate((0,-44,-68))


def parts():
    return [
        ("scocca_R08",shell(),1,False,"kit_corpo"),
        ("coperchio_R08",lid(),1,True,"kit_tetto"),
        ("inserto_T7_R08",adapter("T7"),2,True,"kit_corpo"),
        ("inserto_Shield_R08",adapter("T7_Shield"),2,True,"kit_corpo"),
        ("provino_sede_R08",coupon_slot(),1,False,"provino"),
        ("provino_chiusura_femmina_R08",coupon_latch_female(),1,False,"provino"),
        ("provino_chiusura_maschio_R08",coupon_latch_male(),1,True,"provino")]


def main():
    records=[];shapes={}
    for name,shape,qty,flip,role in parts():
        assert shape.isValid() and len(shape.Solids())==1,(name,shape.isValid(),len(shape.Solids()))
        shapes[name]=shape
        print("ESPORTO",name,flush=True)
        path=ROOT/"CAD"/(name+".step");cq.exporters.export(shape,str(path))
        printed=shape.rotate((0,0,0),(1,0,0),180) if flip else shape
        b=printed.BoundingBox();printed=printed.translate((-b.xmin,-b.ymin,-b.zmin))
        stl=ROOT/"stampa/STL"/(name+".stl")
        cq.exporters.export(printed,str(stl),tolerance=.045,angularTolerance=.09)
        cq.exporters.export(printed,str(ROOT/"CAD"/(name+"_orientato_stampa.step")))
        mesh=ROOT/"verifiche/mesh_assieme"/(name+".ply");mesh_of(shape).export(mesh)
        records.append(dict(name=name,quantity=qty,role=role,stl=str(stl.relative_to(ROOT)),
            stl_sha256=sha(stl),step=str(path.relative_to(ROOT)),bounds_mm=bounds(shape),
            print_bounds_mm=bounds(printed),volume_mm3=shape.Volume(),print_flip_x_180=flip,
            assembly_mesh=str(mesh.relative_to(ROOT)),assembly_mesh_sha256=sha(mesh)))
    display=[];assembly=cq.Assembly(name="BAY_R08_SENZA_VITI")
    def add(name,shape,color,kind):
        path=ROOT/"verifiche/mesh_assieme"/(name+".ply");mesh_of(shape).export(path)
        display.append(dict(name=name,mesh=str(path.relative_to(ROOT)),color=color,kind=kind,bounds_mm=bounds(shape)))
        assembly.add(shape,name=name,color=cq.Color(color))
    add("scocca_R08",shapes["scocca_R08"],P["colori"]["scocca"],"struttura")
    add("coperchio_R08",shapes["coperchio_R08"],P["colori"]["coperchio"],"coperchio")
    for slot,model in enumerate(("T7","T7_Shield","T9")):
        add("SSD_"+model,drive(model,slot),P["colori"][model],"gabarit_ssd")
        if model!="T9":
            for i,y in enumerate(S["centri_y"],1):
                add(f"inserto_{model}_{i}",adapter(model,y,slot),P["colori"]["scocca"],"inserto")
    assembly.save(str(ROOT/"CAD/BAY_R08_ASSIEME_GABARIT.step"))
    save(ROOT/"verifiche/manifest.json",dict(revision="R08",unit="millimeter",parameters_sha256=sha(ROOT/"sorgenti/parametri.json"),
        parts=records,display=display,assembly_models=["T7","T7_Shield","T9"],external_dimensions_mm=[90,101,86],
        kit_printed_parts=6,ssd_nominal=True,hardware_bom={},internal_adhesives=False,
        commercial_components=["4 piedini adesivi trasparenti; misure da scegliere"],physical_print=False,thermal_test=False))
    deps=["cadquery","cadquery-ocp","trimesh","vtk","Pillow","numpy","scipy","shapely","manifold3d","rtree","networkx","lxml"]
    (ROOT/"sorgenti/requirements.txt").write_text("\n".join(f"{n}=={importlib.metadata.version(n)}" for n in deps)+"\n")
    print("R08 CAD COMPLETATO",flush=True)


if __name__=="__main__":main()
