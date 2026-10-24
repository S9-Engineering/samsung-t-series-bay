"""Tavole ingrandite dei percorsi salvati nei 3MF nativi, senza eseguire G-code."""
import json
import math
import tempfile
import zipfile
import argparse
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import genera as g
from slicer_utils import parse_gcode,ROLE_COLORS

ROOT=g.ROOT


def draw_layer(draw,layer,origin,size,frame):
    ox,oy=origin;x0,y0,x1,y1=frame
    scale=min((size-20)/(x1-x0),(size-32)/(y1-y0))
    draw.rectangle((ox,oy,ox+size-1,oy+size-1),outline="#ced5dc",fill="#fafbfd")
    for ax,ay,bx,by,role in layer["segments"]:
        dx,dy=bx-ax,by-ay;t0,t1=0.,1.;visible=True
        for pp,qq in ((-dx,ax-x0),(dx,x1-ax),(-dy,ay-y0),(dy,y1-ay)):
            if abs(pp)<1e-12:
                if qq<0:visible=False;break
            elif pp<0:t0=max(t0,qq/pp)
            else:t1=min(t1,qq/pp)
            if t0>t1:visible=False;break
        if not visible:continue
        ax,ay,bx,by=ax+t0*dx,ay+t0*dy,ax+t1*dx,ay+t1*dy
        draw.line((ox+10+(ax-x0)*scale,oy+size-8-(ay-y0)*scale,
                   ox+10+(bx-x0)*scale,oy+size-8-(by-y0)*scale),
                   fill=ROLE_COLORS.get(role,"#738494"),width=1)
    draw.rectangle((ox+1,oy+1,ox+size-2,oy+18),fill="white")
    draw.text((ox+6,oy+4),f"strato {layer['number']} | Z {layer['z_mm']:.2f} mm",fill="#24323d")


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--only");args=ap.parse_args()
    report=json.loads((ROOT/"verifiche/slicing/riepilogo.json").read_text())
    for job in report["jobs"]:
        if args.only and args.only not in job["name"]:continue
        p=ROOT/job["project"];assert g.sha(p)==job["project_sha256"]
        with zipfile.ZipFile(p)as z,tempfile.TemporaryDirectory()as td:
            settings=json.loads(z.read('Metadata/project_settings.config'))
            tool_offset=[float(v) for v in settings['extruder_offset'][0].split('x')]
            member=[n for n in z.namelist()if n.endswith(".gcode")][0]
            q=Path(td)/"controllo.gcode";q.write_bytes(z.read(member))
            layers,analysis=parse_gcode(q)
        bounds=analysis["extrusion_bounds_xy_mm"]
        frame=[bounds[0][0]-2,bounds[0][1]-2,bounds[1][0]+2,bounds[1][1]+2]
        folder=ROOT/"verifiche/slicing"/job["name"]
        pages=[]
        for start in range(0,len(layers),100):
            subset=layers[start:start+100];size=132;cols=10;rows=math.ceil(len(subset)/cols)
            im=Image.new("RGB",(cols*size,rows*size+30),"white");d=ImageDraw.Draw(im)
            d.text((8,8),job["name"]+" | tutti i percorsi, ritaglio sul piatto",fill="#24323d")
            for i,layer in enumerate(subset):
                draw_layer(d,layer,((i%cols)*size,30+(i//cols)*size),size,frame)
            dst=folder/f"ZOOM_tutti_{start+1:04d}_{start+len(subset):04d}.png";im.save(dst)
            pages.append(str(dst.relative_to(ROOT)))
        # Include ogni livello dei ponti lunghi piu i livelli funzionali noti.
        indexes={0,1,len(layers)-1}
        for b in analysis["longest_bridge_segments"]:
            for offset in (-1,0,1):
                indexes.add(max(0,min(len(layers)-1,b["layer"]-1+offset)))
        for height in (.6,.8,1.0,1.2,1.4,2.8,3,3.2,4.8,5,5.2,6,6.2,8,9.6,9.8,10,10.2,10.4,11.2,12,12.4,13,13.2,13.8,14,14.2,15,19,20,21.4,21.6,22,22.6,22.8,23,25,31,71,71.2,73.8,74,74.2,82.8,83):
            if height<=len(layers)*.2:
                indexes.add(min(len(layers)-1,max(0,round(height/.2)-1)))
        details=[]
        for start in range(0,len(indexes),6):
            selected=sorted(indexes)[start:start+6]
            im=Image.new("RGB",(1500,1035),"white");d=ImageDraw.Draw(im)
            d.text((10,8),job["name"]+" | livelli critici, ponti e strati sottostanti",fill="#24323d")
            for i,index in enumerate(selected):
                draw_layer(d,layers[index],((i%3)*500,30+(i//3)*500),500,frame)
            dst=folder/f"CRITICI_{start//6+1:02d}.png";im.save(dst);details.append(str(dst.relative_to(ROOT)))
        plate=next(p for p in json.loads((ROOT/'verifiche/piatti.json').read_text())['plates'] if p['name']==job['name'])
        insert=next((i for i in plate['items'] if i['part']=='inserto_T7_R13'),None)
        if insert:
            im=Image.new("RGB",(1500,1030),"white");d=ImageDraw.Draw(im)
            d.text((10,8),"Inserto T7: cappello sul piano e crescita delle due pareti",fill="#24323d")
            ix,iy=np.array(insert['xy'])-np.array(tool_offset)
            for i,index in enumerate([4,5,6,48,50,95]):
                draw_layer(d,layers[index],((i%3)*500,30+(i//3)*500),500,[ix-1,iy-1,ix+11,iy+10])
            dst=folder/"CLIP_INGRANDITA.png";im.save(dst);details.append(str(dst.relative_to(ROOT)))
        roof=next((i for i in plate['items'] if i['part']=='coperchio_R13'),None)
        if roof:
            im=Image.new("RGB",(1500,1035),"white");d=ImageDraw.Draw(im)
            d.text((10,8),"Coperchio capovolto: primo strato, tetto e linguette",fill="#24323d")
            rx,ry=np.array(roof['xy'])-np.array(tool_offset)
            for i,index in enumerate([0,14,15,49,59,74]):
                draw_layer(d,layers[index],((i%3)*500,30+(i//3)*500),500,[rx-2,ry-2,rx+92,ry+103])
            dst=folder/"COPERCHIO_AGGANCI.png";im.save(dst);details.append(str(dst.relative_to(ROOT)))
        body=next((i for i in plate['items'] if i['part']=='scocca_R13'),None)
        if body:
            y,z=min(g.side_pattern_points(),key=lambda p:(p[0]-40)**2+(p[1]-40)**2)
            closing=z+g.P["pattern_laterale"]["altezza"]/2
            center=math.ceil(closing/.2)-1
            selected=[max(0,min(len(layers)-1,center+off)) for off in (-3,-2,-1,0,1,2)]
            im=Image.new("RGB",(1500,1035),"white");d=ImageDraw.Draw(im)
            d.text((10,8),"Feritoie laterali: parete sinistra, chiusura superiore delle capsule orizzontali",fill="#24323d")
            bx,by=np.array(body['xy'])-np.array(tool_offset)
            for i,index in enumerate(selected):
                draw_layer(d,layers[index],((i%3)*500,30+(i//3)*500),500,[bx-1.5,by+y-5,bx+4.5,by+y+5])
            dst=folder/"FERITOIE_LATERALI.png";im.save(dst);details.append(str(dst.relative_to(ROOT)))
            logo=g.P['logo_frontale']
            # I percorsi G-code sottraggono l'offset dell'estrusore del profilo macchina.
            x0=body['xy'][0]+g.W-logo['margine_destro_mm']-logo['larghezza_mm']-tool_offset[0]
            y0=body['xy'][1]-tool_offset[1];wall_y=y0+logo['rilievo_mm']
            definition=json.loads((ROOT/'sorgenti'/logo['sorgente']).read_text())
            z0=logo['margine_inferiore_mm'];z1=z0+logo['larghezza_mm']*definition['normalized_height']
            glyph_layers={}
            for index,shape in enumerate(definition['shapes']):
                us=[p[0] for p in shape['outer']];a=x0+min(us)*logo['larghezza_mm'];b=x0+max(us)*logo['larghezza_mm']
                seen=[]
                for layer in layers:
                    if not z0-.01<=layer['z_mm']<=z1+.2:continue
                    if any(min(ax,bx)<=b and max(ax,bx)>=a and min(ay,by)<wall_y-.05 for ax,ay,bx,by,role in layer['segments']):
                        seen.append(dict(layer=layer['number'],z_mm=layer['z_mm']))
                assert seen and z0-.01<=seen[0]['z_mm']<=z0+.4
                assert z1-.4<=seen[-1]['z_mm']<=z1+.2
                glyph_layers['S' if index==0 else '9']=seen
            g.save(folder/'logo_percorsi.json',dict(project_sha256=job['project_sha256'],glyphs=glyph_layers,
                   tool_offset_xy_mm=tool_offset,
                   method='Estrusioni reali davanti alla parete, entro gli intervalli X dei due contorni e le quote del logo; coordinate corrette per offset estrusore del profilo.',
                   both_glyphs_present=True,physical_finish_verified=False))
            selected=[max(0,min(len(layers)-1,round(h/.2)-1)) for h in (z0,z0+.2,z0+.4,z0+3.4,z1-.02,z1+.2)]
            im=Image.new('RGB',(1500,1035),'white');d=ImageDraw.Draw(im)
            d.text((10,8),'S9 frontale: percorsi del rilievo, primo strato / crescita / chiusura',fill='#24323d')
            for i,index in enumerate(selected):
                draw_layer(d,layers[index],((i%3)*500,30+(i//3)*500),500,[x0-2,y0-1.5,x0+logo['larghezza_mm']+2,y0+3.5])
            dst=folder/'LOGO_FRONTALE.png';im.save(dst);details.append(str(dst.relative_to(ROOT)))
        g.save(folder/"tavole_revisione.json",dict(project_sha256=job["project_sha256"],
                  all_layers_zoom=pages,critical_layers=details,manually_reviewed=False,
                  note="Tavole da ispezionare; la loro generazione non costituisce approvazione automatica."))
    print("TAVOLE DI REVISIONE PRONTE",flush=True)


if __name__=="__main__":
    main()
