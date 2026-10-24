"""Traccia i due PNG approvati senza modificarli; produce SVG e contorni CAD.

Richiede opencv-python 4.11.0.86 e numpy. Il CAD usa direttamente il JSON
incluso, quindi non richiede OpenCV per le successive rigenerazioni.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def oriented(points,positive):
    p=np.asarray(points,dtype=float)
    area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
    return (p if (area>0)==positive else p[::-1]).tolist()


def trace(name):
    path=ROOT/(name+'.png');img=cv2.imread(str(path))
    assert img is not None
    mask=(img.min(axis=2)>180).astype('uint8')*255
    contours,hierarchy=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    hierarchy=hierarchy[0];shapes=[]
    for i,c in enumerate(contours):
        if hierarchy[i,3]!=-1 or cv2.contourArea(c)<80:continue
        outer=cv2.approxPolyDP(c,.75,True)[:,0,:].astype(float)
        holes=[];child=hierarchy[i,2]
        while child!=-1:
            holes.append(cv2.approxPolyDP(contours[child],.75,True)[:,0,:].astype(float))
            child=hierarchy[child,0]
        shapes.append((outer,holes))
    expected=2 if name=='logo_S9' else 13
    assert len(shapes)==expected,(name,len(shapes))
    points=np.concatenate([p for p,_ in shapes]);lo=points.min(axis=0);hi=points.max(axis=0)
    width,height=hi-lo
    paths=[];normalized=[]
    for outer,holes in sorted(shapes,key=lambda s:(s[0][:,0].min())):
        commands=[]
        for loop in [outer,*holes]:
            p=loop-lo
            commands.append('M '+' L '.join(f'{x:.3f},{y:.3f}' for x,y in p)+' Z')
        paths.append('<path d="'+' '.join(commands)+'" fill="#30363c" fill-rule="evenodd"/>')
        def convert(loop):return [[float((x-lo[0])/width),float((hi[1]-y)/width)] for x,y in loop]
        normalized.append(dict(outer=oriented(convert(outer),True),holes=[oriented(convert(h),False) for h in holes]))
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" role="img" aria-label="{name}">\n'+"\n".join(paths)+'\n</svg>\n'
    (ROOT/(name+'.svg')).write_text(svg)
    result=dict(name=name,source_png=name+'.png',source_png_sha256=sha(path),
        vector_svg=name+'.svg',vector_svg_sha256=sha(ROOT/(name+'.svg')),
        method='Contorni dei PNG approvati; soglia minima RGB 180/255; semplificazione 0,75 pixel.',
        opencv_version=cv2.__version__,glyphs=len(shapes),normalized_width=1.,normalized_height=float(height/width),shapes=normalized)
    (ROOT/'sorgenti'/(name+'_contorni.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--copy-to-workspace-root',action='store_true');args=ap.parse_args()
    records=[trace(name) for name in ('logo_S9','logo_S9_Engineering')]
    if args.copy_to_workspace_root:
        for name in ('logo_S9','logo_S9_Engineering'):
            for ext in ('.png','.svg'):
                target=ROOT.parent/(name+ext)
                if target.exists():assert sha(target)==sha(ROOT/(name+ext)),target
                else:shutil.copy2(ROOT/(name+ext),target)
    report=dict(logos=[{k:v for k,v in r.items() if k!='shapes'} for r in records],
        original_rasters_unchanged=True,vector_geometry_derived_from_rasters=True,
        application='Solo S9 senza sottotitolo, rilievo monocolore sul fronte basso a destra.')
    (ROOT/'verifiche/provenienza_loghi.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('LOGHI SALVATI E TRACCIATI',[(r['name'],r['glyphs']) for r in records])


if __name__=='__main__':main()
