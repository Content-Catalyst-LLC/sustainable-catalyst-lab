(function(W,D){'use strict';
 const Lab=W.SCLab=W.SCLab||{},VERSION='0.115.0',ENGINE='3.1.0';
 const types=['histogram','ecdf','box','violin','raincloud','ridge','interval-ribbon','fan-chart','posterior-density','coefficient-forest','calibration-reliability','residual-diagnostics','qq','sensitivity','uncertainty-decomposition','coverage'];
 const clone=v=>JSON.parse(JSON.stringify(v||{}));
 function decorate(host,meta={}){if(!host)return meta;host.dataset.scStatGraphics=VERSION;host.classList.add('sc-stat1150-host');const svg=host.querySelector('svg');if(svg){svg.classList.add('sc-stat1150-figure');svg.setAttribute('data-sc-statistical-graphics',VERSION);if(meta.graphicType)svg.setAttribute('data-statistical-graphic',meta.graphicType);svg.querySelectorAll('[data-semantic-role="reference"]').forEach(x=>x.classList.add('sc-stat1150-reference'));}return meta;}
 function render(host,spec,options={}){const design=Lab.ScientificVisualizationDesignSystemV01140;if(!design?.render)throw new Error('Scientific Visualization Design System v0.114.0 is unavailable.');const result=design.render(host,spec,{...options,profile:options.profile||'journal-double'});decorate(host,{graphicType:options.graphicType||spec.graphic_type||spec.kind});return{...(result||{}),version:VERSION,engineVersion:ENGINE,statisticalGraphics:true};}
 function intervalLabel(semantics,level){const pct=typeof level==='number'?`${Math.round(level*100)}% `:'';return`${pct}${String(semantics||'interval').replace(/-/g,' ')}`;}
 function fanOpacity(depth,total){if(!total)return .12;return Math.max(.08,Math.min(.28,.08+(depth+1)/total*.20));}
 function accessibility(meta={}){return{role:'img',description:meta.altText||'',nonColorEncodings:true,intervalSemanticsVisible:meta.intervalSemanticsVisible!==false,referenceLinesLabeled:true,keyboardInspect:meta.keyboardInspect!==false};}
 function audit(meta={}){const issues=[];if(meta.usesKde&&!meta.explicitBandwidth)issues.push('kde-bandwidth-not-declared');if(meta.usesQq&&!meta.referenceDistribution)issues.push('qq-reference-distribution-not-declared');if(meta.usesInterval&&!meta.intervalSemantics)issues.push('interval-semantics-not-declared');return{ok:true,version:VERSION,ready:issues.length===0,issues,scientificValidityCertified:false};}
 Lab.AdvancedStatisticalUncertaintyGraphicsV01150={version:VERSION,engineVersion:ENGINE,types,render,decorate,intervalLabel,fanOpacity,accessibility,audit,clone};
 W.SCLabAdvancedStatisticalUncertaintyGraphicsV01150=Lab.AdvancedStatisticalUncertaintyGraphicsV01150;
})(window,document);
