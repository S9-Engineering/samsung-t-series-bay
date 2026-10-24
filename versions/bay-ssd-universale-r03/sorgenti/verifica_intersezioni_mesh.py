"""Screening dei triangoli esportati, equivalente vettoriale del controllo R03.

Esclude coppie con almeno un vertice condiviso, come il riferimento; non è una
prova per quelle coppie. Nessuna riparazione o modifica delle mesh.
"""
import numpy as np
from shapely import polygons, intersection, area


def self_intersections_fast(mesh, query_batch=128, pair_batch=12000):
    tri=np.asarray(mesh.triangles);faces=np.asarray(mesh.faces)
    bounds=np.c_[tri.min(axis=1),tri.max(axis=1)]
    tree=mesh.triangles_tree;eps=1e-7;candidates=0;hits=0;examples=[]
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1)
    unit=np.divide(normals,length[:,None],out=np.zeros_like(normals),where=length[:,None]>0)
    def record(ii,jj,mask,kind,areas=None):
        nonlocal hits
        indices=np.flatnonzero(mask);hits+=len(indices)
        for k in indices[:max(0,30-len(examples))]:
            r=dict(faces=[int(ii[k]),int(jj[k])],kind=kind)
            if areas is not None:r['area_projected_mm2']=float(areas[k])
            examples.append(r)
    for start in range(0,len(tri),query_batch):
        end=min(start+query_batch,len(tri));chunk=bounds[start:end]
        try:
            ids,counts=tree.intersection_v(np.ascontiguousarray(chunk[:,:3]),np.ascontiguousarray(chunk[:,3:]))
            ii=np.repeat(np.arange(start,end,dtype=np.int64),counts.astype(np.int64));jj=np.asarray(ids,dtype=np.int64)
        except (ValueError,TypeError):
            rows=[np.asarray(list(tree.intersection(row)),dtype=np.int64) for row in chunk]
            ii=np.repeat(np.arange(start,end,dtype=np.int64),[len(r) for r in rows]);jj=np.concatenate(rows)
        mask=jj>ii;ii,jj=ii[mask],jj[mask]
        shared=(faces[ii,:,None]==faces[jj,None,:]).any(axis=(1,2));ii,jj=ii[~shared],jj[~shared]
        candidates+=len(ii)
        valid=(length[ii]>=eps)&(length[jj]>=eps);ii,jj=ii[valid],jj[valid]
        for pos in range(0,len(ii),pair_batch):
            ai,bj=ii[pos:pos+pair_batch],jj[pos:pos+pair_batch]
            a,b=tri[ai],tri[bj];na,nb=unit[ai],unit[bj]
            parallel=np.linalg.norm(np.cross(na,nb),axis=1)<eps
            coplanar=parallel&(np.max(np.abs(np.einsum('nkj,nj->nk',b-a[:,0,None,:],na)),axis=1)<=eps)
            axes=np.argmax(np.abs(na),axis=1)
            for axis in range(3):
                idx=np.flatnonzero(coplanar&(axes==axis))
                if len(idx):
                    sa,sb=np.delete(a[idx],axis,axis=2),np.delete(b[idx],axis,axis=2)
                    values=area(intersection(polygons(sa),polygons(sb)))
                    record(ai[idx],bj[idx],values>1e-7,'coplanar_overlap',values)
            idx=np.flatnonzero(~parallel)
            if not len(idx):continue
            aa,bb=a[idx],b[idx];crossing=np.zeros(len(idx),dtype=bool)
            for first,second in ((aa,bb),(bb,aa)):
                e1=second[:,1]-second[:,0];e2=second[:,2]-second[:,0]
                for k in range(3):
                    origin=first[:,k];delta=first[:,(k+1)%3]-first[:,k]
                    pv=np.cross(delta,e2);det=np.einsum('ij,ij->i',e1,pv)
                    inv=np.divide(1.,det,out=np.zeros_like(det),where=np.abs(det)>=eps)
                    tv=origin-second[:,0];u=np.einsum('ij,ij->i',tv,pv)*inv
                    q=np.cross(tv,e1);v=np.einsum('ij,ij->i',delta,q)*inv;t=np.einsum('ij,ij->i',e2,q)*inv
                    crossing|=(np.abs(det)>=eps)&(u>=-eps)&(u<=1+eps)&(v>=-eps)&(u+v<=1+eps)&(t>eps)&(t<1-eps)
            record(ai[idx],bj[idx],crossing,'crossing')
    return dict(candidate_pairs_no_shared_vertex=candidates,intersection_pairs=hits,examples=examples,
        algorithm='triangle_pairs_vectorized_v1',
        limitation='Stessi test/tolleranze del riferimento R03: coppie con vertici condivisi escluse; nessuna riparazione automatica.')
