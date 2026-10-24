"""R16: tre traverse diagnostiche da provare sulla scocca esistente."""
from pathlib import Path
import json,hashlib
import cadquery as cq
import trimesh
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'sorgenti/parametri.json').read_text())
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
 finger=box(x,yy,TOP-A['lunghezza'],A['spessore'],A['larghezza'],A['lunghezza'])
 tip=P['parete_case']-v['sporgenza_nominale'];anchor=x+.1
 if v['tipo']=='triangolo':points=[(anchor,72),(tip,73),(anchor,74)]
 else:points=[(anchor,v['quota_rampa_bassa']),(tip,v['quota_naso_basso']),(tip,v['quota_spalla']),(anchor,v['quota_spalla'])]
 tooth=profile(points,yy,A['larghezza'])
 low,high,r=A['pattino_z_min'],A['pattino_z_max'],A['pattino_rampa'];reach=P['parete_case']-A['precarico_per_lato']
 pad=profile([(anchor,low),(reach,low+r),(reach,high-r),(anchor,high)],yy,A['larghezza'])
 result=union([finger,tooth,pad]).translate((inward,0,0))
 return result if side=='left' else result.mirror('YZ',(W/2,0,0))
def coupon(v,inward=0):
 dy=P['profondita_traversa'];roof=box(0,CY-dy/2,TOP,W,dy,P['spessore_tetto'])
 # I, II, III: tacche incise sulla faccia esterna, senza isole nei caratteri.
 n=len(v['id']);marks=[box(W/2+(i-(n-1)/2)*2.5-.5,CY-2,TOP+2.6,1,4,.6) for i in range(n)]
 roof=roof.cut(*marks).clean()
 return union([roof,latch(v,'left',inward),latch(v,'right',inward)])
def reference_wall(side='left'):
 dy=P['profondita_traversa']+6;yy=CY-dy/2
 wall=box(0,yy,67,P['parete_case'],dy,TOP-67)
 wall=wall.cut(box(-.1,P['finestra_y_min'],P['finestra_z_min'],P['parete_case']+.2,P['finestra_larghezza_y'],P['finestra_z_max']-P['finestra_z_min'])).clean()
 return wall if side=='left' else wall.mirror('YZ',(W/2,0,0))
def main():
 rows=[]
 for v in P['varianti']:
  name='PROVINO_'+v['id']+'_R16';s=coupon(v)
  assert s.isValid() and len(s.Solids())==1
  printed=s.rotate((0,0,0),(1,0,0),180);b=printed.BoundingBox();printed=printed.translate((-b.xmin,-b.ymin,-b.zmin))
  step=ROOT/'CAD'/(name+'.step');stl=ROOT/'stampa/STL'/(name+'.stl');orient=ROOT/'CAD'/(name+'_STAMPA.step');ply=ROOT/'verifiche/mesh_assieme'/(name+'.ply')
  cq.exporters.export(s,str(step));cq.exporters.export(printed,str(orient));cq.exporters.export(printed,str(stl),tolerance=.035,angularTolerance=.08);mesh_of(s).export(ply)
  rows.append(dict(name=name,variant=v,quantity=1,stl=str(stl.relative_to(ROOT)),step=str(step.relative_to(ROOT)),print_step=str(orient.relative_to(ROOT)),mesh=str(ply.relative_to(ROOT)),stl_sha256=sha(stl),step_sha256=sha(step),bounds_mm=bounds(s),print_bounds_mm=bounds(printed),volume_mm3=s.Volume()))
 for side in ('left','right'):cq.exporters.export(reference_wall(side),str(ROOT/'CAD'/('RIFERIMENTO_PARETE_'+side+'_NON_STAMPARE.step')))
 save(ROOT/'verifiche/manifest.json',dict(revision='R16_PROVINI',unit='millimeter',parameters_sha256=sha(ROOT/'sorgenti/parametri.json'),parts=rows,physical_print=False))
 print('ESPORTATI TRE PROVINI',flush=True)
if __name__=='__main__':main()
