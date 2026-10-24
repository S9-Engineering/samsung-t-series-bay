"""Riapre il 3MF nativo e verifica la selettivita della texture nei percorsi."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
import math

import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import contains_xy
from PIL import Image, ImageDraw, ImageFont

from prepara import ROOT, P, NS, PN, tag, save, sha
from slicer_utils import parse_gcode, ROLE_COLORS

def matrix(text):
    a=np.array([float(x) for x in text.split()]).reshape(4,3)
    m=np.eye(4);m[:3,:3]=a[:3].T;m[:3,3]=a[3]
    return m

def reopen_project(path):
    result=[];footprints=[]
    with zipfile.ZipFile(path) as z:
        root=ET.fromstring(z.read('3D/3dmodel.model'))
        assert root.get('unit')=='millimeter'
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        objects={o.get('id'):o for o in root.findall(tag('resources')+'/'+tag('object'))}
        for item in root.findall(tag('build')+'/'+tag('item')):
            oid=item.get('objectid');obj=objects[oid]
            config=cfg.find(f"object[@id='{oid}']")
            name=next(n.get('value') for n in config.findall('metadata') if n.get('key')=='name')
            for comp in obj.findall(tag('components')+'/'+tag('component')):
                pid=comp.get('objectid');part=config.find(f"part[@id='{pid}']")
                sub=ET.fromstring(z.read(comp.get('{'+PN+'}path').lstrip('/')))
                # Il file nativo puo contenere piu mesh: selezionare l'ID,
                # senza concatenare l'intero file per ciascun componente.
                body=sub.find(tag('resources')+'/'+tag('object')+f"[@id='{pid}']")
                assert body is not None
                v=np.array([[float(a.get(k)) for k in 'xyz'] for a in body.findall('.//'+tag('vertex'))])
                f=np.array([[int(a.get(k)) for k in ['v1','v2','v3']] for a in body.findall('.//'+tag('triangle'))])
                m=trimesh.Trimesh(v,f,process=True)
                identity='1 0 0 0 1 0 0 0 1 0 0 0'
                transform=matrix(item.get('transform',identity))@matrix(comp.get('transform',identity))
                assert abs(np.linalg.det(transform[:3,:3])-1)<1e-9
                m.apply_transform(transform)
                modifier=part.get('subtype')=='modifier_part'
                assert m.is_watertight and m.is_winding_consistent and m.volume>0
                assert len(m.split(only_watertight=False))==(2 if modifier else 1)
                if not modifier:
                    local=trimesh.load_mesh(ROOT/'stampa/STL'/f'{name}.stl',process=True)
                    assert np.max(np.abs(m.extents-local.extents))<.002
                    assert abs(m.volume-local.volume)<.01
                    expected=next((a for a in P['campioni'] if name=='provino_'+a['id']),None)
                    xy=expected['xy'] if expected else P['riferimento_PEI']['xy']
                    assert np.max(np.abs(m.bounds[0]-[*xy,0]))<.002
                    fp=box(m.bounds[0,0]-5,m.bounds[0,1]-5,m.bounds[1,0]+5,m.bounds[1,1]+5)
                    assert fp.within(box(0,0,256,256))
                    assert fp.intersection(box(246,0,256,20)).area==0
                    for previous in footprints:assert fp.intersection(previous).area==0
                    footprints.append(fp)
                result.append(dict(name=name,part_id=pid,role=part.get('subtype'),bounds_mm=m.bounds.tolist(),volume_mm3=float(m.volume),
                    components=2 if modifier else 1,mesh_closed=True,positive_volume=True,normals_consistent=True,rigid_transform=True))
        assert len(result)==8 and len(footprints)==5
    return dict(result='PASS',units='millimeter',printable_objects=5,modifiers=3,parts=result,brim_mm=5,
        method='Lettura XML indipendente per percorso e objectid, trasformazioni build e component composte; confronto con STL separati.',
        library_limitation='Il caricatore trimesh generico concatena le mesh nello stesso file nativo multipart: non usato per contare o approvare i corpi del 3MF.')

def glyph_polys():
    data=json.loads((ROOT/'sorgenti/logo_S9_contorni.json').read_text())
    width=P['logo']['larghezza_mm'];x=36-4-width;z=6
    return [Polygon([(x+u*width,z+v*width) for u,v in s['outer']],
        [[(x+u*width,z+v*width) for u,v in hole] for hole in s['holes']]) for s in data['shapes']]

def resample_front(layer,x):
    values=[]
    for x1,y1,x2,y2,role in layer['segments']:
        if role!='Outer wall' or max(y1,y2)>49.1 or min(y1,y2)<48.3:continue
        if min(x1,x2)<x+.7 or max(x1,x2)>x+35.3:continue
        n=max(2,math.ceil(abs(x2-x1)/.04))
        t=np.linspace(0,1,n)
        values.append(np.c_[x1+(x2-x1)*t-x,y1+(y2-y1)*t])
    return np.vstack(values) if values else np.empty((0,2))

def verify_texture(layers):
    glyphs=glyph_polys();safe=[g.buffer(-.20) for g in glyphs]
    rows=[];allstats=[]
    baseline=48.71 # y=50 + mezzo cordone esterno .21 - offset estrusore 1.5
    for c in P['campioni']:
        amp=c['ampiezza_mm'];x=c['xy'][0]
        logo=[[],[]];rough=[];rear=[];glyph_layers=[set(),set()]
        for layer in layers:
            zslice=layer['z_mm']-.1
            if not 3.6<=zslice<=30.8:continue
            # Segmenti lunghi del controllo liscio vengono campionati anch'essi.
            pts=[]
            for s in layer['segments']:
                x1,y1,x2,y2,role=s
                if role=='Outer wall' and max(y1,y2)<49.1 and min(y1,y2)>48.3 and min(x1,x2)>=x+.15 and max(x1,x2)<=x+35.85:
                    n=max(2,math.ceil(abs(x2-x1)/.04));t=np.linspace(0,1,n)
                    pts.append(np.c_[x1+(x2-x1)*t-x,y1+(y2-y1)*t])
                if role=='Outer wall' and min(y1,y2)>51.2 and max(y1,y2)<51.4 and x+1<(x1+x2)/2<x+35:
                    rear.extend([y1-51.29,y2-51.29])
            if not pts:continue
            pts=np.vstack(pts);xx,yy=pts[:,0],pts[:,1]
            inside_any=np.zeros(len(pts),bool)
            for i,g in enumerate(glyphs):
                inside_any|=contains_xy(g.buffer(.20),xx,np.full(len(xx),zslice))
                inside=contains_xy(safe[i],xx,np.full(len(xx),zslice))
                if inside.any():
                    logo[i].extend((yy[inside]-baseline).tolist());glyph_layers[i].add(layer['number'])
            outside=(xx>1.4)&(xx<34.6)&~inside_any
            rough.extend((yy[outside]-baseline).tolist())
        def stats(vals):
            a=np.asarray(vals)
            return dict(samples=len(vals),max_abs_mm=float(np.max(np.abs(a))),std_mm=float(a.std()))
        assert rough and all(logo)
        rr=stats(rough);ss=[stats(a) for a in logo]
        assert all(a['max_abs_mm']<.0011 for a in ss),(c['id'],ss)
        assert rear and max(abs(v) for v in rear)<.0011
        if amp:
            assert rr['max_abs_mm']>amp*.9 and rr['max_abs_mm']<=amp+.002
            assert rr['std_mm']>amp*.2
        else:assert rr['max_abs_mm']<.0011
        item=dict(id=c['id'],amplitude_mm=amp,point_distance_mm=c['distanza_punti_mm'],rough_background=rr,
            S_smooth=ss[0],nine_smooth=ss[1],glyph_layers=[len(s) for s in glyph_layers],rear_smooth=True)
        allstats.append(item)
    return dict(result='PASS',project_sha256=sha(next((ROOT/'stampa/progetti_ElegooSlicer').glob('*.3mf'))),
        method='Coordinate estruse reali, corrette per offset ugello Y=-1.5 mm; zone interne ai glifi erose 0.20 mm per escludere transizioni. Sezioni a Z-strato meno 0.10 mm.',
        baseline_front_path_y_mm=baseline,logo_nominal_relief_mm=0,parts=allstats,
        physical_gloss_verified=False,physical_texture_verified=False)

def verify_internal_bridges(layers):
    records=[]
    for index,layer in enumerate(layers):
        bridges=[s for s in layer['segments'] if 'bridge' in s[4].lower()]
        if not bridges:continue
        previous=unary_union([LineString([(s[0],s[1]),(s[2],s[3])]).buffer(.21,cap_style=2)
            for s in layers[index-1]['segments']])
        worst=0;full=0
        for s in bridges:
            line=LineString([(s[0],s[1]),(s[2],s[3])]);full=max(full,line.length)
            unsupported=line.difference(previous)
            spans=list(unsupported.geoms) if hasattr(unsupported,'geoms') else [unsupported]
            worst=max(worst,max((v.length for v in spans),default=0))
        assert worst<4.6
        records.append(dict(layer=layer['number'],z_mm=layer['z_mm'],max_full_bridge_segment_mm=full,
            max_uncovered_span_estimate_mm=worst))
    return dict(method='Sottrazione ai segmenti Internal Bridge della copertura dei percorsi dello strato precedente, cordone idealizzato largo .42 mm; nessuna simulazione di sag o adesione.',layers=records)

def font(size,bold=False):
    p=Path('/System/Library/Fonts/Supplemental')/('Arial Bold.ttf' if bold else 'Arial.ttf')
    return ImageFont.truetype(str(p),size) if p.exists() else ImageFont.load_default(size=size)

def render_all_layers(layers):
    files=[];folder=ROOT/'verifiche/slicing/anteprime';folder.mkdir(exist_ok=True)
    # Vista del piatto intero, tutti i 160 strati: cinque oggetti molto semplici.
    for start in range(0,len(layers),40):
        im=Image.new('RGB',(2000,2380),'white');d=ImageDraw.Draw(im)
        d.text((20,10),f'Percorsi reali - strati {start+1}-{min(start+40,len(layers))} / {len(layers)}',font=font(21,True),fill='#223344')
        for i,l in enumerate(layers[start:start+40]):
            ox=(i%4)*500;oy=48+(i//4)*232
            d.rectangle((ox+2,oy+2,ox+498,oy+230),outline='#c9ced5')
            d.text((ox+7,oy+5),f"{l['number']}   Z {l['z_mm']:.1f}",font=font(12),fill='#223344')
            scale=2.25
            for x1,y1,x2,y2,role in l['segments']:
                d.line((ox+8+(x1-25)*scale,oy+220-(y1-43)*scale,ox+8+(x2-25)*scale,oy+220-(y2-43)*scale),fill=ROLE_COLORS.get(role,'#778899'),width=1)
        name=folder/f'strati_{start+1:03d}_{min(start+40,len(layers)):03d}.png';im.save(name);files.append(str(name.relative_to(ROOT)))
    return files

def render_technical(layers):
    im=Image.new('RGB',(1800,1320),'#f3f4f6');d=ImageDraw.Draw(im)
    d.text((45,28),'S9 a filo: tre grane e un controllo liscio',font=font(38,True),fill='#19232f')
    d.text((45,83),'Schema delle zone di finitura, stesso PLA BASIC. La lucentezza reale richiede la stampa.',font=font(23),fill='#47576a')
    glyphs=glyph_polys()
    for i,c in enumerate(P['campioni']):
        x0=45+i*440;y0=155;scale=10
        d.rectangle((x0,y0,x0+360,y0+320),fill='#30343b',outline='#11151b',width=2)
        if c['ampiezza_mm']:
            # Trama schematica: visualizza dove si applica, non simula una foto.
            for x in range(12,350,5):
                for y in range(12,285,5):d.point((x0+x,y0+y),fill='#71767d')
            for g in glyphs:
                ext=[(x0+x*scale,y0+320-z*scale) for x,z in g.exterior.coords]
                d.polygon(ext,fill='#454a52')
                for ring in g.interiors:
                    points=[(x0+x*scale,y0+320-z*scale) for x,z in ring.coords]
                    d.polygon(points,fill='#30343b')
                    # Il vuoto del 9 appartiene al campo ruvido.
                    for x in range(12,350,5):
                        for y in range(12,285,5):
                            if Polygon(points).contains(Point(x0+x,y0+y)):d.point((x0+x,y0+y),fill='#71767d')
        title='00 - liscio' if not c['ampiezza_mm'] else f"0{i} - grana {c['ampiezza_mm']:.2f} mm"
        d.text((x0,y0+342),title,font=font(25,True),fill='#19232f')
        label=f"{c['tacche']} {'tacca' if c['tacche']==1 else 'tacche'} dietro | S9 14 mm"
        d.text((x0,y0+380),label if c['ampiezza_mm'] else 'Riferimento senza texture',font=font(20),fill='#47576a')
    d.text((45,610),'Sotto: percorsi reali del fronte a Z = 10 mm',font=font(28,True),fill='#19232f')
    d.text((45,654),'Deviazione ingrandita 250 volte in verticale. Nei tratti delle lettere il percorso resta liscio.',font=font(21),fill='#47576a')
    layer=layers[49]
    for i,c in enumerate(P['campioni']):
        y=745+i*112;xbase=c['xy'][0]
        d.text((45,y-30),c['id'],font=font(21,True),fill='#19232f')
        d.line((330,y,1730,y),fill='#bdc6d1',width=1)
        for x1,y1,x2,y2,role in layer['segments']:
            if role=='Outer wall' and max(y1,y2)<49.1 and min(y1,y2)>48.3 and min(x1,x2)>=xbase+.15 and max(x1,x2)<=xbase+35.85:
                d.line((330+(x1-xbase)*38,y-(y1-48.71)*250,330+(x2-xbase)*38,y-(y2-48.71)*250),fill=['#637181','#328477','#337bb7','#a76a32'][i],width=2)
    d.text((45,1235),'5 pezzi: 4 provini verticali 36 x 14 x 32 mm + riferimento PEI 36 x 24 x 3 mm.',font=font(22),fill='#19232f')
    d.text((45,1272),'Texture contenuta nel 3MF. Gli STL conservano soltanto le forme lisce nominali.',font=font(22),fill='#47576a')
    im.save(ROOT/'anteprime/01_PROVINI_S9_E_PERCORSI.png')

def render_details(layers):
    im=Image.new('RGB',(1800,1200),'white');d=ImageDraw.Draw(im)
    d.text((30,20),'Piatto e dettagli: primo strato, fine base, logo, ultimo strato',font=font(28,True),fill='#19232f')
    for i,index in enumerate([0,11,12,49,64,159]):
        layer=layers[index];ox=(i%2)*900;oy=80+(i//2)*360
        d.text((ox+20,oy),f"Strato {index+1} - Z {layer['z_mm']:.2f} mm",font=font(22,True),fill='#223344')
        for x1,y1,x2,y2,role in layer['segments']:
            d.line((ox+30+(x1-24)*3.5,oy+320-(y1-42)*3.5,ox+30+(x2-24)*3.5,oy+320-(y2-42)*3.5),fill=ROLE_COLORS.get(role,'#778899'),width=1)
    im.save(ROOT/'anteprime/02_PIATTO_PERCORSI.png')

def main():
    project=next((ROOT/'stampa/progetti_ElegooSlicer').glob('*.3mf'))
    result=reopen_project(project);result['project_sha256']=sha(project);save(ROOT/'verifiche/controllo_3mf.json',result)
    layers,analysis=parse_gcode(ROOT/'verifiche/slicing/percorsi_slicer.gcode')
    texture=verify_texture(layers);save(ROOT/'verifiche/texture_e_logo.json',texture)
    save(ROOT/'verifiche/ponti_interni.json',verify_internal_bridges(layers))
    sheets=render_all_layers(layers);render_technical(layers);render_details(layers)
    save(ROOT/'verifiche/revisione_visiva.json',dict(project_sha256=sha(project),all_layers=sheets,details=['anteprime/01_PROVINI_S9_E_PERCORSI.png','anteprime/02_PIATTO_PERCORSI.png'],
        reviewed=False,note='Generare tavole non equivale a esaminarle. Aggiornare dopo ispezione effettiva delle immagini.'))
    print(json.dumps(dict(geometry='PASS',texture='PASS',layers=len(layers),sheets=sheets),ensure_ascii=False))

if __name__=='__main__':main()
