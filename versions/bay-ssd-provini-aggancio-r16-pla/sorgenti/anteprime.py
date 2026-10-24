"""Anteprime dei provini esportati e sezioni nominali delle finestre."""
from pathlib import Path
import json
import cadquery as cq
import trimesh
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
ROOT=g.ROOT;palette=dict(scocca='#30363c',tetto='#30363c');colors=['#c28b47','#5188aa','#5b9277']
def raw(rows,view,key):
 p=ROOT/'anteprime'/('_'+key+'.png');im=render(rows,palette,view,p);p.unlink();return im

def main():
 man=json.loads((ROOT/'verifiche/manifest.json').read_text())
 im=Image.new('RGB',(2700,1200),BG);d=ImageDraw.Draw(im)
 d.text((55,30),'R16 / tre provini, nessun tetto completo',font=font(44,True),fill=INK)
 d.text((55,100),'Stessa distanza fra le alette, stessa radice e stesso orientamento di stampa della R15',font=font(26),fill=MUTED)
 for i,p in enumerate(man['parts']):
  label=['I / riferimento R15','II / dente piu sporgente','III / spalla di ritenuta'][i]
  d.text((i*900+40,180),label,font=font(32,True),fill=INK)
  mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
  rows=[(dict(kind='coperchio',color_override=colors[i]),mesh)]
  image=raw(rows,dict(camera=(-65,-100,90),target=(45,7,7.5),scale=45),'provino'+str(i))
  im.paste(image.resize((900,708)),(i*900,245))
  d.text((i*900+40,1010),['Dente 0,6 mm / triangolare','Dente 1,0 mm / triangolare','Dente 1,0 mm / spalla quasi a quota finestra'][i],font=font(25),fill=INK)
 d.text((55,1120),'Traverse 90 x 14 mm, alte 15 mm in stampa · I / II / III incisi sulla faccia esterna · PLA unico, colori solo esplicativi',font=font(25),fill=MUTED)
 im.save(ROOT/'anteprime/01_R16_PROVINI.png')
 im=Image.new('RGB',(2700,1250),BG);d=ImageDraw.Draw(im)
 d.text((55,30),'R16 / cosa cambia nella presa',font=font(44,True),fill=INK)
 d.text((55,100),'Sezione su una finestra reale nominale: parete 3 mm, apertura alta 3 mm, bordo superiore 9 mm sotto il tetto',font=font(25),fill=MUTED)
 checks=json.loads((ROOT/'verifiche/geometria.json').read_text())['parts']
 roi=g.box(-.1,49.9,67,6.1,1.2,20)
 for i,p in enumerate(man['parts']):
  v=p['variant'];wall=g.reference_wall().intersect(roi)
  latch=g.coupon(v,inward=.15).intersect(roi)
  rows=[(dict(kind='struttura'),g.mesh_of(wall)),(dict(kind='coperchio',color_override=colors[i]),g.mesh_of(latch))]
  d.text((i*900+40,180),v['id'],font=font(34,True),fill=INK)
  image=raw(rows,dict(camera=(2.8,-200,76.5),target=(2.8,50.5,76.5),scale=10.5),'sezione'+str(i))
  im.paste(image.resize((900,708)),(i*900,235))
  c=checks[i]
  d.text((i*900+40,1005),f"Presa laterale nell’inviluppo: {c['geometric_reach_after_pad_translation_mm']:.2f} mm",font=font(23),fill=INK)
  d.text((i*900+40,1050),f"Gioco verticale geometrico: {c['vertical_lid_play_envelope_mm']:.2f} mm",font=font(23),fill=INK)
 d.text((55,1155),'Linguette traslate di 0,15 mm verso interno: inviluppo geometrico, non simulazione elastica o misura della forza',font=font(25),fill=MUTED)
 im.save(ROOT/'anteprime/02_R16_SEZIONI.png')
 # Provino III appoggiato su entrambe le pareti, controparte solo illustrata.
 rows=[(dict(kind='struttura'),g.mesh_of(g.reference_wall(s))) for s in ('left','right')]
 rows += [(dict(kind='coperchio',color_override=colors[2]),g.mesh_of(g.coupon(g.P['varianti'][2])))]
 im=Image.new('RGB',(1250,1100),BG);d=ImageDraw.Draw(im)
 d.text((45,30),'R16 / si prova sulla scocca esistente',font=font(38,True),fill=INK)
 d.text((45,90),'La traversa va al centro, sopra le due finestrelle laterali',font=font(24),fill=MUTED)
 im.paste(raw(rows,dict(camera=(-50,-80,150),target=(45,50.5,78),scale=52),'montaggio'),(80,175))
 d.text((45,1040),'Grigio: sezioni del case gia stampato · verde: provino III · nessun pezzo di case da stampare',font=font(22),fill=MUTED)
 im.save(ROOT/'anteprime/03_R16_MONTAGGIO.png')
 g.save(ROOT/'verifiche/anteprime.json',dict(source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},physical_photo=False))
 print('ANTEPRIME R16 PRONTE',flush=True)
if __name__=='__main__':main()
