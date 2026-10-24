"""R19: slicing reale di un tetto completo in PLA BASIC, nessun invio macchina."""
from pathlib import Path
import json,tempfile,zipfile,shutil,re,subprocess,plistlib,hashlib,math
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
 name='BAY_R19_TETTO_COMPLETO_ALETTE_R18'
 man=json.loads((ROOT/'verifiche/manifest.json').read_text());geo=json.loads((ROOT/'verifiche/geometria.json').read_text())
 assert geo['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json') and man['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 meshes={p['name']:trimesh.load_mesh(ROOT/p['stl'],process=True) for p in man['parts']}
 items=[dict(part=man['parts'][0]['name'],name=man['parts'][0]['name'],xy=[65,65],support=True)]
 source=ROOT/'sorgenti/TETTO_R19_SORGENTE.3mf';export_plate(source,items,meshes);source_check=validate(source,items)
 slicer=Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer')
 version=re.search(r'ElegooSlicer-([0-9.]+)',subprocess.run([str(slicer),'--help'],capture_output=True,text=True,check=True).stdout).group(1)
 app=plistlib.loads((slicer.parents[1]/'Info.plist').read_bytes())['CFBundleShortVersionString']
 machine,process,filament=[ROOT/'slicer'/n for n in ('machine.json','process.json','filament.json')]
 qa=ROOT/'verifiche/slicing/TETTO';outpath=ROOT/'stampa/progetti_ElegooSlicer'/(name+'_ECC2_PLABASIC.3mf')
 with tempfile.TemporaryDirectory(prefix='bay-r19-tetto-') as td:
  td=Path(td);out=td/'out';out.mkdir()
  cli=run_cli(slicer,['--datadir',str(td/'data'),'--load-settings',str(machine)+';'+str(process),'--load-filaments',str(filament),
   '--arrange','0','--orient','0','--slice','0','--export-3mf','TETTO.3mf','--outputdir',str(out),str(source)],qa/'slicer.log')
  gcodes=list(out.glob('*.gcode'));assert len(gcodes)==1
  layers,analysis=parse_gcode(gcodes[0]);assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header']
  assert not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations']
  analysis['new_wall_islands']=screen_new_wall_islands(layers)
  assert analysis['new_wall_islands']['candidate_count']==0,analysis['new_wall_islands']
  native=out/'TETTO.3mf';check=validate(native,items)
  with zipfile.ZipFile(native) as z:
   settings=json.loads(z.read('Metadata/project_settings.config'));config=ET.fromstring(z.read('Metadata/model_settings.config'))
   assert settings['filament_type']==['PLA'] and settings['nozzle_diameter']==['0.4'] and settings['curr_bed_type']=='Textured PEI Plate'
   assert settings['nozzle_temperature']==['220'] and settings['textured_plate_temp']==['60'] and 'Centauri Carbon 2' in settings['printer_model']
   assert settings['layer_height']=='0.2' and settings['wall_loops']=='4' and settings['filament_max_volumetric_speed']==['5']
   assert settings['enable_support']=='1' and settings['support_on_build_plate_only']=='0' and settings['support_remove_small_overhang']=='0'
   assert settings['support_style']=='snug' and settings['fuzzy_skin']=='disabled_fuzzy'
   object_support={next(e.get('value') for e in o.findall('metadata') if e.get('key')=='name'):
    next(e.get('value') for e in o.findall('metadata') if e.get('key')=='enable_support') for o in config.findall('object')}
   assert object_support=={i['name']:'1' for i in items}
   warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')]
   assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings),warnings
   member=next(n for n in z.namelist() if n.endswith('.gcode'));assert hashlib.sha256(z.read(member)).hexdigest()==g.sha(gcodes[0])
  offset=[float(n) for n in settings['extruder_offset'][0].split('x')];x,y=np.array(items[0]['xy'])-np.array(offset)
  supports=[]
  for layer in layers:
   for ax,ay,bx,by,role in layer['segments']:
    if 'support' in role.lower():
     assert y-.8<=min(ay,by)<=max(ay,by)<=y+109.8
     assert max(ax,bx)<x+10 or min(ax,bx)>x+80,(ax,bx)
     supports.append(dict(z=layer['z_mm'],xy=[ax,ay,bx,by],role=role))
  assert supports,'Mancano i supporti dei braccetti'
  g.save(qa/'analisi.json',analysis);shutil.copy2(native,outpath)
 # Tavole dell'intero percorso, tutte da visionare.
 b=analysis['extrusion_bounds_xy_mm'];frame=[b[0][0]-2,b[0][1]-2,b[1][0]+2,b[1][1]+2];images=[];n=len(layers)
 for start in range(0,n,100):
  subset=layers[start:start+100];cols=10;size=160;im=Image.new('RGB',(cols*size,math.ceil(len(subset)/cols)*size+30),'white');d=ImageDraw.Draw(im)
  d.text((10,8),f'R19 tetto completo / strati {start+1}-{start+len(subset)}; supporti arancioni',fill='#24323d')
  for k,layer in enumerate(subset):draw_layer(d,layer,((k%cols)*size,30+(k//cols)*size),size,frame)
  path=qa/f'TUTTI_STRATI_{start+1:03d}_{start+len(subset):03d}.png';im.save(path);images.append(path)
 def sheet(name,title,indexes,fr):
  im=Image.new('RGB',(1500,1035),'white');d=ImageDraw.Draw(im);d.text((10,8),title,fill='#24323d')
  for k,index in enumerate(indexes):draw_layer(d,layers[index],((k%3)*500,30+(k//3)*500),500,fr)
  path=qa/name;im.save(path);images.append(path)
 for side,a,b in [('SINISTRA',x-1,x+10),('DESTRA',x+80,x+91)]:
  sheet(f'ALETTA_{side}.png',f'R19 aletta {side}: supporto, spalla e chiusura',[round(h/.2)-1 for h in (11.8,12,12.2,12.4,12.8,14.8)],[a,y+50,b,y+84])
 sheet('PRIMO_STRATO_TETTO_CODA.png','R19: primo strato, tetto, alette e coda posteriore',[0,1,14,15,74,n-1],frame)
 sheet('RADICI.png','R19: radici flessibili e uscita delle alette; tagli aperti',[0,1,5,13,14,15],[x-1,y+50,x+11,y+84])
 sheet('CODA_POSTERIORE.png','R19: crescita della coda posteriore, parete e guance',[round(h/.2)-1 for h in (3.2,10,15,20,28.8,29)],[x-1,y-1,x+91,y+9])
 indexes=set()
 for b in analysis['longest_bridge_segments']:
  for k in (-1,0,1):indexes.add(max(0,min(n-1,b['layer']-1+k)))
 for start in range(0,len(indexes),6):sheet(f'PONTI_{start//6+1:02d}.png','R19: ponti piu lunghi e strati adiacenti',sorted(indexes)[start:start+6],frame)
 job=dict(name=name,project=str(outpath.relative_to(ROOT)),project_sha256=g.sha(outpath),geometry_source=str(source.relative_to(ROOT)),geometry_sha256=g.sha(source),items=items,native_check=check,source_check=source_check,
  profile_hashes={p.name:g.sha(p) for p in (machine,process,filament)},layers=n,slicer_engine=version,slicer_app=app,slicer_estimates=analysis['slicer_estimates'],totals=estimate_totals([dict(slicer_estimates=analysis['slicer_estimates'])]),
  object_support=object_support,support_segments=len(supports),support_z_range_mm=[min(s['z'] for s in supports),max(s['z'] for s in supports)],warnings=warnings,
  warning_preparation='PLA con sportello anteriore aperto; soglia software originale conservata.',images=[str(p.relative_to(ROOT)) for p in images],visual_review_complete=False,cli=cli,sent_to_printer=False)
 g.save(qa/'job.json',job)
 print(json.dumps(dict(layers=n,estimate=analysis['slicer_estimates'],support_segments=len(supports),images=len(images),project=str(outpath))),flush=True)
if __name__=='__main__':main()
