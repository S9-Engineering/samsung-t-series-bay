"""R21: supporti rigidi e due perni rimovibili a quarto di giro; nessun braccio elastico."""
from pathlib import Path
import json,hashlib
import cadquery as cq
import numpy as np
import trimesh
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
ROOT=Path(__file__).resolve().parents[1];P=json.loads((ROOT/'sorgenti/parametri.json').read_text())
W=P['larghezza'];D=P['profondita'];TOP=P['quota_tetto'];C=P['chiusura'];CY=C['asse_y_mm'];CZ=C['asse_z_mm']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def union(parts):return parts[0].fuse(*parts[1:]).clean() if len(parts)>1 else parts[0]
def bounds(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);q=b.Get();return [list(q[:3]),list(q[3:])]
def mesh_of(s):
 v,f=s.tessellate(.035,.08);return trimesh.Trimesh(np.array([q.toTuple() for q in v]),np.array(f),process=True)
def round_xy(x,y,z,dx,dy,dz,r):return cq.Workplane('XY').box(dx,dy,dz,centered=False).edges('|Z').fillet(r).val().translate((x,y,z))
def cylinder_x(x,y,z,r,length):return cq.Solid.makeCylinder(r,length,cq.Vector(x,y,z),cq.Vector(1,0,0))
def mirror(s,side):return s if side=='left' else s.mirror('YZ',(W/2,0,0))
def vent_holes(z,height):
 v=P['ventilazione'];out=[]
 for y in v['centri_y']:
  edge=P['venti_due_righe_bordo_mm'] if min(abs(y-45.7),abs(y-55.3))<.01 else (W-v['lunghezza_campo'])/2
  length=W/2-v['spina']/2-edge
  for center in ((edge+W/2-v['spina']/2)/2,W-(edge+W/2-v['spina']/2)/2):
   out.append(cq.Workplane('XY').slot2D(length,v['larghezza']).extrude(height).val().translate((center,y,z)))
 return out

def receiver(side='left'):
 lo=C['blocco_x_min_mm'];hi=C['blocco_x_max_mm'];y=C['blocco_y_min_mm'];z=C['blocco_z_min_mm']
 s=box(lo,y,z,hi-lo,C['blocco_y_max_mm']-y,TOP-z+.1)
 circle=cylinder_x(lo-.1,CY,CZ,C['foro_diametro_mm']/2,hi-lo+.2)
 slot=box(lo-.1,CY-C['foro_asola_larghezza_mm']/2,CZ-C['foro_asola_altezza_mm']/2,hi-lo+.2,C['foro_asola_larghezza_mm'],C['foro_asola_altezza_mm'])
 return mirror(s.cut(circle,slot).clean(),side)

def lid():
 rear=P['retro_coperchio'];depth=D+rear['arretramento_esterno_mm']
 roof=box(0,0,TOP,W,depth,P['tetto']).cut(*vent_holes(TOP-1,P['tetto']+2)).clean()
 loc=[box(x,3.3,80,8,1.6,3) for x in (19,63)]
 z=rear['quota_inferiore_mm'];t=rear['spessore_mm'];gap=rear['gioco_con_scocca_mm']
 tail=box(0,depth-t,z,W,t,TOP-z);cheeks=[box(x,D+gap,z,t,rear['arretramento_esterno_mm']-t-gap,TOP-z) for x in (0,W-t)]
 return union([roof,*loc,tail,*cheeks,receiver(),receiver('right')])

def key(side='left',angle=0,insertion=0):
 floor=CZ+C['perno_piano_inferiore_mm'];thick=C['aletta_baionetta_spessore_mm']
 head=round_xy(C['impugnatura_x_min_mm'],CY-C['impugnatura_larghezza_mm']/2,floor,C['impugnatura_x_max_mm']-C['impugnatura_x_min_mm'],C['impugnatura_larghezza_mm'],thick,.55)
 shaft=cylinder_x(-.5,CY,CZ,C['perno_diametro_mm']/2,11.0).intersect(box(-1,CY-3,floor,12,6,5))
 wing=round_xy(C['aletta_baionetta_x_inizio_mm'],CY-C['aletta_baionetta_larghezza_mm']/2,floor,C['aletta_baionetta_x_fine_mm']-C['aletta_baionetta_x_inizio_mm'],C['aletta_baionetta_larghezza_mm'],thick,.25)
 s=union([head,shaft,wing]).rotate((-20,CY,CZ),(20,CY,CZ),angle).translate((-insertion,0,0))
 return mirror(s,side)

def coupon():
 roof=box(0,40,TOP,W,21,3).cut(box(14,43,TOP-.1,62,15,3.2)).clean()
 return union([roof,receiver(),receiver('right')])

def reference_shell():return cq.importers.importStep(str(ROOT/'CAD/riferimenti_NON_STAMPARE/scocca_R15_NON_STAMPARE.step')).val()
def drive(model,slot):
 d=P['ssd_nominali'][model];s=P['slot'];cx=s['primo_centro_x']+slot*s['passo'];z=P['quota_seduta']+(P['supporti_u']['spessore_base_mm'] if model!='T9' else 0)
 return box(cx-d['spessore']/2,s['inizio_ssd_y'],z,d['spessore'],d['lunghezza'],d['altezza'])
def usb_keepout(model,slot):
 d=P['ssd_nominali'][model];s=P['slot'];r=P['retro_coperchio'];cx=s['primo_centro_x']+slot*s['passo'];z=P['quota_seduta']+(P['supporti_u']['spessore_base_mm'] if model!='T9' else 0)+d['altezza']/2
 return box(cx-r['ingombro_spina_larghezza_mm']/2,s['inizio_ssd_y']+d['lunghezza'],z-r['ingombro_spina_altezza_mm']/2,r['ingombro_spina_larghezza_mm'],r['lunghezza_rigida_cavo_mm'],r['ingombro_spina_altezza_mm'])
def main():
 rows=[]
 for name,s,qty,flip,role in [('TETTO_R21_BAIONETTA',lid(),1,True,'TETTO'),('PERNO_R21_QUARTO_GIRO',key(),2,False,'ENTRAMBI'),('PROVINO_R21_BAIONETTA',coupon(),1,True,'PROVA')]:
  assert s.isValid() and len(s.Solids())==1,(name,len(s.Solids()))
  printed=s.rotate((0,0,0),(1,0,0),180) if flip else s;b=np.array(bounds(printed));printed=printed.translate(tuple(-b[0]))
  step=ROOT/'CAD'/(name+'.step');ps=ROOT/'CAD'/(name+'_STAMPA.step');stl=ROOT/'stampa/STL'/(name+'.stl');ply=ROOT/'verifiche/mesh_assieme'/(name+'.ply')
  cq.exporters.export(s,str(step));cq.exporters.export(printed,str(ps));cq.exporters.export(printed,str(stl),tolerance=.035,angularTolerance=.08);mesh_of(s).export(ply)
  rows.append(dict(name=name,quantity=qty,role=role,stl=str(stl.relative_to(ROOT)),step=str(step.relative_to(ROOT)),print_step=str(ps.relative_to(ROOT)),mesh=str(ply.relative_to(ROOT)),stl_sha256=sha(stl),step_sha256=sha(step),print_step_sha256=sha(ps),bounds_mm=bounds(s),print_bounds_mm=bounds(printed),volume_mm3=s.Volume()))
 mesh_of(reference_shell()).export(ROOT/'verifiche/mesh_assieme/scocca_R15_NON_STAMPARE.ply')
 save(ROOT/'verifiche/manifest.json',dict(revision=P['revisione'],unit='millimeter',parameters_sha256=sha(ROOT/'sorgenti/parametri.json'),parts=rows,physical_print=False,elastic_latch=False,complete_kit_parts=3))
 print(json.dumps(dict(parts=[dict(name=q['name'],bounds=q['print_bounds_mm']) for q in rows])),flush=True)
if __name__=='__main__':main()
