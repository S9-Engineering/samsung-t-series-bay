"""R19: export finali, trasferimento esatto R18 e accoppiamento con scocca R15."""
import json,math
import cadquery as cq
import numpy as np
import trimesh
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT

def volume(s):return sum(q.Volume() for q in s.Solids())
def overlap(a,b):return volume(a.intersect(b))
def diff(a,b):return volume(a.cut(b))+volume(b.cut(a))
def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());p=m['parts'][0]
 s=cq.importers.importStep(str(ROOT/p['step'])).val();ps=cq.importers.importStep(str(ROOT/p['print_step'])).val();mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
 assert s.isValid() and ps.isValid() and len(s.Solids())==len(ps.Solids())==len(mesh.split())==1
 assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
 assert not np.any(mesh.area_faces<1e-10) and len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
 intersects=self_intersections_fast(mesh);assert intersects['intersection_pairs']==0
 assert np.allclose(mesh.bounds,g.bounds(ps),atol=.04) and abs(mesh.volume/s.Volume()-1)<.005 and diff(s,g.lid())<1e-5
 assert np.allclose(mesh.extents,[90.0833333333,109,29],atol=.0001)
 shell=g.reference_shell();assert shell.isValid() and len(shell.Solids())==1
 old=cq.importers.importStep(str(ROOT/'CAD/riferimenti_NON_STAMPARE/coperchio_R15_NON_STAMPARE.step')).val()
 prototype=cq.importers.importStep(str(ROOT/'CAD/riferimenti_NON_STAMPARE/provino_R18_NON_STAMPARE.step')).val()
 for q in [old,prototype]:assert q.isValid() and len(q.Solids())==1
 # Fuori da queste due zone e conservata esattamente la geometria della R15.
 local=g.box(-1,27.7,70.9,10,28.0,15.2);zones=[local,local.mirror('YZ',(45,0,0))]
 external_diff=diff(s.cut(*zones),old.cut(*zones));assert external_diff<1e-5,external_diff
 # Include paletta, braccetto, striscia flessibile e attacco anteriore.
 roi=g.box(-.2,27.8,70.9,4.8,27.8,15.2);checks=[]
 for side in ('left','right'):
  rr=roi if side=='left' else roi.mirror('YZ',(45,0,0))
  delta=diff(s.intersect(rr),prototype.intersect(rr));assert delta<1e-5,(side,delta)
  checks.append(dict(side=side,difference_from_R18_mm3=delta))
 seated=overlap(s,shell);assert seated<1e-5,seated
 stem=s.intersect(g.box(2.5,46.05,71,3,.1,12));minimum=g.bounds(stem)[0][0]-3;assert abs(minimum-.05)<1e-6
 above=s.intersect(g.box(2.5,46.05,74,3,.1,9));upper_gap=g.bounds(above)[0][0]-3;assert abs(upper_gap-.075)<1e-6
 bearing=overlap(s.translate((0,0,.4)),shell);assert bearing>0
 # Spazio nominale di manovra: traslazioni rigide, nessuna FEA.
 path=[];travel=g.a.P['inviluppo_rientro_mm']
 for dz in (16,12,8,4,1,.2,0):
  posed=g.lid(travel).translate((0,0,dz));v=overlap(posed,shell);assert v<1e-5,(dz,v)
  path.append(dict(phase='discesa',dz_mm=dz,inward_mm=travel,intersection_mm3=v))
 for dx in (travel,2.5,2,1.5,1,.5,0):
  v=overlap(g.lid(dx),shell);assert v<1e-5,(dx,v)
  path.append(dict(phase='rilascio',dz_mm=0,inward_mm=dx,intersection_mm3=v))
 fits=[]
 for model in g.P['ssd_nominali']:
  for slot in range(3):
   drive=g.drive(model,slot);usb=g.usb_keepout(model,slot)
   dv=overlap(s,drive);uv=overlap(s,usb);assert dv<1e-5 and uv<1e-5
   fits.append(dict(model=model,slot=slot+1,drive_collision_mm3=dv,usb_collision_mm3=uv,usb_minimum_distance_mm=s.distance(usb),ssd_top_to_roof_mm=g.TOP-drive.BoundingBox().zmax))
 preserved={}
 for label,folder in [('R15','bay-ssd-universale-r15-pla-supporti-u'),('R18','bay-ssd-provino-aggancio-r18-pla')]:
  prev=ROOT.parent/folder;hh=json.loads((prev/'verifiche/SHA256.json').read_text());assert all(g.sha(prev/q)==h for q,h in hh.items());preserved[label]=len(hh)
 for q,h in m['reference_hashes'].items():assert g.sha(ROOT/q)==h
 a=g.a.A
 g.save(ROOT/'verifiche/geometria.json',dict(result='PASS_GEOMETRIA_NOMINALE_TETTO',source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),
  stl_sha256=g.sha(ROOT/p['stl']),step_sha256=g.sha(ROOT/p['step']),print_step_sha256=g.sha(ROOT/p['print_step']),
  closed=True,winding_consistent=True,components=1,faces=len(mesh.faces),volume_mm3=float(mesh.volume),print_bounds_mm=mesh.bounds.tolist(),degenerate_faces=0,duplicate_faces=0,self_intersections=intersects,
  exact_R18_latch_transfer=checks,unchanged_outside_latch_zones_difference_mm3=external_diff,tail_bottom_z_mm=g.P['retro_coperchio']['quota_inferiore_mm'],
  horizontal_roof_vent_cutters=16,roof_thickness_mm=3,finger_thickness_mm=a['spessore'],lateral_arm_mm=3.1,root_wall_clearance_mm=a['gioco_radice'],minimum_stem_wall_clearance_mm=minimum,minimum_gap_above_window_mm=upper_gap,
  outward_bias_mm=a['apertura_esterna_punta_mm'],outward_angle_deg=math.degrees(math.atan(.1/12)),seated_overlap_mm3=seated,bearing_overlap_after_lift_0_4mm_mm3=bearing,
  insertion_envelopes=path,drive_and_usb_checks=fits,minimum_usb_clearance_mm=min(f['usb_minimum_distance_mm'] for f in fits),previous_hashed_files_preserved=preserved,
  limitations=['Geometria nominale; scocca, SSD e spinotti reali non misurati in questa revisione.',
   'Inviluppi di manovra traslati rigidamente, non simulazione della flessione.',
   'Presa, forza, durata e giochi fisici del tetto completo R19 non verificati; nessun nuovo riscontro fisico R18 comunicato.',
   'Screening autointersezioni esclude triangoli con vertici condivisi.'],physical_print=False,physical_fit=False,FEA=False,force_validated=False))
 print(json.dumps(dict(result='PASS',transfer_R18=checks,unchanged_remainder_mm3=external_diff,clearance_mm=minimum,usb_clearance_mm=min(f['usb_minimum_distance_mm'] for f in fits),faces=len(mesh.faces),preserved=preserved)),flush=True)
if __name__=='__main__':main()
