#!/usr/bin/env python3
"""Build the slim Sustainable Catalyst Lab v0.100.0 WordPress runtime package."""
from __future__ import annotations
import argparse, zipfile
from pathlib import Path
ROOT_NAME="sustainable-catalyst-lab"
RUNTIME_TREES=("assets","includes","templates","contracts")
def eligible(rel:Path)->bool:
    parts=set(rel.parts)
    if "__pycache__" in parts or ".pytest_cache" in parts or ".venv" in parts: return False
    if rel.suffix==".pyc": return False
    text=rel.as_posix()
    return not text.startswith("data/") and not text.startswith("backend/data/")
def collect_files(root:Path)->list[Path]:
    files=set()
    for rel in ("sustainable-catalyst-lab.php","LICENSE","build/sc-lab-release-manifest.json"):
        p=root/rel
        if p.is_file(): files.add(p)
    for tree in RUNTIME_TREES:
        base=root/tree
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file() and eligible(p.relative_to(root)): files.add(p)
    return sorted(files,key=lambda p:p.relative_to(root).as_posix())
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default=str(Path(__file__).resolve().parents[1])); ap.add_argument("--output",required=True); a=ap.parse_args()
    root=Path(a.root).resolve(); out=Path(a.output).resolve(); files=collect_files(root); rels={p.relative_to(root).as_posix() for p in files}
    required={
      "sustainable-catalyst-lab.php","build/sc-lab-release-manifest.json","assets/data/elements.json",
      "assets/js/modules/carbon-mrv-reporting-v01000.js","assets/css/sc-lab-carbon-mrv-reporting-v01000.css",
      "includes/class-sc-lab-carbon-mrv-reporting-v01000.php",
      "contracts/carbon-mrv-report-v1700.schema.json","contracts/carbon-mrv-report-validation-v1700.schema.json",
      "contracts/carbon-mrv-audit-packet-v1700.schema.json","contracts/carbon-mrv-reporting-policy-v1700.json",
    }
    missing=sorted(required-rels)
    if missing: raise SystemExit("ERROR: required WordPress runtime files missing: "+", ".join(missing))
    forbidden=[r for r in rels if r.startswith(("backend/","tests/","scripts/","docs/","sdk/","examples/"))]
    if forbidden: raise SystemExit("ERROR: repository-only files leaked into WordPress runtime package")
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists(): out.unlink()
    total=0
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for p in files:
            rel=p.relative_to(root).as_posix(); total+=p.stat().st_size; zf.write(p,f"{ROOT_NAME}/{rel}")
    print(f"WORDPRESS_RUNTIME_FILE_COUNT={len(files)}"); print(f"WORDPRESS_RUNTIME_UNCOMPRESSED_BYTES={total}"); print(f"WORDPRESS_RUNTIME_ZIP_BYTES={out.stat().st_size}"); print(f"WORDPRESS_RUNTIME_ZIP={out}"); return 0
if __name__=="__main__": raise SystemExit(main())
