"""Tavole R24 dagli STEP esportati e dal piatto verificato, non immagini AI."""
import json
import cadquery as cq
import numpy as np
import trimesh
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
ROOT=g.ROOT;PAL=dict(scocca='#30363c',tetto='#30363c');AMBER='#bd8742';BLUE='#547c94'
def row(s,color='#30363c'):return (dict(kind='struttura',color_override=color),g.mesh_of(s))
def read(name):return cq.importers.importStep(str(ROOT/'CAD'/(name+'.step'))).val()
def raw(rows,view,key,size=(1080,850)):
 p=ROOT/'anteprime'/('_'+key+'.png');im=render(rows,PAL,view,p);p.unlink();return im.resize(size,Image.Resampling.LANCZOS)
def main():
 shell=read('SCOCCA_R24');roof=read('TETTO_R24_SCORREVOLE');lock=read('FERMO_CARTUCCE_R24');key=g.closed_key()
 cut=shell.cut(g.box(-1,-1,5,7,111,80),g.box(-1,-1,5,92,9,80)).clean()
 models=list(g.P['ssd_nominali']);carriers=[read('CARTUCCIA_'+m+'_R24').translate((24*i,0,0)) for i,m in enumerate(models)]
 closed=[row(shell),row(roof),row(key)]
 internals=[row(c,AMBER) for c in carriers]+[row(lock,BLUE)]
 disks=[row(g.drive(m,i),g.P['colori'][m]) for i,m in enumerate(models)]
 im=Image.new('RGB',(2250,1960),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R24 / stesso monolite, nuove cartucce B',font=font(43,True),fill=INK)
 d.text((45,92),'T7 + T7 Shield + T9 · innesto comune nei tre slot · nessuna aletta flessibile',font=font(27),fill=MUTED)
 panels=[(closed,dict(camera=(-180,-230,190),target=(45,51,43),scale=77),'Chiuso / tetto e sagoma R22'),
         ([row(cut),*internals,*disks],dict(camera=(-180,-230,190),target=(45,51,40),scale=76),'Dentro / tre cartucce caricate'),
         ([row(cut),*internals],dict(camera=(-180,-230,190),target=(45,51,40),scale=76),'Dentro / cartucce senza SSD'),
         ([row(shell),*internals,*disks,row(roof),row(key)]+[row(g.usb_keepout(m,i),'#74818a') for i,m in enumerate(models)],dict(camera=(-170,275,52),target=(45,78,44),scale=79),'Retro / cavi fuori, coda alta')]
 for i,(rows,view,title) in enumerate(panels):
  x=15+(i%2)*1125;y=160+(i//2)*870;d.text((x+30,y),title,font=font(29,True),fill=INK);im.paste(raw(rows,view,'esterno'+str(i)),(x,y+45))
 d.text((45,1915),'90 × 109,4 × 86 mm, esclusi piedini/cavi. Sezioni e colori illustrativi; gabarit SSD nominali.',font=font(26),fill=MUTED)
 im.save(ROOT/'anteprime/01_R24_CASE_E_INTERNI.png')
 im=Image.new('RGB',(2280,1820),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R24 / tre taglie, un solo innesto',font=font(43,True),fill=INK)
 d.text((45,92),'Ogni cartuccia è un pezzo unico. Cornici da 3 mm; inviti da 0,6 mm alle due estremità.',font=font(27),fill=MUTED)
 for i,m in enumerate(models):
  c=read('CARTUCCIA_'+m+'_R24');x=i*760
  d.text((x+45,160),m.replace('_',' '),font=font(33,True),fill=INK)
  dims=g.dims(m);d.text((x+45,212),f"Canale {dims['spessore']+.4:g} × {dims['altezza']+.5:g} mm",font=font(26),fill=MUTED)
  view=dict(camera=(-140,-205,135),target=(21,53,39),scale=58)
  im.paste(raw([row(c,AMBER)],view,'car'+str(i),(760,598)),(x,260))
  im.paste(raw([row(c,AMBER),row(g.drive(m),g.P['colori'][m])],view,'ssd'+str(i),(760,598)),(x,870))
 d.text((45,1520),'Caricamento: infila il disco da dietro nella cartuccia estratta, con il cavo scollegato.',font=font(29,True),fill=INK)
 d.text((45,1585),'Poi inserisci la cartuccia nel case. Per cambiare ordine sposti SSD e cartuccia insieme.',font=font(29),fill=INK)
 d.text((45,1680),'Gioco SSD iniziale: 0,4 mm totale laterale e 0,5 mm sopra. Calzata reale da verificare sul provino.',font=font(27),fill=MUTED)
 d.text((45,1740),'Non è un serraggio. Il ponte collega le sponde e guida la parte alta del disco.',font=font(27),fill=MUTED)
 im.save(ROOT/'anteprime/02_R24_CARTUCCE.png')
 im=Image.new('RGB',(2250,1940),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R24 / montaggio senza forzare',font=font(43,True),fill=INK)
 steps=[([row(cut),*[row(c.translate((0,-6,15)),AMBER) for c in carriers]],'1. Cala le cartucce 6 mm più avanti'),
        ([row(cut),*[row(c,AMBER) for c in carriers]],'2. Falle scorrere indietro di 6 mm'),
        ([row(cut),*[row(c,AMBER) for c in carriers],row(lock.translate((0,0,15)),BLUE)],'3. Inserisci il fermo frontale comune'),
        ([row(cut),*internals,*disks,row(roof.translate((0,45,0)),AMBER)],'4. Collega i cavi e chiudi il tetto')]
 for i,(rows,title) in enumerate(steps):
  x=(i%2)*1125;y=155+(i//2)*860;d.text((x+40,y),title,font=font(28,True),fill=INK)
  im.paste(raw(rows,dict(camera=(-180,-230,190),target=(45,58,44),scale=85),'uso'+str(i)),(x,y+40))
 d.text((45,1895),'Per smontare: apri, togli il fermo, avanza la cartuccia di 6 mm e sollevala. Nessuna leva sulle cornici.',font=font(25),fill=MUTED)
 im.save(ROOT/'anteprime/03_R24_MONTAGGIO.png')
 jobs=json.loads((ROOT/'verifiche/slicing/riepilogo.json').read_text())['jobs'];man=json.loads((ROOT/'verifiche/manifest.json').read_text());parts={p['name']:p for p in man['parts']}
 for job in jobs:
  rows=[row(g.box(0,0,-1,256,256,1),'#dce2e6'),row(g.box(246,0,.01,10,20,.05),'#bd6565')]
  for it in job['items']:
   mesh=trimesh.load_mesh(ROOT/parts[it['part']]['stl'],process=True);mesh.apply_translation([*it['xy'],0]);col=AMBER if any(s in it['part'] for s in ['CARTUCCIA_','CORNICE_','TETTO_']) else BLUE if 'PERNO_' in it['part'] or 'FERMO_' in it['part'] else '#30363c';rows.append((dict(kind='struttura',color_override=col),mesh))
  im=Image.new('RGB',(1250,1180),BG);d=ImageDraw.Draw(im);title='Kit completo / sette pezzi, un piatto' if job['mode']=='COMPLETO' else 'Provino '+job['mode'].lower()
  d.text((40,25),'R24 / '+title,font=font(36,True),fill=INK)
  d.text((40,90),'ECC2 Combo · 0,4 mm · PEI testurizzato · ELEGOO PLA BASIC',font=font(25),fill=MUTED)
  im.paste(raw(rows,dict(camera=(128,128,650),target=(128,128,0),up=(0,1,0),scale=144),'piatto'+job['mode']),(85,155))
  e=job['slicer_estimates'];d.text((40,1040),f"{e['total filament used [g]']} g / {e['estimated printing time (normal mode)']}",font=font(29,True),fill=INK)
  d.text((40,1100),'Brim 5 mm incluso. Senza supporti, fuzzy skin o torre di spurgo.',font=font(25),fill=MUTED)
  d.text((40,1140),'Colori illustrativi: stampa monocolore. Stime dello slicer, non tempi misurati.',font=font(23),fill=MUTED)
  im.save(ROOT/'anteprime'/('04_R24_PIATTO_'+job['mode']+'.png'))
 g.save(ROOT/'verifiche/anteprime.json',dict(source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),outputs={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},physical_photo=False));print('ANTEPRIME R24 PRONTE',flush=True)
if __name__=='__main__':main()
