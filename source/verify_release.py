"""Read-only reopening of the retained R27 delivery; writes only root verification.

Run with the CAD dependencies declared in the retained revision. This does not
regenerate CAD, reslice a plate, or operate a printer.
"""
from pathlib import Path
import hashlib
import json
import sys
import zipfile
import importlib.metadata

import cadquery as cq
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT/'versions/bay-ssd-r27-logo-retro-80-pla'
sys.path.insert(0, str(REV/'sorgenti'))
import native_3mf
from slicer_utils import parse_gcode


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((REV/'verifiche/manifest.json').read_text())
    original = json.loads((REV/'verifiche/SHA256.json').read_text())
    mismatches = [p for p, value in original.items() if not (REV/p).is_file() or sha(REV/p) != value]
    assert not mismatches, mismatches
    print(f'Original delivery: {len(original)} hashes match', flush=True)
    geometry = json.loads((REV/'verifiche/geometria.json').read_text())
    assert geometry['manifest_sha256'] == sha(REV/'verifiche/manifest.json')
    results = []
    for part in manifest['parts']:
        for fmt in ['stl', 'step', 'print_step']:
            assert sha(REV/part[fmt]) == part[fmt+'_sha256']
        for fmt in ['step', 'print_step']:
            s = cq.importers.importStep(str(REV/part[fmt])).val()
            assert s.isValid() and len(s.Solids()) == 1 and s.Volume() > 0
        m = trimesh.load_mesh(REV/part['stl'], process=True)
        assert m.is_watertight and m.is_winding_consistent and m.volume > 0 and len(m.split()) == 1
        assert np.max(np.abs(m.bounds - np.array(part['print_bounds_mm']))) < 0.06
        assert np.all(m.nondegenerate_faces()) and np.all(m.unique_faces())
        old = next(x for x in geometry['parts'] if x['name'] == part['name'])
        assert old['stl_sha256'] == sha(REV/part['stl'])
        assert old['self_intersections']['intersection_pairs'] == 0
        results.append({'name': part['name'], 'step_reopened_single_valid_solid': True,
            'stl_reopened_closed_positive_single_component': True,
            'normals_consistent': True, 'duplicate_and_degenerate_faces': 0,
            'dimensions_match_manifest': True, 'self_intersection_screen': 'Inherited, identical STL SHA-256',
            'self_intersection_screen_limit': 'Pairs sharing a vertex excluded by the historical algorithm.',
            'stl_sha256': sha(REV/part['stl'])})
        print('Geometry reopened:', part['name'], flush=True)
    assy = cq.importers.importStep(str(REV/'CAD/ASSIEME_R27_NON_STAMPARE.step')).val()
    assert assy.isValid() and len(assy.Solids()) == 11
    jobs = []
    slicing = json.loads((REV/'verifiche/slicing/riepilogo.json').read_text())
    for j in slicing['jobs']:
        assert sha(REV/j['project']) == j['project_sha256']
        assert sha(REV/j['gcode']) == j['gcode_sha256']
        native = native_3mf.validate(REV/j['project'], j['items'])
        assert native['printable_count'] == (4 if j['mode'] == 'PROVINO' else 8)
        with zipfile.ZipFile(REV/j['project']) as z:
            assert z.testzip() is None
            embedded = [p for p in z.namelist() if p.endswith('.gcode')]
            assert len(embedded) == 1
            assert hashlib.sha256(z.read(embedded[0])).hexdigest() == j['gcode_sha256']
            settings = json.loads(z.read('Metadata/project_settings.config'))
            profile = {k: settings.get(k) for k in ['printer_model', 'printer_settings_id', 'nozzle_diameter',
                'filament_type', 'filament_settings_id', 'layer_height', 'wall_loops', 'sparse_infill_density',
                'enable_support', 'brim_width', 'nozzle_temperature', 'textured_plate_temp']}
            assert float(settings['layer_height']) == 0.2
            assert float(settings['brim_width']) == 5
        layers, parsed = parse_gcode(REV/j['gcode'])
        assert parsed['all_layers_nonempty'] and parsed['layer_count_matches_header']
        assert not parsed['out_of_bed_layers'] and not parsed['profile_exclusion_zone_violations']
        assert parsed['parsed_layer_count'] == (145 if j['mode'] == 'PROVINO' else 415)
        del layers
        assert j['visual_review_complete'] is True and j['sent_to_printer'] is False
        jobs.append({'mode': j['mode'], 'native_3mf_reopened': native,
            'gcode_reparsed': {k: v for k, v in parsed.items() if k != 'layers'},
            'embedded_gcode_matches_export': True, 'profile_readback': profile,
            'project_sha256': j['project_sha256'], 'gcode_sha256': j['gcode_sha256'],
            'slicer_version': j['slicer_app'], 'engine_version': j['slicer_engine'],
            'slicer_estimates': j['totals'], 'warnings': j['warnings'],
            'slicing': 'Retained verified R27 slicing, not rerun for publication.'})
        print('Native project and G-code reopened:', j['mode'], flush=True)
    result = {
        'result': 'PASS', 'release': 'v1.0.0', 'project_revision': 'R27',
        'status': 'Ready for printing (digital checks only)', 'unit': 'millimeter',
        'original_delivery_hashes_checked': len(original), 'original_delivery_unchanged': True,
        'packages': {p: importlib.metadata.version(p) for p in ['cadquery', 'trimesh', 'numpy']},
        'parts': results, 'reference_assembly_solids': 11, 'reference_assembly_not_printable': True,
        'jobs': jobs, 'geometry_changed_for_release': False, 'sent_to_printer': False,
        'inherited_kinematics': 'R26/R27 reports, unchanged hashes. Collision sweeps not rerun.',
        'visual_review': 'Original all-layer sheets and critical bridge/logo/pin details reviewed for publication; see visual-review-v1.0.0.md.',
        'physical_evidence': 'User accepted the earlier internal-seat coupon; a previous lid sample entered. No full R27 or double-pin retention/durability/thermal validation.',
        'compatibility': {'included': ['Samsung T7', 'Samsung T7 Shield', 'Samsung T9'],
                          'T5': 'Not supported in v1.0.0: dedicated cartridge absent.'},
        'limits': ['No new force, fatigue, creep or material-temperature measurement.',
                  'Actual USB plug clearance and commercial rubber feet remain to be checked.',
                  'PLA chamber warning retained: use with front door open as documented.'],
    }
    output = ROOT/'verification/release-v1.0.0.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS:', output, flush=True)


if __name__ == '__main__':
    main()
