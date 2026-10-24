"""3MF nativi con modificatori e lettura indipendente per ID dei corpi."""
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np
import trimesh
from shapely.geometry import box
import genera as g
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';PN='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
ET.register_namespace('',NS);ET.register_namespace('p',PN)
def tag(s):return '{'+NS+'}'+s
IDENTITY='1 0 0 0 1 0 0 0 1 0 0 0'
def matrix(text):
    a=np.array([float(x) for x in text.split()]).reshape(4,3);m=np.eye(4);m[:3,:3]=a[:3].T;m[:3,3]=a[3];return m

def export_plate(path,items,meshes):
    root=ET.Element(tag('model'),unit='millimeter',requiredextensions='p')
    for k,v in [('Application','ElegooSlicer-1.5.3.5'),('OrcaSlicer','2.4.2'),('BambuStudio:3mfVersion','1'),('Title','BAY R22 / tetto scorrevole e fermo nascosto, PLA BASIC')]:ET.SubElement(root,tag('metadata'),name=k).text=v
    resources=ET.SubElement(root,tag('resources'));build=ET.SubElement(root,tag('build'));cfg=ET.Element('config');idx=0;files={}
    def add(m):
        nonlocal idx
        idx+=1;r=ET.Element(tag('model'),unit='millimeter');rr=ET.SubElement(r,tag('resources'));o=ET.SubElement(rr,tag('object'),id=str(idx),type='model')
        mm=ET.SubElement(o,tag('mesh'));vs=ET.SubElement(mm,tag('vertices'));ts=ET.SubElement(mm,tag('triangles'))
        for v in m.vertices:ET.SubElement(vs,tag('vertex'),attrib={k:f'{a:.7f}' for k,a in zip('xyz',v)})
        for f in m.faces:ET.SubElement(ts,tag('triangle'),attrib={f'v{i+1}':str(int(a)) for i,a in enumerate(f)})
        ET.SubElement(r,tag('build'));files[f'3D/Objects/part_{idx}.model']=ET.tostring(r,encoding='utf-8',xml_declaration=True);return idx
    for item in items:
        m=meshes[item['part']].copy();m.apply_translation(-m.bounds[0]);pid=add(m)
        placed=m.copy();placed.apply_translation([*item['xy'],0]);item['bounds_mm']=placed.bounds.tolist()
        mids=[]
        idx+=1;oid=idx;o=ET.SubElement(resources,tag('object'),id=str(oid),type='model',name=item['name']);cc=ET.SubElement(o,tag('components'))
        for part in [pid,*[a for a,b in mids]]:ET.SubElement(cc,tag('component'),objectid=str(part),attrib={'{'+PN+'}path':f'/3D/Objects/part_{part}.model'})
        x,y=item['xy'];ET.SubElement(build,tag('item'),objectid=str(oid),transform=f'1 0 0 0 1 0 0 0 1 {x} {y} 0')
        co=ET.SubElement(cfg,'object',id=str(oid))
        opts=dict(name=item['name'],extruder='1',fuzzy_skin='disabled_fuzzy',enable_support='1' if item.get('support') else '0')
        if item.get('solid'):opts['sparse_infill_density']='100%';opts['sparse_infill_pattern']='rectilinear'
        for k,v in opts.items():ET.SubElement(co,'metadata',key=k,value=v)
        cp=ET.SubElement(co,'part',id=str(pid),subtype='normal_part');ET.SubElement(cp,'metadata',key='name',value=item['name'])
    pp=ET.SubElement(cfg,'plate')
    for k,v in dict(plater_id='1',plater_name='BAY R22',locked='false',filament_map_mode='Auto For Flush').items():ET.SubElement(pp,'metadata',key=k,value=v)
    ET.SubElement(cfg,'assemble')
    types='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in [('[Content_Types].xml',types),('_rels/.rels',rels),('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True)),('Metadata/model_settings.config',ET.tostring(cfg,encoding='utf-8',xml_declaration=True)),('Metadata/project_settings.config',(g.ROOT/'slicer/configurazione_completa.json').read_bytes())]:z.writestr(name,data)
        for name,data in files.items():z.writestr(name,data)
        rr=ET.Element('Relationships',xmlns='http://schemas.openxmlformats.org/package/2006/relationships')
        for i,name in enumerate(files):ET.SubElement(rr,'Relationship',Target='/'+name,Id=f'rel{i}',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
        z.writestr('3D/_rels/3dmodel.model.rels',ET.tostring(rr,encoding='utf-8',xml_declaration=True))

def validate(path,items=None):
    rows=[];footprints=[]
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        root=ET.fromstring(z.read('3D/3dmodel.model'));assert root.get('unit')=='millimeter'
        objects={o.get('id'):o for o in root.findall(tag('resources')+'/'+tag('object'))};cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        for item in root.findall(tag('build')+'/'+tag('item')):
            oid=item.get('objectid');co=cfg.find(f"object[@id='{oid}']")
            name=next(v.get('value') for v in co.findall('metadata') if v.get('key')=='name')
            for component in objects[oid].findall(tag('components')+'/'+tag('component')):
                pid=component.get('objectid');part=co.find(f"part[@id='{pid}']");role=part.get('subtype')
                r=ET.fromstring(z.read(component.get('{'+PN+'}path').lstrip('/')))
                o=r.find(tag('resources')+'/'+tag('object')+f"[@id='{pid}']")
                vs=np.array([[float(v.get(k)) for k in 'xyz'] for v in o.findall('.//'+tag('vertex'))]);fs=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in o.findall('.//'+tag('triangle'))])
                mesh=trimesh.Trimesh(vs,fs,process=True);transform=matrix(item.get('transform',IDENTITY))@matrix(component.get('transform',IDENTITY));mesh.apply_transform(transform)
                assert abs(np.linalg.det(transform[:3,:3])-1)<1e-9 and mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
                if role=='normal_part':
                    assert len(mesh.split())==1
                    if items:
                        expected=next(i for i in items if i['name']==name)
                        assert np.max(np.abs(mesh.bounds-np.array(expected['bounds_mm'])))<.06
                    fp=box(mesh.bounds[0,0]-5,mesh.bounds[0,1]-5,mesh.bounds[1,0]+5,mesh.bounds[1,1]+5)
                    assert fp.within(box(0,0,256,256)) and fp.intersection(box(246,0,256,20)).area==0
                    for other in footprints:assert fp.intersection(other).area==0
                    footprints.append(fp)
                rows.append(dict(name=name,role=role,bounds_mm=mesh.bounds.tolist(),volume_mm3=float(mesh.volume),closed=True))
    return dict(result='PASS',units='millimeter',printable_count=len(footprints),modifier_count=sum(r['role']=='modifier_part' for r in rows),parts=rows,
        method='Lettura indipendente per percorso e objectid; trasformazioni build e component composte; brim 5 mm e zona esclusa verificati.')
