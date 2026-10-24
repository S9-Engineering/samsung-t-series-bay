"""Riapertura export, contatti intenzionali e confronto nominale con R15."""
import json
import itertools
import cadquery as cq
import trimesh
import numpy as np
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT

def overlap(a,b):
 return sum(s.Volume() for s in a.intersect(b).Solids())
def diff(a,b):return sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())
def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());checks=[]
 for p in m['parts']:
  mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
  s=cq.importers.importStep(str(ROOT/p['step'])).val();orient=cq.importers.importStep(str(ROOT/p['print_step'])).val()
  assert s.isValid() and orient.isValid() and len(s.Solids())==len(orient.Solids())==1
  assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0 and len(mesh.split())==1
  assert not np.any(mesh.area_faces<1e-10) and len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
  intersections=self_intersections_fast(mesh);assert intersections['intersection_pairs']==0
  assert np.allclose(mesh.bounds,g.bounds(orient),atol=.04) and abs(mesh.volume/s.Volume()-1)<.005
  v=p['variant'];tooth_region=s.intersect(g.box(-1,43,71,g.W+2,16,3));tb=g.bounds(tooth_region)
  tooth_span=tb[1][0]-tb[0][0];assert abs(tooth_span-(g.W-2*(3-v['sporgenza_nominale'])))<1e-5
  walls=[g.reference_wall(side) for side in ('left','right')]
  contacts=[wall.intersect(s) for wall in walls];free_volume=sum(overlap(wall,s) for wall in walls)
  for contact in contacts:
   assert len(contact.Solids())==1
   b=g.bounds(contact);assert b[0][2]>=g.A['pattino_z_min']-1e-6 and b[1][2]<=g.A['pattino_z_max']+1e-6
  loaded=g.coupon(v,inward=g.A['precarico_per_lato'])
  assert sum(overlap(wall,loaded) for wall in walls)<1e-5
  entry=v['sporgenza_nominale']-g.A['precarico_per_lato']
  # Quota a cui il profilo del dente incontra la faccia interna X=3,
  # nell'inviluppo traslato verso interno di 0,15 mm.
  if v['tipo']=='spalla':bearing=v['quota_spalla']
  else:
   tip=3-v['sporgenza_nominale']+g.A['precarico_per_lato'];anchor=3.4+g.A['precarico_per_lato']
   bearing=73+(3-tip)/(anchor-tip)
  checks.append(dict(name=p['name'],stl_sha256=g.sha(ROOT/p['stl']),step_sha256=g.sha(ROOT/p['step']),one_solid=True,closed=True,winding=True,volume_mm3=mesh.volume,
   degenerate_faces=0,duplicate_faces=0,self_intersections=intersections,bounds_mm=mesh.bounds.tolist(),
   nominal_tooth_reach_per_side_mm=v['sporgenza_nominale'],tooth_tip_span_mm=tooth_span,geometric_reach_after_pad_translation_mm=entry,
   window_width_mm=9.6,tab_width_mm=9,tab_y_clearance_per_end_mm=.3,
   first_bearing_z_mm=bearing,vertical_lid_play_envelope_mm=74-bearing,
   intentional_pad_overlap_mm3=free_volume,translated_envelope_collisions_mm3=0,
   mechanical_force_validated=False,FEA=False))
 # Confronto con i file finali R15, senza cambiarli.
 for side in ('left','right'):
  ref=cq.importers.importStep(str(ROOT/'CAD'/('RIFERIMENTO_PARETE_'+side+'_NON_STAMPARE.step'))).val()
  assert ref.isValid() and len(ref.Solids())==1 and diff(ref,g.reference_wall(side))<1e-5
 old=ROOT.parent/'bay-ssd-universale-r15-pla-supporti-u';preserved=None;baseline_delta=None;window_delta=None
 if old.exists():
  hashes=json.loads((old/'verifiche/SHA256.json').read_text());assert all(g.sha(old/p)==h for p,h in hashes.items());preserved=len(hashes)
  old_lid=cq.importers.importStep(str(old/'CAD/coperchio_R15.step')).val()
  roi=g.box(-1,45.9,70,6,9.2,12.999)
  baseline_delta=diff(old_lid.intersect(roi),g.coupon(g.P['varianti'][0]).intersect(roi));assert baseline_delta<1e-5
  shell=cq.importers.importStep(str(old/'CAD/scocca_R15.step')).val()
  roi=g.box(0,40.5,67,3,20,16)
  window_delta=diff(shell.intersect(roi),g.reference_wall().intersect(roi));assert window_delta<1e-5
 g.save(ROOT/'verifiche/geometria.json',dict(result='PASS_GEOMETRIA_NOMINALE',source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),parts=checks,
  R15_hashed_files_preserved=preserved,baseline_left_latch_difference_mm3=baseline_delta,reference_window_difference_mm3=window_delta,
  limitations=['Lieve interferenza solo sui due pattini di precarico.','Inviluppo traslato: nessuna FEA o misura della forza.','Traversa piu rigida del tetto ventilato: qualifica misure e presa locale, non la forza del tetto completo.','Screening autointersezioni esclude triangoli con vertici condivisi.'],physical_print=False))
 print(json.dumps(dict(result='PASS',parts=len(checks),variants=[dict(id=p['name'],reach=p['geometric_reach_after_pad_translation_mm'],play=p['vertical_lid_play_envelope_mm']) for p in checks])),flush=True)
if __name__=='__main__':main()
