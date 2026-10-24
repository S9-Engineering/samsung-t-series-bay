"""Prepare English R27 documentation and byte-identical convenience copies.

Does not edit retained revisions, generate geometry, slice, or publish anything.
Once the v1.0.0 print archive exists, its packaged README and manifest are
preserved; current repository documentation and release presentation can evolve.
Run from any directory: python3 source/prepare_release_docs.py
"""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]
REV=ROOT/'versions/bay-ssd-r27-logo-retro-80-pla'
REL='versions/bay-ssd-r27-logo-retro-80-pla'
RELEASE=ROOT/'releases/v1.0.0'
URL='https://github.com/S9-Engineering/samsung-t-series-bay/releases'
PARTS=[
 ('SCOCCA_R27_DOPPIO_PERNO','shell-r27','Shell',1,'Upright; 4 walls'),
 ('TETTO_R27_DOPPIO_PERNO','lid-r27','Sliding lid with rear tail',1,'Exterior on PEI; Arachne'),
 ('PERNO_R27_NASCOSTO','locking-pin-r27','Hidden locking pin',2,'Flat; 100% rectilinear infill'),
 ('FERMO_CARTUCCE_R27','cartridge-stop-r27','Common front cartridge stop',1,'Upright handle; 4 walls'),
 ('CARTUCCIA_T7_R27','cartridge-t7-r27','T7 cartridge',1,'Upright frames; 6 walls'),
 ('CARTUCCIA_T7_Shield_R27','cartridge-t7-shield-r27','T7 Shield cartridge',1,'Upright frames; 6 walls'),
 ('CARTUCCIA_T9_R27','cartridge-t9-r27','T9 cartridge',1,'Upright frames; 6 walls'),
 ('PROVINO_GUIDE_SCOCCA_R27','coupon-shell-r27','Shell fit coupon',1,'Upright; coupon plate only'),
 ('PROVINO_GUIDE_TETTO_R27','coupon-lid-r27','Lid fit coupon',1,'Exterior down; coupon plate only; Arachne'),
]
JOBS=[('BAY_R27_01_PROVINO_DOPPIO_PERNO','01-fit-coupon-r27-ecc2-pla-basic','Fit coupon','4','26.15 g','1 h 35 min 49 s'),
      ('BAY_R27_02_KIT_COMPLETO_UNICO_PIATTO','02-full-kit-r27-ecc2-pla-basic','Complete kit, one plate','8','214.07 g','12 h 30 min 42 s')]
IMAGES=['01-fit-coupon','02-drive-cartridge','03-cartridge-seating','04-slide-lid','05-locking-pins']


def write(path,text):
 if (path.parent == RELEASE and path.name in {'README.print.md','manifest.json'}
     and (RELEASE/'assets/samsung-t-series-bay-v1.0.0-print-pack.zip').exists()):
  if not path.is_file():
   raise RuntimeError(f'Missing frozen release input: {path}')
  return
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.strip()+'\n')


def content(pack=False):
 slicer='print/3mf' if pack else 'print/slicer'
 images='assembly' if pack else 'previews/assembly'
 out='''## Compatibility and specifications

| Samsung portable SSD | Length × height × thickness | Cartridge |
| --- | --- | --- |
| **T7** | 85 × 57 × 8 mm | T7 cartridge included |
| **T7 Shield** | 88 × 59 × 13 mm | T7 Shield cartridge included |
| **T9** | 88 × 60 × 14 mm | T9 cartridge included |

Three drives stand side by side on their long edges, with their USB ports facing the open rear. Each of the three base positions accepts any of the included model-specific cartridges. The complete kit supplies one cartridge for each model above.

- **Overall size:** 90 × 109.8 × 86 mm (width × depth × height), excluding feet and external cables.
- **Enclosure:** sharp-edged monolithic shell, flat slotted roof and horizontal side ventilation pattern.
- **Cooling:** passive ventilation through the base, sides and top. Four rubber feet keep the bottom air inlets clear.
- **Access:** sliding roof on rigid guides, secured by two hidden quarter-turn pins. USB plugs and cable bends remain outside the enclosure.
- **Branding:** raised S9 on the front and S9 Engineering centred on the rear tail, 0.4 mm relief.

## What you need

### For printing

- **ELEGOO Centauri Carbon 2 Combo**, **0.4 mm nozzle**, **textured PEI** plate.
- **ELEGOO PLA BASIC**, 1.75 mm, one colour; the complete plate uses an estimated **214.07 g**. Have additional filament available for loading and normal machine preparation. Render colour is illustrative; use your available PLA BASIC colour.
- **ElegooSlicer 1.5.3.5** with the included native project. The saved printer profile is named **Elegoo Centauri Carbon 2 0.4 nozzle** for the confirmed Combo setup, with a 256 × 256 mm plate and its excluded corner.
- A clean plate, dry filament and flush cutters or a deburring tool for the brim.

### For assembly

**8 printed components, supplied on one plate:**

| Printed component | Quantity | Print orientation / setting | STL |
| --- | ---: | --- | --- |
'''
 for old,slug,title,qty,orientation in PARTS[:7]:
  out+=f'| {title} | {qty} | {orientation} | [{slug}.stl](print/stl/{slug}.stl) |\n'
 out+='''
| Additional item | Quantity | Specification |
| --- | ---: | --- |
| Rubber feet, including transparent types | 4 | Base fitting the Ø10.5 × 0.65 mm underside recesses, with enough projection to leave **at least 5 mm of air below the bay**. A nominal 6 mm foot height is a starting selection; match the actual foot to the recess. |
| Samsung SSDs | Up to 3 | T7, T7 Shield or T9, using the corresponding cartridge. |
| USB cables | One per drive | Matching cables for your SSDs and host, connected from the rear. |

Assembly is tool-free. There are **no screws, nuts, threaded inserts or internal adhesives**. If you choose self-adhesive rubber feet, their adhesive stays in the four exterior underside recesses. Feet, drives and cables are supplied separately; there is no internal USB hub.

## Download and print

'''
 out+=f'''1. Open [GitHub Releases]({URL}) and select **v1.0.0**.
2. Under **Assets**, download **`samsung-t-series-bay-v1.0.0-print-pack.zip`** and extract it. Use this print pack rather than GitHub's automatic source archives.
3. Read the extracted `README.md` and open **[02-full-kit-r27-ecc2-pla-basic.3mf]({slicer}/02-full-kit-r27-ecc2-pla-basic.3mf)** in ElegooSlicer. Keep its project settings, object orientations and per-object overrides.
4. Select your loaded PLA BASIC channel, confirm the printer/nozzle/plate, and inspect the print preview before sending the job. Use the printer's normal bed-levelling procedure and print with the **front door open for PLA**.
5. Let the plate cool, remove the parts and trim off the brim and stray strings, especially at the guides, cartridge openings and pin seats.

The native 3MF contains the complete one-plate layout, machine/material/process profiles, per-object settings and sliced paths. It is a full slicer project. Separate STLs are already oriented for printing in **millimetres**; print two copies of the locking pin when building a plate from STLs.

**Slicer estimate:** **214.07 g / 12 h 30 min 42 s**, including brim, for all 8 components. One material, no purge tower. This is a slicer estimate, not a measured print time.

'''
 if not pack:
  out+='The same [printing ZIP](releases/v1.0.0/assets/samsung-t-series-bay-v1.0.0-print-pack.zip) is stored in this repository. All development files and retained revisions are separate from the release download.\n\n'
 out+='''### Print settings

| Setting | Prepared value |
| --- | --- |
| Filament | ELEGOO PLA BASIC, one channel |
| Layer height | 0.20 mm |
| Walls | 4 general; 6 on the drive cartridges |
| Infill | 20% gyroid; pins 100% rectilinear |
| Wall generator | Arachne on the lid for the rear lettering |
| Nozzle / textured PEI bed | 220 °C / 60 °C |
| Volumetric flow limit / bridge speed | 5 mm³/s / 25 mm/s |
| Brim | Outer, 5 mm; 0.10 mm separation |
| Elephant-foot compensation | 0.10 mm |
| Supports / raft / fuzzy skin | Disabled |

Use the settings stored in the 3MF. If changing the printer, nozzle, material or part quantities, reslice for the new configuration. The included optional G-code in `print/gcode/` matches the setup above; opening the 3MF is the recommended route.

The archive includes `SHA256SUMS.txt` for file integrity. The separate release checksum file verifies the downloaded ZIP with `shasum -a 256 -c samsung-t-series-bay-v1.0.0-SHA256SUMS.txt` from the download directory.

## Assembly

Gold and blue in the following images distinguish the pieces; the print project uses a single PLA colour. Drive shapes are schematic envelopes.

'''
 out+=f'''![Drive entering a model-specific cartridge from the rear]({images}/02-drive-cartridge.png)

### Load the cartridges

1. With the USB cable unplugged, slide each drive **from the rear through both frames** of its matching cartridge: T7, T7 Shield or T9. The USB port faces the rear.
2. Choose the cartridge's position in the bay. The three base positions share the same interface, so any included cartridge can occupy any position.

![Three cartridges and the common front stop above the shell]({images}/03-cartridge-seating.png)

### Seat the cartridges

3. Hold each cartridge **6 mm forward** of its final position, lower its foot into the base, then slide it **6 mm towards the rear** under the four short rigid tabs.
4. Lower the common front stop into the gap between the front wall and the cartridge feet. Its three lower blocks prevent forward movement; the tall handle lets you lift it out. The stop rests on the floor beside the feet.
5. Fit the four rubber feet in the underside recesses, leaving at least 5 mm of air under the base and keeping the bottom slots unobstructed.

![Roof sliding forward along its guides with rear connector access open]({images}/04-slide-lid.png)

### Connect and close

6. Connect the USB cables through the rear opening. Keep the plugs and cable bends outside the enclosure, clear of the rear tail.
7. Slide the lid forward from the rear until fully seated in both guides. Leave approximately **110 mm behind the bay** for roof removal, plus space for the natural cable bend.

![Underside of the lid showing its two hidden locking pins]({images}/05-locking-pins.png)

8. Insert each pin **from below**, turn it **90°**, then lower it **1.1 mm** into its seat. The two receivers are mirrored; turn each pin in the direction that seats its crossbar. Both pins are identical printed parts. The image hides the shell so the locking arrangement is visible.
9. Place the bay upright on the desk with the ventilation openings clear and the cables relaxed.

### Open or remove a drive

10. Lift each pin **1.1 mm**, turn it back and remove it. Remove **both** pins before sliding the roof rearward.
11. Unplug the drive cable, lift the common front stop by its handle, slide the cartridge forward **6 mm**, and lift it out. Slide the drive out of its cartridge from the rear.
'''
 return out


def public_content():
 """Current brand-neutral overview; retain the published package instructions."""
 original=content(False)
 prefix, rest=original.split('### For printing\n\n',1)
 _, rest=rest.split('### For assembly\n\n',1)
 assembly_bom, rest=rest.split('## Download and print\n\n',1)
 _, rest=rest.split('### Print settings\n\n',1)
 settings, assembly=rest.split('## Assembly\n\n',1)
 table=settings.split('Use the settings stored in the 3MF.',1)[0]
 table=table.replace('| Setting | Prepared value |','| Print setting | My value |')
 table=table.replace('| Filament | ELEGOO PLA BASIC, one channel |\n','')
 assembly_bom=assembly_bom.replace('**8 printed components, supplied on one plate:**',
     '**8 printed components:**')
 assembly_bom=assembly_bom.replace('Exterior on PEI; Arachne','Exterior on the build plate; Arachne')
 printing='''### For printing

- PLA filament in your chosen colour.
- Flush cutters or a deburring tool for removing the brim.

### For assembly

'''
 download=f'''## Download STL and 3MF files

1. Open [GitHub Releases]({URL}) and select **v1.0.0**.
2. Under **Assets**, download **`samsung-t-series-bay-v1.0.0-print-pack.zip`**, extract it and read its `README.md`.
3. Import the [separate STLs](print/stl) into your slicer in **millimetres**, keeping their supplied orientations. Use the quantities listed above, including **two copies of the locking pin**.
4. Arrange the parts for your build plate, apply your printer and PLA profile with the part settings below, and inspect the slicing preview. The supplied [reference 3MF](print/slicer/02-full-kit-r27-ecc2-pla-basic.3mf) already contains the one-plate layout and configuration described in **My setup**.
5. Print the parts, let the plate cool, and remove the brim and stray strings from the guides, cartridge openings and pin seats.

The 3MF is a complete native slicer project with saved profiles, object overrides and sliced paths. Its optional G-code in `print/gcode/` is tied to the reference configuration below. Use the separate STLs to slice for your own equipment.

The same [printing ZIP](releases/v1.0.0/assets/samsung-t-series-bay-v1.0.0-print-pack.zip) is stored in this repository. The archive includes `SHA256SUMS.txt`; the separate release checksum file verifies the downloaded ZIP with `shasum -a 256 -c samsung-t-series-bay-v1.0.0-SHA256SUMS.txt` from the download directory.

## My setup

This is the reference configuration used to prepare the included 3MF and G-code. You can use the separate STLs with your own printer and material profile.

| Item | What I used |
| --- | --- |
| Printer | ELEGOO Centauri Carbon 2 Combo |
| Printer profile | Elegoo Centauri Carbon 2 0.4 nozzle; 256 × 256 mm plate with the profile's excluded corner |
| Nozzle | 0.4 mm |
| Build plate | Textured PEI |
| Filament | ELEGOO PLA BASIC, 1.75 mm, one colour/channel |
| Slicer | ElegooSlicer 1.5.3.5, engine 2.4.2 |
| PLA enclosure setup | Front door open |
| Reference layout | All 8 printed components on one plate |
| Slicer estimate for this setup | 214.07 g / 12 h 30 min 42 s, including brim; one material, no purge tower |

'''
 return prefix+printing+assembly_bom+download+table+'''These are the saved reference values. Temperature, flow and the plate layout should follow your own printer/material configuration when you reslice. The time and consumption above are slicer estimates for this setup.

## Assembly

'''+assembly


def main():
 RELEASE.mkdir(parents=True,exist_ok=True)
 copies=[]
 def copy(src,dst):
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
  assert src.read_bytes()==dst.read_bytes()
  copies.append({'source':str(src.relative_to(ROOT)),'copy':str(dst.relative_to(ROOT)),
                 'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
 for old,slug,*_ in PARTS:
  copy(REV/'stampa/STL'/(old+'.stl'),ROOT/'print/stl'/(slug+'.stl'))
  copy(REV/'CAD'/(old+'.step'),ROOT/'cad'/(slug+'.step'))
 copy(REV/'CAD/ASSIEME_R27_NON_STAMPARE.step',ROOT/'cad/reference-assembly-r27-do-not-print.step')
 for old,slug,*_ in JOBS:
  copy(REV/'stampa/progetti_ElegooSlicer'/(old+'_ECC2_PLABASIC.3mf'),ROOT/'print/slicer'/(slug+'.3mf'))
  copy(REV/'stampa/GCODE'/(old+'_ECC2_PLABASIC.gcode'),ROOT/'print/gcode'/(slug+'.gcode'))
 write(ROOT/'verification/convenience-copies.json',json.dumps({'copies':copies},indent=2))
 header='''# S9 Monolith Bay — DIY 3D-Printable SSD Enclosure

### For Samsung T7, T7 Shield and T9

**Build your own** compact three-drive desktop SSD bay. Download the **STL and 3MF files**, 3D print the PLA parts and assemble an enclosure for **Samsung T7, T7 Shield and T9**, with interchangeable cartridges, passive ventilation and rear cable access.

**v1.0.0 · R27 · PLA · 8 printed components**

![DIY 3D-printable Samsung SSD enclosure on a desk, closed and open with three installed SSDs](previews/renders/hero-desk-closed-open-v2.png)

*AI-generated visualization of the closed bay and open enclosure with three installed SSDs. S9 Engineering signature at bottom right; AI disclosure at bottom left.*

## Product views

| Front | Side | Rear and cable access |
| --- | --- | --- |
| ![Front with raised S9](previews/renders/product-front.png) | ![Horizontal side ventilation](previews/renders/product-side.png) | ![S9 Engineering rear tail and lower cable opening](previews/renders/product-rear.png) |
'''
 footer=f'''## Project files and editable CAD

The repository contains the complete project: current STL, native 3MF, matching G-code, STEP, editable CAD, render assets and retained design revisions. The release print pack contains only the complete kit and its assembly instructions.

- [Current STEP exports](cad): editable-format geometry plus a reference assembly. The assembly STEP contains the parts and drive envelopes in their installed positions; use the separate STL or native 3MF for printing.
- [R27 CAD generator]({REL}/sorgenti/genera.py), [parameters]({REL}/sorgenti/parametri.json), and [pinned dependencies]({REL}/sorgenti/requirements.txt).
- [Retained revision index](docs/revision-history.md). Historical studies and filenames stay in their original language; use this README for v1.0.0 printing and assembly.
- [Render source](source/render_release.py) and [render dependencies](source/requirements-render.txt). [Contextual cover prompt and CAD references](assets/cover-references/cover.json).

To edit/regenerate CAD after cloning, create an environment inside this repository:

```sh
python3.11 -m venv .venv-cad
.venv-cad/bin/pip install -r {REL}/sorgenti/requirements.txt
.venv-cad/bin/python {REL}/sorgenti/genera.py
```

The generator writes to that revision's CAD, STL and manifest paths. Keep released files intact and save design changes as a new revision. `source/prepare_release_docs.py` recreates the English documentation, release selection and byte-identical current-file copies. No sibling project is required.

## License and attribution

Original project designs and documentation are licensed under **CC BY-NC-SA 4.0** ([LICENSE.txt](LICENSE.txt)). Original S9 software, including CAD generators and build/render scripts, is licensed under **PolyForm Noncommercial 1.0.0** ([LICENSE-SOFTWARE.txt](LICENSE-SOFTWARE.txt)). Read [LICENSING.md](LICENSING.md) for scope, required notices, separate commercial permissions, S9 branding and third-party exclusions. The software is source-available; generated models retain their separately stated design license.

The license grants include covered original material in **v1.0.0** and original software in retained revisions and release source archives. Published archives predate these notices and remain unchanged; historical statements that no license was selected or software terms were undecided are superseded by the current grants in LICENSING.md. Future print packages will include both license texts and the scope notice.

Samsung names identify compatible devices; this is an independent enclosure design with no claim of manufacturer affiliation.
'''
 write(ROOT/'README.md',header+'\n'+public_content()+'\n'+footer)
 intro='''# S9 Monolith Bay — v1.0.0

**Samsung T-Series SSD enclosure · R27 · Complete printing and assembly kit**

For **Samsung T7, T7 Shield and T9**. Prepared for **ELEGOO Centauri Carbon 2 Combo / 0.4 mm nozzle / textured PEI / ELEGOO PLA BASIC**.

This print pack includes the complete eight-piece kit on one plate, separate oriented STLs, optional matching G-code, illustrated assembly instructions and integrity metadata. Editable CAD and retained revisions are available in the GitHub repository.
'''
 write(RELEASE/'README.print.md',intro+'\n'+content(True)+'\nNo project license has been selected. Samsung product names identify the intended devices; this is an independent design.\n')
 notes='''# S9 Monolith Bay — DIY 3D-Printable SSD Enclosure

**v1.0.0 · R27 · Samsung T7, T7 Shield and T9**

Build your own three-drive desktop SSD bay. Download the **STL and 3MF files**, 3D print the PLA parts and assemble a compact enclosure for your Samsung portable SSDs, with interchangeable cartridges, passive ventilation and rear cable access.

![S9 Monolith Bay DIY 3D-printable SSD enclosure, closed and open with three Samsung SSDs](https://raw.githubusercontent.com/S9-Engineering/samsung-t-series-bay/main/previews/renders/hero-desk-closed-open-v2.png)

## Download STL and 3MF files

Under **Assets**, download **`samsung-t-series-bay-v1.0.0-print-pack.zip`** and extract it. The print pack contains:

- **Seven separate, print-oriented STL part types**; print two locking pins for **eight components** in total.
- A complete native **3MF slicer project**, with the reference eight-piece layout on one plate.
- Matching optional G-code for the reference setup below.
- Illustrated English assembly instructions, part quantities and a list of separately supplied items.
- File manifest and SHA-256 checksums.

The named print pack is the printing download. GitHub's automatic source archives contain the full development repository. Editable CAD and STEP files are available in the repository at the **v1.0.0** tag.

## Print and build your own SSD bay

1. Extract the print pack and read its `README.md` for part quantities and assembly images.
2. Import the individual **STLs in millimetres** and slice them using your own printer and PLA profile, or use the reference **3MF** with its saved configuration.
3. Print the eight components, remove the brim and assemble the model-specific cartridges, common front stop, sliding roof and two quarter-turn pins.
4. Add four rubber feet, install the T7, T7 Shield and T9 in their matching cartridges, and connect their USB cables through the rear opening.

The assembly uses **no internal screws or glue**. Supply your drives, USB cables and four rubber feet. Each model-specific cartridge fits any of the three base positions.

## My setup

The native 3MF and optional G-code were prepared with this reference configuration. Use the separate STLs to slice for your own equipment.

| Item | What I used |
| --- | --- |
| Printer | ELEGOO Centauri Carbon 2 Combo |
| Nozzle / plate | 0.4 mm / textured PEI |
| Filament | ELEGOO PLA BASIC |
| Slicer | ElegooSlicer 1.5.3.5 |
| Layer height | 0.20 mm |
| Supports / brim | No supports / 5 mm outer brim |
| PLA setup | Front door open |
| Slicer estimate for this setup | 214.07 g / 12 h 30 min 42 s for all eight components |

[Build guide and product details](https://github.com/S9-Engineering/samsung-t-series-bay#readme) · [All printing releases](https://github.com/S9-Engineering/samsung-t-series-bay/releases)

## License and attribution

Original designs and documentation are licensed under **CC BY-NC-SA 4.0** ([design license](https://github.com/S9-Engineering/samsung-t-series-bay/blob/main/LICENSE.txt)). Original S9 software, including CAD generators and build/render scripts, is licensed under **PolyForm Noncommercial 1.0.0** ([software license](https://github.com/S9-Engineering/samsung-t-series-bay/blob/main/LICENSE-SOFTWARE.txt)). Read the [scope notice](https://github.com/S9-Engineering/samsung-t-series-bay/blob/main/LICENSING.md) for required notices, separate commercial permissions, S9 branding and third-party exclusions. Software sources remain in the repository, outside the print pack.

These grants include covered original material in the **v1.0.0 print pack** and original software in retained revisions and release source archives. The published ZIP and tag remain unchanged and predate these notices; earlier statements that no license was selected or software terms were undecided are superseded by the current grants. Retain the applicable license information and required notices when redistributing.

Samsung product names identify compatible devices; this is an independent DIY enclosure design.
'''
 write(RELEASE/'release-notes.md',notes)
 files=[{'source':'releases/v1.0.0/README.print.md','archive':'README.md','role':'instructions'}]
 for _,slug,*_ in PARTS[:7]:
  f=f'print/stl/{slug}.stl';files.append({'source':f,'archive':f,'role':'stl'})
 for _,slug,*_ in JOBS[1:]:
  files.append({'source':f'print/slicer/{slug}.3mf','archive':f'print/3mf/{slug}.3mf','role':'slicer'})
  files.append({'source':f'print/gcode/{slug}.gcode','archive':f'print/gcode/{slug}.gcode','role':'gcode'})
 for image in IMAGES[1:]:
  files.append({'source':f'previews/assembly/{image}.png','archive':f'assembly/{image}.png','role':'assembly-image'})
 write(RELEASE/'manifest.json',json.dumps({'schema_version':1,'repository':'S9-Engineering/samsung-t-series-bay',
  'tag':'v1.0.0','project_revision':'R27','files':files,
  'gcode':{'verified':True,'printer':'ELEGOO Centauri Carbon 2 Combo','nozzle_mm':0.4,'plate':'Textured PEI',
   'filament':'ELEGOO PLA BASIC','slicer':'ElegooSlicer 1.5.3.5','profile':'Elegoo Centauri Carbon 2 0.4 nozzle',
   'verification_report':'verification/release-v1.0.0.json'}},indent=2))
 print('Prepared S9 Monolith Bay product docs and complete-kit release manifest.')

if __name__=='__main__':main()
