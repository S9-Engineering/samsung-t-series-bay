# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""R27: due perni identici, supporti speculari e cartucce B invariate.

mm. Fronte Y0, USB +Y. Il secondo fermo ripete la geometria R24/R25.
"""
from pathlib import Path
from functools import lru_cache
import json
import cadquery as cq
import lid_geometry as r25
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'source/parameters.json').read_text())
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
