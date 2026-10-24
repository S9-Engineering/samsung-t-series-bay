"""Tavole CAD R22 generate dagli STEP esportati; nessuna foto o prova fisica."""
import json
import cadquery as cq
import numpy as np
import trimesh
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
ROOT=g.ROOT;PAL=dict(scocca='#30363c',tetto='#30363c')
def row(s,kind='struttura',color=None):return(dict(kind=kind,**({'color_override':color} if color else {})),g.mesh_of(s))
def raw(rows,view,key,size=None):
 p=ROOT/'anteprime'/('_'+key+'.png');im=render(rows,PAL,view,p);p.unlink()
 return im.resize(size,Image.Resampling.LANCZOS) if size else im
def panel(im,rows,view,xy,key,label):
 d=ImageDraw.Draw(im);d.text((xy[0]+25,xy[1]),label,font=font(27,True),fill=INK)
 im.paste(raw(rows,view,key,(1026,808)),(xy[0],xy[1]+45))
def main():
 shell=cq.importers.importStep(str(ROOT/'CAD/SCOCCA_R22.step')).val();roof=cq.importers.importStep(str(ROOT/'CAD/TETTO_R22_SCORREVOLE.step')).val();key=g.closed_key()
 closed=[row(shell),row(roof,'coperchio'),row(key)]
 im=Image.new('RGB',(2160,1930),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R22 / il monolite resta pulito',font=font(43,True),fill=INK)
 d.text((45,92),'Guide interne · un solo fermo nascosto sotto la coda · spigoli netti · nessuna paletta laterale',font=font(26),fill=MUTED)
 for rows,view,xy,tag,title in [
  (closed,dict(camera=(-180,-230,190),target=(45,51,43),scale=77),(20,160),'iso','Chiuso / tre quarti'),
  (closed,dict(camera=(45,-280,43),target=(45,50,43),scale=67),(1110,160),'fronte','Fronte / S9 in rilievo'),
  (closed,dict(camera=(-280,54.5,43),target=(45,54.5,43),scale=67),(20,1030),'lato','Lato / sagoma senza sporgenze'),
  ([row(roof,'coperchio')],dict(camera=(45,54.5,320),target=(45,54.5,43),up=(0,1,0),scale=67),(1110,1030),'alto','Tetto dall’alto / feritoie orizzontali')]:panel(im,rows,view,xy,tag,title)
 d.text((45,1885),'Ingombro chiuso 90 × 109,4 × 86 mm, incluso rilievo S9. Anteprima CAD, non foto di stampa.',font=font(25),fill=MUTED)
 im.save(ROOT/'anteprime/01_R22_SILHOUETTE.png')
 # Funzionamento: inserimento dal retro e due dettagli reali in sezione.
 im=Image.new('RGB',(2280,2110),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R22 / come si chiude',font=font(43,True),fill=INK)
 d.text((45,95),'1. Fai scorrere il tetto dal retro.  2. Inserisci il perno da sotto.  3. Gira e abbassa nella sede.',font=font(28),fill=MUTED)
 rows=[row(shell),row(roof.translate((0,55,0)),'coperchio','#bd8742')]
 im.paste(raw(rows,dict(camera=(-185,-230,195),target=(45,70,43),scale=96),'scorre',(1080,850)),(15,170))
 # Sezione XZ lontano dal fermo: mostra le due superfici a 45 gradi.
 roi=g.box(-1,35,70,16,14,18);rows=[row(shell.intersect(roi)),row(roof.intersect(roi),'coperchio','#bd8742')]
 im.paste(raw(rows,dict(camera=(50,-90,103),target=(7,42,78),scale=13),'guida',(1080,850)),(1170,170))
 d.text((55,1050),'Le guide trattengono il tetto lungo entrambi i lati.',font=font(28,True),fill=INK)
 d.text((1200,1050),'Sezione di una guida: niente linguette da piegare.',font=font(28,True),fill=INK)
 roi=g.box(0,88,50,15,22,37)
 for j,(angle,dz,title) in enumerate([(0,0,'Perno sollevato / inserimento e rotazione'),(90,-1.1,'Perno abbassato / bloccaggio in sede')]):
  # Taglio anteriore del blocco del tetto per vedere il traversino e il suo appoggio.
  receiver=roof.intersect(roi).cut(g.box(0,88,55,16,7,29))
  ear=shell.intersect(roi).cut(g.box(0,88,55,16,6,29))
  rows=[row(ear),row(receiver,'coperchio','#bd8742'),row(g.key(angle,dz),color='#547c94')]
  im.paste(raw(rows,dict(camera=(32,54,87),target=(7,98,67),scale=24),'fermo'+str(j),(1080,850)),(15+j*1155,1130))
  d.text((55+j*1155,1100),title,font=font(26,True),fill=INK)
 d.text((45,2035),'Per aprire: alza il perno di 1,1 mm, giralo e sfilalo; poi arretra il tetto. Nessuna vite o colla.',font=font(27,True),fill=INK)
 d.text((45,2080),'I colori evidenziano i pezzi. Stampa monocolore; presa, scorrevolezza e durata restano da provare.',font=font(24),fill=MUTED)
 im.save(ROOT/'anteprime/02_R22_GUIDE_E_FERMO.png')
 # Retro reale con SSD e keepout dei connettori: nessuna appendice fuori dalla sagoma.
 im=Image.new('RGB',(2280,1230),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R22 / retro e prova preliminare',font=font(43,True),fill=INK)
 rows=closed.copy()
 for slot,model in enumerate(['T7','T7_Shield','T9']):
  rows.append(row(g.drive(model,slot),color=g.P['colori'][model]))
  rows.append(row(g.usb_keepout(model,slot),color='#74818a'))
 im.paste(raw(rows,dict(camera=(-170,275,52),target=(45,78,44),scale=79),'retro',(1080,850)),(20,160))
 cb=cq.importers.importStep(str(ROOT/'CAD/PROVINO_SCOCCA_R22.step')).val();ct=cq.importers.importStep(str(ROOT/'CAD/PROVINO_TETTO_R22.step')).val()
 rows=[row(cb),row(ct,'coperchio','#bd8742'),row(key,color='#547c94')]
 im.paste(raw(rows,dict(camera=(-150,255,145),target=(45,87,68),scale=61),'coupon',(1080,850)),(1170,160))
 d.text((55,1050),'Comando sotto la coda, dentro il volume del case.',font=font(28,True),fill=INK)
 d.text((1200,1050),'Prima: provino con entrambe le guide e lo stesso fermo.',font=font(27,True),fill=INK)
 d.text((45,1130),'Ingombri USB prudenziali 20 × 20 × 50 mm. Posizione delle porte e accesso con le dita da verificare sui pezzi reali.',font=font(25),fill=MUTED)
 d.text((45,1180),'La scocca R22 va ristampata. Gli inserti a U T7 e Shield gia realizzati restano riutilizzabili.',font=font(26,True),fill=INK)
 im.save(ROOT/'anteprime/03_R22_RETRO_E_PROVINO.png')
 job=json.loads((ROOT/'verifiche/slicing/COMPLETO/job.json').read_text());man=json.loads((ROOT/'verifiche/manifest.json').read_text())
 parts={p['name']:p for p in man['parts']};rows=[row(g.box(0,0,-1,256,256,1),color='#dce2e6'),row(g.box(246,0,.01,10,20,.05),color='#bd6565')]
 for item in job['items']:
  mesh=trimesh.load_mesh(ROOT/parts[item['part']]['stl'],process=True);mesh.apply_translation([*item['xy'],0])
  color='#bd8742' if item['part']=='TETTO_R22_SCORREVOLE' else ('#547c94' if item['part']=='PERNO_R22_NASCOSTO' else '#30363c')
  rows.append((dict(kind='struttura',color_override=color),mesh))
 im=Image.new('RGB',(1250,1170),BG);d=ImageDraw.Draw(im)
 d.text((40,25),'R22 / tutto su un unico piatto',font=font(40,True),fill=INK)
 d.text((40,90),'Scocca + tetto + perno + 2 inserti T7 + 2 inserti Shield',font=font(25),fill=MUTED)
 im.paste(raw(rows,dict(camera=(128,128,650),target=(128,128,0),up=(0,1,0),scale=144),'piatto',(1080,850)),(85,155))
 d.text((40,1040),'159,67 g / 9 h 10 min 40 s · PLA BASIC · ugello 0,4 mm',font=font(28,True),fill=INK)
 d.text((40,1090),'Brim 5 mm compreso negli ingombri verificati. Nessun supporto o torre di spurgo.',font=font(23),fill=MUTED)
 d.text((40,1130),'Colori illustrativi; stampa monocolore. Zona esclusa della macchina evidenziata in rosso.',font=font(23),fill=MUTED)
 im.save(ROOT/'anteprime/04_R22_PIATTO_UNICO.png')
 g.save(ROOT/'verifiche/anteprime.json',dict(source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},physical_photo=False))
 print('ANTEPRIME R22 PRONTE',flush=True)
if __name__=='__main__':main()
