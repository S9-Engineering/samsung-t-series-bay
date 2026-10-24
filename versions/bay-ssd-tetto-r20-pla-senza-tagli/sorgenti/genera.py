"""R20: tetto senza tagli superiori, flessure interne e braccetti R18."""
from pathlib import Path
import json,hashlib
import cadquery as cq
import trimesh
import numpy as np
import agganci_r18 as a
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'sorgenti/parametri.json').read_text());W=P['larghezza'];D=P['profondita'];TOP=P['quota_tetto'];A=a.A
box=a.box;union=a.union;profile=a.profile;bounds=a.bounds;mesh_of=a.mesh_of;sha=a.sha;save=a.save

def vent_holes(z,height):
 v=P['ventilazione'];length=(v['lunghezza_campo']-v['spina'])/2;offset=(length+v['spina'])/2
 return [cq.Workplane('XY').slot2D(length,v['larghezza']).extrude(height).val().translate((W/2+dx,y,z)) for y in v['centri_y'] for dx in (-offset,offset)]

def fixed_lid():
 rear=P['retro_coperchio'];depth=D+rear['arretramento_esterno_mm']
 roof=box(0,0,TOP,W,depth,P['tetto']).cut(*vent_holes(TOP-1,P['tetto']+2)).clean()
 locators=[box(x,3.3,80,8,1.6,3) for x in (19,63)]
 z=rear['quota_inferiore_mm'];t=rear['spessore_mm'];gap=rear['gioco_con_scocca_mm']
 tail=box(0,depth-t,z,W,t,TOP-z)
 cheeks=[box(x,D+gap,z,t,rear['arretramento_esterno_mm']-t-gap,TOP-z) for x in (0,W-t)]
 return union([roof,*locators,tail,*cheeks])

def spring(side='left',inward=0):
 r=P['radice_interna'];shift=r['quota_superiore_mm']-P['tetto']-TOP
 return a.roof_spring(side,inward).translate((0,0,shift))

def latch(side='left',inward=0):
 z=P['radice_interna']['quota_superiore_mm']
 return a.latch(a.P['varianti'][0],side,inward).intersect(box(-10,0,60,W+20,109,z-60)).clean()

def anchor(side='left'):
 r=P['radice_interna'];x=P['parete']+A['gioco_radice'];z=r['quota_superiore_mm']-r['spessore_z_mm']
 s=box(x,r['ancora_y_min_mm'],z,A['spessore'],r['ancora_y_max_mm']-r['ancora_y_min_mm'],TOP-z+.1)
 return s if side=='left' else s.mirror('YZ',(W/2,0,0))

def lid(inward=0):
 return union([fixed_lid(),*[anchor(side) for side in ('left','right')],*[spring(side,inward) for side in ('left','right')],*[latch(side,inward) for side in ('left','right')]])

def reference_shell():return cq.importers.importStep(str(ROOT/'CAD/riferimenti_NON_STAMPARE/scocca_R15_NON_STAMPARE.step')).val()

def drive(model,slot):
 d=P['ssd_nominali'][model];s=P['slot'];cx=s['primo_centro_x']+slot*s['passo']
 z=P['quota_seduta']+(P['supporti_u']['spessore_base_mm'] if model!='T9' else 0)
 return box(cx-d['spessore']/2,s['inizio_ssd_y'],z,d['spessore'],d['lunghezza'],d['altezza'])

def usb_keepout(model,slot):
 d=P['ssd_nominali'][model];s=P['slot'];r=P['retro_coperchio'];cx=s['primo_centro_x']+slot*s['passo']
 z=P['quota_seduta']+(P['supporti_u']['spessore_base_mm'] if model!='T9' else 0)+d['altezza']/2
 return box(cx-r['ingombro_spina_larghezza_mm']/2,s['inizio_ssd_y']+d['lunghezza'],z-r['ingombro_spina_altezza_mm']/2,r['ingombro_spina_larghezza_mm'],r['lunghezza_rigida_cavo_mm'],r['ingombro_spina_altezza_mm'])

def main():
 s=lid();assert s.isValid() and len(s.Solids())==1,(s.isValid(),len(s.Solids()))
 name='TETTO_R20_SENZA_TAGLI';printed=s.rotate((0,0,0),(1,0,0),180);b=printed.BoundingBox();printed=printed.translate((-b.xmin,-b.ymin,-b.zmin))
 step=ROOT/'CAD'/(name+'.step');ps=ROOT/'CAD'/(name+'_STAMPA.step');stl=ROOT/'stampa/STL'/(name+'.stl');ply=ROOT/'verifiche/mesh_assieme'/(name+'.ply')
 cq.exporters.export(s,str(step));cq.exporters.export(printed,str(ps));cq.exporters.export(printed,str(stl),tolerance=.035,angularTolerance=.08);mesh_of(s).export(ply)
 ref=reference_shell();mesh_of(ref).export(ROOT/'verifiche/mesh_assieme/scocca_R15_NON_STAMPARE.ply')
 rows=[dict(name=name,quantity=1,stl=str(stl.relative_to(ROOT)),step=str(step.relative_to(ROOT)),print_step=str(ps.relative_to(ROOT)),mesh=str(ply.relative_to(ROOT)),stl_sha256=sha(stl),step_sha256=sha(step),print_step_sha256=sha(ps),bounds_mm=bounds(s),print_bounds_mm=bounds(printed),volume_mm3=s.Volume())]
 save(ROOT/'verifiche/manifest.json',dict(revision=P['revisione'],unit='millimeter',parameters_sha256=sha(ROOT/'sorgenti/parametri.json'),latch_parameters_sha256=sha(ROOT/'sorgenti/parametri_aggancio_R18.json'),parts=rows,reference_hashes={str(q.relative_to(ROOT)):sha(q) for q in sorted((ROOT/'CAD/riferimenti_NON_STAMPARE').glob('*.step'))},physical_print=False,full_lid_modified=True))
 print(json.dumps(dict(result='ESPORTATO_TETTO_R20',bounds_mm=bounds(s),print_bounds_mm=bounds(printed),volume_mm3=s.Volume())),flush=True)
if __name__=='__main__':main()
