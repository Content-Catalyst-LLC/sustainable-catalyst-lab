#!/usr/bin/env python3
import sys,zipfile
from pathlib import Path
p=Path(sys.argv[1])
with zipfile.ZipFile(p) as z:
 names=z.namelist(); assert names and all(n.startswith('sustainable-catalyst-lab/') for n in names); assert 'sustainable-catalyst-lab/sustainable-catalyst-lab.php' in names; assert 'sustainable-catalyst-lab/assets/js/modules/graph-studio-object-explorer-v013590.js' in names; assert 'sustainable-catalyst-lab/build/sc-lab-release-manifest.json' in names
print(f'PASS - canonical WordPress package {len(names)} members')
