"""Controlli sui file R15 esportati e sull'assieme statico nominale."""
import itertools,json,math
import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
import genera as g
from verifica_intersezioni_mesh import self_intersections_fast
ROOT=g.ROOT;P=g.P


def overlap(a,b):
    ba,bb=np.array(g.bounds(a)),np.array(g.bounds(b))
    if np.any(np.minimum(ba[1],bb[1])-np.maximum(ba[0],bb[0])<=1e-6):return 0.
    return sum(s.Volume() for s in a.intersect(b).Solids())


def section(mesh,z):
    cut=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    out=Polygon()
    if cut:
        for loop in cut.discrete:
            if len(loop)>=4 and np.linalg.norm(loop[0]-loop[-1])<1e-4:
                p=Polygon(loop[:,:2]);out=out.symmetric_difference(p if p.is_valid else p.buffer(0))
    return out


def shadow(mesh,domain):
    triangles=mesh.triangles[:,:,:2]
    a,b=triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]
    cross=a[:,0]*b[:,1]-a[:,1]*b[:,0]
    return unary_union([Polygon(t) for t in triangles[np.abs(cross)>1e-8]]).intersection(domain)


def side_section(mesh,x):
    cut=mesh.section(plane_origin=[x,0,0],plane_normal=[1,0,0]);out=Polygon()
    if cut:
        for loop in cut.discrete:
            if len(loop)>=4 and np.linalg.norm(loop[0]-loop[-1])<1e-4:
                p=Polygon(loop[:,1:3]);out=out.symmetric_difference(p if p.is_valid else p.buffer(0))
    return out


def rear_section(mesh,y):
    cut=mesh.section(plane_origin=[0,y,0],plane_normal=[0,1,0]);out=Polygon()
    if cut:
        for loop in cut.discrete:
            if len(loop)>=4 and np.linalg.norm(loop[0]-loop[-1])<1e-4:
                poly=Polygon(loop[:,[0,2]]);out=out.symmetric_difference(poly if poly.is_valid else poly.buffer(0))
    return out


def main():
    man=json.loads((ROOT/"verifiche/manifest.json").read_text())
    assert man["parameters_sha256"]==g.sha(ROOT/"sorgenti/parametri.json")
    shapes={};rows=[];cache_path=ROOT/"verifiche/cache_autointersezioni.json"
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    for part in man["parts"]:
        print("CONTROLLO",part["name"],flush=True)
        m=trimesh.load_mesh(ROOT/part["stl"],process=True)
        si=cache.get(part["stl_sha256"])
        if si is None:
            si=self_intersections_fast(m);cache[part["stl_sha256"]]=si;g.save(cache_path,cache)
        assert g.sha(ROOT/part["stl"])==part["stl_sha256"]
        source=cq.importers.importStep(str(ROOT/part["step"])).val()
        printed=cq.importers.importStep(str(ROOT/"CAD"/(part["name"]+"_orientato_stampa.step"))).val()
        assert source.isValid() and printed.isValid()
        assert len(source.Solids())==len(printed.Solids())==1
        assert m.is_watertight and m.is_winding_consistent and m.volume>0
        assert len(m.split())==m.body_count==1
        assert not np.any(m.area_faces<1e-10)
        assert len(np.unique(np.sort(m.faces,axis=1),axis=0))==len(m.faces)
        assert si["intersection_pairs"]==0,(part["name"],si)
        assert abs(m.volume/source.Volume()-1)<.005
        assert np.max(np.abs(m.bounds-np.array(g.bounds(printed))))<.06
        shapes[part["name"]]=source
        rows.append(dict(name=part["name"],stl_sha256=part["stl_sha256"],step_sha256=g.sha(ROOT/part["step"]),
            mesh_closed=True,winding_consistent=True,volume_positive_mm3=m.volume,
            components=1,step_valid=True,degenerate_faces=0,duplicate_faces=0,
            self_intersections=si,print_bounds_mm=m.bounds.tolist()))
    shell,lid=shapes["scocca_R15"],shapes["coperchio_R15"]
    logo=P["logo_frontale"];data=json.loads((ROOT/"sorgenti"/logo["sorgente"]).read_text())
    assert man["logo_contours_sha256"]==g.sha(ROOT/"sorgenti"/logo["sorgente"])
    protrusion=shell.intersect(g.box(-1,-1,-1,g.W+2,1,g.TOP+3))
    assert len(protrusion.Solids())==2 and protrusion.isValid()
    expected=[[g.W-logo["margine_destro_mm"]-logo["larghezza_mm"],-logo["rilievo_mm"],logo["margine_inferiore_mm"]],
              [g.W-logo["margine_destro_mm"],0,logo["margine_inferiore_mm"]+logo["larghezza_mm"]*data["normalized_height"]]]
    assert np.allclose(g.bounds(protrusion),expected,atol=1e-5)
    assert not logo["sottotitolo"] and len(data["shapes"])==2
    # Quattro spigoli verticali rettilinei alle coordinate esterne nominali, sui STEP riaperti.
    sharp_edges=[]
    for name,shape,height in (("scocca",shell,g.TOP),("coperchio",lid,P["tetto"])):
        depth=g.D if name=='scocca' else g.D+P['retro_coperchio']['arretramento_esterno_mm']
        corners=[]
        for x,y in ((0,0),(g.W,0),(0,depth),(g.W,depth)):
            edge_height=(g.TOP+P['tetto']-P['retro_coperchio']['quota_inferiore_mm']) if name=='coperchio' and y==depth else height
            matches=[]
            for edge in shape.Edges():
                b=edge.BoundingBox()
                if edge.geomType()=="LINE" and abs(b.xmin-x)<1e-5 and abs(b.xmax-x)<1e-5 and abs(b.ymin-y)<1e-5 and abs(b.ymax-y)<1e-5 and abs(b.zlen-edge_height)<1e-5:
                    matches.append(edge.Length())
            assert len(matches)==1,(name,x,y,matches)
            corners.append(dict(x=x,y=y,vertical_edge_length_mm=matches[0]))
        sharp_edges.append(dict(part=name,corners=corners))
    for key in ("raggio_esterno","raccordo_bordi","raccordo_tetto_superiore","raccordo_tetto_inferiore"):assert P[key]==0
    # Precarico intenzionale limitato ai due pattini.
    free_intersection=shell.intersect(lid);preload=overlap(shell,lid)
    assert preload>0 and len(free_intersection.Solids())==2
    for solid in free_intersection.Solids():
        bb=g.bounds(solid)
        assert bb[0][2]>=P['coperchio']['pattino_z_min_mm']-1e-6
        assert bb[1][2]<=P['coperchio']['pattino_z_max_mm']+1e-6
        assert min(abs(bb[0][0]-3),abs(bb[1][0]-3),abs(bb[0][0]-87),abs(bb[1][0]-87))<1e-5
    loaded_lid=g.lid(loaded=True)
    assert overlap(shell,loaded_lid)<1e-5
    u=P['supporti_u'];wall_min=(u['larghezza_esterna_mm']-g.S['larghezze_adattate']['T7_Shield'])/2
    assert wall_min>=2.4 and u['spessore_base_mm']>=1.2
    for slot in range(3):
        for model in ('T7','T7_Shield'):
            for y in g.S['centri_y']:
                for dz in (0,.2,1,5,10,20,40,90):
                    assert overlap(g.adapter(model,y,slot).translate((0,0,dz)),shell)<1e-5

    cases=[];usb_cases=[]
    for slot in range(3):
        for model,d in P["ssd_nominali"].items():
            ssd=g.drive(model,slot)
            inserts=[] if model=="T9" else [g.adapter(model,y,slot) for y in g.S["centri_y"]]
            solids=[shell,lid,*inserts]
            values=[overlap(ssd,s) for s in solids]
            assert max(values)<1e-5,(slot,model,values)
            plug=g.usb_keepout(model,slot)
            plug_overlap=sum(overlap(plug,shape) for shape in solids)
            assert plug_overlap<1e-5,(slot,model,'USB',plug_overlap)
            upper=g.drive_seat_z(model)+d['altezza']/2+P['retro_coperchio']['ingombro_spina_altezza_mm']/2
            clearance=P['retro_coperchio']['quota_inferiore_mm']-upper
            assert clearance>=3
            usb_cases.append(dict(slot=slot+1,model=model,keepout_bounds_mm=g.bounds(plug),
                nominal_port_center_z_mm=g.drive_seat_z(model)+d['altezza']/2,vertical_clearance_mm=clearance,
                intersections_mm3=plug_overlap,measured=False))
            for insert in inserts:
                assert overlap(insert,shell)<1e-5 and overlap(insert,lid)<1e-5,(slot,model,"inserto")
            lifts=[]
            for dz in (1,5,10,20,40,90):
                v=sum(overlap(g.drive(model,slot,dz),s) for s in [shell,*inserts])
                assert v<1e-5,(slot,model,"estrazione",dz,v)
                lifts.append(dict(lift_mm=dz,intersections_mm3=v))
            cases.append(dict(slot=slot+1,model=model,adapters=len(inserts),
                aperture_mm=g.S["larghezze_adattate"][model],total_thickness_clearance_mm=g.S["larghezze_adattate"][model]-d["spessore"],
                static_intersections_mm3=values,extraction_samples=lifts))
    assignments=[]
    for models in itertools.product(P["ssd_nominali"],repeat=3):
        solids=[]
        for slot,model in enumerate(models):
            solids += [g.drive(model,slot),g.usb_keepout(model,slot)]
            if model!="T9":solids += [g.adapter(model,y,slot) for y in g.S["centri_y"]]
        for a,b in itertools.combinations(solids,2):assert overlap(a,b)<1e-5,models
        assignments.append(list(models))
    ass=cq.importers.importStep(str(ROOT/"CAD/BAY_R15_ASSIEME_GABARIT.step")).val()
    assert ass.isValid() and len(ass.Solids())==len(man["display"])==9
    # Le quattro tasche hanno fondo pieno; la verifica non determina il piedino commerciale.
    feet=[]
    for x,y in P["piedini"]["centri_xy"]:
        probe=g.cylinder(x,y,.8,5,.2);fraction=overlap(probe,shell)/probe.Volume()
        assert fraction>.999;feet.append(dict(x=x,y=y,solid_floor_fraction=fraction))
    mesh_shell=g.mesh_of(shell);mesh_lid=g.mesh_of(lid)
    p=P["pattern_laterale"]
    a,b=p["y_min"],p["y_max"];s=p["inclinazione_bordi"]*(b-a)
    side_domain=Polygon([(a,p["z_min"]),(b,p["z_min"]+s),(b,p["z_max"]+s),(a,p["z_max"])])
    side_openings=[side_domain.difference(side_section(mesh_shell,x)) for x in (1.5,88.5)]
    side_areas=[openings.area/100 for openings in side_openings]
    opening_bounds=[]
    for openings in side_openings:
        holes=list(openings.geoms) if hasattr(openings,"geoms") else [openings]
        assert len(holes)==len(g.side_pattern_points())
        sizes=[(hole.bounds[2]-hole.bounds[0],hole.bounds[3]-hole.bounds[1]) for hole in holes]
        assert all(abs(w-p["larghezza"])<.03 and abs(h-p["altezza"])<.03 and w>h for w,h in sizes),sizes
        opening_bounds.append(sizes)
    assert p["inclinazione_righe"]==p["angolo_feritoia_gradi"]==0
    nominal=len(g.side_pattern_points())*(min(p["larghezza"],p["altezza"])*abs(p["larghezza"]-p["altezza"])+math.pi*(min(p["larghezza"],p["altezza"])/2)**2)/100
    assert all(abs(area/nominal-1)<.01 for area in side_areas),(side_areas,nominal)
    roi=box(3,12,87,101)
    domain=unary_union([box(a,18,b,101) for a,b in ((3,14),(28,38),(52,62),(76,87))])
    obstacles=[mesh_shell,mesh_lid,*[g.mesh_of(g.drive("T9",i)) for i in range(3)]]
    free=domain.difference(unary_union([shadow(m,domain) for m in obstacles]))
    air=dict(floor_net_cm2=roi.difference(section(mesh_shell,2.5)).area/100,
             roof_net_cm2=roi.difference(section(mesh_lid,84.5)).area/100,
             continuous_vertical_corridors_three_T9_cm2=free.area/100,
             side_pattern_holes_per_panel=len(g.side_pattern_points()),
             side_pattern_net_cm2=side_areas,side_pattern_nominal_cm2=nominal,
             side_openings_horizontal_verified=True,side_opening_bounds_yz_mm=opening_bounds,
             method="Aree sulle mesh esportate; corridoi verticali conservativi dalla proiezione di tutti i solidi, tre T9 senza inserti.",
             cfd=False,thermal_test=False)
    # Le U allargano localmente gli appoggi: controllo dei corridoi anche
    # con gli adattatori presenti, non soltanto con tre T9 diretti.
    fixed_shadow=unary_union([shadow(mesh_shell,domain),shadow(mesh_lid,domain)])
    per_slot={}
    for slot in range(3):
        for model in P['ssd_nominali']:
            moving=[g.drive(model,slot)]
            if model!='T9':moving += [g.adapter(model,y,slot) for y in g.S['centri_y']]
            per_slot[(slot,model)]=unary_union([shadow(g.mesh_of(obj),domain) for obj in moving])
    air_cases=[]
    for models in itertools.product(P['ssd_nominali'],repeat=3):
        area=domain.difference(unary_union([fixed_shadow,*[per_slot[(slot,model)] for slot,model in enumerate(models)]])).area/100
        assert area>0
        air_cases.append(dict(models=list(models),vertical_corridors_cm2=area))
    air['assignments_with_U_cradles']=air_cases
    air['minimum_vertical_corridors_all_assignments_cm2']=min(row['vertical_corridors_cm2'] for row in air_cases)
    air['air_method_U']='Intersezione in pianta fra passaggi del fondo/tetto e proiezioni di scocca, coperchio, tre SSD e tutte le U installate; 27 configurazioni nominali, non CFD.'
    back_y=g.D+P['retro_coperchio']['arretramento_esterno_mm']-P['retro_coperchio']['spessore_mm']/2
    rear_domain=box(3,g.B,g.W-3,g.TOP+P['tetto'])
    air['rear_open_below_tail_cm2']=rear_domain.difference(rear_section(mesh_lid,back_y)).area/100
    assert abs(air['rear_open_below_tail_cm2']-(g.W-6)*(P['retro_coperchio']['quota_inferiore_mm']-g.B)/100)<.03
    assert air["continuous_vertical_corridors_three_T9_cm2"]>0
    g.save(ROOT/"verifiche/aria.json",air)
    g.save(ROOT/"verifiche/geometria.json",dict(result="PASS_DIGITALE_QUOTE_NOMINALI",
        source_manifest_sha256=g.sha(ROOT/"verifiche/manifest.json"),source_parameters_sha256=man["parameters_sha256"],
        export_checks=rows,model_slot_cases=cases,assignments_checked=len(assignments),
        assignment_cases=assignments,assignments_include_nominal_usb_keepouts=True,assembly_step_solids=9,kit_parts=6,feet=feet,usb_cases=usb_cases,
        rear_tail=dict(parameters=P['retro_coperchio'],rear_inner_y_mm=back_y-P['retro_coperchio']['spessore_mm']/2,
            longest_ssd_end_y_mm=104,axial_clearance_mm=2,minimum_nominal_usb_clearance_mm=min(c['vertical_clearance_mm'] for c in usb_cases),
            physical_connector_dimensions_verified=False),
        body_lid_static_overlap_mm3=preload,
        lid_preload=dict(per_side_mm=P['coperchio']['precarico_per_lato_mm'],
            intended_contact_solids=2,free_shape_intersection_mm3=preload,
            inward_translated_check_mm=P['coperchio']['precarico_per_lato_mm'],
            envelope_intersection_mm3=overlap(shell,loaded_lid),
            window_width_mm=9.6,tab_width_mm=P['coperchio']['larghezza_linguetta'],window_y_clearance_per_end_mm=(9.6-P['coperchio']['larghezza_linguetta'])/2,
            force_validated=False,FEA=False),
        U_cradles=dict(bilateral=True,wall_min_mm=wall_min,base_mm=u['spessore_base_mm'],end_collar_depth_mm=(u['profondita_mm']-g.S['larghezza_appoggio_y']-2*u['gioco_guide_per_lato_mm'])/2,
            bearing_area_per_cradle_mm2=(g.S['larghezza_libera']-2*u['gioco_guide_per_lato_mm'])*g.S['larghezza_appoggio_y'],
            guide_clearance_per_side_mm=u['gioco_guide_per_lato_mm'],seat_raise_mm=u['spessore_base_mm'],insertion_path_sampled=True,stiffness_validated=False),hardware_components=0,internal_adhesives=False,
        sharp_external_edges_verified=True,external_edges_on_reopened_step=sharp_edges,
        logo_verified=dict(glyphs=2,emboss_mm=logo["rilievo_mm"],width_mm=logo["larghezza_mm"],bounds_mm=g.bounds(protrusion),
                           subtitle=False,fused_with_shell=True,source_png_sha256=data["source_png_sha256"]),
        guide_channel_mm=15,adapters_channels_mm=dict(T7=9,Shield=13.6),
        guide_height_above_seat_mm=18,printed_adapter_side_wall_min_mm=wall_min,
        lid_snap_finger_mm=dict(thickness=1.2,width=P["coperchio"]["larghezza_linguetta"],length=12,engagement=.6),
        adapter_hook_engagement_mm=0,
        side_pattern_holes_per_panel=len(g.side_pattern_points()),
        side_vent_mm=dict(width=p["larghezza"],height=p["altezza"],angle_degrees=0,horizontal_orientation_verified_on_exported_mesh=True,wall_thickness=3,solid_diagonal_band=p["fascia_diagonale_mm"]),
        limitations=["Quote nominali, SSD e gommini reali non misurati.",
            "Precarico geometrico intenzionale 0,15 mm per lato sui due pattini; inviluppo traslato controllato, senza simulazione elastica o misura della forza.",
            "Screening autointersezioni esclude triangoli con vertici condivisi.",
            "Estrazione verificata a quote campionate con coperchio rimosso e cavi scollegati.",
            "Assenza di serraggio: i dischi sono guidati e appoggiati, il retro rimane aperto.",
            "USB al centro nominale della faccia corta; ingombro spina 20 x 20 x 50 mm generoso e modificabile, non misurato.",
            "Nessuna prova fisica o termica."],
        physical_fit=False,physical_print=False,thermal_test=False))
    print(json.dumps(dict(exports=len(rows),model_slot_cases=len(cases),assignments=len(assignments),minimum_air_cm2=air["minimum_vertical_corridors_all_assignments_cm2"])),flush=True)


if __name__=="__main__":main()
