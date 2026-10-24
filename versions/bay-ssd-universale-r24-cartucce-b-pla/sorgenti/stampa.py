"""Tre progetti nativi R24: provino interni, provino tetto, kit su un piatto."""
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
def item(p,xy,**kw):return dict(part=p,name=p,xy=xy,support=False,**kw)
def definitions():return [
 ('INTERNI','BAY_R24_01_PROVINO_INTERNI',[
 item('PROVINO_BASE_R24',[25,20]),item('PROVINO_PIEDE_R24',[80,20],walls=6),item('PROVINO_FERMO_R24',[130,20]),
 *[item('PROVINO_CORNICE_'+m+'_R24',[30+60*i,145],walls=6) for i,m in enumerate(g.P['ssd_nominali'])]]),
 ('TETTO','BAY_R24_02_PROVINO_TETTO',[
 item('PROVINO_GUIDE_SCOCCA_R24',[25,30]),item('PROVINO_GUIDE_TETTO_R24',[135,30]),item('PERNO_R24_NASCOSTO',[45,100],solid=True)]),
 ('COMPLETO','BAY_R24_03_KIT_COMPLETO_UNICO_PIATTO',[
 item('SCOCCA_R24',[12,20]),item('TETTO_R24_SCORREVOLE',[122,20]),
 *[item('CARTUCCIA_'+m+'_R24',[20+42*i,150],walls=6) for i,m in enumerate(g.P['ssd_nominali'])],
 item('FERMO_CARTUCCE_R24',[148,150]),item('PERNO_R24_NASCOSTO',[220,150],solid=True)])]
def main():
 man=json.loads((ROOT/'verifiche/manifest.json').read_text());geo=json.loads((ROOT/'verifiche/geometria.json').read_text())
 assert geo['source_manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json') and man['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 meshes={p['name']:trimesh.load_mesh(ROOT/p['stl'],process=True) for p in man['parts']}
 slicer=Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer');version=re.search(r'ElegooSlicer-([0-9.]+)',subprocess.run([str(slicer),'--help'],capture_output=True,text=True,check=True).stdout).group(1);app=plistlib.loads((slicer.parents[1]/'Info.plist').read_bytes())['CFBundleShortVersionString']
 machine,process,filament=[ROOT/'slicer'/n for n in ('machine.json','process.json','filament.json')];jobs=[]
 for mode,name,items in definitions():
  print('SLICING',mode,flush=True)
  source=ROOT/'sorgenti'/(name+'_SORGENTE.3mf');export_plate(source,items,meshes);source_check=validate(source,items)
  qa=ROOT/'verifiche/slicing'/mode;qa.mkdir(parents=True,exist_ok=True);outpath=ROOT/'stampa/progetti_ElegooSlicer'/(name+'_ECC2_PLABASIC.3mf');gcpath=ROOT/'stampa/GCODE'/(name+'_ECC2_PLABASIC.gcode')
  with tempfile.TemporaryDirectory(prefix='bay-r24-') as td:
   td=Path(td);out=td/'out';out.mkdir()
   cli=run_cli(slicer,['--datadir',str(td/'data'),'--load-settings',str(machine)+';'+str(process),'--load-filaments',str(filament),'--arrange','0','--orient','0','--slice','0','--export-3mf','PIATTO.3mf','--outputdir',str(out),str(source)],qa/'slicer.log')
   gcodes=list(out.glob('*.gcode'));assert len(gcodes)==1
   layers,analysis=parse_gcode(gcodes[0]);assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header'] and not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations']
   analysis['new_wall_islands']=screen_new_wall_islands(layers)
   native=out/'PIATTO.3mf';check=validate(native,items);assert check['printable_count']==len(items)
   with zipfile.ZipFile(native) as z:
    settings=json.loads(z.read('Metadata/project_settings.config'));config=ET.fromstring(z.read('Metadata/model_settings.config'))
    expected=dict(filament_type=['PLA'],nozzle_diameter=['0.4'],curr_bed_type='Textured PEI Plate',printer_model='Elegoo Centauri Carbon 2',nozzle_temperature=['220'],textured_plate_temp=['60'],layer_height='0.2',wall_loops='4',filament_max_volumetric_speed=['5'],enable_support='0',fuzzy_skin='disabled_fuzzy',sparse_infill_density='20%',bridge_speed='25')
    for k,v in expected.items():assert settings[k]==v,(k,settings[k],v)
    object_cfg={}
    for o in config.findall('object'):
     cfg={e.get('key'):e.get('value') for e in o.findall('metadata')};it=next(i for i in items if i['name']==cfg['name']);assert cfg['enable_support']=='0'
     if it.get('solid'):assert cfg['sparse_infill_density']=='100%'
     if it.get('walls'):assert cfg['wall_loops']==str(it['walls'])
     object_cfg[cfg['name']]=cfg
    warnings=[dict(e.attrib) for e in ET.fromstring(z.read('Metadata/slice_info.config')).iter('warning')];assert all(w['msg']=='bed_temperature_too_high_than_filament' for w in warnings),warnings
    member=next(n for n in z.namelist() if n.endswith('.gcode'));assert hashlib.sha256(z.read(member)).hexdigest()==g.sha(gcodes[0])
   assert not any('support' in role.lower() for l in layers for *_,role in l['segments'])
   g.save(qa/'analisi.json',analysis);shutil.copy2(native,outpath);shutil.copy2(gcodes[0],gcpath)
  b=analysis['extrusion_bounds_xy_mm'];frame=[b[0][0]-2,b[0][1]-2,b[1][0]+2,b[1][1]+2];images=[];n=len(layers)
  for start in range(0,n,100):
   subset=layers[start:start+100];cols=10;size=160;im=Image.new('RGB',(cols*size,math.ceil(len(subset)/cols)*size+30),'white');d=ImageDraw.Draw(im);d.text((10,8),f'R24 {mode} / strati {start+1}-{start+len(subset)} / percorsi reali, senza supporti',fill='#24323d')
   for k,layer in enumerate(subset):draw_layer(d,layer,((k%cols)*size,30+(k//cols)*size),size,frame)
   path=qa/f'TUTTI_{start+1:03d}_{start+len(subset):03d}.png';im.save(path);images.append(path)
  def sheet(filename,title,indexes,fr):
   im=Image.new('RGB',(1500,1035),'white');d=ImageDraw.Draw(im);d.text((10,8),title,fill='#24323d')
   for k,index in enumerate(indexes[:6]):draw_layer(d,layers[max(0,min(index,n-1))],((k%3)*500,30+(k//3)*500),500,fr)
   path=qa/filename;im.save(path);images.append(path)
  sheet('PRIMO_INTERMEDI_ULTIMO.png',f'R24 {mode}: primo, secondo, intermedi e ultimo strato',[0,1,n//4,n//2,n-2,n-1],frame)
  # Ingrandimenti delle cornici: prima, durante e dopo il ponte superiore.
  offset=np.array([float(x) for x in settings['extruder_offset'][0].split('x')])
  for it in items:
   if 'CORNICE_' in it['part'] or it['part'].startswith('CARTUCCIA_'):
    model=next(m for m in sorted(g.P['ssd_nominali'],key=len,reverse=True) if m in it['part']);height=g.dims(model)['altezza']+3+.5
    k=round(height/.2)-1;x,y=np.array(it['xy'])-offset;bb=np.array(it['bounds_mm']);w,dep=(bb[1]-bb[0])[:2]
    fr=[x-2,y+11,x+w+2,y+28] if it['part'].startswith('CARTUCCIA_') else [x-2,y-2,x+w+2,y+dep+2]
    sheet('PONTE_'+model+'.png','R24 '+model+': cornice e ponte superiore, strati adiacenti',[k-3,k-2,k-1,k,k+1,k+2],fr)
    if it['part'].startswith('CARTUCCIA_'):sheet('PONTE_POSTERIORE_'+model+'.png','R24 '+model+': seconda cornice e ponte superiore',[k-3,k-2,k-1,k,k+1,k+2],[x-2,y+59,x+w+2,y+76])
  # Guide interne basse e intagli: tutti i particolari alla loro quota.
  if mode in ['INTERNI','COMPLETO']:
   it=items[0];x,y=np.array(it['xy'])-offset;zbase=2 if mode=='INTERNI' else 0;xb=6 if mode=='INTERNI' else 0;yb=0 if mode=='INTERNI' else -.4
   sheet('GUIDE_PIEDE.png','R24: crescita a 45 gradi delle guide basse',[round((h-zbase)/.2)-1 for h in [10,11.4,11.6,12.4,13.2,15.6]],[x+8-xb,y+49-yb,x+14-xb,y+58-yb])
  if mode in ['TETTO','COMPLETO']:
   ri=items[1];rx,ry=np.array(ri['xy'])-offset
   sheet('GUIDA_TETTO.png','R24: guida del tetto invariata R22',[14,15,33,39,58,63],[rx+2,ry+25,rx+13,ry+37])
   sheet('CAMERA_FERMO.png','R24: ponte breve della camera e sede perno',[33,34,52,53,54,57],[rx+2,ry+7,rx+15,ry+22])
   ki=next(i for i in items if i['part']=='PERNO_R24_NASCOSTO');kx,ky=np.array(ki['xy'])-offset
   sheet('PERNO.png','R24: perno stampato piatto',[0,1,4,9,14,16],[kx-1,ky-1,kx+9,ky+28])
  indexes=set()
  for b in analysis['longest_bridge_segments']:
   for k in [-1,0,1]:indexes.add(max(0,min(n-1,b['layer']-1+k)))
  indexes=sorted(indexes)
  for start in range(0,len(indexes),6):sheet(f'PONTI_{start//6+1:02d}.png','R24: ponti e strati adiacenti',indexes[start:start+6],frame)
  keep={p.name for p in images}
  for stale in qa.glob('*.png'):
   if stale.name not in keep:stale.unlink()
  job=dict(mode=mode,name=name,project=str(outpath.relative_to(ROOT)),project_sha256=g.sha(outpath),gcode=str(gcpath.relative_to(ROOT)),gcode_sha256=g.sha(gcpath),geometry_source=str(source.relative_to(ROOT)),geometry_sha256=g.sha(source),items=items,native_check=check,source_check=source_check,profile_hashes={p.name:g.sha(p) for p in [machine,process,filament]},layers=n,slicer_app=app,slicer_engine=version,slicer_estimates=analysis['slicer_estimates'],totals=estimate_totals([dict(slicer_estimates=analysis['slicer_estimates'])]),supports=False,object_config=object_cfg,warnings=warnings,images=[str(p.relative_to(ROOT)) for p in images],visual_review_complete=False,sent_to_printer=False,cli=cli)
  g.save(qa/'job.json',job);jobs.append(job);print(json.dumps(dict(mode=mode,layers=n,estimate=job['slicer_estimates'],images=len(images),island_candidates=analysis['new_wall_islands']['candidate_count'])),flush=True)
 g.save(ROOT/'verifiche/slicing/riepilogo.json',dict(jobs=jobs,explanation='Prima il provino interno. Provino tetto solo se la chiusura R22 non e ancora stata verificata fisicamente. Kit completo: sette pezzi in un piatto. Nessuna stampa inviata.'))
if __name__=='__main__':main()
