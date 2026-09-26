#!/usr/bin/env python3
import argparse,hashlib,json,zipfile
ROOT='sustainable-catalyst-lab/'; MANIFEST=ROOT+'build/sc-lab-release-manifest.json'
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('zip_path'); a=ap.parse_args()
 with zipfile.ZipFile(a.zip_path) as z:
  if z.testzip(): raise SystemExit('ERROR: corrupt ZIP')
  names=z.namelist();
  if not names or any(not n.startswith(ROOT) for n in names): raise SystemExit('ERROR: non-canonical WordPress ZIP root')
  m=json.loads(z.read(MANIFEST));
  if m.get('releaseVersion')!='0.135.8.5.3' or m.get('graphStudioContextRelationshipsVersion')!='0.135.8.5.3': raise SystemExit('ERROR: version mismatch')
  for rel,expected in (m.get('wordpressCriticalFiles') or {}).items():
   b=z.read(ROOT+rel)
   if hashlib.sha256(b).hexdigest()!=expected: raise SystemExit(f'ERROR: hash mismatch {rel}')
  print('PASS: WordPress ZIP integrity'); print(f"PASS: verifiedFileCount={len(m['wordpressCriticalFiles'])}"); print('PASS: canonical root sustainable-catalyst-lab/')
if __name__=='__main__': main()
