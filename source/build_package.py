"""Build the current GitHub print package without publishing a release.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
from pathlib import Path
import hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    package=ROOT/'packages';package.mkdir(exist_ok=True)
    main=(ROOT/'README.md').read_text()
    readme='''# S9 Monolith Bay — R28 print pack

DIY 3D-printable enclosure for Samsung T7, T7 Shield and T9. Current R28 uses an 83.5 mm cartridge stop and a plain rear lid. It accepts the existing R27 shell, cartridges and two pins.

Print the full-kit project once, or print just the replacement parts you need. The stop-only, lid-only and both-parts layouts are alternatives to the full kit; do not print all of them.

## Files and quantities

| Part | Quantity | Print-oriented STL |
| --- | ---: | --- |
| Shell | 1 | [shell.stl](print/stl/shell.stl) |
| Sliding lid | 1 | [lid.stl](print/stl/lid.stl) |
| Hidden locking pin | 2 | [locking-pin.stl](print/stl/locking-pin.stl) |
| Cartridge stop | 1 | [cartridge-stop.stl](print/stl/cartridge-stop.stl) |
| T7 cartridge | 1 | [cartridge-t7.stl](print/stl/cartridge-t7.stl) |
| T7 Shield cartridge | 1 | [cartridge-t7-shield.stl](print/stl/cartridge-t7-shield.stl) |
| T9 cartridge | 1 | [cartridge-t9.stl](print/stl/cartridge-t9.stl) |

Native sliced projects: [full kit](print/slicer/full-kit-ecc2-pla-basic.3mf), [stop only](print/slicer/stop-ecc2-pla-basic.3mf), [lid only](print/slicer/lid-ecc2-pla-basic.3mf), [stop and lid](print/slicer/both-ecc2-pla-basic.3mf).

## What you need and how to print

1. Use PLA filament. No screws, nuts, inserts or internal adhesives are required. Reuse your existing components when replacing the stop/lid.
2. A first complete build needs four rubber feet fitting the diameter 10.5 mm x 0.65 mm underside recesses, with at least 5 mm clearance below the enclosure; up to three supported SSDs and their matching USB cables. No USB hub is included. No dimensionally verified Amazon.it foot listing was found during the 2026-10-25 sourcing check; obtain feet matching the specification rather than an assumed equivalent.
3. Open one native 3MF as a project for the reference setup below. For another machine/material profile, import the STLs in millimetres and reslice. Keep the supplied orientations: shell/cartridge frames upright; lid exterior face down; stop front face down with three blocks up; pins flat and solid.
4. Inspect the first layer and all preview layers for your setup, then print. Let the plate cool and remove the brim and stray strings from the guides and contact edges.
5. The stop's nominal side clearance is 0.25 mm per side in an 84 mm cavity. Reuse existing shell/cartridges/pins; do not force the stop against the walls.

'''
    readme+=main.split('## My setup',1)[1].split('## How to assemble',1)[0]
    readme=readme.replace('This is the reference configuration','## My setup\n\nThis is the reference configuration',1)
    readme+='## How to assemble'+main.split('## How to assemble',1)[1].split('## Editable CAD',1)[0]
    readme+='''## Integrity and licensing

Verify the extracted files with `shasum -a 256 -c SHA256SUMS.txt` from this folder. Optional G-code is specific to the reference setup above. Original designs/documentation: [CC BY-NC-SA 4.0](LICENSE.txt). Original S9 software: [PolyForm Noncommercial 1.0.0](LICENSE-SOFTWARE.txt). See [scope and branding terms](LICENSING.md).

Geometry and actual slicing were checked. No complete R28 physical fit, endurance or thermal test is claimed. Published v1.0.0 remains R27; this current package does not replace its assets.
'''
    repo_readme=re.sub(r'\]\(([^)]+)\)',
                       lambda m:']('+('../'+m[1] if '://' not in m[1] and not m[1].startswith('#') else m[1])+')',readme)
    (package/'README.md').write_text(repo_readme)
    paths=['packages/README.md','LICENSE.txt','LICENSE-SOFTWARE.txt','LICENSING.md']
    parts=['shell','lid','locking-pin','cartridge-stop','cartridge-t7','cartridge-t7-shield','cartridge-t9']
    paths += [f'print/stl/{n}.stl' for n in parts]
    for job in ['full-kit','stop','lid','both']:
        p=ROOT/'verification/slicing'/job/'job.json';d=json.loads(p.read_text());assert d['visual_review_complete']
        for k in ['project','gcode']:
            assert sha((ROOT/d[k]).read_bytes())==d[k+'_sha256'];paths.append(d[k])
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'previews/assembly').glob('0[2-5]-*.png'))]
    entries={'README.md':readme.encode()}
    recipe=[]
    for name in paths:
        if name=='packages/README.md':continue
        assert 'publication-local/' not in name and 'versions/' not in name
        entries[name]=(ROOT/name).read_bytes();recipe.append(dict(source=name,archive=name))
    recipe.insert(0,dict(source='packages/README.md',archive='README.md',
                        transformation='Rebase repository-parent Markdown links to the archive root.'))
    for target in re.findall(r'\]\(([^)]+)\)',readme):
        if '://' not in target and not target.startswith('#'):
            assert target in entries or any(p.startswith(target.rstrip('/')+'/') for p in entries),target
    entries['SHA256SUMS.txt']=''.join(f'{sha(v)}  {k}\n' for k,v in sorted(entries.items())).encode()
    dest=package/'monolith-bay-print-pack.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(entries.items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        for n,b in entries.items():assert z.read(n)==b
    (package/'SHA256SUMS.txt').write_text(f'{sha(dest.read_bytes())}  {dest.name}\n')
    (package/'recipe.json').write_text(json.dumps(dict(revision='R28',release_published=False,files=recipe),indent=2)+'\n')
    (ROOT/'verification/package.json').write_text(json.dumps(dict(result='PASS',path=str(dest.relative_to(ROOT)),sha256=sha(dest.read_bytes()),members=len(entries),bytes=dest.stat().st_size,zip_reopened=True,internal_readme_links_verified=True,portal_files_included=False,public_release_created=False),indent=2)+'\n')
    print('Current R28 print package verified:',dest.stat().st_size,'bytes')
if __name__=='__main__':main()
