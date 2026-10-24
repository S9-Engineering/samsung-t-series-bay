"""Anteprime R26 dai file STEP/STL finali, assemblaggio distinto dai piatti."""
import json
import cadquery as cq
import trimesh
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
ROOT=g.ROOT;PAL=dict(scocca='#30363c',tetto='#30363c')
def read(n):return cq.importers.importStep(str(ROOT/'CAD'/(n+'.step'))).val()
def row(s,col='#30363c',**kw):return (dict(kind='struttura',color_override=col,**kw),g.mesh_of(s))
def raw(rows,view,name,size=(1080,850)):
 p=ROOT/'anteprime'/('_'+name+'.png');im=render(rows,PAL,view,p);p.unlink();return im.resize(size,Image.Resampling.LANCZOS)
def main():
 body=read('SCOCCA_R26_DOPPIO_PERNO');roof=read('TETTO_R26_DOPPIO_PERNO');pin=read('PERNO_R26_NASCOSTO')
 keys=[pin.rotate((g.CX,g.CY,0),(g.CX,g.CY,100),90).translate((0,0,-1.1))];keys.append(g.mirrored(keys[0]))
 rows=[row(body),row(roof),*[row(k) for k in keys],row(read('FERMO_CARTUCCE_R26'))]
 for i,m in enumerate(g.P['ssd_nominali']):rows.append(row(read('CARTUCCIA_'+m+'_R26').translate((g.r24.cx(i)-g.r24.cx(0),0,0))));rows.append(row(g.drive(m,i),g.P['colori'][m]))
 im=Image.new('RGB',(2250,1230),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R26 / doppio perno nascosto',font=font(43,True),fill=INK)
 d.text((45,95),'Scocca e tetto aggiornati · due perni identici · logo S9 Engineering sul retro',font=font(27),fill=MUTED)
 d.text((50,170),'Fronte',font=font(29,True),fill=INK);d.text((1175,170),'Retro',font=font(29,True),fill=INK)
 im.paste(raw(rows,dict(camera=(185,-240,165),target=(45,52,43),scale=81),'fronte'),(10,220))
 im.paste(raw(rows,dict(camera=(185,280,175),target=(45,58,43),scale=81),'retro'),(1140,220))
 d.text((45,1125),'Due punti di arresto interni speculari. Profilo esterno, cartucce B e ventilazione conservati.',font=font(26),fill=MUTED)
 d.text((45,1180),'Anteprima CAD; forza di ritenuta e durata del kit completo non ancora provate.',font=font(25),fill=MUTED)
 im.save(ROOT/'anteprime/01_R26_CASE_COMPLETO.png')
 im=Image.new('RGB',(2250,1230),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R26 / i due bloccaggi interni',font=font(43,True),fill=INK)
 d.text((45,95),'Perni evidenziati in blu soltanto per lettura. Tutti i pezzi stampati nello stesso PLA.',font=font(27),fill=MUTED)
 d.text((50,170),'Vista dal retro, sotto la coda',font=font(29,True),fill=INK);d.text((1175,170),'Tetto visto da sotto',font=font(29,True),fill=INK)
 im.paste(raw([row(body),row(roof),*[row(k,'#547c94') for k in keys]],dict(camera=(45,290,39),target=(45,94,60),scale=43),'perni_retro'),(10,220))
 im.paste(raw([row(roof),*[row(k,'#547c94') for k in keys]],dict(camera=(45,180,-120),target=(45,60,76),up=(0,1,0),scale=70),'tetto_sotto'),(1140,220))
 d.text((45,1125),'Inserire dal basso, ruotare di un quarto di giro e abbassare nella sede di 1,1 mm.',font=font(26),fill=MUTED)
 d.text((45,1180),'Prima di sfilare il tetto occorre sbloccare ed estrarre entrambi i perni.',font=font(25),fill=MUTED);im.save(ROOT/'anteprime/02_R26_DUE_PERNI.png')
 cb=read('PROVINO_GUIDE_SCOCCA_R26');cr=read('PROVINO_GUIDE_TETTO_R26')
 im=Image.new('RGB',(2250,1230),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R26 / provino del doppio bloccaggio',font=font(43,True),fill=INK)
 d.text((45,95),'Due porzioni di scocca e tetto + due perni identici. Prova delle due sedi e delle guide.',font=font(27),fill=MUTED)
 d.text((50,170),'Montato',font=font(29,True),fill=INK);d.text((1175,170),'Esploso illustrativo',font=font(29,True),fill=INK)
 im.paste(raw([row(cb),row(cr),*[row(k,'#547c94') for k in keys]],dict(camera=(145,235,125),target=(45,88,69),scale=57),'provino_montato'),(10,220))
 im.paste(raw([row(cb),row(cr.translate((0,0,27)),'#bd8742'),*[row(k.translate((0,0,-12)),'#547c94') for k in keys]],dict(camera=(145,235,125),target=(45,88,77),scale=68),'provino_esploso'),(1140,220))
 d.text((45,1125),'Gli alleggerimenti del provino conservano integralmente entrambi i ricevitori.',font=font(26),fill=MUTED)
 d.text((45,1180),'Nessuna nuova prova degli interni richiesta: primo provino R24 accettato dall’utente.',font=font(25),fill=MUTED);im.save(ROOT/'anteprime/03_R26_PROVINO_DOPPIO_PERNO.png')
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());parts={q['name']:q for q in m['parts']}
 for job in json.loads((ROOT/'verifiche/slicing/riepilogo.json').read_text())['jobs']:
  rows=[row(g.box(0,0,-1,256,256,1),'#dce2e6'),row(g.box(246,0,.01,10,20,.05),'#bd6565')]
  for it in job['items']:
   mesh=trimesh.load_mesh(ROOT/parts[it['part']]['stl'],process=True);mesh.apply_translation([*it['xy'],0]);col='#bd8742' if 'TETTO' in it['part'] else '#30363c';rows.append((dict(kind='struttura',color_override=col),mesh))
  im=Image.new('RGB',(1250,1160),BG);d=ImageDraw.Draw(im)
  d.text((40,25),'R26 / '+('provino: quattro pezzi' if job['mode']=='PROVINO' else 'kit completo: otto pezzi'),font=font(38,True),fill=INK)
  im.paste(raw(rows,dict(camera=(128,128,650),target=(128,128,0),up=(0,1,0),scale=144),'piatto'+job['mode']),(85,120))
  e=job['slicer_estimates'];d.text((40,1020),f"{e['total filament used [g]']} g / {e['estimated printing time (normal mode)']}",font=font(29,True),fill=INK)
  d.text((40,1080),'PLA BASIC · 0,4 mm · PEI testurizzato · brim 5 mm · senza supporti',font=font(25),fill=MUTED)
  d.text((40,1120),'Colore oro illustrativo. Stime dello slicer, non tempi misurati.',font=font(23),fill=MUTED);im.save(ROOT/'anteprime'/('04_R26_PIATTO_'+job['mode']+'.png'))
 g.save(ROOT/'verifiche/anteprime.json',dict(manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},physical_photos=False));print('ANTEPRIME R26 PRONTE',flush=True)
if __name__=='__main__':main()
