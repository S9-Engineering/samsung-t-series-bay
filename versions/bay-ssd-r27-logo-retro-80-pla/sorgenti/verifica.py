"""R27: riapre gli export e prova che la modifica riguarda solo il logo esterno."""
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
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());refs=json.loads((ROOT/'verifiche/riferimenti_R26.json').read_text());baseline=json.loads((ROOT/'verifiche/geometria_R26_riferimento.json').read_text())
 assert m['source_sha256']==g.sha(ROOT/'sorgenti/genera.py') and m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 assert all(g.sha(ROOT/'sorgenti'/n)==h for n,h in m['geometry_dependencies'].items())
 previous=json.loads((ROOT/'verifiche/geometria.json').read_text()) if (ROOT/'verifiche/geometria.json').exists() else {}
 records=[];shapes={};changes=[];unchanged=[]
 for p in m['parts']:
  s=cq.importers.importStep(str(ROOT/p['step'])).val();ps=cq.importers.importStep(str(ROOT/p['print_step'])).val();mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
  assert s.isValid() and ps.isValid() and len(s.Solids())==len(ps.Solids())==len(mesh.split())==1,p['name']
  assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0 and not np.any(mesh.area_faces<1e-10)
  assert len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
  assert np.allclose(mesh.bounds,g.bounds(ps),atol=.04) and abs(mesh.bounds[0]).max()<1e-4 and abs(mesh.volume/s.Volume()-1)<.005
  assert diff(g.oriented(s,p['orientation']),ps)<1e-5
  for k in ['step','print_step']:assert '.MILLI.,.METRE.' in (ROOT/p[k]).read_text()
  prior=next((q for q in [*previous.get('parts',[]),*baseline['parts']] if q.get('stl_sha256')==p['stl_sha256']),None)
  screen=prior['self_intersections'] if prior else self_intersections_fast(mesh)
  assert screen['intersection_pairs']==0,(p['name'],screen)
  ref=next(q for q in refs['parts'] if q['name']==p['name'].replace('R27','R26'));assert g.sha(ROOT/ref['step'])==ref['sha256']
  old=cq.importers.importStep(str(ROOT/ref['step'])).val()
  if p['name']=='TETTO_R27_DOPPIO_PERNO':
   # Tutto il tetto fino alla faccia posteriore Y109 e identico, inclusi entrambi i ricevitori.
   original_region=g.box(-1,-1,-1,92,110,89)
   assert diff(s.intersect(original_region),old.intersect(original_region))<1e-5
   assert diff(s,g.lid())<1e-5 and diff(s,g.union([g.lid_structure(),*g.logo_shapes()]))<1e-5
   relief=s.cut(g.lid_structure());assert len(relief.Solids())==13
   b=np.array(g.bounds(relief));height=32*.6179337231968811
   assert np.allclose(b[:,0],[29,61],atol=.001) and np.allclose(b[:,1],[109,109.4],atol=.001)
   assert np.allclose(b[:,2],[71.5-height/2,71.5+height/2],atol=.001)
   changes.append(dict(name=p['name'],only_external_logo_changed=True,width_mm=32,height_mm=height,planar_scale=.8,center_x_mm=45,center_z_mm=71.5,relief_mm=.4,glyphs=13,vertical_margin_mm=(29-height)/2,bounds_mm=b.tolist(),functional_roof_unchanged=True))
  else:
   assert diff(s,old)<1e-5
   assert prior is not None and p['stl_sha256']==next(q for q in baseline['parts'] if q['name']==ref['name'])['stl_sha256']
   unchanged.append(p['name'])
  shapes[p['name']]=s;records.append(dict(name=p['name'],quantity=p['quantity'],single_valid_solid=True,mesh_closed=True,winding=True,positive_volume=True,degenerate_faces=0,duplicate_faces=0,self_intersections=screen,screen_reused_identical_stl=prior is not None,volume_mm3=float(mesh.volume),stl_sha256=p['stl_sha256'],step_sha256=p['step_sha256'],print_step_sha256=p['print_step_sha256'],print_bounds_mm=mesh.bounds.tolist()))
  print('EXPORT VERIFICATO',p['name'],flush=True)
 body=shapes['SCOCCA_R27_DOPPIO_PERNO'];roof=shapes['TETTO_R27_DOPPIO_PERNO'];assert vol(body.intersect(roof))<1e-5
 fits=[]
 for model in g.P['ssd_nominali']:
  for slot in range(3):
   for obj in [g.drive(model,slot),g.carrier(model,slot),g.usb_keepout(model,slot),g.front_lock(),g.closed_key(0),g.closed_key(1)]:assert vol(roof.intersect(obj))<1e-5
   fits.append(dict(model=model,slot=slot+1,no_roof_interference=True))
 ap=ROOT/'CAD/ASSIEME_R27_NON_STAMPARE.step';a=cq.importers.importStep(str(ap)).val()
 assert a.isValid() and len(a.Solids())==11 and all(q.Volume()>0 for q in a.Solids()) and np.allclose(g.bounds(a),[[0,-.4,0],[90,109.4,86]],atol=.001)
 result=dict(result='PASS_GEOMETRIA_R27',manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),parts=records,changes=changes,unchanged_types=unchanged,unchanged_kit_types=6,ssd_checks=fits,assembly_sha256=g.sha(ap),assembly_solids=11,pins_identical_printable=True,coupon_functional_surfaces_match=True,inherited_functional_checks=dict(reference_sha256=g.sha(ROOT/'verifiche/geometria_R26_riferimento.json'),roof_poses=35,key_poses=124,cartridge_poses=171,pin_retention=baseline['pin_retention'],reason='Scocca, perni, cartucce, fermo, provino e tetto fino a Y109 identici alla R26; soltanto rilievo esterno ridimensionato. Prove cinematiche conservate per identita geometrica, non rieseguite.'),physical_full_kit_print=False,physical_double_pin_test=False,thermal_test=False,force_validated=False,limitations=['Screening autointersezioni esclude triangoli con vertici condivisi.','La stampa reale, la finitura delle lettere e il kit completo non sono ancora verificati.'])
 g.save(ROOT/'verifiche/geometria.json',result);print('PASS R27: solo logo posteriore ridotto all 80%.',flush=True)
if __name__=='__main__':main()
