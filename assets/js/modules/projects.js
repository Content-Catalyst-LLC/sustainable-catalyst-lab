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
