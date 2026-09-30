/* Sustainable Catalyst Lab v0.152.0.4 critical bootstrap bundle. */

/* === assets/js/modules/core.js === */
(function(w){'use strict';
const Lab=w.SCLab=w.SCLab||{};
Lab.util={
 uid(prefix='id'){return prefix+'-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8)},
 now(){return new Date().toISOString()},
 esc(value){return String(value??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))},
 download(name,text,type='text/plain'){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},0)},
 fmt(date){if(!date)return 'Unknown';const d=new Date(date);return Number.isNaN(d.getTime())?String(date):d.toLocaleString()},
 fingerprint(value){let h=2166136261;const s=JSON.stringify(value);for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16)},
 toast(root,message){const el=root.querySelector('[data-lab-toast]');if(!el)return;el.textContent=message;el.hidden=false;clearTimeout(el._t);el._t=setTimeout(()=>el.hidden=true,2800)},
 fetchJson(url,options={}){return fetch(url,options).then(async r=>{const body=await r.json().catch(()=>({}));if(!r.ok)throw new Error(body.message||`HTTP ${r.status}`);return body})}
};
})(window);
;

/* === assets/js/modules/projects.js === */
(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  const KEY = 'scLabProjectsV010';
  const ACTIVE = 'scLabActiveProjectV010';
  const WORKSPACE_SCHEMA = '0.28.0';
  const LEGACY_SCHEMA = '0.20.0';
  const CHECKPOINT_LIMIT = 20;
  const META_COLLECTIONS = new Set(['recordIndex','relationships','projectCheckpoints','migrationHistory','workspaceEvents']);
  const COLLECTIONS = [
    'evidence','experiments','hypotheses','decisions','notes','calculations','documents','models','sources','computeJobs',
    'maps','mapViews','datasets','savedQueries','observations','sourceSnapshots','citations','activity',
    'chemicalRecords','reactions','spectra','calibrations','methods',
    'physicsRecords','waveforms','circuitAnalyses','fieldModels','particleEvents','detectorAnalyses','nuclearRecords','opticalAnalyses','physicsValidationRecords',
    'biologyRecords','biologicalSamples','sequences','alignments','proteinAnalyses','geneticAnalyses','populationAnalyses','ecologyAnalyses','physiologyRecords','biologyValidationRecords',
    'astronomyRecords','celestialTargets','orbitalAnalyses','stellarAnalyses','photometryRecords','spectralAnalyses','galaxyAnalyses','cosmologyRecords','telescopeAnalyses','astronomyValidationRecords',
    'materialsRecords','materialSamples','mechanicalRecords','thermalRecords','electricalRecords','magneticRecords','opticalRecords','crystallographyRecords','phaseRecords','corrosionRecords','polymerRecords','compositeRecords','microscopyRecords','materialsValidationRecords',
    'earthRecords','geoscienceRecords','atmosphericRecords','climateRecords','hydrologyRecords','oceanRecords','marineSystemRecords','remoteSensingRecords','hazardRecords','carbonCycleRecords','earthValidationRecords',
    'energyRecords','engineeringRecords','energySystemRecords','solarRecords','windRecords','hydroRecords','storageRecords','gridRecords','thermalSystemRecords','fuelHydrogenRecords','emissionsRecords','technoEconomicRecords','reliabilityRecords','energyValidationRecords',
    'visualizations','dimensionalScenes','chartExports','analysisPackets','reports','reportFigures','reportExports','decisionStudioHandoffs','methodContracts','codeArtifacts','implementationComparisons','codeExecutions','languageComparisons','runtimeRecords','compilerRecords','executionJobs','benchmarkRuns','crossLanguageValidationRecords',
    'numericalMethodRuns','numericalSweepRecords','uncertaintyRecords','parameterStudies','designMatrices','designBatches','designAnalyses','sensitivityStudies','designStudyBundles','experimentProtocols','experimentRuns','replicationRecords','experimentComparisons','experimentReports','experimentBundles','reproducibleRuns','runComparisons','reproducibilityBundles','methodReviewRecords','reviewDecisionRecords','methodDeprecationRecords','methodReviewComparisons','methodReviewBundles','discoverySearches','discoveryCandidates','sourceImportBatches','openAccessLookups','libraryProfiles','researchSources','evidenceRecords','assumptionRecords','limitationRecords','researchProvenance','reportDrafts','reportRevisions','reportPackages','restorePreflights','restoreReceipts','accessibilityAudits','migrationValidationRecords',
    'electronicsRecords','embeddedRecords','hardwareValidationRecords','deviceProfiles','firmwareArtifacts','bomRecords','schematicRecords','interfaceRecords',
    'mechanicalThermalAnalyses','fluidRecords','vibrationRecords',
    'recordIndex','relationships','projectCheckpoints','migrationHistory','workspaceEvents'
  ];
  const TYPE_COLLECTIONS = {
    experiment:'experiments', dataset:'datasets', model:'models', calculation:'calculations', note:'notes', source:'sources', report:'reports', 'compute-job':'computeJobs', 'method-review':'methodReviewRecords', 'review-decision':'reviewDecisionRecords', 'method-deprecation':'methodDeprecationRecords', 'method-review-comparison':'methodReviewComparisons', 'discovery-search':'discoverySearches', 'discovery-candidate':'discoveryCandidates', 'source-import-batch':'sourceImportBatches', 'open-access-lookup':'openAccessLookups', 'library-profile':'libraryProfiles', 'experiment-protocol':'experimentProtocols', 'experiment-run':'experimentRuns', 'replication-record':'replicationRecords', 'experiment-comparison':'experimentComparisons', 'experiment-report':'experimentReports', 'parameter-study':'parameterStudies', 'design-matrix':'designMatrices', 'design-batch':'designBatches', 'design-analysis':'designAnalyses', 'sensitivity-study':'sensitivityStudies', 'design-study-bundle':'designStudyBundles'
  };
  const COLLECTION_TYPES = Object.fromEntries(Object.entries(TYPE_COLLECTIONS).map(([type, collection]) => [collection, type]));

  const memoryStorage = new Map();
  const recoveryStorage = w.SCLabProductionStorageV0266 || null;
  const safeMode = !!w.__SCLabSafeModeV0266;
  const now = () => U?.now?.() || new Date().toISOString();
  const uid = prefix => U?.uid?.(prefix) || `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const clone = value => JSON.parse(JSON.stringify(value));

  function storageGet(key) {
    if (safeMode) return memoryStorage.has(key) ? memoryStorage.get(key) : null;
    if (recoveryStorage && typeof recoveryStorage.get === 'function') return recoveryStorage.get(key) ?? (memoryStorage.has(key) ? memoryStorage.get(key) : null);
    try { return w.localStorage?.getItem(key) ?? (memoryStorage.has(key) ? memoryStorage.get(key) : null); }
    catch (_) { return memoryStorage.has(key) ? memoryStorage.get(key) : null; }
  }
  function storageSet(key, value) {
    const text = String(value); memoryStorage.set(String(key), text);
    if (safeMode) return true;
    if (recoveryStorage && typeof recoveryStorage.set === 'function') return recoveryStorage.set(key, text);
    try { w.localStorage?.setItem(key, text); return true; } catch (_) { return false; }
  }

  function inferType(collection, record={}) {
    return record.recordType || COLLECTION_TYPES[collection] || record.type || collection.replace(/Records$|Analyses$|Runs$|s$/,'').replace(/([a-z])([A-Z])/g,'$1-$2').toLowerCase() || 'record';
  }
  function titleFor(record, collection) {
    return String(record.title || record.name || record.label || record.method || record.type || `${inferType(collection, record)} record`);
  }
  function normalizeRecord(record, collection) {
    const created = record?.createdAt || record?.at || now();
    return Object.assign({}, record || {}, {
      id: record?.id || uid(collection),
      recordType: inferType(collection, record || {}),
      collection,
      title: titleFor(record || {}, collection),
      status: record?.status || 'active',
      createdAt: created,
      updatedAt: record?.updatedAt || created,
      schemaVersion: record?.schemaVersion || WORKSPACE_SCHEMA,
    });
  }
  function ensureCollection(name) {
    const safe = String(name || '').trim();
    if (!/^[A-Za-z][A-Za-z0-9_-]{1,79}$/.test(safe)) throw new Error(`Invalid project collection: ${safe}`);
    if (!COLLECTIONS.includes(safe)) COLLECTIONS.push(safe);
    return safe;
  }
  function recordCollections(project) {
    return Object.keys(project || {}).filter(key => Array.isArray(project[key]) && !META_COLLECTIONS.has(key) && key !== 'activity');
  }
  function rebuildIndex(project) {
    const index=[];
    recordCollections(project).forEach(collection => {
      project[collection] = project[collection].map(record => normalizeRecord(record, collection));
      project[collection].forEach(record => index.push({
        id:record.id, collection, recordType:record.recordType, title:record.title, status:record.status,
        createdAt:record.createdAt, updatedAt:record.updatedAt, sourceId:record.sourceId || null, method:record.method || record.methodId || null
      }));
    });
    project.recordIndex = index.sort((a,b)=>String(b.updatedAt).localeCompare(String(a.updatedAt)));
    return project.recordIndex;
  }
  function workspaceMetadata(project) {
    const current = project.workspace && typeof project.workspace === 'object' ? project.workspace : {};
    return Object.assign({
      schemaVersion:WORKSPACE_SCHEMA,
      storageMode:safeMode?'memory-safe-start':'browser-local',
      autosave:true,
      autosaveIntervalMs:750,
      lastSavedAt:project.updatedAt || now(),
      lastCheckpointAt:null,
      migrationState:'current',
      serverBacked:false,
      capabilities:['records','relationships','checkpoints','search','import-export','schema-migration']
    }, current, {schemaVersion:WORKSPACE_SCHEMA, storageMode:safeMode?'memory-safe-start':(current.storageMode || 'browser-local')});
  }
  function blank(name = 'Untitled Lab Project') {
    const stamp=now();
    const project={
      schemaVersion:WORKSPACE_SCHEMA, legacySchemaVersion:LEGACY_SCHEMA, id:uid('project'), name, description:'', createdAt:stamp, updatedAt:stamp,
      workspace:{schemaVersion:WORKSPACE_SCHEMA,storageMode:safeMode?'memory-safe-start':'browser-local',autosave:true,autosaveIntervalMs:750,lastSavedAt:stamp,lastCheckpointAt:null,migrationState:'current',serverBacked:false,capabilities:['records','relationships','checkpoints','search','import-export','schema-migration']}
    };
    COLLECTIONS.forEach(key => { project[key]=[]; });
    project.migrationHistory.push({id:uid('migration'),from:null,to:WORKSPACE_SCHEMA,at:stamp,status:'created',preservedUnknownFields:true});
    return project;
  }
  function normalize(project) {
    const source = project && typeof project === 'object' ? clone(project) : {};
    const base = blank(source.name || 'Untitled Lab Project');
    const fromVersion = source.schemaVersion || source.workspace?.schemaVersion || 'legacy';
    const merged = Object.assign(base, source);
    merged.legacySchemaVersion = source.legacySchemaVersion || (fromVersion !== WORKSPACE_SCHEMA ? fromVersion : LEGACY_SCHEMA);
    merged.schemaVersion = WORKSPACE_SCHEMA;
    COLLECTIONS.forEach(key => { if (!Array.isArray(merged[key])) merged[key]=[]; });
    Object.keys(source).forEach(key => { if (Array.isArray(source[key])) { ensureCollection(key); if (!Array.isArray(merged[key])) merged[key]=[]; } });
    if (!merged.mapViews.length && Array.isArray(merged.maps) && merged.maps.length) merged.mapViews=clone(merged.maps);
    if (!merged.createdAt) merged.createdAt=now();
    if (!merged.updatedAt) merged.updatedAt=merged.createdAt;
    merged.workspace=workspaceMetadata(merged);
    if (!Array.isArray(merged.relationships)) merged.relationships=[];
    merged.relationships=merged.relationships.map(row=>Object.assign({id:uid('relationship'),type:'related-to',createdAt:now()},row));
    if (!Array.isArray(merged.projectCheckpoints)) merged.projectCheckpoints=[];
    if (!Array.isArray(merged.migrationHistory)) merged.migrationHistory=[];
    if (fromVersion !== WORKSPACE_SCHEMA && !merged.migrationHistory.some(row=>row?.to===WORKSPACE_SCHEMA)) {
      merged.migrationHistory.unshift({id:uid('migration'),from:fromVersion,to:WORKSPACE_SCHEMA,at:now(),status:'migrated',preservedUnknownFields:true});
    }
    rebuildIndex(merged);
    return merged;
  }
  function checkpointSnapshot(project) {
    const snapshot=clone(project); snapshot.projectCheckpoints=[]; snapshot.recordIndex=[]; snapshot.workspaceEvents=[]; return snapshot;
  }
  function read() {
    try { const data=JSON.parse(storageGet(KEY)||'[]'); return Array.isArray(data)?data.map(normalize):[]; }
    catch (_) { return []; }
  }
  function write(items){ return storageSet(KEY,JSON.stringify(items)); }

  class Projects {
    constructor(){
      this.items=read();
      if(!this.items.length){this.items=[blank('Lab Project')];write(this.items);}
      this.activeId=storageGet(ACTIVE)||this.items[0].id;
      if(!this.get())this.activeId=this.items[0].id;
      storageSet(ACTIVE,this.activeId);this.listeners=[];this.save('workspace initialization');
    }
    onChange(fn){if(typeof fn!=='function')return()=>{};this.listeners.push(fn);return()=>{this.listeners=this.listeners.filter(x=>x!==fn);};}
    emit(){this.listeners.slice().forEach(fn=>{try{fn(this.get(),this.items);}catch(_){}});}
    get(id=this.activeId){return this.items.find(p=>p.id===id);}
    select(id){if(this.get(id)){this.activeId=id;storageSet(ACTIVE,id);this.emit();return this.get();}return null;}
    create(name){const p=blank(name||'Untitled Lab Project');this.items.unshift(p);this.activeId=p.id;this.save('project created');return p;}
    update(mutator,activity){const p=this.get();if(!p)return null;mutator(p);p.schemaVersion=WORKSPACE_SCHEMA;p.workspace=workspaceMetadata(p);p.updatedAt=now();p.workspace.lastSavedAt=p.updatedAt;if(activity){p.activity.unshift({id:uid('activity'),at:p.updatedAt,text:activity});p.activity=p.activity.slice(0,750);p.workspaceEvents.unshift({id:uid('workspace-event'),at:p.updatedAt,type:'change',text:activity});p.workspaceEvents=p.workspaceEvents.slice(0,1000);}rebuildIndex(p);this.save(activity||'project updated');return p;}
    save(reason='autosave'){this.items=this.items.map(normalize);const p=this.get();if(p){p.workspace.lastSavedAt=now();p.workspace.lastSaveReason=reason;}write(this.items);storageSet(ACTIVE,this.activeId);this.emit();return true;}
    add(collection,record,activity){collection=ensureCollection(collection);return this.update(p=>{if(!Array.isArray(p[collection]))p[collection]=[];p[collection].unshift(normalizeRecord(record,collection));},activity)?.[collection]?.[0]||null;}
    updateRecord(id,patch,activity='Record updated'){const found=this.getRecord(id);if(!found)return null;this.update(p=>{const row=p[found.collection].find(x=>x.id===id);Object.assign(row,typeof patch==='function'?patch(clone(row)):patch,{updatedAt:now()});},activity);return this.getRecord(id)?.record||null;}
    removeRecord(id,activity='Record removed'){const found=this.getRecord(id);if(!found)return false;this.update(p=>{p[found.collection]=p[found.collection].filter(x=>x.id!==id);p.relationships=p.relationships.filter(r=>r.from!==id&&r.to!==id);},activity);return true;}
    getRecord(id){const p=this.get();if(!p)return null;for(const collection of recordCollections(p)){const record=p[collection].find(row=>row.id===id);if(record)return{collection,record};}return null;}
    search(query='',filters={}){const p=this.get();if(!p)return[];const q=String(query||'').toLowerCase();return p.recordIndex.filter(row=>(!q||`${row.title} ${row.recordType} ${row.collection} ${row.method||''}`.toLowerCase().includes(q))&&(!filters.type||row.recordType===filters.type)&&(!filters.collection||row.collection===filters.collection)&&(!filters.status||row.status===filters.status));}
    link(from,to,type='related-to',metadata={}){if(!from||!to||from===to)throw new Error('Two different records are required.');if(!this.getRecord(from)||!this.getRecord(to))throw new Error('Relationship records were not found.');const existing=this.get().relationships.find(r=>r.from===from&&r.to===to&&r.type===type);if(existing)return existing;let created;this.update(p=>{created={id:uid('relationship'),from,to,type:String(type||'related-to'),metadata:metadata||{},createdAt:now()};p.relationships.unshift(created);},`Relationship created: ${type}`);return created;}
    unlink(id){let changed=false;this.update(p=>{const n=p.relationships.length;p.relationships=p.relationships.filter(r=>r.id!==id);changed=n!==p.relationships.length;},'Relationship removed');return changed;}
    createCheckpoint(label='Manual checkpoint',reason='manual'){let checkpoint;this.update(p=>{checkpoint={id:uid('checkpoint'),label:String(label||'Checkpoint'),reason,createdAt:now(),schemaVersion:WORKSPACE_SCHEMA,recordCount:p.recordIndex.length,snapshot:checkpointSnapshot(p)};p.projectCheckpoints.unshift(checkpoint);p.projectCheckpoints=p.projectCheckpoints.slice(0,CHECKPOINT_LIMIT);p.workspace.lastCheckpointAt=checkpoint.createdAt;},`Checkpoint created: ${label}`);return checkpoint;}
    restoreCheckpoint(id){const current=this.get();const cp=current?.projectCheckpoints?.find(row=>row.id===id);if(!cp?.snapshot)throw new Error('Checkpoint not found.');const restored=normalize(Object.assign({},clone(cp.snapshot),{id:current.id,name:current.name,projectCheckpoints:current.projectCheckpoints,updatedAt:now()}));const i=this.items.findIndex(row=>row.id===current.id);this.items[i]=restored;restored.activity.unshift({id:uid('activity'),at:restored.updatedAt,text:`Checkpoint restored: ${cp.label}`});this.save('checkpoint restored');return restored;}
    export(){return this.exportBundle();}
    exportBundle(){const p=this.get();const bundle={schema:'sc-lab-project-bundle/0.28.0',version:WORKSPACE_SCHEMA,exportedAt:now(),activeProjectId:p.id,project:clone(p),integrity:{recordCount:p.recordIndex.length,relationshipCount:p.relationships.length,checkpointCount:p.projectCheckpoints.length}};U.download(`${p.name.replace(/[^a-z0-9]+/gi,'-').toLowerCase()}-lab-project-v0280.json`,JSON.stringify(bundle,null,2),'application/json');return bundle;}
    import(raw,mode='copy'){const parsed=typeof raw==='string'?JSON.parse(raw):raw;const source=parsed?.schema==='sc-lab-project-bundle/0.28.0'?parsed.project:parsed;if(!source||typeof source!=='object'||!source.name)throw new Error('Invalid project or project bundle.');const incoming=normalize(source);if(mode==='merge'&&this.get(incoming.id)){const i=this.items.findIndex(x=>x.id===incoming.id);this.items[i]=normalize(Object.assign({},this.items[i],incoming,{updatedAt:now()}));this.activeId=incoming.id;}else{incoming.id=uid('project');incoming.name=mode==='copy'?`${incoming.name} (Imported)`:incoming.name;incoming.updatedAt=now();this.items.unshift(incoming);this.activeId=incoming.id;}this.save('project imported');return this.get();}
    migrateAll(){this.items=this.items.map(normalize);this.save('workspace schema migration');return this.diagnostics();}
    diagnostics(){const p=this.get();let bytes=0;try{bytes=new Blob([JSON.stringify(this.items)]).size;}catch(_){bytes=JSON.stringify(this.items).length;}return{version:WORKSPACE_SCHEMA,safeMode,storageMode:p?.workspace?.storageMode||'unknown',projectCount:this.items.length,activeProjectId:this.activeId,recordCount:p?.recordIndex?.length||0,relationshipCount:p?.relationships?.length||0,checkpointCount:p?.projectCheckpoints?.length||0,migrationCount:p?.migrationHistory?.length||0,bytes,lastSavedAt:p?.workspace?.lastSavedAt||null,lastCheckpointAt:p?.workspace?.lastCheckpointAt||null,unknownCollections:recordCollections(p).filter(key=>!COLLECTIONS.includes(key))};}
  }

  Lab.Projects=Projects;
  Lab.ProjectModel={blank,normalize,normalizeRecord,rebuildIndex,collections:COLLECTIONS,recordCollections,typeCollections:TYPE_COLLECTIONS,workspaceSchemaVersion:WORKSPACE_SCHEMA,legacySchemaVersion:LEGACY_SCHEMA};
})(window);

// Project collection supported by v0.20.0: civilInfrastructureAnalyses

// Project collection supported by v0.20.0: infrastructureRecords

// Project collection supported by v0.20.0: infrastructureValidationRecords


// v0.20.0 project collections are created dynamically by the Architecture and Building Performance workspace:
// - architectureBuildingAnalyses
// - buildingPerformanceRecords
// - buildingPerformanceValidationRecords
// - buildingEnvelopeRecords
// - daylightRecords
// - indoorEnvironmentalQualityRecords
// - buildingEnergyRecords


// v0.20.0 project collections are created dynamically by the Urban Planning and Spatial Systems workspace:
// - urbanPlanningSpatialAnalyses
// - urbanSpatialRecords
// - urbanPlanningValidationRecords
// - landUseRecords
// - accessibilityRecords
// - mobilityRecords
// - spatialNetworkRecords
// - gisAnalysisRecords
// - publicServiceRecords
// - urbanResilienceRecords
// - spatialScenarioRecords


// v0.20.0 project collections are created dynamically by Sustainable Cities and Urban Resilience:
// - sustainableCitiesResilienceAnalyses
// - sustainableCityResilienceRecords
// - sustainableCitiesValidationRecords
// - urbanMetabolismRecords
// - decarbonizationRecords
// - climateAdaptationRecords
// - infrastructureContinuityRecords
// - socialResilienceRecords
// - cityScenarioRecords


// v0.20.0 project collections are created dynamically by Circular Economy and Industrial Ecology:
// - circularEconomyIndustrialEcologyAnalyses
// - circularEconomyRecords
// - industrialEcologyRecords
// - circularityValidationRecords
// - materialFlowRecords
// - circularProductRecords
// - wasteRecoveryRecords
// - industrialSymbiosisRecords
// - lifecycleFootprintRecords
// - circularTransitionRecords


// v0.20.0 project collections are created dynamically by Circular Economy and Industrial Ecology:
// - comparativeEconomicsDevelopmentAnalyses
// - developmentEconomicsRecords
// - developmentSystemsValidationRecords
// - nationalAccountsRecords
// - growthProductivityRecords
// - tradeTransformationRecords
// - laborInequalityRecords
// - humanDevelopmentRecords
// - publicFinanceRecords
// - developmentFinanceRecords
// - developmentScenarioRecords


// v0.20.0 project collections are created dynamically by Aerospace Engineering and Flight Systems:
// - aerospaceEngineeringFlightAnalyses
// - aerospaceFlightSystemsRecords
// - aerospaceFlightValidationRecords
// - aerodynamicsRecords
// - flightPerformanceRecords
// - flightControlsRecords
// - propulsionEnergyRecords
// - aerospaceStructuresRecords
// - navigationMissionRecords
// - flightSystemsReliabilityRecords
// - flightMissionRecords


// v0.20.0 project collections are created dynamically by Rocket Engineering and Flight Systems:
// - rocketPropulsionSpaceflightAnalyses
// - spaceflightSystemsRecords
// - rocketSpaceflightValidationRecords
// - propulsionFundamentalsRecords
// - nozzleEngineRecords
// - launchVehicleStagingRecords
// - ascentDynamicsRecords
// - orbitalMechanicsRecords
// - spacecraftMissionRecords
// - spaceflightReliabilityRecords
// - missionDeltaVRecords


// v0.20.0 project collections are created dynamically by the Microbiology Laboratory:
// - microbiologyAnalyses
// - microbiologyRecords
// - microbiologyValidationRecords
// - microbialGrowthRecords
// - cultureKineticsRecords
// - enumerationMicroscopyRecords
// - environmentalMicrobiologyRecords
// - antimicrobialScreeningRecords
// - microbialEcologyRecords
// - microbiologyAssayRecords
// - microbiologyQcRecords
;

/* === assets/js/modules/workspace.js === */
(function(w){'use strict';const Lab=w.SCLab=w.SCLab||{};
const modules=[
{id:'overview',label:'Overview',group:'Project',keywords:['dashboard','project','summary']},{id:'activity',label:'Activity',group:'Project',keywords:['history','audit','recent']},
{id:'model-studio',label:'Model Studio',group:'Model',keywords:['model','equation','calibration','diagnostics','cross validation','ODE','response surface','optimization']},{id:'probabilistic-analysis',label:'Uncertainty & sensitivity',group:'Model',keywords:['uncertainty','probability','sensitivity','Monte Carlo','Sobol','Latin hypercube','confidence interval']},{id:'graph-studio',label:'Graph Studio',group:'Visualize',keywords:['graph','figure','chart','publication','SVG','PNG','heatmap','scatter','line','histogram','probabilistic']},
{id:'scientific-feeds',label:'Observation board',group:'Observe',keywords:['feeds','USGS','NASA','PubMed','arXiv','events','observations']},{id:'climate-maps',label:'Climate maps',group:'Observe',keywords:['Earth observation','GIBS','temperature','precipitation','aerosol']},{id:'space-telescopes',label:'Space observations',group:'Observe',keywords:['JWST','Hubble','Chandra','NASA','astronomy']},{id:'marine-biology',label:'Marine biology',group:'Observe',keywords:['OBIS','ocean','species','biodiversity','taxon']},
{id:'soil-organic-carbon',label:'Soil Organic Carbon',group:'Carbon & Nature',keywords:['SOC','soil carbon','bulk density','carbon stock','AFOLU','carbon farming','coarse fragments','Mg C/ha']},{id:'dataset-inspector',label:'Dataset inspector',group:'Analyze',keywords:['table','CSV','JSON','plot','filter','data quality']},{id:'chemistry',label:'Chemistry laboratory',group:'Analyze',keywords:['periodic table','stoichiometry','molar mass','reaction','solutions','acid base','thermochemistry','electrochemistry','kinetics','calibration']},{id:'physics',label:'Physics laboratory',group:'Analyze',keywords:['mechanics','waves','thermodynamics','fluids','optics','electromagnetism','circuits','signals','quantum','nuclear','particle physics','detector']},{id:'biology',label:'Biology laboratory',group:'Analyze',keywords:['cellular biology','molecular biology','genetics','genomics','sequence alignment','protein','enzyme kinetics','population genetics','ecology','physiology','computational biology']},{id:'astronomy',label:'Astronomy and astrophysics laboratory',group:'Analyze',keywords:['celestial coordinates','orbital mechanics','planetary science','stellar astrophysics','photometry','spectroscopy','galaxies','cosmology','telescopes','imaging']},{id:'materials',label:'Materials science and characterization laboratory',group:'Analyze',keywords:['mechanical properties','thermal transport','electrical properties','magnetism','optical characterization','XRD','crystallography','phase diagrams','diffusion','corrosion','polymers','composites','microscopy']},{id:'earth-systems',label:'Earth, climate, ocean, and marine systems laboratory',group:'Analyze',keywords:['geology','atmosphere','climate','hydrology','oceanography','marine ecology','remote sensing','hazards','carbon cycle','Earth systems']},{id:'energy-engineering',label:'Energy and engineering laboratory',group:'Analyze',keywords:['energy balance','solar','wind','hydro','storage','grid','thermal','hydrogen','emissions','LCOE','reliability','engineering']},{id:'visualization-studio',label:'Visualization and export studio',group:'Visualize',keywords:['chart','graph','SVG','PNG','PDF','CSV','Decision Studio','report','3D','4D','polytope','tesseract','scene']},{id:'code-studio',label:'Universal code switcher',group:'Analyze',keywords:['Python','R','Julia','JavaScript','TypeScript','SQL','C','C++','Fortran','Rust','Go','Haskell','method contract','source code']},{id:'science-engineering',label:'Science & engineering',group:'Analyze',keywords:['physics','biology','astronomy','materials','energy','spectrometry','calculator']},
{id:'experiments',label:'Experiments',group:'Record',keywords:['method','procedure','result','test']},{id:'evidence-decisions',label:'Evidence & decisions',group:'Record',keywords:['evidence','hypothesis','decision','claim']},{id:'notebook',label:'Notebook',group:'Record',keywords:['note','observation','lab record']},{id:'documentation',label:'Documentation',group:'Record',keywords:['report','technical document','brief','export']},{id:'report-studio',label:'PDF Reports',group:'Record',keywords:['pdf','report','decision studio','handoff','brief','figure','audit']},
{id:'workspace-data',label:'Workspace data',group:'System',keywords:['backup','restore','reset','clear notes','delete observations','settings']},{id:'source-registry',label:'Source registry',group:'System',keywords:['connector','license','coverage','freshness','provenance']},{id:'system-status',label:'Connector status',group:'System',keywords:['health','source','API','status']}];
const quickTools=[{id:'periodic-table',label:'Periodic Table',kind:'chem-tab',module:'chemistry',tab:'periodic',keywords:['elements','atomic number','chemistry']},{id:'stoichiometry',label:'Stoichiometry',kind:'chem-tab',module:'chemistry',tab:'reactions',keywords:['balance equation','limiting reagent','yield']},{id:'acid-base',label:'Acid–Base Chemistry',kind:'chem-tab',module:'chemistry',tab:'acid-base',keywords:['pH','buffer','titration','Ka','Kb']},{id:'thermochemistry',label:'Thermochemistry',kind:'chem-tab',module:'chemistry',tab:'thermochemistry',keywords:['enthalpy','Gibbs','calorimetry','Hess']},{id:'electrochemistry',label:'Electrochemistry',kind:'chem-tab',module:'chemistry',tab:'electrochemistry',keywords:['Nernst','electrolysis','cell potential']},{id:'electromagnetism-studio',label:'Electromagnetism Studio',kind:'physics-tab',module:'physics',tab:'electromagnetism',keywords:['electric field','magnetic field','induction','Maxwell','waveguide']},{id:'particle-physics',label:'Particle Physics Studio',kind:'physics-tab',module:'physics',tab:'particle',keywords:['quarks','leptons','bosons','invariant mass','detector']},{id:'circuit-bench',label:'Circuit and Signal Bench',kind:'physics-tab',module:'physics',tab:'circuits',keywords:['RLC','FFT','filter','waveform','oscilloscope']},{id:'sequence-analysis',label:'Sequence Analysis',kind:'biology-tab',module:'biology',tab:'sequences',keywords:['DNA','RNA','alignment','ORF','motif','k-mer']},{id:'enzyme-kinetics',label:'Enzyme Kinetics',kind:'biology-tab',module:'biology',tab:'enzymes',keywords:['Michaelis-Menten','Hill','inhibition']},{id:'population-genetics',label:'Population Genetics',kind:'biology-tab',module:'biology',tab:'population',keywords:['Hardy-Weinberg','selection','drift','Jukes-Cantor']},{id:'ecology-analysis',label:'Ecology Analysis',kind:'biology-tab',module:'biology',tab:'ecology',keywords:['diversity','logistic growth','predator prey','mark recapture']},{id:'orbital-mechanics-lab',label:'Orbital Mechanics',kind:'astronomy-tab',module:'astronomy',tab:'orbits',keywords:['Kepler','vis-viva','Hohmann','Hill radius','Roche limit']},{id:'stellar-astrophysics',label:'Stellar Astrophysics',kind:'astronomy-tab',module:'astronomy',tab:'stellar',keywords:['luminosity','temperature','surface gravity','blackbody','main sequence']},{id:'astronomical-photometry',label:'Astronomical Photometry',kind:'astronomy-tab',module:'astronomy',tab:'photometry',keywords:['magnitude','flux','SNR','aperture']},{id:'cosmology-tools',label:'Cosmology Tools',kind:'astronomy-tab',module:'astronomy',tab:'cosmology',keywords:['Hubble','critical density','lookback time']},{id:'materials-characterization',label:'Materials Characterization',kind:'materials-tab',module:'materials',tab:'crystallography',keywords:['XRD','Bragg','Scherrer','lattice parameter','crystallite size']},{id:'mechanical-properties',label:'Mechanical Properties',kind:'materials-tab',module:'materials',tab:'mechanical',keywords:['stress','strain','fracture','fatigue','creep']},{id:'materials-microscopy',label:'Materials Microscopy',kind:'materials-tab',module:'materials',tab:'microscopy',keywords:['particle size','grain size','area fraction','image calibration']},{id:'earth-climate-analysis',label:'Earth and Climate Analysis',kind:'earth-tab',module:'earth-systems',tab:'climate',keywords:['climate trend','radiative forcing','degree days','aridity','sea level']},{id:'ocean-marine-analysis',label:'Ocean and Marine Systems',kind:'earth-tab',module:'earth-systems',tab:'ocean',keywords:['waves','tsunami','geostrophic','Ekman','salinity','marine ecology']},{id:'remote-hazards',label:'Remote Sensing and Hazards',kind:'earth-tab',module:'earth-systems',tab:'remote',keywords:['NDVI','NDWI','classification','brightness temperature','hazard recurrence']},{id:'energy-systems',label:'Energy Systems',kind:'energy-tab',module:'energy-engineering',tab:'balances',keywords:['energy balance','efficiency','capacity factor','load factor']},{id:'renewable-energy',label:'Renewable Energy',kind:'energy-tab',module:'energy-engineering',tab:'solar',keywords:['solar','wind','hydro','PV','turbine']},{id:'storage-grid',label:'Storage and Grid',kind:'energy-tab',module:'energy-engineering',tab:'storage',keywords:['battery','hydrogen','pumped storage','grid','power factor']},{id:'energy-economics',label:'Energy Economics and Reliability',kind:'energy-tab',module:'energy-engineering',tab:'economics',keywords:['LCOE','LCOS','NPV','IRR','reliability','availability']},{id:'spectrometry',label:'Spectrometry',kind:'analysis-tab',module:'science-engineering',tab:'spectrometry',keywords:['spectrum','peak','baseline']},{id:'dataset-inspector',label:'Dataset Inspector',kind:'module',module:'dataset-inspector',keywords:['CSV','table','chart','filter']},{id:'photon',label:'Photon Energy',kind:'calculator',module:'science-engineering',calculatorId:'photon',keywords:['wavelength','frequency','Planck']},{id:'rlc',label:'RLC Impedance',kind:'calculator',module:'science-engineering',calculatorId:'rlc',keywords:['electromagnetism','resonance','circuit']},{id:'orbit',label:'Orbital Mechanics',kind:'calculator',module:'science-engineering',calculatorId:'orbit',keywords:['astronomy','period','velocity']},{id:'uncertainty',label:'Uncertainty Propagation',kind:'calculator',module:'science-engineering',calculatorId:'uncertainty',keywords:['measurement','error']},{id:'pv',label:'Photovoltaic Output',kind:'calculator',module:'science-engineering',calculatorId:'pv',keywords:['energy','solar','power']}];
const trace=[{key:'sourceSnapshots',label:'Sources',module:'source-registry',count:p=>new Set([...(p.sourceSnapshots||[]).map(x=>x.source),...(p.evidence||[]).map(x=>x.source||x.record?.source)].filter(Boolean)).size},{key:'observations',label:'Observations',module:'scientific-feeds',count:p=>(p.observations||[]).length},{key:'evidence',label:'Evidence',module:'evidence-decisions',count:p=>(p.evidence||[]).length},{key:'hypotheses',label:'Hypotheses',module:'evidence-decisions',count:p=>(p.hypotheses||[]).length},{key:'datasets',label:'Datasets',module:'dataset-inspector',count:p=>(p.datasets||[]).length},{key:'calculations',label:'Calculations',module:'science-engineering',count:p=>(p.calculations||[]).length},{key:'experiments',label:'Experiments',module:'experiments',count:p=>(p.experiments||[]).length},{key:'decisions',label:'Decisions',module:'evidence-decisions',count:p=>(p.decisions||[]).length},{key:'documents',label:'Documents',module:'documentation',count:p=>(p.documents||[]).length}];
const norm=v=>String(v||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
function search(query,defs){const q=norm(query);if(!q)return[];const calc=(defs||[]).map(def=>({id:def.id,label:def.name,group:def.domain,kind:'calculator',module:'science-engineering',calculatorId:def.id,keywords:[def.domain,...(def.fields||[]).map(f=>f[1])]}));return [...modules.map(x=>({...x,kind:'module'})),...quickTools,...calc].map(item=>{const h=norm([item.label,item.group,...(item.keywords||[])].join(' '));let score=norm(item.label)===q?100:norm(item.label).startsWith(q)?50:h.includes(q)?20:0;q.split(' ').forEach(t=>{if(t&&h.includes(t))score+=4});return{item,score}}).filter(r=>r.score>0).sort((a,b)=>b.score-a.score||a.item.label.localeCompare(b.item.label)).slice(0,12).map(r=>r.item)}
const traceCounts=p=>trace.map(s=>({...s,value:s.count(p||{})}));
const projectTotal=p=>['evidence','experiments','hypotheses','decisions','notes','calculations','documents','maps','mapViews','datasets','savedQueries','observations','sourceSnapshots','citations','chemicalRecords','reactions','spectra','calibrations','methods','physicsRecords','waveforms','circuitAnalyses','fieldModels','particleEvents','detectorAnalyses','nuclearRecords','opticalAnalyses','physicsValidationRecords','biologyRecords','biologicalSamples','sequences','alignments','proteinAnalyses','geneticAnalyses','populationAnalyses','ecologyAnalyses','physiologyRecords','biologyValidationRecords','astronomyRecords','celestialTargets','orbitalAnalyses','stellarAnalyses','photometryRecords','spectralAnalyses','galaxyAnalyses','cosmologyRecords','telescopeAnalyses','astronomyValidationRecords','materialsRecords','materialSamples','mechanicalRecords','thermalRecords','electricalRecords','magneticRecords','opticalRecords','crystallographyRecords','phaseRecords','corrosionRecords','polymerRecords','compositeRecords','microscopyRecords','materialsValidationRecords','earthRecords','geoscienceRecords','atmosphericRecords','climateRecords','hydrologyRecords','oceanRecords','marineSystemRecords','remoteSensingRecords','hazardRecords','carbonCycleRecords','earthValidationRecords','energyRecords','engineeringRecords','energySystemRecords','solarRecords','windRecords','hydroRecords','storageRecords','gridRecords','thermalSystemRecords','fuelHydrogenRecords','emissionsRecords','technoEconomicRecords','reliabilityRecords','energyValidationRecords','visualizations','dimensionalScenes','chartExports','analysisPackets','reports','reportFigures','reportExports','decisionStudioHandoffs','methodContracts','codeArtifacts','implementationComparisons','codeExecutions','languageComparisons','runtimeRecords','compilerRecords','executionJobs','benchmarkRuns','crossLanguageValidationRecords'].reduce((t,k)=>t+((p&&p[k])||[]).length,0);
Lab.Workspace={modules,quickTools,trace,search,traceCounts,projectTotal};})(window);
;

/* === assets/js/modules/feeds.js === */
(function (w, d) {
  'use strict';

  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;

  function url(source, params = {}) {
    const base = (w.SCLabConfig?.restBase || '/wp-json/sc-lab/v1/') + `feeds/${encodeURIComponent(source)}`;
    return `${base}?${new URLSearchParams(params).toString()}`;
  }

  function queryParams(source, q, limit) {
    const params = { limit };
    if (q) {
      if (source === 'obis-marine') params.scientificName = q;
      else params.q = q;
    }
    return params;
  }

  async function load(source, q = '', limit = 12) {
    return U.fetchJson(url(source, queryParams(source, q, limit)), {
      headers: { 'X-WP-Nonce': w.SCLabConfig?.nonce || '' }
    });
  }

  function recordMeta(record) {
    const location = record.location || {};
    return [
      ['Source', record.source || 'Unknown'],
      ['Domain', record.domain || 'Science'],
      ['Observed', U.fmt(record.observedAt)],
      ['Retrieved', U.fmt(record.retrievedAt)],
      ['Latitude', location.latitude ?? '—'],
      ['Longitude', location.longitude ?? '—'],
      ['Record ID', record.id || '—'],
      ['Record type', record.type || record.kind || '—'],
      ['Freshness', record.freshness || 'source supplied'],
      ['License', record.license || 'See source terms']
    ];
  }

  function inspectRecord(record, root) {
    const dialog = root.querySelector('[data-record-dialog]');
    if (!dialog || typeof dialog.showModal !== 'function') {
      w.alert(`${record.title}\n\n${record.summary || record.abstract || ''}`);
      return;
    }

    dialog.querySelector('[data-dialog-source]').textContent = `${record.source || 'Scientific source'} / ${record.domain || 'Record'}`;
    dialog.querySelector('[data-dialog-title]').textContent = record.title || 'Scientific record';
    dialog.querySelector('[data-dialog-summary]').textContent = record.summary || record.abstract || 'No summary supplied by the source.';
    dialog.querySelector('[data-dialog-meta]').innerHTML = recordMeta(record)
      .map(([key, value]) => `<div><dt>${U.esc(key)}</dt><dd>${U.esc(value)}</dd></div>`)
      .join('');

    const sourceLink = dialog.querySelector('[data-dialog-open-source]');
    sourceLink.href = record.url || '#';
    sourceLink.hidden = !record.url;

    const siteLink = dialog.querySelector('[data-dialog-site-intelligence]');
    const latitude = record.location?.latitude;
    const longitude = record.location?.longitude;
    const route = w.SCLabConfig?.routes?.siteIntelligence;
    if (route && Number.isFinite(Number(latitude)) && Number.isFinite(Number(longitude))) {
      const destination = new URL(route, w.location.href);
      destination.searchParams.set('lat', latitude);
      destination.searchParams.set('lon', longitude);
      destination.searchParams.set('source', record.source || 'Lab');
      destination.searchParams.set('record', record.id || '');
      siteLink.href = destination.toString();
      siteLink.hidden = false;
    } else {
      siteLink.hidden = true;
    }

    dialog.showModal();
  }

  function saveObservation(record, projects, root) {
    projects.add('observations', { title:record.title, source:record.source, domain:record.domain, observedAt:record.observedAt, retrievedAt:record.retrievedAt, location:record.location||null, record }, `Observation saved: ${record.title}`);
    projects.add('sourceSnapshots', { source:record.source, retrievedAt:record.retrievedAt, connectorId:record.connectorId||'', recordId:record.id, provenance:record.provenance||{} }, null);
    U.toast(root, 'Observation saved to the project.');
  }

  function saveEvidence(record, projects, root) {
    projects.add('evidence', {
      title: record.title,
      summary: record.summary || record.abstract || '',
      source: record.source,
      url: record.url,
      observedAt: record.observedAt,
      retrievedAt: record.retrievedAt,
      record,
      status: 'unreviewed'
    }, `Evidence saved: ${record.title}`);
    U.toast(root, 'Saved to evidence inbox.');
  }

  function citeNotebook(record, projects, root) {
    projects.add('citations', { title:record.title, source:record.source, url:record.url, observedAt:record.observedAt, retrievedAt:record.retrievedAt }, null);
    projects.add('notes', {
      type: 'source-citation',
      title: record.title,
      body: `Source: ${record.source}\nURL: ${record.url || ''}\nObserved: ${record.observedAt || ''}\nRetrieved: ${record.retrievedAt || ''}\n\n${record.summary || record.abstract || ''}`,
      tags: ['source', String(record.domain || 'science').toLowerCase()]
    }, `Notebook citation added: ${record.title}`);
    U.toast(root, 'Citation added to notebook.');
  }

  function createExperiment(record, projects, root) {
    projects.add('experiments', {
      title: `Investigate: ${record.title}`,
      question: `What can be learned or tested from this ${record.domain || 'scientific'} record?`,
      hypothesis: '',
      method: `Review the source record, identify measurable variables, define controls or comparison data, and document the analysis method.\n\nSource: ${record.url || record.source}`,
      status: 'planned',
      sourceRecord: record
    }, `Experiment created from scientific signal: ${record.title}`);
    U.toast(root, 'Experiment created from signal.');
  }

  function card(record, projects, root, options = {}) {
    const el = d.createElement('article');
    el.className = options.compact ? 'sc-lab-signal-row' : 'sc-lab-feed-card';

    if (options.compact) {
      el.innerHTML = `
        <div class="sc-lab-signal-source">${U.esc(record.source || 'Source')}</div>
        <div class="sc-lab-signal-copy"><strong>${U.esc(record.title)}</strong><span>${U.esc(record.domain || 'Science')} · ${U.esc(U.fmt(record.observedAt))}</span></div>
        <div class="sc-lab-signal-actions"><button class="sc-lab-text-button" data-inspect>Inspect</button><button class="sc-lab-text-button" data-save-evidence>Save</button></div>`;
    } else {
      const image = record.thumbnail ? `<img loading="lazy" src="${U.esc(record.thumbnail)}" alt="">` : '';
      const sourceLink = record.url ? `<a class="sc-lab-text-button" href="${U.esc(record.url)}" target="_blank" rel="noopener">Open source</a>` : '';
      const routed = (key,label) => {
        const route = w.SCLabConfig?.routes?.[key];
        if (!route) return '';
        const destination = new URL(route, w.location.href);
        destination.searchParams.set('source', record.source || 'Lab');
        destination.searchParams.set('record', record.id || '');
        destination.searchParams.set('title', record.title || '');
        if (Number.isFinite(Number(record.location?.latitude))) destination.searchParams.set('lat', record.location.latitude);
        if (Number.isFinite(Number(record.location?.longitude))) destination.searchParams.set('lon', record.location.longitude);
        return `<a class="sc-lab-button" href="${U.esc(destination.toString())}">${U.esc(label)}</a>`;
      };
      el.innerHTML = `
        ${image}
        <div class="sc-lab-feed-card-body">
          <span class="sc-lab-feed-domain">${U.esc(record.domain || 'Science')}</span>
          <h4>${U.esc(record.title)}</h4>
          <p>${U.esc((record.summary || record.abstract || '').slice(0, 330))}</p>
          <div class="sc-lab-feed-meta">${U.esc(record.source)} · ${U.esc(U.fmt(record.observedAt))}</div>
        </div>
        <div class="sc-lab-card-actions">
          <button class="sc-lab-button" data-inspect>Inspect</button>
          ${sourceLink}
          <button class="sc-lab-button" data-save-observation>Save observation</button>
          <button class="sc-lab-button" data-save-evidence>Save evidence</button>
          <button class="sc-lab-button" data-cite-note>Notebook</button>
          <button class="sc-lab-button" data-open-dataset>Inspect dataset</button>
          ${routed('siteIntelligence','Site Intelligence')}
          ${routed('decisionStudio','Decision Studio')}
          ${routed('workbench','Workbench')}
          <button class="sc-lab-button sc-lab-button-primary" data-create-experiment>Create experiment</button>
        </div>`;
    }

    el.querySelector('[data-inspect]')?.addEventListener('click', () => inspectRecord(record, root));
    el.querySelector('[data-save-observation]')?.addEventListener('click', () => saveObservation(record, projects, root));
    el.querySelector('[data-save-evidence]')?.addEventListener('click', () => saveEvidence(record, projects, root));
    el.querySelector('[data-cite-note]')?.addEventListener('click', () => citeNotebook(record, projects, root));
    el.querySelector('[data-open-dataset]')?.addEventListener('click', () => root.dispatchEvent(new CustomEvent('sc-lab:dataset',{detail:{records:[record],title:record.title,source:record.source}})));
    el.querySelector('[data-create-experiment]')?.addEventListener('click', () => createExperiment(record, projects, root));
    return el;
  }

  function render(target, records, projects, root, options = {}) {
    target.innerHTML = '';
    if (!records?.length) {
      target.innerHTML = '<div class="sc-lab-data-note">No records returned.</div>';
      return;
    }
    records.forEach(record => target.appendChild(card(record, projects, root, options)));
  }

  Lab.Feeds = { load, render, card, inspectRecord, saveObservation, saveEvidence, citeNotebook, createExperiment };
})(window, document);
;

/* === assets/js/modules/project-workspace-v0280.js === */
(function(W,D){'use strict';
 const Lab=W.SCLab=W.SCLab||{},VERSION='0.28.0';
 const state={version:VERSION,mounted:false,ready:false,lastError:null,lastAction:null};
 const root=()=>D.querySelector('[data-lab-module="project-workspace"]');
 const field=n=>root()?.querySelector(`[data-workspace-v0280-${n}]`);
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const app=()=>root()?.closest('.sc-lab-app');
 const store=()=>app()?._scLabProjects||(typeof Lab.Projects==='function'?new Lab.Projects():null);
 function announce(message,tone='ready'){const n=field('status');if(n){n.textContent=message;n.dataset.tone=tone;}Lab.InterfaceV0265?.announce?.(message,tone);}
 function types(project){return [...new Set((project?.recordIndex||[]).map(r=>r.recordType))].sort();}
 function renderMetrics(project,projects){const d=projects.diagnostics();field('metrics').innerHTML=[['Workspace schema',d.version],['Projects',d.projectCount],['Indexed records',d.recordCount],['Relationships',d.relationshipCount],['Checkpoints',d.checkpointCount],['Storage',d.storageMode]].map(([a,b])=>`<article><span>${esc(a)}</span><strong>${esc(b)}</strong></article>`).join('');field('migration').innerHTML=`<strong>${project.workspace?.migrationState==='current'?'Current':'Migration required'}</strong><span>Project schema ${esc(project.schemaVersion)} · legacy baseline ${esc(project.legacySchemaVersion||'none')}</span><small>${(project.migrationHistory||[]).length} migration record(s); unknown fields are preserved.</small>`;field('storage').textContent=`${d.bytes.toLocaleString()} bytes in ${d.storageMode}; last saved ${d.lastSavedAt||'not recorded'}.`;}
 function renderRecords(project,projects){const q=field('search').value||'',type=field('type').value||'';const rows=projects.search(q,{type});field('record-count').textContent=`${rows.length} record${rows.length===1?'':'s'}`;field('records').innerHTML=rows.slice(0,250).map(row=>`<tr><td><strong>${esc(row.title)}</strong><small>${esc(row.id)}</small></td><td>${esc(row.recordType)}</td><td>${esc(row.collection)}</td><td>${esc(row.status)}</td><td>${esc(row.updatedAt||'')}</td></tr>`).join('')||'<tr><td colspan="5">No matching records.</td></tr>';const current=field('type').value;field('type').innerHTML='<option value="">All record types</option>'+types(project).map(t=>`<option value="${esc(t)}">${esc(t)}</option>`).join('');field('type').value=current;}
 function renderCheckpoints(project){const rows=project.projectCheckpoints||[];field('checkpoints').innerHTML=rows.map(cp=>`<article><div><strong>${esc(cp.label)}</strong><span>${esc(cp.createdAt)} · ${esc(cp.recordCount)} records</span></div><button type="button" class="sc-lab-button" data-restore-checkpoint="${esc(cp.id)}">Restore</button></article>`).join('')||'<div class="sc-lab-data-note">No checkpoints yet.</div>';}
 function renderRelationships(project){const idx=project.recordIndex||[],opts=idx.slice(0,500).map(r=>`<option value="${esc(r.id)}">${esc(r.title)} · ${esc(r.recordType)}</option>`).join('');['from','to'].forEach(n=>{const s=field(n),v=s.value;s.innerHTML='<option value="">Choose a record</option>'+opts;s.value=v;});field('relationships').innerHTML=(project.relationships||[]).slice(0,100).map(r=>{const a=idx.find(x=>x.id===r.from),b=idx.find(x=>x.id===r.to);return `<article><span><strong>${esc(a?.title||r.from)}</strong> ${esc(r.type)} <strong>${esc(b?.title||r.to)}</strong></span><button type="button" class="sc-lab-button" data-remove-relationship="${esc(r.id)}">Remove</button></article>`;}).join('')||'<div class="sc-lab-data-note">No record relationships yet.</div>';}
 function render(){const projects=store(),project=projects?.get();if(!projects||!project)return;renderMetrics(project,projects);renderRecords(project,projects);renderCheckpoints(project);renderRelationships(project);field('project-name').textContent=project.name;state.ready=true;announce(`Project workspace ready with ${project.recordIndex.length} indexed records.`);}
 function bind(){const projects=store();if(!projects)throw new Error('Project store is unavailable.');field('search').addEventListener('input',()=>renderRecords(projects.get(),projects));field('type').addEventListener('change',()=>renderRecords(projects.get(),projects));field('checkpoint').addEventListener('click',()=>{const label=W.prompt('Checkpoint label','Manual checkpoint');if(!label)return;projects.createCheckpoint(label,'manual');state.lastAction='checkpoint';render();});field('export').addEventListener('click',()=>{projects.exportBundle();state.lastAction='export';announce('Project bundle exported.');});field('migrate').addEventListener('click',()=>{projects.migrateAll();state.lastAction='migration';render();announce('All local projects were normalized to schema 0.28.0.');});field('relationship-add').addEventListener('click',()=>{try{projects.link(field('from').value,field('to').value,field('relationship-type').value||'related-to');state.lastAction='relationship';render();}catch(e){announce(e.message,'error');}});field('import').addEventListener('click',()=>field('file').click());field('file').addEventListener('change',async e=>{const f=e.target.files?.[0];if(!f)return;try{projects.import(await f.text(),'copy');state.lastAction='import';render();announce('Project bundle imported as a copy.');}catch(err){announce(err.message,'error');}e.target.value='';});root().addEventListener('click',e=>{const restore=e.target.closest('[data-restore-checkpoint]');if(restore&&W.confirm('Restore this checkpoint? Current project records will be replaced, while checkpoint history is preserved.')){try{projects.restoreCheckpoint(restore.dataset.restoreCheckpoint);state.lastAction='restore';render();}catch(err){announce(err.message,'error');}}const remove=e.target.closest('[data-remove-relationship]');if(remove){projects.unlink(remove.dataset.removeRelationship);render();}});projects.onChange(()=>render());}
 function mount(){const r=root();if(!r||r.dataset.workspaceV0280Mounted==='1')return false;r.dataset.workspaceV0280Mounted='1';try{bind();render();state.mounted=true;return true;}catch(e){state.lastError=e.message;announce(e.message,'error');return false;}}
 const observer=new MutationObserver(()=>mount());observer.observe(D.documentElement,{childList:true,subtree:true});if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',mount);else mount();
 Lab.ProjectWorkspaceV0280={mount,status:()=>({...state,diagnostics:store()?.diagnostics?.()||null})};W.SCLabProjectWorkspaceV0280=Lab.ProjectWorkspaceV0280;
})(window,document);
;

/* === assets/js/sc-lab-navigation-recovery-v015201.js === */
(function(w,d){'use strict';
  const VERSION='0.152.0.3';
  function roots(){return Array.from(d.querySelectorAll('.sc-lab-app'));}
  function canonical(id){return w.SCLabRuntimeV02631?.resolveModule?.(id)||String(id||'overview');}
  function open(root,id){
    id=canonical(id);
    const panels=Array.from(root.querySelectorAll('[data-lab-module]'));
    const panel=panels.find(p=>p.dataset.labModule===id);
    if(!panel){w.SCLabRuntimeV02631?.navigate?.(id);return false;}
    panels.forEach(p=>{p.hidden=p!==panel;});
    root.querySelectorAll('[data-lab-module-button]').forEach(b=>b.classList.toggle('is-active',canonical(b.dataset.labModuleButton)===id));
    root.dataset.activeModule=id;
    root.dispatchEvent(new CustomEvent('sc-lab:module-opened',{detail:{module:id,recovery:true,version:VERSION}}));
    root.querySelector('[data-lab-nav]')?.classList.remove('is-open');
    root.querySelector('[data-lab-nav-toggle]')?.setAttribute('aria-expanded','false');
    try{panel.scrollIntoView({block:'start'});}catch(_){}
    return true;
  }
  function bind(root){
    if(root.dataset.scLabNavigationRecoveryBound==='1')return;
    root.dataset.scLabNavigationRecoveryBound='1';
    root.addEventListener('click',e=>{
      const b=e.target.closest('[data-lab-module-button],[data-open-module]');
      if(!b||!root.contains(b))return;
      // The full app owns navigation once it is healthy. Recovery only intervenes if it has not booted.
      if(root.dataset.scLabAppReady==='1'&&root.dataset.scLabAppFailed!=='1')return;
      const id=b.dataset.labModuleButton||b.dataset.openModule;
      if(id){e.preventDefault();open(root,id);}
    },true);
    root.dataset.scLabNavigationRecoveryVersion=VERSION;
    root.dataset.scLabPanelRetentionRecovery='1';
  }
  function boot(){roots().forEach(bind);}
  if(d.readyState==='loading')d.addEventListener('DOMContentLoaded',boot,{once:true}); else boot();
  d.addEventListener('sc-lab:app-error',e=>{const r=e.detail?.root;if(r){bind(r);r.dataset.scLabNavigationRecoveryActive='1';}});
  w.SCLabNavigationRecoveryV015201={version:VERSION,open,bind,status:()=>({version:VERSION,roots:roots().length,ready:roots().filter(r=>r.dataset.scLabAppReady==='1').length,failed:roots().filter(r=>r.dataset.scLabAppFailed==='1').length})};
})(window,document);
;

/* === assets/js/sc-lab-app.js === */
(function (w, d) {
  'use strict';

  const Lab = w.SCLab;
  const U = Lab.util;

  const missingClassList = Object.freeze({ add() {}, remove() {}, toggle() { return false; }, contains() { return false; } });
  const missingStyle = new Proxy({}, { get() { return ''; }, set() { return true; } });
  const missingElement = new Proxy({
    value: '', checked: false, disabled: false, hidden: true, files: [], children: [], options: [],
    dataset: {}, style: missingStyle, classList: missingClassList, innerHTML: '', textContent: '',
    addEventListener() {}, removeEventListener() {}, appendChild() {}, add() {}, remove() {}, click() {}, focus() {}, select() {},
    setAttribute() {}, removeAttribute() {}, getAttribute() { return null; }, dispatchEvent() { return false; },
    insertAdjacentHTML() {}, contains() { return false; }, closest() { return null; }, querySelectorAll() { return []; },
    getBoundingClientRect() { return { width: 0, height: 0, top: 0, left: 0, right: 0, bottom: 0 }; }
  }, { get(target, property) { if (property === 'querySelector') return () => missingElement; return property in target ? target[property] : undefined; }, set(target, property, value) { target[property] = value; return true; } });

  function qs(root, selector) { return root?.querySelector?.(selector) || missingElement; }
  function qsa(root, selector) { return root?.querySelectorAll ? [...root.querySelectorAll(selector)] : []; }
  function canonicalModule(id) { return w.SCLabRuntimeV02631?.resolveModule?.(id) || String(id || 'overview'); }
  function workspaceApi() {
    if (Lab.Workspace) return Lab.Workspace;
    return {
      traceCounts() { return []; },
      projectTotal(project) {
        if (!project || typeof project !== 'object') return 0;
        return Object.values(project).reduce((total, value) => total + (Array.isArray(value) ? value.length : 0), 0);
      },
      search() { return []; },
      quickTools: []
    };
  }
  function empty(text) { return `<div class="sc-lab-data-note">${U.esc(text)}</div>`; }
  function reportRuntimeError(scope, error, metadata = {}) {
    if (w.SCLabRuntimeV02631?.recordError) return w.SCLabRuntimeV02631.recordError(scope, error, metadata);
    try { console.error('[Sustainable Catalyst Lab]', scope, error, metadata); } catch (_) {}
    return null;
  }

  function promptRecord(fields) {
    const record = {};
    for (const [key, title, defaultValue = ''] of fields) {
      const value = w.prompt(title, defaultValue);
      if (value === null) return null;
      record[key] = value;
    }
    return record;
  }

  function listHTML(title, body, time, meta = '') {
    return `<article class="sc-lab-list-item">
      <header><h5>${U.esc(title)}</h5><time>${U.esc(U.fmt(time))}</time></header>
      ${body ? `<p>${U.esc(body)}</p>` : ''}
      ${meta ? `<span class="sc-lab-list-meta">${U.esc(meta)}</span>` : ''}
    </article>`;
  }

  function csvCell(value) {
    const text = String(value ?? '');
    return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  }

  function init(root) {
    if (!root || root.dataset.scLabAppInitialized === '1') return;
    root.dataset.scLabAppInitialized = '1';
    const projects = new Lab.Projects();
    root._scLabProjects = projects;
    root.dataset.scLabRuntimeState = root.dataset.scLabRuntimeState || 'initializing';
    root.dataset.scLabBootstrapVersion = '0.152.0.4';
    const config = w.SCLabConfig || {};
    const initial = root.dataset.initialModule || 'overview';
    const observeOwned = !!w.SCLabObserveDomainV02633?.owns?.(initial);
    const select = qs(root, '[data-lab-project-select]');
    const file = qs(root, '[data-lab-import-file]');
    const nav = qs(root, '[data-lab-nav]');
    const navToggle = qs(root, '[data-lab-nav-toggle]');
    const commandInput = qs(root, '[data-lab-command-input]');
    const commandResults = qs(root, '[data-lab-command-results]');
    let currentDocument = null;
    let overviewLoaded = false;
    let currentDataset = null;
    let currentFeedRecords = [];
    let currentSpaceRecords = [];
    let currentMarineRecords = [];
    let spectrum = [];

    function renderSelect() {
      select.innerHTML = '';
      projects.items.forEach(project => {
        const option = d.createElement('option');
        option.value = project.id;
        option.textContent = project.name;
        option.selected = project.id === projects.activeId;
        select.appendChild(option);
      });
    }

    function closeMobileNav() {
      nav.classList.remove('is-open');
      navToggle?.setAttribute('aria-expanded', 'false');
    }

    function openModule(id, options = {}) {
      id = canonicalModule(id);
      const exists = qsa(root, '[data-lab-module]').find(panel => panel.dataset.labModule === id);
      if (!exists) {
        if (w.SCLabRuntimeV02631?.navigate) w.SCLabRuntimeV02631.navigate(id);
        return;
      }
      qsa(root, '[data-lab-module]').forEach(panel => { panel.hidden = panel.dataset.labModule !== id; });
      qsa(root, '[data-lab-module-button]').forEach(button => button.classList.toggle('is-active', button.dataset.labModuleButton === id));
      root.dataset.activeModule = id;
      root.dispatchEvent(new CustomEvent('sc-lab:module-opened', { detail: { module: id } }));
      closeMobileNav();

      if (id === 'overview') renderOverview();
      if (id === 'activity') renderActivity();
      if (id === 'experiments') renderExperiments();
      if (id === 'evidence-decisions') renderEvidence();
      if (id === 'notebook') renderNotes();
      if (id === 'system-status') runStatus(false);
      if (id === 'source-registry') loadSourceRegistry();
      if (id === 'dataset-inspector') renderDataset();
      if (options.focus) requestAnimationFrame(() => options.focus.focus());
    }

    function setTab(buttonSelector, buttonData, paneSelector, paneData, value) {
      qsa(root, buttonSelector).forEach(button => button.classList.toggle('is-active', button.dataset[buttonData] === value));
      qsa(root, paneSelector).forEach(pane => { pane.hidden = pane.dataset[paneData] !== value; });
    }

    function openTool(id) {
      const item = workspaceApi().quickTools?.find?.(tool => tool.id === id)
        || { kind: 'calculator', module: 'science-engineering', calculatorId: id };
      openModule(item.module);
      if (item.kind === 'chem-tab') setTab('[data-chem-tab]', 'chemTab', '[data-chem-pane]', 'chemPane', item.tab);
      if (item.kind === 'analysis-tab') setTab('[data-analysis-tab]', 'analysisTab', '[data-analysis-pane]', 'analysisPane', item.tab);
      if (item.kind === 'physics-tab') setTab('[data-physics-tab]', 'physicsTab', '[data-physics-pane]', 'physicsPane', item.tab);
      if (item.kind === 'biology-tab') setTab('[data-biology-tab]', 'biologyTab', '[data-biology-pane]', 'biologyPane', item.tab);
      if (item.kind === 'astronomy-tab') setTab('[data-astronomy-tab]', 'astronomyTab', '[data-astronomy-pane]', 'astronomyPane', item.tab);
      if (item.kind === 'materials-tab') setTab('[data-materials-tab]', 'materialsTab', '[data-materials-pane]', 'materialsPane', item.tab);
      if (item.kind === 'earth-tab') setTab('[data-earth-tab]', 'earthTab', '[data-earth-pane]', 'earthPane', item.tab);
      if (item.kind === 'energy-tab') setTab('[data-energy-tab]', 'energyTab', '[data-energy-pane]', 'energyPane', item.tab);
      if (item.kind === 'calculator') {
        setTab('[data-analysis-tab]', 'analysisTab', '[data-analysis-pane]', 'analysisPane', 'calculators');
        selectCalculator(item.calculatorId);
      }
    }

    function executeCommand(item) {
      commandInput.value = '';
      commandResults.hidden = true;
      if (item.kind === 'module') openModule(item.id);
      else if (item.kind === 'calculator') openTool(item.calculatorId || item.id);
      else openTool(item.id);
    }

    function renderCommandResults(query) {
      const matches = workspaceApi().search ? workspaceApi().search(query, Lab.Calculators?.definitions || []) : [];
      if (!query.trim() || !matches.length) {
        commandResults.hidden = true;
        commandResults.innerHTML = '';
        return;
      }
      commandResults.innerHTML = matches.map((item, index) => `
        <button type="button" data-command-index="${index}">
          <span>${U.esc(item.label)}</span>
          <small>${U.esc(item.group || item.kind || 'Lab')}</small>
        </button>`).join('');
      commandResults.hidden = false;
      qsa(commandResults, '[data-command-index]').forEach(button => {
        button.addEventListener('click', () => executeCommand(matches[Number(button.dataset.commandIndex)]));
      });
    }

    function createExperiment(seed = {}) {
      const record = promptRecord([
        ['title', 'Experiment title', seed.title || 'New experiment'],
        ['question', 'Research question', seed.question || ''],
        ['hypothesis', 'Hypothesis', seed.hypothesis || ''],
        ['method', 'Method or procedure', seed.method || '']
      ]);
      if (!record) return;
      projects.add('experiments', { ...record, status: 'planned' }, `Experiment created: ${record.title}`);
      U.toast(root, 'Experiment added to the project.');
    }

    function createNote(seed = {}) {
      const record = promptRecord([
        ['title', 'Notebook entry title', seed.title || 'Lab note'],
        ['body', 'Observation or note', seed.body || ''],
        ['tagsText', 'Tags, comma separated', seed.tagsText || 'observation']
      ]);
      if (!record) return;
      projects.add('notes', {
        type: seed.type || 'observation',
        title: record.title,
        body: record.body,
        tags: record.tagsText.split(',').map(tag => tag.trim()).filter(Boolean)
      }, `Notebook entry added: ${record.title}`);
      U.toast(root, 'Notebook entry saved.');
    }

    function createObservation() {
      const record = promptRecord([
        ['title', 'Observation title', 'Scientific observation'],
        ['body', 'What was observed?', ''],
        ['conditions', 'Conditions, instrument, or context', '']
      ]);
      if (!record) return;
      projects.add('notes', {
        type: 'observation',
        title: record.title,
        body: `${record.body}${record.conditions ? `\n\nConditions: ${record.conditions}` : ''}`,
        tags: ['observation']
      }, `Observation recorded: ${record.title}`);
      U.toast(root, 'Observation added to the notebook.');
    }

    function handleQuickAction(action) {
      if (action === 'experiment') createExperiment();
      if (action === 'note') createNote();
      if (action === 'observation') createObservation();
    }

    function metricHTML(label, value, module) {
      return `<button type="button" class="sc-lab-metric" data-open-module="${U.esc(module)}"><strong>${value}</strong><span>${U.esc(label)}</span></button>`;
    }

    function renderTrace() {
      const target = qs(root, '[data-traceability]');
      target.innerHTML = workspaceApi().traceCounts(projects.get()).map((stage, index, rows) => `
        <button type="button" class="sc-lab-trace-stage" data-open-module="${U.esc(stage.module)}" data-trace-key="${U.esc(stage.key)}">
          <strong>${stage.value}</strong><span>${U.esc(stage.label)}</span>
        </button>${index < rows.length - 1 ? '<span class="sc-lab-trace-arrow" aria-hidden="true">→</span>' : ''}`
      ).join('');
    }

    function renderProjectWork() {
      const project = projects.get();
      const experiments = project.experiments.slice(0, 3).map(item => ({
        title: item.title || 'Untitled experiment',
        body: item.question || item.method || '',
        time: item.createdAt,
        meta: `Experiment · ${item.status || 'planned'}`
      }));
      const calculations = project.calculations.slice(0, 3).map(item => ({
        title: item.type || 'Calculation',
        body: item.calculatorId ? `Calculator: ${item.calculatorId}` : '',
        time: item.createdAt,
        meta: 'Calculation'
      }));
      const biology = project.biologyRecords.slice(0, 3).map(item => ({
        title: item.type || 'Biology analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Biology'
      }));
      const astronomy = project.astronomyRecords.slice(0, 3).map(item => ({
        title: item.type || 'Astronomy analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Astronomy'
      }));
      const materials = project.materialsRecords.slice(0, 3).map(item => ({
        title: item.type || 'Materials analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Materials'
      }));
      const earth = project.earthRecords.slice(0, 3).map(item => ({
        title: item.type || 'Earth systems analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Earth systems'
      }));
      const energy = project.energyRecords.slice(0, 3).map(item => ({
        title: item.type || 'Energy and engineering analysis',
        body: item.methodId ? `Method: ${item.methodId}` : '',
        time: item.createdAt || item.recordedAt,
        meta: 'Energy & engineering'
      }));
  const electrical = project.electricalRecords.slice(0, 3).map(item => ({
  title: item.type || 'Electrical and embedded analysis',
  body: item.methodId ? `Method: ${item.methodId}` : '',
  time: item.createdAt || item.recordedAt,
  meta: 'Electrical & embedded'
  }));
  const mechanical = project.mechanicalThermalAnalyses.slice(0, 3).map(item => ({
  title: item.title || item.type || 'Mechanical and thermal analysis',
  body: item.methodId ? `Method: ${item.methodId}` : '',
  time: item.createdAt || item.recordedAt || item.audit?.createdAt,
  meta: 'Mechanical & thermal'
  }));
      const rows = [...experiments, ...calculations, ...biology, ...astronomy, ...materials, ...earth, ...energy, ...electrical, ...mechanical]
        .sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
        .slice(0, 5);
      qs(root, '[data-project-work]').innerHTML = rows.length
        ? rows.map(row => listHTML(row.title, row.body, row.time, row.meta)).join('')
        : empty('No experiments or calculations have been recorded.');
    }

    function renderOverview() {
      const project = projects.get();
      const counts = [
        ['Models', (project.models || []).length, 'model-studio'],
        ['Figures', (project.visualizations || []).length, 'graph-studio'],
        ['Datasets', (project.datasets || []).length, 'dataset-registry'],
        ['Experiments', (project.experiments || []).length, 'experiments'],
        ['Evidence', (project.evidence || []).length, 'evidence-decisions'],
        ['Notes', (project.notes || []).length, 'notebook']
      ];
      qs(root, '[data-overview-metrics]').innerHTML = counts.map(([label, value, module]) => metricHTML(label, value, module)).join('');
      qs(root, '[data-recent-activity]').innerHTML = project.activity.slice(0, 8).map(item => listHTML(item.text, '', item.at)).join('') || empty('No project activity yet.');
      renderProjectWork();
      renderTrace();
      qs(root, '[data-overview-empty]').hidden = workspaceApi().projectTotal(project) > 0;
      if (!overviewLoaded && config.features?.feeds !== false) loadOverviewSignals();
    }

    async function loadOverviewSignals() {
      const target = qs(root, '[data-overview-signals]');
      overviewLoaded = true;
      if (!Lab.Feeds || typeof Lab.Feeds.load !== 'function') {
        target.innerHTML = empty('Scientific signals are still loading. Core Lab navigation is ready.');
        return;
      }
      target.innerHTML = '<div class="sc-lab-data-note">Retrieving concise scientific signals…</div>';
      const requests = [
        ['usgs-earthquakes', '', 2],
        ['nasa-eonet', '', 2],
        ['nasa-space-telescopes', 'James Webb Hubble', 2],
        ['obis-marine', 'Cetacea', 2],
        ['pubmed-science', 'environmental monitoring OR materials science', 2],
        ['arxiv-physics', 'all:physics OR all:materials', 2]
      ];
      const results = await Promise.allSettled(requests.map(args => Lab.Feeds.load(...args)));
      const records = results.flatMap(result => result.status === 'fulfilled' ? (result.value.records || []) : []);
      if (!records.length) {
        target.innerHTML = empty('Live signals are temporarily unavailable. Open Scientific signals to query an individual source.');
        return;
      }
      records.sort((a, b) => String(b.observedAt || '').localeCompare(String(a.observedAt || '')));
      Lab.Feeds.render(target, records.slice(0, 8), projects, root, { compact: true });
    }

    function renderActivity() {
      const filter = (qs(root, '[data-activity-filter]')?.value || '').toLowerCase();
      const limit = Number(qs(root, '[data-activity-limit]')?.value || 50);
      const rows = projects.get().activity
        .filter(item => !filter || String(item.text || '').toLowerCase().includes(filter))
        .slice(0, limit);
      qs(root, '[data-activity-list]').innerHTML = rows.map(item => listHTML(item.text, '', item.at)).join('') || empty('No matching activity.');
    }

    function renderExperiments() {
      const rows = projects.get().experiments;
      qs(root, '[data-experiment-list]').innerHTML = rows.map(item => listHTML(item.title, item.question || item.method, item.createdAt, item.status || 'planned')).join('') || empty('No experiments recorded.');
    }

    function renderEvidence() {
      const project = projects.get();
      qs(root, '[data-evidence-list]').innerHTML = project.evidence.map(item => listHTML(item.title, item.summary, item.createdAt, `${item.source || 'Source'} · ${item.status || 'unreviewed'}`)).join('') || empty('No evidence saved.');
      qs(root, '[data-hypothesis-list]').innerHTML = project.hypotheses.map(item => listHTML(item.title, item.statement, item.createdAt, item.status || 'proposed')).join('') || empty('No hypotheses recorded.');
      qs(root, '[data-decision-list]').innerHTML = project.decisions.map(item => listHTML(item.title, item.rationale, item.createdAt, item.status || 'draft')).join('') || empty('No decisions recorded.');
    }

    function renderNotes() {
      const query = (qs(root, '[data-note-filter]').value || '').toLowerCase();
      const rows = projects.get().notes.filter(item => {
        const text = `${item.title || ''} ${item.body || ''} ${(item.tags || []).join(' ')}`.toLowerCase();
        return !query || text.includes(query);
      });
      qs(root, '[data-note-list]').innerHTML = rows.map(item => listHTML(item.title, item.body, item.createdAt, `${item.type || 'note'} · ${(item.tags || []).join(', ')}`)).join('') || empty('No notebook entries match this filter.');
    }

    function renderSelectAndViews() {
      renderSelect();
      renderOverview();
      if (root.dataset.activeModule === 'activity') renderActivity();
      if (root.dataset.activeModule === 'experiments') renderExperiments();
      if (root.dataset.activeModule === 'evidence-decisions') renderEvidence();
      if (root.dataset.activeModule === 'notebook') renderNotes();
      updateDocStale();
      populateDatasetSelect();
    }

    qsa(root, '[data-lab-module-button]').forEach(button => button.addEventListener('click', () => openModule(button.dataset.labModuleButton)));
    root.addEventListener('click', event => {
      const moduleButton = event.target.closest('[data-open-module]');
      if (moduleButton && root.contains(moduleButton)) openModule(moduleButton.dataset.openModule);
      const quickTool = event.target.closest('[data-quick-tool]');
      if (quickTool && root.contains(quickTool)) openTool(quickTool.dataset.quickTool);
      const commandAction = event.target.closest('[data-command-action]');
      if (commandAction && root.contains(commandAction)) handleQuickAction(commandAction.dataset.commandAction);
    });

    navToggle?.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(open));
    });

    qsa(root, '[data-route]').forEach(link => { link.href = config.routes?.[link.dataset.route] || '#'; });
    select.addEventListener('change', () => projects.select(select.value));
    qs(root, '[data-lab-action="new-project"]').addEventListener('click', () => {
      const name = w.prompt('Project name', 'New Lab Project');
      if (name) { projects.create(name); U.toast(root, 'Project created.'); }
    });
    qs(root, '[data-lab-action="export-project"]').addEventListener('click', () => projects.export());
    qs(root, '[data-lab-action="import-project"]').addEventListener('click', () => file.click());
    file.addEventListener('change', () => {
      const selectedFile = file.files[0];
      if (!selectedFile) return;
      selectedFile.text().then(text => {
        projects.import(text);
        U.toast(root, 'Project imported.');
      }).catch(error => U.toast(root, error.message));
      file.value = '';
    });
    projects.onChange(renderSelectAndViews);

    commandInput.addEventListener('input', () => renderCommandResults(commandInput.value));
    commandInput.addEventListener('keydown', event => {
      if (event.key === 'Escape') { commandResults.hidden = true; commandInput.blur(); }
      if (event.key === 'Enter') {
        const first = qs(commandResults, '[data-command-index="0"]');
        if (first) { event.preventDefault(); first.click(); }
      }
    });
    d.addEventListener('keydown', event => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        commandInput.focus();
        commandInput.select();
      }
      if (event.key === '/' && !/input|textarea|select/i.test(d.activeElement?.tagName || '')) {
        event.preventDefault();
        commandInput.focus();
      }
    });
    d.addEventListener('click', event => {
      if (!root.contains(event.target) || !event.target.closest('.sc-lab-command-search')) commandResults.hidden = true;
    });

    qs(root, '[data-overview-refresh]').addEventListener('click', () => { overviewLoaded = false; loadOverviewSignals(); });

    // Scientific feeds.
    async function feedTo(source, query, limit, target, status) {
      if (status) status.textContent = 'Loading scientific source…';
      try {
        let records = [], retrievedAt = U.now(), cached = false;
        if (source === 'all-science') {
          records = await Lab.Observations.loadBoard();
        } else {
          const data = await Lab.Feeds.load(source, query, limit);
          records = data.records || []; retrievedAt = data.retrievedAt; cached = !!data.cached;
        }
        currentFeedRecords = records;
        Lab.Feeds.render(target, records, projects, root);
        qs(root,'[data-feed-to-dataset]').disabled = !records.length;
        qs(root,'[data-save-query]').disabled = !records.length;
        if (status) status.textContent = `${records.length} records · ${source==='all-science'?'multi-source board':cached?'cached':'live retrieval'} · ${U.fmt(retrievedAt)}`;
        return records;
      } catch (error) { target.innerHTML=empty(error.message); if(status)status.textContent=error.message; return []; }
    }

    const feedSource = qs(root, '[data-feed-source]');
    const feedQuery = qs(root, '[data-feed-query]');
    const feedLimit = qs(root, '[data-feed-limit]');
    const feedTarget = qs(root, '[data-feed-results]');
    const feedStatus = qs(root, '[data-feed-status]');
    const runFeed = () => feedTo(feedSource.value, feedQuery.value, Number(feedLimit.value), feedTarget, feedStatus);
    if (!observeOwned) {
      qs(root, '[data-feed-run]').addEventListener('click', runFeed);
      qs(root, '[data-feed-refresh]').addEventListener('click', runFeed);
      qs(root, '[data-space-load]').addEventListener('click', async () => { const telescope=qs(root,'[data-space-telescope]').value; const query=`${telescope==='all'?'':telescope+' '} ${qs(root,'[data-space-query]').value}`.trim(); currentSpaceRecords=await feedTo('nasa-space-telescopes',query,Number(qs(root,'[data-space-limit]').value),qs(root,'[data-space-results]')); qs(root,'[data-space-dataset]').disabled=!currentSpaceRecords.length; const groups={};currentSpaceRecords.forEach(r=>{const t=Lab.Observations.telescope(r);groups[t]=(groups[t]||0)+1});qs(root,'[data-space-summary]').textContent=Object.entries(groups).map(([k,v])=>`${k}: ${v}`).join(' · ')||'No observations returned.'; });
      qs(root, '[data-marine-load]').addEventListener('click', async () => { currentMarineRecords=await feedTo('obis-marine',qs(root,'[data-marine-query]').value,Number(qs(root,'[data-marine-limit]').value),qs(root,'[data-marine-results]')); qs(root,'[data-marine-dataset]').disabled=!currentMarineRecords.length; const taxa=Lab.Observations.taxonSummary(currentMarineRecords).slice(0,6);qs(root,'[data-marine-summary]').textContent=`${currentMarineRecords.length} occurrences · `+taxa.map(([n,c])=>`${n}: ${c}`).join(' · '); renderMarineChart(); });
    }


    function loadDataset(dataset){ currentDataset=dataset; openModule('dataset-inspector'); renderDataset(); }
    root._scLabGetCurrentDataset=()=>currentDataset;
    root._scLabSetCurrentDataset=(dataset)=>{currentDataset=dataset;renderDataset();};
    root.addEventListener('sc-lab:dataset',event=>loadDataset(Lab.Datasets.fromRecords(event.detail.records,{title:event.detail.title,source:event.detail.source})));
    if (!observeOwned) {
      qs(root,'[data-feed-to-dataset]').addEventListener('click',()=>loadDataset(Lab.Datasets.fromRecords(currentFeedRecords,{title:'Scientific observation board',source:feedSource.value,query:{q:feedQuery.value,limit:Number(feedLimit.value)}})));
      qs(root,'[data-space-dataset]').addEventListener('click',()=>loadDataset(Lab.Datasets.fromRecords(currentSpaceRecords,{title:'Space telescope observations',source:'NASA Image and Video Library'})));
      qs(root,'[data-marine-dataset]').addEventListener('click',()=>loadDataset(Lab.Datasets.fromRecords(currentMarineRecords,{title:'Marine biodiversity occurrences',source:'OBIS'})));
    }
    qs(root,'[data-save-query]').addEventListener('click',()=>{projects.add('savedQueries',{source:feedSource.value,q:feedQuery.value,limit:Number(feedLimit.value),recordCount:currentFeedRecords.length},`Scientific query saved: ${feedSource.value}`);U.toast(root,'Query saved to project.');});
    function datasetRows(){return currentDataset?Lab.Datasets.filter(currentDataset,qs(root,'[data-dataset-filter]').value):[];}
    function populateDatasetSelect(){const sel=qs(root,'[data-dataset-select]');const value=sel.value;sel.innerHTML='<option value="">Current working dataset</option>'+projects.get().datasets.map(x=>`<option value="${U.esc(x.id)}">${U.esc(x.title||'Dataset')}</option>`).join('');sel.value=value;}
    function renderDataset(){populateDatasetSelect();const header=qs(root,'[data-dataset-header]'),table=qs(root,'[data-dataset-table]'),chart=qs(root,'[data-dataset-chart]');if(!currentDataset){header.textContent='No dataset loaded. Open feed results, import CSV, or select a saved project dataset.';table.innerHTML=empty('No dataset loaded.');chart.innerHTML=empty('No dataset loaded.');return;}const rows=datasetRows(),stats=Lab.Datasets.summary(currentDataset,rows);header.textContent=`${currentDataset.title} · ${currentDataset.source} · ${rows.length} filtered rows / ${currentDataset.rows.length} total`;const selects=[qs(root,'[data-dataset-x]'),qs(root,'[data-dataset-y]')];selects.forEach((sel,i)=>{const prev=sel.value;sel.innerHTML=(i===0?'<option value="">Row index</option>':'<option value="">Select numeric variable</option>')+currentDataset.columns.map(c=>`<option>${U.esc(c)}</option>`).join('');if(currentDataset.columns.includes(prev))sel.value=prev;});if(!qs(root,'[data-dataset-y]').value){const num=Object.keys(stats.numeric)[0];if(num)qs(root,'[data-dataset-y]').value=num;}qs(root,'[data-dataset-stats]').innerHTML=`<div><strong>${stats.rows}</strong><span>Rows</span></div><div><strong>${stats.columns}</strong><span>Variables</span></div><div><strong>${stats.missing}</strong><span>Missing cells</span></div><div><strong>${Object.keys(stats.numeric).length}</strong><span>Numeric variables</span></div>`;Lab.Datasets.renderTable(table,currentDataset,rows,Number(qs(root,'[data-dataset-limit]').value));Lab.Datasets.renderChart(chart,currentDataset,rows,qs(root,'[data-dataset-x]').value,qs(root,'[data-dataset-y]').value);}
    ['[data-dataset-filter]','[data-dataset-x]','[data-dataset-y]','[data-dataset-limit]'].forEach(sel=>qs(root,sel).addEventListener(sel.includes('filter')?'input':'change',renderDataset));
    qs(root,'[data-dataset-select]').addEventListener('change',e=>{const found=projects.get().datasets.find(x=>x.id===e.target.value);if(found){currentDataset=found;renderDataset();}});
    qs(root,'[data-dataset-import-run]').addEventListener('click',()=>{try{const raw=qs(root,'[data-dataset-import]').value.trim();if(!raw)throw new Error('Paste CSV or JSON first.');currentDataset=raw[0]==='['?Lab.Datasets.fromRecords(JSON.parse(raw),{title:'Imported JSON dataset',source:'User import'}):Lab.Datasets.parseCSV(raw);renderDataset();}catch(error){U.toast(root,error.message);}});
    qs(root,'[data-dataset-save]').addEventListener('click',()=>{if(!currentDataset)return U.toast(root,'Load a dataset first.');const saved=JSON.parse(JSON.stringify(currentDataset));saved.id=U.uid('datasets');projects.add('datasets',saved,`Dataset saved: ${saved.title}`);U.toast(root,'Dataset saved to project.');});
    qs(root,'[data-dataset-export]').addEventListener('click',()=>{if(currentDataset)U.download(`${(currentDataset.title||'dataset').replace(/[^a-z0-9]+/gi,'-').toLowerCase()}.csv`,Lab.Datasets.csv(currentDataset,datasetRows()),'text/csv');});
    function renderMarineChart(){const points=Lab.Observations.depthSeries(currentMarineRecords);const target=qs(root,'[data-marine-chart]');if(!points.length){target.innerHTML='<div class="sc-lab-data-note">No depth values were supplied by these records.</div>';return;}const max=Math.max(...points.map(p=>p.depth),1);target.innerHTML=`<svg viewBox="0 0 700 140"><line x1="35" y1="15" x2="35" y2="120" stroke="#89949d"/><line x1="35" y1="120" x2="680" y2="120" stroke="#89949d"/>${points.map((p,i)=>`<circle cx="${35+i*(640/Math.max(points.length-1,1))}" cy="${15+p.depth/max*100}" r="3" fill="#d00000"/>`).join('')}<text x="5" y="18" font-size="10">0 m</text><text x="2" y="120" font-size="10">${max.toFixed(0)} m</text></svg>`;}

    // Climate map.
    const climateDate = qs(root, '[data-climate-date]');
    climateDate.value = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    function renderMap() {
      const layer=qs(root,'[data-climate-layer]').value,bbox=qs(root,'[data-climate-region]').value;qs(root,'[data-climate-metadata]').innerHTML=`<span>Layer: ${U.esc(Lab.ClimateMap.layers[layer]?.label||layer)}</span><span>Date: ${U.esc(climateDate.value)}</span><span>Region: ${U.esc(bbox)}</span><span>Unit: ${U.esc(Lab.ClimateMap.layers[layer]?.unit||'source-defined')}</span>`;
      return Lab.ClimateMap.render(
        qs(root, '[data-climate-image]'),
        qs(root, '[data-climate-layer]').value,
        climateDate.value,
        qs(root, '[data-climate-region]').value,
        qs(root, '[data-climate-loading]')
      );
    }
    if (!observeOwned) {
      qs(root, '[data-climate-render]').addEventListener('click', renderMap);
      qs(root,'[data-climate-opacity]').addEventListener('input',e=>qs(root,'[data-climate-image]').style.opacity=Number(e.target.value)/100);
      qs(root,'[data-climate-image]').addEventListener('click',event=>{const point=Lab.ClimateMap.coordinate(event,qs(root,'[data-climate-image]'),qs(root,'[data-climate-region]').value);qs(root,'[data-climate-readout]').textContent=`Selected coordinate: ${point.latitude.toFixed(4)}, ${point.longitude.toFixed(4)}`;projects.add('observations',{title:'Climate map coordinate',source:'NASA GIBS',location:point,layer:qs(root,'[data-climate-layer]').value,date:climateDate.value},`Map coordinate observed: ${point.latitude.toFixed(3)}, ${point.longitude.toFixed(3)}`);});
      qs(root,'[data-climate-export]').addEventListener('click',()=>{const record={source:'NASA GIBS',layer:qs(root,'[data-climate-layer]').value,date:climateDate.value,bbox:qs(root,'[data-climate-region]').value,url:renderMap()};U.download('lab-climate-map.json',JSON.stringify(record,null,2),'application/json');});
      qs(root, '[data-climate-save]').addEventListener('click', () => {
        const record = {
          title: 'NASA GIBS climate map',
          layer: qs(root, '[data-climate-layer]').value,
          date: climateDate.value,
          bbox: qs(root, '[data-climate-region]').value,
          url: renderMap()
        };
        projects.add('mapViews', record, `Climate map saved: ${record.layer}`);
        U.toast(root, 'Climate map state saved.');
      });
      renderMap();
    }

    // Chemistry Laboratory and Spectrometry Studio.
    let rawSpectrum = [];
    let spectrumHistory = [];
    let detectedPeaks = [];
    let currentChemCalibration = null;
    let currentSpectrumCalibration = null;

    const periodic = qs(root, '[data-periodic-table]');
    const elementDetail = qs(root, '[data-element-detail]');
    Lab.Periodic.load(config.elementsUrl).then(elements => {
      Lab.Stoichiometry.setElements(elements);
      drawElements();
    }).catch(error => { elementDetail.textContent = error.message; });

    function drawElements() {
      Lab.Periodic.render(periodic, elementDetail, {
        query: qs(root, '[data-element-search]').value,
        property: qs(root, '[data-element-property]').value
      });
    }
    qs(root, '[data-element-search]').addEventListener('input', drawElements);
    qs(root, '[data-element-property]').addEventListener('change', drawElements);
    qsa(root, '[data-chem-tab]').forEach(button => button.addEventListener('click', () => setTab('[data-chem-tab]', 'chemTab', '[data-chem-pane]', 'chemPane', button.dataset.chemTab)));
    qsa(root, '[data-analysis-tab]').forEach(button => button.addEventListener('click', () => setTab('[data-analysis-tab]', 'analysisTab', '[data-analysis-pane]', 'analysisPane', button.dataset.analysisTab)));

    qs(root, '[data-chem-new-experiment]').addEventListener('click', () => createExperiment({ title: 'Chemistry experiment', question: 'What chemical behavior or analytical result is being investigated?' }));
    qs(root, '[data-chem-notebook]').addEventListener('click', () => createNote({ title: 'Chemistry laboratory note', tagsText: 'chemistry, laboratory' }));

    function recordCalculation(type, input, result, collection = 'calculations') {
      projects.add(collection, { type, input, result, methodVersion: '0.9.4' }, `${type} completed`);
      return result;
    }

    function bindResult(buttonSelector, outputSelector, type, inputFn, calculationFn, collection = 'calculations') {
      qs(root, buttonSelector).addEventListener('click', () => {
        const output = qs(root, outputSelector);
        try {
          const input = inputFn();
          const result = calculationFn(input);
          output.textContent = JSON.stringify(result, null, 2);
          recordCalculation(type, input, result, collection);
        } catch (error) { output.textContent = `Error: ${error.message}`; }
      });
    }

    bindResult('[data-formula-run]', '[data-formula-output]', 'Molar mass',
      () => ({ formula: qs(root, '[data-formula-input]').value }),
      input => Lab.Stoichiometry.molarMass(input.formula));
    bindResult('[data-percent-run]', '[data-formula-output]', 'Percent composition',
      () => ({ formula: qs(root, '[data-formula-input]').value }),
      input => Lab.ChemistryLab.percentComposition(input.formula), 'chemicalRecords');
    bindResult('[data-empirical-run]', '[data-empirical-output]', 'Empirical formula',
      () => JSON.parse(qs(root, '[data-empirical-input]').value),
      input => Lab.ChemistryLab.empiricalFormula(input), 'chemicalRecords');
    bindResult('[data-molecular-run]', '[data-molecular-output]', 'Molecular formula',
      () => ({ empiricalFormula: qs(root, '[data-molecular-empirical]').value, molecularMass: qs(root, '[data-molecular-mass]').value }),
      input => Lab.ChemistryLab.molecularFormula(input), 'chemicalRecords');
    bindResult('[data-balance-run]', '[data-balance-output]', 'Equation balance',
      () => ({ equation: qs(root, '[data-balance-input]').value }),
      input => Lab.Stoichiometry.balanceEquation(input.equation));
    bindResult('[data-limit-run]', '[data-limit-output]', 'Limiting reagent',
      () => ({ equation: qs(root, '[data-limit-equation]').value, moles: JSON.parse(qs(root, '[data-limit-moles]').value) }),
      input => Lab.Stoichiometry.limitingReagent(input.equation, input.moles));
    bindResult('[data-yield-run]', '[data-yield-output]', 'Theoretical yield',
      () => ({ formula: qs(root, '[data-yield-product]').value, moles: qs(root, '[data-yield-moles]').value }),
      input => Lab.Stoichiometry.theoreticalYield(input.formula, input.moles));

    qs(root, '[data-reaction-save]').addEventListener('click', () => {
      const output = qs(root, '[data-reaction-save-output]');
      try {
        const equation = qs(root, '[data-limit-equation]').value || qs(root, '[data-balance-input]').value;
        const balanced = Lab.Stoichiometry.balanceEquation(equation);
        const record = {
          title: qs(root, '[data-reaction-title]').value || 'Chemical reaction',
          equation,
          balancedEquation: balanced.balanced,
          coefficients: balanced.coefficients,
          conditions: qs(root, '[data-reaction-conditions]').value,
          status: 'planned'
        };
        projects.add('reactions', record, `Reaction record saved: ${record.title}`);
        output.textContent = JSON.stringify(record, null, 2);
        U.toast(root, 'Reaction record saved to the active project.');
      } catch (error) { output.textContent = `Error: ${error.message}`; }
    });

    bindResult('[data-conc-run]', '[data-conc-output]', 'Solution concentration',
      () => ({ moles: qs(root, '[data-conc-moles]').value, solutionL: qs(root, '[data-conc-volume]').value, soluteG: qs(root, '[data-conc-solute-g]').value, solventKg: qs(root, '[data-conc-solvent-kg]').value, solutionG: qs(root, '[data-conc-solution-g]').value }),
      input => Lab.ChemistryLab.concentration(input));
    bindResult('[data-dilution-run]', '[data-dilution-output]', 'Dilution',
      () => ({ c1: qs(root, '[data-dilution-c1]').value, v1: qs(root, '[data-dilution-v1]').value, c2: qs(root, '[data-dilution-c2]').value, v2: qs(root, '[data-dilution-v2]').value }),
      input => Lab.Stoichiometry.dilution(input));
    bindResult('[data-ksp-run]', '[data-ksp-output]', 'Molar solubility',
      () => ({ ksp: qs(root, '[data-ksp]').value, cationStoich: qs(root, '[data-ksp-cation]').value, anionStoich: qs(root, '[data-ksp-anion]').value }),
      input => Lab.ChemistryLab.solubility(input));

    bindResult('[data-strong-run]', '[data-strong-output]', 'Strong acid/base pH',
      () => ({ type: qs(root, '[data-strong-type]').value, concentration: qs(root, '[data-strong-conc]').value, equivalents: qs(root, '[data-strong-eq]').value }),
      input => Lab.ChemistryLab.strongAcidBase(input));
    bindResult('[data-weak-run]', '[data-weak-output]', 'Weak acid/base equilibrium',
      () => ({ type: qs(root, '[data-weak-type]').value, concentration: qs(root, '[data-weak-conc]').value, k: qs(root, '[data-weak-k]').value }),
      input => input.type === 'acid' ? Lab.ChemistryLab.weakAcid({ concentration: input.concentration, ka: input.k }) : Lab.ChemistryLab.weakBase({ concentration: input.concentration, kb: input.k }));
    bindResult('[data-buffer-run]', '[data-buffer-output]', 'Buffer pH',
      () => ({ pKa: qs(root, '[data-buffer-pka]').value, acid: qs(root, '[data-buffer-acid]').value, base: qs(root, '[data-buffer-base]').value }),
      input => Lab.ChemistryLab.buffer(input));
    bindResult('[data-titration-run]', '[data-titration-output]', 'Strong acid/base titration',
      () => ({ analyteType: qs(root, '[data-titration-type]').value, analyteC: qs(root, '[data-titration-analyte-c]').value, analyteMl: qs(root, '[data-titration-analyte-v]').value, titrantC: qs(root, '[data-titration-titrant-c]').value, titrantMl: qs(root, '[data-titration-titrant-v]').value }),
      input => Lab.ChemistryLab.titration(input));

    bindResult('[data-cal-run]', '[data-cal-output]', 'Calorimetry',
      () => ({ massG: qs(root, '[data-cal-mass]').value, specificHeat: qs(root, '[data-cal-cp]').value, initialC: qs(root, '[data-cal-ti]').value, finalC: qs(root, '[data-cal-tf]').value }),
      input => Lab.ChemistryLab.calorimetry(input));
    bindResult('[data-gibbs-run]', '[data-gibbs-output]', 'Gibbs free energy',
      () => ({ deltaHkJ: qs(root, '[data-gibbs-h]').value, deltaSJmolK: qs(root, '[data-gibbs-s]').value, temperatureK: qs(root, '[data-gibbs-t]').value }),
      input => Lab.ChemistryLab.gibbs(input));
    bindResult('[data-hess-run]', '[data-hess-output]', 'Hess law',
      () => JSON.parse(qs(root, '[data-hess-input]').value),
      input => Lab.ChemistryLab.hess(input));

    bindResult('[data-nernst-run]', '[data-nernst-output]', 'Nernst cell potential',
      () => ({ eStandard: qs(root, '[data-nernst-e]').value, temperatureK: qs(root, '[data-nernst-t]').value, electrons: qs(root, '[data-nernst-n]').value, reactionQuotient: qs(root, '[data-nernst-q]').value }),
      input => Lab.ChemistryLab.nernst(input));
    bindResult('[data-electrolysis-run]', '[data-electrolysis-output]', 'Electrolysis',
      () => ({ currentA: qs(root, '[data-electrolysis-current]').value, timeS: qs(root, '[data-electrolysis-time]').value, electrons: qs(root, '[data-electrolysis-n]').value, molarMassGmol: qs(root, '[data-electrolysis-mm]').value }),
      input => Lab.ChemistryLab.electrolysis(input));

    bindResult('[data-arr-run]', '[data-arr-output]', 'Arrhenius rate constant',
      () => ({ preExponential: qs(root, '[data-arr-a]').value, activationEnergyKJ: qs(root, '[data-arr-ea]').value, temperatureK: qs(root, '[data-arr-t]').value }),
      input => Lab.ChemistryLab.arrhenius(input));
    bindResult('[data-rate-run]', '[data-rate-output]', 'Integrated rate law',
      () => ({ order: qs(root, '[data-rate-order]').value, k: qs(root, '[data-rate-k]').value, initialConcentration: qs(root, '[data-rate-a0]').value, time: qs(root, '[data-rate-time]').value }),
      input => Lab.ChemistryLab.integratedRate(input));

    function parsePairs(text) {
      return Lab.Spectrometry.parse(text).map(point => ({ x: point.x, y: point.y }));
    }
    function calibrationSvg(result, xLabel = 'Concentration', yLabel = 'Signal') {
      const points = result.points || [];
      if (!points.length) return '';
      const fitted = points.map(point => ({ x: point.x, y: result.slope * point.x + result.intercept }));
      const base = Lab.Spectrometry.svg(fitted, [], { xLabel, yLabel });
      const dots = points.map(point => `<span>${U.esc(point.x)} → ${U.esc(point.y)}</span>`).join('');
      return `${base}<div class="sc-lab-calibration-points">${dots}</div>`;
    }
    qs(root, '[data-chem-cal-run]').addEventListener('click', () => {
      const output = qs(root, '[data-chem-cal-output]');
      try {
        const input = { points: parsePairs(qs(root, '[data-chem-cal-points]').value), unknownSignal: qs(root, '[data-chem-cal-unknown]').value };
        currentChemCalibration = Lab.ChemistryLab.calibration(input);
        output.textContent = JSON.stringify(currentChemCalibration, null, 2);
        qs(root, '[data-chem-cal-chart]').innerHTML = calibrationSvg(currentChemCalibration);
        recordCalculation('Analytical calibration', input, currentChemCalibration, 'calibrations');
      } catch (error) { output.textContent = `Error: ${error.message}`; }
    });
    qs(root, '[data-chem-cal-save]').addEventListener('click', () => {
      if (!currentChemCalibration) return U.toast(root, 'Run the calibration first.');
      projects.add('calibrations', { type: 'chemistry-calibration', result: currentChemCalibration, status: 'draft' }, 'Chemistry calibration record saved');
      U.toast(root, 'Calibration record saved.');
    });

    // Calculator registry.
    const domainSelect = qs(root, '[data-calculator-domain]');
    const calculatorSelect = qs(root, '[data-calculator-select]');
    const calculatorForm = qs(root, '[data-calculator-form]');
    (Lab.Calculators?.domains?.() || []).forEach(domain => domainSelect.add(new Option(domain, domain)));

    function populateCalculators(preferredId) {
      calculatorSelect.innerHTML = '';
      (Lab.Calculators?.byDomain?.(domainSelect.value) || []).forEach(calculator => calculatorSelect.add(new Option(calculator.name, calculator.id)));
      if (preferredId && [...calculatorSelect.options].some(option => option.value === preferredId)) calculatorSelect.value = preferredId;
      renderCalculator();
    }

    function renderCalculator() {
      const definition = Lab.Calculators?.get?.(calculatorSelect.value);
      if (!definition) { calculatorForm.innerHTML = ''; return; }
      calculatorForm.innerHTML = `<div class="sc-lab-calculator-form" data-calculator-id="${U.esc(definition.id)}"><h4>${U.esc(definition.name)}</h4>
        ${definition.fields.map(([key, label, unit, value]) => `<label>${U.esc(label)}${unit ? ` (${U.esc(unit)})` : ''}<input data-calc-field="${U.esc(key)}" value="${U.esc(value)}"></label>`).join('')}
        <button class="sc-lab-button sc-lab-button-primary" data-calc-run>Calculate</button>
        <div class="sc-lab-calculator-result" data-calc-result>Ready.</div>
      </div>`;
      qs(calculatorForm, '[data-calc-run]').addEventListener('click', () => {
        try {
          const values = {};
          qsa(calculatorForm, '[data-calc-field]').forEach(input => { values[input.dataset.calcField] = input.value; });
          const result = definition.run(values);
          qs(calculatorForm, '[data-calc-result]').textContent = JSON.stringify(result, null, 2);
          projects.add('calculations', { type: definition.name, calculatorId: definition.id, inputs: values, result }, `${definition.name} calculation completed`);
        } catch (error) { qs(calculatorForm, '[data-calc-result]').textContent = `Error: ${error.message}`; }
      });
    }

    function selectCalculator(id) {
      const definition = Lab.Calculators?.get?.(id);
      if (!definition) return;
      domainSelect.value = definition.domain;
      populateCalculators(id);
    }
    domainSelect.addEventListener('change', () => populateCalculators());
    calculatorSelect.addEventListener('change', renderCalculator);
    populateCalculators();

    // Spectrometry Studio.
    function spectrumMethod() { return qs(root, '[data-spectrum-method]').value; }
    function spectrumSummary() {
      if (!spectrum.length) return null;
      const ys = spectrum.map(point => point.y);
      return {
        method: spectrumMethod(), sampleId: qs(root, '[data-spectrum-sample]').value,
        points: spectrum.length, xMin: spectrum[0].x, xMax: spectrum[spectrum.length - 1].x,
        yMin: Math.min(...ys), yMax: Math.max(...ys), area: Lab.Spectrometry.integrate(spectrum),
        centroid: Lab.Spectrometry.centroid(spectrum), estimatedNoise: Lab.Spectrometry.estimateNoise(spectrum),
        peaks: detectedPeaks.length, processingSteps: spectrumHistory.length
      };
    }
    function renderSpectrum() {
      const options = { method: spectrumMethod() };
      qs(root, '[data-spectrum-chart]').innerHTML = spectrum.length ? Lab.Spectrometry.svg(spectrum, detectedPeaks, options) : empty('Load a spectrum to begin.');
      const summary = spectrumSummary();
      qs(root, '[data-spectrum-metrics]').innerHTML = summary ? Object.entries(summary).filter(([key]) => !['method','sampleId'].includes(key)).map(([key,value]) => `<div><strong>${typeof value === 'number' ? Number(value).toPrecision(6) : U.esc(value)}</strong><span>${U.esc(key)}</span></div>`).join('') : '';
      qs(root, '[data-spectrum-peak-table]').innerHTML = detectedPeaks.length ? `<table><thead><tr><th>Position</th><th>Intensity</th><th>Prominence</th><th>FWHM</th></tr></thead><tbody>${detectedPeaks.map(peak => `<tr><td>${U.esc(Number(peak.x).toPrecision(7))}</td><td>${U.esc(Number(peak.y).toPrecision(7))}</td><td>${U.esc(Number(peak.prominence).toPrecision(5))}</td><td>${U.esc(Number(peak.fwhm).toPrecision(5))}</td></tr>`).join('')}</tbody></table>` : empty('No characterized peaks.');
      qs(root, '[data-spectrum-output]').textContent = JSON.stringify({ summary, processingHistory: spectrumHistory, peaks: detectedPeaks }, null, 2);
    }
    function applySpectrumStep(label, fn) {
      if (!spectrum.length) return U.toast(root, 'Load a spectrum first.');
      try {
        spectrum = fn(spectrum);
        spectrumHistory.push({ at: U.now(), action: label });
        detectedPeaks = [];
        renderSpectrum();
      } catch (error) { U.toast(root, error.message); }
    }
    qs(root, '[data-spectrum-method]').addEventListener('change', renderSpectrum);
    qs(root, '[data-spectrum-load]').addEventListener('click', () => {
      try {
        rawSpectrum = Lab.Spectrometry.parse(qs(root, '[data-spectrum-input]').value);
        spectrum = Lab.Spectrometry.clone(rawSpectrum);
        spectrumHistory = [{ at: U.now(), action: 'Imported raw spectrum', points: spectrum.length }];
        detectedPeaks = [];
        renderSpectrum();
      } catch (error) { qs(root, '[data-spectrum-output]').textContent = `Error: ${error.message}`; }
    });
    qs(root, '[data-spectrum-reset]').addEventListener('click', () => {
      if (!rawSpectrum.length) return;
      spectrum = Lab.Spectrometry.clone(rawSpectrum); detectedPeaks = [];
      spectrumHistory.push({ at: U.now(), action: 'Reset to raw data' }); renderSpectrum();
    });
    qs(root, '[data-spectrum-baseline]').addEventListener('click', () => applySpectrumStep(`Baseline: ${qs(root, '[data-spectrum-baseline-method]').value}`, points => Lab.Spectrometry.baseline(points, qs(root, '[data-spectrum-baseline-method]').value, { windowSize: qs(root, '[data-spectrum-window]').value })));
    qs(root, '[data-spectrum-smooth]').addEventListener('click', () => applySpectrumStep(`Smoothing: ${qs(root, '[data-spectrum-smooth-method]').value}`, points => qs(root, '[data-spectrum-smooth-method]').value === 'median' ? Lab.Spectrometry.medianSmooth(points, qs(root, '[data-spectrum-radius]').value) : Lab.Spectrometry.smooth(points, qs(root, '[data-spectrum-radius]').value)));
    qs(root, '[data-spectrum-normalize]').addEventListener('click', () => applySpectrumStep(`Normalization: ${qs(root, '[data-spectrum-normalize-mode]').value}`, points => Lab.Spectrometry.normalize(points, qs(root, '[data-spectrum-normalize-mode]').value)));
    qs(root, '[data-spectrum-derivative]').addEventListener('click', () => applySpectrumStep('First derivative', points => Lab.Spectrometry.derivative(points, 1)));
    qs(root, '[data-spectrum-convert]').addEventListener('click', () => {
      const mode = qs(root, '[data-spectrum-conversion]').value;
      if (mode === 'none') return;
      applySpectrumStep(`Conversion: ${mode}`, points => {
        if (mode === 't-to-a') return Lab.Spectrometry.transmittanceToAbsorbance(points, 'fraction');
        if (mode === 'percent-to-a') return Lab.Spectrometry.transmittanceToAbsorbance(points, 'percent');
        if (mode === 'a-to-t') return Lab.Spectrometry.absorbanceToTransmittance(points, 'fraction');
        return Lab.Spectrometry.absorbanceToTransmittance(points, 'percent');
      });
    });
    qs(root, '[data-spectrum-peaks]').addEventListener('click', () => {
      if (!spectrum.length) return;
      const thresholdRaw = qs(root, '[data-spectrum-threshold]').value;
      detectedPeaks = Lab.Spectrometry.peaks(spectrum, {
        threshold: thresholdRaw === '' ? undefined : Number(thresholdRaw),
        minDistance: qs(root, '[data-spectrum-distance]').value,
        minProminence: qs(root, '[data-spectrum-prominence]').value
      });
      spectrumHistory.push({ at: U.now(), action: 'Peak detection', count: detectedPeaks.length });
      const result = spectrumSummary();
      projects.add('calculations', { type: 'Spectrometry peak analysis', method: spectrumMethod(), result, peaks: detectedPeaks }, 'Spectrometry peak analysis completed');
      renderSpectrum();
    });
    qs(root, '[data-spectrum-export]').addEventListener('click', () => {
      if (!spectrum.length) return;
      U.download(`${(qs(root, '[data-spectrum-sample]').value || 'processed-spectrum').replace(/[^a-z0-9_-]+/gi,'-')}.csv`, Lab.Spectrometry.csv(spectrum), 'text/csv');
    });
    qs(root, '[data-spectrum-save]').addEventListener('click', () => {
      if (!spectrum.length) return U.toast(root, 'Load a spectrum first.');
      const record = {
        title: qs(root, '[data-spectrum-title]').value || 'Analytical spectrum', sampleId: qs(root, '[data-spectrum-sample]').value,
        method: spectrumMethod(), raw: rawSpectrum, processed: spectrum, processingHistory: spectrumHistory,
        peaks: detectedPeaks, summary: spectrumSummary(), status: 'processed'
      };
      projects.add('spectra', record, `Spectrum saved: ${record.title}`);
      U.toast(root, 'Spectrum and processing history saved.');
    });
    qs(root, '[data-spectrum-note]').addEventListener('click', () => {
      const summary = spectrumSummary();
      if (!summary) return U.toast(root, 'Load a spectrum first.');
      createNote({ title: `${qs(root, '[data-spectrum-sample]').value} spectrometry analysis`, body: JSON.stringify({ summary, peaks: detectedPeaks, processingHistory: spectrumHistory }, null, 2), tagsText: `spectrometry, ${spectrumMethod()}, analysis` });
    });

    qs(root, '[data-spectrum-cal-run]').addEventListener('click', () => {
      const output = qs(root, '[data-spectrum-cal-output]');
      try {
        const points = parsePairs(qs(root, '[data-spectrum-cal-points]').value);
        currentSpectrumCalibration = Lab.Spectrometry.calibration(points, qs(root, '[data-spectrum-cal-unknown]').value);
        output.textContent = JSON.stringify(currentSpectrumCalibration, null, 2);
        qs(root, '[data-spectrum-cal-chart]').innerHTML = calibrationSvg(currentSpectrumCalibration);
      } catch (error) { output.textContent = `Error: ${error.message}`; }
    });
    qs(root, '[data-spectrum-cal-save]').addEventListener('click', () => {
      if (!currentSpectrumCalibration) return U.toast(root, 'Run the calibration first.');
      projects.add('calibrations', { type: 'spectrometry-calibration', method: spectrumMethod(), sampleId: qs(root, '[data-spectrum-sample]').value, result: currentSpectrumCalibration }, 'Spectrometry calibration saved');
      U.toast(root, 'Spectrometry calibration saved.');
    });


    function initializeController(scope, controller, selector, ...args) {
      if (!root.querySelector(selector)) return false;
      if (!controller || typeof controller.init !== 'function') {
        reportRuntimeError(scope, new Error(`Required controller is unavailable: ${scope}`), { selector });
        return false;
      }
      try {
        controller.init(root, projects, ...args);
        root.querySelector(selector)?.setAttribute('data-sc-lab-controller-ready', '1');
        return true;
      } catch (error) {
        reportRuntimeError(scope, error, { selector, activeModule: root.dataset.initialModule || initial });
        root.querySelector(selector)?.setAttribute('data-sc-lab-controller-error', error.message || String(error));
        return false;
      }
    }

    initializeController('physics', Lab.PhysicsLab, '[data-physics-tool]');
    initializeController('biology', Lab.BiologyLab, '[data-biology-tool-grid]');
    initializeController('astronomy', Lab.AstronomyLab, '[data-astronomy-tool-grid]');
    initializeController('materials', Lab.MaterialsLab, '[data-materials-tool-grid]');
    initializeController('earth-systems', Lab.EarthLab, '[data-earth-tool-grid]');
    initializeController('energy-engineering', Lab.EnergyLab, '[data-energy-tool-grid]');
    initializeController('electrical-embedded', Lab.ElectricalEmbedded, '[data-electrical-grid]');
    initializeController('mechanical-thermal', Lab.MechanicalThermalLab, '[data-mechanical-thermal-root]');
    initializeController('civil-infrastructure', Lab.CivilInfrastructureLab, '[data-civil-infrastructure-root]');
    initializeController('code-switcher', Lab.CodeSwitcher, '[data-lab-module="code-studio"]');
    initializeController('visualization', Lab.Visualization, '[data-viz-chart]', config);
    initializeController('reporting', Lab.Reporting, '[data-lab-module="report-studio"]');
    initializeController('dimensional-visualization', Lab.DimensionalVisualization, '[data-dim-chart]');
    initializeController('workspace-data', Lab.DataManagement, '[data-workspace-counts]');

    // Project records.
    qs(root, '[data-new-experiment]').addEventListener('click', () => createExperiment());
    qs(root, '[data-new-hypothesis]').addEventListener('click', () => {
      const record = promptRecord([['title', 'Hypothesis title', 'Working hypothesis'], ['statement', 'Hypothesis statement', ''], ['status', 'Status', 'proposed']]);
      if (record) projects.add('hypotheses', record, `Hypothesis added: ${record.title}`);
    });
    qs(root, '[data-new-decision]').addEventListener('click', () => {
      const record = promptRecord([['title', 'Decision title', 'Project decision'], ['rationale', 'Rationale and evidence', ''], ['status', 'Status', 'draft']]);
      if (record) projects.add('decisions', record, `Decision added: ${record.title}`);
    });
    qs(root, '[data-new-note]').addEventListener('click', () => createNote());
    qs(root, '[data-note-filter]').addEventListener('input', renderNotes);
    qs(root, '[data-export-notebook]').addEventListener('click', () => {
      const project = projects.get();
      const markdown = `# ${project.name} — Lab Notebook\n\n${project.notes.map(note => `## ${note.title}\n\n${note.body || ''}\n\n*${U.fmt(note.createdAt)}*`).join('\n\n')}`;
      U.download(`${project.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}-notebook.md`, markdown, 'text/markdown');
    });
    qs(root, '[data-activity-filter]').addEventListener('input', renderActivity);
    qs(root, '[data-activity-limit]').addEventListener('change', renderActivity);
    qs(root, '[data-export-activity]').addEventListener('click', () => {
      const lines = [['timestamp', 'activity'], ...projects.get().activity.map(item => [item.at, item.text])];
      U.download('lab-project-activity.csv', lines.map(row => row.map(csvCell).join(',')).join('\n'), 'text/csv');
    });

    // Documentation.
    function fingerprint(project) {
      const data = {
        updatedAt: project.updatedAt,
        counts: {
          evidence: project.evidence.length,
          experiments: project.experiments.length,
          hypotheses: project.hypotheses.length,
          decisions: project.decisions.length,
          notes: project.notes.length,
          calculations: project.calculations.length,
          maps: project.maps.length,
          physics: ['physicsRecords','waveforms','circuitAnalyses','fieldModels','particleEvents','detectorAnalyses','nuclearRecords','opticalAnalyses','physicsValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          biology: ['biologyRecords','biologicalSamples','sequences','alignments','proteinAnalyses','geneticAnalyses','populationAnalyses','ecologyAnalyses','physiologyRecords','biologyValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          astronomy: ['astronomyRecords','celestialTargets','orbitalAnalyses','stellarAnalyses','photometryRecords','spectralAnalyses','galaxyAnalyses','cosmologyRecords','telescopeAnalyses','astronomyValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          materials: ['materialsRecords','materialSamples','mechanicalRecords','thermalRecords','electricalRecords','magneticRecords','opticalRecords','crystallographyRecords','phaseRecords','corrosionRecords','polymerRecords','compositeRecords','microscopyRecords','materialsValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          earthSystems: ['earthRecords','geoscienceRecords','atmosphericRecords','climateRecords','hydrologyRecords','oceanRecords','marineSystemRecords','remoteSensingRecords','hazardRecords','carbonCycleRecords','earthValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0),
          energyEngineering: ['energyRecords','engineeringRecords','energySystemRecords','solarRecords','windRecords','hydroRecords','storageRecords','gridRecords','thermalSystemRecords','fuelHydrogenRecords','emissionsRecords','technoEconomicRecords','reliabilityRecords','energyValidationRecords'].reduce((total,key)=>total+(project[key]||[]).length,0)
        }
      };
      return btoa(unescape(encodeURIComponent(JSON.stringify(data))));
    }

    function generateDocument(type, title) {
      const project = projects.get();
      const sections = [`# ${title}`, '', `Project: ${project.name}`, `Generated: ${new Date().toISOString()}`, `Document type: ${type}`, ''];
      sections.push('## Project summary', '', project.description || 'No project description has been recorded.', '');
      sections.push('## Evidence', '', project.evidence.length ? project.evidence.map(item => `- **${item.title}** — ${item.source || 'Source'}${item.url ? ` — ${item.url}` : ''}`).join('\n') : 'No evidence records.', '');
      sections.push('## Hypotheses', '', project.hypotheses.length ? project.hypotheses.map(item => `- **${item.title}** — ${item.statement || ''}`).join('\n') : 'No hypotheses recorded.', '');
      sections.push('## Calculations and analyses', '', project.calculations.length ? project.calculations.map(item => `- **${item.type || 'Calculation'}** — ${JSON.stringify(item.result || {})}`).join('\n') : 'No calculations recorded.', '');
      const physicsCollections = ['physicsRecords','waveforms','circuitAnalyses','fieldModels','particleEvents','detectorAnalyses','nuclearRecords','opticalAnalyses','physicsValidationRecords'];
      const physicsRecords = physicsCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Physics analyses', '', physicsRecords.length ? physicsRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || {})}`).join('\n') : 'No physics analyses recorded.', '');
      const biologyCollections = ['biologyRecords','biologicalSamples','sequences','alignments','proteinAnalyses','geneticAnalyses','populationAnalyses','ecologyAnalyses','physiologyRecords','biologyValidationRecords'];
      const biologyRecords = biologyCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Biology analyses', '', biologyRecords.length ? biologyRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No biology analyses recorded.', '');
      const astronomyCollections = ['astronomyRecords','celestialTargets','orbitalAnalyses','stellarAnalyses','photometryRecords','spectralAnalyses','galaxyAnalyses','cosmologyRecords','telescopeAnalyses','astronomyValidationRecords'];
      const astronomyRecords = astronomyCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Astronomy analyses', '', astronomyRecords.length ? astronomyRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No astronomy analyses recorded.', '');
      const materialsCollections = ['materialsRecords','materialSamples','mechanicalRecords','thermalRecords','electricalRecords','magneticRecords','opticalRecords','crystallographyRecords','phaseRecords','corrosionRecords','polymerRecords','compositeRecords','microscopyRecords','materialsValidationRecords'];
      const materialsRecords = materialsCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Materials analyses', '', materialsRecords.length ? materialsRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No materials analyses recorded.', '');
      const earthCollections = ['earthRecords','geoscienceRecords','atmosphericRecords','climateRecords','hydrologyRecords','oceanRecords','marineSystemRecords','remoteSensingRecords','hazardRecords','carbonCycleRecords','earthValidationRecords'];
      const earthRecords = earthCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Earth systems analyses', '', earthRecords.length ? earthRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No Earth systems analyses recorded.', '');
      const energyCollections = ['energyRecords','engineeringRecords','energySystemRecords','solarRecords','windRecords','hydroRecords','storageRecords','gridRecords','thermalSystemRecords','fuelHydrogenRecords','emissionsRecords','technoEconomicRecords','reliabilityRecords','energyValidationRecords'];
      const energyRecords = energyCollections.flatMap(key => (project[key] || []).map(item => ({...item, collection:key})));
      sections.push('## Energy and engineering analyses', '', energyRecords.length ? energyRecords.map(item => `- **${item.type || item.collection}** — ${JSON.stringify(item.result || item.report || {})}`).join('\n') : 'No energy and engineering analyses recorded.', '');
      sections.push('## Experiments', '', project.experiments.length ? project.experiments.map(item => `### ${item.title}\n\nQuestion: ${item.question || ''}\n\nHypothesis: ${item.hypothesis || ''}\n\nMethod: ${item.method || ''}\n\nStatus: ${item.status || 'planned'}`).join('\n\n') : 'No experiments recorded.', '');
      sections.push('## Decisions', '', project.decisions.length ? project.decisions.map(item => `- **${item.title}** — ${item.rationale || ''}`).join('\n') : 'No decisions recorded.', '');
      sections.push('## Notebook record', '', project.notes.length ? project.notes.slice(0, 25).map(item => `### ${item.title}\n\n${item.body || ''}`).join('\n\n') : 'No notebook entries.', '');
      sections.push('## Traceability', '', 'Sources → Evidence → Hypotheses → Calculations → Experiments → Decisions → Documentation', '');
      sections.push('## Scientific review boundary', '', 'Imported observations, calculations, models, prototype outputs, and generated documentation require review against authoritative sources, validated methods, and actual operating conditions.');
      return sections.join('\n');
    }

    function updateDocStale() {
      if (!currentDocument) return;
      const stale = currentDocument.fingerprint !== fingerprint(projects.get());
      qs(root, '[data-doc-status]').textContent = stale
        ? 'Project data changed after generation. Regenerate or preserve this text as a released snapshot.'
        : 'Document reflects the current project record.';
      qs(root, '[data-doc-status]').classList.toggle('is-stale', stale);
    }

    qs(root, '[data-generate-doc]').addEventListener('click', () => {
      const type = qs(root, '[data-doc-type]').value;
      const title = qs(root, '[data-doc-title]').value || 'Lab project report';
      const markdown = generateDocument(type, title);
      currentDocument = { type, title, markdown, fingerprint: fingerprint(projects.get()), generatedAt: U.now() };
      qs(root, '[data-doc-editor]').value = markdown;
      updateDocStale();
      populateDatasetSelect();
    });
    qs(root, '[data-save-doc]').addEventListener('click', () => {
      const markdown = qs(root, '[data-doc-editor]').value;
      if (!markdown.trim()) return;
      const type = qs(root, '[data-doc-type]').value;
      const title = qs(root, '[data-doc-title]').value || 'Lab project report';
      projects.add('documents', { type, title, markdown, fingerprint: fingerprint(projects.get()), status: 'snapshot' }, `Document snapshot saved: ${title}`);
      currentDocument = { type, title, markdown, fingerprint: fingerprint(projects.get()), generatedAt: U.now() };
      updateDocStale();
      populateDatasetSelect();
      U.toast(root, 'Document snapshot saved.');
    });
    qs(root, '[data-export-doc-md]').addEventListener('click', () => {
      const text = qs(root, '[data-doc-editor]').value;
      if (text.trim()) U.download('lab-document.md', text, 'text/markdown');
    });
    qs(root, '[data-export-doc-html]').addEventListener('click', () => {
      const text = qs(root, '[data-doc-editor]').value;
      if (!text.trim()) return;
      const html = `<!doctype html><meta charset="utf-8"><title>${U.esc(qs(root, '[data-doc-title]').value)}</title><pre>${U.esc(text)}</pre>`;
      U.download('lab-document.html', html, 'text/html');
    });


    async function loadSourceRegistry(){const target=qs(root,'[data-source-registry]');target.innerHTML='<div class="sc-lab-data-note">Loading source metadata and connector health…</div>';try{const data=await U.fetchJson(`${config.restBase}sources/status`);root._sourceRows=Object.entries(data.sources||{});renderSourceRegistry();}catch(error){target.innerHTML=empty(error.message);}}
    function renderSourceRegistry(){const q=(qs(root,'[data-source-filter]').value||'').toLowerCase();const rows=(root._sourceRows||[]).filter(([id,m])=>!q||`${id} ${m.label} ${m.domain} ${m.coverage} ${m.format}`.toLowerCase().includes(q));qs(root,'[data-source-registry]').innerHTML=rows.map(([id,m])=>`<article class="sc-lab-source-row"><div><strong>${U.esc(m.label)}</strong><span>${U.esc(id)}</span></div><div><strong>${U.esc(m.domain)}</strong><span>${U.esc(m.kind)}</span></div><div><strong>${U.esc(m.coverage||'—')}</strong><span>${U.esc(m.temporal||'—')}</span></div><div><strong>${U.esc(m.endpoint||'—')}</strong><span>${U.esc(m.format||'—')}</span></div><div><strong class="sc-lab-source-state ${U.esc(m.status||'not_checked')}">${U.esc(m.status||'not checked')}</strong><span>${U.esc(m.lastChecked?U.fmt(m.lastChecked):m.message||'Not checked')}</span></div></article>`).join('')||empty('No matching sources.');}
    qs(root,'[data-source-refresh]').addEventListener('click',loadSourceRegistry);qs(root,'[data-source-filter]').addEventListener('input',renderSourceRegistry);

    // System status.
    async function runStatus(showToast = true) {
      const target = qs(root, '[data-system-status]');
      target.innerHTML = '<div class="sc-lab-status-row"><span>Lab REST API</span><span class="sc-lab-status-value warn">Checking</span><span>Testing WordPress route and source registry.</span></div>';
      try {
        const [status, sources] = await Promise.all([
          U.fetchJson(`${config.restBase}status`),
          U.fetchJson(`${config.restBase}sources/status`)
        ]);
        const rows = [
          ['Lab REST API', status.ok ? 'Ready' : 'Unavailable', `Version ${status.version || 'unknown'} · ${U.fmt(status.time)}`],
          ['Scientific source registry', sources.sources ? 'Ready' : 'Unavailable', `${Object.keys(sources.sources || {}).length} configured connectors`],
          ['Browser project storage', 'Ready', `${projects.items.length} local project${projects.items.length === 1 ? '' : 's'}`],
          ['Periodic table', Lab.Periodic?.getElements?.().length === 118 ? 'Ready' : 'Loading', `${Lab.Periodic?.getElements?.().length || 0} element records`],
          ['Calculator registry', Lab.Calculators?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.Calculators?.definitions?.length || 0} scientific calculators`],
          ['Physics laboratory', Lab.PhysicsLab?.particles?.length ? 'Ready' : 'Unavailable', `${Lab.PhysicsLab?.particles?.length || 0} particle reference records · ${Object.keys(Lab.PhysicsLab?.tools || {}).length} physics methods`],
          ['Biology laboratory', Lab.BiologyLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.BiologyLab?.definitions?.length || 0} computational biology methods · ${Lab.BiologyLab?.benchmarks?.length || 0} validation cases`],
          ['Astronomy laboratory', Lab.AstronomyLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.AstronomyLab?.definitions?.length || 0} astronomy methods · ${Lab.AstronomyLab?.benchmarks?.length || 0} validation cases`],
          ['Materials laboratory', Lab.MaterialsLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.MaterialsLab?.definitions?.length || 0} materials methods · ${Lab.MaterialsLab?.benchmarks?.length || 0} validation cases`],
          ['Earth systems laboratory', Lab.EarthLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.EarthLab?.definitions?.length || 0} Earth systems methods · ${Lab.EarthLab?.benchmarks?.length || 0} validation cases`],
          ['Energy and engineering laboratory', Lab.EnergyLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.EnergyLab?.definitions?.length || 0} energy and engineering methods · ${Lab.EnergyLab?.benchmarks?.length || 0} validation cases`], ['Mechanical and thermal engineering laboratory', Lab.MechanicalThermalLab?.definitions?.length ? 'Ready' : 'Unavailable', `${Lab.MechanicalThermalLab?.definitions?.length || 0} mechanical and thermal methods · ${Lab.MechanicalThermalLab?.benchmarks?.length || 0} validation cases`],
          ['Visualization and export engine', Lab.Visualization ? 'Ready' : 'Unavailable', 'SVG, PNG, PDF, CSV, JSON, project records, and Decision Studio packets'],
          ['Workspace data management', Lab.DataManagement ? 'Ready' : 'Unavailable', 'Workspace backup, restore, selective clearing, and factory reset']
        ];
        target.innerHTML = rows.map(([name, value, detail]) => `<div class="sc-lab-status-row"><span>${U.esc(name)}</span><span class="sc-lab-status-value ${value === 'Ready' ? 'ok' : 'warn'}">${U.esc(value)}</span><span>${U.esc(detail)}</span></div>`).join('');
        if (showToast) U.toast(root, 'System checks completed.');
      } catch (error) {
        target.innerHTML = `<div class="sc-lab-status-row"><span>Lab REST API</span><span class="sc-lab-status-value warn">Unavailable</span><span>${U.esc(error.message)}</span></div>`;
      }
    }
    qs(root, '[data-status-refresh]').addEventListener('click', () => runStatus(true));

    renderSelect();
    openModule(initial);
    root.dataset.scLabAppReady = '1';
    root.dataset.scLabRuntimeState = 'ready';
    d.dispatchEvent(new CustomEvent('sc-lab:app-ready', { detail: { version: config.version || '0.26.3.2', module: initial, root } }));
  }

  d.addEventListener('DOMContentLoaded', () => {
    d.querySelectorAll('.sc-lab-app').forEach(root => {
      try {
        init(root);
      } catch (error) {
        root.dataset.scLabAppFailed = '1';
        root.dataset.scLabRuntimeState = 'failed';
        reportRuntimeError('app-bootstrap', error, { module: root.dataset.initialModule || 'overview' });
        d.dispatchEvent(new CustomEvent('sc-lab:app-error', { detail: { error, module: root.dataset.initialModule || 'overview', root } }));
      }
    });
  });
})(window, document);
;
