"""Technical previews from the exported meshes, with no generated geometry.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
import importlib.util
import json
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
spec = importlib.util.spec_from_file_location('s9_renderer', PROJECT/'source/render_release.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
r.ROOT = ROOT
r.CACHE = ROOT/'.cache/render'
r.CACHE.mkdir(parents=True, exist_ok=True)
r.records = []


def load(name):
    return trimesh.load_mesh(ROOT/'verification/meshes'/f'{name}.ply', process=True)


def main():
    stop = load('cartridge-stop-r28')
    lid = load('lid-plain-r28')
    p = r.render('01-wide-stop', [(stop, r.BLUE)], (190, -245, 165), (45, 8, 40),
                 size=(1200, 1000), spp=96, floor=False)
    r.caption(p, 'R28 / 83.5 mm wide cartridge stop',
              '0.25 mm nominal side clearance; original three blocking noses and lifting handle.')
    p = r.render('02-plain-rear-lid', [(lid, r.CHARCOAL)], (190, 315, 195), (45, 56, 70),
                 size=(1200, 1000), spp=96, floor=False)
    r.caption(p, 'R28 / Plain rear tail',
              'Rear lettering removed. Roof slots, sliding guides and both pin receivers retained.')

    baseline = PROJECT/'versions/bay-ssd-r27-logo-retro-80-pla/verifiche/mesh_assieme'
    shell = trimesh.load_mesh(baseline/'SCOCCA_R27_DOPPIO_PERNO.ply', process=True)
    shell = shell.slice_plane([0, 0, 28], [0, 0, -1])
    parts = [(shell, r.CHARCOAL), (stop, r.BLUE)]
    for i, model in enumerate(['T7', 'T7_Shield', 'T9']):
        m = trimesh.load_mesh(baseline/f'CARTUCCIA_{model}_R27.ply', process=True)
        m.apply_translation((24*i, 0, 0))
        m = m.slice_plane([0, 0, 28], [0, 0, -1])
        parts.append((m, r.GOLD))
    p = r.render('03-stop-seating-cutaway', parts, (195, 245, 240), (45, 45, 30),
                 size=(1400, 1100), spp=96, floor=False)
    r.caption(p, 'R28 / Stop seated in the existing R27 shell',
              'Illustrative cutaway at Z28 mm. Blue: stop; gold: cartridge feet. No printed colour changes.')

    parts = []
    for name, xy in [('lid-plain-r28', (20, 20)), ('cartridge-stop-r28', (135, 25))]:
        m = trimesh.load_mesh(ROOT/'print/stl'/f'{name}.stl', process=True)
        m.apply_translation((*xy, 0))
        parts.append((m, r.BLUE if name.startswith('cartridge') else r.CHARCOAL))
    p = r.render('04-print-orientation', parts, (280, -245, 390), (115, 75, 5),
                 size=(1400, 1000), spp=96, floor=False)
    r.caption(p, 'R28 / Two replacement parts, one plate',
              'Stop front face down; three blocks up. Lid exterior face down. Brim shown in toolpath sheets.')
    (ROOT/'verification/render.json').write_text(json.dumps(dict(
        renderer='Mitsuba / llvm_ad_rgb', actual_exported_meshes=True,
        physical_photographs=False, outputs=r.records,
        note='Technical views with illustrative colours and smooth shading. Cutaway is presentation only.'), indent=2)+'\n')


if __name__ == '__main__':
    main()
