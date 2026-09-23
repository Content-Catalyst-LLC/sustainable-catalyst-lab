from pathlib import Path
import json,re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
required=['sustainable-catalyst-lab.php','includes/class-sc-lab-global-science-v0280.php','assets/js/modules/global-science-lab-v0280.js','assets/css/sc-lab-global-science-v0280.css','contracts/global-science-laboratory-v0280.json','backend/app/global_science_v0280.py','tests/test-v0280.php','tests/test-v0280.js']
missing=[x for x in required if not (root/x).is_file()]
if missing: raise SystemExit('Missing v0.28.0 files: '+', '.join(missing))
main=(root/'sustainable-catalyst-lab.php').read_text(errors='replace')
if not re.search(r'^\s*\*\s*Version:\s*0\.28\.0\s*$',main,re.M): raise SystemExit('Plugin header is not v0.28.0')
if 'class-sc-lab-global-science-v0280.php' not in main: raise SystemExit('Global science bootstrap is missing')
contract=json.loads((root/'contracts/global-science-laboratory-v0280.json').read_text())
assert contract['version']=='0.28.0' and contract['freeSourceOnly'] is True
php=(root/'includes/class-sc-lab-global-science-v0280.php').read_text()
for marker in ('SC_LAB_PLATFORM_CORE_URL','SC_LAB_PLATFORM_CORE_PUBLIC_API_KEY','/api/v1/science/records','/api/v1/stac/search','credentials_embedded'):
    if marker not in php: raise SystemExit('Missing marker: '+marker)
print('Sustainable Catalyst Lab v0.28.0 release contract passed.')
