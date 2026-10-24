"""R20: tetto senza tagli superiori e flessure visibili solo da sotto."""
import json,zipfile,tempfile
from pathlib import Path
import cadquery as cq
import trimesh
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
from slicer_utils import parse_gcode
from percorsi import draw_layer
ROOT=g.ROOT;palette=dict(scocca='#30363c',tetto='#bd8742')
def raw(rows,view,key):
 p=ROOT/'anteprime'/('_'+key+'.png');im=render(rows,palette,view,p);p.unlink();return im

def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());p=m['parts'][0]
 printed=trimesh.load_mesh(ROOT/p['stl'],process=True);source=cq.importers.importStep(str(ROOT/p['step'])).val()
 im=Image.new('RGB',(2280,1230),BG);d=ImageDraw.Draw(im)
 d.text((55,30),'R20 / tetto pulito sopra, agganci flessibili sotto',font=font(42,True),fill=INK)
 d.text((55,100),'Eliminati i tagli attorno alle alette; restano le sole feritoie orizzontali',font=font(27),fill=MUTED)
 d.text((55,175),'Orientamento di stampa: faccia esterna sul piano',font=font(26,True),fill=INK)
 d.text((1190,175),'Vista dall’alto, nella posizione montata',font=font(26,True),fill=INK)
 im.paste(raw([(dict(kind='coperchio'),printed)],dict(camera=(-100,220,170),target=(45,54.5,9),scale=71),'stampa'),(30,235))
 im.paste(raw([(dict(kind='coperchio'),g.mesh_of(source))],dict(camera=(-100,-160,220),target=(45,54.5,76),scale=72),'alto'),(1170,235))
 d.text((55,1125),'90,083 × 109 × 29 mm · un solo pezzo · flessure distanziate 3 mm dal tetto',font=font(26,True),fill=INK)
 d.text((55,1180),'Braccetti nella posizione R18; attacco interno riprogettato. Supporti sotto flessure e braccetti da rimuovere.',font=font(24),fill=MUTED)
 im.save(ROOT/'anteprime/01_TETTO_R20.png')
 shell=trimesh.load_mesh(ROOT/'verifiche/mesh_assieme/scocca_R15_NON_STAMPARE.ply',process=True)
 rows=[(dict(kind='struttura'),shell),(dict(kind='coperchio'),g.mesh_of(source))]
 im=Image.new('RGB',(1250,1160),BG);d=ImageDraw.Draw(im)
 d.text((45,30),'R20 / sulla scocca esistente',font=font(40,True),fill=INK)
 d.text((45,95),'Sul piatto e presente soltanto il nuovo tetto',font=font(25),fill=MUTED)
 im.paste(raw(rows,dict(camera=(-180,-220,185),target=(45,50,43),scale=84),'assieme'),(80,185))
 d.text((45,1070),'Tetto evidenziato in ocra; progetto di stampa monocolore PLA BASIC.',font=font(23),fill=MUTED)
 d.text((45,1115),'Anteprima CAD; accoppiamento fisico del tetto completo ancora da verificare.',font=font(22),fill=MUTED)
 im.save(ROOT/'anteprime/02_ASSIEME_R20.png')
 job=json.loads((ROOT/'verifiche/slicing/TETTO/job.json').read_text())
 with zipfile.ZipFile(ROOT/job['project']) as z,tempfile.TemporaryDirectory() as td:
  path=Path(td)/'percorsi.gcode';path.write_bytes(z.read(next(n for n in z.namelist() if n.endswith('.gcode'))));layers,analysis=parse_gcode(path)
 im=Image.new('RGB',(1250,1250),BG);d=ImageDraw.Draw(im)
 d.text((45,30),'R20 / un solo tetto su un piatto',font=font(40,True),fill=INK)
 d.text((45,95),'Primo strato reale dal 3MF, con brim e supporti',font=font(26),fill=MUTED)
 draw_layer(d,layers[0],(80,165),1000,[0,0,256,256])
 # La zona esclusa e in basso a destra: fuori dalla disposizione del pezzo.
 d.text((45,1190),'ECC2 Combo · PEI testurizzato · ugello 0,4 mm · PLA BASIC · strato 0,20 mm',font=font(24),fill=MUTED)
 im.save(ROOT/'anteprime/03_PIATTO_R20.png')
 g.save(ROOT/'verifiche/anteprime.json',dict(source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),project_sha256=job['project_sha256'],outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},physical_photo=False))
 print('ANTEPRIME TETTO R20 PRONTE',flush=True)
if __name__=='__main__':main()
