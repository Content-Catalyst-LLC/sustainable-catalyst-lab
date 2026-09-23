#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,zipfile
ROOT='sustainable-catalyst-lab/'; MANIFEST=ROOT+'build/sc-lab-release-manifest.json'
def digest(b): return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('zip_path'); a=ap.parse_args()
 with zipfile.ZipFile(a.zip_path) as z:
  bad=z.testzip()
  if bad: raise SystemExit(f'ERROR: corrupt ZIP member: {bad}')
  names=[n for n in z.namelist() if not n.endswith('/')]
  if not names or any(not n.startswith(ROOT) for n in names): raise SystemExit('ERROR: invalid WordPress plugin root')
  m=json.loads(z.read(MANIFEST))
  if m.get('releaseVersion')!='0.111.0': raise SystemExit('ERROR: releaseVersion is not 0.111.0')
  if m.get('platformCoreMinimumVersion')!='3.0.0': raise SystemExit('ERROR: stale Platform Core minimum requirement')
  if m.get('platformCoreScientificInvestigationRuntimeVersion')!='0.111.0': raise SystemExit('ERROR: scientific-investigation bridge version mismatch')
  critical=m.get('wordpressCriticalFiles') or {}
  for rel,expected in sorted(critical.items()):
   member=ROOT+rel
   if member not in names: raise SystemExit(f'ERROR: missing {rel}')
   if digest(z.read(member))!=expected: raise SystemExit(f'ERROR: hash mismatch {rel}')
  if len(names)!=len(critical)+1: raise SystemExit(f'ERROR: file count {len(names)} != {len(critical)+1}')
  print('PASS: WordPress ZIP integrity'); print('PASS: releaseVersion=0.111.0'); print('PASS: Platform Core minimum release=3.0.0'); print('PASS: scientific investigation runtime integration version=0.111.0'); print(f'PASS: verifiedFileCount={len(critical)}')
if __name__=='__main__': main()
