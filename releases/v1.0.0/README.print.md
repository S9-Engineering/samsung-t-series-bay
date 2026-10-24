# S9 Samsung T-Series Bay — v1.0.0 print pack

Internal geometry revision **R27**. Designed for **ELEGOO Centauri Carbon 2 Combo / 0.4 mm nozzle / textured PEI / ELEGOO PLA BASIC**. Status: **Ready for printing (digital checks); full-kit physical and thermal validation pending**.

This ZIP is the printing selection for v1.0.0: two native sliced 3MF projects, separate oriented STLs, optional matching G-code, assembly images and integrity metadata. It contains no CAD, scripts or older revisions. Source and reports remain in the GitHub repository. Gold/blue assembly colours are illustrative; all parts use the same PLA BASIC.

## Compatibility and dimensions

| Device | Nominal length × height × thickness | v1.0.0 cartridge |
| --- | --- | --- |
| Samsung T7 | 85 × 57 × 8 mm | Included |
| Samsung T7 Shield | 88 × 59 × 13 mm | Included |
| Samsung T9 | 88 × 60 × 14 mm | Included |
| Samsung T5 | Different format | **Not supported in v1.0.0**; dedicated cartridge not included |

The three base positions accept any of the included cartridges. Universality comes from swapping the model-specific cartridge, not squeezing different drives into one frame. T5 EVO and other formats are outside this release. Device dimensions are nominal; check the actual drives before a full print.

External envelope: **90 mm wide × 109.8 mm deep × 86 mm high**, excluding rubber feet and external cables. Front is Y=0; USB exits towards +Y. Slot centres are 24 mm apart. The largest nominal drive faces have a 10 mm gap, with the cartridges interrupting that space locally.

Monolithic sharp-edged shell, horizontal top slots, side ventilation pattern, small raised front S9 and centred **32 × 19.8 mm S9 Engineering** rear logo, both with 0.4 mm relief. The roof slides on rigid guides and is held by two hidden quarter-turn pins. No elastic lid arms remain.

## What you need

### Printing requirements

- ELEGOO Centauri Carbon 2 Combo, **0.4 mm nozzle**, **textured PEI** plate; the prepared layouts use the 256 × 256 mm profile and its excluded corner.
- **ELEGOO PLA BASIC**, 1.75 mm, one available colour. Allow at least **241 g** for coupon plus complete kit, then a practical reserve for loading and calibration. Charcoal in the renders is illustrative; the spool colour was not specified.
- **ElegooSlicer 1.5.3.5** (engine 2.4.2), profile **Elegoo Centauri Carbon 2 0.4 nozzle**. This is the profile name used for the confirmed Combo setup. A different printer/profile requires new slicing and checks.
- Clean, dry filament and a clean PEI plate. Flush cutters or a deburring tool for the brim; no support-removal tools are required.

### Final assembly requirements

Print the complete-kit quantities below: **8 components, 7 unique part types**. The fit coupon is separate and uses two additional copies of the same pin.

| Printed component | Quantity in final bay | Print orientation / override | STL |
| --- | ---: | --- | --- |
| Shell | 1 | Upright; 4 walls | [shell-r27.stl](print/stl/shell-r27.stl) |
| Sliding lid with rear tail | 1 | Exterior on PEI; Arachne | [lid-r27.stl](print/stl/lid-r27.stl) |
| Hidden locking pin | 2 | Flat; 100% rectilinear infill | [locking-pin-r27.stl](print/stl/locking-pin-r27.stl) |
| Common front cartridge stop | 1 | Upright handle; 4 walls | [cartridge-stop-r27.stl](print/stl/cartridge-stop-r27.stl) |
| T7 cartridge | 1 | Upright frames; 6 walls | [cartridge-t7-r27.stl](print/stl/cartridge-t7-r27.stl) |
| T7 Shield cartridge | 1 | Upright frames; 6 walls | [cartridge-t7-shield-r27.stl](print/stl/cartridge-t7-shield-r27.stl) |
| T9 cartridge | 1 | Upright frames; 6 walls | [cartridge-t9-r27.stl](print/stl/cartridge-t9-r27.stl) |

Commercial items, supplied separately:

| Item | Quantity | Specification |
| --- | ---: | --- |
| Rubber feet, including transparent types | 4 | Four recesses are Ø10.5 × 0.65 mm. Choose a foot base that fits and enough projection to leave **at least 5 mm of air below the base**; nominal 6 mm foot height is a starting point. Actual commercial feet have not been measured. |
| Portable SSDs | Up to 3 | Use the matching T7, T7 Shield or T9 cartridge; the kit contains one of each. |
| USB cables | One per installed SSD | Matching drive/host cables, connected from the open rear. No internal hub or electronics. |

The enclosure uses **no screws, nuts, threaded inserts, internal glue or adhesive pads**, and requires no assembly tools. If self-adhesive feet are selected, their adhesive is external, in the four underside recesses. Feet and cables are not printed parts.

## Downloads and print files

Open [GitHub Releases](https://github.com/S9-Engineering/samsung-t-series-bay/releases), select **v1.0.0 / R27**, and download **`samsung-t-series-bay-v1.0.0-print-pack.zip`** under **Assets**, together with its SHA-256 file. The automatic GitHub source archives contain the development history; the named print pack is the focused printing download. Keep all parts from the same release.

| Project | Parts | Native 3MF | Filament estimate | Time estimate |
| --- | ---: | --- | ---: | ---: |
| Fit coupon | 4 | [01-fit-coupon-r27-ecc2-pla-basic.3mf](print/3mf/01-fit-coupon-r27-ecc2-pla-basic.3mf) | 26.15 g | 1 h 35 min 49 s |
| Complete kit, one plate | 8 | [02-full-kit-r27-ecc2-pla-basic.3mf](print/3mf/02-full-kit-r27-ecc2-pla-basic.3mf) | 214.07 g | 12 h 30 min 42 s |

These are **native, sliced ElegooSlicer projects** with machine/material/process and object overrides, not geometry-only 3MFs. Times and consumption come from the retained actual slicing, including brim; they are not measured print results. The combined estimate is **240.22 g / 14 h 6 min 31 s**. There is no purge tower and no multicolour change.

The coupon plate contains [shell coupon](print/stl/coupon-shell-r27.stl) ×1, [lid coupon](print/stl/coupon-lid-r27.stl) ×1 and [locking pin](print/stl/locking-pin-r27.stl) ×2. The complete-kit plate already includes its own two pins.

All separate STLs are **print-oriented in millimetres**. Import one file per component, preserving the supplied orientation; duplicate the locking pin. A reference assembly STEP is not a printable plate. To change the number of each cartridge, replace that cartridge in the slicer, keep all clearances and overrides, and reslice/review the changed plate.

Optional exported G-code is included in `print/gcode/` for the exact configuration above. Prefer opening the 3MF to inspect the configuration before sending anything to the printer. G-code generated for this setup must not be reused after changing the printer, nozzle, plate or material without new slicing.

### Prepared settings

| Setting | Value |
| --- | --- |
| Layer height | 0.20 mm |
| Walls | 4 general; 6 on drive cartridges |
| Infill | 20% gyroid general; 100% rectilinear on both pins |
| Wall generator | Arachne on lid and lid coupon to preserve thin lettering; other objects retain their saved generator |
| Nozzle / textured PEI bed | 220 °C / 60 °C |
| Volumetric flow limit / bridge speed | 5 mm³/s / 25 mm/s |
| Filament / process flow ratios | 0.98 / 0.97; inherited starting values, not a new spool calibration |
| Pressure advance | 0.04; verify for the actual spool if needed |
| Brim | Outer, 5 mm; 0.10 mm separation |
| Elephant-foot compensation | 0.10 mm |
| Supports / raft / fuzzy skin | Disabled |
| Material assignment | One PLA BASIC channel for all objects; choose the actual loaded CANVAS channel |

The slicer retains one warning: **`bed_temperature_too_high_than_filament` (1000C001)**. Its 45 °C warning threshold is below the saved 60 °C bed setting. Use the documented PLA setup with the **front door open**; verify actual ambient conditions and first-layer adhesion. This warning has been reviewed, not silently removed. Other material settings remain those saved in the native project.

## How to

### Download and prepare

1. Open the Releases page above, choose the intended version and extract the named print pack. Read its root `README.md`; do not mix in older revision parts.
2. Optionally verify the download with `shasum -a 256 -c samsung-t-series-bay-v1.0.0-SHA256SUMS.txt` from the directory containing the downloaded ZIP and checksum file. Inside the extracted package, `shasum -a 256 -c SHA256SUMS.txt` checks its members.
3. Open **01-fit-coupon-r27-ecc2-pla-basic.3mf** in ElegooSlicer, retaining its project settings. Confirm the machine, 0.4 mm nozzle, textured PEI and the loaded PLA BASIC channel. Inspect the first layer and full preview. If your slicer discards a saved setting, restore it and reslice before printing.
4. Clean the plate, open the front door for PLA, run the printer's normal bed levelling and check the first layer. Let the parts and plate cool before removal. Remove brim and any stray strings without rounding the mating edges.

![Exploded sliding-lid coupon and two pins](assembly/01-fit-coupon.png)

### Test the fit coupon first

5. Slide the lid sample into the shell sample from the rear. Both guides must engage fully without visible wall bending. In the image the gold piece is lifted only to reveal the mechanism; installation is by sliding along the guides.
6. Insert each pin **from below**, turn it **90°**, then lower it **1.1 mm** into its seat. The two receivers are mirrored; use the quarter-turn direction that seats the crossbar. The same printed pin fits either side.
7. Check that the sample lid cannot slide out with both pins seated. To unlock, lift a pin 1.1 mm, turn it back, and remove it; repeat on the other side. Try several gentle cycles. Proceed only if both sides seat, turn and release by hand without cracking, forcing or loose engagement. Record the actual fit; a CAD clearance is not a physical fit measurement.
8. Open **02-full-kit-r27-ecc2-pla-basic.3mf** and print its one plate after the coupon passes. Keep the supplied object orientations and overrides. Remove brim and strings, especially from guide entries, frame openings and pin seats.

![Nominal SSD sliding into its model-specific cartridge](assembly/02-drive-cartridge.png)

### Load the drive cartridges

9. With the USB cable unplugged, insert each drive **from the rear through both frames** of its matching cartridge. The image uses a simplified nominal SSD envelope, without a connector or brand detailing. The nominal lateral clearance is **0.40 mm total (0.20 mm per side)**; the top allowance is **0.50 mm**. The drive should enter by hand and remain upright without rattling or spreading the frame.
10. Each model-specific cartridge can occupy any of the three identical base positions. Do not put a smaller drive in a larger cartridge and assume it will be supported. If the real drive binds, stop and check the frame opening and printer calibration before proceeding.

![Cartridges above the shell and separate common front stop](assembly/03-cartridge-seating.png)

### Seat the cartridges and front stop

11. Position each cartridge **6 mm forward** of its final position, lower its foot into the base, then slide it **6 mm towards the rear** under the four short rigid tabs. The foot has **0.20 mm clearance per side** and **0.20 mm vertical clearance**. Do not pry or flex the tabs.
12. Lower the common front stop into the gap between the front wall and the cartridge feet. Its three lower blocks prevent the feet sliding forward; its tall handle is for removal. The stop sits on the floor **beside the feet**, not underneath them. It must sit flat, leaving each cartridge seated and upright.
13. Fit the four rubber feet in the underside recesses and verify at least 5 mm of air below the base. Keep all bottom ventilation slots clear.

![Sliding roof and open rear connector area](assembly/04-slide-lid.png)

### Connect the cables and close the lid

14. Connect the USB cables through the rear opening. The rear tail ends above the connector area; plugs and cable bends stay **outside the enclosure**. Nominal connector envelopes are generous **20 × 20 mm** with up to **50 mm rigid cable length**, but actual port location and cable clearance still need a physical check. Plugs must not bear on the tail or pull on the cartridges.
15. Slide the lid forward from the rear until fully seated in both guides. Leave approximately **110 mm behind the bay** for lid removal, plus the natural cable bend. Do not force it against a connector.

![Lid underside with both hidden locking pins](assembly/05-locking-pins.png)

16. Insert both pins from below, turn each 90°, then lower it 1.1 mm into its seat, as tested on the coupon. The view hides the shell to show the two mechanisms; blue and gold are diagram colours only. No screw, spring tab or side clip must be bent.
17. Check that the lid stays seated, both pins are retained, all three drives stand upright and the cables remain accessible. The stop is gravity-seated for an upright desktop bay; the product is not qualified for inverted transport.
18. To open, lift/turn/remove **both** pins and slide the lid rearward. To remove a cartridge, unplug its cable, lift the common stop by its handle, slide the cartridge forward 6 mm, and lift it out.

### First-use check

19. Begin with an idle test, then compare the same drives and workload inside and outside the bay, especially the centre drive. Check drive temperature, throttling, stability and any PLA distortion. Bottom inlets, top exhaust slots and side openings provide a passive airflow path; airflow rate and temperature rise have not been measured. Keep the bay ventilated and away from direct heat. No fan is included or required by the assembly instructions.
20. Record material, settings, dimensions, coupon fit and full-kit observations before treating the assembly as physically validated. Recheck the pins and cartridge seating after the first warm run.

## Verification and limitations

The selected files were reopened without modifying the R27 geometry: 9 single-solid STL/STEP part types, 4 coupon parts, 8 complete-kit parts, correct millimetre units/transforms, brim/bed clearance and positive closed meshes. Both native 3MFs contain the matching exported G-code. All 145 coupon and 415 complete-kit layers were reparsed, with reviewed original preview sheets. There was no new slicing solely for publication.

The original self-intersection screening and collision-sweep results are retained for identical files, with their documented limits. These checks do not prove print strength or physical fit. The earlier internal-seat coupon passed according to user feedback; full R27 assembly, two-pin retention/durability, real drive/connector fit, feet and thermal behaviour remain physically unverified. Begin with the included coupon. No print has been started automatically.

No license has been selected for the project. Samsung names identify the intended devices; the enclosure is an independent design.
