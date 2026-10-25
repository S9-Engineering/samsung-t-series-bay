"""Reopen current exports; check R28 geometry and archived print identity.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
import itertools
import subprocess
import cadquery as cq
import numpy as np
import trimesh
import generate as g
from mesh_intersections import self_intersections_fast


def volume(s):
    return sum(q.Volume() for q in s.Solids())


def main():
    checks=[];shapes={}
    for name,(model,mode,quantity) in g.catalog().items():
        step=g.ROOT/'cad'/f'{name}.step';stl=g.ROOT/'print/stl'/f'{name}.stl'
        exported=cq.importers.importStep(str(step)).val()
        printing=cq.importers.importStep(str(g.ROOT/'cad/print'/f'{name}.step')).val()
        mesh=trimesh.load_mesh(stl,process=True)
        assert model.isValid() and exported.isValid() and printing.isValid()
        assert len(exported.Solids())==len(printing.Solids())==1,name
        assert volume(model.cut(exported))+volume(exported.cut(model))<1e-4,name
        expected=g.core.oriented(exported,mode)
        assert volume(expected.cut(printing))+volume(printing.cut(expected))<1e-5,name
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0,name
        assert len(mesh.split(only_watertight=False))==1,name
        assert np.all(mesh.area_faces>1e-10),name
        assert len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces),name
        assert np.allclose(mesh.bounds,g.core.bounds(printing),atol=.04),name
        assert np.allclose(mesh.bounds[0],0,atol=1e-5),name
        assert abs(mesh.volume/exported.Volume()-1)<.005,name
        screen=self_intersections_fast(mesh)
        assert screen['intersection_pairs']==0,(name,screen)
        shapes[name]=exported
        checks.append(dict(part=name,quantity=quantity,source_matches_export=True,
                           step_solid_count=1,watertight=True,winding_consistent=True,
                           positive_volume=True,no_degenerate_or_duplicate_faces=True,
                           bounds_mm=mesh.bounds.tolist(),stl_sha256=g.sha(stl),
                           self_intersection_screen=screen))
        print('Verified',name,flush=True)
    shell,lid,stop=map(shapes.get,['shell','lid','cartridge-stop'])
    sb=np.array(g.core.bounds(stop));assert np.isclose(sb[1,0]-sb[0,0],83.5)
    assert np.isclose(g.core.bounds(lid)[1][1],109)
    assert volume(shell.intersect(lid))<1e-6 and volume(stop.intersect(lid))<1e-6
    for dx,z in itertools.product([-.25,0,.25],np.linspace(0,80,17)):
        assert volume(shell.intersect(stop.translate((dx,0,float(z)))))<1e-6,(dx,z)
    fits=[]
    for model,slot in itertools.product(['t7','t7-shield','t9'],range(3)):
        carrier=shapes['cartridge-'+model].translate((24*slot,0,0))
        assert volume(stop.intersect(carrier))<1e-6
        assert volume(lid.intersect(carrier))<1e-6
        overlaps=[]
        for dx,foot_dx in itertools.product([-.25,0,.25],[-.2,.2]):
            overlap=volume(stop.translate((dx,0,0)).intersect(carrier.translate((foot_dx,-.5,0))))
            assert overlap>0,(model,slot,dx,foot_dx)
            overlaps.append(overlap)
        fits.append(dict(model=model,slot=slot+1,nominal_interference_mm3=0,
                         minimum_blocking_overlap_volume_mm3=min(overlaps)))
    historical={}
    for name,old in [('cartridge-stop','cartridge-stop-r28'),('lid','lid-plain-r28')]:
        path='versions/r28-stop-wings-plain-rear/cad/'+old+'.step'
        saved=subprocess.run(['git','show','b0ebe1e:'+path],cwd=g.ROOT,capture_output=True)
        if saved.returncode:
            historical[name]=dict(status='SKIPPED',reason='Full Git history unavailable; current geometry checks still performed.')
            continue
        raw=saved.stdout
        target=g.ROOT/'.cache/verification'/f'{name}.step';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        previous=cq.importers.importStep(str(target)).val()
        delta=volume(previous.cut(shapes[name]))+volume(shapes[name].cut(previous))
        assert delta<1e-4,(name,delta)
        historical[name]=dict(source_commit='b0ebe1e',symmetric_difference_mm3=delta)
    report=dict(result='PASS',revision='R28',parts=checks,full_kit_count=8,
                manifest_sha256=g.sha(g.ROOT/'verification/manifest.json'),
                stop_width_after_mm=83.5,side_clearance_mm=.25,
                maximum_nominal_lateral_travel_mm=.5,vertical_removal_poses=51,
                cartridge_checks=fits,exact_previous_r28_design=historical,
                physical_test_scope='User approved the repository update after the R28 stop-only project was opened; no dimensional, cycling or thermal evidence was supplied.',
                limitations=['Self-intersection screening excludes pairs sharing a vertex.',
                             'Nominal CAD checks do not establish holding force or thermal performance.'],
                physical_fit_verified=False,sent_to_printer=False)
    g.save(g.ROOT/'verification/geometry.json',report)
    g.save(g.ROOT/'verification/current-exports.json',report)
    print('Current R28 geometry and all nine cartridge positions: PASS',flush=True)


if __name__=='__main__':main()
