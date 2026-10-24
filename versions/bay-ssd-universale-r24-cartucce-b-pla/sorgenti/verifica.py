"""Riapre export R24 e verifica gli accoppiamenti con corpi rigidi nominali."""
import json,itertools
import numpy as np
import cadquery as cq
import trimesh
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT
def vol(s):return sum(q.Volume() for q in s.Solids())
def ov(a,b):return vol(a.intersect(b))
def diff(a,b):return vol(a.cut(b))+vol(b.cut(a))
def clear(a,b,label):
 v=ov(a,b);assert v<1e-5,(label,v);return v
def main():
 man=json.loads((ROOT/'verifiche/manifest.json').read_text());assert man['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json') and man['source_sha256']==g.sha(ROOT/'sorgenti/genera.py')
 records=[];parts={}
 previous=json.loads((ROOT/'verifiche/geometria.json').read_text()) if (ROOT/'verifiche/geometria.json').exists() else {}
 previous_parts={q['name']:q for q in previous.get('parts',[])}
 for p in man['parts']:
  s=cq.importers.importStep(str(ROOT/p['step'])).val();ps=cq.importers.importStep(str(ROOT/p['print_step'])).val();mesh=trimesh.load_mesh(ROOT/p['stl'],process=True)
  assert s.isValid() and ps.isValid() and len(s.Solids())==len(ps.Solids())==len(mesh.split())==1
  assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
  assert not np.any(mesh.area_faces<1e-10) and len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
  prior=previous_parts.get(p['name'],{})
  inter=prior['self_intersections'] if prior.get('stl_sha256')==g.sha(ROOT/p['stl']) else self_intersections_fast(mesh)
  assert inter['intersection_pairs']==0,(p['name'],inter)
  assert np.allclose(mesh.bounds,g.bounds(ps),atol=.04) and abs(mesh.volume/s.Volume()-1)<.005 and abs(mesh.bounds[0]).max()<1e-4
  assert diff(g.oriented(s,p['orientation']),ps)<1e-5
  assert '.MILLI.,.METRE.' in (ROOT/p['step']).read_text() and '.MILLI.,.METRE.' in (ROOT/p['print_step']).read_text()
  parts[p['name']]=s;records.append(dict(name=p['name'],closed=True,components=1,winding=True,positive_volume=True,degenerate_faces=0,duplicate_faces=0,self_intersections=inter,stl_sha256=g.sha(ROOT/p['stl']),step_sha256=g.sha(ROOT/p['step']),print_step_sha256=g.sha(ROOT/p['print_step']),print_bounds_mm=mesh.bounds.tolist(),volume_mm3=float(mesh.volume)))
  print('EXPORT VERIFICATO',p['name'],flush=True)
 shell=parts['SCOCCA_R24'];roof=parts['TETTO_R24_SCORREVOLE'];lock=parts['FERMO_CARTUCCE_R24'];key=g.closed_key()
 assert diff(shell,g.shell())<1e-5
 r22=ROOT/'CAD/riferimenti_R22'
 oldroof=cq.importers.importStep(str(r22/'TETTO_R22_SCORREVOLE.step')).val();oldkey=cq.importers.importStep(str(r22/'PERNO_R22_NASCOSTO.step')).val()
 assert diff(roof,oldroof)<1e-5 and diff(parts['PERNO_R24_NASCOSTO'],oldkey)<1e-5
 clear(shell,roof,'scocca/tetto');clear(lock,shell,'fermo/scocca');clear(lock,roof,'presa fermo/tetto')
 paths=[];fits=[];retention=[];models=list(g.P['ssd_nominali'])
 fixed=g.union([g.receiver(i) for i in range(3)])
 for model in models:
  for slot in range(3):
   c=g.carrier(model,slot);d=g.drive(model,slot);u=g.usb_keepout(model,slot)
   for label,s in [('scocca',shell),('SSD',d),('tetto',roof),('fermo',lock),('chiave',key),('USB',u)]:clear(c,s,(model,slot,label))
   clear(d,shell,'SSD/scocca');clear(u,shell,'USB/scocca')
   for travel in [110,80,50,20,5,0]:clear(d.translate((0,travel,0)),c,('ingresso SSD',model,slot,travel))
   for dz in [90,60,30,10,3,0]:
    move=c.translate((0,-6,dz));paths.append(dict(phase='verticale_cartuccia',model=model,slot=slot+1,dy_mm=-6,dz_mm=dz,overlap_mm3=clear(move,shell,('verticale',model,slot,dz))))
    clear(d.translate((0,-6,dz)),shell,('verticale SSD',model,slot,dz))
   for dy in np.linspace(-6,0,13):
    move=c.translate((0,float(dy),0));paths.append(dict(phase='scorrimento_cartuccia',model=model,slot=slot+1,dy_mm=float(dy),dz_mm=0,overlap_mm3=clear(move,shell,('scorrimento',model,slot,dy))))
   # La ritenuta e geometrica: piedi sotto guide, fermo comune davanti, battuta dietro.
   values=dict(lift=ov(c.translate((0,0,.5)),fixed),front=ov(c.translate((0,-.6,0)),lock),back=ov(c.translate((0,.5,0)),fixed),left=ov(c.translate((-.5,0,0)),fixed),right=ov(c.translate((.5,0,0)),fixed),down=ov(c.translate((0,0,-.3)),fixed))
   assert all(v>0 for v in values.values()),(model,slot,values);retention.append(dict(model=model,slot=slot+1,blocking_overlap_mm3=values))
   for dz in [90,60,30,10,3,0]:clear(lock.translate((0,0,dz)),c,('ingresso fermo',model,slot,dz))
   for dy in [0,10,40,75,101]:
    rr=roof.translate((0,dy,0));clear(rr,lock,'presa fermo/tetto in moto');clear(rr,c,('tetto/cartuccia',model,slot,dy));clear(rr,d,'tetto/SSD');clear(rr,u,'tetto/USB')
   margins=[]
   for angle in range(0,91,5):
    k=g.key(angle);clear(k,c,'perno/cartuccia');clear(k,u,'perno/USB');clear(k,d,'perno/SSD');margins.append(k.distance(u))
   clear(key,u,'perno chiuso/USB')
   fits.append(dict(model=model,slot=slot+1,aperture_width_mm=g.dims(model)['spessore']+.4,aperture_height_mm=g.dims(model)['altezza']+.5,usb_key_min_distance_mm=min(margins+[key.distance(u)]),roof_carrier_distance_mm=roof.distance(c)))
  print('ACCOPPIAMENTI OK',model,flush=True)
 for left,right,slot in itertools.product(models,models,[0,1]):clear(g.carrier(left,slot),g.carrier(right,slot+1),'cartucce adiacenti')
 for dz in [90,60,30,10,3,0]:clear(lock.translate((0,0,dz)),shell,'fermo dall alto')
 # Identita del provino con le superfici funzionali del kit finale.
 cb=parts['PROVINO_BASE_R24'];cf=parts['PROVINO_PIEDE_R24'];cl=parts['PROVINO_FERMO_R24']
 clear(cb,cf,'provino piede/base');clear(cl,cf,'provino fermo/piede');clear(cl,cb,'provino fermo/base')
 for y in [52,64]:
  roi=g.box(7.6,y-.1,9.9,26.8,4.2,6);assert diff(cb.intersect(roi),shell.intersect(roi))<1e-5
  assert diff(cf.intersect(roi),g.carrier('T9').intersect(roi))<1e-5
 for model in models:
  production=g.ring(model);coupon=parts['PROVINO_CORNICE_'+model+'_R24']
  # Le bocche hanno lo stesso invito; il corpo centrale ha la stessa apertura.
  for cy,dy in [(29,-4),(39,4)]:
   roi=g.box(5,cy-.61,9.9,32,1.22,70);assert diff(production.intersect(roi),coupon.translate((0,dy,0)).intersect(roi))<1e-5
  clear(coupon,g.drive(model),'cornice provino/SSD')
 # Tetto e fermo: controllo ripetuto sulla nuova scocca e sui provini esportati.
 top_shell=shell.intersect(g.box(-1,-1,64,92,103,25));local=shell.intersect(g.box(0,88,50,14,14,34));roof_paths=[];key_paths=[]
 for travel in np.linspace(101,0,35):roof_paths.append(dict(travel_mm=float(travel),overlap_mm3=clear(roof.translate((0,float(travel),0)),top_shell,'tetto')))
 for dz in np.linspace(-30,0,31):
  k=g.key(0,float(dz));clear(k,local,'chiave entra/scocca');clear(k,roof,'chiave entra/tetto');key_paths.append(['inserimento',float(dz),0])
 for angle in range(0,91,5):
  k=g.key(angle);clear(k,local,'chiave gira/scocca');clear(k,roof,'chiave gira/tetto');key_paths.append(['rotazione',0,angle])
 for dz in np.linspace(0,-g.C['abbassamento_chiuso_mm'],12):
  k=g.key(90,float(dz));clear(k,local,'chiave scende/scocca');clear(k,roof,'chiave scende/tetto');key_paths.append(['sede',float(dz),90])
 roof_retention=dict(front=ov(roof.translate((0,-.5,0)),top_shell),lift=ov(roof.translate((0,0,.6)),top_shell),key_extraction=ov(key.translate((0,0,-.3)),roof),key_turn=ov(key.rotate((g.CX,g.CY,0),(g.CX,g.CY,100),10),roof),rear=ov(key,roof.translate((0,.6,0))))
 assert all(v>0 for v in roof_retention.values())
 assert diff(parts['PROVINO_GUIDE_SCOCCA_R24'],g.r22.coupon_body(shell))<1e-5 and diff(parts['PROVINO_GUIDE_TETTO_R24'],g.r22.coupon_lid(roof))<1e-5
 assembly=ROOT/'CAD/ASSIEME_R24_NON_STAMPARE.step';s=cq.importers.importStep(str(assembly)).val();assert s.isValid() and len(s.Solids())==10 and all(q.Volume()>0 for q in s.Solids())
 assert np.allclose(g.bounds(s),[[0,-.4,0],[90,109,86]],atol=.001)
 result=dict(result='PASS_GEOMETRIA_E_CINEMATICA_R24',source_manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),parts=records,ssd_checks=fits,cartridge_paths=paths,cartridge_retention=retention,roof_paths=roof_paths,key_paths=key_paths,roof_retention=roof_retention,roof_R22_geometrically_unchanged=True,coupon_functional_surfaces_match=True,assembly=dict(sha256=g.sha(assembly),solids=10,bounds_mm=g.bounds(s)),physical_print=False,physical_fit=False,force_validated=False,thermal_test=False,limitations=['Corpi rettangolari SSD nominali, non scansioni dei rivestimenti.','Moto campionato; nessuna analisi delle forze, fatica o creep del PLA.','Gioco piede .2 mm per lato e .2 verticale sulle rampe = circa .141 normale; da provare fisicamente.','Il fermo frontale si appoggia per gravita: progetto per uso da scrivania in posizione verticale.','Screening mesh esclude triangoli con vertici condivisi.'])
 g.save(ROOT/'verifiche/geometria.json',result);print(json.dumps(dict(result='PASS',parts=len(records),ssd_cases=len(fits),cartridge_poses=len(paths),roof_poses=len(roof_paths),key_poses=len(key_paths))),flush=True)
if __name__=='__main__':main()
