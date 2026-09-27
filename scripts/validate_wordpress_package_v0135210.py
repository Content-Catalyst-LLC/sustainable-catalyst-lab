#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,zipfile
ROOT='sustainable-catalyst-lab/';MANIFEST=ROOT+'build/sc-lab-release-manifest.json'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('zip');a=ap.parse_args()
 with zipfile.ZipFile(a.zip) as z:
  names=set(z.namelist());m=json.loads(z.read(MANIFEST));assert m.get('releaseVersion')=='0.135.21.0';assert m.get('graphStudioReviewWorkspaceConsolidationVersion')=='0.135.21.0'
  for rel,expected in m['wordpressCriticalFiles'].items():
   name=ROOT+rel;assert name in names,name;assert hashlib.sha256(z.read(name)).hexdigest()==expected,rel
 print(f"PASS: v0.135.21.0 WordPress package validates ({len(m['wordpressCriticalFiles'])} critical files)")
if __name__=='__main__':main()
