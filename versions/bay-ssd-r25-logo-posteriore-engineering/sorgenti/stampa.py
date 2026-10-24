"""ElegooSlicer R25: tetto singolo e kit completo sul piatto R24."""
from pathlib import Path
import json,tempfile,zipfile,shutil,subprocess,re,plistlib,math
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from PIL import Image,ImageDraw
import genera as g
from native_3mf import export_plate,validate
from slicer_utils import run_cli,parse_gcode,screen_new_wall_islands,estimate_totals
from percorsi import draw_layer
ROOT=g.ROOT
def item(part,xy,**kw):return dict(part=part,name=part,xy=xy,support=False,**kw)
def definitions():
 roof=lambda xy:item('TETTO_R25_LOGO_ENGINEERING',xy,options={'wall_generator':'arachne'})
 return [('TETTO','BAY_R25_01_SOLO_TETTO_LOGO_ENGINEERING',[roof([60,60])]),
 ('COMPLETO','BAY_R25_02_KIT_COMPLETO_UNICO_PIATTO',[
 item('SCOCCA_R25',[12,20]),roof([122,20]),*[item('CARTUCCIA_'+m+'_R25',[20+42*i,150],walls=6) for i,m in enumerate(g.P['ssd_nominali'])],item('FERMO_CARTUCCE_R25',[148,150]),item('PERNO_R25_NASCOSTO',[220,150],solid=True)])]
def main():
 m=json.loads((ROOT/'verifiche/manifest.json').read_text());geo=json.loads((ROOT/'verifiche/geometria.json').read_text());assert geo['manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 meshes={p['name']:trimesh.load_mesh(ROOT/p['stl'],process=True) for p in m['parts']}
 exe=Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer');engine=re.search(r'ElegooSlicer-([0-9.]+)',subprocess.run([str(exe),'--help'],capture_output=True,text=True,check=True).stdout).group(1);app=plistlib.loads((exe.parents[1]/'Info.plist').read_bytes())['CFBundleShortVersionString']
 profiles=[ROOT/'slicer'/n for n in ['machine.json','process.json','filament.json']];jobs=[]
 for mode,name,items in definitions():
  print('SLICING',mode,flush=True);qa=ROOT/'verifiche/slicing'/mode;qa.mkdir(parents=True,exist_ok=True)
  source=ROOT/'sorgenti'/(name+'_SORGENTE.3mf');export_plate(source,items,meshes);source_check=validate(source,items)
  target=ROOT/'stampa/progetti_ElegooSlicer'/(name+'_ECC2_PLABASIC.3mf');gcode=ROOT/'stampa/GCODE'/(name+'_ECC2_PLABASIC.gcode')
  with tempfile.TemporaryDirectory(prefix='bay-r25-') as td:
   td=Path(td);out=td/'out';out.mkdir();cli=run_cli(exe,['--datadir',str(td/'data'),'--load-settings',str(profiles[0])+';'+str(profiles[1]),'--load-filaments',str(profiles[2]),'--arrange','0','--orient','0','--slice','0','--export-3mf','PIATTO.3mf','--outputdir',str(out),str(source)],qa/'slicer.log')
   gcodes=list(out.glob('*.gcode'));assert len(gcodes)==1
   layers,analysis=parse_gcode(gcodes[0]);assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations']
   analysis['new_wall_islands']=screen_new_wall_islands(layers);native=out/'PIATTO.3mf';check=validate(native,items)
   with zipfile.ZipFile(native) as z:
    settings=json.loads(z.read('Metadata/project_settings.config'));config=ET.fromstring(z.read('Metadata/model_settings.config'))
    expected=dict(printer_model='Elegoo Centauri Carbon 2',nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',filament_type=['PLA'],nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',wall_loops='4',sparse_infill_density='20%',sparse_infill_pattern='gyroid',filament_max_volumetric_speed=['5'],enable_support='0',fuzzy_skin='disabled_fuzzy',brim_width='5',bridge_speed='25')
    for k,v in expected.items():assert settings[k]==v,(k,settings[k],v)
    object_config={}
    for o in config.findall('object'):
     cfg={e.get('key'):e.get('value') for e in o.findall('metadata')};it=next(q for q in items if q['name']==cfg['name']);assert cfg['enable_support']=='0'
     for k,v in it.get('options',{}).items():assert cfg[k]==v
     if it.get('walls'):assert cfg['wall_loops']==str(it['walls'])
     if it.get('solid'):assert cfg['sparse_infill_density']=='100%'
     object_config[cfg['name']]=cfg
    warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')];assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings)
    member=next(n for n in z.namelist() if n.endswith('.gcode'));assert __import__('hashlib').sha256(z.read(member)).hexdigest()==g.sha(gcodes[0])
   assert not any('support' in role.lower() for l in layers for *_,role in l['segments'])
   shutil.copy2(native,target);shutil.copy2(gcodes[0],gcode);g.save(qa/'analisi.json',analysis)
  n=len(layers);b=np.array(analysis['extrusion_bounds_xy_mm']);frame=[*b[0]-2,*b[1]+2];images=[]
  for start in range(0,n,100):
   subset=layers[start:start+100];im=Image.new('RGB',(1600,math.ceil(len(subset)/10)*160+30),'white');d=ImageDraw.Draw(im);d.text((10,8),f'R25 {mode} / percorsi reali / strati {start+1}-{start+len(subset)}',fill='#24323d')
   for k,l in enumerate(subset):draw_layer(d,l,((k%10)*160,30+(k//10)*160),160,frame)
   p=qa/f'TUTTI_{start+1:03d}_{start+len(subset):03d}.png';im.save(p);images.append(str(p.relative_to(ROOT)))
  def sheet(name,title,ix,fr):
   im=Image.new('RGB',(1500,1035),'white');d=ImageDraw.Draw(im);d.text((10,8),title,fill='#24323d')
   for k,i in enumerate(ix):draw_layer(d,layers[max(0,min(i,n-1))],((k%3)*500,30+(k//3)*500),500,fr)
   p=qa/name;im.save(p);images.append(str(p.relative_to(ROOT)))
  sheet('PRIMO_INTERMEDI_ULTIMO.png','R25 / primo, secondo, intermedi e ultimo strato',[0,1,n//4,n//2,n-2,n-1],frame)
  roof=next(q for q in items if q['part'].startswith('TETTO_'));off=np.array([float(v) for v in settings['extruder_offset'][0].split('x')]);rx,ry=np.array(roof['xy'])-off
  sheet('GUIDE_E_PERNO_TETTO.png','R25 / guide e camera del fermo, tetto con Arachne',[15,33,39,53,58,63],[rx+2,ry+7,rx+15,ry+37.5])
  sheet('LOGO_PRIMI_STRATI.png','R25 / inizio logo sul retro; strati di S9 e ENGINEERING',[9,10,11,119,120,121],[rx+23,ry-1,rx+67,ry+2])
  if mode=='COMPLETO':
   for i,model in enumerate(g.P['ssd_nominali']):
    it=next(q for q in items if q['part']=='CARTUCCIA_'+model+'_R25');x,y=np.array(it['xy'])-off;k=round((g.P['ssd_nominali'][model]['altezza']+3.5)/.2)-1
    sheet('PONTI_'+model+'.png','R25 / cornici '+model,[k-1,k,k+1,k+2,k+3,k+4],[x-2,y+11,x+23,y+76])
  indexes=sorted({max(0,min(n-1,q['layer']-1+delta)) for q in analysis['longest_bridge_segments'] for delta in [-1,0,1]})
  for start in range(0,len(indexes),6):sheet(f'PONTI_LUNGHI_{start//6+1:02d}.png','R25 / linee ponte e strati adiacenti',indexes[start:start+6],frame)
  keep={Path(n).name for n in images}
  for stale in qa.glob('*.png'):
   if stale.name not in keep:stale.unlink()
  job=dict(mode=mode,name=name,items=items,project=str(target.relative_to(ROOT)),project_sha256=g.sha(target),gcode=str(gcode.relative_to(ROOT)),gcode_sha256=g.sha(gcode),geometry_source=str(source.relative_to(ROOT)),geometry_sha256=g.sha(source),source_check=source_check,native_check=check,profiles={p.name:g.sha(p) for p in profiles},object_config=object_config,images=images,layers=n,slicer_app=app,slicer_engine=engine,slicer_estimates=analysis['slicer_estimates'],totals=estimate_totals([dict(slicer_estimates=analysis['slicer_estimates'])]),warnings=warnings,cli=cli,visual_review_complete=False,sent_to_printer=False)
  g.save(qa/'job.json',job);jobs.append(job);print(json.dumps(dict(mode=mode,estimate=job['slicer_estimates'],island_candidates=analysis['new_wall_islands']['candidate_count'],images=len(images))),flush=True)
 g.save(ROOT/'verifiche/slicing/riepilogo.json',dict(jobs=jobs))
if __name__=='__main__':main()
