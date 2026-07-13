const fs = require('fs');
const vm = require('vm');
const path = require('path');
const root = path.resolve(__dirname, '..');
const storage = new Map();
const localStorage = { getItem(key) { return storage.has(key) ? storage.get(key) : null; }, setItem(key, value) { storage.set(key, String(value)); }, removeItem(key) { storage.delete(key); } };
const context = {
  window: {},
  localStorage,
  console,
  setTimeout,
  clearTimeout,
  Blob: function () {},
  URL: { createObjectURL() { return ''; }, revokeObjectURL() {} },
  TextEncoder, TextDecoder, Uint8Array, Uint32Array, atob, btoa
};
context.window.window = context.window;
context.window.localStorage = localStorage;
vm.createContext(context);
function load(file) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, { filename: file });
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
load('assets/js/modules/core.js');
load('assets/js/modules/projects.js');
load('assets/js/modules/stoichiometry.js');
load('assets/js/modules/chemistry-lab.js');
load('assets/js/modules/spectrometry.js');
load('assets/js/modules/calculators.js');
load('assets/js/modules/datasets.js');
load('assets/js/modules/observations.js');
load('assets/js/modules/physics-lab.js');
load('assets/js/modules/physics-validation.js');
load('assets/js/modules/biology-lab.js');
load('assets/js/modules/astronomy-lab.js');
load('assets/js/modules/materials-lab.js');
load('assets/js/modules/earth-lab.js');
load('assets/js/modules/energy-lab.js');
load('assets/js/modules/method-contracts.js');
context.window.SCLabConfig={compute:{enabled:true,configured:true,endpoints:{status:'/status',languages:'/languages',methods:'/methods',execute:'/execute',compare:'/compare',jobs:'/jobs',reportValidate:'/reports/validate',reportPdf:'/reports/pdf',handoffValidate:'/handoffs/validate'}},nonce:'test'};
load('assets/js/modules/compute-client.js');
load('assets/js/modules/visualization.js');
load('assets/js/modules/reporting.js');
load('assets/js/modules/dimensional-visualization.js');
load('assets/js/modules/data-management.js');
load('assets/js/modules/workspace.js');

const ProjectModel = context.window.SCLab.ProjectModel;
const blankProject = ProjectModel.blank('Validation project');
assert(blankProject.schemaVersion === '0.20.0', 'Project schema version failed');
assert(Array.isArray(blankProject.physicsValidationRecords), 'Physics validation collection missing');
assert(Array.isArray(blankProject.astronomyRecords) && Array.isArray(blankProject.orbitalAnalyses) && Array.isArray(blankProject.astronomyValidationRecords), 'Astronomy project collections missing');
assert(Array.isArray(blankProject.biologyRecords) && Array.isArray(blankProject.sequences) && Array.isArray(blankProject.biologyValidationRecords), 'Biology project collections missing');
assert(Array.isArray(blankProject.materialsRecords) && Array.isArray(blankProject.crystallographyRecords) && Array.isArray(blankProject.materialsValidationRecords), 'Materials project collections missing');
assert(Array.isArray(blankProject.earthRecords) && Array.isArray(blankProject.oceanRecords) && Array.isArray(blankProject.earthValidationRecords), 'Earth systems project collections missing');
assert(Array.isArray(blankProject.energyRecords) && Array.isArray(blankProject.gridRecords) && Array.isArray(blankProject.energyValidationRecords), 'Energy project collections missing');
assert(Array.isArray(blankProject.visualizations) && Array.isArray(blankProject.dimensionalScenes) && Array.isArray(blankProject.chartExports) && Array.isArray(blankProject.analysisPackets) && Array.isArray(blankProject.reports) && Array.isArray(blankProject.reportFigures) && Array.isArray(blankProject.reportExports) && Array.isArray(blankProject.decisionStudioHandoffs), 'Visualization project collections missing');
assert(Array.isArray(blankProject.methodContracts) && Array.isArray(blankProject.codeArtifacts) && Array.isArray(blankProject.implementationComparisons) && Array.isArray(blankProject.codeExecutions) && Array.isArray(blankProject.languageComparisons) && Array.isArray(blankProject.runtimeRecords) && Array.isArray(blankProject.executionJobs) && Array.isArray(blankProject.crossLanguageValidationRecords), 'Code contract project collections missing');
const elements = JSON.parse(fs.readFileSync(path.join(root, 'assets/data/elements.json'), 'utf8'));
assert(elements.length === 118, 'Expected 118 elements');

const S = context.window.SCLab.Stoichiometry;
S.setElements(elements);
let composition = S.parseFormula('H2O');
assert(composition.H === 2 && composition.O === 1, 'H2O parse failed');
composition = S.parseFormula('Al2(SO4)3');
assert(composition.Al === 2 && composition.S === 3 && composition.O === 12, 'Parenthesized formula failed');
assert(Math.abs(S.molarMass('H2O').molarMass - 18.015) < 0.02, 'Molar mass failed');
const balance = S.balanceEquation('Fe + O2 -> Fe2O3');
assert(balance.coefficients.join(',') === '4,3,2', `Equation balance failed: ${balance.coefficients}`);
const limiting = S.limitingReagent('2 H2 + O2 -> 2 H2O', { H2: 3, O2: 2 });
assert(limiting.limiting === 'H2' && Math.abs(limiting.productMoles[0].moles - 3) < 1e-9, 'Limiting reagent failed');


const Chemistry = context.window.SCLab.ChemistryLab;
const weak = Chemistry.weakAcid({ concentration: 0.1, ka: 1.8e-5 });
assert(Math.abs(weak.pH - 2.875) < 0.02, 'Weak acid equilibrium failed');
const buffer = Chemistry.buffer({ pKa: 4.76, acid: 0.1, base: 0.1 });
assert(Math.abs(buffer.pH - 4.76) < 1e-12, 'Buffer calculation failed');
const titration = Chemistry.titration({ analyteType: 'acid', analyteC: 0.1, analyteMl: 25, titrantC: 0.1, titrantMl: 25 });
assert(Math.abs(titration.pH - 7) < 1e-12, 'Strong titration equivalence failed');
const nernst = Chemistry.nernst({ eStandard: 1.1, temperatureK: 298.15, electrons: 2, reactionQuotient: 10 });
assert(nernst.cellPotentialV < 1.1 && nernst.cellPotentialV > 1.06, 'Nernst calculation failed');
const empirical = Chemistry.empiricalFormula([{ symbol: 'C', amount: 40 }, { symbol: 'H', amount: 6.7 }, { symbol: 'O', amount: 53.3 }]);
assert(empirical.formula === 'CH2O', `Empirical formula failed: ${empirical.formula}`);
const cal = Chemistry.calibration({ points: [{x:0,y:0},{x:1,y:2},{x:2,y:4}], unknownSignal: 3 });
assert(Math.abs(cal.estimatedConcentration - 1.5) < 1e-12 && cal.rSquared > 0.999, 'Chemistry calibration failed');

const Spectrometry = context.window.SCLab.Spectrometry;
const points = Spectrometry.parse('400,0\n450,1\n500,0');
assert(Spectrometry.peaks(points).length === 1, 'Peak detection failed');
assert(Math.abs(Spectrometry.integrate(points) - 50) < 1e-9, 'Integration failed');
const normalized = Spectrometry.normalize(points, 'max');
assert(Math.abs(Math.max(...normalized.map(p => p.y)) - 1) < 1e-12, 'Spectrum normalization failed');
const absorbance = Spectrometry.transmittanceToAbsorbance([{x:500,y:0.1}]);
assert(Math.abs(absorbance[0].y - 1) < 1e-12, 'Transmittance conversion failed');
const advancedPeaks = Spectrometry.peaks(Spectrometry.parse('0,0\n1,2\n2,0\n3,3\n4,0'), { minDistance: 1, minProminence: 0.5 });
assert(advancedPeaks.length === 2 && advancedPeaks.every(p => Number.isFinite(p.fwhm)), 'Advanced peak characterization failed');


const Physics = context.window.SCLab.PhysicsLab;
assert(Physics.particles.length >= 20, 'Expected particle reference records');
assert(Object.keys(Physics.tools).length >= 30, 'Expected substantive physics method registry');
const projectile = Physics.tools.projectile({ v: 20, angle: 45, y0: 0, g: 9.80665 });
assert(projectile.range > 40 && projectile.range < 42 && projectile.series.length === 80, 'Projectile model failed');
const field = Physics.tools.coulomb({ q1: 1e-6, q2: -2e-6, r: 0.25 });
assert(field.interaction === 'attractive' && field.forceMagnitude > 0, 'Coulomb calculation failed');
const rlc = Physics.tools.rlc({ R: 100, L: 0.01, C: 1e-6, frequency: 1591.549, voltage: 10 });
assert(Math.abs(rlc.phaseDegrees) < 0.1 && Math.abs(rlc.impedanceMagnitude - 100) < 0.1, 'RLC resonance failed');
const photonPhysics = Physics.tools.photon({ wavelengthNm: 500 });
assert(Math.abs(photonPhysics.energyEv - 2.47968) < 0.001, 'Physics photon method failed');
const decay = Physics.tools.decay({ halfLife: 10, time: 20, initial: 1000 });
assert(Math.abs(decay.remaining - 250) < 1e-9, 'Nuclear decay failed');
const invariant = Physics.tools.invariantMass({ fourVectors: [{E:60,px:30,py:0,pz:40},{E:50,px:-20,py:0,pz:-30}] });
assert(invariant.invariantMass > 108 && invariant.invariantMass < 110, 'Invariant mass reconstruction failed');
const twoBody = Physics.tools.twoBodyDecay({ parentMass: 125.25, mass1: 0, mass2: 0 });
assert(Math.abs(twoBody.daughterMomentum - 62.625) < 1e-9, 'Two-body decay failed');
const detector = Physics.tools.detector({ B:2, radius:1.2, charge:1, distance:3, time:1.2e-8, events:1250, background:400, efficiency:0.82, luminosity:100 });
assert(detector.transverseMomentumGeVPerC > 0.7 && detector.signalEvents === 850, 'Detector analysis failed');
const validationReport = Physics.validation.runBenchmarks();
assert(validationReport.failed === 0 && validationReport.total >= 9, 'Physics benchmark validation failed');
const detectorInvalid = Physics.tools.detector({ B:2, radius:1.2, charge:1, distance:4, time:1e-9, events:100, background:10, efficiency:0.8, luminosity:50 });
assert(detectorInvalid._validation.status === 'invalid', 'Superluminal time-of-flight should fail validation');
const propagated = Physics.tools.powerLawUncertainty({ coefficient:1, variables:[{name:'x',value:2,uncertainty:0.1,power:2},{name:'y',value:3,uncertainty:0.2,power:1}] });
assert(Math.abs(propagated.value - 12) < 1e-12 && propagated.standardUncertainty > 1.3 && propagated.standardUncertainty < 1.5, 'Power-law uncertainty propagation failed');
const weighted = Physics.tools.weightedMean({ measurements:[{value:9.8,uncertainty:0.1},{value:10,uncertainty:0.2}] });
assert(weighted.weightedMean > 9.83 && weighted.weightedMean < 9.85 && weighted.reducedChiSquare > 0, 'Weighted mean failed');


const Biology = context.window.SCLab.BiologyLab;
assert(Biology.definitions.length >= 40, 'Expected substantive biology method registry');
const seqStats = Biology.tools.sequenceStats({ sequence: 'GCGCATAT' });
assert(Math.abs(seqStats.gcPercent - 50) < 1e-12 && seqStats.length === 8, 'DNA sequence statistics failed');
const translated = Biology.tools.translate({ sequence: 'ATGGGCTAA', frame: 0, stopAtStop: 'yes' });
assert(translated.protein === 'MG*', `Translation failed: ${translated.protein}`);
const alignment = Biology.tools.globalAlignment({ sequenceA: 'GATTACA', sequenceB: 'GCATGCU', match: 1, mismatch: -1, gap: -2 });
assert(alignment.alignmentLength >= 7 && Number.isFinite(alignment.score), 'Global alignment failed');
const local = Biology.tools.localAlignment({ sequenceA: 'TGTTACGG', sequenceB: 'GGTTGACTA', match: 2, mismatch: -1, gap: -2 });
assert(local.score > 0 && local.identityPercent > 0, 'Local alignment failed');
const enzyme = Biology.tools.michaelisMenten({ vmax: 100, substrate: 8, km: 2 });
assert(Math.abs(enzyme.rate - 80) < 1e-12, 'Michaelis-Menten failed');
const qpcr = Biology.tools.qpcr({ targetSampleCt: 22, targetReferenceCt: 18, controlSampleCt: 25, controlReferenceCt: 18, efficiency: 2 });
assert(Math.abs(qpcr.relativeExpression - 8) < 1e-12, 'qPCR relative expression failed');
const diversity = Biology.tools.shannonDiversity({ counts: '1,1,1,1' });
assert(Math.abs(diversity.shannonIndex - Math.log(4)) < 1e-12, 'Shannon diversity failed');
const ecology = Biology.tools.logisticGrowth({ initial: 50, carryingCapacity: 1000, growthRate: 0.4, time: 20 });
assert(ecology.population > 900 && ecology.series.length === 101, 'Logistic growth failed');
const protein = Biology.tools.proteinStats({ sequence: 'MKWVTFISLLFLFSSAYSRGVFRR' });
assert(protein.length === 24 && protein.molecularWeightDa > 2000, 'Protein properties failed');
const biologyValidation = Biology.runBenchmarks();
assert(biologyValidation.failed === 0 && biologyValidation.total >= 8, 'Biology benchmark validation failed');


const Astronomy = context.window.SCLab.AstronomyLab;
assert(Astronomy.definitions.length >= 40, 'Expected substantive astronomy method registry');
const jd = Astronomy.tools.julianDate({ isoDate: '2000-01-01T12:00:00Z' });
assert(Math.abs(jd.julianDate - 2451545.0) < 1e-9, 'Julian date failed');
const kep = Astronomy.tools.keplerPeriod({ semiMajorAxisAu: 1, centralMassSolar: 1 });
assert(Math.abs(kep.periodYears - 1) < 1e-12, 'Kepler period failed');
const parallax = Astronomy.tools.parallaxDistance({ parallaxArcsec: 0.1 });
assert(Math.abs(parallax.distanceParsec - 10) < 1e-12, 'Parallax distance failed');
const stellar = Astronomy.tools.stefanLuminosity({ radiusSolar: 1, tempK: 5772 });
assert(stellar.luminositySolar > 0.99 && stellar.luminositySolar < 1.01, 'Stellar luminosity failed');
const transit = Astronomy.tools.transitDepth({ planetRadiusJupiter: 1, starRadiusSolar: 1 });
assert(transit.percent > 0.9 && transit.percent < 1.1, 'Transit depth failed');
const blackbody = Astronomy.tools.blackbodySpectrum({ tempK: 5772, minNm: 100, maxNm: 2500, points: 100 });
assert(blackbody.series.length === 100 && blackbody.peakWavelengthNm > 500 && blackbody.peakWavelengthNm < 503, 'Blackbody spectrum failed');
const hubble = Astronomy.tools.hubbleDistance({ redshift: 0.01, h0: 70 });
assert(hubble.distanceMpc > 42 && hubble.distanceMpc < 43, 'Hubble distance failed');
const astroValidation = Astronomy.runBenchmarks();
assert(astroValidation.failed === 0 && astroValidation.total >= 10, 'Astronomy benchmark validation failed');


const Materials = context.window.SCLab.MaterialsLab;
assert(Materials.definitions.length >= 45, 'Expected substantive materials method registry');
const stress = Materials.tools.engineeringStress({ forceN: 1000, areaMm2: 10 });
assert(Math.abs(stress.stressMPa - 100) < 1e-12, 'Engineering stress failed');
const elasticMaterials = Materials.tools.elasticConstants({ youngsModulusGPa: 210, poissonRatio: 0.3 });
assert(elasticMaterials.shearModulusGPa > 80 && elasticMaterials.shearModulusGPa < 81, 'Elastic constants failed');
const bragg = Materials.tools.braggLaw({ wavelengthNm: 0.15406, twoThetaDeg: 60, order: 1 });
assert(Math.abs(bragg.dSpacingAngstrom - 1.5406) < 0.001, 'Bragg law failed');
const scherrer = Materials.run('scherrer', { wavelengthNm: 0.15406, fwhmDeg: 0.2, twoThetaDeg: 44.7, shapeFactor: 0.9 });
assert(scherrer.crystalliteSizeNm > 35 && scherrer._validation.status === 'validated', 'Scherrer analysis failed');
const leverMaterials = Materials.tools.leverRule({ composition: 50, alphaComposition: 20, betaComposition: 80 });
assert(Math.abs(leverMaterials.alphaFraction - 0.5) < 1e-12, 'Lever rule failed');
const corrosion = Materials.tools.corrosionRate({ massLossMg: 100, densityGcm3: 7.87, areaCm2: 10, timeHours: 168 });
assert(corrosion.corrosionRateMmYr > 0.65 && corrosion.corrosionRateMmYr < 0.67, 'Corrosion rate failed');
const composite = Materials.tools.ruleOfMixtures({ fiberFraction: 0.5, fiberModulusGPa: 100, matrixModulusGPa: 10 });
assert(Math.abs(composite.longitudinalModulusGPa - 55) < 1e-12, 'Composite rule of mixtures failed');
const particles = Materials.tools.particleStats({ diameters: [1,2,3,4,5] });
assert(particles.count === 5 && particles.d50 === 3, 'Particle statistics failed');
const materialsValidation = Materials.runBenchmarks();
assert(materialsValidation.failed === 0 && materialsValidation.total >= 10, 'Materials benchmark validation failed');

const Earth = context.window.SCLab.EarthLab;
assert(Earth.definitions.length >= 80, 'Expected substantive Earth systems method registry');
const plate = Earth.tools.plateMotion({ rateMmYr: 50, years: 1000, bearingDeg: 90 });
assert(Math.abs(plate.displacementM - 50) < 1e-12 && Math.abs(plate.eastM - 50) < 1e-12, 'Plate motion failed');
const forcingEarth = Earth.tools.co2RadiativeForcing({ initialPpm: 280, finalPpm: 560 });
assert(forcingEarth.radiativeForcingWm2 > 3.70 && forcingEarth.radiativeForcingWm2 < 3.72, 'CO2 forcing failed');
const runoffEarth = Earth.tools.rationalRunoff({ runoffCoefficient: 0.6, rainfallIntensityMmHr: 50, areaKm2: 2 });
assert(Math.abs(runoffEarth.peakDischargeM3S - 16.6666667) < 1e-5, 'Rational runoff failed');
const tsunami = Earth.tools.tsunamiTravel({ distanceKm: 1000, meanDepthM: 4000 });
assert(tsunami.travelTimeHours > 1.3 && tsunami.travelTimeHours < 1.5, 'Tsunami travel failed');
const ndviEarth = Earth.tools.ndvi({ nir: 0.6, red: 0.2 });
assert(Math.abs(ndviEarth.ndvi - 0.5) < 1e-12, 'NDVI failed');
const marineDiversity = Earth.tools.shannonMarine({ counts: '1,1,1,1' });
assert(Math.abs(marineDiversity.shannonIndex - Math.log(4)) < 1e-8, 'Marine diversity failed');
const earthValidation = Earth.runBenchmarks();
assert(earthValidation.failed === 0 && earthValidation.total >= 12, 'Earth systems benchmark validation failed');


const Energy = context.window.SCLab.EnergyLab;
assert(Energy.definitions.length >= 100, 'Expected substantive energy and engineering method registry');
assert(Energy.definitions.every(def => typeof Energy.tools[def.id] === 'function'), 'Every energy definition must have an implementation');
assert(new Set(Energy.definitions.map(def => def.id)).size === Energy.definitions.length, 'Energy method identifiers must be unique');
const pvEnergy = Energy.tools.pvPower({ irradianceWm2: 1000, areaM2: 10, moduleEfficiency: 0.2, systemFactor: 1 });
assert(Math.abs(pvEnergy.dcPowerKW - 2) < 1e-12, 'PV output failed');
const windEnergy = Energy.tools.windPower({ airDensityKgM3: 1.225, sweptAreaM2: 100, windSpeedMS: 8, powerCoefficient: 0.4 });
assert(Math.abs(windEnergy.powerKW - 12.544) < 1e-9, 'Wind output failed');
const hydroEnergy = Energy.tools.hydroPower({ waterDensityKgM3: 1000, flowM3S: 1, headM: 10, efficiency: 1 });
assert(Math.abs(hydroEnergy.powerW - 98066.5) < 1e-6, 'Hydropower failed');
const storageEnergy = Energy.tools.batteryEnergy({ voltageV: 48, capacityAh: 100, usableFraction: 0.8 });
assert(Math.abs(storageEnergy.usableEnergyKWh - 3.84) < 1e-12, 'Battery energy failed');
const gridEnergy = Energy.tools.threePhasePower({ lineVoltageV: 400, lineCurrentA: 100, powerFactor: 1 });
assert(Math.abs(gridEnergy.realPowerW - 69282.0323) < 0.1, 'Three-phase power failed');
const thermalEnergy = Energy.tools.conduction({ thermalConductivityWmK: 0.04, areaM2: 100, tempHotC: 20, tempColdC: 0, thicknessM: 0.2 });
assert(Math.abs(thermalEnergy.heatTransferW - 400) < 1e-12, 'Thermal conduction failed');
const lcoeEnergy = Energy.tools.lcoe({ capitalCost: 0.000001, annualFixedCost: 0, variableCostPerMWh: 50, annualEnergyMWh: 100, discountRate: 0, lifetimeYears: 1 });
assert(Math.abs(lcoeEnergy.lcoePerMWh - 50) < 1e-6, 'LCOE failed');
const reliabilityEnergy = Energy.tools.seriesReliability({ componentReliabilities: '0.9,0.8' });
assert(Math.abs(reliabilityEnergy.systemReliability - 0.72) < 1e-12, 'Series reliability failed');
const energyValidation = Energy.runBenchmarks();
assert(energyValidation.failed === 0 && energyValidation.total >= 12, 'Energy benchmark validation failed');

const Calculators = context.window.SCLab.Calculators;
assert(Calculators.definitions.length >= 30, 'Expected at least 30 calculators');
assert(Math.abs(Calculators.run('photon', { wavelengthNm: 500 }).electronVolts - 2.47968) < 0.001, 'Photon calculator failed');
assert(Math.abs(Calculators.run('michaelis', { vmax: 100, substrate: 8, km: 2 }).rate - 80) < 1e-9, 'Michaelis-Menten failed');


const MethodContracts = context.window.SCLab.MethodContracts;
assert(MethodContracts.contracts.length >= 19, 'Expected portable method contract catalog');
assert(Object.keys(MethodContracts.languages).length === 12 && MethodContracts.languages.rust, 'Expected twelve language targets including Rust');
const portableKinetic = MethodContracts.evaluate('kinetic', { mass: 10, velocity: 5 });
assert(Math.abs(portableKinetic.kineticEnergyJ - 125) < 1e-12 && portableKinetic.momentumKgMs === 50, 'Portable kinetic method failed');
const portableProjectile = MethodContracts.evaluate('projectile', { speed:20, angleDeg:45, height:0 });
assert(portableProjectile.rangeM > 40 && portableProjectile.rangeM < 42, 'Portable projectile method failed');
for (const language of Object.keys(MethodContracts.languages)) {
  const generated = MethodContracts.generate('kinetic', language);
  assert(generated.includes('Kinetic energy and momentum') && generated.length > 180, `Generated ${language} source failed`);
}
new vm.Script(MethodContracts.generate('kinetic', 'javascript'));
assert(MethodContracts.generate('kinetic','rust').includes('fn main()'), 'Rust source marker missing');
assert(MethodContracts.generate('kinetic','fortran').includes('program sc_lab_method'), 'Fortran source marker missing');
assert(MethodContracts.generate('kinetic','sql').includes('WITH inputs AS'), 'SQL source marker missing');
const parity = MethodContracts.validateAgainstRuntime('kinetic', {mass:10,velocity:5});
assert(parity.passed && parity.rows.every(row=>row.passed), 'Portable method parity failed');
assert(MethodContracts.notebook('kinetic').nbformat === 4, 'Notebook generation failed');
const ComputeClient = context.window.SCLab.ComputeClient;
assert(ComputeClient.isConfigured() && ComputeClient.config().endpoints.execute === '/execute' && ComputeClient.config().endpoints.reportPdf === '/reports/pdf', 'Compute client configuration failed');


const Visualization = context.window.SCLab.Visualization;
const scalarContract = Visualization.makeContract({ methodId:'test.scalar', title:'Scalar test', inputs:{x:2}, outputs:{alpha:10,beta:4}, project:blankProject });
assert(scalarContract.schema === 'sc-lab-analysis/1.0' && scalarContract.chartSpec.type === 'bar', 'Universal scalar result contract failed');
assert(scalarContract.audit.inputFingerprint && scalarContract.audit.outputFingerprint, 'Analysis audit fingerprints missing');
const scalarSvg = Visualization.renderSVG(scalarContract.chartSpec, { theme:'institutional', aspect:'16:9' });
assert(
  typeof scalarSvg === 'string' &&
  scalarSvg.includes('<svg') &&
  scalarSvg.includes('Scalar test') &&
  scalarSvg.includes('Sustainable Catalyst Lab v0.20.0'),
  'Universal SVG renderer failed'
);
assert(Visualization.csv(scalarContract).includes('metric,value') || Visualization.csv(scalarContract).includes('label,value'), 'Universal CSV export failed');
const seriesContract = Visualization.makeContract({ methodId:'test.series', title:'Series test', outputs:{series:[{x:0,y:1},{x:1,y:3},{x:2,y:2}]} });
assert(seriesContract.chartSpec.type === 'line' && seriesContract.chartSpec.data.length === 3, 'Series chart inference failed');
const packet = Visualization.analysisPacket(seriesContract, Visualization.renderSVG(seriesContract.chartSpec));
assert(packet.packetType === 'scientific-analysis' && packet.charts.length === 1 && packet.analysis.methodId === 'test.series', 'Decision Studio analysis packet failed');
const fakeJpeg = 'data:image/jpeg;base64,' + Buffer.from([255,216,255,217]).toString('base64');
const pdfBytes = Visualization.makeJpegPdf(fakeJpeg, 10, 10, 'PDF test');
assert(pdfBytes.length > 400 && Buffer.from(pdfBytes).toString('latin1').startsWith('%PDF-1.4'), 'Direct PDF generator failed');

const Reporting = context.window.SCLab.Reporting;
const report = Reporting.makeReport({ title:'Auditable test report', subtitle:'PDF and handoff validation', executiveSummary:'Deterministic report test.', project:blankProject, analyses:[scalarContract,seriesContract] });
assert(report.schema === 'sc-lab-report/1.0' && report.analyses.length === 2 && report.tables.length === 2, 'Report contract generation failed');
const reportPacket = Reporting.makeDecisionStudioPacket(report);
assert(reportPacket.packetType === 'scientific-report' && reportPacket.schemaVersion === '2.0' && reportPacket.analyses.length === 2, 'Decision Studio report packet failed');
const reportPdf = Reporting.makePdf(report);
assert(reportPdf.length > 1200 && Buffer.from(reportPdf).toString('latin1').startsWith('%PDF-1.4'), 'Structured local report PDF failed');
assert(Reporting.flatten({alpha:1,nested:{beta:2}}).length === 2, 'Report table flattening failed');


const Dimensional = context.window.SCLab.DimensionalVisualization;
const tesseract = Dimensional.presets.tesseract4d();
assert(tesseract.dimensions === 4 && tesseract.vertices.length === 16 && tesseract.edges.length === 32, 'Tesseract topology failed');
const simplex4d = Dimensional.presets.simplex4d();
assert(simplex4d.vertices.length === 5 && simplex4d.edges.length === 10, '4-simplex topology failed');
const cell16 = Dimensional.presets.crossPolytope4d();
assert(cell16.vertices.length === 8 && cell16.edges.length === 24, '16-cell topology failed');
const rotated4 = Dimensional.rotate4([1,2,3,4], {xw:90,yz:33});
const normBefore = Math.sqrt(1+4+9+16), normAfter = Math.sqrt(rotated4.reduce((sum,v)=>sum+v*v,0));
assert(Math.abs(normBefore-normAfter) < 1e-10, '4D rotation must preserve Euclidean norm');
const projected = Dimensional.project4To3(Dimensional.rotate4([1,1,1,1], {xw:25,yw:-15}), 4);
assert(projected.length === 3 && projected.every(Number.isFinite), '4D projection failed');
const tesseractSvg = Dimensional.renderSVG(tesseract, {theme:'institutional',rotation4:{xw:25,yw:-18,zw:12},rotation3:{x:18,y:-24,z:8}});
assert(tesseractSvg.includes('<svg') && tesseractSvg.includes('4D → 3D → 2D') && tesseractSvg.includes('16 vertices'), 'Projected 4D SVG renderer failed');
const derivedScene = Dimensional.sceneFromContract(scalarContract, 4);
assert(derivedScene.dimensions === 4 && derivedScene.metadata.derived === true && derivedScene.metadata.warning, 'Universal derived result-space scene failed');
const parsedScene = Dimensional.parseScene('{"dimensions":3,"title":"Triangle","vertices":[[0,0,0],[1,0,0],[0,1,0]],"edges":[[0,1],[1,2],[2,0]]}');
assert(parsedScene.vertices.length === 3 && parsedScene.edges.length === 3, 'Custom scene parser failed');
const sceneContract = Dimensional.sceneContract(tesseract,tesseractSvg,blankProject,seriesContract);
const scenePacket = Visualization.analysisPacket(sceneContract,tesseractSvg);
assert(scenePacket.scenes.length === 1 && scenePacket.charts.length === 0 && scenePacket.scenes[0].dimensions === 4, 'Decision Studio dimensional scene handoff failed');
const packageEntries = Visualization.analysisPackageEntries(sceneContract,tesseractSvg);
assert(packageEntries['analysis.json'] && packageEntries['chart.svg'] && packageEntries['scene.json'] && packageEntries['decision-studio-packet.json'], 'Analysis package entries failed');

const DataManagement = context.window.SCLab.DataManagement;
const zipBytes = DataManagement.makeZip({'workspace.json':'{"ok":true}','README.md':'test'});
const zipEntries = DataManagement.parseStoredZip(zipBytes);
assert(new TextDecoder().decode(zipEntries['workspace.json']) === '{"ok":true}', 'Workspace ZIP round trip failed');
const projectStore = new context.window.SCLab.Projects();
projectStore.add('notes',{title:'Reset note',body:'remove me'},'test note');
projectStore.add('observations',{title:'Reset observation'},'test observation');
projectStore.add('visualizations',{title:'Saved chart'},'test chart');
const beforeReset = DataManagement.counts(projectStore);
assert(DataManagement.scopeRemovalCount(projectStore,'notes-observations') >= 2, 'Reset scope count failed');
assert(beforeReset.notes >= 1 && beforeReset.observations >= 1 && beforeReset.visualizations >= 1, 'Workspace counts failed');
const backup = DataManagement.workspace(projectStore);
DataManagement.reset(projectStore,'notes-observations');
assert(projectStore.get().notes.length === 0 && projectStore.get().observations.length === 0 && projectStore.get().visualizations.length >= 1, 'Selective notes and observations reset failed');
const restored = DataManagement.restore(projectStore,backup,'replace');
assert(restored.restored >= 1 && projectStore.get().notes.length >= 1, 'Workspace restore failed');

const Workspace = context.window.SCLab.Workspace;
assert(Workspace.modules.length >= 20, 'Expected grouped module catalog');
assert(Workspace.quickTools.length >= 16, 'Expected quick scientific tools');
const search = Workspace.search('stoichiometry', Calculators.definitions);
assert(search.length && search[0].id === 'stoichiometry', 'Command search failed');
const trace = Workspace.traceCounts({ evidence: [{ source: 'USGS' }, { source: 'NASA' }], hypotheses: [], calculations: [1], experiments: [1, 2], decisions: [], documents: [] });
assert(trace[0].value === 2 && trace[5].value === 1 && trace[6].value === 2, 'Traceability counts failed');
assert(Workspace.projectTotal({ evidence: [1], experiments: [], hypotheses: [], decisions: [], notes: [1], calculations: [], documents: [], maps: [] }) === 2, 'Project total failed');

const D=context.window.SCLab.Datasets;const ds=D.parseCSV('x,y\n1,2\n3,4');assert(ds.rows.length===2&&D.summary(ds).numeric.y.mean===3,'Dataset inspector failed');const O=context.window.SCLab.Observations;assert(O.telescope({title:'JWST deep field'})==='JWST','Telescope classification failed');console.log(`JS tests passed: ${elements.length} elements, ${Calculators.definitions.length} calculators, ${Object.keys(Physics.tools).length} physics methods, ${Biology.definitions.length} biology methods, ${Astronomy.definitions.length} astronomy methods, ${Materials.definitions.length} materials methods, ${Earth.definitions.length} Earth systems methods, ${Energy.definitions.length} energy methods, ${validationReport.total + biologyValidation.total + astroValidation.total + materialsValidation.total + earthValidation.total + energyValidation.total} validation benchmarks, ${Workspace.modules.length} modules.`);
