"""Viste accurate dello studio R23: nessuna immagine generativa o prova fisica."""
import json
import cadquery as cq
from PIL import Image,ImageDraw
import genera as g
from render_base import render,font,BG,INK,MUTED
ROOT=g.ROOT;PAL=dict(scocca='#30363c',tetto='#30363c');ORANGE='#bd8742';BLUE='#668ca5'
def row(s,color='#30363c',opacity=None):return(dict(kind='struttura',color_override=color,**({'opacity':opacity} if opacity else {})),g.mesh_of(s))
def raw(rows,view,name,size=(940,740)):
 p=ROOT/'anteprime'/('_'+name+'.png');im=render(rows,PAL,view,p);p.unlink();return im.resize(size,Image.Resampling.LANCZOS)
def textlines(d,xy,lines,size=26,bold=False,color=MUTED,line_height=37):
 for k,line in enumerate(lines):d.text((xy[0],xy[1]+k*line_height),line,font=font(size,bold),fill=color)
def loaded(option,model,slot,opacity=None):
 rows=[row(g.carrier(option,model,slot),ORANGE),row(g.drive(model,slot),g.P['colori'][model],opacity)]
 if option=='C':rows.append(row(g.upper_guide(model,slot),BLUE))
 return rows
def cutaway(s):return s.cut(g.box(-1,-2,5,92,11,70),g.box(-1,-1,5,7,104,65)).clean()
def main():
 manifest=json.loads((ROOT/'verifiche/manifest.json').read_text());assert manifest['source_sha256']==g.sha(ROOT/'sorgenti/genera.py')
 im=Image.new('RGB',(2940,2005),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R23 / tre modi di tenere dritti gli SSD',font=font(46,True),fill=INK)
 d.text((45,95),'Stesso T9 nelle tre viste · culle in PLA BASIC · disco libero, base della culla trattenuta sul basamento',font=font(30),fill=MUTED)
 titles={'A':'A / Culla aperta alta','B':'B / Due cornici chiuse','C':'C / Guida bassa + guida alta'}
 subtitles={'A':['Inserisci e sfili il disco dall’alto.','Una culla monoblocco per ciascun modello.'],
  'B':['Infili il disco da dietro nella cartuccia.','Poi inserisci cartuccia e SSD nel case.'],
  'C':['Il tetto guida anche la parte alta del disco.','Servono una culla e una guida abbinata.']}
 notes={'A':['Sponde spesse 3 mm; guida attiva 32 mm.','Accesso comodo; resta piu leva nella parte alta.'],
  'B':['Cornici collegate alla stessa base larga.','Guida fino in alto; piu superficie coperta.'],
  'C':['Piccole zone guidate sopra e sotto.','Piu pezzi e nuovo aggancio interno al tetto.']}
 for j,option in enumerate(['A','B','C']):
  x=20+j*980;d.text((x+25,170),titles[option],font=font(34,True),fill=INK);textlines(d,(x+25,225),subtitles[option],size=26)
  rows=[row(g.receiver(0),'#87939b'),*loaded(option,'T9',0)]
  im.paste(raw(rows,dict(camera=(-140,-190,155),target=(21,54,41),scale=56),option+'_carico'),(x,310))
  d.text((x+25,1050),'La stessa sede senza SSD',font=font(29,True),fill=INK)
  rows=[row(g.receiver(0),'#87939b'),row(g.carrier(option,'T9',0),ORANGE)]
  if option=='C':rows.append(row(g.upper_guide('T9',0),BLUE))
  im.paste(raw(rows,dict(camera=(-140,-190,155),target=(21,54,41),scale=56),option+'_vuoto'),(x,1100))
  textlines(d,(x+25,1840),notes[option],size=26,color=INK)
 d.text((45,1960),'Studio CAD: contatti e giochi indicativi. Nessuna di queste tre alternative e ancora un kit da stampare.',font=font(28),fill=MUTED)
 im.save(ROOT/'anteprime/01_CONFRONTO_A_B_C.png')
 # Tre sistemi nella stessa scocca, aperta per vedere le parti interne.
 im=Image.new('RGB',(2940,1360),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R23 / dentro il monolite',font=font(46,True),fill=INK)
 d.text((45,95),'Scocca mostrata in sezione, senza tetto · T7 a sinistra, T7 Shield al centro, T9 a destra',font=font(30),fill=MUTED)
 shell=cutaway(g.shell_empty());fixed=g.union([g.receiver(i) for i in range(3)])
 for j,option in enumerate(['A','B','C']):
  x=20+j*980;d.text((x+25,175),titles[option],font=font(34,True),fill=INK)
  rows=[row(shell),row(fixed,'#87939b')]
  for slot,model in enumerate(['T7','T7_Shield','T9']):rows+=loaded(option,model,slot)
  im.paste(raw(rows,dict(camera=(-180,-230,200),target=(45,53,41),scale=73),option+'_case'),(x,250))
 textlines(d,(45,1050),['Tutte le sedi del basamento hanno la stessa interfaccia: scegli la cartuccia del modello e la puoi mettere in qualunque slot.',
  'Le vecchie alette della base sono eliminate. La nuova interfaccia ha appoggi larghi e fermi bassi solidali al basamento.',
  'A e B lasciano invariato il tetto R22; C richiede sviluppare il fissaggio delle guide superiori e raccordare le feritoie.'],size=29,line_height=54)
 d.text((45,1280),'Il CAD controlla ingombri e inserimento nominale; rigidita, giochi reali e dissipazione restano da verificare sul prototipo scelto.',font=font(27),fill=MUTED)
 im.save(ROOT/'anteprime/02_NEL_CASE.png')
 # Sequenza B: mostra esplicitamente il gesto differente, non un inserimento dall'alto impossibile.
 im=Image.new('RGB',(2940,1410),BG);d=ImageDraw.Draw(im)
 d.text((45,25),'R23 / come useresti la soluzione B',font=font(46,True),fill=INK)
 d.text((45,95),'Una cartuccia per disco, aperta davanti e dietro. La porta USB resta accessibile.',font=font(30),fill=MUTED)
 steps=[('1 / SSD dentro la cartuccia',
  [row(g.carrier('B','T9',0),ORANGE),row(g.drive('T9',0,45),'#668ca5')],
  dict(camera=(-145,280,160),target=(21,80,41),scale=78),
  ['Operazione fuori dal case, con cavo scollegato.','Il disco scorre da dietro nelle due cornici.']),
 ('2 / Cartuccia nel basamento',
  [row(g.receiver(0),'#87939b'),row(g.carrier('B','T9',0).translate((0,-6,18)),ORANGE),row(g.drive('T9',0).translate((0,-6,18)),'#668ca5')],
  dict(camera=(-140,-210,165),target=(21,54,48),scale=71),
  ['Cali il gruppo dall’alto con gli inviti allineati.','Poi lo fai arretrare di 6 mm nella propria sede.']),
 ('3 / Appoggio senza stringere l’SSD',
  [row(g.receiver(0),'#87939b'),*loaded('B','T9',0)],
  dict(camera=(-140,-190,155),target=(21,54,41),scale=56),
  ['Si trattiene la base della cartuccia.','Il disco rimane sfilabile dopo averla rimossa.'])]
 for j,(title,rows,view,lines) in enumerate(steps):
  x=20+j*980;d.text((x+25,175),title,font=font(33,True),fill=INK)
  im.paste(raw(rows,view,'B_step'+str(j)),(x,260));textlines(d,(x+25,1060),lines,size=26,color=INK)
 d.text((45,1230),'L’innesto largo sul basamento e comune anche ad A e C. Accoppiamento a cuneo ancora da calibrare; nessuna aletta sottile.',font=font(27),fill=MUTED)
 d.text((45,1290),'Per il disco il gioco iniziale e 0,4 mm totale (0,2 per lato): e un parametro da provare, non la promessa di gioco zero.',font=font(27),fill=MUTED)
 d.text((45,1350),'Cornici chiuse: maggiore controllo geometrico del dondolio; caricamento meno immediato rispetto alla culla aperta A.',font=font(28,True),fill=INK)
 im.save(ROOT/'anteprime/03_USO_SOLUZIONE_B.png')
 g.save(ROOT/'verifiche/anteprime.json',dict(manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),images={str(p.relative_to(ROOT)):g.sha(p) for p in sorted((ROOT/'anteprime').glob('*.png'))},generated_from_cad=True,physical_photos=False))
 print('ANTEPRIME R23 PRONTE',flush=True)
if __name__=='__main__':main()
