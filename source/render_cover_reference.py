"""Create the CAD references used for the contextual cover, without editing CAD.

Run with source/requirements-render.txt installed:
  .venv/bin/python source/render_cover_reference.py

The final desk composition is produced with the built-in image generation tool
using assets/cover-references/cover-prompt.txt and the three declared references.
"""
from pathlib import Path
import shutil
import render_release as r

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = ROOT/'assets/cover-references'
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/'previews/renders/hero.png', target/'r27-closed-cad.png')
    parts = r.assembly(roof=False, drives=True)
    colours = [(0.18, 0.34, 0.47), (0.04, 0.05, 0.065), (0.035, 0.04, 0.045)]
    for i, colour in enumerate(colours):
        index = 3+2*i
        mesh, _ = parts[index]
        parts[index] = (mesh, colour)
    path = r.render('cover-open-reference-r27', parts,
                    (210, 300, 260), (45, 55, 42),
                    fov=30, size=(1400, 1150), spp=256)
    shutil.move(path, target/'r27-open-cad.png')


if __name__ == '__main__':
    main()
