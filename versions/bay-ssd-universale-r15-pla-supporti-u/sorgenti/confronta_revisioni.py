"""Confronto R15/R14: scocca riutilizzabile, modifiche limitate a ricambi."""
import json
import cadquery as cq
import genera as g
from verifica import overlap
ROOT=g.ROOT

def main():
    old=ROOT.parent/'bay-ssd-universale-r14-pla-coda-posteriore'
    checks=json.loads((old/'verifiche/SHA256.json').read_text())
    assert all(g.sha(old/p)==h for p,h in checks.items())
    before=cq.importers.importStep(str(old/'CAD/scocca_R14.step')).val()
    after=cq.importers.importStep(str(ROOT/'CAD/scocca_R15.step')).val()
    delta=sum(s.Volume() for s in before.cut(after).Solids())+sum(s.Volume() for s in after.cut(before).Solids())
    assert delta<1e-5
    old_lid=cq.importers.importStep(str(old/'CAD/coperchio_R14.step')).val()
    new_lid=cq.importers.importStep(str(ROOT/'CAD/coperchio_R15.step')).val()
    # Tetto esterno e griglia identici; coda accorciata in altezza di 1 mm.
    roi=g.box(-1,-1,83,g.W+2,112,4)
    a,b=old_lid.intersect(roi),new_lid.intersect(roi)
    roof_delta=sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())
    assert roof_delta<1e-5
    g.save(ROOT/'verifiche/confronto_revisioni.json',dict(result='PASS',
        previous_revision='R14',previous_hashed_files_preserved=len(checks),body_identical=True,
        body_symmetric_difference_mm3=delta,roof_and_grille_difference_mm3=roof_delta,
        body_step_sha256=g.sha(ROOT/'CAD/scocca_R15.step'),lid_step_sha256=g.sha(ROOT/'CAD/coperchio_R15.step'),
        changes=['Culle bilaterali a U al posto degli spessori laterali; scocca R14 riutilizzabile',
            'Alette larghe 9 anziche 8 mm; pattini con interferenza nominale di 0,15 mm per lato',
            'Bordo inferiore coda da Z56 a Z57 per compensare base culle 1,2 mm'],
        physical_fit=False))
    print('CONFRONTO R14/R15 PASS: scocca identica, tetto esterno identico',flush=True)

if __name__=='__main__':main()
