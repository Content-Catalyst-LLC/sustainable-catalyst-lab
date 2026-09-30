#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

# These paths are development/build state, not shippable plugin source.
SKIP_DIR_NAMES = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "vendor",
}
SKIP_PREFIXES = (
    ".v015208-backup-",
    ".release-backups",
    "dist-v0.152.0.8",
    "sc-lab-v0.152.0.8-artifacts",
)

def shippable_php_files(root: Path):
    for p in sorted(root.rglob("*.php")):
        rel = p.relative_to(root)
        parts = rel.parts
        if any(part in SKIP_DIR_NAMES for part in parts):
            continue
        if any(part.startswith(SKIP_PREFIXES) for part in parts):
            continue
        yield p

issues = []
checked = 0
for p in shippable_php_files(root):
    checked += 1
    data = p.read_bytes()
    rel = p.relative_to(root).as_posix()
    if data.startswith(b"\xef\xbb\xbf"):
        issues.append(f"{rel}: UTF-8 BOM")
        continue
    if not data.startswith(b"<?php"):
        pos = data.find(b"<?php")
        if pos > 0 and not data[:pos].strip():
            issues.append(f"{rel}: {pos} leading whitespace byte(s) before <?php")

if issues:
    print("FAIL - PHP output-safety gate")
    print("\n".join(issues))
    raise SystemExit(1)

print(f"PASS - PHP output-safety gate ({checked} shippable PHP files checked)")
