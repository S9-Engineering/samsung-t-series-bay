"""Audit R11 rispetto alla R10: cambiano soltanto i raccordi esterni."""
import json
import numpy as np
import cadquery as cq
import genera as g
ROOT=g.ROOT;PRIOR=ROOT.parent/'bay-ssd-universale-r10-feritoie-orizzontali'


def read(path):
    obj=cq.importers.importStep(str(path)).val()
    assert obj.isValid()
    return obj


def diff(a,b):
    value=sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())
    assert value<1e-5,value
    return value


def main():
    body=ROOT/'CAD/scocca_R11.step';lid=ROOT/'CAD/coperchio_R11.step'
    new,old=read(body),read(PRIOR/'CAD/scocca_R10.step')
    roof,old_roof=read(lid),read(PRIOR/'CAD/coperchio_R10.step')
    assert np.allclose(g.bounds(new),g.bounds(old),atol=1e-5)
    assert np.allclose(g.bounds(roof),g.bounds(old_roof),atol=1e-5)
    region=g.box(4,4,0,82,93,83)
    internal=diff(new.intersect(region),old.intersect(region))
    side_region=g.box(-1,8,8,92,85,70)
    roof_region=g.box(3.01,3.01,70,83.98,94.98,20)
    sides=diff(new.intersect(side_region),old.intersect(side_region))
    roof_delta=diff(roof.intersect(roof_region),old_roof.intersect(roof_region))
    body_removed=sum(s.Volume() for s in old.cut(new).Solids())
    roof_removed=sum(s.Volume() for s in old_roof.cut(roof).Solids())
    assert body_removed<1e-5 and roof_removed<1e-5
    identical=[]
    for name in ('inserto_T7','inserto_Shield','provino_sede','provino_chiusura_femmina','provino_chiusura_maschio'):
        path=ROOT/'CAD'/f'{name}_R11.step'
        identical.append(dict(part=name,current_sha256=g.sha(path),
            symmetric_difference_mm3=diff(read(path),read(PRIOR/'CAD'/f'{name}_R10.step'))))
    prior=json.loads((PRIOR/'verifiche/confronto_revisioni.json').read_text())
    assert prior['R05_internal_unchanged']
    old_parameters=json.loads((PRIOR/'sorgenti/parametri.json').read_text())
    changed={'revisione','raggio_esterno','raccordo_bordi','raccordo_tetto_superiore','raccordo_tetto_inferiore'}
    for key in g.P:
        if key not in changed:assert g.P[key]==old_parameters[key],key
    for key in changed-{'revisione'}:assert g.P[key]==0
    checks=json.loads((PRIOR/'verifiche/SHA256.json').read_text())
    assert all(g.sha(PRIOR/p)==h for p,h in checks.items())
    g.save(ROOT/'verifiche/confronto_revisioni.json',dict(
        revision='R11',source_revision='R10',external_dimensions_unchanged=True,
        R05_internal_unchanged=True,horizontal_vents_and_latches_unchanged=True,external_radii_zero=True,
        body=dict(current_sha256=g.sha(body),internal_difference_mm3=internal,side_region_difference_mm3=sides,
                  removed_material_mm3=body_removed,added_external_material_mm3=new.Volume()-old.Volume()),
        lid=dict(current_sha256=g.sha(lid),functional_region_difference_mm3=roof_delta,
                 removed_material_mm3=roof_removed,added_external_material_mm3=roof.Volume()-old_roof.Volume()),
        identical_parts=identical,R10_hashed_files_preserved=len(checks),
        physical_print=False,thermal_validation=False))
    print('SPIGOLI ESTERNI NETTI; INTERNI, FORATURE E AGGANCI R10 CONSERVATI',flush=True)


if __name__=='__main__':main()
