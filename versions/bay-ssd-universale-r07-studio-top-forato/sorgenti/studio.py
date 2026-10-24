"""Studio di un solo nuovo coperchio, senza modificare la consegna R06."""
import json,math
import cadquery as cq
import numpy as np
import trimesh
from PIL import Image,ImageDraw
from OCP.Geom import Geom_BezierSurface
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
import genera as g
from render_base import render,font,BG,INK,MUTED

ROOT=g.ROOT;T=g.P['top_studio'];PALETTE=dict(scocca='#30363c',tetto='#30363c')


def flat_face(points):
    return cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True))


def curved_plate():
    w,d,z=g.W,g.D,g.TOP
    high=z+T['spessore_minimo']+T['concavita']
    poles=TColgp_Array2OfPnt(1,5,1,5)
    # B2^4(u) B2^4(v) vale 36/256 al centro; bordi e pendenze al bordo
    # restano alti e orizzontali, senza un gradino intorno alla concavita.
    for i in range(5):
        for j in range(5):
            zz=high-T['concavita']*256/36 if (i,j)==(2,2) else high
            poles.SetValue(i+1,j+1,gp_Pnt(w*i/4,d*j/4,zz))
    face=cq.Face(BRepBuilderAPI_MakeFace(Geom_BezierSurface(poles),1e-7).Face())
    bottom=flat_face([(0,0,z),(0,d,z),(w,d,z),(w,0,z)])
    faces=[face,bottom]
    for a,b in [((0,0),(w,0)),((w,0),(w,d)),((w,d),(0,d)),((0,d),(0,0))]:
        faces.append(flat_face([(*a,z),(*b,z),(*b,high),(*a,high)]))
    solid=cq.Solid.makeSolid(cq.Shell.makeShell(faces)).fix()
    assert solid.isValid() and solid.Volume()>0
    outline=g.rounded(0,0,z,w,d,high-z,g.P['raggio_esterno'])
    shape=solid.intersect(outline).clean()
    # Piccolo raccordo superiore coerente con il monolite R06.
    outer_edges=[e for e in shape.Edges() if e.BoundingBox().zmin>high-.05]
    shape=shape.Solids()[0].fillet(.3,outer_edges).clean()
    return g.outer_fillet(shape,z,.2)


def new_lid():
    panel=curved_plate()
    radius=T['diametro_fori']/2
    x0,y0=T['primo_centro']
    holes=[g.cylinder(x0+i*T['passo'],y0+j*T['passo'],g.TOP-1,radius,7)
           for i in range(T['colonne']) for j in range(T['righe'])]
    panel=panel.cut(*holes).clean()
    locators=[g.box(x,3.3,80,8,1.6,3) for x in (19,63)]
    return g.union([panel,g.lid_latch('left'),g.lid_latch('right'),*locators])


def normalize(shape):
    b=shape.BoundingBox()
    return shape.translate((-b.xmin,-b.ymin,-b.zmin))


def main():
    lid=new_lid()
    assert lid.isValid() and len(lid.Solids())==1
    path=ROOT/'CAD_studio/coperchio_R07_STUDIO.step'
    cq.exporters.export(lid,str(path))
    lid=cq.importers.importStep(str(path)).val()
    assert lid.isValid() and len(lid.Solids())==1
    bounds=g.bounds(lid)
    mesh=g.mesh_of(lid)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
    assert len(mesh.split())==1 and mesh.area_faces.min()>1e-10
    assert len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces)
    mesh.export(ROOT/'verifiche/mesh_assieme/coperchio_R07_STUDIO.ply')
    shell=g.shell();body_mesh=g.mesh_of(shell)
    body_mesh.export(ROOT/'verifiche/mesh_assieme/scocca_R06.ply')
    assert sum(s.Volume() for s in shell.intersect(lid).Solids())<1e-5
    rows=[(dict(kind='struttura'),body_mesh),(dict(kind='coperchio'),mesh)]
    for slot,model in enumerate(('T7','T7_Shield','T9')):
        drive=g.drive(model,slot)
        assert sum(s.Volume() for s in drive.intersect(lid).Solids())<1e-5
        rows.append((dict(kind='gabarit_ssd',color=g.P['colori'][model]),g.mesh_of(drive)))
        if model!='T9':
            rows += [(dict(kind='inserto'),g.mesh_of(g.adapter(model,y,slot))) for y in g.S['centri_y']]
    for name,view in [
        ('02_R07_TRE_QUARTI.png',dict(camera=(-190,-230,190),target=(45,50.5,43),scale=84)),
        ('03_R07_TOP.png',dict(camera=(45,50.5,350),target=(45,50.5,43),up=(0,1,0),scale=64)),
        ('04_R07_DETTAGLIO.png',dict(camera=(-70,-115,175),target=(45,50.5,85),scale=65))]:
        render(rows,PALETTE,view,ROOT/'anteprime'/name)
    panel_only=lid.intersect(g.box(-1,-1,g.TOP,92,103,5)).clean()
    render([(dict(kind='coperchio'),g.mesh_of(panel_only))],PALETTE,
           dict(camera=(-45,-70,185),target=(45,50.5,85),scale=65),
           ROOT/'anteprime/05_R07_PANNELLO.png')
    board=Image.new('RGB',(2280,1180),BG);d=ImageDraw.Draw(board)
    d.text((60,35),'R07 / TOP FORATO',font=font(48,True),fill=INK)
    d.text((62,107),'Fori tondi · lieve concavità · un solo coperchio a incastro',font=font(26),fill=MUTED)
    for x,label,name in [(30,'MONOLITE','02_R07_TRE_QUARTI.png'),(1170,'DETTAGLIO DEL TETTO','05_R07_PANNELLO.png')]:
        d.text((x+30,191),label,font=font(25,True),fill=INK)
        board.paste(Image.open(ROOT/'anteprime'/name).convert('RGB'),(x,230))
    d.text((60,1120),'Studio CAD · concavità 1 mm · interno R05 e scocca R06 conservati · senza LED',font=font(25),fill=MUTED)
    board.save(ROOT/'anteprime/01_R07_STUDIO.png')
    variants=[]
    for name,shape in [('faccia_concava_giu',lid.rotate((0,0,0),(1,0,0),180)),
                       ('sul_bordo_frontale',lid.rotate((0,0,0),(1,0,0),90))]:
        shape=normalize(shape)
        out=ROOT/'verifiche/slicing_input'/f'R07_STUDIO_{name}.stl'
        cq.exporters.export(shape,str(out),tolerance=.045,angularTolerance=.09)
        printed=trimesh.load_mesh(out,process=True)
        printed.apply_translation(-printed.bounds[0]);printed.export(out)
        assert printed.is_watertight and printed.is_winding_consistent and printed.volume>0
        variants.append(dict(name=name,path=str(out.relative_to(ROOT)),sha256=g.sha(out),bounds_mm=printed.bounds.tolist()))
    old=json.loads((ROOT.parent/'bay-ssd-universale-r06-monolite/verifiche/aria.json').read_text())
    area=T['righe']*T['colonne']*math.pi*T['diametro_fori']**2/4/100
    g.save(ROOT/'verifiche/studio.json',dict(
        state='STUDIO_COPERCHIO_NON_PRONTO_PER_LA_STAMPA',unit='mm',
        holes=T['righe']*T['colonne'],hole_diameter_mm=T['diametro_fori'],pitch_mm=T['passo'],
        min_web_mm=T['passo']-T['diametro_fori'],depression_mm=T['concavita'],
        min_panel_thickness_mm=T['spessore_minimo'],bare_height_mm=87,
        old_top_aperture_cm2=old['roof_net_cm2'],round_hole_area_cm2=area,
        area_delta_percent=(area/old['roof_net_cm2']-1)*100,
        lid_valid=True,lid_solids=1,mesh_closed=True,mesh_winding=True,bounds_mm=bounds,
        step_sha256=g.sha(path),extra_parts=0,new_hardware=0,slicing_variants=variants,
        leds=False,fan=False,physical_print=False,thermal_validation=False,
        note='Le aree aperte non provano pari portata o prestazioni termiche. Orientamento e supporti da verificare nello slicer.'))
    print('STUDIO R07 ESPORTATO',flush=True)


if __name__=='__main__':main()
