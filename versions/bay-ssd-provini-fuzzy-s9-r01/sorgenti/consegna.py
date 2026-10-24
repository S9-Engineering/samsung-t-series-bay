"""Impacchetta i soli risultati verificati, dopo revisione visiva effettiva."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

def main():
    review=json.loads((ROOT/'verifiche/revisione_visiva.json').read_text())
    job=json.loads((ROOT/'verifiche/slicing/job.json').read_text())
    project=ROOT/job['project'];assert sha(project)==job['project_sha256']==review['project_sha256']
    assert review['reviewed']
    for name,value in review['image_sha256'].items():assert sha(ROOT/name)==value,name
    for name in ['geometria.json','controllo_3mf.json','texture_e_logo.json']:
        assert json.loads((ROOT/'verifiche'/name).read_text())['result']=='PASS',name
    assert len(list((ROOT/'stampa/STL').glob('*.stl')))==5
    assert len(list((ROOT/'stampa/progetti_ElegooSlicer').glob('*.3mf')))==1
    status=dict(status='PRONTO_PER_LA_STAMPA_DEI_PROVINI',revision='R01',physical_printed=False,
        sent_to_printer=False,configuration='ECC2 Combo / ugello 0.4 / PEI testurizzato / ELEGOO PETG PRO',
        printable_objects=5,non_printable_modifiers=3,project=job['project'],project_sha256=sha(project),
        sliced=True,all_layers_reviewed=True,texture_selectivity_checked=True,nominal_logo_relief_mm=0,
        estimates=job['totals'],limits=['Lucentezza e grana non provate fisicamente','Il case R12 non e stato modificato'])
    save(ROOT/'verifiche/STATO_CONSEGNA.json',status)
    files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.zip','.pyc']
        and p.name not in ['SHA256.json','00000.log']]
    hashes={str(p.relative_to(ROOT)):sha(p) for p in files}
    save(ROOT/'verifiche/SHA256.json',hashes)
    archive=ROOT/'PROVINI_FUZZY_S9_R01_CONSEGNA.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files+[ROOT/'verifiche/SHA256.json']:z.write(p,str(p.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(hashes)+1
        for name,value in hashes.items():
            assert hashlib.sha256(z.read(name)).hexdigest()==value
            assert sha(ROOT/name)==value
    print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,members=len(files)+1,sha256=sha(archive)),ensure_ascii=False))

if __name__=='__main__':main()
