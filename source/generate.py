"""Current SSD enclosure CAD, in millimetres.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
from pathlib import Path
import hashlib,json
import cadquery as cq
import base_geometry as core

ROOT=Path(__file__).resolve().parents[1]

def catalog():
    return {
        'shell':(core.shell(),'none',1),
        'lid':(core.lid(),'flip',1),
        'locking-pin':(core.key(),'key',2),
        'cartridge-stop':(core.front_lock(),'none',1),
        **{'cartridge-'+model.lower().replace('_','-'):(core.carrier(model),'none',1)
           for model in core.P['ssd_nominali']},
    }

def main():
    rows=[]
    for name,(shape,mode,quantity) in catalog().items():
        assert shape.isValid() and len(shape.Solids())==1,name
        printing=core.oriented(shape,mode)
        paths={'step':ROOT/'cad'/f'{name}.step',
               'print_step':ROOT/'cad/print'/f'{name}.step',
               'stl':ROOT/'print/stl'/f'{name}.stl'}
        for p in paths.values():p.parent.mkdir(parents=True,exist_ok=True)
        cq.exporters.export(shape,str(paths['step']))
        cq.exporters.export(printing,str(paths['print_step']))
        cq.exporters.export(printing,str(paths['stl']),tolerance=.035,angularTolerance=.08)
        rows.append({'name':name,'quantity':quantity,'orientation':mode,
                     **{k:str(p.relative_to(ROOT)) for k,p in paths.items()},
                     'volume_mm3':shape.Volume(),
                     'sha256':{k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()}})
    out=ROOT/'verification/manifest.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({'unit':'millimeter','parts':rows,'full_kit_count':8,'physical_tests_added':False},indent=2)+'\n')
    print('Exported current seven part types / eight components.')

if __name__=='__main__':main()
