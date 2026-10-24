"""Lettura e anteprime percorsi ElegooSlicer. Adattato dai controlli locali V11."""

from __future__ import annotations

import argparse

import collections

import concurrent.futures

import hashlib

import json

import math

import plistlib

import re

import shutil

import subprocess

import tempfile

from pathlib import Path

import zipfile

import xml.etree.ElementTree as ET

import numpy as np

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]

PARAM = re.compile(r"([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))")

ROLE_COLORS = {"Outer wall": "#233c59", "Inner wall": "#48789a", "Sparse infill": "#299f99",
               "Internal solid infill": "#70ab8e", "Top surface": "#6e4c91", "Bottom surface": "#6e4c91",
               "Bridge": "#d6472d", "Support": "#dc9c2d", "Support interface": "#cf6724", "Brim": "#bdc6d0"}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def estimate_totals(jobs):
    grams, seconds = 0.0, 0
    for job in jobs:
        estimates = job.get("slicer_estimates", {})
        mass = estimates.get("total filament used [g]", estimates.get("filament used [g]", "0"))
        grams += sum(float(v) for v in re.findall(r"\d+(?:\.\d+)?", mass))
        duration = estimates.get("estimated printing time (normal mode)", "")
        for value, unit in re.findall(r"(\d+)\s*([dhms])", duration):
            seconds += int(value)*{"d": 86400, "h": 3600, "m": 60, "s": 1}[unit]
    return {"filament_g": round(grams, 2), "printing_seconds": seconds,
            "note": "Somma delle stime restituite dallo slicer per tutti i piatti completati; include il brim e le impostazioni di questo scenario. Nessuna torre, ogni piatto ha un solo materiale."}

def parse_gcode(path):
    """Legge tutti i movimenti di estrusione del modello, senza eseguirli."""
    layers = []
    current = None
    role = "Custom"
    xyz = np.zeros(3)
    epos = 0.0
    absolute_xyz, absolute_e = True, True
    unsupported = collections.Counter()
    stats = {}
    declared_layers = None
    with path.open() as handle:
        for line_number, line in enumerate(handle, 1):
            if line.startswith("; total layer number:"):
                declared_layers = int(line.split(":", 1)[1])
            if line.startswith(";LAYER_CHANGE"):
                current = {"number": len(layers)+1, "segments": [], "roles": collections.Counter(), "z_mm": None}
                layers.append(current)
            if line.startswith(";Z:") and current is not None:
                current["z_mm"] = float(line.split(":", 1)[1])
            if line.startswith(";TYPE:"):
                role = line.split(":", 1)[1].strip()
            if line.startswith(";") and "=" in line and any(token in line for token in
                    ("filament used [g]", "filament used [cm3]", "filament used [mm]", "estimated printing time (normal mode)")):
                key, value = line.lstrip("; ").strip().split("=", 1)
                stats[key.strip()] = value.strip()
            code = line.split(";", 1)[0].strip()
            if not code:
                continue
            command = code.split()[0]
            values = {k: float(v) for k, v in PARAM.findall(code)}
            if command == "G90":
                absolute_xyz = True
            elif command == "G91":
                absolute_xyz = False
            elif command == "M82":
                absolute_e = True
            elif command == "M83":
                absolute_e = False
            elif command == "G92":
                if "E" in values:
                    epos = values["E"]
                for index, axis in enumerate("XYZ"):
                    if axis in values:
                        xyz[index] = values[axis]
            elif command in ("G0", "G1", "G00", "G01"):
                new = xyz.copy()
                for index, axis in enumerate("XYZ"):
                    if axis in values:
                        new[index] = values[axis] if absolute_xyz else new[index]+values[axis]
                de = (values["E"]-epos if absolute_e else values["E"]) if "E" in values else 0
                if "E" in values:
                    epos = values["E"] if absolute_e else epos+values["E"]
                if de > 1e-7 and np.linalg.norm(new[:2]-xyz[:2]) > 1e-7 and current is not None and role != "Custom":
                    current["segments"].append((float(xyz[0]), float(xyz[1]), float(new[0]), float(new[1]), role))
                    current["roles"][role] += 1
                    if current["z_mm"] is None:
                        current["z_mm"] = float(new[2])
                    if any(token in role.lower() for token in ("bridge", "overhang", "support")):
                        unsupported[role] += 1
                xyz = new
            elif command in ("G2", "G3"):
                if current is not None and role != "Custom":
                    raise RuntimeError("Percorso modello ad archi inatteso: disabilitare enable_arc_fitting e ripetere")
                # I macro iniziali/finali del profilo possono usare archi per lo
                # spurgo; non sono geometria modello e non entrano nell'analisi.
                for index, axis in enumerate("XYZ"):
                    if axis in values:
                        xyz[index] = values[axis] if absolute_xyz else xyz[index]+values[axis]
                if "E" in values:
                    epos = values["E"] if absolute_e else epos+values["E"]
    summary = []
    violations = []
    exclusion_violations = []
    bridge_examples = []
    all_bounds = []
    for layer in layers:
        segments = layer["segments"]
        if segments:
            a = np.array([s[:4] for s in segments]).reshape(-1, 2)
            bounds = np.array([a.min(0), a.max(0)])
            all_bounds.append(bounds)
            # Include bead half-width: the widest proposed first-layer width is .5.
            if np.any(bounds[0]-.25 < -1e-3) or np.any(bounds[1]+.25 > 256+1e-3):
                violations.append({"layer": layer["number"], "bounds_mm": bounds.tolist()})
            endpoints = np.array([s[:4] for s in segments]).reshape(-1, 2, 2)
            bridge_indexes = [i for i, segment in enumerate(segments) if "bridge" in segment[4].lower()]
            bridge_max = 0.0
            if bridge_indexes:
                distances = np.linalg.norm(endpoints[bridge_indexes, 1]-endpoints[bridge_indexes, 0], axis=1)
                bridge_max = float(distances.max())
                for idx in np.argsort(distances)[-3:]:
                    i = bridge_indexes[int(idx)]
                    bridge_examples.append({"layer": layer["number"], "z_mm": layer["z_mm"],
                                            "segment_length_mm": float(distances[idx]), "endpoints_xy_mm": endpoints[i].tolist(),
                                            "role": segments[i][4]})
            low, high = endpoints.min(axis=1)-.25, endpoints.max(axis=1)+.25
            candidates = np.flatnonzero((high[:, 0] >= 246) & (low[:, 0] <= 256) & (high[:, 1] >= 0) & (low[:, 1] <= 20))
            if len(candidates):
                from shapely.geometry import LineString, box
                excluded = box(246, 0, 256, 20)
                hits = [int(i) for i in candidates if LineString(endpoints[i]).buffer(.25).intersects(excluded)]
                if hits:
                    exclusion_violations.append({"layer": layer["number"], "extrusion_segment_indexes": hits[:20], "hit_count": len(hits),
                                                 "examples": [{"endpoints_xy_mm": endpoints[i].tolist(), "role": segments[i][4]} for i in hits[:20]]})
        else:
            bounds = None
            bridge_max = 0.0
        summary.append({"layer": layer["number"], "z_mm": layer["z_mm"], "extrusion_segments": len(segments),
                        "roles": dict(layer["roles"]), "bounds_xy_mm": bounds.tolist() if bounds is not None else None})
        summary[-1]["bridge_max_segment_mm"] = bridge_max
    union = np.array([np.min([b[0] for b in all_bounds], axis=0), np.max([b[1] for b in all_bounds], axis=0)]).tolist() if all_bounds else None
    return layers, {"declared_layer_count": declared_layers, "parsed_layer_count": len(layers), "layers": summary,
                    "all_layers_nonempty": bool(layers and all(x["extrusion_segments"] > 0 for x in summary)),
                    "layer_count_matches_header": declared_layers == len(layers),
                    "extrusion_bounds_xy_mm": union, "out_of_bed_layers": violations,
                    "profile_exclusion_zone_xy_mm": [[246, 0], [256, 20]], "profile_exclusion_zone_violations": exclusion_violations,
                    "bridge_overhang_support_segments": dict(unsupported), "slicer_estimates": stats,
                    "longest_bridge_segments": sorted(bridge_examples, key=lambda x: x["segment_length_mm"], reverse=True)[:20],
                    "bridge_length_note": "Lunghezza del segmento etichettato Bridge dallo slicer, non necessariamente campata libera: puo passare sopra infill o supporti. Valutare gli strati sottostanti.",
                    "limitation": "Tutti gli strati analizzati per presenza e ingombro. I ruoli ponte/sbalzo richiedono valutazione; questo controllo non prova adesione, rimovibilita supporti o resistenza."}

def draw_layer(draw, layer, origin, size, label=True):
    ox, oy = origin
    # Riservare una fascia alle etichette: non coprire i percorsi presso Y=256.
    scale = (size-24)/256
    draw.rectangle((ox, oy, ox+size-1, oy+size-1), outline="#d6dbe0", fill="#fafbfd")
    for x1, y1, x2, y2, role in layer["segments"]:
        color = ROLE_COLORS.get(role, "#738494")
        draw.line((ox+4+x1*scale, oy+size-4-y1*scale, ox+4+x2*scale, oy+size-4-y2*scale), fill=color, width=1)
    if label:
        draw.rectangle((ox+2, oy+2, ox+size-3, oy+12), fill="white")
        draw.text((ox+3, oy+2), f"{layer['number']} z{layer['z_mm']:.2f}", fill="#172b40")

def render_layers(layers, folder):
    folder.mkdir(parents=True, exist_ok=True)
    pages = []
    columns, rows, size, gap, header = 12, 12, 96, 3, 28
    for start in range(0, len(layers), columns*rows):
        subset = layers[start:start+columns*rows]
        used_rows = math.ceil(len(subset)/columns)
        canvas = Image.new("RGB", (columns*(size+gap)+gap, used_rows*(size+gap)+header), "white")
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 7), f"PROVINI FUZZY S9 R01 - percorsi reali - strati {start+1}-{start+len(subset)} / {len(layers)}", fill="#172b40")
        for i, layer in enumerate(subset):
            draw_layer(draw, layer, (gap+(i % columns)*(size+gap), header+(i//columns)*(size+gap)), size)
        out = folder/f"tutti_strati_{start+1:04d}_{start+len(subset):04d}.png"
        canvas.save(out)
        pages.append(str(out))
    sample_names = []
    indexes = sorted(set((0, min(1, len(layers)-1), len(layers)//2, len(layers)-1)))
    canvas = Image.new("RGB", (1024, 1024), "white")
    draw = ImageDraw.Draw(canvas)
    for i, index in enumerate(indexes):
        draw_layer(draw, layers[index], ((i % 2)*512, (i//2)*512), 512)
    out = folder/"dettaglio_primo_secondo_medio_ultimo.png"
    canvas.save(out)
    sample_names.append(str(out))
    return {"all_layer_contact_sheets": pages, "detail_sheets": sample_names,
            "legend": ROLE_COLORS, "full_path_rendered_for_every_layer": True}

def screen_new_wall_islands(layers):
    """Screening conservativo raster dei contorni comparsi senza contatto sotto.

    Non e' una simulazione dell'estrusione: i ponti e l'infill vanno interpretati
    insieme alle tavole degli strati. Non viene usato per approvare un pezzo.
    """
    from scipy import ndimage
    scale, pixels = 2, 513  # 0,5 mm/pixel, piano nominale intero
    previous = None
    candidates = []
    for layer in layers:
        all_image = Image.new("1", (pixels, pixels), 0)
        wall_image = Image.new("1", (pixels, pixels), 0)
        full, walls = ImageDraw.Draw(all_image), ImageDraw.Draw(wall_image)
        for x1, y1, x2, y2, role in layer["segments"]:
            line = (round(x1*scale), round(y1*scale), round(x2*scale), round(y2*scale))
            full.line(line, fill=1, width=1)
            if role in ("Outer wall", "Overhang wall"):
                walls.line(line, fill=1, width=1)
        current = np.asarray(all_image, dtype=bool)
        if previous is not None:
            labels, count = ndimage.label(np.asarray(wall_image, dtype=bool), structure=np.ones((3, 3)))
            supported = ndimage.binary_dilation(previous, structure=np.ones((3, 3)))
            contacts = np.bincount(labels[supported], minlength=count+1)
            sizes = np.bincount(labels.ravel(), minlength=count+1)
            new = np.flatnonzero((contacts == 0) & (sizes >= 8))
            new = new[new > 0]
            for index in new:
                yy, xx = np.where(labels == index)
                candidates.append({"layer": layer["number"], "z_mm": layer["z_mm"], "wall_pixels": int(sizes[index]),
                                   "bounds_xy_mm": [[float(xx.min()/scale), float(yy.min()/scale)], [float(xx.max()/scale), float(yy.max()/scale)]]})
        previous = current
    return {"pixel_mm": .5, "previous_layer_dilation_pixels": 1, "minimum_candidate_pixels": 8,
            "new_outer_wall_island_candidates": candidates, "candidate_count": len(candidates),
            "limitation": "Screening approssimato dei soli contorni esterni. Risoluzione e dilatazione possono nascondere dettagli piccoli o generare falsi positivi; i candidati richiedono ispezione delle anteprime e non provano stampabilita."}

def run_cli(slicer, args, log):
    command = [str(slicer), "--debug", "2", *args]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout)
    errors = [line for line in result.stdout.splitlines() if re.search(r"\berror\b|\bfatal\b", line, re.I)]
    if result.returncode or errors:
        raise RuntimeError(f"ElegooSlicer non completato ({result.returncode}), vedi {log}: {errors[:3]}")
    warnings = [line for line in result.stdout.splitlines() if "warning" in line.lower()]
    return {"exit_code": result.returncode, "warnings": warnings, "command": command}
