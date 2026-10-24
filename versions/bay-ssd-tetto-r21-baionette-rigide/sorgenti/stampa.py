"""R21: due progetti nativi, prova e tetto, ciascuno con due perni rigidi."""
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
 man=json.loads((ROOT/'verifiche/manifest.json').read_text());geo=json.loads((ROOT/'verifiche/geometria.json').read_text())
 assert geo['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json') and man['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 meshes={p['name']:trimesh.load_mesh(ROOT/p['stl'],process=True) for p in man['parts']}
 slicer=Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer');version=re.search(r'ElegooSlicer-([0-9.]+)',subprocess.run([str(slicer),'--help'],capture_output=True,text=True,check=True).stdout).group(1);app=plistlib.loads((slicer.parents[1]/'Info.plist').read_bytes())['CFBundleShortVersionString']
 machine,process,filament=[ROOT/'slicer'/n for n in ('machine.json','process.json','filament.json')];jobs=[]
 for mode,part,name in [('PROVA','PROVINO_R21_BAIONETTA','BAY_R21_01_PROVA_AGGANCIO'),('TETTO','TETTO_R21_BAIONETTA','BAY_R21_02_TETTO_COMPLETO')]:
  items=[dict(part=part,name=part,xy=[65,65],support=False),*[dict(part='PERNO_R21_QUARTO_GIRO',name=f'PERNO_R21_{i+1}',xy=[170,70+26*i],support=False) for i in range(2)]]
  source=ROOT/'sorgenti'/(name+'_SORGENTE.3mf');export_plate(source,items,meshes);source_check=validate(source,items)
  qa=ROOT/'verifiche/slicing'/mode;outpath=ROOT/'stampa/progetti_ElegooSlicer'/(name+'_ECC2_PLABASIC.3mf')
  with tempfile.TemporaryDirectory(prefix='bay-r21-') as td:
   td=Path(td);out=td/'out';out.mkdir()
   cli=run_cli(slicer,['--datadir',str(td/'data'),'--load-settings',str(machine)+';'+str(process),'--load-filaments',str(filament),'--arrange','0','--orient','0','--slice','0','--export-3mf','PIATTO.3mf','--outputdir',str(out),str(source)],qa/'slicer.log')
   gcodes=list(out.glob('*.gcode'));assert len(gcodes)==1
   layers,analysis=parse_gcode(gcodes[0]);assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations']
   analysis['new_wall_islands']=screen_new_wall_islands(layers);assert analysis['new_wall_islands']['candidate_count']==0,analysis['new_wall_islands']
   native=out/'PIATTO.3mf';check=validate(native,items);assert check['printable_count']==3
   with zipfile.ZipFile(native) as z:
    settings=json.loads(z.read('Metadata/project_settings.config'));config=ET.fromstring(z.read('Metadata/model_settings.config'))
    assert settings['filament_type']==['PLA'] and settings['nozzle_diameter']==['0.4'] and settings['curr_bed_type']=='Textured PEI Plate' and settings['printer_model']=='Elegoo Centauri Carbon 2'
    assert settings['nozzle_temperature']==['220'] and settings['textured_plate_temp']==['60'] and settings['layer_height']=='0.2' and settings['wall_loops']=='4' and settings['filament_max_volumetric_speed']==['5']
    assert settings['enable_support']=='0' and settings['fuzzy_skin']=='disabled_fuzzy'
    object_support={next(e.get('value') for e in o.findall('metadata') if e.get('key')=='name'):next(e.get('value') for e in o.findall('metadata') if e.get('key')=='enable_support') for o in config.findall('object')};assert all(v=='0' for v in object_support.values())
    warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')];assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings),warnings
    member=next(n for n in z.namelist() if n.endswith('.gcode'));assert hashlib.sha256(z.read(member)).hexdigest()==g.sha(gcodes[0])
   assert not any('support' in role.lower() for l in layers for *_,role in l['segments'])
   g.save(qa/'analisi.json',analysis);shutil.copy2(native,outpath)
  offset=[float(n) for n in settings['extruder_offset'][0].split('x')];b=analysis['extrusion_bounds_xy_mm'];frame=[b[0][0]-2,b[0][1]-2,b[1][0]+2,b[1][1]+2];images=[];n=len(layers)
  for start in range(0,n,100):
   subset=layers[start:start+100];cols=10;size=160;im=Image.new('RGB',(cols*size,math.ceil(len(subset)/cols)*size+30),'white');d=ImageDraw.Draw(im);d.text((10,8),f'R21 {mode} / strati {start+1}-{start+len(subset)} / senza supporti',fill='#24323d')
   for k,layer in enumerate(subset):draw_layer(d,layer,((k%cols)*size,30+(k//cols)*size),size,frame)
   path=qa/f'TUTTI_{start+1:03d}_{start+len(subset):03d}.png';im.save(path);images.append(path)
  def sheet(filename,title,indexes,fr):
   im=Image.new('RGB',(1500,1035),'white');d=ImageDraw.Draw(im);d.text((10,8),title,fill='#24323d')
   for k,index in enumerate(indexes):draw_layer(d,layers[min(index,n-1)],((k%3)*500,30+(k//3)*500),500,fr)
   path=qa/filename;im.save(path);images.append(path)
  x,y=np.array(items[0]['xy'])-np.array(offset);base_y=109 if mode=='TETTO' else 61
  for side,xlo,xhi in [('SINISTRO',x+3,x+11),('DESTRO',x+79,x+87)]:
   sheet(f'SUPPORTO_RIGIDO_{side}.png',f'R21 {mode}: supporto rigido {side}, foro e ponte di chiusura',[round(h/.2)-1 for h in (11.8,12,13.4,14.8,15.2,15.4)],[xlo,y+base_y-57.5,xhi,y+base_y-43.5])
  kx,ky=np.array(items[1]['xy'])-np.array(offset);sheet('PERNO_INGRANDITO.png','R21: perno stampato piatto, gambo continuo e testa trasversale',[0,1,4,9,12,13],[kx-1,ky-1,kx+17,ky+10])
  sheet('PRIMO_INTERMEDI_ULTIMO.png',f'R21 {mode}: primo strato, tetto, fori e ultimo strato',[0,1,14,59,min(n-1,85),n-1],frame)
  indexes=set()
  for b in analysis['longest_bridge_segments']:
   for k in (-1,0,1):indexes.add(max(0,min(n-1,b['layer']-1+k)))
  for start in range(0,len(indexes),6):sheet(f'PONTI_{start//6+1:02d}.png','R21: ponti e strati adiacenti',sorted(indexes)[start:start+6],frame)
  keep={p.name for p in images}
  for stale in qa.glob('*.png'):
   if stale.name not in keep:stale.unlink()
  job=dict(mode=mode,name=name,project=str(outpath.relative_to(ROOT)),project_sha256=g.sha(outpath),geometry_source=str(source.relative_to(ROOT)),geometry_sha256=g.sha(source),items=items,native_check=check,source_check=source_check,profile_hashes={p.name:g.sha(p) for p in [machine,process,filament]},layers=n,slicer_app=app,slicer_engine=version,slicer_estimates=analysis['slicer_estimates'],totals=estimate_totals([dict(slicer_estimates=analysis['slicer_estimates'])]),supports=False,object_support=object_support,warnings=warnings,images=[str(p.relative_to(ROOT)) for p in images],visual_review_complete=False,sent_to_printer=False,cli=cli)
  g.save(qa/'job.json',job);jobs.append(job);print(json.dumps(dict(mode=mode,layers=n,estimate=job['slicer_estimates'],images=len(images))),flush=True)
 g.save(ROOT/'verifiche/slicing/riepilogo.json',dict(jobs=jobs,not_to_print_both_required=True,explanation='Prima il provino leggero; i due perni sono identici e riutilizzabili sul tetto completo.'))
if __name__=='__main__':main()
