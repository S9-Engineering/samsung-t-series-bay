"""Slice the actual R28 STL exports with the confirmed ECC2 / PLA BASIC setup.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
import argparse
import json
import math
import plistlib
import re
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw

import generate as g
from native_3mf import export_plate, validate
from slicer_utils import run_cli, parse_gcode, screen_new_wall_islands, estimate_totals
from toolpath_preview import draw_layer

ROOT = g.ROOT


def definitions():
    def stop(xy):
        return dict(part='cartridge-stop-r28', name='R28 wide cartridge stop', xy=xy, support=False)
    def lid(xy):
        return dict(part='lid-plain-r28', name='R28 plain rear lid', xy=xy,
                    support=False, options={'wall_generator': 'arachne'})
    return {'stop': [stop([40, 40])], 'lid': [lid([40, 40])],
            'both': [lid([20, 20]), stop([135, 25])]}


def previews(layers, analysis, qa, name, items):
    bounds = np.array(analysis['extrusion_bounds_xy_mm'])
    frame = [*(bounds[0]-2), *(bounds[1]+2)]
    images = []
    for start in range(0, len(layers), 100):
        subset = layers[start:start+100]
        im = Image.new('RGB', (2000, math.ceil(len(subset)/10)*200+32), 'white')
        d = ImageDraw.Draw(im)
        d.text((10, 8), f'R28 {name} | actual sliced toolpaths | layers {start+1}-{start+len(subset)}', fill='#24323d')
        for k, layer in enumerate(subset):
            draw_layer(d, layer, ((k % 10)*200, 32+(k//10)*200), 200, frame)
        path = qa/f'all-layers-{start+1:03d}-{start+len(subset):03d}.png'
        im.save(path)
        images.append(str(path.relative_to(ROOT)))

    def sheet(label, indexes, fr=frame):
        indexes = sorted(set(max(0, min(i, len(layers)-1)) for i in indexes))
        for start in range(0, len(indexes), 6):
            im = Image.new('RGB', (1800, 1240), 'white')
            d = ImageDraw.Draw(im)
            d.text((10, 8), f'R28 {name} | {label} | actual toolpaths', fill='#24323d')
            for k, i in enumerate(indexes[start:start+6]):
                draw_layer(d, layers[i], ((k % 3)*600, 32+(k//3)*600), 600, fr)
            path = qa/f'{label}-{start//6+1:02d}.png'
            im.save(path)
            images.append(str(path.relative_to(ROOT)))

    n = len(layers)
    sheet('first-middle-last', [0, 1, n//4, n//2, n-2, n-1])
    bridge_indexes = {b['layer']-1+delta for b in analysis['longest_bridge_segments'] for delta in [-1, 0, 1]}
    if bridge_indexes:
        sheet('bridge-details', bridge_indexes)
    true_bridge_indexes = {i+d for i, layer in enumerate(layers)
                           if layer['roles'].get('Bridge') for d in [-1, 0, 1]}
    if true_bridge_indexes:
        sheet('external-bridge-details', true_bridge_indexes)
    roof = next((it for it in items if it['part'].startswith('lid-')), None)
    if roof:
        settings = json.loads((ROOT/'source/profiles/project.json').read_text())
        offset = np.array([float(v) for v in settings['extruder_offset'][0].split('x')])
        rx, ry = np.array(roof['xy'])-offset
        for side, x0, x1 in [('left', 1, 15), ('right', 75, 89)]:
            sheet('guide-and-receiver-'+side, [53, 54, 57, 58, 59, 60],
                  [rx+x0, ry-1, rx+x1, ry+38])
    islands = analysis['new_wall_islands']['new_outer_wall_island_candidates']
    if islands:
        sheet('island-candidate-details', [a['layer']-1+d for a in islands for d in [-1, 0, 1]])
    return images


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', choices=['stop', 'lid', 'both', 'all'], default='all')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'verification/manifest.json').read_text())
    geometry = json.loads((ROOT/'verification/geometry.json').read_text())
    assert geometry['result'] == 'PASS' and geometry['stop_width_after_mm'] == 83.5
    meshes = {}
    for part in manifest['parts']:
        assert g.sha(ROOT/part['stl']) == part['stl_sha256']
        meshes[part['name']] = trimesh.load_mesh(ROOT/part['stl'], process=True)
    exe = Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer')
    help_text = subprocess.run([str(exe), '--help'], capture_output=True, text=True, check=True).stdout
    engine = re.search(r'ElegooSlicer-([0-9.]+)', help_text).group(1)
    app = plistlib.loads((exe.parents[1]/'Info.plist').read_bytes())['CFBundleShortVersionString']
    assert app == '1.5.3.5' and engine == '2.4.2'
    profiles = [ROOT/'source/profiles'/name for name in ['machine.json', 'process.json', 'filament.json']]
    baseline = json.loads((g.PROJECT/'versions/bay-ssd-r27-logo-retro-80-pla/verifiche/provenienza_profili.json').read_text())
    provenance = []
    installed = exe.parents[1]/'Resources/profiles/Elegoo'
    for name, rel in [('machine', 'machine/ECC2/Elegoo Centauri Carbon 2 0.4 nozzle.json'),
                      ('process', 'process/ECC2/0.20mm Standard @Elegoo CC2 0.4 nozzle.json'),
                      ('filament', 'filament/ECC2/Elegoo PLA Basic @ECC2.json')]:
        path = installed/rel
        key = {'machine': 'macchina', 'process': 'processo', 'filament': 'filamento'}[name]
        assert g.sha(path) == baseline['profiles'][key]['sha256'], f'Installed {name} profile changed'
        provenance.append(dict(kind=name, installed_profile=str(path), installed_sha256=g.sha(path)))
    g.save(ROOT/'verification/profile-provenance.json', dict(
        slicer_app=app, slicer_engine=engine, installed_profiles=provenance,
        saved_profiles={p.name: g.sha(p) for p in profiles},
        baseline_evidence='versions/bay-ssd-r27-logo-retro-80-pla/verifiche/provenienza_profili.json',
        configuration='Confirmed ECC2 Combo / 0.4 mm / textured PEI / ELEGOO PLA BASIC; existing R27 reference settings.'))
    for name, items in definitions().items():
        if args.job not in ('all', name):
            continue
        print('SLICING', name, flush=True)
        qa = ROOT/'verification/slicing'/name
        qa.mkdir(parents=True, exist_ok=True)
        source = qa/f'r28-{name}-geometry.3mf'
        export_plate(source, items, meshes)
        source_check = validate(source, items)
        target = ROOT/'print/slicer'/f'r28-{name}-ecc2-pla-basic.3mf'
        gcode = ROOT/'print/gcode'/f'r28-{name}-ecc2-pla-basic.gcode'
        with tempfile.TemporaryDirectory(prefix='s9-r28-') as td:
            td = Path(td)
            out = td/'out'
            out.mkdir()
            cli = run_cli(exe, ['--datadir', str(td/'data'), '--load-settings', str(profiles[0])+';'+str(profiles[1]),
                               '--load-filaments', str(profiles[2]), '--arrange', '0', '--orient', '0',
                               '--slice', '0', '--export-3mf', 'plate.3mf', '--outputdir', str(out), str(source)], qa/'slicer.log')
            gcodes = list(out.glob('*.gcode'))
            assert len(gcodes) == 1
            layers, analysis = parse_gcode(gcodes[0])
            assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header']
            assert not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations']
            analysis['new_wall_islands'] = screen_new_wall_islands(layers)
            native = out/'plate.3mf'
            native_check = validate(native, items)
            with zipfile.ZipFile(native) as z:
                settings = json.loads(z.read('Metadata/project_settings.config'))
                config = ET.fromstring(z.read('Metadata/model_settings.config'))
                expected = dict(printer_model='Elegoo Centauri Carbon 2', nozzle_diameter=['0.4'],
                                curr_bed_type='Textured PEI Plate', filament_type=['PLA'],
                                nozzle_temperature=['220'], textured_plate_temp=['60'],
                                layer_height='0.2', wall_loops='4', sparse_infill_density='20%',
                                sparse_infill_pattern='gyroid', filament_max_volumetric_speed=['5'],
                                enable_support='0', fuzzy_skin='disabled_fuzzy', brim_width='5', bridge_speed='25')
                for k, v in expected.items():
                    assert settings[k] == v, (k, settings[k], v)
                object_config = {}
                for obj in config.findall('object'):
                    cfg = {e.get('key'): e.get('value') for e in obj.findall('metadata')}
                    item = next(it for it in items if it['name'] == cfg['name'])
                    assert cfg['enable_support'] == '0'
                    for k, v in item.get('options', {}).items():
                        assert cfg[k] == v
                    object_config[cfg['name']] = cfg
                warnings = [dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')]
                assert all(w['msg'] == 'bed_temperature_too_high_than_filament' for w in warnings), warnings
                member = next(n for n in z.namelist() if n.endswith('.gcode'))
                assert __import__('hashlib').sha256(z.read(member)).hexdigest() == g.sha(gcodes[0])
            assert not any('support' in role.lower() for layer in layers for *_, role in layer['segments'])
            shutil.copy2(native, target)
            shutil.copy2(gcodes[0], gcode)
            g.save(qa/'analysis.json', analysis)
        images = previews(layers, analysis, qa, name, items)
        job = dict(name=name, revision='R28', items=items, project=str(target.relative_to(ROOT)),
                   project_sha256=g.sha(target), gcode=str(gcode.relative_to(ROOT)), gcode_sha256=g.sha(gcode),
                   manifest_sha256=g.sha(ROOT/'verification/manifest.json'),
                   geometry_report_sha256=g.sha(ROOT/'verification/geometry.json'),
                   source_check=source_check, native_check=native_check, object_config=object_config,
                   slicer_app=app, slicer_engine=engine, layers=len(layers),
                   slicer_estimates=analysis['slicer_estimates'], totals=estimate_totals([analysis]),
                   warnings=warnings, cli=cli, images=images,
                   visual_review_complete=False, sent_to_printer=False)
        g.save(qa/'job.json', job)
        print(json.dumps(dict(name=name, layers=len(layers), estimates=job['totals'],
                              island_candidates=analysis['new_wall_islands']['candidate_count'])), flush=True)


if __name__ == '__main__':
    main()
