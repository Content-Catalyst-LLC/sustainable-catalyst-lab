(function(global){
  'use strict';
  const VERSION='0.118.0';
  const API='/wp-json/sc-lab/v1/visualization/v01180';
  function clone(v){return JSON.parse(JSON.stringify(v));}
  function refFigure(input,index){
    const x=clone(input||{});
    return {
      id:x.id||`figure-${(index||0)+1}`,
      figure_ref:x.figure_ref||x.figureRef||'',
      figure_kind:x.figure_kind||x.figureKind||'scientific-figure',
      title:x.title||`Figure ${(index||0)+1}`,
      caption:x.caption||null,
      alt_text:x.alt_text||x.altText||null,
      source_refs:clone(x.source_refs||x.sourceRefs||[]),
      method_refs:clone(x.method_refs||x.methodRefs||[]),
      finding_refs:clone(x.finding_refs||x.findingRefs||[]),
      evidence_refs:clone(x.evidence_refs||x.evidenceRefs||[]),
      citation_refs:clone(x.citation_refs||x.citationRefs||[]),
      immutable_underlying_figure:true
    };
  }
  function composePlate(figures,columns){
    const rows=(figures||[]).map(refFigure);
    const cols=Math.max(1,Math.min(4,Number(columns||Math.min(2,rows.length||1))));
    return {version:VERSION,figures:rows,columns:cols,rows:Math.ceil(rows.length/cols),panel_labels:rows.map((f,i)=>({panel_label:String.fromCharCode(65+i),figure_ref:f.figure_ref}))};
  }
  function narrativeOutline(narrative){
    const n=clone(narrative||{});
    return {id:n.id||'research-narrative',title:n.title||'Research narrative',format:n.format||'research-report',figure_count:(n.figures||[]).length,section_count:(n.sections||[]).length,automatic_conclusion_generation:false};
  }
  global.SCLabVisualResearchNarrativeV01180={VERSION,API,refFigure,composePlate,narrativeOutline};
})(window);
