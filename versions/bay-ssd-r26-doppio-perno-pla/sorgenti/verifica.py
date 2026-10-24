"""R26: riapertura export, secondo fermo e cinematica campionata dei due perni."""
import json
import numpy as np
import cadquery as cq
import trimesh
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT
def vol(s):return sum(q.Volume() for q in s.Solids())
def diff(a,b):return vol(a.cut(b))+vol(b.cut(a))
def ov(a,b):
 aa=np.array(g.bounds(a));bb=np.array(g.bounds(b))
 if np.any(np.minimum(aa[1],bb[1])-np.maximum(aa[0],bb[0])<1e-8):return 0.
 return vol(a.intersect(b))
def clear(a,b,label):
 v=ov(a,b);assert v<1e-5,(label,v);return v
def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());refs=json.loads((ROOT/'verifiche/riferimenti_R25.json').read_text());base=json.loads((ROOT/'verifiche/geometria_R25_riferimento.json').read_text())
 assert m['source_sha256']==g.sha(ROOT/'sorgenti/genera.py') and m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 assert all(g.sha(ROOT/'sorgenti'/n)==h for n,h in m['geometry_dependencies'].items())
 prev=json.loads((ROOT/'verifiche/geometria.json').read_text()) if (ROOT/'verifiche/geometria.json').exists() else {}
 prior={q['name']:q for q in prev.get('parts',[])};records=[];shapes={};changes=[];unchanged=[]
 names={'SCOCCA_R26_DOPPIO_PERNO':'SCOCCA_R25','TETTO_R26_DOPPIO_PERNO':'TETTO_R25_LOGO_ENGINEERING'}
 old_shapes={}
 for p in m['parts']:
  s=cq.importers.importStep(str(ROOT/p['step'])).val();ps=cq.importers.importStep(str(ROOT/p['print_step'])).val();mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
  assert s.isValid() and ps.isValid() and len(s.Solids())==len(ps.Solids())==len(mesh.split())==1,p['name']
  assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0 and not np.any(mesh.area_faces<1e-10)
  assert len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
  assert np.allclose(mesh.bounds,g.bounds(ps),atol=.04) and abs(mesh.bounds[0]).max()<1e-4 and abs(mesh.volume/s.Volume()-1)<.005
  assert diff(g.oriented(s,p['orientation']),ps)<1e-5
  for k in ['step','print_step']:assert '.MILLI.,.METRE.' in (ROOT/p[k]).read_text()
  previous=next((q for q in [*prior.values(),*base['parts']] if q.get('stl_sha256')==p['stl_sha256']),None)
  screen=previous['self_intersections'] if previous else self_intersections_fast(mesh)
  assert screen['intersection_pairs']==0,(p['name'],screen)
  if not p['name'].startswith('PROVINO_'):
   oldname=names.get(p['name'],p['name'].replace('R26','R25'));ref=next(q for q in refs['parts'] if q['name']==oldname)
   assert g.sha(ROOT/ref['step'])==ref['sha256'];old=cq.importers.importStep(str(ROOT/ref['step'])).val();old_shapes[oldname]=old
   delta=diff(s,old)
   if p['name'] in names:
    extra=g.extra_body_support() if p['name'].startswith('SCOCCA_') else g.mirrored(g.r22.receiver())
    assert vol(old.cut(s))<1e-5 and diff(s,g.union([old,extra]))<1e-5 and delta>0
    changes.append(dict(name=p['name'],added_only=True,addition_volume_mm3=delta,addition_bounds_mm=g.bounds(s.cut(old)),original_removed_mm3=0))
   else:assert delta<1e-5;unchanged.append(p['name'])
  shapes[p['name']]=s
  records.append(dict(name=p['name'],quantity=p['quantity'],single_valid_solid=True,mesh_closed=True,winding=True,positive_volume=True,degenerate_faces=0,duplicate_faces=0,self_intersections=screen,screen_reused_identical_stl=previous is not None,volume_mm3=float(mesh.volume),stl_sha256=p['stl_sha256'],step_sha256=p['step_sha256'],print_step_sha256=p['print_step_sha256'],print_bounds_mm=mesh.bounds.tolist()))
  print('EXPORT VERIFICATO',p['name'],flush=True)
 body=shapes['SCOCCA_R26_DOPPIO_PERNO'];roof=shapes['TETTO_R26_DOPPIO_PERNO'];functional_roof=g.lid_structure();extra=g.extra_body_support();lock=shapes['FERMO_CARTUCCE_R26']
 clear(body,roof,'scocca/tetto');clear(body,lock,'scocca/fermo cartucce');clear(roof,lock,'tetto/fermo cartucce')
 assert diff(roof,g.lid())<1e-5 and diff(body,g.shell())<1e-5
 # Medesimo STL del perno per entrambi i lati: la forma aperta e simmetrica in X.
 open_left=g.key();open_right=g.key(side=1)
 assert diff(open_left.translate((g.W-2*g.CX,0,0)),open_right)<1e-5
 closed=[g.closed_key(i) for i in range(2)]
 for i,k in enumerate(closed):clear(k,body,('perno chiuso/scocca',i));clear(k,roof,('perno chiuso/tetto',i));clear(k,lock,('perno chiuso/fermo',i))
 clear(*closed,'perni tra loro')
 fits=[];cartridge_paths=[];models=list(g.P['ssd_nominali'])
 for model in models:
  for slot in range(3):
   c=g.carrier(model,slot);d=g.drive(model,slot);u=g.usb_keepout(model,slot)
   for label,obj in [('cartuccia',c),('SSD',d),('USB nominale',u)]:
    clear(obj,body,(model,slot,label,'scocca'));clear(obj,roof,(model,slot,label,'tetto'))
    for i,k in enumerate(closed):clear(obj,k,(model,slot,label,'perno',i))
   for dz in [90,60,30,10,3,0]:
    for label,obj in [('cartuccia',c),('SSD',d)]:clear(obj.translate((0,-6,dz)),extra,(model,slot,label,'verticale nuovo supporto',dz))
    cartridge_paths.append(dict(model=model,slot=slot+1,phase='calata',dy_mm=-6,dz_mm=dz,overlap_mm3=0))
   for dy in np.linspace(-6,0,13):
    clear(c.translate((0,float(dy),0)),extra,(model,slot,'scorrimento nuovo supporto',dy))
    cartridge_paths.append(dict(model=model,slot=slot+1,phase='arretramento',dy_mm=float(dy),dz_mm=0,overlap_mm3=0))
   distances=[]
   for side in range(2):
    for angle in range(0,91,5):
     k=g.key(angle,side=side)
     for label,obj in [('cartuccia',c),('SSD',d),('USB',u)]:clear(k,obj,(side,angle,label,model,slot))
     distances.append(k.distance(u))
   for dy in [0,10,40,75,101]:
    rr=functional_roof.translate((0,dy,0))
    for label,obj in [('cartuccia',c),('SSD',d),('USB',u)]:clear(rr,obj,(label,'tetto in moto',model,slot,dy))
   fits.append(dict(model=model,slot=slot+1,usb_pin_min_distance_mm=min(distances),roof_carrier_distance_mm=roof.distance(c),new_support_drive_distance_mm=extra.distance(d)))
  print('SSD E CONNETTORI OK',model,flush=True)
 roof_paths=[];key_paths=[];retention=[]
 top_body=body.intersect(g.box(-1,-1,54,92,103,35))
 for dy in np.linspace(101,0,35):
  rr=functional_roof.translate((0,float(dy),0));roof_paths.append(dict(travel_mm=float(dy),overlap_mm3=clear(rr,top_body,'scorrimento tetto')));clear(rr,lock,'scorrimento tetto/fermo cartucce')
 for side in range(2):
  local=body.intersect(g.box(0 if side==0 else 76,88,50,14,14,34))
  for dz in np.linspace(-30,0,31):
   k=g.key(0,float(dz),side);clear(k,local,('ingresso perno/scocca',side,dz));clear(k,functional_roof,('ingresso perno/tetto',side,dz));key_paths.append(dict(side=side,phase='inserimento',dz_mm=float(dz),angle_deg=0))
  for angle in range(0,91,5):
   k=g.key(angle,side=side);clear(k,local,('giro/scocca',side,angle));clear(k,functional_roof,('giro/tetto',side,angle));key_paths.append(dict(side=side,phase='rotazione',dz_mm=0,angle_deg=angle))
  for dz in np.linspace(0,-g.C['abbassamento_chiuso_mm'],12):
   k=g.key(90,float(dz),side);clear(k,local,('sede/scocca',side,dz));clear(k,functional_roof,('sede/tetto',side,dz));key_paths.append(dict(side=side,phase='sede',dz_mm=float(dz),angle_deg=90))
  k=closed[side];axisx=g.CX if side==0 else g.W-g.CX
  values=dict(pin_extraction=ov(k.translate((0,0,-.3)),functional_roof),pin_rotation=ov(k.rotate((axisx,g.CY,0),(axisx,g.CY,100),10),functional_roof),roof_back=ov(k,functional_roof.translate((0,.6,0))))
  assert all(v>0 for v in values.values()),(side,values);retention.append(dict(side=side,blocking_overlap_mm3=values))
 assert ov(functional_roof.translate((0,0,.6)),top_body)>0
 # Le guide e i supporti dei due lati del provino replicano il kit finale.
 cb=shapes['PROVINO_GUIDE_SCOCCA_R26'];cr=shapes['PROVINO_GUIDE_TETTO_R26']
 assert diff(cb,g.coupon_body())<1e-5 and diff(cr,g.coupon_lid())<1e-5
 clear(cb,cr,'provino scocca/tetto')
 for side in range(2):
  roi=g.box(0 if side==0 else 76,88.5,54,14,18,29.1)
  assert diff(cb.intersect(roi),body.intersect(roi))<1e-5
  assert diff(cr.intersect(roi),functional_roof.intersect(roi))<1e-5
  clear(closed[side],cb,('provino perno/scocca',side));clear(closed[side],cr,('provino perno/tetto',side))
 assyp=ROOT/'CAD/ASSIEME_R26_NON_STAMPARE.step';a=cq.importers.importStep(str(assyp)).val()
 assert a.isValid() and len(a.Solids())==11 and all(q.Volume()>0 for q in a.Solids())
 assert np.allclose(g.bounds(a),[[0,-.4,0],[90,109.4,86]],atol=.001)
 result=dict(result='PASS_GEOMETRIA_E_CINEMATICA_R26',manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),parts=records,changes=changes,unchanged_types=unchanged,ssd_checks=fits,new_support_cartridge_paths=cartridge_paths,roof_paths=roof_paths,key_paths=key_paths,pin_retention=retention,pins_identical_printable=True,coupon_functional_surfaces_match=True,assembly_sha256=g.sha(assyp),assembly_solids=11,physical_full_kit_print=False,physical_double_pin_test=False,thermal_test=False,force_validated=False,inherited_checks='R24: cinematica e ritenuta piede/fermo conservate per identita geometrica; ripetuti i percorsi rispetto al supporto aggiunto e quelli del tetto e di entrambi i perni.',limitations=['Moto campionato; nessuna analisi delle forze, fatica o creep del PLA.','SSD e cavi nominali, non scansioni dei pezzi reali.','Screening autointersezioni esclude triangoli con vertici condivisi.','Utente: primo provino interni accettato; secondo provino precedente entra, rotazione e ritenuta non esplicitamente confermate.'])
 g.save(ROOT/'verifiche/geometria.json',result);print(json.dumps(dict(result='PASS',parts=len(records),ssd_cases=len(fits),cartridge_poses=len(cartridge_paths),roof_poses=len(roof_paths),key_poses=len(key_paths))),flush=True)
if __name__=='__main__':main()
