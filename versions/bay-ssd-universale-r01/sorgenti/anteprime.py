"""Viste tecniche ottenute dalle mesh finali, non immagini generative."""
from pathlib import Path
import json
import math
import numpy as np
import trimesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk
from PIL import Image, ImageDraw, ImageFont
import genera as g

ROOT=g.ROOT
MAN=json.loads((ROOT/"verifiche/manifest.json").read_text())
FONT="/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD="/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size,bold=False):
    return ImageFont.truetype(BOLD if bold else FONT,size)


def actor(mesh,color,opacity=1):
    data=vtk.vtkPolyData();pts=vtk.vtkPoints()
    pts.SetData(numpy_to_vtk(np.ascontiguousarray(mesh.vertices),deep=True));data.SetPoints(pts)
    cells=vtk.vtkCellArray()
    for f in mesh.faces:
        cells.InsertNextCell(3)
        for i in f:cells.InsertCellPoint(int(i))
    data.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(data);normals.SetFeatureAngle(45);normals.SplittingOn();normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper)
    a.GetProperty().SetColor(*[int(color[i:i+2],16)/255 for i in (1,3,5)])
    a.GetProperty().SetOpacity(opacity);a.GetProperty().SetAmbient(.22);a.GetProperty().SetDiffuse(.75)
    a.GetProperty().SetSpecular(.2);a.GetProperty().SetSpecularPower(32)
    return a


def render(name,mode):
    renderer=vtk.vtkRenderer();renderer.SetBackground(.95,.96,.965)
    for row in MAN["display"]:
        if mode in ("interno","esploso") and row["kind"]=="coperchio":continue
        if mode in ("interno","esploso") and row["kind"]=="ferramenta_commerciale" and "coperchio_" in row["name"]:continue
        m=trimesh.load_mesh(ROOT/row["mesh"],process=False)
        if mode=="interno" and row["name"]=="scocca_ventilata_R01":
            c=m.triangles_center
            keep=~(((c[:,0]<3.2)|(c[:,1]<3.2))&(c[:,2]>g.B+.01))
            m=m.submesh([np.flatnonzero(keep)],append=True,repair=False)
        if mode=="esploso":
            if row["kind"]=="gabarit_ssd":m.apply_translation([0,0,65])
            if row["kind"] in ("silicone_commerciale",) and not row["name"].startswith("piedino"):
                continue
            if row["kind"] in ("gabarit_cavo","gabarit_connettore_non_rilevato"):continue
        renderer.AddActor(actor(m,row["color"]))
    camera=renderer.GetActiveCamera()
    target=(45,g.D/2,35)
    camera.SetFocalPoint(*target);camera.SetPosition(-190,-210,285)
    if mode=="retro":camera.SetPosition(230,g.D+260,205)
    camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();camera.SetParallelScale(155 if mode=="esploso" else 139)
    for pos,power in [((-100,-200,400),.8),((250,50,300),.55),((30,400,240),.4)]:
        light=vtk.vtkLight();light.SetPosition(*pos);light.SetFocalPoint(*target);light.SetIntensity(power);renderer.AddLight(light)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1250,1100)
    window.SetMultiSamples(8);window.AddRenderer(renderer);renderer.ResetCameraClippingRange();window.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
    out=ROOT/"anteprime"/("_"+name+".png")
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(out));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()
    return Image.open(out).convert("RGB")


def wrap(draw,text,xy,max_width,ft,fill="#41505a",leading=1.4):
    x,y=xy;line=""
    for word in text.split():
        nxt=(line+" "+word).strip()
        if draw.textlength(nxt,font=ft)>max_width and line:
            draw.text((x,y),line,font=ft,fill=fill);y+=int(ft.size*leading);line=word
        else:line=nxt
    if line:draw.text((x,y),line,font=ft,fill=fill);y+=int(ft.size*leading)
    return y


def panel(image,title,subtitle,bullets,file):
    canvas=Image.new("RGB",(1740,1230),"#f2f4f6")
    canvas.paste(image,(0,100))
    d=ImageDraw.Draw(canvas)
    d.text((60,35),title,font=font(36,True),fill="#24323d")
    d.text((62,82),subtitle,font=font(20),fill="#52616a")
    x,y=1290,170
    d.rounded_rectangle((1260,140,1705,1130),radius=18,fill="white")
    d.text((x,y),"BAY / R01",font=font(24,True),fill="#a46c26");y+=65
    for heading,text in bullets:
        d.text((x,y),heading,font=font(22,True),fill="#24323d");y+=36
        y=wrap(d,text,(x,y),370,font(20));y+=30
    d.text((60,1180),"Vista tecnica da CAD e mesh esportate. SSD, connettori e cavi sono gabarit; nessuna prova fisica.",font=font(18),fill="#63717a")
    canvas.save(ROOT/"anteprime"/file)


def top_plan():
    im=Image.new("RGB",(1420,1230),"#f2f4f6");d=ImageDraw.Draw(im)
    d.text((65,35),"Distribuzione interna / vista dall'alto",font=font(34,True),fill="#24323d")
    s=4.35;ox,oy=120,180
    def rect(x0,y0,x1,y1,fill,outline=None):
        d.rectangle((ox+x0*s,oy+y0*s,ox+x1*s,oy+y1*s),fill=fill,outline=outline,width=2)
    rect(0,0,90,g.D,"#dce1e4","#63717a")
    rect(3,3,87,g.D-3,"#f8f9fa")
    colors=["#719cb4","#394b58","#242c32"]
    for i,(model,color) in enumerate(zip(MAN["assembly_models"],colors)):
        q=g.P["ssd_nominali"][model];x=14+24*i
        rect(x,16,x+q["spessore"],16+q["lunghezza"],color)
        for yy in g.P["appoggi_y"]:
            rect(x-3,yy-3,x-1,yy+3,"#59626a")
            rect(x+q["spessore"]+1.2,yy-3,x+q["spessore"]+3.2,yy+3,"#d28b3e")
        d.text((ox+(x-1)*s,oy+113*s),str(i+1),font=font(26,True),fill="#41505a")
        pts=g.cable_path(model,i)
        qx=x+q["spessore"]/2;qy=16+q["lunghezza"]
        d.line([(ox+qx*s,oy+qy*s),(ox+qx*s,oy+(qy+50)*s)],fill="#5e6870",width=11)
        d.line([(ox+px*s,oy+py*s)for px,py,pz in pts],fill="#252b32",width=9)
    d.text((ox+65,oy-45),"FRONTE",font=font(22,True),fill="#41505a")
    x,y=650,190
    for heading,text in [
        ("Tre slot identici","Qualsiasi modello in qualsiasi posizione. La sponda si regola sullo spessore reale."),
        ("10 mm fra due T9","Distanza nominale fra le facce. Guide e appoggi occupano soltanto piccole zone."),
        ("Vano cavi","Riserva di 50 mm rettilinei prima della parte flessibile. Uscita comune e fermacavi apribile."),
        ("Scocca 90 x 216 x 91 mm","Altezza inclusi piedini in silicone da 5 mm. Tetto a 10 mm dal T9."),
        ("Prima il provino","Provare T7, Shield e T9 nella sede campione prima della scocca completa.")]:
        d.text((x,y),heading,font=font(26,True),fill="#24323d");y+=43
        y=wrap(d,text,(x,y),650,font(24));y+=38
    d.text((65,1180),"Schema quotato sui gabarit nominali; non rappresenta misure al calibro o una simulazione termica.",font=font(19),fill="#63717a")
    im.save(ROOT/"anteprime/04_DISTRIBUZIONE_INTERNA.png")


def plate_plan():
    p=ROOT/"verifiche/piatti.json"
    if not p.exists():return
    data=json.loads(p.read_text())
    im=Image.new("RGB",(1660,860),"#f2f4f6");d=ImageDraw.Draw(im)
    d.text((50,35),"Piatti di stampa / R01",font=font(34,True),fill="#24323d")
    labels=["00 / Provino prima di tutto","01 / Scocca, tre sponde, fermacavi","02 / Coperchio capovolto"]
    colors=["#64747d","#d28b3e","#59626a","#b7bec4","#7e8d96"]
    for k,(plate,label)in enumerate(zip(data["plates"],labels)):
        ox,oy=50+k*540,160;s=1.8
        d.text((ox,105),label,font=font(22,True),fill="#24323d")
        d.rectangle((ox,oy,ox+256*s,oy+256*s),fill="white",outline="#9eabb4",width=2)
        d.rectangle((ox+246*s,oy+236*s,ox+256*s,oy+256*s),fill="#e8bcb4")
        for j,item in enumerate(plate["items"]):
            b=item["bounds_mm"];lo,hi=b
            d.rounded_rectangle((ox+lo[0]*s,oy+(256-hi[1])*s,ox+hi[0]*s,oy+(256-lo[1])*s),
                                radius=3,fill=colors[j%len(colors)])
            d.text((ox+lo[0]*s+4,oy+(256-hi[1])*s+4),str(j+1),font=font(15,True),fill="white")
        y=oy+480
        for j,item in enumerate(plate["items"]):
            d.text((ox,y),f"{j+1}. {item['name'].replace('_',' ')}",font=font(18),fill="#41505a");y+=27
    d.text((50,820),"Sagome d'ingombro della geometria; brim 5 mm verificato separatamente. Percorsi reali nelle tavole di slicing.",font=font(19),fill="#63717a")
    im.save(ROOT/"anteprime/05_PIATTI_R01.png")


def main():
    panel(render("INTERNO","interno"),"Tre SSD, una sede universale","Vista con coperchio e pareti anteriore/sinistra rimossi virtualmente",[
        ("Regolazione integrata","Sponde arancioni scorrevoli; vite accessibile davanti a ciascun disco."),
        ("Contatti piccoli","Appoggi e tamponi in silicone sulle sole zone necessarie."),
        ("Passaggi verticali","Prese dal basso e uscite nel tetto, con 10 mm fra le facce dei T9."),
        ("Cavi posteriori","50 mm rigidi riservati prima della curva verso il fermacavi.")],"01_INTERNO_R01.png")
    panel(render("CHIUSO","chiuso"),"Scocca ventilata e accesso dall'alto","Aspetto del prototipo meccanico; finitura reale dipendente dalla stampa",[
        ("Ingombro","90 x 216 x 91 mm, piedini commerciali inclusi."),
        ("Coperchio rimovibile","Quattro viti M3 svasate e dadi accessibili dall'interno."),
        ("Materiale","ELEGOO PETG PRO; appoggi, piedini e rivestimenti in silicone separati."),
        ("Stato","Modello nominale da provare. Prestazioni termiche ancora da misurare.")],"02_ASSIEME_CHIUSO_R01.png")
    panel(render("RETRO","retro"),"Vano posteriore e uscita comune","Cavi e spine rappresentati da ingombri di progetto",[
        ("Accesso alle spine","Collegamento manuale con coperchio rimosso."),
        ("Fermacavi apribile","Tre canali rivestiti in silicone; due viti con battute rigide."),
        ("Nessuna matassa","I cavi proseguono fuori dal bay."),
        ("Da rilevare","Sagoma e posizione esatte degli spinotti, rigidita e raggio di piega reale.")],"03_RETRO_R01.png")
    top_plan()
    plate_plan()
    for p in (ROOT/"anteprime").glob("_*.png"):p.unlink()
    print("ANTEPRIME COMPLETATE",flush=True)


if __name__=="__main__":
    main()
