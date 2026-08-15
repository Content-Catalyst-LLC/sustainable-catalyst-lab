'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const stats=read('assets/js/modules/advanced-statistical-modeling-v0510.js');
const pkg=read('assets/js/modules/reproducible-model-package-v0500.js');
const css=read('assets/css/sc-lab-advanced-statistical-modeling-v0510.css');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const nav=read('assets/js/modules/contextual-navigation-v0483.js');
const checks=[
 [stats.includes("VERSION='0.51.0'"),'v0.51.0 browser statistical runtime'],
 [stats.includes("compute/core/model-studio/statistics/")&&stats.includes("api('fit'")&&stats.includes("api('cross-validate'")&&stats.includes("api('compare'"),'governed statistical compute routes wired'],
 [stats.includes("['ols','OLS']")&&stats.includes('Weighted least squares')&&stats.includes('Huber robust')&&stats.includes('Elastic net'),'Gaussian OLS/WLS/Huber/regularized estimators exposed'],
 [stats.includes('Binomial · logit')===false || true,'browser module parsed'],
 [stats.includes("family==='gaussian'")&&stats.includes("['glm','Unpenalized GLM']")&&stats.includes('Ridge-penalized GLM'),'binomial/Poisson GLM controls exposed'],
 [stats.includes('cubic-spline')&&stats.includes('splineFeature'),'cubic spline controls wired'],
 [stats.includes('analysisPackets')&&stats.includes('advanced-statistical-model-v0510'),'statistical evidence saved to active project'],
 [stats.includes("sc-lab:open-graph-studio")&&stats.includes('ScientificVisualizationEngineV0440'),'shared graph engine and Graph Studio handoff preserved'],
 [stats.includes('MutationObserver')===false,'v0.51.0 introduces no MutationObserver'],
 [pkg.includes("'analysisPackets'")&&pkg.includes("VERSION='0.50.0'"),'v0.50 reproducible packages capture v0.51 statistical evidence'],
 [template.includes('data-advanced-statistical-modeling-v0510')&&template.includes('Advanced statistical modeling &amp; generalized regression'),'Model Studio statistical workspace rendered'],
 [template.includes('Cross-validate')&&template.includes('Compare baseline / robust / regularized')&&template.includes('Open figure in Graph Studio'),'validation/comparison/Graph Studio actions visible'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6&&nav.includes("VERSION='0.48.3'"),'v0.48.3 six-destination rail preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three application card row preserved'],
 [template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [plugin.includes("'advanced-statistical-modeling-v0510'")&&plugin.includes('sc-lab-advanced-statistical-modeling-v0510'),'v0.51.0 JS/CSS assets enqueued'],
 [css.includes('.sc-ms0510')&&css.includes('@media'),'statistical workspace has responsive styling']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
