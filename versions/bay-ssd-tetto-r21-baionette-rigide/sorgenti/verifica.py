"""R21: controlli export e cinematica senza flessione di bracci o pareti."""
import json
import numpy as np
import cadquery as cq
import trimesh
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT

def overlap(a,b):return sum(s.Volume() for s in a.intersect(b).Solids())
def diff(a,b):return sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())
def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());records=[];shapes={}
 for p in m['parts']:
  s=cq.importers.importStep(str(ROOT/p['step'])).val();ps=cq.importers.importStep(str(ROOT/p['print_step'])).val();mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
  assert s.isValid() and ps.isValid() and len(s.Solids())==len(ps.Solids())==len(mesh.split())==1
  assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
  assert not np.any(mesh.area_faces<1e-10) and len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
  inter=self_intersections_fast(mesh);assert inter['intersection_pairs']==0,(p['name'],inter)
  assert np.allclose(mesh.bounds,g.bounds(ps),atol=.04) and abs(mesh.volume/s.Volume()-1)<.005
  assert abs(mesh.bounds[0]).max()<1e-4
  shapes[p['name']]=s;records.append(dict(name=p['name'],closed=True,components=1,winding=True,positive_volume=True,degenerate_faces=0,duplicate_faces=0,self_intersections=inter,stl_sha256=g.sha(ROOT/p['stl']),step_sha256=g.sha(ROOT/p['step']),print_step_sha256=g.sha(ROOT/p['print_step']),print_bounds_mm=mesh.bounds.tolist(),volume_mm3=float(mesh.volume)))
 roof=shapes['TETTO_R21_BAIONETTA'];coupon=shapes['PROVINO_R21_BAIONETTA'];key=shapes['PERNO_R21_QUARTO_GIRO'];shell=g.reference_shell()
 assert diff(roof,g.lid())<1e-5 and diff(key,g.key())<1e-5
 assert overlap(roof,shell)<1e-5 and overlap(coupon,shell)<1e-5
 lowered=[]
 for z in [30,20,10,5,2,.5,0]:
  v=overlap(roof.translate((0,0,z)),shell);assert v<1e-5,(z,v)
  lowered.append(dict(dz_mm=z,overlap_mm3=v))
 # Inserimento estrazione e rotazione dei due perni: tutte parti rigide.
 paths=[]
 for side in ['left','right']:
  for withdrawal in np.linspace(13.2,0,23):
   k=g.key(side,0,float(withdrawal));v=overlap(k,roof)+overlap(k,shell);assert v<1e-5,(side,withdrawal,v)
   paths.append(dict(side=side,phase='inserimento',withdrawal_mm=float(withdrawal),angle_deg=0,overlap_mm3=v))
  for angle in range(0,91,5):
   k=g.key(side,angle);v=overlap(k,roof)+overlap(k,shell);assert v<1e-5,(side,angle,v)
   paths.append(dict(side=side,phase='rotazione',withdrawal_mm=0,angle_deg=angle,overlap_mm3=v))
  # A 90 gradi la testa interna non passa piu dal foro.
  retention=overlap(g.key(side,90,.7),roof);assert retention>0
  # Peg in salita nel caso reale: dopo il piccolo gioco incontra la finestra.
  case_stop=overlap(g.key(side,90).translate((0,0,.4)),shell);assert case_stop>0
  # Una chiave mantenuta nella finestra impedisce al tetto di alzarsi.
  lid_stop=overlap(g.key(side,90).translate((0,0,.1)),roof.translate((0,0,.6)));assert lid_stop>0
  paths.append(dict(side=side,phase='ritenuta',withdrawal_block_overlap_mm3=retention,case_bearing_after_key_lift_0_4mm_mm3=case_stop,lid_bearing_after_lift_0_6mm_mm3=lid_stop))
 # Provino: stessi due supporti rigidi e stessa sede della chiave del tetto.
 roi=g.box(3.9,44.4,68.4,6.2,12.2,14.7)
 for rr in [roi,roi.mirror('YZ',(45,0,0))]:assert diff(roof.intersect(rr),coupon.intersect(rr))<1e-5
 fits=[];locked=[g.key(side,90) for side in ['left','right']]
 for model in g.P['ssd_nominali']:
  for slot in range(3):
   d=g.drive(model,slot);u=g.usb_keepout(model,slot);assert overlap(roof,d)<1e-5 and overlap(roof,u)<1e-5
   for k in locked:assert overlap(k,d)<1e-5 and overlap(k,u)<1e-5
   fits.append(dict(model=model,slot=slot+1,roof_drive_distance_mm=roof.distance(d),pin_drive_distance_mm=min(k.distance(d) for k in locked),usb_clearance_mm=roof.distance(u)))
 preserved={}
 for rev,folder in [('R15','bay-ssd-universale-r15-pla-supporti-u'),('R18','bay-ssd-provino-aggancio-r18-pla'),('R19','bay-ssd-tetto-r19-pla-alette-r18'),('R20','bay-ssd-tetto-r20-pla-senza-tagli')]:
  old=ROOT.parent/folder;hh=json.loads((old/'verifiche/SHA256.json').read_text());assert all(g.sha(old/p)==h for p,h in hh.items());preserved[rev]=len(hh)
 g.save(ROOT/'verifiche/geometria.json',dict(result='PASS_GEOMETRIA_E_CINEMATICA_RIGIDA',source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),parts=records,lowering_path=lowered,key_paths=paths,ssd_checks=fits,previous_files_preserved=preserved,
  without_elastic_installation=True,elastic_arm=False,extra_hardware=False,receiver_root_nominal_section_mm2=6*12,nominal_pin_diameter_mm=2.8,quarter_turn_deg=90,
  minimum_pin_drive_distance_mm=min(f['pin_drive_distance_mm'] for f in fits),minimum_usb_distance_mm=min(f['usb_clearance_mm'] for f in fits),physical_print=False,physical_fit=False,force_validated=False,
  limitations=['Controllo cinematico con corpi rigidi; non misura della forza, resistenza o durata.',
   'Scocca e finestre nominali; corrispondenza con la scocca stampata da provare.',
   'Prima verifica prevista sul provino R21: due supporti e perni della stessa geometria del tetto.',
   'Screening autointersezioni esclude triangoli con vertici condivisi.']))
 print(json.dumps(dict(result='PASS',parts=len(records),poses=len(paths),minimum_pin_drive_distance_mm=min(f['pin_drive_distance_mm'] for f in fits),minimum_usb_distance_mm=min(f['usb_clearance_mm'] for f in fits),preserved=preserved)),flush=True)
if __name__=='__main__':main()
