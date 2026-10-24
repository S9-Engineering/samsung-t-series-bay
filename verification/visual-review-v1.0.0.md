# v1.0.0 visual and slicing review

Revision: R27. The publication work leaves all original geometry and slicing files unchanged. This review uses their verified hashes and reopened final exports, not a new slicing run.

## Slicer preview evidence reviewed

The seven `TUTTI_*` sheets in the retained revision's `verifiche/slicing/COMPLETO/` and `PROVINO/` show every one of the 415 complete-kit and 145 coupon layers. All sheets were opened for publication review. First-layer footprints/brims, the two pins, carrier feet, frames, shell/lid walls and final layers remain present in the intended plate positions.

Additional details opened: both jobs' `PRIMO_INTERMEDI_ULTIMO`, `GUIDE_E_PERNO_SX`, `GUIDE_E_PERNO_DX`, `DUE_PERNI`; complete-kit `PONTI_T7`, `PONTI_T7_Shield`, `PONTI_T9`, `PONTI_LUNGHI_04` and `LOGO_PERCORSI`. These show the pin crossbars/receivers, the frame bridge starts and supported later layers, and all 13 rear-logo glyphs. Physical bridge quality and small-letter finish remain unproven.

The new reopening script independently checked both native 3MF structures/units/transforms and object count, 5 mm brim spacing/bed exclusion, then reparsed the matching G-code for all layers and bed bounds. The embedded and exported G-code hashes match. The original collision sweeps and self-intersection screening are reused with their original limitations; this is not a new load or retention test.

The only retained slicer warning is `bed_temperature_too_high_than_filament` / `1000C001`: saved bed 60 °C versus warning threshold 45 °C. The active English instructions keep this visible and specify the PLA front-door-open setup. No support, raft or purge tower is used.

## Publication images

Images use the actual final R27 assembly PLY meshes, with rigid pin rotation/mirroring and nominal cartridge positioning matching the source. Hero plus separate front, side and rear views show the same geometry. Five assembly views explain the coupon, model-specific frame, cartridge seating/common stop, sliding roof/rear opening and both hidden pins. Illustrative colours and exploded offsets are declared in the captions. SSD envelopes are schematic. Feet/cables are omitted from studio renders and remain user-supplied items in the BOM.

The visual checks do not establish physical print strength, fit, thermal performance or a measured surface finish. The source report records every input mesh hash and final image hash.
