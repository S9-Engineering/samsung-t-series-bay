"""Viste R25 dagli STEP esportati, marchio nello stesso colore del tetto."""
import json
import cadquery as cq
import trimesh
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
ROOT=g.ROOT;PAL=dict(scocca='#30363c',tetto='#30363c')
def read(n):return cq.importers.importStep(str(ROOT/'CAD'/(n+'.step'))).val()
def row(s,col='#30363c'):return (dict(kind='struttura',color_override=col),g.mesh_of(s))
def raw(rows,view,name,size=(1080,850)):
 p=ROOT/'anteprime'/('_'+name+'.png');im=render(rows,PAL,view,p);p.unlink();return im.resize(size,Image.Resampling.LANCZOS)
def main():
 body=read('SCOCCA_R25');roof=read('TETTO_R25_LOGO_ENGINEERING');rows=[row(body),row(roof)]
 for i,m in enumerate(g.P['ssd_nominali']):rows.append(row(g.drive(m,i),g.P['colori'][m]))
 im=Image.new('RGB',(2250,1230),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R25 / S9 Engineering sul retro',font=font(43,True),fill=INK)
 d.text((45,95),'Logo completo approvato · centrato sulla coda · stesso PLA del tetto · rilievo 0,4 mm',font=font(27),fill=MUTED)
 d.text((50,170),'Tre quarti posteriore',font=font(29,True),fill=INK);d.text((1175,170),'Retro / logo 40 × 24,7 mm',font=font(29,True),fill=INK)
 im.paste(raw(rows,dict(camera=(185,280,175),target=(45,58,43),scale=81),'retro'),(10,220))
 im.paste(raw(rows,dict(camera=(45,350,43),target=(45,70,43),scale=64),'dritto'),(1140,220))
 d.text((45,1125),'Interni, chiusura e aperture conservati. L’aggiunta sporge soltanto 0,4 mm dalla faccia posteriore.',font=font(26),fill=MUTED)
 d.text((45,1180),'Anteprima CAD; nessuna prova fisica di finitura o leggibilità.',font=font(25),fill=MUTED)
 im.save(ROOT/'anteprime/01_R25_LOGO_POSTERIORE.png')
 im=Image.new('RGB',(1250,1110),BG);d=ImageDraw.Draw(im);d.text((40,25),'R25 / dettaglio del rilievo',font=font(40,True),fill=INK)
 im.paste(raw([row(roof)],dict(camera=(45,330,71.5),target=(45,109,71.5),scale=20),'dettaglio'),(85,130))
 d.text((40,1020),'Composizione originale S9 + ENGINEERING, senza deformazioni del marchio.',font=font(25),fill=MUTED);im.save(ROOT/'anteprime/02_R25_DETTAGLIO_LOGO.png')
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());parts={q['name']:q for q in m['parts']}
 for job in json.loads((ROOT/'verifiche/slicing/riepilogo.json').read_text())['jobs']:
  rows=[row(g.box(0,0,-1,256,256,1),'#dce2e6'),row(g.box(246,0,.01,10,20,.05),'#bd6565')]
  for it in job['items']:
   mesh=trimesh.load_mesh(ROOT/parts[it['part']]['stl'],process=True);mesh.apply_translation([*it['xy'],0]);col='#bd8742' if it['part'].startswith('TETTO_') else '#30363c';rows.append((dict(kind='struttura',color_override=col),mesh))
  im=Image.new('RGB',(1250,1160),BG);d=ImageDraw.Draw(im);d.text((40,25),'R25 / '+('tetto singolo' if job['mode']=='TETTO' else 'kit completo, unico piatto'),font=font(38,True),fill=INK)
  im.paste(raw(rows,dict(camera=(128,128,650),target=(128,128,0),up=(0,1,0),scale=144),'piatto'+job['mode']),(85,120))
  e=job['slicer_estimates'];d.text((40,1020),f"{e['total filament used [g]']} g / {e['estimated printing time (normal mode)']}",font=font(29,True),fill=INK)
  d.text((40,1080),'PLA BASIC · 0,4 mm · PEI testurizzato · brim 5 mm · senza supporti',font=font(25),fill=MUTED)
  d.text((40,1120),'Colore oro illustrativo; tutti i pezzi nello stesso PLA. Stime dello slicer.',font=font(23),fill=MUTED);im.save(ROOT/'anteprime'/('03_R25_PIATTO_'+job['mode']+'.png'))
 g.save(ROOT/'verifiche/anteprime.json',dict(manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},physical_photos=False));print('ANTEPRIME R25 PRONTE',flush=True)
if __name__=='__main__':main()
