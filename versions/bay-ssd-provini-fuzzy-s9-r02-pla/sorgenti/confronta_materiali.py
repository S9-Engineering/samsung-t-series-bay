"""Controllo aggiuntivo del confronto PLA/PETG; nessuna modifica alla R01."""
from pathlib import Path
import json
import re
import zipfile

import numpy as np
import trimesh

from prepara import ROOT, P, sha, save

def main():
    previous=ROOT.parent/'bay-ssd-provini-fuzzy-s9-r01'
    if not previous.exists():
        raise SystemExit('Per ripetere il confronto affiancare la cartella originale bay-ssd-provini-fuzzy-s9-r01. I controlli autonomi restano disponibili con controlla.py.')
    old=json.loads((previous/'sorgenti/parametri.json').read_text())
    keys=['dimensioni_provino_mm','spessore_parete_mm','spessore_base_mm','logo','campo_fuzzy_mm','campioni','riferimento_PEI']
    assert all(P[k]==old[k] for k in keys)
    assert sha(ROOT/'sorgenti/logo_S9_contorni.json')==sha(previous/'sorgenti/logo_S9_contorni.json')
    assert sha(ROOT/'slicer/machine.json')==sha(previous/'slicer/machine.json')
    meshes=[]
    for path in sorted((ROOT/'stampa/STL').glob('*.stl')):
        original=previous/'stampa/STL'/path.name
        a=trimesh.load_mesh(path,process=True);b=trimesh.load_mesh(original,process=True)
        assert np.max(np.abs(a.bounds-b.bounds))<1e-5 and abs(a.volume-b.volume)<1e-5
        assert len(a.faces)==len(b.faces)
        assert np.max(np.abs(np.sort(a.vertices,axis=0)-np.sort(b.vertices,axis=0)))<1e-5
        meshes.append(dict(name=path.name,stl_sha256=sha(path),original_sha256=sha(original),
            byte_identical=sha(path)==sha(original),geometry_equal=True))
    a=json.loads((ROOT/'slicer/process.json').read_text());b=json.loads((previous/'slicer/process.json').read_text())
    for k in set(a)|set(b):
        if k not in ['name','print_settings_id']:assert a.get(k)==b.get(k),(k,a.get(k),b.get(k))
    f=json.loads((ROOT/'slicer/filament.json').read_text());oldf=json.loads((previous/'slicer/filament.json').read_text())
    fields=['nozzle_temperature','textured_plate_temp','filament_max_volumetric_speed','filament_flow_ratio','filament_density',
        'pressure_advance','fan_min_speed','fan_max_speed','close_fan_the_first_x_layers','slow_down_layer_time','temperature_vitrification']
    profile_comparison={k:dict(PETG=oldf.get(k),PLA=f.get(k)) for k in fields}
    job=json.loads((ROOT/'verifiche/slicing/job.json').read_text())
    with zipfile.ZipFile(ROOT/job['project']) as z:
        settings=json.loads(z.read('Metadata/project_settings.config'))
        assert settings['filament_type']==['PLA'] and settings['filament_vendor']==['Elegoo']
        assert settings['nozzle_temperature']==['220'] and settings['textured_plate_temp']==['60']
        gc=z.read(next(n for n in z.namelist() if n.endswith('.gcode'))).decode()
        commands=[line.split(';')[0].strip() for line in gc.splitlines()]
        def values(code):
            return [float(m.group(1)) for l in commands if l.startswith(code+' ') and (m:=re.search(r'\bS(-?\d+(?:\.\d+)?)',l))]
        nozzle=values('M104')+values('M109');bed=values('M140')+values('M190')
        assert 220 in nozzle and 240 not in nozzle
        assert 60 in bed and 65 not in bed
    manifest=json.loads((previous/'verifiche/SHA256.json').read_text())
    assert all(sha(previous/n)==h for n,h in manifest.items())
    save(ROOT/'verifiche/confronto_PLA_PETG.json',dict(result='PASS',geometry_parameters_equal=keys,meshes=meshes,
        machine_profile_identical=True,process_equal_except_names=True,material_profiles=profile_comparison,
        actual_gcode_temperature_commands=dict(nozzle_setpoints_C=sorted(set(nozzle)),bed_setpoints_C=sorted(set(bed))),
        original_PETG_files_preserved=len(manifest),physical_comparison_performed=False,
        note='Geometrie e parametri Fuzzy identici; temperatura, raffreddamento e pressure advance specifici del materiale. Non e una misura del risultato fisico.'))
    print('CONFRONTO PLA/PETG: PASS; cinque geometrie identiche, profilo PLA effettivo nel 3MF e nel G-code.')

if __name__=='__main__':main()
