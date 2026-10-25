# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""R22: scorrimento su guide interne e singolo fermo rigido nascosto.

Coordinate d'assieme in mm: fronte Y0, retro Y101, tetto Z83.
Il perno si inserisce lungo Z, ruota nel piano XY e scende in una sede
trasversale: il fermo angolare non richiede molle o deformazione.
"""
from pathlib import Path
import json,hashlib
import cadquery as cq
import numpy as np
import trimesh
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
import shell_geometry as base
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'source/parameters.json').read_text())
W=P['larghezza'];D=P['profondita'];TOP=P['quota_tetto']
G=P['guide_scorrevoli'];C=P['fermo_nascosto'];CX=C['asse_x_mm'];CY=C['asse_y_mm']
box=base.box;union=base.union;profile=base.profile
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def bounds(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);q=b.Get();return [list(q[:3]),list(q[3:])]
def mesh_of(s):
 v,f=s.tessellate(.035,.08);return trimesh.Trimesh(np.array([q.toTuple() for q in v]),np.array(f),process=True)
def mirrored(s):return s.mirror('YZ',(W/2,0,0))
def slot(z,h,xy):return box(CX-xy[0]/2,CY-xy[1]/2,z,*xy,h)
def rails(which):
 points=G['profilo_scocca_xz']
 if which=='tetto':
  (x0,z0),(x1,z1)=points[:2];slope=(z1-z0)/(x1-x0)
  tip=3+G['gioco_x_mm'];root=x1+G['gioco_x_mm'];outside=root+G['spessore_radice_tetto_mm']
  diag=lambda x:z0+slope*(x-x0)-G['gioco_z_sotto_diagonale_mm']
  floor=diag(tip)-G['spessore_punta_tetto_mm']
  points=[(tip,floor),(outside,floor),(outside,TOP+.1),(root,TOP+.1),(root,diag(root)),(tip,diag(tip))]
 s=profile(points,G['inizio_y_mm'],G['fine_y_mm']-G['inizio_y_mm'])
 return [s,mirrored(s)]
def shell():
 # La scocca conserva tutte le geometrie approvate R15; chiude solo i vecchi fori dei ganci.
 s=base.shell()
 fills=[box(x,45.7,71,3,9.6,3) for x in (0,W-3)]
 ear=profile(C['supporto_scocca_xz'],C['supporto_scocca_y_mm'][0],C['supporto_scocca_y_mm'][1]-C['supporto_scocca_y_mm'][0])
 ear=ear.cut(slot(50,33,C['foro_xy_mm'])).clean()
 return union([s,*fills,*rails('scocca'),ear])
def receiver():
 # Finestra aperta sui due lati: ponti brevi, controllabili e senza supporti intrappolati.
 s=box(*C['supporto_tetto_box_mm']).cut(box(*C['camera_box_mm']))
 s=s.cut(slot(70.9,4.4,C['foro_xy_mm']),slot(C['sede_bloccaggio_z_mm'],1.0,C['sede_bloccaggio_xy_mm']))
 return s.clean()
def vents():
 v=P['ventilazione'];edge=G['margine_feritoie_top_mm'];length=W/2-v['spina']/2-edge
 return [cq.Workplane('XY').slot2D(length,v['larghezza']).extrude(5).val().translate((x,y,TOP-1))
         for y in v['centri_y'] for x in [(edge+W/2-v['spina']/2)/2,W-(edge+W/2-v['spina']/2)/2]]
def lid():
 rear=P['retro_coperchio'];depth=D+rear['arretramento_esterno_mm'];z=rear['quota_inferiore_mm'];t=rear['spessore_mm'];gap=rear['gioco_con_scocca_mm']
 roof=box(0,0,TOP,W,depth,P['tetto']).cut(*vents()).clean()
 loc=[box(x,3.3,80,8,1.6,3.1) for x in (19,63)]
 tail=box(0,depth-t,z,W,t,TOP-z+.1)
 cheeks=[box(x,D+gap,z,t,rear['arretramento_esterno_mm']-t-gap,TOP-z+.1) for x in (0,W-t)]
 return union([roof,tail,*cheeks,*loc,*rails('tetto'),receiver()])
def key(angle=0,dz=0):
 floor=CY+C['perno_piano_y_mm'];z0,z1=C['perno_z_mm']
 shaft=cq.Solid.makeCylinder(C['perno_diametro_mm']/2,z1-z0,cq.Vector(CX,CY,z0))
 shaft=shaft.intersect(box(CX-3,floor,z0,6,6,z1-z0))
 parts=[shaft]
 for prefix in ['traversino','impugnatura']:
  dx,dy=C[prefix+'_xy_mm'];lo,hi=C[prefix+'_z_mm']
  parts.append(box(CX-dx/2,floor,lo,dx,dy,hi-lo))
 return union(parts).rotate((CX,CY,0),(CX,CY,100),angle).translate((0,0,dz))
def closed_key():return key(90,-C['abbassamento_chiuso_mm'])
def coupon_body(s=None):
 s=s if s is not None else shell();y=G['provino_inizio_y_mm'];z=G['provino_base_z_mm']
 cropped=s.intersect(box(-1,y,z,W+2,40,30))
 return union([cropped,box(0,y,z,W,3,3)])
def coupon_lid(s=None):
 s=s if s is not None else lid();y=G['provino_inizio_y_mm']
 cropped=s.intersect(box(-1,y,50,W+2,42,40))
 # Alleggerimenti lontani da guide, ricevitore e coda davanti al comando.
 return cropped.cut(box(15,y+4,82.9,60,104-y-4,3.2),box(16,101.2,56.9,68,8,22.6)).clean()
def drive(model,slot):return base.drive(model,slot)
def usb_keepout(model,slot):return base.usb_keepout(model,slot)
def adapter(model,y=36,slot=0):return base.adapter(model,y,slot)
def oriented(s,mode):
 if mode=='flip':s=s.rotate((0,0,0),(1,0,0),180)
 if mode=='key':s=s.rotate((0,0,0),(1,0,0),90)
 b=np.array(bounds(s));return s.translate(tuple(-b[0]))
