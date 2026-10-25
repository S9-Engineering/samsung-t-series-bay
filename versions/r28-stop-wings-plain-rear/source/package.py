"""Build a local R28 replacement print pack without changing a release.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def local_links(text, names):
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' in target or target.startswith('#'):
            continue
        clean = target.split('#', 1)[0]
        assert clean in names or any(n.startswith(clean.rstrip('/')+'/') for n in names), clean


def main():
    manifest = json.loads((ROOT/'verification/manifest.json').read_text())
    assert manifest['source_sha256'] == sha((ROOT/'source/generate.py').read_bytes())
    assert manifest['parameters_sha256'] == sha((ROOT/'source/parameters.json').read_bytes())
    geometry = json.loads((ROOT/'verification/geometry.json').read_text())
    assert geometry['result'] == 'PASS' and geometry['stop_width_after_mm'] == 83.5
    review = json.loads((ROOT/'verification/visual-review.json').read_text())
    assert review['result'] == 'PASS'
    for name, checksum in review['images_sha256'].items():
        assert sha((ROOT/name).read_bytes()) == checksum, name
    jobs = []
    for path in sorted((ROOT/'verification/slicing').glob('*/job.json')):
        job = json.loads(path.read_text())
        assert job['visual_review_complete'] and job['native_check']['result'] == 'PASS'
        assert job['manifest_sha256'] == sha((ROOT/'verification/manifest.json').read_bytes())
        assert job['geometry_report_sha256'] == sha((ROOT/'verification/geometry.json').read_bytes())
        for key in ['project', 'gcode']:
            assert sha((ROOT/job[key]).read_bytes()) == job[key+'_sha256']
        with zipfile.ZipFile(ROOT/job['project']) as z:
            assert z.testzip() is None
            embedded = next(n for n in z.namelist() if n.endswith('.gcode'))
            assert sha(z.read(embedded)) == job['gcode_sha256']
        jobs.append(job)
    assert {j['name'] for j in jobs} == {'stop', 'lid', 'both'}
    delivery = dict(revision='R28', status='ready_for_printing',
                    replacement_parts_only=True, printable_part_types=2,
                    compatible_shell='R27', material='ELEGOO PLA BASIC',
                    nominal_stop_width_mm=83.5, nominal_clearance_per_side_mm=.25,
                    geometry_report_sha256=sha((ROOT/'verification/geometry.json').read_bytes()),
                    visual_review_sha256=sha((ROOT/'verification/visual-review.json').read_bytes()),
                    jobs=[{k: j[k] for k in ['name', 'project', 'project_sha256', 'gcode', 'gcode_sha256', 'layers', 'totals']} for j in jobs],
                    physical_fit_verified=False, sent_to_printer=False, github_release_created=False,
                    note='Digital preparation completed; the revised physical fit remains to be checked.')
    (ROOT/'verification/delivery.json').write_text(json.dumps(delivery, indent=2)+'\n')

    readme = (ROOT/'README.md').read_text().split('## Editable files and verification')[0]
    readme += ('## License\n\nDesign/documentation: [CC BY-NC-SA 4.0](LICENSE.txt). '
               'Original S9 software: [PolyForm Noncommercial 1.0.0](LICENSE-SOFTWARE.txt). '
               'See [licensing scope](LICENSING.md).\n')
    entries = {'README.md': readme.encode()}
    for pattern in ['print/stl/*.stl', 'print/slicer/*.3mf', 'print/gcode/*.gcode', 'previews/assembly/*.png']:
        for path in sorted(ROOT.glob(pattern)):
            entries[str(path.relative_to(ROOT))] = path.read_bytes()
    for name in ['LICENSE.txt', 'LICENSE-SOFTWARE.txt', 'LICENSING.md']:
        entries[name] = (PROJECT/name).read_bytes()
    local_links(readme, entries)
    local_links(entries['LICENSING.md'].decode(), entries)
    checksums = ''.join(f'{sha(data)}  {name}\n' for name, data in sorted(entries.items()))
    entries['SHA256SUMS.txt'] = checksums.encode()
    target = ROOT/'print/s9-monolith-bay-r28-replacements-print-pack.zip'
    prefix = 's9-monolith-bay-r28-replacements/'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(entries.items()):
            z.writestr(prefix+name, data)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name, data in entries.items():
            assert z.read(prefix+name) == data
        for line in z.read(prefix+'SHA256SUMS.txt').decode().splitlines():
            digest, name = line.split('  ', 1)
            assert sha(z.read(prefix+name)) == digest
    target.with_suffix('.SHA256SUMS.txt').write_text(f'{sha(target.read_bytes())}  {target.name}\n')
    (ROOT/'verification/package.json').write_text(json.dumps(dict(
        result='PASS', file=str(target.relative_to(ROOT)), sha256=sha(target.read_bytes()),
        entries=len(entries), bytes=target.stat().st_size, archive_reopened=True,
        all_member_checksums_verified=True, internal_readme_links_verified=True,
        public_release=False), indent=2)+'\n')
    print(f'R28 print pack verified: {len(entries)} files, {target.stat().st_size} bytes')


if __name__ == '__main__':
    main()
