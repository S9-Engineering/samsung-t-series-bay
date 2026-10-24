"""Presenza dei 13 glifi nei percorsi del retro, vista da +Y.

Il disegno e una proiezione approssimata dei cordoni: non una misura
della leggibilita o del risultato fisico.
"""
import json
import numpy as np
from shapely.geometry import LineString,box
from PIL import Image,ImageDraw
import genera as g
from slicer_utils import parse_gcode
ROOT=g.ROOT
def main():
 summary=json.loads((ROOT/'verifiche/slicing/riepilogo.json').read_text());glyphs=g.logo_shapes();bbs=[np.array(g.bounds(s)) for s in glyphs];p=g.P['logo_posteriore'];w=p['larghezza_mm'];zlo=min(b[0,2] for b in bbs);zhi=max(b[1,2] for b in bbs);xright=p['centro_x_mm']+w/2
 data=json.loads((ROOT/'sorgenti'/p['sorgente']).read_text());reports=[]
 for job in summary['jobs']:
  if job['mode']!='COMPLETO':continue
  roof=next(it for it in job['items'] if it['part']=='TETTO_R27_DOPPIO_PERNO');layers,_=parse_gcode(ROOT/job['gcode']);rx,ry=np.array(roof['xy'])-[0,1.5]
  roi=box(rx+28,ry-1,rx+62,ry+p['rilievo_mm']-.03);hits=[set() for _ in glyphs];segments=[]
  for layer in layers:
   z=86-layer['z_mm']
   if z<zlo-.2 or z>zhi+.2:continue
   for ax,ay,bx,by,role in layer['segments']:
    if min(ay,by)>ry+p['rilievo_mm']-.03 or max(ax,bx)<rx+28 or min(ax,bx)>rx+62:continue
    clip=LineString([(ax,ay),(bx,by)]).intersection(roi)
    if clip.is_empty:continue
    pieces=list(clip.geoms) if hasattr(clip,'geoms') else [clip]
    for q in pieces:
     if q.geom_type!='LineString' or q.length<1e-5:continue
     xx=[c[0]-rx for c in q.coords];low,high=min(xx),max(xx);segments.append((low,high,z))
     for i,b in enumerate(bbs):
      if b[0,2]-.11<=z<=b[1,2]+.11 and high+.11>=b[0,0] and low-.11<=b[1,0]:hits[i].add(layer['number'])
  assert all(len(s)>=5 for s in hits),[(i,len(s)) for i,s in enumerate(hits)]
  im=Image.new('RGB',(1500,660),'#f2f4f6');d=ImageDraw.Draw(im);scale=15.;origin=[(55,115),(815,115)]
  def point(x,z,org):return (org[0]+x*scale,org[1]+(zhi-z)*scale)
  d.text((35,20),'R27 / logo completo sul retro - CAD e proiezione dei percorsi reali',fill='#24323d');d.text((55,65),'Contorni approvati / 32 mm di larghezza',fill='#24323d');d.text((815,65),job['mode']+' / tutti i 13 glifi presenti',fill='#24323d')
  for q in data['shapes']:
   pts=[point(u*w,zlo+v*w,origin[0]) for u,v in q['outer']];d.polygon(pts,fill='#26343e')
   for hole in q['holes']:d.polygon([point(u*w,zlo+v*w,origin[0]) for u,v in hole],fill='#f2f4f6')
  for low,high,z in segments:
   a=point(xright-high,z+.1,origin[1]);b=point(xright-low,z-.1,origin[1]);d.rectangle([a[0]-1,a[1],b[0]+1,b[1]],fill='#3f667c')
  d.text((35,565),'Proiezione dei centri dei cordoni fuori dalla faccia originale; spessore verticale 0,2 mm approssimato.',fill='#65737c')
  d.text((35,600),'Conferma della presenza nel G-code; finitura e leggibilita reali non ancora provate.',fill='#65737c')
  path=ROOT/'verifiche/slicing'/job['mode']/'LOGO_PERCORSI.png';im.save(path)
  if str(path.relative_to(ROOT)) not in job['images']:job['images'].append(str(path.relative_to(ROOT)))
  report=dict(result='PASS_13_GLIFI_PRESENTI',source_gcode_sha256=job['gcode_sha256'],glyphs=[dict(index=i,layers=len(h),first_layer=min(h),last_layer=max(h)) for i,h in enumerate(hits)],projection_segments=len(segments),physical_readability_test=False)
  g.save(ROOT/'verifiche/slicing'/job['mode']/'logo.json',report);g.save(ROOT/'verifiche/slicing'/job['mode']/'job.json',job);reports.append(dict(mode=job['mode'],**report))
 g.save(ROOT/'verifiche/logo_percorsi.json',dict(reports=reports));g.save(ROOT/'verifiche/slicing/riepilogo.json',summary);print('PASS: 13 glifi presenti nel G-code completo R27',flush=True)
if __name__=='__main__':main()
