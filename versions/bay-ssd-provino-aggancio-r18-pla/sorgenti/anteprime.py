"""R18: viste dai file finali e confronto delle quote della paletta."""
import json
import cadquery as cq
import trimesh
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
ROOT=g.ROOT;palette=dict(scocca='#30363c',tetto='#bd8742')
def raw(rows,view,key):
 p=ROOT/'anteprime'/('_'+key+'.png');im=render(rows,palette,view,p);p.unlink();return im

def main():
 man=json.loads((ROOT/'verifiche/manifest.json').read_text());part=man['parts'][0]
 geo=json.loads((ROOT/'verifiche/geometria.json').read_text())
 s=cq.importers.importStep(str(ROOT/part['step'])).val()
 wall=cq.importers.importStep(str(ROOT/'CAD/RIFERIMENTO_PARETE_left_NON_STAMPARE.step')).val()
 roi=g.box(-.2,49.9,67,9.4,1.2,20)
 cut=[(dict(kind='struttura'),g.mesh_of(wall.intersect(roi))),
  (dict(kind='coperchio'),g.mesh_of(s.intersect(roi)))]
 mesh=trimesh.load_mesh(ROOT/part['stl'],process=True)
 im=Image.new('RGB',(2280,1260),BG);d=ImageDraw.Draw(im)
 d.text((55,30),'R18 / aletta vicina al case, appena aperta verso fuori',font=font(40,True),fill=INK)
 d.text((55,100),'Gioco radice 0,15 mm · apertura 0,10 mm su 12 mm · braccetto lungo 3,1 mm come R17',font=font(27),fill=MUTED)
 d.text((55,180),'Un solo provino, due agganci',font=font(29,True),fill=INK)
 d.text((1190,180),'Sezione: nessuna interferenza a riposo',font=font(27,True),fill=INK)
 im.paste(raw([(dict(kind='coperchio'),mesh)],dict(camera=(-60,-90,90),target=(45,16,7.5),scale=47),'completo'),(30,240))
 im.paste(raw(cut,dict(camera=(4,-200,76.5),target=(4,50.5,76.5),scale=10.3),'sezione'),(1170,240))
 d.text((55,1140),'Il taglio nel tetto resta identico alla R17',font=font(27,True),fill=INK)
 d.text((1190,1140),'Gioco minimo aletta-parete: 0,05 mm',font=font(25,True),fill=INK)
 d.text((55,1200),'Quote nominali dal CAD · apertura circa 0,48° · punta praticamente a filo (0,04 mm oltre) · presa da provare',font=font(23),fill=MUTED)
 im.save(ROOT/'anteprime/01_R18_AGGANCIO.png')
 rows=[(dict(kind='struttura'),g.mesh_of(g.reference_wall(side))) for side in ('left','right')]
 rows += [(dict(kind='coperchio'),g.mesh_of(s))]
 im=Image.new('RGB',(1250,1120),BG);d=ImageDraw.Draw(im)
 d.text((45,30),'R18 / prova sulla scocca esistente',font=font(38,True),fill=INK)
 d.text((45,95),'Stesso foro e stessa lunghezza del braccetto R17',font=font(25),fill=MUTED)
 im.paste(raw(rows,dict(camera=(-70,-90,155),target=(45,42,77),scale=56),'montaggio'),(80,190))
 d.text((45,1060),'Grigio: case esistente · ocra: provino · rimuovere i supporti di stampa prima del test',font=font(22),fill=MUTED)
 im.save(ROOT/'anteprime/02_R18_MONTAGGIO.png')
 # Proiezione XZ del STEP: inclinazione reale, senza amplificazione del disegno.
 im=Image.new('RGB',(1600,1170),BG);d=ImageDraw.Draw(im)
 d.text((50,30),'R17 → R18 / cambia solo la posizione dell’aletta',font=font(36,True),fill=INK)
 d.text((50,90),'Sezioni in scala reale fra loro; il lieve angolo non e amplificato',font=font(24),fill=MUTED)
 old=ROOT.parent/'bay-ssd-provino-braccetto-passante-r17-pla/CAD/PROVINO_BRACCETTO_PASSANTE_R17.step'
 sections=[cq.importers.importStep(str(old)).val(),s]
 scale=30
 for index,ss in enumerate(sections):
  ox=90+index*770;oy=800
  def xy(x,z):return(ox+(x+1)*scale,oy-(z-67)*scale)
  d.text((ox,145),'R17 — provato' if index==0 else 'R18 — da provare',font=font(28,True),fill=INK)
  for solid,color in [(wall,'#454b50'),(ss,'#bc8849')]:
   mm=g.mesh_of(solid.intersect(roi))
   for tri in mm.triangles:d.polygon([xy(float(x),float(z)) for x,y,z in tri],fill=color)
  texts=['Gioco alla radice: 0,30 mm','Aletta verticale','Braccetto: 3,1 mm'] if index==0 else ['Gioco alla radice: 0,15 mm','Apertura alla punta: 0,10 mm','Gioco minimo: 0,05 mm']
  for k,t in enumerate(texts):d.text((ox,840+k*48),t,font=font(24),fill=INK)
 d.text((50,1060),'Parete 3 mm · aletta spessa 1,2 mm in entrambe le revisioni · taglio superiore conservato',font=font(24,True),fill=INK)
 d.text((50,1110),'Il gioco residuo evita una collisione nominale; tolleranze e forza si verificano sulla stampa.',font=font(23),fill=MUTED)
 im.save(ROOT/'anteprime/03_R17_R18_CONFRONTO.png')
 g.save(ROOT/'verifiche/anteprime.json',dict(source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},physical_photo=False))
 print('ANTEPRIME R18 PRONTE',flush=True)
if __name__=='__main__':main()
