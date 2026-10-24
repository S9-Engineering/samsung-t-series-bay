from PIL import Image,ImageDraw
from slicer_utils import ROLE_COLORS

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

