"""Provini Fuzzy Skin e S9 a filo. Non modifica il bay e non avvia stampe."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
import xml.etree.ElementTree as ET

import cadquery as cq
import numpy as np
import trimesh

from slicer_utils import run_cli, parse_gcode, screen_new_wall_islands, estimate_totals
from verifica_intersezioni_mesh import self_intersections_fast

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT/'sorgenti/parametri.json').read_text())
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PN = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
ET.register_namespace('', NS)
ET.register_namespace('p', PN)
def tag(s): return '{'+NS+'}'+s
def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def box(x,y,z,w,d,h): return cq.Solid.makeBox(w,d,h,cq.Vector(x,y,z))
def mesh(shape):
    v,f=shape.tessellate(.02,.06)
    return trimesh.Trimesh(np.array([p.toTuple() for p in v]),np.array(f),process=True)

def logo_shapes():
    data=json.loads((ROOT/'sorgenti'/P['logo']['sorgente']).read_text())
    width=P['logo']['larghezza_mm']
    x=P['dimensioni_provino_mm'][0]-P['logo']['margine_destro_mm']-width
    z=P['logo']['margine_inferiore_mm']
    def wire(points):
        return cq.Wire.makePolygon([cq.Vector(x+u*width,-1,z+v*width) for u,v in points],close=True)
    return [cq.Solid.extrudeLinear(wire(s['outer']),[wire(h) for h in s['holes']],cq.Vector(0,3,0)) for s in data['shapes']]

def generate():
    w,d,h=P['dimensioni_provino_mm'];t=P['spessore_base_mm']
    base=box(0,0,0,w,d,t).fuse(box(0,0,0,w,P['spessore_parete_mm'],h)).clean()
    glyphs=logo_shapes()
    q=P['campo_fuzzy_mm']
    mask=box(q['x'][0],q['y'][0],q['z'][0],q['x'][1]-q['x'][0],q['y'][1]-q['y'][0],q['z'][1]-q['z'][0]).cut(*glyphs).clean()
    records=[];bodies={}
    for c in P['campioni']:
        shape=base
        for i in range(c['tacche']):
            shape=shape.cut(box(3+i*3,d-1.2,-.1,1.6,1.4,t+.2)).clean()
        name='provino_'+c['id'];bodies[name]=shape
        records.append(dict(name=name,shape=shape,xy=c['xy'],amplitude=c['ampiezza_mm'],point_distance=c['distanza_punti_mm'],notches=c['tacche']))
    r=P['riferimento_PEI'];shape=box(0,0,0,*r['dimensioni_mm']);name='riferimento_PEI'
    bodies[name]=shape
    records.append(dict(name=name,shape=shape,xy=r['xy'],amplitude=0,point_distance=.25,notches=None))
    checks=[]
    for name,shape in list(bodies.items())+[('MASCHERA_NON_STAMPABILE_FUZZY',mask)]:
        assert shape.isValid(),name
        m=mesh(shape)
        expected=2 if name.startswith('MASCHERA') else 1
        assert len(shape.Solids())==expected,(name,len(shape.Solids()))
        if name.startswith('MASCHERA'):
            step=ROOT/'CAD'/f'{name}.step'
            cq.exporters.export(shape,str(step))
        else:
            step=ROOT/'CAD'/f'{name}.step';stl=ROOT/'stampa/STL'/f'{name}.stl'
            cq.exporters.export(shape,str(step));m.export(stl)
            m=trimesh.load_mesh(stl,process=True)
        reopened=cq.importers.importStep(str(step)).val()
        assert reopened.isValid() and len(reopened.Solids())==expected
        assert m.is_watertight and m.is_winding_consistent and m.volume>0
        assert len(m.split(only_watertight=False))==expected
        assert bool(np.all(m.area_faces>1e-10))
        assert len(np.unique(np.sort(m.faces,axis=1),axis=0))==len(m.faces)
        intersections=self_intersections_fast(m)
        assert intersections['intersection_pairs']==0,(name,intersections)
        checks.append(dict(name=name,bounds_mm=m.bounds.tolist(),volume_mm3=float(m.volume),components=expected,
            closed=True,normals_consistent=True,positive_volume=True,degenerate_faces=0,duplicate_faces=0,
            self_intersections=intersections,step_reopened=True,printable=not name.startswith('MASCHERA')))
    # Il logo non cambia il solido del pannello: e un foro nella sola maschera.
    assert all(abs(s.BoundingBox().ymin)<1e-5 for s in bodies.values())
    for c in records:
        if c['name']!='riferimento_PEI':assert abs(c['shape'].Volume()-base.Volume()+((c['notches'] or 0)*1.6*1.2*t))<1e-5
    save(ROOT/'verifiche/geometria.json',dict(result='PASS',units='mm',parts=checks,
        mask_components_intentional='Campo principale e isola interna al 9: due volumi modificatori, nessun materiale aggiunto.',
        relief_mm=0,nominal_front_y_mm=0,texture_only_in_slicer=True,physical_verified=False))
    write_project(records,mask)
    return records

def write_project(records,mask):
    root=ET.Element(tag('model'),unit='millimeter',attrib={'{http://www.w3.org/XML/1998/namespace}lang':'it-IT','requiredextensions':'p'})
    for name,value in [('Application','ElegooSlicer-1.5.3.5'),('OrcaSlicer','2.4.2'),('BambuStudio:3mfVersion','1'),('Title','PROVINI FUZZY S9 R02')]:
        ET.SubElement(root,tag('metadata'),name=name).text=value
    resources=ET.SubElement(root,tag('resources'));build=ET.SubElement(root,tag('build'))
    config=ET.Element('config');idx=0;placements=[];part_files={}
    def add_mesh(shape):
        nonlocal idx
        idx+=1
        partroot=ET.Element(tag('model'),unit='millimeter')
        rr=ET.SubElement(partroot,tag('resources'))
        obj=ET.SubElement(rr,tag('object'),id=str(idx),type='model')
        m=mesh(shape);mm=ET.SubElement(obj,tag('mesh'));vs=ET.SubElement(mm,tag('vertices'));ts=ET.SubElement(mm,tag('triangles'))
        for v in m.vertices:ET.SubElement(vs,tag('vertex'),attrib={a:f'{x:.8f}' for a,x in zip('xyz',v)})
        for f in m.faces:ET.SubElement(ts,tag('triangle'),attrib={f'v{i+1}':str(int(v)) for i,v in enumerate(f)})
        ET.SubElement(partroot,tag('build'))
        part_files[f'3D/Objects/part_{idx}.model']=ET.tostring(partroot,encoding='utf-8',xml_declaration=True)
        return idx
    for item in records:
        body_id=add_mesh(item['shape'])
        mask_id=add_mesh(mask) if item['amplitude'] else None
        idx+=1;object_id=idx
        obj=ET.SubElement(resources,tag('object'),id=str(object_id),type='model',name=item['name'])
        comps=ET.SubElement(obj,tag('components'))
        ET.SubElement(comps,tag('component'),objectid=str(body_id),attrib={'{'+PN+'}path':f'/3D/Objects/part_{body_id}.model'})
        if mask_id:ET.SubElement(comps,tag('component'),objectid=str(mask_id),attrib={'{'+PN+'}path':f'/3D/Objects/part_{mask_id}.model'})
        xy=item['xy'];ET.SubElement(build,tag('item'),objectid=str(object_id),transform=f'1 0 0 0 1 0 0 0 1 {xy[0]} {xy[1]} 0')
        co=ET.SubElement(config,'object',id=str(object_id))
        for key,value in dict(name=item['name'],extruder='1',fuzzy_skin='disabled_fuzzy').items():ET.SubElement(co,'metadata',key=key,value=value)
        part=ET.SubElement(co,'part',id=str(body_id),subtype='normal_part')
        ET.SubElement(part,'metadata',key='name',value=item['name'])
        if mask_id:
            part=ET.SubElement(co,'part',id=str(mask_id),subtype='modifier_part')
            settings=dict(name='Solo fronte ruvido, S9 liscio a filo',extruder='0',fuzzy_skin='external',
                fuzzy_skin_thickness=str(item['amplitude']),fuzzy_skin_point_distance=str(item['point_distance']),
                fuzzy_skin_mode='displacement',fuzzy_skin_noise_type='classic',fuzzy_skin_first_layer='0')
            for key,value in settings.items():ET.SubElement(part,'metadata',key=key,value=value)
        placements.append(dict(name=item['name'],xy_mm=xy,amplitude_mm=item['amplitude'],distance_mm=item['point_distance'],body_id=body_id,modifier_id=mask_id))
    plate=ET.SubElement(config,'plate')
    for key,value in dict(plater_id='1',plater_name='Provini fuzzy e S9 a filo',locked='false',filament_map_mode='Auto For Flush').items():ET.SubElement(plate,'metadata',key=key,value=value)
    ET.SubElement(config,'assemble')
    types='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    source=ROOT/'sorgenti/PROVINI_FUZZY_S9_R02_MODIFICATORI.3mf'
    with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in [('[Content_Types].xml',types),('_rels/.rels',rels),('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True)),('Metadata/model_settings.config',ET.tostring(config,encoding='utf-8',xml_declaration=True))]:z.writestr(name,data)
        for name,data in part_files.items():z.writestr(name,data)
        z.writestr('Metadata/project_settings.config',(ROOT/'slicer/configurazione_completa.json').read_bytes())
        partrels=ET.Element('Relationships',xmlns='http://schemas.openxmlformats.org/package/2006/relationships')
        for i,name in enumerate(part_files):ET.SubElement(partrels,'Relationship',Target='/'+name,Id=f'rel{i}',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
        z.writestr('3D/_rels/3dmodel.model.rels',ET.tostring(partrels,encoding='utf-8',xml_declaration=True))
    save(ROOT/'verifiche/piatto.json',dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),objects=placements,
        printable_count=5,modifier_count=3,units='millimeter',nominal_bed_mm=[256,256],brim_mm=5,
        note='I tre modificatori non sono pezzi stampabili e non aggiungono volume. Non usare STL per conservare la texture.'))

def slice_project(slicer):
    qa=ROOT/'verifiche/slicing';qa.mkdir(parents=True,exist_ok=True)
    source=ROOT/'sorgenti/PROVINI_FUZZY_S9_R02_MODIFICATORI.3mf'
    with tempfile.TemporaryDirectory(prefix='provini-fuzzy-s9-') as tmp:
        tmp=Path(tmp);out=tmp/'out';out.mkdir()
        args=['--datadir',str(tmp/'data'),'--load-settings',str(ROOT/'slicer/machine.json')+';'+str(ROOT/'slicer/process.json'),
            '--load-filaments',str(ROOT/'slicer/filament.json'),'--arrange','0','--orient','0','--slice','0',
            '--export-3mf','PROVINI.3mf','--outputdir',str(out),str(source)]
        previous=Path.cwd()
        try:
            os.chdir(ROOT)
            result=run_cli(slicer,args,qa/'slicer.log')
        finally:
            os.chdir(previous)
        gc=list(out.glob('*.gcode'));assert len(gc)==1
        layers,analysis=parse_gcode(gc[0])
        assert analysis['all_layers_nonempty'] and analysis['layer_count_matches_header']
        assert not analysis['out_of_bed_layers'] and not analysis['profile_exclusion_zone_violations']
        analysis['new_wall_islands']=screen_new_wall_islands(layers)
        assert analysis['new_wall_islands']['candidate_count']==0
        target=ROOT/'stampa/progetti_ElegooSlicer/PROVINI_FUZZY_S9_R02_ECC2_PLABASIC.3mf'
        shutil.copy2(out/'PROVINI.3mf',target)
        with zipfile.ZipFile(target) as z:
            assert z.testzip() is None
            warnings=[dict(n.attrib) for n in ET.fromstring(z.read('Metadata/slice_info.config')).iter() if n.tag=='warning']
            # Il profilo PLA ufficiale conserva la soglia di rammollimento
            # di 45 C: a piano 60 C il programma richiede ventilazione della
            # camera. Non alzare la soglia per nascondere l'avviso.
            assert all(w.get('msg')=='bed_temperature_too_high_than_filament' for w in warnings),warnings
            settings=json.loads(z.read('Metadata/project_settings.config'))
            assert settings['nozzle_diameter']==['0.4'] and settings['curr_bed_type']=='Textured PEI Plate'
            assert settings['layer_height']=='0.2' and settings['filament_type']==['PLA']
            assert settings['nozzle_temperature']==['220'] and settings['nozzle_temperature_initial_layer']==['220']
            assert settings['textured_plate_temp']==['60'] and settings['textured_plate_temp_initial_layer']==['60']
            assert settings['filament_max_volumetric_speed']==['5']
            assert 'PLA BASIC' in settings['filament_settings_id'][0]
            assert settings['enable_support']=='0' and settings['enable_prime_tower']=='0'
            cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
            printable=cfg.findall(".//part[@subtype='normal_part']")
            masks=cfg.findall(".//part[@subtype='modifier_part']")
            assert len(printable)==5 and len(masks)==3,(len(printable),len(masks))
            assert sorted(float(next(m.get('value') for m in v.findall('metadata') if m.get('key')=='fuzzy_skin_thickness')) for v in masks)==[.06,.08,.1]
            assert ET.fromstring(z.read('3D/3dmodel.model')).get('unit')=='millimeter'
            actual=z.read(next(n for n in z.namelist() if n.endswith('.gcode')))
            assert actual==gc[0].read_bytes()
        job=dict(project=str(target.relative_to(ROOT)),project_sha256=sha(target),slicer_version='2.4.2',application_bundle_version='1.5.3.5',material='ELEGOO PLA BASIC',
            source_sha256=sha(source),profiles={n:sha(ROOT/'slicer'/n) for n in ['machine.json','process.json','filament.json']},
            slicer_estimates=analysis['slicer_estimates'],cli=result,model_warnings=warnings,layers=len(layers),
            printable_objects=5,modifier_volumes=3,sent_to_printer=False,visual_review_complete=False)
        job['warning_resolution']=[dict(warning=w,action='Stampare con sportello anteriore aperto; evitare accumulo di calore nella camera. Soglia del profilo ufficiale conservata.',
            reference='https://github.com/OrcaSlicer/OrcaSlicer/wiki/material_basic_information') for w in warnings]
        job['totals']=estimate_totals([job])
        save(qa/'analisi.json',analysis);save(qa/'job.json',job)
        # Solo copia di lettura per il controllo; non e un G-code scritto a mano.
        (qa/'percorsi_slicer.gcode').write_bytes(actual)
        print(json.dumps(dict(layers=len(layers),estimates=job['totals'],project=str(target)),ensure_ascii=False),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--slice',action='store_true')
    ap.add_argument('--slicer',type=Path,default=Path('/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer'))
    args=ap.parse_args();generate()
    if args.slice:slice_project(args.slicer)
