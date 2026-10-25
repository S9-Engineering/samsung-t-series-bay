"""Release numbering and artifact-integrity regression checks.

SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
Required Notice: S9 Engineering (https://github.com/S9-Engineering)
"""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('print_release',ROOT/'source/release.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class ReleaseChecks(unittest.TestCase):
    def test_next_patch_and_explicit_major_minor(self):
        self.assertEqual(r.next_version('1.0.1',['v1.0.0']),'1.0.1')
        self.assertEqual(r.next_version('1.0.1',['v1.0.0','v1.0.1']),'1.0.2')
        self.assertEqual(r.next_version('1.1.0',['v1.0.9']),'1.1.0')
        self.assertEqual(r.next_version('2.0.0',['v1.9.9']),'2.0.0')
        self.assertEqual(r.next_version('1.0.0',['old-snapshot','v1.2.3-rc.1']),'1.0.0')

    def test_real_stl_corruption_blocks_a_release(self):
        manifest=json.loads((ROOT/'verification/manifest.json').read_text())
        with tempfile.TemporaryDirectory(prefix='s9-release-regression-') as td:
            dest=Path(td)
            shutil.copytree(ROOT/'source',dest/'source',ignore=shutil.ignore_patterns('__pycache__'))
            (dest/'verification').mkdir()
            shutil.copyfile(ROOT/'VERSION',dest/'VERSION')
            shutil.copyfile(ROOT/'verification/manifest.json',dest/'verification/manifest.json')
            first=manifest['parts'][0]
            for key in ['step','print_step','stl']:
                path=dest/first[key];path.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/first[key],path)
            with (dest/first['stl']).open('ab') as f:f.write(b'changed after verification')
            with self.assertRaisesRegex(AssertionError,'Changed export'):
                r.verify_assets(dest)

    def test_self_consistent_zip_with_stale_stl_is_rejected(self):
        with zipfile.ZipFile(ROOT/r.ASSETS[0]) as z:
            entries={n:z.read(n) for n in z.namelist()}
        entries['print/stl/cartridge-stop.stl']+=b'changed after packaging'
        entries['SHA256SUMS.txt']=''.join(
            r.hashlib.sha256(data).hexdigest()+'  '+name+'\n'
            for name,data in sorted(entries.items()) if name!='SHA256SUMS.txt').encode()
        with tempfile.TemporaryDirectory(prefix='s9-archive-regression-') as td:
            path=Path(td)/'stale-print-pack.zip'
            with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
                for name,data in entries.items():z.writestr(name,data)
            with self.assertRaisesRegex(AssertionError,'Stale archived file'):
                r.verify_zip(path)

if __name__=='__main__':unittest.main()
