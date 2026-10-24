"""R25: aggiunge il marchio completo alla faccia esterna della coda R24.
Coordinate in mm. Il logo e leggibile dal retro (+Y); gli interni restano R24.
"""
from pathlib import Path
import json
import cadquery as cq
import numpy as np
import geometria_r24 as r24
ROOT=Path(__file__).resolve().parents[1];P=json.loads((ROOT/'sorgenti/parametri.json').read_text())
box=r24.box;union=r24.union;bounds=r24.bounds;mesh_of=r24.mesh_of;save=r24.save;sha=r24.sha
oriented=r24.oriented;drive=r24.drive;usb_keepout=r24.usb_keepout;carrier=r24.carrier
def logo_shapes():
 p=P['logo_posteriore'];data=json.loads((ROOT/'sorgenti'/p['sorgente']).read_text())
 assert data['name']=='logo_S9_Engineering' and data['glyphs']==13
 assert sha(ROOT/data['source_png'])==data['source_png_sha256'] and sha(ROOT/data['vector_svg'])==data['vector_svg_sha256']
 w=p['larghezza_mm'];h=w*data['normalized_height'];left=p['centro_x_mm']-w/2;low=p['centro_z_mm']-h/2
 back=P['profondita']+P['retro_coperchio']['arretramento_esterno_mm'];y=back-p['sovrapposizione_mm'];depth=p['rilievo_mm']+p['sovrapposizione_mm']
 def wire(points):return cq.Wire.makePolygon([cq.Vector(left+w-u*w,y,low+v*w) for u,v in points],close=True)
 return [cq.Solid.extrudeLinear(wire(q['outer']),[wire(h) for h in q['holes']],cq.Vector(0,depth,0)) for q in data['shapes']]
def lid():return union([r24.lid(),*logo_shapes()])
def main():
 roof=lid();body=r24.shell()
 definitions=[('SCOCCA_R25',body,'none'),('TETTO_R25_LOGO_ENGINEERING',roof,'flip'),('PERNO_R25_NASCOSTO',r24.key(),'key'),('FERMO_CARTUCCE_R25',r24.front_lock(),'none'),*[('CARTUCCIA_'+m+'_R25',r24.carrier(m),'none') for m in P['ssd_nominali']]]
 rows=[]
 for name,s,mode in definitions:
  assert s.isValid() and len(s.Solids())==1,name
  print('ESPORTO',name,flush=True);ps=oriented(s,mode)
  step=ROOT/'CAD'/(name+'.step');pstep=ROOT/'CAD'/(name+'_STAMPA.step');stl=ROOT/'stampa/STL'/(name+'.stl');ply=ROOT/'verifiche/mesh_assieme'/(name+'.ply')
  cq.exporters.export(s,str(step));cq.exporters.export(ps,str(pstep));cq.exporters.export(ps,str(stl),tolerance=.035,angularTolerance=.08);mesh_of(s).export(ply)
  rows.append(dict(name=name,quantity=1,orientation=mode,stl=str(stl.relative_to(ROOT)),step=str(step.relative_to(ROOT)),print_step=str(pstep.relative_to(ROOT)),mesh=str(ply.relative_to(ROOT)),stl_sha256=sha(stl),step_sha256=sha(step),print_step_sha256=sha(pstep),bounds_mm=bounds(s),print_bounds_mm=bounds(ps),volume_mm3=s.Volume()))
 assy=cq.Assembly(name='BAY_R25_ASSIEME_NON_STAMPARE')
 for name,s,col in [('scocca',body,'#30363c'),('tetto',roof,'#30363c'),('perno',r24.closed_key(),'#547c94'),('fermo',r24.front_lock(),'#30363c')]:assy.add(s,name=name,color=cq.Color(col))
 for i,m in enumerate(P['ssd_nominali']):assy.add(r24.carrier(m,i),name='cartuccia_'+m,color=cq.Color('#30363c'));assy.add(drive(m,i),name=m,color=cq.Color(P['colori'][m]))
 assy.save(str(ROOT/'CAD/ASSIEME_R25_NON_STAMPARE.step'))
 save(ROOT/'verifiche/manifest.json',dict(revision=P['revisione'],unit='millimeter',source_sha256=sha(ROOT/'sorgenti/genera.py'),parameters_sha256=sha(ROOT/'sorgenti/parametri.json'),parts=rows,full_kit_count=7,external_dimensions_mm=[90,109.8,86],logo_glyphs=13,logo_bounds_mm=bounds(cq.Compound.makeCompound(logo_shapes())),physical_print=False,physical_fit=False,sent_to_printer=False))
 print('EXPORT R25 COMPLETATO',flush=True)
if __name__=='__main__':main()
