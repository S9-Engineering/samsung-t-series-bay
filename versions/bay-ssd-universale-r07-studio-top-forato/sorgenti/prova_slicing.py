"""Confronto preliminare di orientamenti; non approva una stampa R07."""
import json,tempfile,zipfile,shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import trimesh
import genera as g
from slicer_utils import run_cli,parse_gcode,render_layers,screen_new_wall_islands

ROOT=g.ROOT
SLICER=Path('/private/tmp/stampe3d-slicer/ElegooSlicer.app/Contents/MacOS/ElegooSlicer')


def main():
    model=json.loads((ROOT/'verifiche/studio.json').read_text())
    process=json.loads((ROOT/'slicer/process.json').read_text())
    process.update(name='R07 STUDIO - supporti dal piano',enable_support='1',support_on_build_plate_only='1')
    profile=ROOT/'slicer/process_prova_supporti.json';g.save(profile,process)
    folder=ROOT/'verifiche/slicing_prova';folder.mkdir(exist_ok=True)
    jobs=[]
    for variant in model['slicing_variants']:
        name=variant['name'];dst=folder/name;dst.mkdir(exist_ok=True)
        print('PROVA SLICING',name,flush=True)
        with tempfile.TemporaryDirectory(prefix='bay-r07-studio-') as td:
            td=Path(td);out=td/'out';out.mkdir()
            mesh=trimesh.load_mesh(ROOT/variant['path'],process=True)
            mesh.apply_translation(-mesh.bounds[0]);mesh.apply_translation([35,35,0])
            source=td/'COPERCHIO_STUDIO.stl';mesh.export(source)
            cli=run_cli(SLICER,['--datadir',str(td/'data'),'--load-settings',str(ROOT/'slicer/machine.json')+';'+str(profile),
                '--load-filaments',str(ROOT/'slicer/filament.json'),'--arrange','0','--orient','0','--slice','0',
                '--export-3mf','SOLO_PROVA.3mf','--outputdir',str(out),str(source)],dst/'slicer.log')
            gcodes=list(out.glob('*.gcode'));assert len(gcodes)==1
            layers,analysis=parse_gcode(gcodes[0])
            assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header']
            assert not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations']
            analysis['new_wall_islands']=screen_new_wall_islands(layers)
            images=render_layers(layers,dst)
            native=out/'SOLO_PROVA.3mf'
            with zipfile.ZipFile(native) as z:
                assert z.testzip() is None
                warnings=[dict(n.attrib) for n in ET.fromstring(z.read('Metadata/slice_info.config')).iter() if n.tag=='warning']
            shutil.copy2(native,dst/'R07_SOLO_PROVA_NON_APPROVATO.3mf')
            supports=[l for l in layers if any('support' in role.lower() for role in l['roles'])]
            picks=sorted({0,min(len(layers)-1,4),min(len(layers)-1,9),len(layers)//2,len(layers)-1,
                          *[l['number']-1 for l in layers if any('bridge' in role.lower() for role in l['roles'])]})
            images['critical_layer_indexes']=picks
            g.save(dst/'analisi.json',analysis)
            job=dict(variant=name,source_stl_sha256=variant['sha256'],model_warnings=warnings,
                layers=len(layers),support_layers=len(supports),
                support_z_span_mm=[min(l['z_mm'] for l in supports),max(l['z_mm'] for l in supports)] if supports else None,
                estimates=analysis['slicer_estimates'],new_wall_candidates=analysis['new_wall_islands']['candidate_count'],
                cli=cli,visual_review_complete=False,physical_validation=False)
            jobs.append(job);g.save(folder/'confronto.json',dict(state='PROVE_NON_APPROVATE_PER_LA_STAMPA',jobs=jobs))
    print(json.dumps(jobs),flush=True)


if __name__=='__main__':main()
