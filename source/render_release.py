"""Render the unmodified R27 exported meshes with Mitsuba (millimetres).

All exploded translations and illustrative colours are presentation only.
Run: .venv/bin/python source/render_release.py [--smoke]
"""
from pathlib import Path
import argparse
import hashlib
import json
import time

import mitsuba as mi
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / 'versions/bay-ssd-r27-logo-retro-80-pla'
CACHE = ROOT / '.cache/render'
CACHE.mkdir(parents=True, exist_ok=True)
mi.set_variant('llvm_ad_rgb')
T = mi.ScalarTransform4f
CHARCOAL = (0.065, 0.075, 0.085)
BLUE = (0.11, 0.34, 0.52)
GOLD = (0.62, 0.29, 0.075)
DRIVE = (0.25, 0.31, 0.36)
records = []


def load(name, shift=(0, 0, 0)):
    m = trimesh.load_mesh(REV / 'verifiche/mesh_assieme' / (name + '.ply'))
    m.apply_translation(shift)
    return m


def pin_pair(locked=True):
    m = load('PERNO_R27_NASCOSTO')
    if locked:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1], [8.2, 96, 0]))
        m.apply_translation((0, 0, -1.1))
    n = m.copy()
    reflection = np.eye(4)
    reflection[0, 0] = -1
    reflection[0, 3] = 90
    n.apply_transform(reflection)
    return [m, n]


def assembly(roof=True, drives=False):
    parts = [(load('SCOCCA_R27_DOPPIO_PERNO'), CHARCOAL),
             (load('FERMO_CARTUCCE_R27'), CHARCOAL)]
    for i, name in enumerate(['T7', 'T7_Shield', 'T9']):
        parts.append((load('CARTUCCIA_' + name + '_R27', (24*i, 0, 0)), CHARCOAL))
        if drives:
            parts.append((drive(name, i), DRIVE))
    if roof:
        parts.append((load('TETTO_R27_DOPPIO_PERNO'), CHARCOAL))
        parts.extend((m, CHARCOAL) for m in pin_pair())
    return parts


def drive(name, i=0):
    dims = {'T7': (8, 85, 57), 'T7_Shield': (13, 88, 59), 'T9': (14, 88, 60)}[name]
    m = trimesh.creation.box(extents=dims)
    m.apply_translation((21 + 24*i, 16 + dims[1]/2, 13 + dims[2]/2))
    return m


def render(name, parts, eye, target, fov=30, size=(1440, 1120), spp=256, floor=True, up=(0, 0, 1)):
    start = time.monotonic()
    if not floor:
        # Frame every exploded component; the normal product shots use fixed cameras.
        bounds = np.array([m.bounds for m, _ in parts])
        centre = (bounds[:, 0].min(0) + bounds[:, 1].max(0))/2
        radius = max(np.linalg.norm(m.vertices-centre, axis=1).max() for m, _ in parts)
        angle = np.arctan(np.tan(np.radians(fov/2))/max(1, size[0]/size[1]))
        direction = np.array(eye, dtype=float)-np.array(target)
        direction /= np.linalg.norm(direction)
        eye = centre + direction*radius/np.sin(angle)*1.08
        target = centre
    scene = {
        'type': 'scene',
        'integrator': {'type': 'path', 'max_depth': 8, 'hide_emitters': True},
        'sensor': {
            'type': 'perspective', 'fov': fov,
            'to_world': T.look_at(origin=np.array(eye)*0.01, target=np.array(target)*0.01, up=up),
            'sampler': {'type': 'independent', 'sample_count': spp},
            'film': {'type': 'hdrfilm', 'width': size[0], 'height': size[1],
                     'rfilter': {'type': 'tent'}, 'pixel_format': 'rgb'},
        },
        'environment': {'type': 'constant', 'radiance': {'type': 'rgb', 'value': [0.55, 0.55, 0.55]}},
    }
    for i, (mesh, col) in enumerate(parts):
        path = CACHE / (name + f'-{i}.ply')
        mesh.export(path)
        scene[f'part_{i}'] = {
            'type': 'ply', 'filename': str(path), 'to_world': T.scale(0.01),
            'face_normals': True,
            'bsdf': {'type': 'roughplastic', 'distribution': 'ggx', 'alpha': 0.24,
                     'diffuse_reflectance': {'type': 'rgb', 'value': col}},
        }
    if floor:
        scene['floor'] = {'type': 'rectangle', 'to_world': T.translate([0, 0, -0.012]) @ T.scale(200),
                          'bsdf': {'type': 'diffuse', 'reflectance': {'type': 'rgb', 'value': [0.62, 0.64, 0.67]}}}
    for i, (pos, power, scale) in enumerate([((-2, -3, 5), 9, 2.0), ((3, 1, 4), 7, 1.5), ((-1, 4, 3), 5, 1.5)]):
        scene[f'light_{i}'] = {'type': 'rectangle',
            'to_world': T.look_at(origin=pos, target=[0.45, 0.5, 0.4], up=[0, 0, 1]) @ T.scale(scale),
            'emitter': {'type': 'area', 'radiance': {'type': 'rgb', 'value': [power]*3}}}
    out = mi.render(mi.load_dict(scene), seed=17)
    path = ROOT / ('previews/renders' if name.startswith('product') or name == 'hero' else 'previews/assembly') / (name + '.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    mi.util.write_bitmap(str(path), out, write_async=False)
    records.append({'file': str(path.relative_to(ROOT)), 'seconds': round(time.monotonic()-start, 2),
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'samples_per_pixel': spp})
    print('Rendered', path.name, records[-1]['seconds'], flush=True)
    return path


def caption(path, title, subtitle):
    old = Image.open(path).convert('RGB')
    im = Image.new('RGB', (old.width, old.height + 110), '#f3f4f5')
    im.paste(old, (0, 110))
    d = ImageDraw.Draw(im)
    font = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
    def face(size):
        return ImageFont.truetype(str(font), size) if font.exists() else ImageFont.load_default(size=size)
    d.text((30, 19), title, font=face(28), fill='#202c36')
    d.text((30, 61), subtitle, font=face(20), fill='#465565')
    im.save(path)
    records[-1]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--assembly-only', action='store_true')
    a = parser.parse_args()
    if a.smoke:
        render('hero', assembly(), (240, -265, 200), (45, 52, 41), size=(800, 650), spp=16)
        return
    if not a.assembly_only:
        render('hero', assembly(), (240, -265, 200), (45, 52, 41))
        render('product-front', assembly(), (45, -315, 112), (45, 47, 42), size=(1200, 1000))
        render('product-side', assembly(), (360, 52, 120), (45, 52, 42), size=(1200, 1000))
        render('product-rear', assembly(), (215, 315, 170), (45, 57, 43), size=(1200, 1000))
    else:
        previous = json.loads((ROOT/'verification/render-v1.0.0.json').read_text())
        records.extend(r for r in previous['outputs'] if r['file'].startswith('previews/renders/'))

    coupon = [(load('PROVINO_GUIDE_SCOCCA_R27'), CHARCOAL),
              (load('PROVINO_GUIDE_TETTO_R27', (0, 0, 25)), GOLD)]
    for m in pin_pair(locked=False):
        m.apply_translation((0, 0, -20))
        coupon.append((m, BLUE))
    p = render('01-fit-coupon', coupon, (155, 225, 135), (45, 88, 70), fov=29, size=(1200, 900), floor=False)
    caption(p, '01 / Sliding-lid fit coupon', 'Gold: lid sample, lifted 25 mm. Blue: two identical pins, shown below their receivers.')

    parts = [(load('CARTUCCIA_T7_R27'), GOLD), (drive('T7'), DRIVE)]
    # Shift the schematic drive backwards to reveal the insertion direction and both frames.
    parts[1][0].apply_translation((0, 55, 0))
    p = render('02-drive-cartridge', parts, (170, 240, 155), (21, 85, 43), fov=29, size=(1200, 900), floor=False)
    caption(p, '02 / Model-specific cartridge', 'Insert the unplugged SSD from the rear through both frames. Drive envelope is schematic.')

    parts = [(load('SCOCCA_R27_DOPPIO_PERNO'), CHARCOAL)]
    for i, model in enumerate(['T7', 'T7_Shield', 'T9']):
        parts.append((load('CARTUCCIA_' + model + '_R27', (24*i, -6, 22)), GOLD))
    parts.append((load('FERMO_CARTUCCE_R27', (0, -18, 0)), BLUE))
    p = render('03-cartridge-seating', parts, (220, -240, 220), (45, 48, 47), size=(1200, 1000), floor=False)
    caption(p, '03 / Seat the three cartridges', 'Lower 6 mm forward of the final seat; slide back 6 mm. Lower the blue front stop last.')

    parts = assembly(roof=False, drives=True)
    parts.append((load('TETTO_R27_DOPPIO_PERNO', (0, 68, 0)), GOLD))
    p = render('04-slide-lid', parts, (225, 300, 220), (45, 75, 47), size=(1200, 1000), floor=False)
    caption(p, '04 / Sliding lid and rear cable access', 'Slide the lid forward from the rear. USB plugs and cable bends remain outside the enclosure.')

    parts = [(load('TETTO_R27_DOPPIO_PERNO'), CHARCOAL)]
    parts.extend((m, BLUE) for m in pin_pair())
    p = render('05-locking-pins', parts, (160, 240, -60), (45, 65, 75), fov=28, size=(1200, 900), floor=False, up=(0, 0, 1))
    caption(p, '05 / Two hidden quarter-turn pins', 'Underside view, shell hidden. Insert upwards, turn 90 degrees, lower 1.1 mm into the seat.')

    inputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((REV/'verifiche/mesh_assieme').glob('*.ply'))}
    (ROOT/'verification/render-v1.0.0.json').write_text(json.dumps({
        'renderer': 'Mitsuba 3.9.1 / llvm_ad_rgb', 'revision': 'R27',
        'actual_exported_meshes': True, 'physical_photographs': False,
        'notes': 'Illustrative smooth charcoal PLA shading, not a measured print finish. No simulated layer texture, feet or cables. Assembly colours/exploded offsets are illustrative; drive envelopes are nominal.',
        'inputs_sha256': inputs, 'outputs': records}, indent=2)+'\n')


if __name__ == '__main__':
    main()
