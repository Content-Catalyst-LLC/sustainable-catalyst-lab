#!/usr/bin/env python3
import argparse,json,hashlib,zipfile
ap=argparse.ArgumentParser();ap.add_argument('zip');a=ap.parse_args()
with zipfile.ZipFile(a.zip) as z:
 mp='sustainable-catalyst-lab/build/sc-lab-release-manifest.json';m=json.loads(z.read(mp));assert m.get('releaseVersion')=='0.135.18.0';assert m.get('graphStudioMultiReviewerPanelsVersion')=='0.135.18.0'
 for rel,exp in m.get('wordpressCriticalFiles',{}).items():
  data=z.read('sustainable-catalyst-lab/'+rel);assert hashlib.sha256(data).hexdigest()==exp,rel
 print(f"PASS: WordPress package integrity ({len(m.get('wordpressCriticalFiles',{}))} critical files)")
