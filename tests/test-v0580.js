'use strict';
const fs=require('fs');const read=p=>fs.readFileSync(p,'utf8');
const js=read('assets/js/modules/scientific-compute-hardening-v0580.js');
const py=read('backend/app/scientific_compute_hardening.py');
const main=read('backend/app/main.py');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const compute=read('includes/class-sc-lab-python-compute-core-v0261.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [js.includes("VERSION='0.58.0'")&&js.includes('ScientificComputeHardeningV0580'),'v0.58 browser contract'],
 [py.includes('ScientificComputeManager')&&py.includes('ThreadPoolExecutor'),'bounded asynchronous compute manager implemented'],
 [py.includes('result_cache')&&py.includes('cache_key')&&py.includes('cacheHit'),'deterministic persistent result cache implemented'],
 [py.includes('assess_workload')&&py.includes('async-recommended')&&py.includes('hardLimits'),'workload assessment and hard limits implemented'],
 [py.includes('dataset_window')&&py.includes('limit = _safe_int'),'bounded dataset window backend implemented'],
 [py.includes('cancellation-requested')&&py.includes('cancelled-after-completion'),'cooperative cancellation states implemented'],
 [py.includes('forceTerminateRunningScientificCode')&&py.includes('arbitraryCodeExecution'),'unsafe force termination and arbitrary code disabled'],
 [main.includes('/v1/compute-hardening/v0580/jobs')&&main.includes('/v1/compute-hardening/v0580/cache'),'FastAPI v0.58 jobs/cache routes implemented'],
 [template.includes('data-compute-hardening-v0580')&&template.includes('Queue workflow asynchronously'),'compute hardening integrated contextually'],
 [js.includes("operation:'workflow.run'")&&js.includes('setTimeout'),'async workflow submission and bounded polling implemented'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes('sc-lab-scientific-compute-hardening-v0580')&&plugin.includes("'scientific-compute-hardening-v0580'"),'v0.58 assets registered'],
 [compute.includes('/compute/core/compute-hardening/v0580/jobs')&&compute.includes('/compute/core/compute-hardening/v0580/cache'),'WordPress v0.58 compute proxies registered'],
 [!js.includes('MutationObserver'),'v0.58 introduces no MutationObserver']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
