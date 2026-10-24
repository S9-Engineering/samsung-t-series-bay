"""R23: tre concetti parametrici per confronto, NON file di stampa.

A = culla aperta alta; B = cartuccia a due cornici chiuse;
C = culla bassa e guida alta separata. Base comune con appoggi ampi,
ingresso verticale avanzato di 6 mm e breve traslazione di assestamento.
L'interfaccia a cuneo e le tolleranze vanno sviluppate dopo la scelta.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import cadquery as cq
import trimesh
import involucro_r22 as r22
ROOT=Path(__file__).resolve().parents[1];P=json.loads((ROOT/'sorgenti/parametri.json').read_text());S=P['studio_sedi']
box=r22.box;union=r22.union;bounds=r22.bounds;mesh_of=r22.mesh_of;save=r22.save;sha=r22.sha
def dims(model):return P['ssd_nominali'][model]
def cx(slot):return S['centri_slot_x_mm'][slot]
def profile_yz(points,x,dx):
 w=cq.Wire.makePolygon([cq.Vector(x,y,z) for y,z in points],close=True)
 return cq.Solid.extrudeLinear(w,[],cq.Vector(dx,0,0))
def shell_empty():
 b=r22.base;W=P['larghezza'];D=P['profondita'];B=P['base'];TOP=P['quota_tetto']
 s=b.rounded(0,0,0,W,D,TOP,0).cut(b.rounded(3,3,B,W-6,D-6,TOP,1.2))
 s=s.cut(*b.vent_holes(-1,B+1.01),box(3,D-4,B,W-6,6,TOP),*b.side_pattern_holes())
 pads=[b.cylinder(x,y,0,P['piedini']['piazzole_diametro']/2,B) for x,y in P['piedini']['centri_xy']]
 s=union([s,*pads]);s=s.cut(*[b.cylinder(x,y,-.1,P['piedini']['sedi_diametro']/2,P['piedini']['sedi_profondita']+.1) for x,y in P['piedini']['centri_xy']])
 ear=r22.profile(r22.C['supporto_scocca_xz'],88.8,12.2).cut(r22.slot(50,33,r22.C['foro_xy_mm']))
 return union([s,*b.logo_relief_shapes(),*r22.rails('scocca'),ear])
def receiver(slot):
 # Pareti di localizzazione basse e solidali al basamento, non alette alte libere.
 c=cx(slot);s=box(c-13.6,14.8,5,27.2,79.2,7.9)
 s=s.cut(box(c-10.6,14.7,10,21.2,77.5,6),box(c-10.6,40,4.9,21.2,36,5.2),
         box(c-10.6,14.7,4.9,21.2,13.3,5.2),box(c-10.6,88,4.9,21.2,4.2,5.2))
 lips=[]
 for y in [52,64]:
  for x in [c-13.6,c+10.6]:lips.append(box(x,y,12.8,3,4,2.7))
  for x in [c-10.6,c+8.9]:
   lips.append(profile_yz([(y,13.3),(y+4,13.05),(y+4,15.5),(y,15.5)],x,1.7))
 return union([s,*lips])
def foot(model,slot):
 c=cx(slot);s=box(c-10.4,24,10,20.8,68,3)
 s=s.cut(box(c-5,40,9.9,10,36,3.2))
 # Intagli d'ingresso: al primo appoggio la culla e 6 mm piu avanti.
 for y in [57.8,69.8]:
  for x in [c-10.5,c+8.8]:s=s.cut(box(x,y,9.9,1.7,4.4,3.6))
 ramps=[]
 for y in [52,64]:
  for x in [c-10.4,c+8.9]:ramps.append(profile_yz([(y,12.95),(y+4,12.95),(y+4,13.05),(y,13.3)],x,1.5))
 # Bassa battuta frontale; la porta USB resta libera dietro.
 width=dims(model)['spessore']+S['gioco_ssd_totale_x_mm']
 tongue=box(c-4.5,15.7,10,9,8.4,3)
 stop=box(c-width/2-2,14.3,10,width+4,1.5,9)
 return union([s,*ramps,tongue,stop])
def open_cradle(model,slot,height):
 c=cx(slot);w=dims(model)['spessore']+S['gioco_ssd_totale_x_mm'];t=S['A_spessore_sponde_mm'];parts=[foot(model,slot)]
 for cy in S['centri_collari_y_mm']:
  y=cy-6;parts.append(box(c-w/2-t,y,10,w+2*t,12,3))
  for side in [-1,1]:
   x=c-w/2-t if side<0 else c+w/2
   top=13+height+S['A_invito_alto_mm'];wall=box(x,y,12.9,t,12,top-12.9)
   edge=c-w/2 if side<0 else c+w/2
   cut=[(edge,top-2),(edge,top+.1),(edge+side,top+.1)]
   wall=wall.cut(r22.profile(cut,y-.1,12.2));parts.append(wall)
   # Due allargamenti di radice, esterni alla superficie di guida.
   if side<0:points=[(x-1.0,13),(x+1,13),(x+1,21),(x,21)]
   else:points=[(x+t-1,13),(x+t+1.0,13),(x+t,21),(x+t-1,21)]
   parts.append(r22.profile(points,y,12))
 return union(parts)
def carrier(option,model,slot=0):
 if option=='A':return open_cradle(model,slot,S['A_altezza_guida_attiva_mm'])
 if option=='C':return open_cradle(model,slot,S['C_altezza_guida_bassa_mm'])
 c=cx(slot);d=dims(model);w=d['spessore']+S['gioco_ssd_totale_x_mm'];h=d['altezza'];t=S['B_spessore_cornice_mm'];parts=[foot(model,slot)]
 for cy in S['centri_collari_y_mm']:
  outer=box(c-w/2-t,cy-6,10,w+2*t,12,3+h+S['gioco_ssd_alto_mm']+S['B_spessore_ponte_alto_mm'])
  aperture=box(c-w/2,cy-6.1,13,w,12.2,h+S['gioco_ssd_alto_mm'])
  ring=outer.cut(aperture)
  # Sponde da 3 mm. Solo gli angoli esterni in alto rientrano per lasciare
  # libere le guide del tetto R22, senza ridurre il canale interno del disco.
  z=gz=S['B_smusso_inizio_z_mm'];top=13+h+S['gioco_ssd_alto_mm']+S['B_spessore_ponte_alto_mm'];inset=S['B_smusso_esterno_alto_mm']
  left=c-w/2-t;right=c+w/2+t
  for pts in [[(left-.1,z),(left,z),(left+inset,z+inset),(left+inset,top+.1),(left-.1,top+.1)],
              [(right,z),(right+.1,z),(right+.1,top+.1),(right-inset,top+.1),(right-inset,z+inset)]]:
   ring=ring.cut(r22.profile(pts,cy-6.1,12.2))
  parts.append(ring)
 return union(parts)
def upper_guide(model,slot=0):
 d=dims(model);c=cx(slot);w=d['spessore']+S['gioco_ssd_totale_x_mm'];top=13+d['altezza'];y=S['C_guida_superiore_y_mm']-4;lo=top-S['C_presa_superiore_mm']
 outer=box(c-9.2,y,lo,18.4,8,83-lo)
 opening=box(c-w/2,y-.1,lo-.1,w,8.2,top+S['gioco_ssd_alto_mm']-lo+.1)
 return outer.cut(opening).clean()
def drive(model,slot=0,dy=0):
 d=dims(model);return box(cx(slot)-d['spessore']/2,16+dy,13,d['spessore'],d['lunghezza'],d['altezza'])
def usb(model,slot=0):
 d=dims(model);return box(cx(slot)-10,16+d['lunghezza'],13+d['altezza']/2-10,20,50,20)
def main():
 records=[]
 def export(name,shape,kind,**extra):
  assert shape.isValid() and len(shape.Solids())==1,(name,len(shape.Solids()))
  p=ROOT/'CAD_STUDIO_NON_STAMPARE'/(name+'.step');cq.exporters.export(shape,str(p))
  m=ROOT/'verifiche'/(name+'.ply');mesh_of(shape).export(m)
  rec=dict(name=name,kind=kind,step=str(p.relative_to(ROOT)),sha256=sha(p),mesh=str(m.relative_to(ROOT)),mesh_sha256=sha(m),bounds_mm=bounds(shape),volume_mm3=shape.Volume(),**extra);records.append(rec)
  return shape
 shell=export('INVOLUCRO_R23_SENZA_VECCHIE_ALETTE',shell_empty(),'involucro')
 roof=export('TETTO_R22_RIFERIMENTO',r22.lid(),'tetto_riferimento')
 fixed=union([receiver(i) for i in range(3)]);export('BASAMENTO_COMUNE_R23',fixed,'basamento')
 for option in ['A','B','C']:
  for model in P['ssd_nominali']:
   export(option+'_'+model,carrier(option,model),'culla',option=option,model=model)
   if option=='C':export('C_GUIDA_ALTA_'+model,upper_guide(model),'guida_alta',option=option,model=model)
  assy=cq.Assembly(name='R23_'+option+'_STUDIO_NON_STAMPARE')
  assy.add(shell,name='involucro',color=cq.Color('#30363c'));assy.add(fixed,name='basamento_indicativo',color=cq.Color('#6f7f8d'))
  for i,model in enumerate(['T7','T7_Shield','T9']):
   assy.add(carrier(option,model,i),name='culla_'+model,color=cq.Color('#bd8742'));assy.add(drive(model,i),name='SSD_'+model,color=cq.Color(P['colori'][model]))
   if option=='C':assy.add(upper_guide(model,i),name='guida_alta_'+model,color=cq.Color('#668ca5'))
  assy.save(str(ROOT/'CAD_STUDIO_NON_STAMPARE'/('ASSIEME_'+option+'_NON_STAMPARE.step')))
 save(ROOT/'verifiche/manifest.json',dict(revision=P['revisione'],state='STUDIO_COMPARATIVO_NON_STAMPARE',parameters_sha256=sha(ROOT/'sorgenti/parametri.json'),source_sha256=sha(ROOT/'sorgenti/genera.py'),parts=records,complete_print_kit=False,dimensions_are_nominal=True,physical_test=False,sliced=False,old_fins_retained=False,hardware_bom={},material='ELEGOO PLA BASIC'))
 print(json.dumps(dict(parts=len(records),state='STUDIO_COMPARATIVO_NON_STAMPARE')),flush=True)
if __name__=='__main__':main()
