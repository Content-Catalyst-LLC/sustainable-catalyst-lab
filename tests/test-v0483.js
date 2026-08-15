'use strict';
const fs=require('fs'); const read=p=>fs.readFileSync(p,'utf8');
const ui=read('assets/js/modules/contextual-navigation-v0483.js');
const css=read('assets/css/sc-lab-contextual-navigation-v0483.css');
const template=read('templates/lab-app.php');
const plugin=read('includes/class-sc-lab-plugin.php');
const runtime=read('assets/js/modules/presentation-runtime-v0482.js');
const checks=[
 [ui.includes("VERSION='0.48.3'")&&ui.includes('ContextualNavigationV0483'),'v0.48.3 browser navigation contract'],
 [ui.includes('MutationObserver')===false,'no MutationObserver introduced by v0.48.3'],
 [(template.match(/data-v0483-primary=/g)||[]).length===6,'persistent rail has exactly six primary destinations'],
 [template.includes('data-v0483-tools-search')&&template.includes('data-v0483-tools-groups'),'searchable scientific tools launcher present'],
 [template.includes('data-v0483-context-nav')&&ui.includes('renderContext'),'contextual subnavigation present'],
 [ui.includes('is-rail-collapsed-v0483')&&css.includes('is-rail-collapsed-v0483'),'desktop rail collapse state implemented'],
 [css.includes('@media(max-width:980px)')&&template.includes('data-lab-nav-toggle'),'mobile drawer remains supported'],
 [template.includes('data-v0481-workspace-switcher')&&template.includes('GRAPH STUDIO / PROJECT FIGURE'),'Graph Studio front door preserved'],
 [template.includes('Prototyping Workbench')&&template.includes('Decision Studio')&&template.includes('Site Intelligence'),'three related applications preserved'],
 [plugin.includes("'contextual-navigation-v0483'")&&plugin.includes('sc-lab-contextual-navigation-v0483'),'v0.48.3 assets enqueued'],
 [runtime.includes('SCLabConfig?.version')&&runtime.includes("labPresentationVersion!=='0.48.1'")&&runtime.includes('labReleaseVersion')&&runtime.includes('space-telescopes'),'outer release badge is dynamic and observation workspace mapping is current']
];
for(const [ok,label] of checks){if(!ok){console.error('FAIL - '+label);process.exit(1);}console.log('PASS - '+label);}
