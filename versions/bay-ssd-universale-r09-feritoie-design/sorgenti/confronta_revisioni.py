"""Audit R09: involucro, interni e agganci conservati; solo fianchi forati."""
import json
import numpy as np
import cadquery as cq
import genera as g
ROOT=g.ROOT;R06=ROOT.parent/'bay-ssd-universale-r06-monolite'


def read(path):
    obj=cq.importers.importStep(str(path)).val()
    assert obj.isValid()
    return obj


def diff(a,b):
    value=sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())
    assert value<1e-5,value
    return value


def main():
    body=ROOT/'CAD/scocca_R09.step';lid=ROOT/'CAD/coperchio_R09.step'
    new,old=read(body),read(R06/'CAD/scocca_R06.step')
    assert np.allclose(g.bounds(new),g.bounds(old),atol=1e-5)
    region=g.box(4,4,0,82,93,83)
    internal=diff(new.intersect(region),old.intersect(region))
    roof_delta=diff(read(lid),read(R06/'CAD/coperchio_R06.step'))
    identical=[]
    for name in ('inserto_T7','inserto_Shield','provino_sede','provino_chiusura_femmina','provino_chiusura_maschio'):
        path=ROOT/'CAD'/f'{name}_R09.step'
        identical.append(dict(part=name,current_sha256=g.sha(path),
            symmetric_difference_mm3=diff(read(path),read(R06/'CAD'/f'{name}_R06.step'))))
    prior=json.loads((R06/'verifiche/confronto_revisioni.json').read_text())
    assert prior['R05_internal_unchanged']
    p06=json.loads((R06/'sorgenti/parametri.json').read_text())
    for key in ('slot','coperchio','piedini','ventilazione','ssd_nominali'):
        assert g.P[key]==p06[key],key
    checks=json.loads((R06/'verifiche/SHA256.json').read_text())
    assert all(g.sha(R06/p)==h for p,h in checks.items())
    g.save(ROOT/'verifiche/confronto_revisioni.json',dict(
        revision='R09',monolith_envelope_unchanged=True,R05_internal_unchanged=True,R06_horizontal_roof_restored=True,
        body=dict(current_sha256=g.sha(body),internal_difference_mm3=internal),
        lid=dict(current_sha256=g.sha(lid),symmetric_difference_mm3=roof_delta),
        identical_parts=identical,R06_hashed_files_preserved=len(checks),
        physical_print=False,thermal_validation=False))
    print('INTERNI CONSERVATI E TETTO ORIZZONTALE R06 RIPRISTINATO',flush=True)


if __name__=='__main__':main()
