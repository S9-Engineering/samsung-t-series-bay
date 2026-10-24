"""Esporta e mostra il monolite R06; non prepara una nuova stampa."""
from pathlib import Path
import json
import cadquery as cq
import trimesh
import numpy as np
from PIL import Image, ImageDraw
import genera as g
from render_base import render, font, BG, INK, MUTED

ROOT = g.ROOT
REFERENCE = ROOT.parent / 'bay-ssd-universale-r05-incastri'
PALETTE = dict(scocca=g.P['colori']['scocca'], tetto=g.P['colori']['coperchio'])


def check_shape(name, shape):
    path = ROOT / 'CAD_studio' / (name + '.step')
    cq.exporters.export(shape, str(path))
    reopened = cq.importers.importStep(str(path)).val()
    assert reopened.isValid() and len(reopened.Solids()) == 1, name
    # Leggere il BRep prima della tessellazione: la triangolazione memorizzata
    # amplia la bounding box conservativa di OpenCascade della sua deflessione.
    bounds = g.bounds(reopened)
    assert np.allclose(bounds, g.bounds(shape), atol=1e-5), name
    mesh = g.mesh_of(reopened)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0, name
    assert len(mesh.split(only_watertight=False)) == 1, name
    assert np.isfinite(mesh.vertices).all() and mesh.area_faces.min() > 1e-12, name
    assert np.allclose(mesh.bounds, bounds, atol=.05), name
    mesh.export(ROOT / 'verifiche' / (name + '.ply'))
    return reopened, mesh, dict(
        step=str(path.relative_to(ROOT)), sha256=g.sha(path), valid=True, solids=1,
        bounds_mm=bounds, volume_mm3=reopened.Volume(),
        mesh_closed=True, mesh_winding_consistent=True, mesh_components=1,
        degenerate_faces=0,
    )


def same_solid(a, b, tolerance=1e-5):
    delta = a.cut(b).Volume() + b.cut(a).Volume()
    assert delta < tolerance, delta
    return delta


def picture(rows, view, filename):
    path = ROOT / 'anteprime' / filename
    return render(rows, PALETTE, view, path)


def main():
    shape_body, mesh_body, body_report = check_shape('scocca_R06_STUDIO', g.shell())
    print('Scocca esportata e riaperta', flush=True)
    shape_lid, mesh_lid, lid_report = check_shape('coperchio_R06_STUDIO', g.lid())
    print('Coperchio esportato e riaperto', flush=True)
    # Le differenze devono rimanere sul contorno esterno. Il volume che contiene
    # sedi, fermi, guide, agganci e feritoie rimane quello della R05.
    roi = g.box(3, 3, 0, 84, 95, 86)
    old_body = cq.importers.importStep(str(REFERENCE / 'CAD/scocca_R05.step')).val()
    old_lid = cq.importers.importStep(str(REFERENCE / 'CAD/coperchio_R05.step')).val()
    internal_body_delta = same_solid(shape_body.intersect(roi), old_body.intersect(roi))
    internal_lid_delta = same_solid(shape_lid.intersect(roi), old_lid.intersect(roi))
    overlap = shape_body.intersect(shape_lid).Volume()
    assert overlap < 1e-5, overlap
    old_parameters = json.loads((REFERENCE / 'sorgenti/parametri.json').read_text())
    for field in ('slot', 'coperchio', 'piedini', 'ventilazione', 'ssd_nominali'):
        assert g.P[field] == old_parameters[field], field
    rows = [
        (dict(name='Scocca', kind='struttura'), mesh_body),
        (dict(name='Tetto', kind='coperchio'), mesh_lid),
    ]
    assembly = cq.Assembly(name='R06_STUDIO_MONOLITE')
    assembly.add(shape_body, name='Scocca', color=cq.Color(PALETTE['scocca']))
    assembly.add(shape_lid, name='Tetto', color=cq.Color(PALETTE['tetto']))
    # SSD volutamente schematizzati, presenti nelle viste attraverso le aperture.
    for slot, model in enumerate(('T7', 'T7_Shield', 'T9')):
        drive = g.drive(model, slot)
        rows.append((dict(name=model, kind='gabarit_ssd', color=g.P['colori'][model]), g.mesh_of(drive)))
        assembly.add(drive, name=model, color=cq.Color(g.P['colori'][model]))
        if model != 'T9':
            for number, y in enumerate(g.S['centri_y'], 1):
                insert = g.adapter(model, y, slot)
                rows.append((dict(name=f'{model}_{number}', kind='inserto'), g.mesh_of(insert)))
                assembly.add(insert, name=f'Inserto_{model}_{number}', color=cq.Color(PALETTE['scocca']))
    assembly_path = ROOT / 'CAD_studio/R06_STUDIO_ASSIEME.step'
    assembly.save(str(assembly_path))
    reopened_assembly = cq.importers.importStep(str(assembly_path)).val()
    assert reopened_assembly.isValid() and len(reopened_assembly.Solids()) == 9
    front = picture(rows, dict(camera=(45, -300, 43), target=(45, 50.5, 43), scale=66), '02_R06_FRONTE.png')
    quarter = picture(rows, dict(camera=(-190, -230, 190), target=(45, 50.5, 43), scale=84), '03_R06_TRE_QUARTI.png')
    top = picture(rows, dict(camera=(45, 50.5, 350), target=(45, 50.5, 43), up=(0, 1, 0), scale=66), '04_R06_ALTO.png')
    board = Image.new('RGB', (2280, 1180), BG)
    d = ImageDraw.Draw(board)
    d.text((60, 35), 'R06 / MONOLITE', font=font(48, True), fill=INK)
    d.text((62, 107), 'Grafite uniforme · fronte pieno · raccordi contenuti', font=font(26), fill=MUTED)
    for x, label, im in ((30, 'DAVANTI', front), (1170, 'TRE QUARTI', quarter)):
        d.text((x+30, 191), label, font=font(25, True), fill=INK)
        board.paste(im, (x, 230))
    d.text((60, 1120), 'Studio esterno dal CAD · interno R05 conservato · colore indicativo', font=font(25), fill=MUTED)
    board.save(ROOT / 'anteprime/01_R06_MONOLITE.png')
    audit = json.loads((REFERENCE / 'verifiche/SHA256.json').read_text())
    failures = [name for name, sha in audit.items() if g.sha(REFERENCE / name) != sha]
    assert not failures, failures
    report = dict(
        revision='R06_STUDIO_ESTERNO', state='STUDIO_ESTETICO_NON_PREPARATO_PER_LA_STAMPA',
        source_revision='R05', source_revision_unchanged=True,
        source_revision_hashed_files_checked=len(audit),
        unit='mm', bare_case_dimensions=[90, 101, 86],
        changes=dict(external_corner_radius_mm=3, body_edge_radius_mm=.4,
                     lid_upper_edge_radius_mm=.4, lid_lower_edge_radius_mm=.2,
                     body_color=PALETTE['scocca'], lid_color=PALETTE['tetto']),
        internal_body_difference_mm3=internal_body_delta,
        internal_lid_difference_mm3=internal_lid_delta,
        body_lid_overlap_mm3=overlap, solids_assembly=9,
        parts=[body_report, lid_report], sliced=False, physical_print=False,
        thermal_test=False, self_intersections_screened=False,
        notes='Controlli limitati allo studio. Nessun nuovo file di stampa. Render dai STEP riaperti; nessuna prova fisica o termica.',
    )
    g.save(ROOT / 'verifiche/studio.json', report)
    paths = [p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name != 'SHA256.json']
    g.save(ROOT / 'verifiche/SHA256.json', {str(p.relative_to(ROOT)): g.sha(p) for p in sorted(paths)})
    print('R06 STUDIO MONOLITE COMPLETATO', flush=True)


if __name__ == '__main__':
    main()
