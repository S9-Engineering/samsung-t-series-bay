# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""R25: aggiunge il marchio completo alla faccia esterna della coda R24.
Coordinate in mm. Il logo e leggibile dal retro (+Y); gli interni restano R24.
"""
from pathlib import Path
import json
import cadquery as cq
import numpy as np
import cartridge_geometry as r24
ROOT=Path(__file__).resolve().parents[1];P=json.loads((ROOT/'source/parameters.json').read_text())
box=r24.box;union=r24.union;bounds=r24.bounds;mesh_of=r24.mesh_of;save=r24.save;sha=r24.sha
oriented=r24.oriented;drive=r24.drive;usb_keepout=r24.usb_keepout;carrier=r24.carrier
def logo_shapes():
 p=P['logo_posteriore'];data=json.loads((ROOT/'source'/p['sorgente']).read_text())
 assert data['name']=='logo_S9_Engineering' and data['glyphs']==13
 assert sha(ROOT/data['source_png'])==data['source_png_sha256'] and sha(ROOT/data['vector_svg'])==data['vector_svg_sha256']
 w=p['larghezza_mm'];h=w*data['normalized_height'];left=p['centro_x_mm']-w/2;low=p['centro_z_mm']-h/2
 back=P['profondita']+P['retro_coperchio']['arretramento_esterno_mm'];y=back-p['sovrapposizione_mm'];depth=p['rilievo_mm']+p['sovrapposizione_mm']
 def wire(points):return cq.Wire.makePolygon([cq.Vector(left+w-u*w,y,low+v*w) for u,v in points],close=True)
 return [cq.Solid.extrudeLinear(wire(q['outer']),[wire(h) for h in q['holes']],cq.Vector(0,depth,0)) for q in data['shapes']]
def lid():return union([r24.lid(),*logo_shapes()])
