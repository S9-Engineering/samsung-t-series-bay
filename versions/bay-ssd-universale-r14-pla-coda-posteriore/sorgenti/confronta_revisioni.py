"""R14 rispetto alla R13: coda posteriore aggiunta soltanto al coperchio."""
import json
import cadquery as cq
import genera as g
ROOT=g.ROOT
PRIOR=ROOT.parent/'bay-ssd-universale-r13-pla-s9-rilievo'

def read(path):
    obj=cq.importers.importStep(str(path)).val();assert obj.isValid();return obj

def delta(a,b):
    return sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())

def main():
    previous=json.loads((PRIOR/'verifiche/confronto_revisioni.json').read_text());assert previous['R05_internal_unchanged']
    rows=[]
    for name in ('scocca','inserto_T7','inserto_Shield'):
        current=ROOT/'CAD'/f'{name}_R14.step';old=PRIOR/'CAD'/f'{name}_R13.step'
        difference=delta(read(current),read(old));assert difference<1e-5
        rows.append(dict(part=name,current_sha256=g.sha(current),previous_sha256=g.sha(old),symmetric_difference_mm3=difference))
    path=ROOT/'CAD/coperchio_R14.step';a=read(path);b=read(PRIOR/'CAD/coperchio_R13.step')
    removed=sum(s.Volume() for s in b.cut(a).Solids());assert removed<1e-5
    old_region=g.box(-1,-1,0,92,102,90)
    functional=delta(a.intersect(old_region),b);assert functional<1e-5
    added=a.cut(b);region=g.box(-1,101,51,92,9,36)
    outside=sum(s.Volume() for s in added.cut(region).Solids());assert outside<1e-5
    original=json.loads((PRIOR/'verifiche/SHA256.json').read_text());assert all(g.sha(PRIOR/p)==h for p,h in original.items())
    g.save(ROOT/'verifiche/confronto_revisioni.json',dict(result='PASS',previous_revision=PRIOR.name,
        R05_internal_unchanged=True,body_and_inserts_identical=True,horizontal_vents_and_latches_unchanged=True,
        external_radii_zero=True,parts=rows,lid=dict(current_sha256=g.sha(path),removed_material_mm3=removed,
            original_region_difference_mm3=functional,added_material_mm3=a.Volume()-b.Volume(),addition_outside_rear_region_mm3=outside),
        note='Solo prolungamento del tetto e coda superiore posteriore con due corti risvolti. Sei pezzi e zero ferramenta, come R13.'))
    g.save(ROOT/'verifiche/conservazione_R13.json',dict(original_project=PRIOR.name,original_files_checked=len(original),original_manifest_sha256=g.sha(PRIOR/'verifiche/SHA256.json'),hashes_unchanged=True))
    print('PASS: SOLO CODA POSTERIORE AGGIUNTA AL COPERCHIO; R13 CONSERVATA',flush=True)

if __name__=='__main__':main()
