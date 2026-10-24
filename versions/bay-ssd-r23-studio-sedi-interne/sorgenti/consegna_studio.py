"""Consegna dello studio comparativo R23, senza promozione a file di stampa."""
import json,hashlib,zipfile
import genera as g
ROOT=g.ROOT
def read(n):return json.loads((ROOT/n).read_text())
def main():
 m=read('verifiche/manifest.json');v=read('verifiche/controlli_studio.json');a=read('verifiche/anteprime.json');review=read('verifiche/revisione_visiva.json')
 assert m['source_sha256']==g.sha(ROOT/'sorgenti/genera.py') and m['parameters_sha256']==g.sha(ROOT/'sorgenti/parametri.json')
 assert v['manifest_sha256']==a['manifest_sha256']==g.sha(ROOT/'verifiche/manifest.json')
 assert v['not_print_ready'] and len(v['ssd_cases'])==27 and len(v['base_motion_samples'])==108 and len(v['base_vertical_motion_samples'])==108
 assert len(m['parts'])==15 and len(v['parts'])==15 and len(v['assemblies'])==3
 for p in m['parts']:
  assert g.sha(ROOT/p['step'])==p['sha256'] and g.sha(ROOT/p['mesh'])==p['mesh_sha256']
  assert '.MILLI.,.METRE.' in (ROOT/p['step']).read_text()
 assert a['images']==review['images'] and len(a['images'])==3
 for n,h in a['images'].items():assert g.sha(ROOT/n)==h
 assert not [p for p in ROOT.rglob('*') if p.suffix.lower() in ['.stl','.3mf','.gcode']]
 state=dict(revision=g.P['revisione'],state='STUDIO_COMPARATIVO_A_B_C_DA_SCEGLIERE',not_print_ready=True,nominal_geometry_checked=True,models_per_slot=27,source_editable=True,step_export_reopened=True,cad_images_reviewed=True,slicing_performed=False,physical_print=False,physical_fit=False,force_validated=False,thermal_test=False,recommendation='B se accettato caricamento della cartuccia fuori dal case; A se prioritario inserimento diretto dall alto.',preserved_roof_design='R22',full_r22_kit_under_redesign=True,limitations=v['limitations'])
 g.save(ROOT/'verifiche/STATO_STUDIO.json',state)
 hh={str(p.relative_to(ROOT)):g.sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name not in ['SHA256.json','.DS_Store'] and p.suffix!='.zip' and '__pycache__' not in p.parts}
 g.save(ROOT/'verifiche/SHA256.json',hh);archive=ROOT/'BAY_R23_STUDIO_SEDI_A_B_C_NON_STAMPARE.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for n in [*hh,'verifiche/SHA256.json']:z.write(ROOT/n,ROOT.name+'/'+n)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for n,h in hh.items():assert hashlib.sha256(z.read(ROOT.name+'/'+n)).hexdigest()==h
 print(json.dumps(dict(state=state['state'],files=len(hh)+1,archive=str(archive))),flush=True)
if __name__=='__main__':main()
