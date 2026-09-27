#!/usr/bin/env python3
import argparse,hashlib,json,zipfile
ap=argparse.ArgumentParser(); ap.add_argument('zip'); a=ap.parse_args()
with zipfile.ZipFile(a.zip) as z:
 names=set(z.namelist()); prefix='sustainable-catalyst-lab/'; mp=prefix+'build/sc-lab-release-manifest.json'; assert mp in names
 m=json.loads(z.read(mp)); assert m.get('releaseVersion')=='0.135.15.0'; assert m.get('graphStudioVerificationArtifactsVersion')=='0.135.15.0'
 for rel,expected in (m.get('wordpressCriticalFiles') or {}).items():
  name=prefix+rel; assert name in names,name; actual=hashlib.sha256(z.read(name)).hexdigest(); assert actual==expected,(rel,expected,actual)
 bad=[n for n in names if n and not n.startswith(prefix)]; assert not bad,bad[:5]
 print('PASS: WordPress ZIP integrity'); print(f"PASS: verifiedFileCount={len(m['wordpressCriticalFiles'])}"); print('PASS: canonical root sustainable-catalyst-lab/')
