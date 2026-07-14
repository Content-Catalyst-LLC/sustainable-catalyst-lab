'use strict';const assert=require('node:assert/strict');const path=require('node:path');global.window={SCLab:{}};require(path.resolve(__dirname,'../assets/js/modules/genomic-validation-sequence-provenance-v0243.js'));const api=window.SCLab.GenomicValidationSequenceProvenance;
assert.equal(api.contract.profiles.length,8);assert.equal(api.contract.eventTypes.length,6);
const validation=api.evaluate('sequence-record-integrity',[{sequenceId:'s1',sequence:'ACGTN',alphabet:'DNA'}]);assert.equal(validation.decision,'pass');
const manifest=api.createManifest([{id:'s1',sequence:'ACGT'}],[{sequenceId:'s1'}],{build:'GRCh38'},[{step:'align'}],[],[]);
const first=api.createRecord(manifest,{recordId:'r1',timestamp:'2026-07-14T00:00:00.000Z',eventType:'sequence-import',datasetId:'d1'}),second=api.createRecord({decision:'pass'},{recordId:'r2',timestamp:'2026-07-14T00:01:00.000Z',eventType:'validation-decision',datasetId:'d1'},first.recordHash);
assert.equal(api.verifyLedger([first,second]).valid,true);const tampered=JSON.parse(JSON.stringify([first,second]));tampered[1].payload.decision='fail';assert.equal(api.verifyLedger(tampered).valid,false);
const dossier=api.createDossier([validation],manifest,[first,second],'release');assert.equal(dossier.summary.releaseReady,true);assert.equal(dossier.dossierHash.length,64);
console.log('Lab v0.24.3 JS tests passed: 8 profiles, 6 events, manifest hashing, ledger verification, tamper detection, dossier.');
