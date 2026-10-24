"""R26: due perni identici, supporti speculari e cartucce B invariate.

mm. Fronte Y0, USB +Y. Il secondo fermo ripete la geometria R24/R25.
"""
from pathlib import Path
from functools import lru_cache
import json
import cadquery as cq
import geometria_r25 as r25
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'sorgenti/parametri.json').read_text())
r24=r25.r24;r22=r24.r22;C=r22.C;CX=r22.CX;CY=r22.CY;W=P['larghezza']
box=r25.box;union=r25.union;bounds=r25.bounds;mesh_of=r25.mesh_of;save=r25.save;sha=r25.sha
oriented=r25.oriented;drive=r25.drive;usb_keepout=r25.usb_keepout
carrier=r24.carrier;front_lock=r24.front_lock;logo_shapes=r25.logo_shapes
def mirrored(s):return s.mirror('YZ',(W/2,0,0))
@lru_cache(None)
def extra_body_support():
 ear=r22.profile(C['supporto_scocca_xz'],*([C['supporto_scocca_y_mm'][0],C['supporto_scocca_y_mm'][1]-C['supporto_scocca_y_mm'][0]]))
 return mirrored(ear.cut(r22.slot(50,33,C['foro_xy_mm'])).clean())
@lru_cache(None)
def shell():return union([r24.shell(),extra_body_support()])
@lru_cache(None)
def lid_structure():return union([r24.lid(),mirrored(r22.receiver())])
@lru_cache(None)
def lid():return union([lid_structure(),*logo_shapes()])
def key(angle=0,dz=0,side=0):
 s=r24.key(angle,dz)
 return mirrored(s) if side else s
def closed_key(side=0):return key(90,-C['abbassamento_chiuso_mm'],side)
def coupon_body():return r22.coupon_body(shell())
def coupon_lid():
 # Provino senza logo. Alleggerimenti simmetrici lasciano integri entrambi i ricevitori.
 y=P['guide_scorrevoli']['provino_inizio_y_mm']
 s=lid_structure().intersect(box(-1,y,50,W+2,42,40))
 return s.cut(box(15,y+4,82.9,W-30,104-y-4,3.2),box(16,101.2,56.9,W-32,8,22.6)).clean()
def main():
 definitions=[
 ('SCOCCA_R26_DOPPIO_PERNO',shell(),'none',1,'COMPLETO'),
 ('TETTO_R26_DOPPIO_PERNO',lid(),'flip',1,'COMPLETO'),
 ('PERNO_R26_NASCOSTO',key(),'key',2,'COMPLETO_E_PROVINO'),
 ('FERMO_CARTUCCE_R26',front_lock(),'none',1,'COMPLETO'),
 *[('CARTUCCIA_'+m+'_R26',carrier(m),'none',1,'COMPLETO') for m in P['ssd_nominali']],
 ('PROVINO_GUIDE_SCOCCA_R26',coupon_body(),'none',1,'PROVINO'),
 ('PROVINO_GUIDE_TETTO_R26',coupon_lid(),'flip',1,'PROVINO')]
 rows=[]
 for name,s,mode,qty,role in definitions:
  assert s.isValid() and len(s.Solids())==1,(name,s.isValid(),len(s.Solids()))
  print('ESPORTO',name,flush=True);ps=oriented(s,mode)
  step=ROOT/'CAD'/(name+'.step');pstep=ROOT/'CAD'/(name+'_STAMPA.step');stl=ROOT/'stampa/STL'/(name+'.stl');ply=ROOT/'verifiche/mesh_assieme'/(name+'.ply')
  cq.exporters.export(s,str(step));cq.exporters.export(ps,str(pstep));cq.exporters.export(ps,str(stl),tolerance=.035,angularTolerance=.08);mesh_of(s).export(ply)
  rows.append(dict(name=name,quantity=qty,role=role,orientation=mode,stl=str(stl.relative_to(ROOT)),step=str(step.relative_to(ROOT)),print_step=str(pstep.relative_to(ROOT)),mesh=str(ply.relative_to(ROOT)),stl_sha256=sha(stl),step_sha256=sha(step),print_step_sha256=sha(pstep),bounds_mm=bounds(s),print_bounds_mm=bounds(ps),volume_mm3=s.Volume()))
 assy=cq.Assembly(name='BAY_R26_ASSIEME_NON_STAMPARE')
 for name,s,col in [('scocca',shell(),'#30363c'),('tetto',lid(),'#30363c'),('perno_sx',closed_key(0),'#547c94'),('perno_dx',closed_key(1),'#547c94'),('fermo',front_lock(),'#30363c')]:assy.add(s,name=name,color=cq.Color(col))
 for i,m in enumerate(P['ssd_nominali']):assy.add(carrier(m,i),name='cartuccia_'+m,color=cq.Color('#30363c'));assy.add(drive(m,i),name=m,color=cq.Color(P['colori'][m]))
 assy.save(str(ROOT/'CAD/ASSIEME_R26_NON_STAMPARE.step'))
 save(ROOT/'verifiche/manifest.json',dict(revision=P['revisione'],unit='millimeter',source_sha256=sha(ROOT/'sorgenti/genera.py'),parameters_sha256=sha(ROOT/'sorgenti/parametri.json'),geometry_dependencies={p.name:sha(p) for p in (ROOT/'sorgenti').glob('*.py') if p.name in ['geometria_r25.py','geometria_r24.py','involucro_r22.py','base_r15.py']},parts=rows,full_kit_count=8,full_kit_types=7,coupon_count=4,external_dimensions_mm=[90,109.8,86],logo_glyphs=13,logo_bounds_mm=bounds(cq.Compound.makeCompound(logo_shapes())),pin_axes_x_mm=[CX,W-CX],physical_full_kit_print=False,physical_double_pin_test=False,sent_to_printer=False))
 print('EXPORT R26 COMPLETATO',flush=True)
if __name__=='__main__':main()
