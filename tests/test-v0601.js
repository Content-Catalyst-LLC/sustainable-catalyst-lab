'use strict';
const fs=require('fs');const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/beta-field-diagnostics-v0601.js');
const py=read('backend/app/beta_field_diagnostics_v0601.py');
const main=read('backend/app/main.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [js.includes("VERSION='0.60.1'")&&js.includes('BetaFieldDiagnosticsV0601'),'v0.60.1 browser diagnostics contract'],
 [py.includes('normalize_runtime_snapshot')&&py.includes('integration_probe')&&py.includes('analyze_soak'),'field diagnostics backend implemented'],
 [py.includes('rawScientificDataAccepted')&&py.includes('automaticRepairAuthorized'),'metadata-only / no automatic repair boundary'],
 [py.includes('externalTelemetryAuthorized')&&py.includes('backgroundMonitoringAuthorized'),'external telemetry/background monitoring disabled'],
 [main.includes('/v1/beta-diagnostics/v0601/probe')&&main.includes('/v1/beta-diagnostics/v0601/soak')&&main.includes('/v1/beta-diagnostics/v0601/packet'),'FastAPI v0.60.1 diagnostics routes implemented'],
 [template.includes('data-beta-field-diagnostics-v0601')&&template.includes('Run bounded integration soak'),'contextual beta diagnostics UI present'],
 [js.includes("recordType:'beta-field-diagnostics-v0601'")&&js.includes("s.add('analysisPackets'"),'diagnostic evidence saves to active project'],
 [js.includes("const soakEndpoints")&&js.includes("cycle<=4")&&js.includes("Promise.all"),'bounded browser round-trip soak implemented'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-beta-field-diagnostics-v0601')&&plugin.includes("'beta-field-diagnostics-v0601'"),'v0.60.1 assets registered'],
 [compute.includes('/compute/core/beta-diagnostics/v0601/probe')&&compute.includes('/compute/core/beta-diagnostics/v0601/soak'),'WordPress v0.60.1 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.60.1 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
