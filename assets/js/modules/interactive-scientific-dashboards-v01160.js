(function(W,D){'use strict';
 const Lab=W.SCLab=W.SCLab||{},VERSION='0.116.0',ENGINE='3.2.0';
 const channels=['selection','brush','filter','cursor','state-axis','parameter','time-window'];
 const clone=v=>JSON.parse(JSON.stringify(v||{}));
 function decorate(host,meta={}){if(!host)return meta;host.dataset.scScientificDashboard=VERSION;host.classList.add('sc-dashboard1160-host');host.querySelectorAll('[data-sc-panel]').forEach((p,i)=>{p.classList.add('sc-dashboard1160-panel');p.setAttribute('data-panel-index',String(i));});return meta;}
 function responsiveColumns(count,width){if(width<640)return 1;if(width<980)return Math.min(2,count);return Math.min(4,count);}
 function applyInteraction(root,event){if(!root||!event)return[];const detail={...clone(event),dashboardVersion:VERSION};root.dispatchEvent(new CustomEvent('sc-lab-dashboard-interaction',{detail,bubbles:true}));return detail;}
 function snapshot(root,state={}){return{version:VERSION,filters:clone(state.filters),selections:clone(state.selections),parameters:clone(state.parameters),timeWindow:clone(state.timeWindow),panelViewState:clone(state.panelViewState),capturedAt:new Date().toISOString()};}
 function renderPanel(host,spec,options={}){const design=Lab.ScientificVisualizationDesignSystemV01140;if(!design?.render)throw new Error('Scientific Visualization Design System v0.114.0 is unavailable.');return design.render(host,spec,{...options,profile:options.profile||'web-responsive'});}
 function audit(meta={}){const issues=[];if(meta.panelCount>48)issues.push('panel-limit-exceeded');if(meta.linkCount>256)issues.push('link-limit-exceeded');return{ok:true,version:VERSION,ready:issues.length===0,issues,scientificValidityCertified:false,truthDetermined:false};}
 Lab.InteractiveScientificDashboardsV01160={version:VERSION,engineVersion:ENGINE,channels,decorate,responsiveColumns,applyInteraction,snapshot,renderPanel,audit,clone};
 W.SCLabInteractiveScientificDashboardsV01160=Lab.InteractiveScientificDashboardsV01160;
})(window,document);
