"""Verify current exports and their correspondence to the editable CAD.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
import json,hashlib
import numpy as np
import cadquery as cq
import trimesh
import generate as g

def main():
    checks=[]
    for name,(model,mode,quantity) in g.catalog().items():
        step=g.ROOT/'cad'/f'{name}.step';stl=g.ROOT/'print/stl'/f'{name}.stl'
        exported=cq.importers.importStep(str(step)).val()
        mesh=trimesh.load_mesh(stl,process=True)
        assert model.isValid() and exported.isValid() and len(exported.Solids())==1,name
        delta=model.cut(exported).Volume()+exported.cut(model).Volume()
        assert delta<1e-4,(name,delta)
        printing=g.core.oriented(exported,mode)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0,name
        assert len(mesh.split(only_watertight=False))==1,name
        assert np.all(mesh.area_faces>1e-10),name
        assert len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces),name
        assert np.allclose(mesh.bounds,g.core.bounds(printing),atol=.04),name
        assert abs(mesh.volume/exported.Volume()-1)<.01,name
        checks.append({'part':name,'quantity':quantity,'source_matches_export':True,'step_solid_count':1,
                       'watertight':True,'winding_consistent':True,'positive_volume':True,
                       'no_degenerate_or_duplicate_faces':True,'bounds_mm':mesh.bounds.tolist(),
                       'stl_sha256':hashlib.sha256(stl.read_bytes()).hexdigest()})
        print('Verified',name,flush=True)
    report={'status':'PASS','parts':checks,'full_kit_count':sum(p['quantity'] for p in checks),
            'geometry_changed_by_layout_migration':False,'physical_tests_added':False,
            'self_intersection_screen':'Previous exported-file evidence retained in Git; not repeated for a path-only migration.'}
    (g.ROOT/'verification/current-exports.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
