"""R17: export e corsa geometrica dei braccetti attraverso pareti da 3 mm."""
import json
import cadquery as cq
import numpy as np
import trimesh
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT

def overlap(a,b):return sum(s.Volume() for s in a.intersect(b).Solids())
def diff(a,b):return sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())
def main():
 man=json.loads((ROOT/'verifiche/manifest.json').read_text());assert len(man['parts'])==1
 part=man['parts'][0];s=cq.importers.importStep(str(ROOT/part['step'])).val();orient=cq.importers.importStep(str(ROOT/part['print_step'])).val()
 mesh=trimesh.load_mesh(ROOT/part['stl'],process=True)
 assert s.isValid() and orient.isValid() and len(s.Solids())==len(orient.Solids())==len(mesh.split())==1
 assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
 assert not np.any(mesh.area_faces<1e-10) and len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
 intersections=self_intersections_fast(mesh);assert intersections['intersection_pairs']==0
 assert np.allclose(mesh.bounds,g.bounds(orient),atol=.04) and abs(mesh.volume/s.Volume()-1)<.005
 walls=[]
 for side in ('left','right'):
  p=ROOT/'CAD'/('RIFERIMENTO_PARETE_'+side+'_NON_STAMPARE.step');wall=cq.importers.importStep(str(p)).val()
  assert wall.isValid() and len(wall.Solids())==1 and diff(wall,g.reference_wall(side))<1e-5
  walls.append(wall)
 assert sum(overlap(s,w) for w in walls)<1e-5
 v=g.P['varianti'][0];dente=g.latch(v).intersect(g.box(-1,45,71,5,11,3));b=g.bounds(dente)
 assert abs(b[0][0]-.2)<1e-5
 penetration=3-b[0][0];recess=b[0][0]
 assert abs(penetration-2.8)<1e-5 and abs(recess-.2)<1e-5
 tooth_width=v['larghezza_dente'];assert abs(tooth_width-8.4)<1e-5
 assert (9.6-tooth_width)/2>=.59 and abs(74-v['quota_spalla']-.2)<1e-5
 # Controllo di spazio, non modello della forma elastica: alette e tratti
 # mobili traslati di 3 mm verso interno durante la discesa.
 path=[]
 for dz in (16,12,8,4,1,.2,0):
  posed=g.coupon(v,inward=3).translate((0,0,dz));vol=sum(overlap(posed,w) for w in walls)
  assert vol<1e-5,(dz,vol);path.append(dict(phase='discesa',dz_mm=dz,inward_mm=3,intersections_mm3=vol))
 for dx in (3,2.5,2,1.5,1,.5,0):
  posed=g.coupon(v,inward=dx);vol=sum(overlap(posed,w) for w in walls)
  assert vol<1e-5,(dx,vol);path.append(dict(phase='rilascio_nel_foro',dz_mm=0,inward_mm=dx,intersections_mm3=vol))
 # Il dente lungo spinge sul bordo superiore dopo soli 0,2 mm di alzata.
 up=s.translate((0,0,.4));bearing=overlap(up,walls[0]);assert bearing>0
 # Controparte ricavata dalle quote dei file finali del case esistente.
 old=ROOT.parent/'bay-ssd-universale-r15-pla-supporti-u';preserved={};reference_diff=None
 if old.exists():
  hh=json.loads((old/'verifiche/SHA256.json').read_text());assert all(g.sha(old/p)==h for p,h in hh.items());preserved['R15']=len(hh)
  shell=cq.importers.importStep(str(old/'CAD/scocca_R15.step')).val();roi=g.box(0,23,67,3,38,16)
  reference_diff=diff(shell.intersect(roi),walls[0].intersect(roi));assert reference_diff<1e-5
 old=ROOT.parent/'bay-ssd-provini-aggancio-r16-pla'
 if old.exists():
  hh=json.loads((old/'verifiche/SHA256.json').read_text());assert all(g.sha(old/p)==h for p,h in hh.items());preserved['R16']=len(hh)
 g.save(ROOT/'verifiche/geometria.json',dict(result='PASS_GEOMETRIA_NOMINALE',source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),
  stl_sha256=g.sha(ROOT/part['stl']),step_sha256=g.sha(ROOT/part['step']),print_step_sha256=g.sha(ROOT/part['print_step']),
  closed=True,winding_consistent=True,components=1,volume_mm3=mesh.volume,bounds_mm=mesh.bounds.tolist(),degenerate_faces=0,duplicate_faces=0,self_intersections=intersections,
  wall_thickness_mm=3,penetration_in_wall_mm=penetration,penetration_fraction=penetration/3,outer_recess_mm=recess,
  lateral_arm_from_finger_face_mm=3.3-recess,tip_span_mm=90-2*recess,tooth_width_mm=tooth_width,
  window_y_clearance_per_end_mm=(9.6-tooth_width)/2,vertical_retention_play_mm=.2,
  seated_overlap_mm3=sum(overlap(s,w) for w in walls),bearing_overlap_after_lift_0_4mm_mm3=bearing,
  insertion_envelopes=path,reference_difference_mm3=reference_diff,previous_hashed_files_preserved=preserved,
  root_release_slot=g.P['scarico_radice'],spring_free_length_y_mm=18,
  limitations=['Corsa controllata con inviluppi traslati: non simulazione della deformazione elastica.',
   'Forza di inserimento, ritenuta, ritorno e durata PLA non misurati.',
   'Scarichi di radice presenti solo sul provino, da trasferire e ricontrollare sul tetto dopo la prova.',
   'Screening autointersezioni esclude triangoli con vertici condivisi.'],physical_print=False,force_validated=False,FEA=False))
 print(json.dumps(dict(result='PASS',penetration_mm=penetration,wall_mm=3,outer_recess_mm=recess,swept_clearance_samples=len(path),preserved=preserved)),flush=True)
if __name__=='__main__':main()
