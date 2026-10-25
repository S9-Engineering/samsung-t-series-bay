"""R28 replacement stop (83.5 mm wide) and plain-rear lid, in millimetres.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)

Run from a clone of samsung-t-series-bay; reference exports stay inside it.
The R27 sources, parts, release archives and public tags are never overwritten.
"""
from pathlib import Path
import hashlib
import json

import cadquery as cq
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
P = json.loads((ROOT / 'source/parameters.json').read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def box(x, y, z, dx, dy, dz):
    return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x, y, z))


def bounds(shape):
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    b = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape.wrapped, b, False, False)
    v = b.Get()
    return np.array([v[:3], v[3:]], dtype=float)


def reference(relative):
    path = (PROJECT / relative).resolve()
    if not path.is_relative_to(PROJECT) or not path.is_file():
        raise ValueError(f'Missing project-contained reference: {relative}')
    return cq.importers.importStep(str(path)).val()


def mesh_of(shape):
    vertices, faces = shape.tessellate(.025, .08)
    return trimesh.Trimesh([v.toTuple() for v in vertices], faces, process=True)


def normalize(shape):
    return shape.translate(tuple(-bounds(shape)[0]))


def models():
    old_stop = reference(P['baseline']['stop'])
    b = bounds(old_stop)
    extension = P['stop']['extension_per_side_mm']
    z = b[0, 2]
    height = P['stop']['crossbar_top_z_mm'] - z
    # Only the added side wings stop at Y5.6: the shell roof rails start at
    # Y6.0, so the wider stop can still be lifted out vertically.
    depth = P['stop']['wing_depth_mm']
    left = box(b[0, 0] - extension, b[0, 1], z, extension, depth, height)
    right = box(b[1, 0], b[0, 1], z, extension, depth, height)
    stop = old_stop.fuse(left, right).clean()
    # Relieve the two front corners to clear the R27 cavity's R1.2 corners.
    # Side guides remain full width behind the short lead-in chamfers.
    sb = bounds(stop)
    chamfer = P['stop']['front_corner_chamfer_mm']
    for x, direction in [(sb[0, 0], 1), (sb[1, 0], -1)]:
        y = sb[0, 1]
        wire = cq.Wire.makePolygon([
            cq.Vector(x, y, z - .1),
            cq.Vector(x + direction * chamfer, y, z - .1),
            cq.Vector(x, y + chamfer, z - .1),
        ], close=True)
        stop = stop.cut(cq.Solid.extrudeLinear(wire, [], cq.Vector(0, 0, height + .2)))
    stop = stop.clean()
    old_lid = reference(P['baseline']['lid'])
    lb = bounds(old_lid)
    # Remove only relief protruding past the existing rear face. The
    # rear tail, roof, rails and both pin receivers remain unchanged.
    plane = P['lid']['plain_rear_plane_y_mm']
    cutter = box(lb[0, 0] - 1, plane, lb[0, 2] - 1,
                 lb[1, 0] - lb[0, 0] + 2, lb[1, 1] - plane + 1,
                 lb[1, 2] - lb[0, 2] + 2)
    lid = old_lid.cut(cutter).clean()
    return {
        'cartridge-stop-r28': (stop, normalize(stop.rotate((0, 0, 0), (1, 0, 0), 90))),
        'lid-plain-r28': (lid, normalize(lid.rotate((0, 0, 0), (1, 0, 0), 180))),
    }


def main():
    for folder in ['cad', 'print/stl', 'print/slicer', 'print/gcode',
                   'previews', 'verification/meshes', 'source/profiles']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    rows = []
    for name, (assembled, printing) in models().items():
        assert assembled.isValid() and len(assembled.Solids()) == 1, name
        assert printing.isValid() and len(printing.Solids()) == 1, name
        for shape, target in [(assembled, ROOT / 'cad' / (name + '.step')),
                              (printing, ROOT / 'cad' / (name + '-print.step'))]:
            cq.exporters.export(shape, str(target))
        stl = ROOT / 'print/stl' / (name + '.stl')
        cq.exporters.export(printing, str(stl), tolerance=.025, angularTolerance=.08)
        mesh_of(assembled).export(ROOT / 'verification/meshes' / (name + '.ply'))
        rows.append({'name': name, 'quantity': 1,
                     'assembled_step': 'cad/' + name + '.step',
                     'print_step': 'cad/' + name + '-print.step',
                     'stl': str(stl.relative_to(ROOT)), 'stl_sha256': sha(stl),
                     'assembled_bounds_mm': bounds(assembled).tolist(),
                     'print_bounds_mm': bounds(printing).tolist(),
                     'volume_mm3': assembled.Volume()})
        print(name, bounds(assembled).tolist(), flush=True)
    baselines = {k: v for k, v in P['baseline'].items() if k != 'cartridges'}
    baselines.update(P['baseline']['cartridges'])
    save(ROOT / 'verification/manifest.json', {
        'revision': 'R28', 'units': 'millimeter', 'parts': rows,
        'source_sha256': sha(Path(__file__)),
        'parameters_sha256': sha(ROOT / 'source/parameters.json'),
        'baseline_sha256': {v: sha(PROJECT / v) for v in baselines.values()},
        'physical_fit_verified': False, 'sent_to_printer': False,
    })


if __name__ == '__main__':
    main()
