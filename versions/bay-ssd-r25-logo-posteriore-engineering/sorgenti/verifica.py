"""Riapertura R25, confronto selettivo con R24 e verifica dell'aggiunta esterna."""
import json
import numpy as np
import cadquery as cq
import trimesh
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT
def vol(s):return sum(q.Volume() for q in s.Solids())
def diff(a,b):return vol(a.cut(b))+vol(b.cut(a))
def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());refs=json.loads((ROOT/'verifiche/riferimenti_R24.json').read_text());baseline=json.loads((ROOT/'verifiche/geometria_R24_riferimento.json').read_text())
 assert m['source_sha256']==g.sha(ROOT/'sorgenti/genera.py') and m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 rows=[];shapes={};changes=[]
 for p in m['parts']:
  s=cq.importers.importStep(str(ROOT/p['step'])).val();ps=cq.importers.importStep(str(ROOT/p['print_step'])).val();mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
  assert s.isValid() and ps.isValid() and len(s.Solids())==len(ps.Solids())==len(mesh.split())==1
  assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0 and not np.any(mesh.area_faces<1e-10)
  assert len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces) and np.allclose(mesh.bounds,g.bounds(ps),atol=.04) and abs(mesh.bounds[0]).max()<1e-4 and abs(mesh.volume/s.Volume()-1)<.005
  assert diff(g.oriented(s,p['orientation']),ps)<1e-5 and '.MILLI.,.METRE.' in (ROOT/p['step']).read_text()
  old_name=p['name'].replace('R25','R24').replace('TETTO_R24_LOGO_ENGINEERING','TETTO_R24_SCORREVOLE');ref=next(q for q in refs['parts'] if q['name']==old_name);assert g.sha(ROOT/ref['step'])==ref['sha256']
  old=cq.importers.importStep(str(ROOT/ref['step'])).val();change=diff(s,old)
  prior=next(q for q in baseline['parts'] if q['name']==old_name)
  same_mesh=p['stl_sha256']==prior['stl_sha256'];screen=prior['self_intersections'] if same_mesh else self_intersections_fast(mesh)
  assert screen['intersection_pairs']==0
  if p['name']!='TETTO_R25_LOGO_ENGINEERING':assert change<1e-5,(p['name'],change)
  else:
   # Nessuna sottrazione: la forma originale e tutti gli accoppiamenti sono conservati.
   assert vol(old.cut(s))<1e-5 and change>0
   addition=s.cut(old);assert len(addition.Solids())==13
   b=np.array(g.bounds(addition));assert b[0,1]>=109-1e-6 and b[1,1]<=109.40001
   assert np.allclose(b[:,0],[25,65],atol=.001) and abs(b[:,2].mean()-71.5)<.001
   assert b[0,2]>57 and b[1,2]<86
   changes.append(dict(name=p['name'],added_only=True,added_volume_mm3=change,added_bounds_mm=b.tolist(),glyphs=13,original_roof_removed_mm3=0))
  shapes[p['name']]=s;rows.append(dict(name=p['name'],single_valid_solid=True,mesh_closed=True,winding=True,volume_mm3=float(mesh.volume),self_intersections=screen,screen_reused_identical_stl=same_mesh,stl_sha256=p['stl_sha256'],step_sha256=p['step_sha256'],print_step_sha256=p['print_step_sha256'],difference_from_R24_mm3=change))
  print('VERIFICATO',p['name'],flush=True)
 roof=shapes['TETTO_R25_LOGO_ENGINEERING'];body=shapes['SCOCCA_R25'];assert vol(roof.intersect(body))<1e-5
 added=roof.cut(cq.importers.importStep(str(ROOT/'CAD/riferimenti_R24/TETTO_R24_SCORREVOLE.step')).val());fits=[]
 for model in g.P['ssd_nominali']:
  for slot in range(3):
   for s in [g.drive(model,slot),g.carrier(model,slot),g.usb_keepout(model,slot),g.r24.closed_key(),g.r24.front_lock()]:assert vol(roof.intersect(s))<1e-5
   fits.append(dict(model=model,slot=slot+1,logo_usb_distance_mm=added.distance(g.usb_keepout(model,slot))))
 # Durante apertura +Y, il materiale aggiunto si allontana ulteriormente dal case.
 assert g.bounds(added)[0][1]>g.bounds(body)[1][1]
 assembly=ROOT/'CAD/ASSIEME_R25_NON_STAMPARE.step';a=cq.importers.importStep(str(assembly)).val();assert a.isValid() and len(a.Solids())==10 and np.allclose(g.bounds(a),[[0,-.4,0],[90,109.4,86]],atol=.001)
 result=dict(result='PASS_GEOMETRIA_R25',manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),parts=rows,changes=changes,unchanged_printable_parts=6,ssd_checks=fits,assembly_sha256=g.sha(assembly),assembly_solids=10,baseline_kinematics='R24: identita delle sei parti e della porzione originale del tetto verificata. L aggiunta esterna non modifica gli accoppiamenti; non ripetute le prove geometriche di moto dei pezzi identici.',physical_print=False,physical_fit=False,thermal_test=False,limitations=['Screening delle autointersezioni esclude triangoli con vertici condivisi.','Quote SSD e cavi nominali; finitura e leggibilita del marchio da verificare in stampa.'])
 g.save(ROOT/'verifiche/geometria.json',result);print('PASS R25',flush=True)
if __name__=='__main__':main()
