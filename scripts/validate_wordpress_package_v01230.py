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
  if m.get('releaseVersion')!='0.123.0' or m.get('simulationMonteCarloResearchStudioVersion')!='0.123.0': raise SystemExit('ERROR: version mismatch')
  critical=m.get('wordpressCriticalFiles') or {}
  for rel,expected in critical.items():
   member=ROOT+rel
   if member not in names: raise SystemExit(f'ERROR: missing critical WordPress member: {rel}')
   if digest(z.read(member))!=expected: raise SystemExit(f'ERROR: hash mismatch: {rel}')
  print('PASS: WordPress ZIP integrity'); print('PASS: releaseVersion=0.123.0'); print('PASS: Simulation & Monte Carlo Research Studio=0.123.0'); print(f'PASS: verifiedFileCount={len(critical)}')
if __name__=='__main__': main()
