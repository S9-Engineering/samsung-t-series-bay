"""Viste R15 del CAD esportato: nessuna vite o gomma interna."""
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
    assert len(plates)==2 and len(plates[0]['items'])==5
    from verifica import section
    im=Image.new("RGB",(1100,1250),BG);d=ImageDraw.Draw(im)
    d.text((50,30),"R15 / ricambi su un piatto",font=font(42,True),fill=INK)
    d.text((50,100),"5 pezzi · PLA BASIC · stesso orientamento di stampa",font=font(25),fill=MUTED)
    ox,oy,s=100,170,3.5
    def xy(x,y):return (ox+x*s,oy+(256-y)*s)
    d.rectangle((ox,oy,ox+256*s,oy+256*s),fill='white',outline='#a3adb5',width=2)
    for n in range(0,257,32):
        x,y=xy(n,0);d.line((x,oy,x,oy+256*s),fill='#e5e9ed')
        x,y=xy(0,n);d.line((ox,y,ox+256*s,y),fill='#e5e9ed')
        if n%64==0:
            d.text((ox+n*s-12,oy+256*s+8),str(n),font=font(17),fill=MUTED)
            d.text((ox-45,oy+(256-n)*s-8),str(n),font=font(17),fill=MUTED)
    d.rectangle((*xy(246,20),*xy(256,0)),fill='#f6dadd',outline='#bb6a73')
    meshes={}
    for item in plates[0]['items']:
        name=item['part'];color='#354b60' if name=='scocca_R15' else ('#657581' if name=='coperchio_R15' else '#b17d43')
        b=item['bounds_mm'];a,c=xy(b[0][0]-5,b[1][1]+5),xy(b[1][0]+5,b[0][1]-5)
        d.rectangle((*a,*c),fill='#edf0f3',outline='#b8c4cf',width=2)
        if name not in meshes:meshes[name]=trimesh.load_mesh(ROOT/'stampa/STL'/(name+'.stl'),process=True)
        m=meshes[name].copy();m.apply_translation(-m.bounds[0]);m.apply_translation([*item['xy'],0])
        polygon=section(m,.1)
        for poly in (list(polygon.geoms) if hasattr(polygon,'geoms') else [polygon]):
            d.polygon([xy(x,y) for x,y in poly.exterior.coords],fill=color)
            for ring in poly.interiors:d.polygon([xy(x,y) for x,y in ring.coords],fill='white')
    for text,x,y in [('COPERCHIO',70,51),('2 × T7',37,211),('2 × SHIELD',157,211)]:
        a,b=xy(x,y);d.text((a,b),text,font=font(22,True),fill=INK)
    d.text((100,1120),"Scocca R14 riutilizzata · stampare solo questi 5 ricambi",font=font(26,True),fill=INK)
    d.text((100,1165),"Rettangoli chiari: margine brim 5 mm · rosso: zona esclusa",font=font(22),fill=MUTED)
    d.text((100,1200),"Sezioni inferiori dagli STL finali · piano utile 256 × 256 mm",font=font(22),fill=MUTED)
    im.save(ROOT/"anteprime/04_R15_PIATTI.png")


def save_manifest():
    outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/"anteprime").glob("*.png"))}
    g.save(ROOT/"verifiche/anteprime.json",dict(source_manifest_sha256=g.sha(ROOT/"verifiche/manifest.json"),outputs=outputs,
        cfd=False,physical_photo=False,notes="Render dai solidi esportati; colori degli inserti esplicativi, stampa con lo stesso PLA BASIC della scocca."))


def main():
    man=json.loads((ROOT/"verifiche/manifest.json").read_text())
    rows=[(r,trimesh.load_mesh(ROOT/r["mesh"],process=False)) for r in man["display"]]
    two_views(rows,"R15 / monolite, senza viti","Tre sedi uguali · adattatori rimovibili · coperchio a due agganci","01_R15_CHIUSO.png",[
        ("Davanti",dict(camera=(-190,-230,220),scale=82),None),
        ("Retro con coda",dict(camera=(245,310,180),scale=82),None)],
        "CAD nominale · grafite indicativo · SSD schematizzati · solo quattro gommini commerciali esterni da aggiungere")
    two_views(rows,"R15 / MONOLITE","Grafite uniforme · fronte pieno · spigoli netti","05_R15_MONOLITE.png",[
        ("Davanti",dict(camera=(45,-300,43),target=(45,50.5,43),scale=66),None),
        ("Tre quarti",dict(camera=(-190,-230,190),target=(45,50.5,43),scale=84),None)],
        "Esterno approvato · culle a U bilaterali · render dai file esportati · colore indicativo")
    image_view(rows,dict(camera=(45,50.5,350),target=(45,50.5,43),up=(0,1,0),scale=66),"alto").save(ROOT/"anteprime/06_R15_ALTO.png")
    empty_shell=[(r,m) for r,m in rows if r["kind"] in ("struttura","coperchio")]
    lid_only=[(r,m) for r,m in rows if r['kind']=='coperchio']
    two_views(rows,"R15 / LA CODA DEL TETTO","Retro solidale al tetto · accesso USB dal basso · alette con precarico","09_R15_CODA_POSTERIORE.png",[
        ("Un solo pezzo: tetto e retro",dict(camera=(-160,260,150),target=(45,60,69),scale=72),lid_only),
        ("Chiuso, visto da dietro",dict(camera=(200,340,170),target=(45,54.5,43),scale=82),None)],
        "Coda fino a quota 57 mm · 2 mm dietro Shield/T9 · spazio generoso per spine alte 20 mm · posizione USB nominale")
    two_views(empty_shell,"R15 / S9 IN RILIEVO","Logo senza sottotitolo · fronte in basso a destra · stesso colore della scocca","08_R15_LOGO_FRONTALE.png",[
        ("Fronte completo",dict(camera=(45,-300,43),target=(45,0,43),scale=56),None),
        ("Dettaglio del rilievo",dict(camera=(104,-100,29),target=(79,0,9.4),scale=10.5),None)],
        "S9 largo 14 mm · rilievo 0,4 mm · margine destro 4 mm e inferiore 6 mm · render del CAD, finitura fisica da verificare")
    side=cq.importers.importStep(str(ROOT/"CAD/scocca_R15.step")).val()
    side=side.intersect(g.box(-.1,-1,-1,3.101,103,88)).clean()
    side_rows=[(dict(kind="struttura"),g.mesh_of(side))]
    two_views(empty_shell,"R15 / SPIGOLI NETTI","Spigoli esterni a 90° · feritoie orizzontali · interno a incastro conservato","07_R15_PATTERN_LATERALE.png",[
        ("Tre quarti",dict(camera=(-190,-230,190),target=(45,50.5,43),scale=84),None),
        ("Dettaglio del fianco",dict(camera=(-300,50.5,43),target=(1.5,50.5,43),scale=65),side_rows)],
        "Scocca vuota · a destra parete isolata virtualmente · pattern su entrambi i fianchi · scocca R14 conservata")
    opened=[]
    cut_shell=cq.importers.importStep(str(ROOT/"CAD/scocca_R15.step")).val()
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
    two_views(opened,"L’interno ridotto all’essenziale","Coperchio e due pareti rimossi virtualmente per mostrare gli appoggi","02_R15_INTERNO.png",[
        ("Sei appoggi integrati nella scocca",dict(camera=(-150,-190,235),scale=84),empty),
        ("T7 + Shield + T9",dict(camera=(-150,-190,235),scale=84),None)],
        "Arancione: inserti T7 · blu: inserti Shield · SSD semitrasparenti · nessuna vite, tampone o adesivo interno")
    # Una sezione locale di ciascun alloggiamento, con SSD trasparente.
    im=Image.new("RGB",(2700,1170),BG);d=ImageDraw.Draw(im)
    d.text((60,35),"Una sede, tre formati",font=font(45,True),fill=INK)
    d.text((62,105),"Le culle calzano sulle guide R14: due sponde unite da una base",font=font(26),fill=MUTED)
    for i,model in enumerate(("T9","T7","T7_Shield")):
        x=i*900
        text="T9 / diretto" if model=="T9" else ("T7 / culla a U" if model=="T7" else "Shield / culla a U")
        d.text((x+50,185),text,font=font(31,True),fill=INK)
        local=[(dict(kind="struttura"),g.mesh_of(g.saddle(36)))]
        dssd=g.drive(model).intersect(g.box(10,28,0,25,16,100))
        local += [(dict(kind="gabarit_ssd",color="#455969",opacity=.23),g.mesh_of(dssd))]
        if model!="T9":
            local += [(dict(kind="inserto",color_override="#d89443" if model=="T7" else "#548caa"),g.mesh_of(g.adapter(model)))]
        path=ROOT/"anteprime"/("_sede"+str(i)+".png")
        raw=render(local,PALETTE,dict(camera=(-70,-70,105),target=(21,36,34),scale=43),path)
        im.paste(raw.resize((900,708)),(x,260));path.unlink()
        width=g.S["larghezze_adattate"][model]
        d.text((x+50,1005),f"Apertura {width:g} mm",font=font(26),fill=INK)
    d.text((60,1100),"Sezione locale del CAD · ingombri SSD trasparenti · due appoggi uguali per disco · stabilita e accoppiamento da verificare sul pezzo reale",font=font(23),fill=MUTED)
    im.save(ROOT/"anteprime/03_R15_SEDI.png")
    urows=[(dict(kind="inserto",color_override="#d89443"),g.mesh_of(g.adapter("T7")))]
    mounted=[(dict(kind="struttura"),g.mesh_of(g.saddle(36))),
        (dict(kind="inserto",color_override="#548caa"),g.mesh_of(g.adapter("T7_Shield"))),
        (dict(kind="gabarit_ssd",color="#455969",opacity=.23),
            g.mesh_of(g.drive("T7_Shield").intersect(g.box(10,26,0,24,20,90))))]
    two_views(urows,"R15 / CULLE A U", "Due sponde unite dal fondo · due collari pieni · guide R14 conservate", "10_R15_CULLE_U.png",[
        ("Culla T7, senza dispositivo",dict(camera=(-45,-55,65),target=(21,36,23),scale=20),None),
        ("Culla Shield sulla guida esistente",dict(camera=(-65,-65,80),target=(21,36,30),scale=38),mounted)],
        "2 culle T7 + 2 culle Shield · T9 diretto · base 1,2 mm · pareti Shield 2,5 mm · nessun adesivo o vite")
    # Sezione della parete e della linguetta, ricavata dai solidi CAD.
    roi=g.box(-.1,49,69,10.2,3,18)
    wall=g.shell().intersect(roi)
    free=g.lid().intersect(roi)
    loaded=g.lid(loaded=True).intersect(roi)
    contactrows=[(dict(kind="struttura"),g.mesh_of(wall)),
        (dict(kind="inserto",color_override="#d89443"),g.mesh_of(free))]
    loadedrows=[(dict(kind="struttura"),g.mesh_of(wall)),
        (dict(kind="inserto",color_override="#548caa"),g.mesh_of(loaded))]
    two_views(contactrows,"R15 / PRESA DEL COPERCHIO", "Sezione ingrandita della parete sinistra e della linguetta", "11_R15_ALETTE.png",[
        ("Forma libera: pattino +0,15 mm",dict(camera=(4,-200,77),target=(4,50.5,77),scale=10),None),
        ("Inviluppo spostato all’interno di 0,15 mm",dict(camera=(4,-200,77),target=(4,50.5,77),scale=10),loadedrows)],
        "Aletta 9 mm, prima 8 mm · 0,3 mm liberi per estremita dello slot · inviluppo geometrico, forza e deformazione non simulate")
    plate_plan()
    save_manifest()
    print("R15 ANTEPRIME PRONTE",flush=True)


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--plate-only',action='store_true');args=parser.parse_args()
    if args.plate_only:plate_plan();save_manifest()
    else:main()
