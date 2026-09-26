#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,pathlib,zipfile
MANIFEST_REL=pathlib.Path("build/sc-lab-release-manifest.json"); ROOT_NAME="sustainable-catalyst-lab"
def sha256(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--output",required=True); a=ap.parse_args(); repo=pathlib.Path(a.repo).resolve(); out=pathlib.Path(a.output).resolve(); m=json.loads((repo/MANIFEST_REL).read_text())
 if m.get("releaseVersion")!="0.135.11.0" or m.get("graphStudioCompetingPathsVersion")!="0.135.11.0": raise SystemExit("ERROR: v0.135.11.0 version mismatch")
 critical=m.get("wordpressCriticalFiles") or {}; errors=[]
 for rel,expected in sorted(critical.items()):
  p=repo/rel
  if not p.is_file(): errors.append(f"MISSING {rel}")
  elif sha256(p)!=expected: errors.append(f"HASH {rel}")
 if errors: print("\n".join(errors[:50])); raise SystemExit(1)
 out.parent.mkdir(parents=True,exist_ok=True); out.unlink(missing_ok=True)
 with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  def add(rel,b):
   zi=zipfile.ZipInfo(f"{ROOT_NAME}/{rel}",(1980,1,1,0,0,0)); zi.external_attr=(0o100644<<16); zi.compress_type=zipfile.ZIP_DEFLATED; z.writestr(zi,b)
  add(MANIFEST_REL.as_posix(),(repo/MANIFEST_REL).read_bytes())
  for rel in sorted(critical): add(rel,(repo/rel).read_bytes())
 print(f"PASS: built {out}"); print(f"PASS: packaged {len(critical)} manifest-critical WordPress files + canonical manifest")
if __name__=="__main__": main()
