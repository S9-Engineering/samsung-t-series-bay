"""Validate, version and publish the current print kit on an authorized main push.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
ASSETS=['packages/monolith-bay-print-pack.zip','packages/SHA256SUMS.txt']
VERSION_RE=re.compile(r'^(\d+)\.(\d+)\.(\d+)$')


def run(args, *, check=True, root=ROOT):
    return subprocess.run(args,cwd=root,capture_output=True,text=True,check=check)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path,root=ROOT):
    return json.loads((root/path).read_text())


def version_tuple(value):
    m=VERSION_RE.fullmatch(value.removeprefix('v'))
    if not m:raise ValueError('Expected MAJOR.MINOR.PATCH: '+value)
    return tuple(map(int,m.groups()))


def next_version(requested,tags):
    requested=version_tuple(requested)
    versions=[version_tuple(t) for t in tags if VERSION_RE.fullmatch(t.removeprefix('v'))]
    if not versions:return '.'.join(map(str,requested))
    latest=max(versions)
    if requested<=latest:requested=(*latest[:2],latest[2]+1)
    return '.'.join(map(str,requested))


def verify_assets(root=ROOT):
    """Reuse geometry/slicer evidence only for byte-identical inputs/outputs."""
    if (root/'.git').exists():
        assert not run(['git','ls-files','publication-local'],root=root).stdout.strip(),'Portal files must stay local'
    version_tuple((root/'VERSION').read_text().strip())
    manifest=read('verification/manifest.json',root)
    assert manifest['source_sha256']==sha(root/'source/generate.py'),'Stale CAD generator evidence'
    assert manifest['parameters_sha256']==sha(root/'source/parameters.json'),'Stale CAD parameter evidence'
    assert manifest.get('geometry_inputs_sha256'),'Missing CAD input inventory'
    for path,digest in manifest['geometry_inputs_sha256'].items():
        assert sha(root/path)==digest,'Stale CAD input: '+path
    assert len(manifest['parts'])==7 and sum(p['quantity'] for p in manifest['parts'])==8
    for part in manifest['parts']:
        for kind in ['step','print_step','stl']:
            assert sha(root/part[kind])==part['sha256'][kind],'Changed export: '+part[kind]
    geometry=read('verification/geometry.json',root)
    assert geometry['result']=='PASS'
    assert geometry['manifest_sha256']==sha(root/'verification/manifest.json'),'Stale geometry report'
    assert len(geometry['parts'])==7
    review=read('verification/visual-review.json',root)
    assert review['result']=='PASS'
    for path,digest in review['images_sha256'].items():
        assert sha(root/path)==digest,'Changed reviewed preview: '+path
    provenance=read('verification/profile-provenance.json',root)
    assert 'project.json' in provenance['saved_profiles']
    for name,digest in provenance['saved_profiles'].items():
        assert sha(root/'source/profiles'/name)==digest,'Changed slicer profile: '+name
    for name,count in [('full-kit',8),('stop',1),('lid',1),('both',2)]:
        job=read(f'verification/slicing/{name}/job.json',root)
        assert job['visual_review_complete'] and job['native_check']['result']=='PASS'
        assert job['native_check']['printable_count']==count
        assert job['manifest_sha256']==sha(root/'verification/manifest.json')
        assert job['geometry_report_sha256']==sha(root/'verification/geometry.json')
        for key in ['project','gcode']:
            assert sha(root/job[key])==job[key+'_sha256'],'Changed print file: '+job[key]
        with zipfile.ZipFile(root/job['project']) as z:
            assert z.testzip() is None
            model=ET.fromstring(z.read('3D/3dmodel.model'))
            assert model.get('unit')=='millimeter'
            member=next(n for n in z.namelist() if n.endswith('.gcode'))
            assert hashlib.sha256(z.read(member)).hexdigest()==job['gcode_sha256']
    print('CAD, STL, STEP, native 3MF, embedded G-code and saved review evidence: PASS',flush=True)


def verify_zip(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        names=set(z.namelist())
        assert {'README.md','LICENSE.txt','LICENSE-SOFTWARE.txt','LICENSING.md','SHA256SUMS.txt'}<=names
        version=(ROOT/'VERSION').read_text().strip()
        assert 'v'+version+' print pack' in z.read('README.md').decode(),'Package version differs from VERSION'
        assert not any(n.startswith(('source/','cad/','verification/','publication-local/','versions/')) for n in names)
        checked=set()
        for line in z.read('SHA256SUMS.txt').decode().splitlines():
            digest,name=line.split('  ',1)
            assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
            checked.add(name)
        assert checked==names-{'SHA256SUMS.txt'},'Incomplete archive checksums'
        recipe=read('packages/recipe.json')
        assert recipe['version']==version,'Stale package recipe'
        assert {p['archive'] for p in recipe['files']}==checked,'Archive differs from package recipe'
        for entry in recipe['files']:
            expected=(ROOT/entry['source']).read_bytes()
            if entry.get('transformation'):
                assert entry['source']=='packages/README.md' and entry['archive']=='README.md'
                expected=re.sub(r'\]\(\.\./([^)]+)\)',r'](\1)',expected.decode()).encode()
            assert z.read(entry['archive'])==expected,'Stale archived file: '+entry['archive']
        checksum=(ROOT/ASSETS[1]).read_text().strip()
        assert checksum==sha(path)+'  '+Path(ASSETS[0]).name,'Archive checksum differs'
        for target in re.findall(r'\]\(([^)]+)\)',z.read('README.md').decode()):
            if '://' not in target and not target.startswith('#'):
                assert target in names or any(n.startswith(target.rstrip('/')+'/') for n in names),target


def output_ready(value):
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('ready='+str(value).lower()+'\n')


def prepare(event_sha):
    repository=read('.3dcook.json')['repository']
    remote=run(['git','ls-remote','origin','refs/heads/main']).stdout.split()[0]
    if remote!=event_sha:
        run(['git','fetch','origin','main'])
        body=run(['git','show','-s','--format=%B',remote]).stdout
        if 'Release-Source: '+event_sha not in body:
            print('A newer main push superseded this run.');output_ready(False);return
        run(['git','checkout','--detach',remote])
        verify_assets()
        output_ready(True);return
    verify_assets()
    tags=run(['git','tag','--list','v*']).stdout.split()
    current=(ROOT/'VERSION').read_text().strip()
    current_tag=run(['git','rev-parse','v'+current+'^{commit}'],check=False)
    if current_tag.returncode==0 and current_tag.stdout.strip()==remote:
        print('This exact version/commit is already tagged; resume publication if needed.')
        output_ready(True);return
    version=next_version(current,tags)
    (ROOT/'VERSION').write_text(version+'\n')
    readme=(ROOT/'README.md').read_text()
    readme=re.sub(r'(?s)(<!-- project-version:start -->).*?(<!-- project-version:end -->)',
                  lambda m:m[1]+'\n**Version v'+version+' · PLA · 8 printed components**\n'+m[2],readme)
    (ROOT/'README.md').write_text(readme)
    changelog=ROOT/'CHANGELOG.md'
    text=changelog.read_text() if changelog.exists() else '# Changelog\n\n'
    if '\n## v'+version+'\n' not in text:
        previous=max((t for t in tags if VERSION_RE.fullmatch(t.removeprefix('v'))),key=version_tuple,default=None)
        args=['git','log','--format=%s',previous+'..HEAD' if previous else 'HEAD']
        messages=[m for m in run(args).stdout.splitlines() if not m.startswith('chore: release v')]
        block='## v'+version+'\n\n'+''.join('- '+m+'\n' for m in messages)+'\n'
        text=text.replace('# Changelog\n\n','# Changelog\n\n'+block,1)
        changelog.write_text(text)
    run(['python3','source/build_package.py'])
    verify_zip(ROOT/ASSETS[0])
    dirty=run(['git','ls-files','publication-local']).stdout.strip()
    assert not dirty,'Local portal files must never be versioned'
    allowed=['VERSION','README.md','CHANGELOG.md','packages','verification/package.json']
    run(['git','add','--',*allowed])
    if run(['git','diff','--cached','--quiet'],check=False).returncode:
        run(['git','config','user.name','github-actions[bot]'])
        run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'])
        run(['git','commit','-m','chore: release v'+version,'-m','Release-Source: '+event_sha])
        run(['git','push','origin','HEAD:main'])
    print('Prepared v'+version+' for '+repository,flush=True)
    output_ready(True)


def notes(version):
    text=(ROOT/'CHANGELOG.md').read_text()
    match=re.search(r'(?ms)^## v'+re.escape(version)+r'\n(.*?)(?=^## |\Z)',text)
    changes=match[1].strip() if match else 'Updated project files and printing instructions.'
    return (f'# S9 Monolith Bay v{version}\n\n'
            'DIY 3D-printable SSD enclosure for Samsung T7, T7 Shield and T9. '
            'Download **monolith-bay-print-pack.zip** under Assets for STL, native 3MF, '
            'setup-specific G-code and illustrated assembly instructions.\n\n'+changes+'\n\n'
            'The shell, cartridges and both pins from v1.0.0 remain compatible. '
            'Native profiles use ELEGOO Centauri Carbon 2 Combo / 0.4 mm / textured PEI / PLA BASIC. '
            'Geometry and slicing are digitally checked; full-kit physical endurance and thermal validation are not claimed. '
            'Designs/documentation: CC BY-NC-SA 4.0; original S9 software: PolyForm Noncommercial 1.0.0.\n')


def publish():
    verify_assets();verify_zip(ROOT/ASSETS[0])
    version=(ROOT/'VERSION').read_text().strip();tag='v'+version
    repository=read('.3dcook.json')['repository'];head=run(['git','rev-parse','HEAD']).stdout.strip()
    run(['git','config','user.name','github-actions[bot]'])
    run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'])
    existing=run(['git','rev-parse',tag+'^{commit}'],check=False)
    if existing.returncode==0:assert existing.stdout.strip()==head,'An existing tag points to another commit'
    else:
        remote=run(['git','ls-remote','origin','refs/heads/main']).stdout.split()[0]
        assert remote==head,'Main changed before tagging; do not publish a stale snapshot'
        run(['git','tag','-a',tag,'-m','S9 Monolith Bay '+tag,head])
        run(['git','push','origin',tag])
    remote_tag=run(['git','ls-remote','origin','refs/tags/'+tag+'^{}']).stdout.split()
    assert remote_tag and remote_tag[0]==head,'Remote annotated tag differs from the intended commit'
    details=run(['gh','release','view',tag,'--repo',repository,'--json','isDraft,tagName,assets,url'],check=False)
    cache=ROOT/'.cache/release';cache.mkdir(parents=True,exist_ok=True)
    note_file=cache/'notes.md';note_file.write_text(notes(version))
    if details.returncode:
        assert 'release not found' in details.stderr.lower(),details.stderr
        run(['gh','release','create',tag,*ASSETS,'--repo',repository,'--verify-tag','--draft',
             '--title',tag+' — S9 Monolith Bay: DIY 3D-Printable Samsung SSD Enclosure','--notes-file',str(note_file)])
    else:
        info=json.loads(details.stdout)
        present={a['name'] for a in info['assets']}
        assert present<={Path(p).name for p in ASSETS},'Unexpected assets already attached to this version'
        missing=[p for p in ASSETS if Path(p).name not in present]
        assert info['isDraft'] or not missing,'Published releases are immutable'
        if missing:run(['gh','release','upload',tag,*missing,'--repo',repository])
    with tempfile.TemporaryDirectory(prefix='s9-release-check-') as td:
        run(['gh','release','download',tag,'--repo',repository,'--dir',td])
        for name in ASSETS:assert sha(Path(td)/Path(name).name)==sha(ROOT/name),'Remote release asset differs'
        verify_zip(Path(td)/Path(ASSETS[0]).name)
    info=json.loads(run(['gh','release','view',tag,'--repo',repository,'--json','isDraft,tagName,assets,url']).stdout)
    if info['isDraft']:run(['gh','release','edit',tag,'--repo',repository,'--draft=false','--latest'])
    final=json.loads(run(['gh','release','view',tag,'--repo',repository,'--json','isDraft,tagName,url']).stdout)
    assert not final['isDraft'] and final['tagName']==tag
    print(json.dumps(dict(version=version,commit=head,url=final['url'],published=True,downloaded_assets_verified=True)),flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['check','prepare','publish']);p.add_argument('--event-sha');args=p.parse_args()
    if args.command=='check':verify_assets();verify_zip(ROOT/ASSETS[0])
    elif args.command=='prepare':
        assert args.event_sha,'prepare requires the exact triggering commit';prepare(args.event_sha)
    else:publish()

if __name__=='__main__':main()
