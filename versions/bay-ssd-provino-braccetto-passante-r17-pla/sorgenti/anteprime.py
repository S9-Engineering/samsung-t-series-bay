"""R17: vista reale del CAD esportato e penetrazione nella parete da 3 mm."""
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
 s=cq.importers.importStep(str(ROOT/part['step'])).val()
 wall=cq.importers.importStep(str(ROOT/'CAD/RIFERIMENTO_PARETE_left_NON_STAMPARE.step')).val()
 roi=g.box(-.2,49.9,67,9.4,1.2,20)
 cut=[(dict(kind='struttura'),g.mesh_of(wall.intersect(roi))),
  (dict(kind='coperchio'),g.mesh_of(s.intersect(roi)))]
 mesh=trimesh.load_mesh(ROOT/part['stl'],process=True)
 im=Image.new('RGB',(2280,1260),BG);d=ImageDraw.Draw(im)
 d.text((55,30),'R17 / il braccetto entra quasi fino al filo esterno',font=font(43,True),fill=INK)
 d.text((55,100),'Parete del case: 3 mm · penetrazione nel foro: 2,8 mm · margine esterno: 0,2 mm',font=font(28),fill=MUTED)
 d.text((55,180),'Un solo provino, due braccetti',font=font(29,True),fill=INK)
 d.text((1190,180),'Sezione del foro e dell’aggancio',font=font(29,True),fill=INK)
 im.paste(raw([(dict(kind='coperchio'),mesh)],dict(camera=(-60,-90,90),target=(45,16,7.5),scale=47),'completo'),(30,240))
 im.paste(raw(cut,dict(camera=(4,-200,76.5),target=(4,50.5,76.5),scale=10.3),'sezione'),(1170,240))
 d.text((55,1140),'Lunghezza dal fianco dell’aletta alla punta: 3,1 mm',font=font(27,True),fill=INK)
 d.text((1190,1140),'Braccetto largo 8,4 mm nel foro largo 9,6 mm',font=font(25,True),fill=INK)
 d.text((55,1200),'Quote nominali dal CAD · scarichi alla radice per la corsa laterale · forza e ritorno elastico da provare sulla stampa',font=font(23),fill=MUTED)
 im.save(ROOT/'anteprime/01_R17_BRACCETTO_PASSANTE.png')
 # Vista sulla scocca; la controparte non e un componente da stampare.
 rows=[(dict(kind='struttura'),g.mesh_of(g.reference_wall(side))) for side in ('left','right')]
 rows += [(dict(kind='coperchio'),g.mesh_of(s))]
 im=Image.new('RGB',(1250,1120),BG);d=ImageDraw.Draw(im)
 d.text((45,30),'R17 / prova sulla scocca esistente',font=font(38,True),fill=INK)
 d.text((45,95),'Entrambi i braccetti nelle finestrelle laterali',font=font(25),fill=MUTED)
 im.paste(raw(rows,dict(camera=(-70,-90,155),target=(45,42,77),scale=56),'montaggio'),(80,190))
 d.text((45,1060),'Grigio: case esistente · ocra: provino · i supporti di stampa sono da rimuovere prima del test',font=font(22),fill=MUTED)
 im.save(ROOT/'anteprime/02_R17_MONTAGGIO.png')
 g.save(ROOT/'verifiche/anteprime.json',dict(source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},physical_photo=False))
 print('ANTEPRIME R17 PRONTE',flush=True)
if __name__=='__main__':main()
