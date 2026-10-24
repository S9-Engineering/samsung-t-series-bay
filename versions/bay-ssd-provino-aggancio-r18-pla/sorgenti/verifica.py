"""R18: export, gioco della paletta, lieve apertura e braccetto lungo R17."""
import json,math
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
 v=g.P['varianti'][0];a=g.A;assert diff(s,g.coupon(v))<1e-5
 walls=[]
 for side in ('left','right'):
  p=ROOT/'CAD'/('RIFERIMENTO_PARETE_'+side+'_NON_STAMPARE.step');wall=cq.importers.importStep(str(p)).val()
  assert wall.isValid() and len(wall.Solids())==1 and diff(wall,g.reference_wall(side))<1e-5
  walls.append(wall)
 seated=sum(overlap(s,w) for w in walls);assert seated<1e-5
 # Fascia esterna al braccetto: misura solo l'aletta dal STEP finale.
 stem=s.intersect(g.box(2.5,46.05,71,3,.1,12));sb=g.bounds(stem)
 clearance=sb[0][0]-g.P['parete_case'];assert abs(clearance-.05)<1e-6
 # Sopra la finestra, dove la parete e continua, il gioco e ancora maggiore.
 above=s.intersect(g.box(2.5,46.05,74,3,.1,9));above_clearance=g.bounds(above)[0][0]-3
 assert abs(above_clearance-.075)<1e-6
 root_x=3+a['gioco_radice'];tip_x=root_x-v['lunghezza_braccetto_dal_fianco']-a['apertura_esterna_punta_mm']*(g.TOP-v['quota_naso_basso'])/a['lunghezza']
 actual_tip=g.bounds(s)[0][0];assert abs(actual_tip-tip_x)<1e-6
 assert abs(root_x-a['gioco_radice']-3)<1e-6
 penetration=min(3,3-actual_tip);protrusion=max(0,-actual_tip)
 tooth_width=v['larghezza_dente'];assert abs(tooth_width-8.4)<1e-5
 assert (9.6-tooth_width)/2>=.59 and abs(74-v['quota_spalla']-.2)<1e-5
 # Inviluppi rigidi per lo spazio di manovra: non simulazione elastica.
 path=[];travel=g.P['inviluppo_rientro_mm']
 for dz in (16,12,8,4,1,.2,0):
  posed=g.coupon(v,inward=travel).translate((0,0,dz));vol=sum(overlap(posed,w) for w in walls)
  assert vol<1e-5,(dz,vol);path.append(dict(phase='discesa',dz_mm=dz,inward_mm=travel,intersections_mm3=vol))
 for dx in (travel,2.5,2,1.5,1,.5,0):
  posed=g.coupon(v,inward=dx);vol=sum(overlap(posed,w) for w in walls)
  assert vol<1e-5,(dx,vol);path.append(dict(phase='rilascio_nel_foro',dz_mm=0,inward_mm=dx,intersections_mm3=vol))
 bearing=overlap(s.translate((0,0,.4)),walls[0]);assert bearing>0
 preserved={};reference_diff=None
 for label,folder in [('R15','bay-ssd-universale-r15-pla-supporti-u'),('R16','bay-ssd-provini-aggancio-r16-pla'),('R17','bay-ssd-provino-braccetto-passante-r17-pla')]:
  old=ROOT.parent/folder
  if old.exists():
   hh=json.loads((old/'verifiche/SHA256.json').read_text());assert all(g.sha(old/p)==h for p,h in hh.items());preserved[label]=len(hh)
   if label=='R15':
    shell=cq.importers.importStep(str(old/'CAD/scocca_R15.step')).val();roi=g.box(0,23,67,3,38,16)
    reference_diff=diff(shell.intersect(roi),walls[0].intersect(roi));assert reference_diff<1e-5
   if label=='R17':
    previous=json.loads((old/'sorgenti/parametri.json').read_text());assert g.P['scarico_radice']==previous['scarico_radice']
 g.save(ROOT/'verifiche/geometria.json',dict(result='PASS_GEOMETRIA_NOMINALE',source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),
  stl_sha256=g.sha(ROOT/part['stl']),step_sha256=g.sha(ROOT/part['step']),print_step_sha256=g.sha(ROOT/part['print_step']),
  closed=True,winding_consistent=True,components=1,volume_mm3=float(mesh.volume),bounds_mm=mesh.bounds.tolist(),degenerate_faces=0,duplicate_faces=0,self_intersections=intersections,
  wall_thickness_mm=3,penetration_in_wall_mm=penetration,outer_protrusion_mm=protrusion,actual_tip_x_mm=actual_tip,
  lateral_arm_from_finger_face_mm=v['lunghezza_braccetto_dal_fianco'],tip_span_mm=90-2*actual_tip,tooth_width_mm=tooth_width,
  root_wall_clearance_mm=a['gioco_radice'],minimum_stem_wall_clearance_mm=clearance,minimum_clearance_above_window_mm=above_clearance,
  outward_tip_bias_mm=a['apertura_esterna_punta_mm'],outward_angle_deg=math.degrees(math.atan(a['apertura_esterna_punta_mm']/a['lunghezza'])),
  finger_thickness_mm=a['spessore'],window_y_clearance_per_end_mm=(9.6-tooth_width)/2,vertical_retention_play_mm=.2,
  seated_overlap_mm3=seated,bearing_overlap_after_lift_0_4mm_mm3=bearing,
  insertion_envelopes=path,reference_difference_mm3=reference_diff,previous_hashed_files_preserved=preserved,
  root_release_slot=g.P['scarico_radice'],spring_free_length_y_mm=18,roof_relief_unchanged_from_R17=True,
  prior_user_observation=g.P['riscontro_R17_utente'],
  limitations=['Corsa controllata con inviluppi traslati: non simulazione della deformazione elastica.',
   'Forza di inserimento, ritenuta, ritorno e durata PLA R18 non misurati.',
   'Gioco minimo 0,05 mm nominali: tolleranza fisica della stampa da verificare sul case esistente.',
   'Scarichi di radice presenti solo sul provino, da trasferire e ricontrollare sul tetto dopo la prova.',
   'Screening autointersezioni esclude triangoli con vertici condivisi.'],physical_print=False,force_validated=False,FEA=False))
 print(json.dumps(dict(result='PASS',minimum_clearance_mm=clearance,angle_deg=math.degrees(math.atan(.1/12)),peg_length_mm=3.1,tip_x_mm=actual_tip,swept_clearance_samples=len(path),preserved=preserved)),flush=True)
if __name__=='__main__':main()
