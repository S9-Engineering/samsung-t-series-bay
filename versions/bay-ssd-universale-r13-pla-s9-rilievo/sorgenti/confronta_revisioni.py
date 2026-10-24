"""Confronto geometrico R13 PLA con la R12 approvata, senza modificare la R12."""
import json
import cadquery as cq
import genera as g
ROOT=g.ROOT
PRIOR=ROOT.parent/'bay-ssd-universale-r12-logo-s9'

def main():
    previous=json.loads((PRIOR/'verifiche/confronto_revisioni.json').read_text())
    assert previous['R05_internal_unchanged']
    rows=[]
    for name in ('scocca','coperchio','inserto_T7','inserto_Shield'):
        current=ROOT/'CAD'/f'{name}_R13.step'
        old=PRIOR/'CAD'/f'{name}_R12.step'
        a=cq.importers.importStep(str(current)).val()
        b=cq.importers.importStep(str(old)).val()
        assert a.isValid() and b.isValid()
        delta=sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())
        assert delta<1e-5,(name,delta)
        rows.append(dict(part=name,current_sha256=g.sha(current),previous_sha256=g.sha(old),symmetric_difference_mm3=delta))
    original=json.loads((PRIOR/'verifiche/SHA256.json').read_text())
    assert all(g.sha(PRIOR/p)==h for p,h in original.items())
    g.save(ROOT/'verifiche/conservazione_R12.json',dict(original_files_checked=len(original),original_manifest_sha256=g.sha(PRIOR/'verifiche/SHA256.json'),hashes_unchanged=True))
    g.save(ROOT/'verifiche/confronto_revisioni.json',dict(result='PASS',previous_revision=PRIOR.name,
        kit_geometry_identical=True,R05_internal_unchanged=True,horizontal_vents_and_latches_unchanged=True,
        external_radii_zero=True,logo_relief_mm=g.P['logo_frontale']['rilievo_mm'],parts=rows,
        note='Geometria del kit identica alla R12 approvata; profili PLA, Fuzzy Skin disattivata e nessun provino nella consegna. Forza e durata degli incastri non validate fisicamente.'))
    print('R13 IDENTICA ALLA R12 NELLE QUATTRO PARTI DEL KIT; R12 CONSERVATA',flush=True)

if __name__=='__main__':main()
