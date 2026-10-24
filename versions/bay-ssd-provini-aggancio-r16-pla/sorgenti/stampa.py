"""Piatto R16 di tre provini, slicing reale, supporti solo sulla spalla III."""
from pathlib import Path
import json,tempfile,zipfile,shutil,re,subprocess,plistlib,argparse
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from PIL import Image,ImageDraw
import genera as g
from native_3mf import export_plate,validate
from slicer_utils import run_cli,parse_gcode,screen_new_wall_islands,estimate_totals
from percorsi import draw_layer
ROOT=g.ROOT

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--solo-iii',action='store_true');args=ap.parse_args()
 mode='RAPIDO' if args.solo_iii else 'CONFRONTO'
 name='BAY_R16_01_PROVINO_III' if args.solo_iii else 'BAY_R16_02_CONFRONTO'
 man=json.loads((ROOT/'verifiche/manifest.json').read_text());geo=json.loads((ROOT/'verifiche/geometria.json').read_text())
 assert geo['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 assert man['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 meshes={p['name']:trimesh.load_mesh(ROOT/p['stl'],process=True) for p in man['parts']}
 items=[dict(part=p['name'],name=p['name'],xy=[60,65+i*30],support=(i==2)) for i,p in enumerate(man['parts'])]
 if args.solo_iii:items=[dict(part=man['parts'][2]['name'],name=man['parts'][2]['name'],xy=[60,65],support=True)]
 support_item=next(i for i in items if i['support'])
 source=ROOT/'sorgenti'/('PROVINO_III_R16_SORGENTE.3mf' if args.solo_iii else 'PROVINI_R16_SORGENTE.3mf');export_plate(source,items,meshes);source_check=validate(source,items)
 slicer=Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer')
 version=re.search(r'ElegooSlicer-([0-9.]+)',subprocess.run([str(slicer),'--help'],capture_output=True,text=True,check=True).stdout).group(1)
 app=plistlib.loads((slicer.parents[1]/'Info.plist').read_bytes())['CFBundleShortVersionString']
 machine,process,filament=[ROOT/'slicer'/n for n in ('machine.json','process.json','filament.json')]
 qa=ROOT/'verifiche/slicing'/mode;qa.mkdir(exist_ok=True);outpath=ROOT/'stampa/progetti_ElegooSlicer'/(name+'_ECC2_PLABASIC.3mf')
 with tempfile.TemporaryDirectory(prefix='bay-r16-provini-') as td:
  td=Path(td);out=td/'out';out.mkdir()
  cli=run_cli(slicer,['--datadir',str(td/'data'),'--load-settings',str(machine)+';'+str(process),'--load-filaments',str(filament),
   '--arrange','0','--orient','0','--slice','0','--export-3mf','PROVINI.3mf','--outputdir',str(out),str(source)],qa/'slicer.log')
  gcodes=list(out.glob('*.gcode'));assert len(gcodes)==1
  layers,analysis=parse_gcode(gcodes[0]);assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header']
  assert not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations']
  analysis['new_wall_islands']=screen_new_wall_islands(layers)
  assert analysis['new_wall_islands']['candidate_count']==0,analysis['new_wall_islands']
  native=out/'PROVINI.3mf';check=validate(native,items)
  with zipfile.ZipFile(native) as z:
   settings=json.loads(z.read('Metadata/project_settings.config'));config=ET.fromstring(z.read('Metadata/model_settings.config'))
   assert settings['filament_type']==['PLA'] and settings['nozzle_diameter']==['0.4'] and settings['curr_bed_type']=='Textured PEI Plate'
   assert settings['nozzle_temperature']==['220'] and settings['textured_plate_temp']==['60']
   assert settings['layer_height']=='0.2' and settings['wall_loops']=='4' and settings['filament_max_volumetric_speed']==['5']
   assert settings['enable_support']=='1' and settings['support_on_build_plate_only']=='0' and settings['support_remove_small_overhang']=='0'
   assert settings['support_style']=='snug' and settings['fuzzy_skin']=='disabled_fuzzy'
   object_support={next(e.get('value') for e in o.findall('metadata') if e.get('key')=='name'):
    next(e.get('value') for e in o.findall('metadata') if e.get('key')=='enable_support') for o in config.findall('object')}
   assert object_support=={i['name']:'1' if i['support'] else '0' for i in items},object_support
   warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')]
   assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings),warnings
   member=next(n for n in z.namelist() if n.endswith('.gcode'));assert __import__('hashlib').sha256(z.read(member)).hexdigest()==g.sha(gcodes[0])
  offset=[float(n) for n in settings['extruder_offset'][0].split('x')]
  supports=[]
  for layer in layers:
   for ax,ay,bx,by,role in layer['segments']:
    if 'support' in role.lower():
     assert support_item['xy'][1]-offset[1]-.8<=min(ay,by)<=max(ay,by)<=support_item['xy'][1]-offset[1]+14.8
     supports.append(dict(z=layer['z_mm'],xy=[ax,ay,bx,by],role=role))
  assert supports,'Mancano i supporti della spalla III'
  g.save(qa/'analisi.json',analysis)
  shutil.copy2(native,outpath)
 # Una tavola di tutti gli strati, piu dettagli dei due agganci e della spalla.
 b=analysis['extrusion_bounds_xy_mm'];frame=[b[0][0]-2,b[0][1]-2,b[1][0]+2,b[1][1]+2]
 n=len(layers);cols=10;size=160;im=Image.new('RGB',(cols*size,((n+cols-1)//cols)*size+30),'white');d=ImageDraw.Draw(im)
 d.text((10,8),f'R16 {mode} / tutti gli strati; supporti arancioni solo sul III',fill='#24323d')
 for k,layer in enumerate(layers):draw_layer(d,layer,((k%cols)*size,30+(k//cols)*size),size,frame)
 overview=qa/'TUTTI_STRATI.png';im.save(overview)
 images=[overview]
 for j,item in enumerate(items):
  for side in ('sinistra','destra'):
   im=Image.new('RGB',(1500,1035),'white');d=ImageDraw.Draw(im)
   d.text((10,8),f"{item['name']} / aletta {side}: pattino, dente, supporto e chiusura",fill='#24323d')
   x,y=np.array(item['xy'])-np.array(offset);a,b=(x-1,x+7) if side=='sinistra' else (x+83,x+91)
   for k,height in enumerate((11.8,12,12.2,12.4,12.8,14.8)):
    index=min(len(layers)-1,round(height/.2)-1);draw_layer(d,layers[index],((k%3)*500,30+(k//3)*500),500,[a,y-1,b,y+15])
   path=qa/f"{item['name']}_{side}.png";im.save(path);images.append(path)
 im=Image.new('RGB',(1500,1035),'white');d=ImageDraw.Draw(im)
 d.text((10,8),'R16 / primo strato e crescita delle alette dalla traversa',fill='#24323d')
 for k,index in enumerate((0,1,2,14,15,len(layers)-1)):draw_layer(d,layers[index],((k%3)*500,30+(k//3)*500),500,frame)
 path=qa/'PRIMI_STRATI_RADICI.png';im.save(path);images.append(path)
 job=dict(name=name,project=str(outpath.relative_to(ROOT)),project_sha256=g.sha(outpath),
  geometry_source=str(source.relative_to(ROOT)),geometry_sha256=g.sha(source),items=items,native_check=check,source_check=source_check,
  profile_hashes={p.name:g.sha(p) for p in (machine,process,filament)},layers=n,
  slicer_engine=version,slicer_app=app,slicer_estimates=analysis['slicer_estimates'],totals=estimate_totals([dict(slicer_estimates=analysis['slicer_estimates'])]),
  object_support=object_support,support_segments=len(supports),support_z_range_mm=[min(s['z'] for s in supports),max(s['z'] for s in supports)],
  warnings=warnings,warning_preparation='PLA con sportello anteriore aperto; soglia software originale conservata.',
  images=[str(p.relative_to(ROOT)) for p in images],visual_review_complete=False,cli=cli,sent_to_printer=False)
 g.save(qa/'job.json',job)
 print(json.dumps(dict(layers=n,estimate=analysis['slicer_estimates'],support_segments=len(supports),project=str(outpath))),flush=True)
if __name__=='__main__':main()
