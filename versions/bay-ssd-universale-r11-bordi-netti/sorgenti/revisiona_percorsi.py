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
        # Ingrandimento dell'inserto T7 del provino.
        if job["group"]=="provino":
            im=Image.new("RGB",(1500,1030),"white");d=ImageDraw.Draw(im)
            for i,index in enumerate([4,5,6,48,50,52]):
                draw_layer(d,layers[index],((i%3)*500,30+(i//3)*500),500,[64,27,76,37])
            dst=folder/"CLIP_INGRANDITA.png";im.save(dst);details.append(str(dst.relative_to(ROOT)))
        if "SCOCCA" in job["name"]:
            y,z=min(g.side_pattern_points(),key=lambda p:(p[0]-40)**2+(p[1]-40)**2)
            closing=z+g.P["pattern_laterale"]["altezza"]/2
            center=math.ceil(closing/.2)-1
            selected=[max(0,min(len(layers)-1,center+off)) for off in (-3,-2,-1,0,1,2)]
            im=Image.new("RGB",(1500,1035),"white");d=ImageDraw.Draw(im)
            d.text((10,8),"Feritoie laterali: parete sinistra, chiusura superiore delle capsule orizzontali",fill="#24323d")
            for i,index in enumerate(selected):
                draw_layer(d,layers[index],((i%3)*500,30+(i//3)*500),500,[18.5,28+y-5,24.5,28+y+5])
            dst=folder/"FERITOIE_LATERALI.png";im.save(dst);details.append(str(dst.relative_to(ROOT)))
        g.save(folder/"tavole_revisione.json",dict(project_sha256=job["project_sha256"],
                  all_layers_zoom=pages,critical_layers=details,manually_reviewed=False,
                  note="Tavole da ispezionare; la loro generazione non costituisce approvazione automatica."))
    print("TAVOLE DI REVISIONE PRONTE",flush=True)


if __name__=="__main__":
    main()
