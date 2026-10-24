"""Audit di conservazione rispetto alla R06 e verifica del tetto piatto."""
import json
import cadquery as cq
import genera as g
ROOT=g.ROOT
R06=ROOT.parent/'bay-ssd-universale-r06-monolite'
R07=ROOT.parent/'bay-ssd-universale-r07-studio-top-forato'


def read(path):
    obj=cq.importers.importStep(str(path)).val()
    assert obj.isValid()
    return obj


def diff(a,b):
    value=sum(s.Volume() for s in a.cut(b).Solids())+sum(s.Volume() for s in b.cut(a).Solids())
    assert value<1e-5,value
    return value


def main():
    body=ROOT/'CAD/scocca_R08.step';lid=ROOT/'CAD/coperchio_R08.step'
    body_delta=diff(read(body),read(R06/'CAD/scocca_R06.step'))
    new_lid,old_lid=read(lid),read(R06/'CAD/coperchio_R06.step')
    roi=g.box(-1,-1,70,92,103,13)
    attachment_delta=diff(new_lid.intersect(roi),old_lid.intersect(roi))
    faces=[f for f in new_lid.Faces() if abs(f.BoundingBox().zmin-86)<1e-5 and abs(f.BoundingBox().zmax-86)<1e-5]
    assert len(faces)==1 and faces[0].geomType()=='PLANE'
    assert len(faces[0].Wires())==91
    identical=[]
    for name in ('inserto_T7','inserto_Shield','provino_sede','provino_chiusura_femmina','provino_chiusura_maschio'):
        path=ROOT/'CAD'/f'{name}_R08.step'
        identical.append(dict(part=name,current_sha256=g.sha(path),
            symmetric_difference_mm3=diff(read(path),read(R06/'CAD'/f'{name}_R06.step'))))
    prior=json.loads((R06/'verifiche/confronto_revisioni.json').read_text())
    assert prior['R05_internal_unchanged']
    p06=json.loads((R06/'sorgenti/parametri.json').read_text())
    for key in ('slot','coperchio','piedini','ventilazione','ssd_nominali'):
        assert g.P[key]==p06[key],key
    p07=json.loads((R07/'sorgenti/parametri.json').read_text())['top_studio']
    for key in ('diametro_fori','passo','colonne','righe','primo_centro'):
        assert g.P['tetto_forato'][key]==p07[key],key
    preserved=[]
    for root in (R06,R07):
        checks=json.loads((root/'verifiche/SHA256.json').read_text())
        assert all(g.sha(root/p)==h for p,h in checks.items())
        preserved.append(dict(folder=root.name,files_checked=len(checks),unchanged=True))
    g.save(ROOT/'verifiche/confronto_revisioni.json',dict(
        revision='R08',monolith_body_unchanged=True,R05_internal_unchanged=True,
        lid_attachment_unchanged=True,roof_is_flat=True,
        body=dict(current_sha256=g.sha(body),symmetric_difference_mm3=body_delta),
        lid=dict(current_sha256=g.sha(lid),attachments_difference_mm3=attachment_delta,
                 planar_top_z_mm=86,top_faces=1,top_wires=91),
        identical_parts=identical,prior_revisions=preserved,
        physical_print=False,thermal_validation=False))
    print('SCOCCA E INTERNI CONSERVATI; TETTO PIATTO CON 90 FORI',flush=True)


if __name__=='__main__':main()
