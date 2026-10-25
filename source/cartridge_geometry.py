# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""R24: cartucce B dedicate, interfaccia comune rigida e fermo frontale.

mm. Fronte Y0; USB verso +Y. Le cornici si caricano fuori dal case.
Il tetto e il perno sono geometricamente quelli della R22.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import cadquery as cq
import locking_geometry as r22
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'source/parameters.json').read_text());S=P['cartucce_b']
box=r22.box;union=r22.union;profile=r22.profile;bounds=r22.bounds
mesh_of=r22.mesh_of;save=r22.save;sha=r22.sha
C=r22.C;CX=r22.CX;CY=r22.CY
lid=r22.lid;key=r22.key;closed_key=r22.closed_key
def dims(model):return P['ssd_nominali'][model]
def cx(slot):return S['centri_slot_x_mm'][slot]
def shell_empty():
 b=r22.base;W=P['larghezza'];D=P['profondita'];B=P['base'];TOP=P['quota_tetto']
 s=b.rounded(0,0,0,W,D,TOP,0).cut(b.rounded(3,3,B,W-6,D-6,TOP,1.2))
 s=s.cut(*b.vent_holes(-1,B+1.01),box(3,D-4,B,W-6,6,TOP),*b.side_pattern_holes())
 pads=[b.cylinder(x,y,0,P['piedini']['piazzole_diametro']/2,B) for x,y in P['piedini']['centri_xy']]
 s=union([s,*pads]);s=s.cut(*[b.cylinder(x,y,-.1,P['piedini']['sedi_diametro']/2,P['piedini']['sedi_profondita']+.1) for x,y in P['piedini']['centri_xy']])
 ear=profile(C['supporto_scocca_xz'],88.8,12.2).cut(r22.slot(50,33,C['foro_xy_mm']))
 return union([s,*b.logo_relief_shapes(),*r22.rails('scocca'),ear])
def receiver(slot):
 c=cx(slot);half=S['base_larghezza_mm']/2;gx=S['gioco_piede_x_per_lato_mm'];edge=half+gx
 s=box(c-13.4,14.8,5,26.8,79.2,7.9)
 s=s.cut(box(c-edge,14.7,10,2*edge,77.5,6),box(c-edge,40,4.9,2*edge,36,5.2),
         box(c-edge,14.7,4.9,2*edge,13.3,5.2),box(c-edge,88,4.9,2*edge,4.2,5.2))
 # Fermi corti spessi 3 mm: sottosquadro a 45 gradi, non alette flessibili.
 # Foot top Z13; diag distance is .2 mm vertically, about .141 normal.
 lips=[];bevel=S['smusso_piede_mm'];gz=S['gioco_guide_z_mm'];inner=half-bevel
 for y in [52,64]:
  left=[(c-13.4,11.0),(c-edge,11.0),(c-edge,13-bevel+gz-gx),
        (c-inner,13+gz),(c-inner,15.6),(c-13.4,15.6)]
  lip=profile(left,y,4);lips.extend([lip,lip.mirror('YZ',(c,0,0))])
 return union([s,*lips])
def shell():
 # Appoggi sotto le fasce portanti: spezzano le campate sulle prese inferiori.
 # Costole 2.4 mm x 12 mm, distanti 14 mm, senza chiudere le finestre centrali.
 ribs=[box(cx(i)+dx-1.2,y-6,0,2.4,12,5.1) for i in range(3) for dx in [-7,7] for y in S['centri_collari_y_mm']]
 s=union([shell_empty(),*[receiver(i) for i in range(3)],*ribs])
 b=r22.base
 return s.cut(*[b.cylinder(x,y,-.1,P['piedini']['sedi_diametro']/2,P['piedini']['sedi_profondita']+.1) for x,y in P['piedini']['centri_xy']]).clean()

def foot(model,slot=0):
 c=cx(slot);half=S['base_larghezza_mm']/2;bevel=S['smusso_piede_mm']
 s=box(c-half,24,10,2*half,68,3).cut(box(c-5,40,9.9,10,36,3.2))
 # Smusso continuo del piede: superfici di appoggio larghe, senza cunei forzati.
 for pts in [[(c-half-.1,13-bevel),(c-half,13-bevel),(c-half+bevel,13),(c-half+bevel,13.1),(c-half-.1,13.1)],
             [(c+half,13-bevel),(c+half+.1,13-bevel),(c+half+.1,13.1),(c+half-bevel,13.1),(c+half-bevel,13)]]:
  s=s.cut(profile(pts,23.9,68.2))
 for y in [57.8,69.8]:
  for x in [c-half-.1,c+half-bevel-.1]:s=s.cut(box(x,y,9.9,bevel+.2,4.4,3.6))
 width=dims(model)['spessore']+S['gioco_ssd_totale_x_mm']
 tongue=box(c-4.5,15.7,10,9,8.4,3)
 stop=box(c-width/2-2,14.3,10,width+4,1.5,9)
 return union([s,tongue,stop])
def aperture_wire(c,y,w,z,h):
 return cq.Wire.makePolygon([cq.Vector(x,y,zz) for x,zz in [(c-w/2,z),(c+w/2,z),(c+w/2,z+h),(c-w/2,z+h)]],close=True)
def ring(model,slot=0,cy=34,depth=None):
 c=cx(slot);d=dims(model);w=d['spessore']+S['gioco_ssd_totale_x_mm'];h=d['altezza'];t=S['B_spessore_cornice_mm']
 depth=depth or S['profondita_collare_mm'];y=cy-depth/2;ap_h=h+S['gioco_ssd_alto_mm'];top=13+ap_h+S['B_spessore_ponte_alto_mm']
 s=box(c-w/2-t,y,10,w+2*t,depth,top-10).cut(box(c-w/2,y-.1,13,w,depth+.2,ap_h))
 # Invito di .6 mm a entrambe le bocche; la parte centrale mantiene la quota.
 lead=S['invito_ssd_mm']
 for mouth,inside in [(y,y+lead),(y+depth,y+depth-lead)]:
  cut=cq.Solid.makeLoft([aperture_wire(c,mouth,w+2*lead,13-lead,ap_h+2*lead),aperture_wire(c,inside,w,13,ap_h)],True)
  s=s.cut(cut)
 z=S['B_smusso_inizio_z_mm'];ins=S['B_smusso_esterno_alto_mm'];left=c-w/2-t;right=c+w/2+t
 for pts in [[(left-.1,z),(left,z),(left+ins,z+ins),(left+ins,top+.1),(left-.1,top+.1)],
             [(right,z),(right+.1,z),(right+.1,top+.1),(right-ins,top+.1),(right-ins,z+ins)]]:s=s.cut(profile(pts,y-.1,depth+.2))
 return s.clean()
def carrier(model,slot=0):return union([foot(model,slot),*[ring(model,slot,y) for y in S['centri_collari_y_mm']]])
def front_lock(slots=(0,1,2)):
 # Un solo fermo appoggiato sul fondo e contro il fronte del case.
 # Il naso finisce a Y14.1, .2 davanti alla battuta della cartuccia.
 f=S['fermo_frontale'];x0=cx(min(slots))-f['larghezza_naso_mm']/2;x1=cx(max(slots))+f['larghezza_naso_mm']/2
 y0=3+f['gioco_frontale_mm'];y1=14.3-f['gioco_dietro_mm'];z=f['quota_base_mm'];h=f['quota_alta_mm']-z
 parts=[box(x0,y0,z,x1-x0,f['spessore_traversa_mm'],h)]
 for i in slots:parts.append(box(cx(i)-4.5,y0,z,9,y1-y0,10))
 # Presa in alto soltanto sul fermo comune; il provino basso prova le battute.
 if len(slots)>1:
  center=(cx(min(slots))+cx(max(slots)))/2;top=f['quota_presa_mm'];rear=y0+f['spessore_traversa_mm']
  parts.append(box(center-10,y0,20,20,f['spessore_traversa_mm'],top-20))
  wire=cq.Wire.makePolygon([cq.Vector(center-10,y,z) for y,z in [(rear-.1,top-8),(rear+5,top-2.9),(rear+5,top),(rear-.1,top)]],close=True)
  parts.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(20,0,0)))
 return union(parts)
def drive(model,slot=0):
 d=dims(model);return box(cx(slot)-d['spessore']/2,16,13,d['spessore'],d['lunghezza'],d['altezza'])
def usb_keepout(model,slot=0):
 d=dims(model);return box(cx(slot)-10,16+d['lunghezza'],13+d['altezza']/2-10,20,50,20)
def coupon_base():
 c=cx(0)
 floor=box(c-15,0,2,30,96,3);front=box(c-15,0,2,30,3,20)
 return union([floor,front,receiver(0)])
def coupon_foot():
 f=foot('T9',0)
 # Presa bassa centrale, non rappresenta una cornice SSD.
 return union([f,box(cx(0)-3,29,12.9,6,8,9.1)])
def oriented(s,mode):return r22.oriented(s,mode)
