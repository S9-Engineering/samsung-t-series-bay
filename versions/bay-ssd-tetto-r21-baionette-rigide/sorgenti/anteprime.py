"""R21: assieme, sezioni e sequenza di chiusura dai file CAD esportati."""
import json
import cadquery as cq
import trimesh
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
ROOT=g.ROOT;pal=dict(scocca='#30363c',tetto='#bd8742')
def raw(rows,view,key):
 p=ROOT/'anteprime'/('_'+key+'.png');im=render(rows,pal,view,p);p.unlink();return im

def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());p=next(p for p in m['parts'] if p['role']=='TETTO');roof=cq.importers.importStep(str(ROOT/p['step'])).val();shell=g.reference_shell()
 def row(s,kind='coperchio',color=None):return(dict(kind=kind,**({'color_override':color} if color else {})),g.mesh_of(s))
 im=Image.new('RGB',(2280,1270),BG);d=ImageDraw.Draw(im)
 d.text((50,25),'R21 / tetto con due perni a quarto di giro',font=font(43,True),fill=INK)
 d.text((50,95),'Appoggi il tetto · inserisci i due perni · giri di 90° · nessun braccio da piegare',font=font(28),fill=MUTED)
 d.text((50,170),'Sotto il tetto: due supporti pieni',font=font(29,True),fill=INK)
 d.text((1190,170),'Chiuso sulla scocca esistente',font=font(29,True),fill=INK)
 s=roof.rotate((0,0,0),(1,0,0),180);b=g.bounds(s);s=s.translate(tuple(-__import__('numpy').array(b[0])))
 im.paste(raw([row(s)],dict(camera=(-110,220,180),target=(45,54,12),scale=74),'sotto'),(25,225))
 rows=[row(shell,'struttura'),row(roof),*[row(g.key(side,90),color='#547c94') for side in ['left','right']]]
 im.paste(raw(rows,dict(camera=(-180,-220,185),target=(45,50,43),scale=85),'assieme'),(1170,225))
 d.text((50,1120),'Tetto + 2 perni · PLA BASIC · nessuna vite, colla o ferramenta',font=font(28,True),fill=INK)
 d.text((50,1180),'I perni azzurri sono evidenziati per spiegare il montaggio; il progetto e monocolore.',font=font(24),fill=MUTED)
 d.text((50,1220),'Cinematica verificata sul CAD. Incastro reale da provare prima sulla traversa leggera inclusa.',font=font(24),fill=MUTED)
 im.save(ROOT/'anteprime/01_R21_TETTO_E_ASSIEME.png')
 # Vista dettagliata: foro passante e traversino interno prima/dopo il quarto di giro.
 roi=g.box(-5,43,67,20,15,18);part=roof.intersect(roi);wall=shell.intersect(roi)
 im=Image.new('RGB',(2280,1240),BG);d=ImageDraw.Draw(im)
 d.text((50,30),'R21 / come resta agganciato',font=font(43,True),fill=INK)
 d.text((50,100),'La testa trasversale passa in orizzontale; ruotata in verticale resta dietro al supporto.',font=font(27),fill=MUTED)
 for j,angle in enumerate([0,90]):
  d.text((50+j*1140,175),'1. Inserisci il perno' if j==0 else '2. Ruota di 90° per bloccare',font=font(29,True),fill=INK)
  rows=[row(wall,'struttura'),row(part),row(g.key('left',angle),color='#547c94')]
  im.paste(raw(rows,dict(camera=(35,-5,101),target=(5,50.5,75),scale=14),'fase'+str(j)),(25+j*1140,235))
 d.text((50,1125),'Il supporto e il perno trattengono il tetto per interferenza geometrica, senza richiedere una flessione.',font=font(26,True),fill=INK)
 d.text((50,1180),'Per aprire: torna in orizzontale, estrai entrambi i perni e solleva. Perni stampati piatti e sostituibili.',font=font(24),fill=MUTED)
 im.save(ROOT/'anteprime/02_R21_MECCANISMO.png')
 # Provino sullo stesso case: geometria degli agganci identica al tetto.
 cp=cq.importers.importStep(str(ROOT/'CAD/PROVINO_R21_BAIONETTA.step')).val()
 im=Image.new('RGB',(1250,1160),BG);d=ImageDraw.Draw(im)
 d.text((45,30),'R21 / prima la prova leggera',font=font(39,True),fill=INK)
 d.text((45,95),'Traversa + due perni, sulla tua scocca esistente',font=font(25),fill=MUTED)
 rows=[row(shell,'struttura'),row(cp),*[row(g.key(side,90),color='#547c94') for side in ['left','right']]]
 im.paste(raw(rows,dict(camera=(-180,-220,190),target=(45,50,43),scale=84),'provino'),(80,180))
 d.text((45,1080),'Serve a verificare i fori reali, la rotazione e il gioco prima del tetto completo.',font=font(23),fill=MUTED)
 d.text((45,1120),'Non richiede una nuova scocca; i perni sono riutilizzabili sul tetto.',font=font(23),fill=MUTED)
 im.save(ROOT/'anteprime/03_R21_PROVINO.png')
 g.save(ROOT/'verifiche/anteprime.json',dict(source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},physical_photo=False))
 print('ANTEPRIME R21 PRONTE',flush=True)
if __name__=='__main__':main()
