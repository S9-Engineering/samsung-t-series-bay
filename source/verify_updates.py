"""Reopen R28 exports and check the two changes against R27.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
import itertools
import json

import cadquery as cq
import numpy as np
import trimesh

import update_geometry as g
from mesh_intersections import self_intersections_fast


def volume(shape):
    return sum(s.Volume() for s in shape.Solids())


def difference(a, b):
    return volume(a.cut(b)) + volume(b.cut(a))


def main():
    manifest = json.loads((g.ROOT / 'verification/update-manifest.json').read_text())
    assert manifest['source_sha256'] == g.sha(g.ROOT / 'source/update_geometry.py')
    assert manifest['parameters_sha256'] == g.sha(g.ROOT / 'source/update-parameters.json')
    assert all(g.sha(g.PROJECT / p) == h for p, h in manifest['baseline_sha256'].items())
    rows, shapes = [], {}
    for part in manifest['parts']:
        shape = cq.importers.importStep(str(g.ROOT / part['assembled_step'])).val()
        printing = cq.importers.importStep(str(g.ROOT / part['print_step'])).val()
        mesh = trimesh.load_mesh(g.ROOT / part['stl'], process=True)
        assert g.sha(g.ROOT / part['stl']) == part['stl_sha256']
        assert shape.isValid() and printing.isValid()
        assert len(shape.Solids()) == len(printing.Solids()) == len(mesh.split(only_watertight=False)) == 1
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
        assert np.all(mesh.area_faces > 1e-10)
        assert len(np.unique(np.sort(mesh.faces, axis=1), axis=0)) == len(mesh.faces)
        assert np.allclose(mesh.bounds, g.bounds(printing), atol=.035)
        assert np.allclose(mesh.bounds[0], 0, atol=1e-4)
        assert abs(mesh.volume / shape.Volume() - 1) < .005
        for key in ['assembled_step', 'print_step']:
            assert '.MILLI.,.METRE.' in (g.ROOT / part[key]).read_text()
        screen = self_intersections_fast(mesh)
        assert screen['intersection_pairs'] == 0, screen
        angle = 90 if part['name'].startswith('cartridge') else 180
        expected_printing = g.normalize(shape.rotate((0, 0, 0), (1, 0, 0), angle))
        assert difference(expected_printing, printing) < 1e-5
        shapes[part['name']] = shape
        rows.append({'name': part['name'], 'valid_single_solid': True,
                     'watertight': True, 'consistent_winding': True,
                     'positive_volume': True, 'degenerate_faces': 0,
                     'duplicate_faces': 0, 'self_intersection_screen': screen,
                     'bounds_mm': mesh.bounds.tolist(), 'volume_mm3': float(mesh.volume)})
        print('Verified exports:', part['name'], flush=True)
    stop, lid = shapes['cartridge-stop'], shapes['lid']
    old_stop = g.reference(g.P['baseline']['stop'])
    old_lid = g.reference(g.P['baseline']['lid'])
    assert np.isclose(g.bounds(old_stop)[1, 0] - g.bounds(old_stop)[0, 0], 57)
    assert np.isclose(g.bounds(stop)[1, 0] - g.bounds(stop)[0, 0], 83.5)
    assert volume(old_stop.cut(stop)) < 1e-6
    assert np.isclose(volume(stop.cut(old_stop)), 1056.72, atol=1e-5)
    # The three noses, their spacing and the handle remain exactly unchanged.
    nose_region = g.box(-1, 6.20001, -1, 92, 110, 90)
    assert difference(stop.intersect(nose_region), old_stop.intersect(nose_region)) < 1e-6
    front = g.box(-1, -1, -1, 92, 110, 90)
    assert difference(lid, old_lid.intersect(front)) < 1e-5
    removed = old_lid.cut(lid)
    assert len(removed.Solids()) == 13
    assert g.bounds(removed)[0, 1] >= 109 - 1e-5
    assert np.isclose(g.bounds(lid)[1, 1], 109, atol=1e-6)
    shell = g.reference(g.P['baseline']['shell'])
    assert volume(shell.intersect(stop)) < 1e-6
    assert volume(shell.intersect(lid)) < 1e-6
    assert volume(stop.intersect(lid)) < 1e-6
    for z in np.linspace(0, 80, 17):
        assert volume(shell.intersect(stop.translate((0, 0, float(z))))) < 1e-6
    fits = []
    for model, slot in itertools.product(g.P['baseline']['cartridges'], range(3)):
        carrier = g.reference(g.P['baseline']['cartridges'][model]).translate((24 * slot, 0, 0))
        assert volume(stop.intersect(carrier)) < 1e-6
        assert volume(lid.intersect(carrier)) < 1e-6
        # Small forward motion must hit the corresponding nose even at
        # the conservative maximum case-side shift and cartridge x play.
        overlaps = []
        for dx, foot_dx in itertools.product([-.25, 0, .25], [-.2, .2]):
            overlap = volume(stop.translate((dx, 0, 0)).intersect(carrier.translate((foot_dx, -.5, 0))))
            assert overlap > 0, (model, slot, dx, foot_dx)
            overlaps.append(overlap)
        fits.append({'model': model, 'slot': slot + 1, 'nominal_interference_mm3': 0,
                     'minimum_blocking_overlap_volume_mm3': min(overlaps)})
    g.save(g.ROOT / 'verification/update-geometry.json', {
        'result': 'PASS', 'revision': 'R28', 'parts': rows,
        'stop_width_before_mm': 57, 'stop_width_after_mm': 83.5,
        'extension_per_side_mm': 13.25, 'added_stop_volume_mm3': 1056.72,
        'wing_depth_mm': 2.4, 'nominal_wing_to_roof_rail_clearance_y_mm': .4,
        'front_corner_chamfer_mm': 1.2,
        'noses_and_handle_unchanged': True, 'rear_logo_removed_glyphs': 13,
        'lid_changes_only_beyond_rear_plane_y_mm': 109,
        'case_lid_and_stop_interference_mm3': 0,
        'stop_vertical_removal_poses_checked': 17, 'cartridge_checks': fits,
        'residual_clearance': {'case_internal_width_mm': 84, 'stop_width_mm': 83.5,
                               'nominal_side_gap_mm': .25, 'maximum_nominal_lateral_travel_mm': .5,
                               'minimum_tab_overlap_width_with_foot_play_mm': 9.0},
        'limitations': ['Clearances are nominal; actual PLA fit remains to be checked on the printed R27 shell.',
                       'Self-intersection screening excludes pairs sharing a vertex.',
                       'Nominal CAD overlap does not prove printed fit, holding force or thermal performance.'],
        'physical_fit_verified': False, 'sent_to_printer': False,
    })
    print('R28 geometry and nominal R27 compatibility checks passed.', flush=True)


if __name__ == '__main__':
    main()
