"""Screening campate sotto basamento dai percorsi realmente generati.

Approssima ogni cordone precedente con buffer r=.21 mm. Non e una
simulazione della deposizione: serve a leggere le linee Bridge lunghe
che attraversano piu appoggi. Lo spessore reale dipende dal flusso.
"""
import json,re,math
from shapely.geometry import LineString,box
from shapely.ops import unary_union
from PIL import Image,ImageDraw
import genera as g
from slicer_utils import parse_gcode
ROOT=g.ROOT
def check_frame_bridges(job):
 targets=[]
 for i,model in enumerate(g.P['ssd_nominali']):
  it=next(it for it in job['items'] if it['part']=='CARTUCCIA_'+model+'_R24');x,y=it['xy'];w=g.dims(model)['spessore']+.4
  for band in [0,1]:targets.append(dict(model=model,band=band+1,cx=x+10.4,y0=y-1.5+[13.7,61.7][band],y1=y-1.5+[25.7,73.7][band],minimum_x_span=w-.6,z0=g.dims(model)['altezza']+3.5,moves=[]))
 xyz=[0.,0.,0.];feed=0.;role=''
 for raw in (ROOT/job['gcode']).open():
  if raw.startswith(';TYPE:'):role=raw.strip()[6:]
  if not raw.startswith(('G0 ','G1 ')):continue
  p={k:float(v) for k,v in re.findall(r'([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))',raw)};new=[p.get(k,v) for k,v in zip('XYZ',xyz)];feed=p.get('F',feed)
  if p.get('E',0)>0 and ('bridge' in role.lower() or role=='Overhang wall'):
   for t in targets:
    if t['z0']<=new[2]<=t['z0']+.8 and t['y0']-.1<=min(xyz[1],new[1]) and max(xyz[1],new[1])<=t['y1']+.1 and min(xyz[0],new[0])<t['cx']<max(xyz[0],new[0]) and abs(new[0]-xyz[0])>t['minimum_x_span']:
     t['moves'].append(dict(z_mm=new[2],role=role,speed_mm_s=feed/60,x_span_mm=abs(new[0]-xyz[0])))
  xyz=new
 for t in targets:
  assert t['moves'],t
  assert max(q['speed_mm_s'] for q in t['moves'])<=25.01,t
  t['first_z_mm']=min(q['z_mm'] for q in t['moves']);t['max_bridge_speed_mm_s']=max(q['speed_mm_s'] for q in t['moves'])
 g.save(ROOT/'verifiche/slicing/COMPLETO/cornici_ponti_gcode.json',dict(result='PASS',source_gcode_sha256=job['gcode_sha256'],cornici=targets,meaning='Passaggi trasversali delle prime chiusure riconosciuti come ponte/sbalzo nello slicer; non prova della stampa reale.'))
def main():
 job=json.loads((ROOT/'verifiche/slicing/COMPLETO/job.json').read_text());check_frame_bridges(job);layers,_=parse_gcode(ROOT/job['gcode']);index=25
 current=layers[index];previous=layers[index-1]
 assert abs(current['z_mm']-5.2)<.001 and abs(previous['z_mm']-5)<.001
 # La scocca occupa X12..102, Y18.5..120. Solo questo pezzo.
 roi=box(11.5,18,102.5,121)
 paths=[LineString([s[:2],s[2:4]]) for s in previous['segments'] if roi.intersects(LineString([s[:2],s[2:4]]))]
 support=unary_union([line.buffer(.21,cap_style=2) for line in paths]);rows=[]
 for s in current['segments']:
  if 'bridge' not in s[4].lower():continue
  line=LineString([s[:2],s[2:4]])
  if not roi.covers(line):continue
  free=line.difference(support);pieces=list(free.geoms) if hasattr(free,'geoms') else [free]
  spans=[q.length for q in pieces if not q.is_empty];rows.append(dict(role=s[4],endpoints_xy_mm=[list(s[:2]),list(s[2:4])],line_length_mm=line.length,max_approx_free_span_mm=max(spans,default=0)))
 assert rows
 rows.sort(key=lambda x:x['max_approx_free_span_mm'],reverse=True)
 maximum=rows[0]['max_approx_free_span_mm'];assert maximum<15,(maximum,rows[:3])
 # Ingrandimento con strato precedente in azzurro e nuovi ponti in rosso.
 im=Image.new('RGB',(1500,1050),'white');d=ImageDraw.Draw(im);scale=9.;x0,y0=10,17
 def pt(x,y):return (35+(x-x0)*scale,1010-(y-y0)*scale)
 for s in previous['segments']:
  line=LineString([s[:2],s[2:4]])
  if not roi.intersects(line):continue
  d.line((*pt(*s[:2]),*pt(*s[2:4])),fill='#9ac7da',width=3)
 for r in rows:
  a,b=r['endpoints_xy_mm'];d.line((*pt(*a),*pt(*b)),fill='#b63b2b',width=1)
 d.text((35,12),f"R24 / basamento Z5.2 sopra Z5.0 / campata libera approssimata max {maximum:.2f} mm",fill='#24323d')
 path=ROOT/'verifiche/slicing/COMPLETO/CAMPATE_BASAMENTO.png';im.save(path)
 data=dict(result='PASS_SCREENING_CAMPATE_BASAMENTO',source_gcode_sha256=job['gcode_sha256'],current_layer=26,previous_layer=25,current_z_mm=5.2,previous_z_mm=5,bead_approx_radius_mm=.21,max_approx_free_span_mm=maximum,checked_bridge_segments=len(rows),longest_free_spans=rows[:20],image=str(path.relative_to(ROOT)),limitations=['Approssimazione geometrica dai cordoni precedenti, non prova di bridging fisico.','Una linea Bridge lunga attraversa piu appoggi; la lunghezza intera non e una campata unica.'])
 g.save(ROOT/'verifiche/slicing/COMPLETO/campate_basamento.json',data)
 if str(path.relative_to(ROOT)) not in job['images']:job['images'].append(str(path.relative_to(ROOT)))
 g.save(ROOT/'verifiche/slicing/COMPLETO/job.json',job)
 summary=json.loads((ROOT/'verifiche/slicing/riepilogo.json').read_text());summary['jobs']=[job if j['mode']=='COMPLETO' else j for j in summary['jobs']];g.save(ROOT/'verifiche/slicing/riepilogo.json',summary)
 print(json.dumps(dict(max_free_span_mm=maximum,bridge_segments=len(rows))),flush=True)
if __name__=='__main__':main()
