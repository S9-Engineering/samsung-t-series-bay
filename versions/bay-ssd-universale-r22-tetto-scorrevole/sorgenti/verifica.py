"""Riapertura degli export, controllo delle guide e della chiusura rigida R22."""
import json
import numpy as np
import cadquery as cq
import trimesh
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT
def vol(s):return sum(q.Volume() for q in s.Solids())
def overlap(a,b):return vol(a.intersect(b))
def diff(a,b):return vol(a.cut(b))+vol(b.cut(a))
def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());assert m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 records=[];shapes={}
 for p in m['parts']:
  s=cq.importers.importStep(str(ROOT/p['step'])).val();ps=cq.importers.importStep(str(ROOT/p['print_step'])).val();mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
  assert s.isValid() and ps.isValid() and len(s.Solids())==len(ps.Solids())==len(mesh.split())==1
  assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
  assert not np.any(mesh.area_faces<1e-10) and len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
  inter=self_intersections_fast(mesh);assert inter['intersection_pairs']==0,(p['name'],inter)
  assert np.allclose(mesh.bounds,g.bounds(ps),atol=.04) and abs(mesh.volume/s.Volume()-1)<.005
  assert abs(mesh.bounds[0]).max()<1e-4
  shapes[p['name']]=s;records.append(dict(name=p['name'],closed=True,components=1,winding=True,positive_volume=True,degenerate_faces=0,duplicate_faces=0,self_intersections=inter,stl_sha256=g.sha(ROOT/p['stl']),step_sha256=g.sha(ROOT/p['step']),print_step_sha256=g.sha(ROOT/p['print_step']),print_bounds_mm=mesh.bounds.tolist(),volume_mm3=float(mesh.volume)))
  print('EXPORT VERIFICATO',p['name'],flush=True)
 shell=shapes['SCOCCA_R22'];roof=shapes['TETTO_R22_SCORREVOLE'];cb=shapes['PROVINO_SCOCCA_R22'];ct=shapes['PROVINO_TETTO_R22']
 assert diff(roof,g.lid())<1e-5 and diff(shapes['PERNO_R22_NASCOSTO'],g.key())<1e-5
 assert overlap(shell,roof)<1e-5 and overlap(cb,ct)<1e-5
 top_shell=shell.intersect(g.box(-1,-1,64,92,103,25));local_shell=shell.intersect(g.box(0,88,50,14,14,34));paths=[]
 # Per offset >=0 coda e guance hanno Y>101.3, quindi non possono toccare la scocca sotto Z64.
 for travel in np.linspace(101,0,35):
  r=roof.translate((0,float(travel),0));v=overlap(r,top_shell);assert v<1e-5,('scorrimento',travel,v)
  paths.append(dict(phase='scorrimento_tetto',travel_mm=float(travel),overlap_mm3=v))
 # Sede di battuta anteriore, ritenuta verso l'alto e impossibilita di montaggio verticale.
 front=overlap(roof.translate((0,-.5,0)),top_shell);lift=overlap(roof.translate((0,0,.6)),top_shell)
 assert front>0 and lift>0
 key_paths=[]
 for dz in np.linspace(-30,0,31):
  k=g.key(0,float(dz));v=overlap(k,local_shell)+overlap(k,roof);assert v<1e-5,('inserimento',dz,v)
  key_paths.append(dict(phase='inserimento_da_sotto',dz_mm=float(dz),angle_deg=0,overlap_mm3=v))
 for angle in range(0,91,5):
  k=g.key(angle);v=overlap(k,local_shell)+overlap(k,roof);assert v<1e-5,('rotazione',angle,v)
  key_paths.append(dict(phase='rotazione_solleva',dz_mm=0,angle_deg=angle,overlap_mm3=v))
 for dz in np.linspace(0,-g.C['abbassamento_chiuso_mm'],12):
  k=g.key(90,float(dz));v=overlap(k,local_shell)+overlap(k,roof);assert v<1e-5,('assestamento',dz,v)
  key_paths.append(dict(phase='sede_trasversale',dz_mm=float(dz),angle_deg=90,overlap_mm3=v))
 locked=g.closed_key();retention=overlap(locked.translate((0,0,-.3)),roof)
 angular=overlap(locked.rotate((g.CX,g.CY,0),(g.CX,g.CY,100),10),roof)
 # Il perno puo muoversi solo del gioco del foro prima di fermare lo scorrimento del tetto.
 slide_stop=overlap(locked,roof.translate((0,.6,0)))
 assert retention>0 and angular>0 and slide_stop>0,(retention,angular,slide_stop)
 for q in [g.box(0,68,64,14,34,19),g.box(76,68,70,14,21,13)]:assert diff(shell.intersect(q),cb.intersect(q))<1e-5
 assert diff(g.coupon_lid(roof),ct)<1e-5
 for roi in [g.box(0,68,57,14,42,30),g.box(76,68,70,14,21,17)]:assert diff(roof.intersect(roi),ct.intersect(roi))<1e-5
 assert overlap(locked,cb)<1e-5 and overlap(locked,ct)<1e-5
 fits=[]
 # Tutti i nove modelli/slot, anche durante scorrimento e azionamento della chiave.
 for model in g.P['ssd_nominali']:
  for slot in range(3):
   d=g.drive(model,slot);u=g.usb_keepout(model,slot)
   assert overlap(shell,d)<1e-5 and overlap(shell,u)<1e-5
   for travel in [0,10,25,50,75,101]:
    r=roof.translate((0,travel,0));assert overlap(r,d)<1e-5 and overlap(r,u)<1e-5,(model,slot,travel)
   key_clear=[]
   for angle in range(0,91,5):
    k=g.key(angle);assert overlap(k,d)<1e-5 and overlap(k,u)<1e-5,(model,slot,angle)
    key_clear.append(k.distance(u))
   assert overlap(locked,d)<1e-5 and overlap(locked,u)<1e-5
   fits.append(dict(model=model,slot=slot+1,roof_drive_distance_mm=roof.distance(d),rail_drive_lateral_margin_mm=14-11.4,receiver_drive_distance_mm=g.receiver().distance(d),key_drive_distance_mm=locked.distance(d),usb_min_key_sweep_distance_mm=min(key_clear+[locked.distance(u)]),usb_roof_distance_mm=roof.distance(u)))
 # Sagoma chiusa: niente supera i lati X0/90, il retro109 o l'altezza86.
 for s in [roof,locked]:
  b=np.array(g.bounds(s));assert b[0,0]>=-1e-6 and b[1,0]<=90+1e-6 and b[1,1]<=109+1e-6 and b[1,2]<=86+1e-6
 # Gli inserti conservano esattamente la forma approvata; riusabili se gia stampati.
 inserts={}
 for model,name in [('T7','INSERTO_T7_R22'),('T7_Shield','INSERTO_SHIELD_R22')]:
  assert diff(shapes[name],g.adapter(model))<1e-5
  for slot in range(3):
   for y in g.P['slot']['centri_y']:assert overlap(g.adapter(model,y,slot),shell)<1e-5
  inserts[model]='forma R15 invariata'
 previous={}
 for folder in ['bay-ssd-universale-r15-pla-supporti-u','bay-ssd-tetto-r19-pla-alette-r18','bay-ssd-tetto-r20-pla-senza-tagli','bay-ssd-tetto-r21-baionette-rigide']:
  old=ROOT.parent/folder;hh=json.loads((old/'verifiche/SHA256.json').read_text());assert all(g.sha(old/p)==h for p,h in hh.items());previous[folder]=len(hh)
 result=dict(result='PASS_GEOMETRIA_E_CINEMATICA_RIGIDA',source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),parts=records,roof_paths=paths,key_paths=key_paths,ssd_checks=fits,retention=dict(front_stop_overlap_mm3=front,lift_block_overlap_mm3=lift,key_extraction_block_mm3=retention,key_rotation_seated_block_mm3=angular,rear_sliding_block_mm3=slide_stop),insert_compatibility=inserts,previous_files_preserved=previous,physical_print=False,physical_fit=False,force_validated=False,thermal_test=False,side_protrusions=False,limitations=['Controlli su corpi rigidi, senza misurazione di forza e durata.','Passi discreti del moto: controllo geometrico, non analisi continua certificata.','Posizione USB e ingombro connettori nominali: da verificare con i cavi reali.','Accesso manuale al perno e scorrimento delle guide da provare sul provino.','Screening autointersezioni esclude facce con vertici condivisi.'])
 g.save(ROOT/'verifiche/geometria.json',result);print(json.dumps(dict(result='PASS',parts=len(records),roof_poses=len(paths),key_poses=len(key_paths),minimum_usb_key_clearance_mm=min(q['usb_min_key_sweep_distance_mm'] for q in fits))),flush=True)
if __name__=='__main__':main()
