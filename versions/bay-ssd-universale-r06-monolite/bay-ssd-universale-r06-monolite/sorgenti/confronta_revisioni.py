"""Controlla l'esterno approvato e l'interno R05 sui STEP finali R06.

Audit di provenienza facoltativo per la rigenerazione: richiede le due cartelle
precedenti, che non servono invece a genera.py per produrre i modelli R06.
"""
import json
import cadquery as cq
import genera as g

ROOT=g.ROOT
R05=ROOT.parent/'bay-ssd-universale-r05-incastri'
STUDIO=ROOT.parent/'bay-ssd-universale-r06-studio-monolite'


def read(path):
    obj=cq.importers.importStep(str(path)).val()
    assert obj.isValid()
    return obj


def difference(a,b):
    value=sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())
    assert value<1e-5,value
    return value


def main():
    roi=g.box(3,3,0,84,95,86)
    checks=[]
    for name in ('scocca','coperchio'):
        actual=read(ROOT/'CAD'/f'{name}_R06.step')
        approved=read(STUDIO/'CAD_studio'/f'{name}_R06_STUDIO.step')
        prior=read(R05/'CAD'/f'{name}_R05.step')
        checks.append(dict(part=name,approved_study_symmetric_difference_mm3=difference(actual,approved),
            R05_internal_symmetric_difference_mm3=difference(actual.intersect(roi),prior.intersect(roi)),
            current_sha256=g.sha(ROOT/'CAD'/f'{name}_R06.step'),
            approved_sha256=g.sha(STUDIO/'CAD_studio'/f'{name}_R06_STUDIO.step')))
    unchanged=[]
    for name in ('inserto_T7','inserto_Shield','provino_sede','provino_chiusura_femmina','provino_chiusura_maschio'):
        newpath=ROOT/'CAD'/f'{name}_R06.step';oldpath=R05/'CAD'/f'{name}_R05.step'
        unchanged.append(dict(part=name,symmetric_difference_mm3=difference(read(newpath),read(oldpath)),
            R06_sha256=g.sha(newpath),R05_sha256=g.sha(oldpath)))
    # Tutti i file delle revisioni di partenza devono restare integri.
    preserved=[]
    for ref in (R05,STUDIO):
        hashes=json.loads((ref/'verifiche/SHA256.json').read_text())
        failures=[p for p,h in hashes.items() if g.sha(ref/p)!=h]
        assert not failures,(ref,failures)
        preserved.append(dict(folder=ref.name,files_checked=len(hashes),unchanged=True))
    g.save(ROOT/'verifiche/confronto_revisioni.json',dict(
        revision='R06',approved_exterior_unchanged=True,R05_internal_unchanged=True,
        exterior_and_internal=checks,identical_parts=unchanged,prior_revisions=preserved,
        physical_validation=False))
    print('ESTERNO APPROVATO E INTERNI R05 CONFERMATI',flush=True)


if __name__=='__main__':main()
