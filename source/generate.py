"""Current SSD enclosure CAD, in millimetres.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
from pathlib import Path
import hashlib,json
import cadquery as cq
import base_geometry as core

ROOT=Path(__file__).resolve().parents[1]
P=core.P
VERSION=(ROOT/'VERSION').read_text().strip()
sha=core.sha
save=core.save

def catalog():
    return {
        'shell':(core.shell(),'none',1),
        'lid':(core.lid(),'flip',1),
        'locking-pin':(core.key(),'key',2),
        'cartridge-stop':(core.front_lock(),'key',1),
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
        mesh_path=ROOT/'verification/meshes'/f'{name}.ply'
        mesh_path.parent.mkdir(parents=True,exist_ok=True)
        core.mesh_of(shape).export(mesh_path)
        rows.append({'name':name,'quantity':quantity,'orientation':mode,
                     **{k:str(p.relative_to(ROOT)) for k,p in paths.items()},
                     'stl_sha256':sha(paths['stl']),
                     'volume_mm3':shape.Volume(),
                     'sha256':{k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()}})
    out=ROOT/'verification/manifest.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({'version':VERSION,'unit':'millimeter','parts':rows,'full_kit_count':8,
                              'source_sha256':sha(Path(__file__)),
                              'parameters_sha256':sha(ROOT/'source/parameters.json'),
                              'geometry_inputs_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'source').glob('*')) if p.name in ['generate.py','base_geometry.py','cartridge_geometry.py','lid_geometry.py','locking_geometry.py','shell_geometry.py','parameters.json','front-logo-outlines.json']},
                              'physical_tests_added':False},indent=2)+'\n')
    assembly=cq.Assembly()
    assembly.add(core.shell(),name='shell')
    assembly.add(core.lid(),name='lid')
    assembly.add(core.front_lock(),name='cartridge-stop')
    for i,model in enumerate(core.P['ssd_nominali']):
        assembly.add(core.carrier(model).translate((24*i,0,0)),name='cartridge-'+model.lower().replace('_','-'))
    for side in [0,1]:assembly.add(core.closed_key(side),name='locking-pin-'+str(side+1))
    assembly.save(str(ROOT/'cad/reference-assembly-do-not-print.step'))
    print('Exported current seven part types / eight components.')

if __name__=='__main__':main()
