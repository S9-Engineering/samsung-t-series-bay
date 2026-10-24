"""Studio estetico da CAD R03: raccordi, palette, sole sedi per piedini adesivi."""
from pathlib import Path
import json
import hashlib
import importlib.metadata
import cadquery as cq
import numpy as np
import trimesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/"sorgenti/parametri_estetici.json").read_text())
BG="#f2f4f6";INK="#26343e";MUTED="#65737c"
FONT="/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD="/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,size)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def rounded_outline(z,height):
    return (cq.Workplane("XY").box(90,101,height,centered=False)
            .edges("|Z").fillet(P["raccordo_verticale_esterno"]).val().translate((0,0,z)))


def outer_edges(solid,z):
    selected=[]
    for edge in solid.Edges():
        b=edge.BoundingBox()
        if abs(b.zmin-z)>1e-5 or abs(b.zmax-z)>1e-5:continue
        if min(abs(b.xmin),abs(b.xmax-90),abs(b.ymin),abs(b.ymax-101))<1e-5:
            selected.append(edge)
    assert selected
    return selected


def fillet_outer(solid,z,radius):
    return solid.Solids()[0].fillet(radius,outer_edges(solid,z)).clean().Solids()[0]


def mesh_of(shape):
    verts,faces=shape.tessellate(.035,.07)
    return trimesh.Trimesh(np.array([v.toTuple() for v in verts]),np.array(faces),process=True)


def build():
    source=ROOT/"sorgenti/riferimento_r03"
    shell=cq.importers.importStep(str(source/"scocca_ventilata_R03.step")).val()
    lid=cq.importers.importStep(str(source/"coperchio_ventilato_R03.step")).val()
    shell=shell.intersect(rounded_outline(0,83)).clean()
    shell=fillet_outer(shell,0,P["raccordo_bordo_inferiore_scocca"])
    seats=P["sedi_piedini"]
    lands=[cq.Solid.makeCylinder(seats["piazzola_piena_diametro"]/2,5,cq.Vector(x,y,0))
           for x,y in seats["centri_xy"]]
    shell=shell.fuse(*lands).clean()
    cuts=[cq.Solid.makeCylinder(seats["diametro_indicativo"]/2,seats["profondita_indicativa"]+.1,cq.Vector(x,y,-.1))
          for x,y in seats["centri_xy"]]
    shell=shell.cut(*cuts).clean()
    lid=lid.intersect(rounded_outline(83,3)).clean()
    lid=fillet_outer(lid,86,P["raccordo_bordo_superiore_tetto"])
    lid=fillet_outer(lid,83,P["raccordo_bordo_inferiore_tetto"])
    checks=[]
    for name,shape in (("scocca_estetica_R04",shell),("tetto_estetico_R04",lid)):
        assert shape.isValid() and len(shape.Solids())==1
        step=ROOT/"CAD_studio"/(name+".step")
        cq.exporters.export(shape,str(step))
        reopened=cq.importers.importStep(str(step)).val()
        assert reopened.isValid() and len(reopened.Solids())==1
        mesh=mesh_of(reopened)
        dst=ROOT/"verifiche"/(name+".ply");mesh.export(dst)
        mesh=trimesh.load_mesh(dst,process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
        assert len(mesh.split())==1
        assert not np.any(mesh.area_faces<1e-10)
        assert len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
        checks.append(dict(name=name,step=str(step.relative_to(ROOT)),step_sha256=sha(step),
            mesh=str(dst.relative_to(ROOT)),mesh_sha256=sha(dst),step_valid=True,solids=1,
            mesh_closed=True,consistent_normals=True,volume_mm3=float(mesh.volume),
            bounds_mm=mesh.bounds.tolist(),degenerate_faces=0,duplicate_faces=0))
    report=dict(revision=P["revisione"],scope="STUDIO_ESTETICO",checks=checks,
        feet_seats=seats,parameters_sha256=sha(ROOT/"sorgenti/parametri_estetici.json"),
        slicing=False,structural_validation=False,thermal_validation=False,
        self_intersection_screening=False,physical_fit=False,
        print_ready=False,reference_print_revision="R03")
    (ROOT/"verifiche/stato_studio.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    return [dict(name=r["name"],kind=k,mesh=r["mesh"]) for r,k in zip(checks,("struttura","coperchio"))]


def actor(mesh,color,metal=False):
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(np.ascontiguousarray(mesh.vertices),deep=True))
    data=vtk.vtkPolyData();data.SetPoints(points);cells=vtk.vtkCellArray()
    for triangle in mesh.faces:
        cells.InsertNextCell(3)
        for i in triangle:cells.InsertCellPoint(int(i))
    data.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(data)
    normals.SetFeatureAngle(28);normals.SplittingOn();normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    item=vtk.vtkActor();item.SetMapper(mapper)
    prop=item.GetProperty()
    prop.SetColor(*[int(color[i:i+2],16)/255 for i in (1,3,5)])
    prop.SetInterpolationToFlat();prop.SetAmbient(.32);prop.SetDiffuse(.7)
    prop.SetSpecular(.15 if not metal else .3);prop.SetSpecularPower(34)
    return item


def render(rows,palette,view,output):
    renderer=vtk.vtkRenderer();renderer.SetBackground(242/255,244/255,246/255)
    for row,mesh in rows:
        kind=row["kind"]
        color=palette["tetto"] if kind=="coperchio" else palette["scocca"]
        if kind in ("gabarit_ssd","silicone_commerciale","ferramenta_commerciale"):color=row["color"]
        renderer.AddActor(actor(mesh,color,kind=="ferramenta_commerciale"))
    camera=renderer.GetActiveCamera()
    target=view.get("target",(45,50.5,41))
    camera.SetFocalPoint(*target);camera.SetPosition(*view["camera"])
    camera.SetViewUp(*view.get("up",(0,0,1)));camera.ParallelProjectionOn()
    camera.SetParallelScale(view.get("scale",82))
    for pos,power in [((-170,-240,320),.75),((260,80,240),.45),((40,330,280),.3),
                       (view["camera"],.32)]:
        light=vtk.vtkLight();light.SetPosition(*pos);light.SetFocalPoint(*target)
        light.SetIntensity(power);renderer.AddLight(light)
    if view["camera"][2]<0:
        light=vtk.vtkLight();light.SetPosition(-90,-100,-220);light.SetFocalPoint(*target)
        light.SetIntensity(.75);renderer.AddLight(light)
    # Occlusione ambientale per leggere bordi, fuga del tetto e tasche poco profonde.
    passes=vtk.vtkRenderStepsPass();ao=vtk.vtkSSAOPass();ao.SetDelegatePass(passes)
    ao.SetRadius(3);ao.SetBias(.03);ao.SetKernelSize(96)
    renderer.SetPass(ao);renderer.UseFXAAOn()
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1080,850)
    window.SetMultiSamples(0);window.AddRenderer(renderer);renderer.ResetCameraClippingRange()
    window.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window)
    capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()
    return Image.open(output).convert("RGB")


def main():
    modified=build()
    reference=json.loads((ROOT/"sorgenti/riferimento_r03/elementi_assieme.json").read_text())
    rows=[(r,trimesh.load_mesh(ROOT/r["mesh"],process=False)) for r in modified+reference]
    palettes=P["palette"]
    view=dict(camera=(-190,-230,220),scale=82)
    board=Image.new("RGB",(2280,2050),BG);draw=ImageDraw.Draw(board)
    draw.text((60,35),"R04 / studio estetico",font=font(46,True),fill=INK)
    draw.text((62,105),"Bordi più morbidi · quattro abbinamenti · scocca e tetto separati",font=font(26),fill=MUTED)
    for i,palette in enumerate(palettes):
        x=(i%2)*1140;y=180+(i//2)*900
        draw.text((x+60,y),palette["id"]+"  "+palette["nome"],font=font(31,True),fill=INK)
        for k,key in enumerate(("scocca","tetto")):
            draw.rounded_rectangle((x+885+k*65,y+3,x+933+k*65,y+31),radius=5,
                                   fill=palette[key],outline="#b4bdc2",width=1)
        path=ROOT/"anteprime"/("_colore_"+palette["id"]+".png")
        raw=render(rows,palette,view,path)
        board.paste(raw,(x+30,y+55));path.unlink()
    draw.text((60,1990),"Viste del CAD di studio · colori indicativi · SSD schematizzati · piedini commerciali non montati · nessuno slicing R04",font=font(22),fill=MUTED)
    board.save(ROOT/"anteprime/01_R04_PALETTE.png")
    # Variante richiesta da due angolazioni, su scala comune.
    hero=Image.new("RGB",(2280,1120),BG);d=ImageDraw.Draw(hero)
    d.text((60,35),"Bianco / rosso",font=font(48,True),fill=INK)
    d.text((62,108),"Raccordi contenuti e tetto a contrasto",font=font(27),fill=MUTED)
    for i,camera in enumerate(((-190,-230,220),(245,310,230))):
        path=ROOT/"anteprime"/f"_hero_{i}.png"
        raw=render(rows,palettes[0],dict(camera=camera,scale=82),path)
        hero.paste(raw,(30+1140*i,175));path.unlink()
    d.text((60,1065),"Studio estetico R04 · scocca bianca, tetto rosso · interni della R03 come riferimento · nessun piedino stampato",font=font(23),fill=MUTED)
    hero.save(ROOT/"anteprime/02_R04_BIANCO_ROSSO.png")
    # Dettaglio vero dei raccordi e del fondo: soltanto scocca e tetto.
    detail=Image.new("RGB",(2280,1260),BG);d=ImageDraw.Draw(detail)
    d.text((60,35),"Raccordi e sedi per i piedini",font=font(44,True),fill=INK)
    d.text((62,103),"Spigoli alleggeriti, senza cambiare il carattere compatto del bay",font=font(26),fill=MUTED)
    for i,(title,v) in enumerate((
        ("Angolo anteriore / dettaglio",dict(camera=(-95,-140,155),target=(9,9,77),scale=21)),
        ("Fondo / quattro tasche",dict(camera=(215,-205,-245),target=(45,50.5,20),scale=84)))):
        x=1140*i
        d.text((x+60,190),title,font=font(29,True),fill=INK)
        path=ROOT/"anteprime"/f"_dettaglio_{i}.png"
        raw=render([(r,m) for r,m in rows if r["kind"] in ("struttura","coperchio","ferramenta_commerciale")],
                   palettes[0],v,path)
        detail.paste(raw,(x+30,240));path.unlink()
    d.text((60,1115),"Angoli verticali R4,5 mm · bordi esterni R0,8 mm",font=font(25),fill=INK)
    d.text((1200,1115),"4 sedi Ø10,5 × 0,65 mm, quote indicative",font=font(25),fill=INK)
    d.text((60,1180),"Gommini trasparenti adesivi da aggiungere separatamente. Dimensioni delle sedi da adattare al piedino scelto.",font=font(24),fill=MUTED)
    detail.save(ROOT/"anteprime/03_R04_DETTAGLI.png")
    outputs=[str(p.relative_to(ROOT)) for p in sorted((ROOT/"anteprime").glob("*.png"))]
    report=json.loads((ROOT/"verifiche/stato_studio.json").read_text())
    report["previews"]={p:sha(ROOT/p) for p in outputs}
    report["dependencies"]={name:importlib.metadata.version(name) for name in ("cadquery","trimesh","vtk","Pillow","numpy")}
    (ROOT/"verifiche/stato_studio.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(dict(state=report["scope"],previews=outputs,seats=4,print_ready=False)),flush=True)


if __name__=="__main__":main()
