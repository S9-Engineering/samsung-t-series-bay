"""Controlli nominali dello studio, senza qualifica di stampabilita."""
import json
import cadquery as cq
import numpy as np
import trimesh
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT
def overlap(a,b):return sum(s.Volume() for s in a.intersect(b).Solids())
def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());assert m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json') and m['source_sha256']==g.sha(ROOT/'sorgenti/genera.py')
 results=[]
 for q in m['parts']:
  s=cq.importers.importStep(str(ROOT/q['step'])).val();mesh=trimesh.load_mesh(ROOT/q['mesh'],process=True)
  assert s.isValid() and len(s.Solids())==len(mesh.split())==1 and mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
  assert np.allclose(mesh.bounds,g.bounds(s),atol=.04) and abs(mesh.volume/s.Volume()-1)<.005
  assert not np.any(mesh.area_faces<1e-10) and len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
  screening=self_intersections_fast(mesh);assert screening['intersection_pairs']==0
  results.append(dict(name=q['name'],single_valid_solid=True,mesh_closed=True,volume_mm3=float(mesh.volume),bounds_mm=mesh.bounds.tolist(),intersection_screen=screening,step_sha256=g.sha(ROOT/q['step']),mesh_sha256=g.sha(ROOT/q['mesh'])))
  print('EXPORT OK',q['name'],flush=True)
 shell=g.shell_empty();roof=g.r22.lid();fixed=g.union([g.receiver(i) for i in range(3)]);cases=[];paths=[];vertical=[]
 for option in ['A','B','C']:
  for model in g.P['ssd_nominali']:
   for slot in range(3):
    carrier=g.carrier(option,model,slot);d=g.drive(model,slot);u=g.usb(model,slot)
    vals={label:overlap(carrier,s) for label,s in [('disco',d),('base',fixed),('scocca',shell),('tetto',roof),('usb',u)]}
    assert all(v<1e-5 for v in vals.values()),(option,model,slot,vals)
    caps=[]
    if option=='C':
     cap=g.upper_guide(model,slot);caps=[cap]
     assert overlap(cap,d)<1e-5 and overlap(cap,shell)<1e-5 and overlap(cap,u)<1e-5
    # Scorrimento tetto: C muove anche la guida superiore selezionata per quel modello.
    for travel in [0,10,40,75,101]:
     moving=g.union([roof,*caps]) if caps else roof
     assert overlap(moving.translate((0,travel,0)),d)<1e-5
     assert overlap(moving.translate((0,travel,0)),carrier)<1e-5
    cases.append(dict(option=option,model=model,slot=slot+1,overlap_mm3=vals,roof_carrier_distance_mm=roof.distance(carrier),usb_carrier_distance_mm=carrier.distance(u),entry_from_top=option!='B',nominal_channel_total_clearance_mm=.4))
    # Base comune: alzata con intagli allineati a Y-6, poi scorrimento verso il retro.
    for dy in [-6,-4,-2,0]:
     v=overlap(carrier.translate((0,dy,0)),fixed)+overlap(carrier.translate((0,dy,0)),shell)
     assert v<1e-5,('base',option,model,slot,dy,v)
     paths.append(dict(option=option,model=model,slot=slot+1,dy_mm=dy,overlap_mm3=v))
    for dz in [45,15,3,0]:
     entering=carrier.translate((0,-6,dz));v=overlap(entering,fixed)+overlap(entering,shell)
     assert v<1e-5,('ingresso_verticale_base',option,model,slot,dz,v)
     vertical.append(dict(option=option,model=model,slot=slot+1,dy_mm=-6,dz_mm=dz,overlap_mm3=v))
    # Entrata SSD: A/C dall'alto, B assiale da dietro (cartuccia rimossa dalla scocca).
    for travel in [100,60,30,10,0]:
     dd=d.translate((0,travel,0)) if option=='B' else d.translate((0,0,travel))
     assert overlap(dd,carrier)<1e-5,(option,model,slot,travel)
  # Nessuna collisione tra moduli di modelli diversi in slot adiacenti.
  for left in g.P['ssd_nominali']:
   for right in g.P['ssd_nominali']:
    for slot in [0,1]:assert overlap(g.carrier(option,left,slot),g.carrier(option,right,slot+1))<1e-5
 assemblies=[]
 for option in ['A','B','C']:
  path=ROOT/'CAD_STUDIO_NON_STAMPARE'/('ASSIEME_'+option+'_NON_STAMPARE.step');s=cq.importers.importStep(str(path)).val();expected=11 if option=='C' else 8
  assert s.isValid() and len(s.Solids())==expected,(option,len(s.Solids()))
  assemblies.append(dict(option=option,solids=expected,sha256=g.sha(path)))
 # Solo geometria: i giochi di base e gli agganci C sono ancora uno studio.
 data=dict(result='PASS_CONTROLLI_NOMINALI_STUDIO',manifest_sha256=g.sha(ROOT/'verifiche/manifest.json'),parts=results,ssd_cases=cases,base_motion_samples=paths,base_vertical_motion_samples=vertical,assemblies=assemblies,models_per_slot_verified=27,sliced=False,physical_print=False,load_test=False,thermal_test=False,not_print_ready=True,limitations=['Cinematica campionata e geometria nominale: nessuna prova fisica o analisi delle forze.','Innesto a cuneo al basamento da calibrare; non e un aggancio di stampa finalizzato.','Opzione C: fissaggio delle guide al tetto e compatibilita del disegno delle feritoie da sviluppare dopo scelta.','Cornici B con ponti superiori da verificare nel successivo slicing.','Dimensioni SSD nominali, senza rilievo delle curvature, rivestimenti o tolleranze reali.','Tolleranza indicativa .4 mm totale = .2 per lato, non garanzia di assenza di gioco.','Screening autointersezioni non comprende triangoli con vertici condivisi.'])
 g.save(ROOT/'verifiche/controlli_studio.json',data);print(json.dumps(dict(result=data['result'],cases=len(cases),paths=len(paths))),flush=True)
if __name__=='__main__':main()
