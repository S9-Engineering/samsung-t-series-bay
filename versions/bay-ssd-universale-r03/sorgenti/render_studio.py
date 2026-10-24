"""Render del CAD R03 vuoto/carico, piu schema qualitativo dei passaggi aria."""
import json
import math
from pathlib import Path
import numpy as np
import trimesh
import vtk
from PIL import Image, ImageDraw
from anteprime import ROOT, MAN, actor, font, wrap

BG="#f2f4f6";INK="#24323d";MUTED="#63717a"


def arrow(start,end,color):
    delta=np.array(end)-np.array(start);length=np.linalg.norm(delta)
    z=delta/length
    guide=np.array([0.,0.,1.]) if abs(z[2])<.9 else np.array([0.,1.,0.])
    y=np.cross(z,guide);y/=np.linalg.norm(y);x=np.cross(y,z)
    source=vtk.vtkArrowSource();source.SetTipLength(.17);source.SetTipRadius(.035)
    source.SetShaftRadius(.012);source.SetShaftResolution(20);source.SetTipResolution(24)
    matrix=vtk.vtkMatrix4x4()
    # vtkArrowSource e allineata a X.
    for i in range(3):
        for j,col in enumerate((z,y,x)):matrix.SetElement(i,j,col[i]*length)
        matrix.SetElement(i,3,start[i])
    transform=vtk.vtkTransform();transform.SetMatrix(matrix)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(source.GetOutputPort())
    item=vtk.vtkActor();item.SetMapper(mapper);item.SetUserTransform(transform)
    item.GetProperty().SetColor(*[int(color[i:i+2],16)/255 for i in (1,3,5)])
    return item


def render(rows,view,output,cutaway=False,arrows=False):
    renderer=vtk.vtkRenderer();renderer.SetBackground(242/255,244/255,246/255)
    for row,mesh in rows:
        m=mesh
        if cutaway and row["kind"]=="struttura":
            centers=m.triangles_center
            keep=~(((centers[:,0]<3.2)|(centers[:,1]<3.2))&(centers[:,2]>5.01))
            m=m.submesh([np.flatnonzero(keep)],append=True,repair=False)
        item=actor(m,row["color"])
        item.GetProperty().SetInterpolationToFlat();item.GetProperty().SetAmbient(.33)
        item.GetProperty().SetDiffuse(.66);item.GetProperty().SetSpecular(.1)
        renderer.AddActor(item)
    if arrows:
        # Frecce schematiche in tre corridoi liberi a Y=45.7 mm; nessuna CFD.
        for x in (8.5,35.5,59.5,83.5):
            renderer.AddActor(arrow((x,45.7,-11),(x,45.7,100),"#2e9db1"))
        renderer.AddActor(arrow((42,124,48),(42,105,48),"#9db8be"))
    camera=renderer.GetActiveCamera()
    target=(45,50.5,40.5)
    camera.SetFocalPoint(*target);camera.SetPosition(*view["camera"])
    camera.SetViewUp(*view.get("up",(0,0,1)));camera.ParallelProjectionOn()
    camera.SetParallelScale(view.get("scale",85))
    for pos,power in [((-160,-220,350),.85),((240,120,220),.6),((70,350,300),.4)]:
        light=vtk.vtkLight();light.SetPosition(*pos);light.SetFocalPoint(*target)
        light.SetIntensity(power);renderer.AddLight(light)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1)
    window.SetSize(1080,850);window.SetMultiSamples(8);window.AddRenderer(renderer)
    renderer.ResetCameraClippingRange();window.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window)
    capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(output));writer.SetInputConnection(capture.GetOutputPort())
    writer.Write();window.Finalize()
    return Image.open(output).convert("RGB")


def board(rows,loaded):
    views=[dict(title="Davanti / tre quarti",camera=(-190,-230,230)),
           dict(title="Retro aperto / tre quarti",camera=(245,310,235)),
           dict(title="Tetto / feritoie regolari",camera=(45,50.5,350),up=(0,1,0),scale=63),
           dict(title="Fondo / prese d’aria",camera=(45,50.5,-350),up=(0,-1,0),scale=63)]
    label="CON_SSD" if loaded else "SENZA_SSD"
    im=Image.new("RGB",(2280,2040),BG);d=ImageDraw.Draw(im)
    d.text((60,35),"R03 / "+("con tre SSD" if loaded else "senza dispositivi"),font=font(46,True),fill=INK)
    d.text((62,100),"90 × 101 × 91 mm · coperchio montato · raffreddamento passivo",font=font(25),fill=MUTED)
    outputs=[]
    for i,view in enumerate(views):
        p=ROOT/"anteprime"/f"_R03_{label}_{i}.png"
        raw=render(rows,view,p)
        x=(i%2)*1140;y=165+(i//2)*900
        d.text((x+60,y+10),view["title"],font=font(28,True),fill=INK)
        im.paste(raw,(x+30,y+50));p.unlink()
    footer="Render dalle mesh CAD esportate · SSD e viti schematizzati · cavi/spine nascosti · tinta indicativa PETG monocolore"
    d.text((60,1984),footer,font=font(21),fill=MUTED)
    path=ROOT/"anteprime"/(f"10_R03_{label}.png" if loaded else f"11_R03_{label}.png")
    im.save(path)
    return str(path.relative_to(ROOT))


def main():
    rows=[(r,trimesh.load_mesh(ROOT/r["mesh"],process=False)) for r in MAN["display"]
          if r["kind"] not in ("gabarit_cavo","gabarit_connettore_non_rilevato")]
    loaded=board(rows,True)
    empty=board([(r,m) for r,m in rows if r["kind"]!="gabarit_ssd"],False)
    # Schema aperto: coperchio rimosso virtualmente, pareti anteriori tagliate.
    opened=[(r,m) for r,m in rows if r["kind"]!="coperchio"
            and not (r["kind"]=="ferramenta_commerciale" and "coperchio_" in r["name"])]
    path=ROOT/"anteprime/_ARIA.png"
    view=dict(camera=(-155,-180,200),scale=92)
    raw=render(opened,view,path,cutaway=True,arrows=True)
    im=Image.new("RGB",(1780,1160),BG);d=ImageDraw.Draw(im)
    d.text((55,30),"R03 / percorso dell’aria",font=font(43,True),fill=INK)
    d.text((58,92),"Schema qualitativo dei passaggi · nessuna simulazione di flusso o temperatura",font=font(23),fill=MUTED)
    im.paste(raw,(0,180));path.unlink()
    air=json.loads((ROOT/"verifiche/valutazione_aria.json").read_text())
    x,y=1130,220
    paragraphs=[("Ingresso dal basso",f"Fondo: {air['current']['floor_net_vent_cm2']:.1f} cm² netti di aperture. Piedini da 5 mm e prese laterali basse."),
                ("Facce libere", "Tre SSD verticali, almeno 10 mm tra due T9. Appoggi piccoli; nessuna parete continua tra i dischi."),
                ("Uscita superiore",f"Tetto: {air['current']['roof_net_vent_cm2']:.1f} cm² netti. Otto coppie di feritoie arrotondate, con spina centrale di rinforzo."),
                ("Scambio anche dal retro","Il retro rimane aperto: l’aria può entrare e uscire anche lateralmente. Le frecce non impongono un flusso unico.")]
    for title,text in paragraphs:
        d.text((x,y),title,font=font(27,True),fill=INK);y+=43
        y=wrap(d,text,(x,y),590,font(24));y+=36
    d.text((58,1095),"Coperchio e due pareti rimossi virtualmente per mostrare l’interno. Frecce illustrative; nessuna portata prevista.",font=font(21),fill=MUTED)
    out=ROOT/"anteprime/12_R03_SCHEMA_ARIA.png";im.save(out)
    gabarit_notes="Dispositivi rappresentati dagli inviluppi nominali, viti senza filetto/impronta. Tinta unica indicativa. Geometria della scocca invariata rispetto agli STL della R03."
    evidence=dict(revision="R03",source_manifest_sha256=__import__("hashlib").sha256((ROOT/"verifiche/manifest.json").read_bytes()).hexdigest(),
                  outputs=[loaded,empty,str(out.relative_to(ROOT))],notes=gabarit_notes,
                  orthographic=True,cfd=False,physical_photo=False)
    (ROOT/"verifiche/render_studio.json").write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(evidence,ensure_ascii=False),flush=True)


if __name__=="__main__":main()
