(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  // Preserve the original storage keys so v0.1.x projects migrate in place.
  const KEY = 'scLabProjectsV010';
  const ACTIVE = 'scLabActiveProjectV010';
  const COLLECTIONS = [
    'evidence','experiments','hypotheses','decisions','notes','calculations','documents',
    'maps','mapViews','datasets','savedQueries','observations','sourceSnapshots','citations','activity',
    'chemicalRecords','reactions','spectra','calibrations','methods',
    'physicsRecords','waveforms','circuitAnalyses','fieldModels','particleEvents','detectorAnalyses','nuclearRecords','opticalAnalyses','physicsValidationRecords',
    'biologyRecords','biologicalSamples','sequences','alignments','proteinAnalyses','geneticAnalyses','populationAnalyses','ecologyAnalyses','physiologyRecords','biologyValidationRecords',
    'astronomyRecords','celestialTargets','orbitalAnalyses','stellarAnalyses','photometryRecords','spectralAnalyses','galaxyAnalyses','cosmologyRecords','telescopeAnalyses','astronomyValidationRecords',
    'materialsRecords','materialSamples','mechanicalRecords','thermalRecords','electricalRecords','magneticRecords','opticalRecords','crystallographyRecords','phaseRecords','corrosionRecords','polymerRecords','compositeRecords','microscopyRecords','materialsValidationRecords',
    'earthRecords','geoscienceRecords','atmosphericRecords','climateRecords','hydrologyRecords','oceanRecords','marineSystemRecords','remoteSensingRecords','hazardRecords','carbonCycleRecords','earthValidationRecords',
    'energyRecords','engineeringRecords','energySystemRecords','solarRecords','windRecords','hydroRecords','storageRecords','gridRecords','thermalSystemRecords','fuelHydrogenRecords','emissionsRecords','technoEconomicRecords','reliabilityRecords','energyValidationRecords',
    'visualizations','dimensionalScenes','chartExports','analysisPackets','reports','reportFigures','reportExports','decisionStudioHandoffs','methodContracts','codeArtifacts','implementationComparisons','codeExecutions','languageComparisons','runtimeRecords','compilerRecords','executionJobs','benchmarkRuns','crossLanguageValidationRecords',
  'reportDrafts','reportRevisions','reportPackages','restorePreflights','restoreReceipts','accessibilityAudits','migrationValidationRecords',
  'electronicsRecords','embeddedRecords','hardwareValidationRecords','deviceProfiles','firmwareArtifacts','bomRecords','schematicRecords','interfaceRecords',
  'mechanicalThermalAnalyses','fluidRecords','vibrationRecords'];

  function blank(name = 'Untitled Lab Project') {
    const now = U.now();
    const project = { schemaVersion:'0.12.0', id:U.uid('project'), name, createdAt:now, updatedAt:now, description:'' };
    COLLECTIONS.forEach(key => { project[key] = []; });
    return project;
  }

  function normalize(project) {
    const base = blank(project?.name || 'Untitled Lab Project');
    const merged = Object.assign(base, project || {}, { schemaVersion:'0.12.0' });
    COLLECTIONS.forEach(key => { if (!Array.isArray(merged[key])) merged[key] = []; });
    // Preserve legacy map records while exposing the v0.9.5 mapViews collection.
    if (!merged.mapViews.length && merged.maps.length) merged.mapViews = merged.maps.slice();
    if (!merged.createdAt) merged.createdAt = U.now();
    if (!merged.updatedAt) merged.updatedAt = merged.createdAt;
    return merged;
  }

  function read() {
    try { const data=JSON.parse(localStorage.getItem(KEY)||'[]'); return Array.isArray(data)?data.map(normalize):[]; }
    catch (_) { return []; }
  }
  function write(items){ localStorage.setItem(KEY,JSON.stringify(items)); }

  class Projects {
    constructor(){
      this.items=read();
      if(!this.items.length){this.items=[blank('Lab Project')];write(this.items);}
      this.activeId=localStorage.getItem(ACTIVE)||this.items[0].id;
      if(!this.get())this.activeId=this.items[0].id;
      localStorage.setItem(ACTIVE,this.activeId);this.listeners=[];
    }
    onChange(fn){this.listeners.push(fn);} emit(){this.listeners.forEach(fn=>fn(this.get(),this.items));}
    get(id=this.activeId){return this.items.find(p=>p.id===id);} select(id){if(this.get(id)){this.activeId=id;localStorage.setItem(ACTIVE,id);this.emit();}}
    create(name){const p=blank(name||'Untitled Lab Project');this.items.unshift(p);this.activeId=p.id;this.save();return p;}
    update(mutator,activity){const p=this.get();if(!p)return;mutator(p);p.schemaVersion='0.12.0';p.updatedAt=U.now();if(activity)p.activity.unshift({id:U.uid('activity'),at:p.updatedAt,text:activity});p.activity=p.activity.slice(0,750);this.save();}
    save(){write(this.items);localStorage.setItem(ACTIVE,this.activeId);this.emit();}
    add(collection,record,activity){if(!COLLECTIONS.includes(collection))throw new Error(`Unknown project collection: ${collection}`);this.update(p=>p[collection].unshift(Object.assign({id:U.uid(collection),createdAt:U.now()},record)),activity);return this.get()[collection][0];}
    export(){const p=this.get();U.download(`${p.name.replace(/[^a-z0-9]+/gi,'-').toLowerCase()}-lab-project.json`,JSON.stringify(p,null,2),'application/json');}
    import(raw){const parsed=JSON.parse(raw);if(!parsed||typeof parsed!=='object'||!parsed.name)throw new Error('Invalid project file');const p=normalize(Object.assign({},parsed,{id:U.uid('project'),updatedAt:U.now()}));this.items.unshift(p);this.activeId=p.id;this.save();return p;}
  }
  Lab.Projects=Projects; Lab.ProjectModel={blank,normalize,collections:COLLECTIONS};
})(window);

// Project collection supported by v0.12.0: civilInfrastructureAnalyses

// Project collection supported by v0.12.0: infrastructureRecords

// Project collection supported by v0.12.0: infrastructureValidationRecords
