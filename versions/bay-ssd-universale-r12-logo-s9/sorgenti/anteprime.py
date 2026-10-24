"""Viste R12 del CAD esportato: nessuna vite o gomma interna."""
import json
import cadquery as cq
import trimesh
import numpy as np
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
ROOT=g.ROOT
PALETTE=dict(scocca=g.P["colori"]["scocca"],tetto=g.P["colori"]["coperchio"])


def image_view(rows,view,key):
    path=ROOT/"anteprime"/("_"+key+".png")
    out=render(rows,PALETTE,view,path);path.unlink()
    return out


def two_views(rows,title,subtitle,name,views,footer):
    im=Image.new("RGB",(2280,1190),BG);d=ImageDraw.Draw(im)
    d.text((60,35),title,font=font(45,True),fill=INK)
    d.text((62,105),subtitle,font=font(25),fill=MUTED)
    for i,(label,view,custom) in enumerate(views):
        x=i*1140;d.text((x+60,185),label,font=font(27,True),fill=INK)
        im.paste(image_view(custom if custom is not None else rows,view,name+str(i)),(x+30,230))
    d.text((60,1125),footer,font=font(23),fill=MUTED)
    im.save(ROOT/"anteprime"/name)


def plate_plan():
    p=ROOT/"verifiche/piatti.json"
    if not p.exists():return
    plates=json.loads(p.read_text())["plates"]
    im=Image.new("RGB",(2220,960),BG);d=ImageDraw.Draw(im)
    d.text((50,30),"R12 / disposizione dei piatti",font=font(42,True),fill=INK)
    titles=["00 / Provini","01 / Scocca e inserti","02 / Coperchio"]
    for k,(plate,title) in enumerate(zip(plates,titles)):
        ox=50+k*735;oy=165;s=2.4
        d.text((ox,105),title,font=font(26,True),fill=INK)
        d.rectangle((ox,oy,ox+256*s,oy+256*s),fill="white",outline="#a3adb5",width=2)
        for j,item in enumerate(plate["items"]):
            b=item["bounds_mm"]
            color="#30363c"
            d.rounded_rectangle((ox+b[0][0]*s,oy+(256-b[1][1])*s,ox+b[1][0]*s,oy+(256-b[0][1])*s),radius=3,fill=color)
        count=len(plate["items"])
        d.text((ox,815),f"{count} {'pezzo' if count==1 else 'pezzi'} · PETG PRO",font=font(24),fill=INK)
    d.text((50,905),"Sagome d’ingombro dei 3MF. Brim da 5 mm verificato; nessun cambio materiale o torre di spurgo.",font=font(24),fill=MUTED)
    im.save(ROOT/"anteprime/04_R12_PIATTI.png")


def main():
    man=json.loads((ROOT/"verifiche/manifest.json").read_text())
    rows=[(r,trimesh.load_mesh(ROOT/r["mesh"],process=False)) for r in man["display"]]
    two_views(rows,"R12 / monolite, senza viti","Tre sedi uguali · adattatori rimovibili · coperchio a due agganci","01_R12_CHIUSO.png",[
        ("Davanti",dict(camera=(-190,-230,220),scale=82),None),
        ("Retro aperto",dict(camera=(245,310,230),scale=82),None)],
        "CAD nominale · grafite indicativo · SSD schematizzati · solo quattro gommini commerciali esterni da aggiungere")
    two_views(rows,"R12 / MONOLITE","Grafite uniforme · fronte pieno · spigoli netti","05_R12_MONOLITE.png",[
        ("Davanti",dict(camera=(45,-300,43),target=(45,50.5,43),scale=66),None),
        ("Tre quarti",dict(camera=(-190,-230,190),target=(45,50.5,43),scale=84),None)],
        "Esterno approvato · interno R05 a incastro · render dai file esportati · colore indicativo")
    image_view(rows,dict(camera=(45,50.5,350),target=(45,50.5,43),up=(0,1,0),scale=66),"alto").save(ROOT/"anteprime/06_R12_ALTO.png")
    empty_shell=[(r,m) for r,m in rows if r["kind"] in ("struttura","coperchio")]
    two_views(empty_shell,"R12 / S9 IN RILIEVO","Logo senza sottotitolo · fronte in basso a destra · stesso colore della scocca","08_R12_LOGO_FRONTALE.png",[
        ("Fronte completo",dict(camera=(45,-300,43),target=(45,0,43),scale=56),None),
        ("Dettaglio del rilievo",dict(camera=(104,-100,29),target=(79,0,9.4),scale=10.5),None)],
        "S9 largo 14 mm · rilievo 0,4 mm · margine destro 4 mm e inferiore 6 mm · render del CAD, finitura fisica da verificare")
    side=cq.importers.importStep(str(ROOT/"CAD/scocca_R12.step")).val()
    side=side.intersect(g.box(-.1,-1,-1,3.101,103,88)).clean()
    side_rows=[(dict(kind="struttura"),g.mesh_of(side))]
    two_views(empty_shell,"R12 / SPIGOLI NETTI","Spigoli esterni a 90° · feritoie orizzontali · interno a incastro conservato","07_R12_PATTERN_LATERALE.png",[
        ("Tre quarti",dict(camera=(-190,-230,190),target=(45,50.5,43),scale=84),None),
        ("Dettaglio del fianco",dict(camera=(-300,50.5,43),target=(1.5,50.5,43),scale=65),side_rows)],
        "Scocca vuota · a destra parete isolata virtualmente · pattern su entrambi i fianchi · interno R05 conservato")
    opened=[]
    cut_shell=cq.importers.importStep(str(ROOT/"CAD/scocca_R12.step")).val()
    cut_shell=cut_shell.cut(g.box(-1,-1,5.01,5.3,103,84),g.box(-1,-1,5.01,92,5.3,84)).clean()
    for r,m in rows:
        if r["kind"]=="coperchio":continue
        if r["kind"]=="struttura":
            m=g.mesh_of(cut_shell)
        if r["kind"]=="inserto":
            r={**r,"color_override":"#548caa" if "_T7_Shield_" in r["name"] else "#d89443"}
        if r["kind"]=="gabarit_ssd":r={**r,"opacity":.38}
        opened.append((r,m))
    empty=[(r,m) for r,m in opened if r["kind"] not in ("gabarit_ssd","inserto")]
    two_views(opened,"L’interno ridotto all’essenziale","Coperchio e due pareti rimossi virtualmente per mostrare gli appoggi","02_R12_INTERNO.png",[
        ("Sei appoggi integrati nella scocca",dict(camera=(-150,-190,235),scale=84),empty),
        ("T7 + Shield + T9",dict(camera=(-150,-190,235),scale=84),None)],
        "Arancione: inserti T7 · blu: inserti Shield · SSD semitrasparenti · nessuna vite, tampone o adesivo interno")
    # Una sezione locale di ciascun alloggiamento, con SSD trasparente.
    im=Image.new("RGB",(2700,1170),BG);d=ImageDraw.Draw(im)
    d.text((60,35),"Una sede, tre formati",font=font(45,True),fill=INK)
    d.text((62,105),"Gli inserti scattano sulla guida; il dispositivo resta appoggiato con gioco",font=font(26),fill=MUTED)
    for i,model in enumerate(("T9","T7","T7_Shield")):
        x=i*900
        text="T9 / diretto" if model=="T9" else ("T7 / inserto largo" if model=="T7" else "Shield / inserto sottile")
        d.text((x+50,185),text,font=font(31,True),fill=INK)
        local=[(dict(kind="struttura"),g.mesh_of(g.saddle(36)))]
        dssd=g.drive(model).intersect(g.box(10,32,0,25,8,100))
        local += [(dict(kind="gabarit_ssd",color="#455969",opacity=.23),g.mesh_of(dssd))]
        if model!="T9":
            local += [(dict(kind="inserto",color_override="#d89443" if model=="T7" else "#548caa"),g.mesh_of(g.adapter(model)))]
        path=ROOT/"anteprime"/("_sede"+str(i)+".png")
        raw=render(local,PALETTE,dict(camera=(-70,-70,105),target=(21,36,34),scale=47),path)
        im.paste(raw.resize((900,708)),(x,260));path.unlink()
        width=g.S["larghezze_adattate"][model]
        d.text((x+50,1005),f"Apertura {width:g} mm",font=font(26),fill=INK)
    d.text((60,1100),"Sezione locale del CAD · ingombri SSD trasparenti · due appoggi uguali per disco · elasticità degli scatti da provare sul provino",font=font(23),fill=MUTED)
    im.save(ROOT/"anteprime/03_R12_SEDI.png")
    plate_plan()
    outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/"anteprime").glob("*.png"))}
    g.save(ROOT/"verifiche/anteprime.json",dict(source_manifest_sha256=g.sha(ROOT/"verifiche/manifest.json"),outputs=outputs,
        cfd=False,physical_photo=False,notes="Render dai solidi esportati; colori degli inserti esplicativi, stampa con lo stesso PETG della scocca."))
    print("R12 ANTEPRIME PRONTE",flush=True)


if __name__=="__main__":main()
