"""R18: alette aperte di 0,10 mm, gioco ridotto e braccetti R17 da 3,1 mm."""
from pathlib import Path
import json,hashlib
import cadquery as cq
import trimesh
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'sorgenti/parametri_aggancio_R18.json').read_text())
W=P['larghezza'];TOP=P['quota_tetto'];CY=P['centro_y'];A=P['aletta']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def union(parts):return parts[0].fuse(*parts[1:]).clean()
def profile(points,y,width):
 w=cq.Wire.makePolygon([cq.Vector(x,y,z) for x,z in points],close=True)
 return cq.Solid.extrudeLinear(w,[],cq.Vector(0,width,0))
def bounds(s):
 b=s.BoundingBox();return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]
def mesh_of(s):
 vs,fs=s.tessellate(.035,.08);return trimesh.Trimesh(np.array([v.toTuple() for v in vs]),np.array(fs),process=True)
def latch(v,side='left',inward=0):
 x=P['parete_case']+A['gioco_radice'];yy=CY-A['larghezza']/2
 bias=A['apertura_esterna_punta_mm'];lo=TOP-A['lunghezza'];t=A['spessore']
 finger=profile([(x,TOP),(x+t,TOP),(x+t-bias,lo),(x-bias,lo)],yy,A['larghezza'])
 tip=x-v['lunghezza_braccetto_dal_fianco'];anchor=x+.1;c=v['smusso_naso']
 points=[(anchor,v['quota_rampa_bassa']),(tip+c,v['quota_naso_basso']-c),(tip,v['quota_naso_basso']),
  (tip,v['quota_spalla']-c),(tip+c,v['quota_spalla']),(anchor,v['quota_spalla'])]
 points=[(xx+bias*(zz-TOP)/A['lunghezza'],zz) for xx,zz in points]
 tooth=profile(points,CY-v['larghezza_dente']/2,v['larghezza_dente'])
 result=union([finger,tooth]).translate((inward,0,0))
 return result if side=='left' else result.mirror('YZ',(W/2,0,0))
def roof_spring(side='left',inward=0):
 r=P['scarico_radice'];x=P['parete_case']+A['gioco_radice']
 # La parte prima di Y28 collega la radice alla traversa; tratto libero
 # lungo 18 mm fino all'inizio della paletta verticale a Y46.
 s=box(x+inward,r['y_min']-.2,TOP,A['spessore'],CY+A['larghezza']/2-r['y_min']+.2,P['spessore_tetto'])
 return s if side=='left' else s.mirror('YZ',(W/2,0,0))
def coupon(v,inward=0):
 roof=box(0,P['inizio_traversa_y'],TOP,W,P['profondita_traversa'],P['spessore_tetto'])
 r=P['scarico_radice'];cut=box(r['x_min'],r['y_min'],TOP-.1,r['x_max']-r['x_min'],r['y_max']-r['y_min'],P['spessore_tetto']+.2)
 p=P['apertura_alleggerimento']
 roof=roof.cut(cut,cut.mirror('YZ',(W/2,0,0)),box(p['x'],p['y'],TOP-.1,p['larghezza'],p['profondita'],P['spessore_tetto']+.2),
  box(W/2-.5,49,TOP+2.6,1,4,.6)).clean()
 return union([roof,roof_spring('left',inward),roof_spring('right',inward),latch(v,'left',inward),latch(v,'right',inward)])
def reference_wall(side='left'):
 dy=P['profondita_traversa']+6;yy=P['inizio_traversa_y']-3
 wall=box(0,yy,67,P['parete_case'],dy,TOP-67)
 wall=wall.cut(box(-.1,P['finestra_y_min'],P['finestra_z_min'],P['parete_case']+.2,P['finestra_larghezza_y'],P['finestra_z_max']-P['finestra_z_min'])).clean()
 return wall if side=='left' else wall.mirror('YZ',(W/2,0,0))
