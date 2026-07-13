(function (global) {
'use strict';

const Lab = global.SCLab = global.SCLab || {};
const VERSION = '0.20.0';
const CATALOG = {"schema":"sc-lab-microbiology-laboratory-catalog/1.0","version":"0.20.0","methodCount":48,"categories":["Microbial growth & population dynamics","Culture systems & bioreactor kinetics","Enumeration, microscopy & assay quantification","Environmental & food microbiology","Antimicrobial & disinfection screening","Microbial ecology & laboratory quality control"],"methods":[{"id":"mb.exponential_growth","category":"Microbial growth & population dynamics","title":"Exponential microbial growth","equation":"N_t = N_0 e^(\u03bct)","inputs":[{"key":"initialPopulation","label":"Initial population","unit":"cells or CFU","default":100000},{"key":"specificGrowthRatePerHour","label":"Specific growth rate","unit":"1/h","default":0.65},{"key":"timeHours","label":"Growth time","unit":"h","default":6}],"outputs":{"finalPopulation":{"expression":"initialPopulation*exp(specificGrowthRatePerHour*timeHours)","unit":"cells or CFU"}},"assumptions":["Constant specific growth rate and no resource limitation during the interval."],"notes":[],"version":"0.20.0"},{"id":"mb.specific_growth_rate","category":"Microbial growth & population dynamics","title":"Observed specific growth rate","equation":"\u03bc = ln(N_t/N_0)/t","inputs":[{"key":"initialPopulation","label":"Initial population","unit":"cells or CFU","default":100000},{"key":"finalPopulation","label":"Final population","unit":"cells or CFU","default":5000000},{"key":"timeHours","label":"Elapsed time","unit":"h","default":6}],"outputs":{"specificGrowthRatePerHour":{"expression":"log(finalPopulation/initialPopulation)/timeHours","unit":"1/h"}},"assumptions":["Population estimates describe the same viable or total-cell basis."],"notes":[],"version":"0.20.0"},{"id":"mb.generation_time","category":"Microbial growth & population dynamics","title":"Generation time","equation":"g = ln(2)/\u03bc","inputs":[{"key":"specificGrowthRatePerHour","label":"Specific growth rate","unit":"1/h","default":0.65}],"outputs":{"generationTimeHours":{"expression":"log(2)/specificGrowthRatePerHour","unit":"h"}},"assumptions":["Positive constant specific growth rate."],"notes":[],"version":"0.20.0"},{"id":"mb.number_of_generations","category":"Microbial growth & population dynamics","title":"Number of generations","equation":"n = log\u2082(N_t/N_0)","inputs":[{"key":"initialPopulation","label":"Initial population","unit":"cells or CFU","default":100000},{"key":"finalPopulation","label":"Final population","unit":"cells or CFU","default":12800000}],"outputs":{"generationCount":{"expression":"log(finalPopulation/initialPopulation)/log(2)","unit":"generations"}},"assumptions":["Binary fission equivalent and compatible population measurements."],"notes":[],"version":"0.20.0"},{"id":"mb.logistic_growth","category":"Microbial growth & population dynamics","title":"Logistic growth","equation":"N_t = K/[1 + ((K\u2212N_0)/N_0)e^(\u2212rt)]","inputs":[{"key":"initialPopulation","label":"Initial population","unit":"cells or CFU","default":100000},{"key":"carryingCapacity","label":"Carrying capacity","unit":"cells or CFU","default":1000000000},{"key":"intrinsicGrowthRatePerHour","label":"Intrinsic growth rate","unit":"1/h","default":0.8},{"key":"timeHours","label":"Elapsed time","unit":"h","default":12}],"outputs":{"finalPopulation":{"expression":"carryingCapacity/(1+((carryingCapacity-initialPopulation)/initialPopulation)*exp(-intrinsicGrowthRatePerHour*timeHours))","unit":"cells or CFU"}},"assumptions":["Fixed carrying capacity and homogeneous population."],"notes":[],"version":"0.20.0"},{"id":"mb.first_order_death","category":"Microbial growth & population dynamics","title":"First-order microbial inactivation","equation":"N_t = N_0 e^(\u2212kt)","inputs":[{"key":"initialPopulation","label":"Initial viable population","unit":"CFU","default":1000000},{"key":"inactivationRatePerHour","label":"Inactivation rate","unit":"1/h","default":0.9},{"key":"timeHours","label":"Exposure time","unit":"h","default":3}],"outputs":{"survivingPopulation":{"expression":"initialPopulation*exp(-inactivationRatePerHour*timeHours)","unit":"CFU"}},"assumptions":["Single first-order inactivation population."],"notes":[],"version":"0.20.0"},{"id":"mb.population_fold_change","category":"Microbial growth & population dynamics","title":"Population fold change","equation":"Fold change = N_t/N_0","inputs":[{"key":"initialPopulation","label":"Initial population","unit":"cells or CFU","default":100000},{"key":"finalPopulation","label":"Final population","unit":"cells or CFU","default":800000}],"outputs":{"populationFoldChange":{"expression":"finalPopulation/initialPopulation","unit":"1"}},"assumptions":["Initial and final measurements use the same method and units."],"notes":[],"version":"0.20.0"},{"id":"mb.carrying_capacity_utilization","category":"Microbial growth & population dynamics","title":"Carrying-capacity utilization","equation":"Utilization = N/K","inputs":[{"key":"observedPopulation","label":"Observed population","unit":"cells or CFU","default":800000000},{"key":"carryingCapacity","label":"Carrying capacity","unit":"cells or CFU","default":1000000000}],"outputs":{"carryingCapacityFraction":{"expression":"observedPopulation/carryingCapacity","unit":"1"}},"assumptions":["Observed population and carrying capacity use the same basis."],"notes":[],"version":"0.20.0"},{"id":"mb.chemostat_dilution_rate","category":"Culture systems & bioreactor kinetics","title":"Chemostat dilution rate","equation":"D = F/V","inputs":[{"key":"flowRateLPerHour","label":"Feed flow rate","unit":"L/h","default":2.5},{"key":"reactorVolumeL","label":"Working volume","unit":"L","default":10}],"outputs":{"dilutionRatePerHour":{"expression":"flowRateLPerHour/reactorVolumeL","unit":"1/h"}},"assumptions":["Constant volume and equal inlet/outlet flow."],"notes":[],"version":"0.20.0"},{"id":"mb.chemostat_residence_time","category":"Culture systems & bioreactor kinetics","title":"Hydraulic residence time","equation":"\u03c4 = V/F = 1/D","inputs":[{"key":"reactorVolumeL","label":"Working volume","unit":"L","default":10},{"key":"flowRateLPerHour","label":"Flow rate","unit":"L/h","default":2.5}],"outputs":{"residenceTimeHours":{"expression":"reactorVolumeL/flowRateLPerHour","unit":"h"}},"assumptions":["Constant working volume and flow."],"notes":[],"version":"0.20.0"},{"id":"mb.monod_growth_rate","category":"Culture systems & bioreactor kinetics","title":"Monod specific growth rate","equation":"\u03bc = \u03bc_max S/(K_s + S)","inputs":[{"key":"maximumGrowthRatePerHour","label":"Maximum specific growth rate","unit":"1/h","default":0.9},{"key":"substrateConcentrationMgL","label":"Limiting substrate","unit":"mg/L","default":40},{"key":"halfSaturationMgL","label":"Half-saturation constant","unit":"mg/L","default":10}],"outputs":{"specificGrowthRatePerHour":{"expression":"maximumGrowthRatePerHour*substrateConcentrationMgL/(halfSaturationMgL+substrateConcentrationMgL)","unit":"1/h"}},"assumptions":["Single limiting substrate and Monod kinetics."],"notes":[],"version":"0.20.0"},{"id":"mb.chemostat_steady_substrate","category":"Culture systems & bioreactor kinetics","title":"Chemostat steady-state substrate","equation":"S* = K_sD/(\u03bc_max\u2212D)","inputs":[{"key":"halfSaturationMgL","label":"Half-saturation constant","unit":"mg/L","default":10},{"key":"dilutionRatePerHour","label":"Dilution rate","unit":"1/h","default":0.25},{"key":"maximumGrowthRatePerHour","label":"Maximum specific growth rate","unit":"1/h","default":0.9}],"outputs":{"steadyStateSubstrateMgL":{"expression":"halfSaturationMgL*dilutionRatePerHour/(maximumGrowthRatePerHour-dilutionRatePerHour)","unit":"mg/L"}},"assumptions":["Steady-state Monod chemostat with dilution rate below maximum growth rate."],"notes":[],"version":"0.20.0"},{"id":"mb.washout_margin","category":"Culture systems & bioreactor kinetics","title":"Chemostat washout margin","equation":"Margin = \u03bc_max \u2212 D","inputs":[{"key":"maximumGrowthRatePerHour","label":"Maximum specific growth rate","unit":"1/h","default":0.9},{"key":"dilutionRatePerHour","label":"Dilution rate","unit":"1/h","default":0.25}],"outputs":{"washoutMarginPerHour":{"expression":"maximumGrowthRatePerHour-dilutionRatePerHour","unit":"1/h"}},"assumptions":["Positive margin indicates the nominal dilution rate is below maximum growth."],"notes":[],"version":"0.20.0"},{"id":"mb.biomass_productivity","category":"Culture systems & bioreactor kinetics","title":"Volumetric biomass productivity","equation":"P_X = D X","inputs":[{"key":"dilutionRatePerHour","label":"Dilution rate","unit":"1/h","default":0.25},{"key":"biomassConcentrationGL","label":"Biomass concentration","unit":"g/L","default":4.2}],"outputs":{"biomassProductivityGLH":{"expression":"dilutionRatePerHour*biomassConcentrationGL","unit":"g/(L*h)"}},"assumptions":["Steady continuous culture and representative biomass concentration."],"notes":[],"version":"0.20.0"},{"id":"mb.biomass_yield_on_substrate","category":"Culture systems & bioreactor kinetics","title":"Biomass yield on substrate","equation":"Y_X/S = \u0394X/\u0394S","inputs":[{"key":"biomassProducedG","label":"Biomass produced","unit":"g","default":42},{"key":"substrateConsumedG","label":"Substrate consumed","unit":"g","default":70}],"outputs":{"biomassYieldGPerG":{"expression":"biomassProducedG/substrateConsumedG","unit":"g/g"}},"assumptions":["Biomass and substrate balances use the same interval and dry-mass basis."],"notes":[],"version":"0.20.0"},{"id":"mb.oxygen_uptake_rate","category":"Culture systems & bioreactor kinetics","title":"Volumetric oxygen uptake rate","equation":"OUR = q_O2 X","inputs":[{"key":"specificOxygenUptakeMgGHour","label":"Specific oxygen uptake","unit":"mg O2/(g*h)","default":85},{"key":"biomassConcentrationGL","label":"Biomass concentration","unit":"g/L","default":4.2}],"outputs":{"oxygenUptakeRateMgLHour":{"expression":"specificOxygenUptakeMgGHour*biomassConcentrationGL","unit":"mg O2/(L*h)"}},"assumptions":["Representative specific uptake and biomass concentration."],"notes":[],"version":"0.20.0"},{"id":"mb.cfu_per_ml","category":"Enumeration, microscopy & assay quantification","title":"Colony-forming units per milliliter","equation":"CFU/mL = colonies/(volume plated \u00d7 dilution)","inputs":[{"key":"colonyCount","label":"Counted colonies","unit":"colonies","default":126},{"key":"platedVolumeMl","label":"Plated volume","unit":"mL","default":0.1},{"key":"sampleDilution","label":"Sample fraction plated","unit":"1","default":0.0001}],"outputs":{"cfuPerMl":{"expression":"colonyCount/(platedVolumeMl*sampleDilution)","unit":"CFU/mL"}},"assumptions":["Counted colonies arise from the stated dilution and plated volume."],"notes":[],"version":"0.20.0"},{"id":"mb.pfu_per_ml","category":"Enumeration, microscopy & assay quantification","title":"Plaque-forming units per milliliter","equation":"PFU/mL = plaques/(volume plated \u00d7 dilution)","inputs":[{"key":"plaqueCount","label":"Counted plaques","unit":"plaques","default":84},{"key":"platedVolumeMl","label":"Plated volume","unit":"mL","default":0.1},{"key":"sampleDilution","label":"Sample fraction plated","unit":"1","default":1e-05}],"outputs":{"pfuPerMl":{"expression":"plaqueCount/(platedVolumeMl*sampleDilution)","unit":"PFU/mL"}},"assumptions":["Plaques arise from the stated dilution and plated volume."],"notes":[],"version":"0.20.0"},{"id":"mb.serial_dilution_factor","category":"Enumeration, microscopy & assay quantification","title":"Cumulative serial dilution","equation":"Dilution = d\u2081d\u2082d\u2083d\u2084","inputs":[{"key":"dilutionStep1","label":"Dilution step 1","unit":"1","default":0.1},{"key":"dilutionStep2","label":"Dilution step 2","unit":"1","default":0.1},{"key":"dilutionStep3","label":"Dilution step 3","unit":"1","default":0.1},{"key":"dilutionStep4","label":"Dilution step 4","unit":"1","default":0.1}],"outputs":{"cumulativeDilution":{"expression":"dilutionStep1*dilutionStep2*dilutionStep3*dilutionStep4","unit":"1"}},"assumptions":["Each step is expressed as sample volume divided by total diluted volume."],"notes":[],"version":"0.20.0"},{"id":"mb.hemocytometer_concentration","category":"Enumeration, microscopy & assay quantification","title":"Hemocytometer cell concentration","equation":"Cells/mL = average count \u00d7 chamber factor \u00d7 dilution factor","inputs":[{"key":"averageCellCount","label":"Average cells per counted square","unit":"cells","default":72},{"key":"chamberFactorPerMl","label":"Chamber conversion factor","unit":"1/mL","default":10000},{"key":"dilutionFactor","label":"Reciprocal sample dilution","unit":"1","default":2}],"outputs":{"cellsPerMl":{"expression":"averageCellCount*chamberFactorPerMl*dilutionFactor","unit":"cells/mL"}},"assumptions":["Counting geometry and chamber factor match the selected grid."],"notes":[],"version":"0.20.0"},{"id":"mb.viable_fraction","category":"Enumeration, microscopy & assay quantification","title":"Viable-cell fraction","equation":"Viability = viable cells/total cells","inputs":[{"key":"viableCellCount","label":"Viable cells","unit":"cells","default":880},{"key":"totalCellCount","label":"Total cells","unit":"cells","default":1000}],"outputs":{"viableFraction":{"expression":"viableCellCount/totalCellCount","unit":"1"}},"assumptions":["Viable and total counts use the same field or population."],"notes":[],"version":"0.20.0"},{"id":"mb.od_calibrated_biomass","category":"Enumeration, microscopy & assay quantification","title":"Optical-density biomass calibration","equation":"X = slope \u00d7 OD + intercept","inputs":[{"key":"opticalDensity","label":"Optical density","unit":"AU","default":0.85},{"key":"calibrationSlopeGLPerAu","label":"Calibration slope","unit":"g/L per AU","default":0.42},{"key":"calibrationInterceptGL","label":"Calibration intercept","unit":"g/L","default":0.02}],"outputs":{"biomassConcentrationGL":{"expression":"calibrationSlopeGLPerAu*opticalDensity+calibrationInterceptGL","unit":"g/L"}},"assumptions":["Linear calibration is valid over the stated OD range."],"notes":[],"version":"0.20.0"},{"id":"mb.assay_recovery","category":"Enumeration, microscopy & assay quantification","title":"Microbial assay recovery","equation":"Recovery = measured amount/spiked amount","inputs":[{"key":"measuredAmount","label":"Measured recovered amount","unit":"cells, CFU, or copies","default":820000},{"key":"spikedAmount","label":"Known spike amount","unit":"cells, CFU, or copies","default":1000000}],"outputs":{"recoveryFraction":{"expression":"measuredAmount/spikedAmount","unit":"1"}},"assumptions":["Measured and spiked quantities use the same assay basis."],"notes":[],"version":"0.20.0"},{"id":"mb.z_prime_factor","category":"Enumeration, microscopy & assay quantification","title":"Assay Z-prime factor","equation":"Z' = 1 \u2212 3(\u03c3_p + \u03c3_n)/|\u03bc_p \u2212 \u03bc_n|","inputs":[{"key":"positiveMean","label":"Positive-control mean","unit":"signal","default":1.0},{"key":"negativeMean","label":"Negative-control mean","unit":"signal","default":0.1},{"key":"positiveSd","label":"Positive-control standard deviation","unit":"signal","default":0.04},{"key":"negativeSd","label":"Negative-control standard deviation","unit":"signal","default":0.03}],"outputs":{"zPrimeFactor":{"expression":"1-3*(positiveSd+negativeSd)/abs(positiveMean-negativeMean)","unit":"1"}},"assumptions":["Control distributions are representative and sufficiently replicated."],"notes":[],"version":"0.20.0"},{"id":"mb.first_order_environmental_decay","category":"Environmental & food microbiology","title":"Environmental first-order microbial decay","equation":"C_t = C_0 e^(\u2212kt)","inputs":[{"key":"initialConcentration","label":"Initial concentration","unit":"CFU, cells, or copies/volume","default":1000000},{"key":"decayRatePerDay","label":"Decay rate","unit":"1/day","default":0.45},{"key":"timeDays","label":"Elapsed time","unit":"day","default":5}],"outputs":{"finalConcentration":{"expression":"initialConcentration*exp(-decayRatePerDay*timeDays)","unit":"CFU, cells, or copies/volume"}},"assumptions":["Constant first-order decay rate."],"notes":[],"version":"0.20.0"},{"id":"mb.log_reduction","category":"Environmental & food microbiology","title":"Decimal log reduction","equation":"Log reduction = log\u2081\u2080(N_0/N_t)","inputs":[{"key":"initialPopulation","label":"Initial population","unit":"CFU","default":1000000},{"key":"finalPopulation","label":"Final population","unit":"CFU","default":1000}],"outputs":{"logReduction":{"expression":"log10(initialPopulation/finalPopulation)","unit":"log10"}},"assumptions":["Initial and final counts use the same enumeration basis."],"notes":[],"version":"0.20.0"},{"id":"mb.removal_efficiency","category":"Environmental & food microbiology","title":"Microbial removal efficiency","equation":"Removal = (C_in \u2212 C_out)/C_in","inputs":[{"key":"influentConcentration","label":"Influent concentration","unit":"CFU or copies/volume","default":1000000},{"key":"effluentConcentration","label":"Effluent concentration","unit":"CFU or copies/volume","default":25000}],"outputs":{"removalFraction":{"expression":"(influentConcentration-effluentConcentration)/influentConcentration","unit":"1"}},"assumptions":["Influent and effluent measurements use the same analytical method."],"notes":[],"version":"0.20.0"},{"id":"mb.surface_loading_rate","category":"Environmental & food microbiology","title":"Microbial surface loading rate","equation":"Loading = concentration \u00d7 flow/surface area","inputs":[{"key":"concentrationPerL","label":"Microbial concentration","unit":"CFU/L","default":100000},{"key":"flowRateLPerDay","label":"Volumetric flow","unit":"L/day","default":5000},{"key":"surfaceAreaM2","label":"Receiving surface area","unit":"m^2","default":250}],"outputs":{"surfaceLoadingCfuM2Day":{"expression":"concentrationPerL*flowRateLPerDay/surfaceAreaM2","unit":"CFU/(m^2*day)"}},"assumptions":["Uniform loading over the stated surface area."],"notes":[],"version":"0.20.0"},{"id":"mb.biofilm_surface_density","category":"Environmental & food microbiology","title":"Biofilm biomass surface density","equation":"Surface density = dry biomass/surface area","inputs":[{"key":"dryBiomassMg","label":"Dry biofilm biomass","unit":"mg","default":420},{"key":"surfaceAreaCm2","label":"Colonized surface area","unit":"cm^2","default":120}],"outputs":{"biofilmSurfaceDensityMgCm2":{"expression":"dryBiomassMg/surfaceAreaCm2","unit":"mg/cm^2"}},"assumptions":["Dry biomass and area describe the same sampled region."],"notes":[],"version":"0.20.0"},{"id":"mb.biochemical_oxygen_demand_rate","category":"Environmental & food microbiology","title":"Volumetric oxygen demand rate","equation":"Rate = oxygen consumed/(volume \u00d7 time)","inputs":[{"key":"oxygenConsumedMg","label":"Oxygen consumed","unit":"mg","default":240},{"key":"sampleVolumeL","label":"Sample volume","unit":"L","default":2},{"key":"incubationTimeHours","label":"Incubation time","unit":"h","default":6}],"outputs":{"oxygenDemandMgLHour":{"expression":"oxygenConsumedMg/(sampleVolumeL*incubationTimeHours)","unit":"mg/(L*h)"}},"assumptions":["Oxygen loss is attributed to the measured biological process."],"notes":[],"version":"0.20.0"},{"id":"mb.temperature_adjusted_rate","category":"Environmental & food microbiology","title":"Q10 temperature-adjusted microbial rate","equation":"k_T = k_ref Q10^((T\u2212T_ref)/10)","inputs":[{"key":"referenceRate","label":"Reference process rate","unit":"rate units","default":1},{"key":"q10Factor","label":"Q10 factor","unit":"1","default":2},{"key":"temperatureC","label":"Operating temperature","unit":"degC","default":30},{"key":"referenceTemperatureC","label":"Reference temperature","unit":"degC","default":20}],"outputs":{"adjustedRate":{"expression":"referenceRate*q10Factor**((temperatureC-referenceTemperatureC)/10)","unit":"rate units"}},"assumptions":["Q10 approximation is valid over the selected temperature range."],"notes":[],"version":"0.20.0"},{"id":"mb.relative_source_contribution","category":"Environmental & food microbiology","title":"Relative microbial source contribution","equation":"Contribution = source marker copies/total marker copies","inputs":[{"key":"sourceMarkerCopies","label":"Source-associated marker copies","unit":"copies","default":240000},{"key":"totalMarkerCopies","label":"Total marker copies","unit":"copies","default":1000000}],"outputs":{"sourceContributionFraction":{"expression":"sourceMarkerCopies/totalMarkerCopies","unit":"1"}},"assumptions":["Marker recovery and amplification efficiency are comparable."],"notes":[],"version":"0.20.0"},{"id":"mb.mic_fold_change","category":"Antimicrobial & disinfection screening","title":"MIC fold change","equation":"Fold change = MIC_test/MIC_reference","inputs":[{"key":"testMicMgL","label":"Test MIC","unit":"mg/L","default":8},{"key":"referenceMicMgL","label":"Reference MIC","unit":"mg/L","default":2}],"outputs":{"micFoldChange":{"expression":"testMicMgL/referenceMicMgL","unit":"1"}},"assumptions":["MIC values use the same organism, medium, endpoint, and protocol."],"notes":[],"version":"0.20.0"},{"id":"mb.fic_index","category":"Antimicrobial & disinfection screening","title":"Fractional inhibitory concentration index","equation":"FICI = MIC_A,comb/MIC_A + MIC_B,comb/MIC_B","inputs":[{"key":"micACombination","label":"MIC of agent A in combination","unit":"mg/L","default":1},{"key":"micAAlone","label":"MIC of agent A alone","unit":"mg/L","default":4},{"key":"micBCombination","label":"MIC of agent B in combination","unit":"mg/L","default":2},{"key":"micBAlone","label":"MIC of agent B alone","unit":"mg/L","default":8}],"outputs":{"fractionalInhibitoryConcentrationIndex":{"expression":"micACombination/micAAlone+micBCombination/micBAlone","unit":"1"}},"assumptions":["Screening interpretation depends on the chosen protocol and threshold convention."],"notes":[],"version":"0.20.0"},{"id":"mb.time_kill_log_change","category":"Antimicrobial & disinfection screening","title":"Time-kill log change","equation":"\u0394log\u2081\u2080 = log\u2081\u2080(N_t) \u2212 log\u2081\u2080(N_0)","inputs":[{"key":"initialPopulation","label":"Initial viable count","unit":"CFU/mL","default":1000000},{"key":"finalPopulation","label":"Final viable count","unit":"CFU/mL","default":1000}],"outputs":{"log10Change":{"expression":"log10(finalPopulation)-log10(initialPopulation)","unit":"log10"}},"assumptions":["Counts use the same plating and detection basis."],"notes":[],"version":"0.20.0"},{"id":"mb.decimal_reduction_time","category":"Antimicrobial & disinfection screening","title":"Decimal reduction time","equation":"D = t/log\u2081\u2080(N_0/N_t)","inputs":[{"key":"exposureTimeMinutes","label":"Exposure time","unit":"min","default":12},{"key":"initialPopulation","label":"Initial viable population","unit":"CFU","default":1000000},{"key":"finalPopulation","label":"Final viable population","unit":"CFU","default":1000}],"outputs":{"decimalReductionTimeMinutes":{"expression":"exposureTimeMinutes/log10(initialPopulation/finalPopulation)","unit":"min/log10 reduction"}},"assumptions":["Log-linear survivor curve over the interval."],"notes":[],"version":"0.20.0"},{"id":"mb.z_value","category":"Antimicrobial & disinfection screening","title":"Thermal resistance z-value","equation":"z = (T\u2082\u2212T\u2081)/log\u2081\u2080(D\u2081/D\u2082)","inputs":[{"key":"temperature1C","label":"Temperature 1","unit":"degC","default":60},{"key":"temperature2C","label":"Temperature 2","unit":"degC","default":70},{"key":"dValue1Min","label":"D-value at temperature 1","unit":"min","default":10},{"key":"dValue2Min","label":"D-value at temperature 2","unit":"min","default":1}],"outputs":{"zValueC":{"expression":"(temperature2C-temperature1C)/log10(dValue1Min/dValue2Min)","unit":"degC"}},"assumptions":["Log-linear relationship between D-value and temperature over the interval."],"notes":[],"version":"0.20.0"},{"id":"mb.ct_value","category":"Antimicrobial & disinfection screening","title":"Disinfectant concentration-time value","equation":"CT = concentration \u00d7 contact time","inputs":[{"key":"disinfectantConcentrationMgL","label":"Disinfectant concentration","unit":"mg/L","default":2},{"key":"contactTimeMinutes","label":"Contact time","unit":"min","default":30}],"outputs":{"ctMgMinL":{"expression":"disinfectantConcentrationMgL*contactTimeMinutes","unit":"mg*min/L"}},"assumptions":["Constant concentration during the stated contact time."],"notes":[],"version":"0.20.0"},{"id":"mb.disinfectant_decay","category":"Antimicrobial & disinfection screening","title":"First-order disinfectant decay","equation":"C_t = C_0 e^(\u2212kt)","inputs":[{"key":"initialConcentrationMgL","label":"Initial disinfectant concentration","unit":"mg/L","default":2},{"key":"decayRatePerHour","label":"Decay rate","unit":"1/h","default":0.25},{"key":"timeHours","label":"Elapsed time","unit":"h","default":2}],"outputs":{"finalConcentrationMgL":{"expression":"initialConcentrationMgL*exp(-decayRatePerHour*timeHours)","unit":"mg/L"}},"assumptions":["Single first-order decay constant."],"notes":[],"version":"0.20.0"},{"id":"mb.inhibition_zone_normalized","category":"Antimicrobial & disinfection screening","title":"Normalized inhibition-zone ratio","equation":"Ratio = test zone/reference zone","inputs":[{"key":"testZoneDiameterMm","label":"Test inhibition-zone diameter","unit":"mm","default":24},{"key":"referenceZoneDiameterMm","label":"Reference zone diameter","unit":"mm","default":20}],"outputs":{"normalizedZoneRatio":{"expression":"testZoneDiameterMm/referenceZoneDiameterMm","unit":"1"}},"assumptions":["Zone diameters use the same assay conditions and reading convention."],"notes":[],"version":"0.20.0"},{"id":"mb.relative_abundance","category":"Microbial ecology & laboratory quality control","title":"Taxon relative abundance","equation":"Relative abundance = taxon reads/total reads","inputs":[{"key":"taxonReadCount","label":"Taxon reads","unit":"reads","default":24000},{"key":"totalReadCount","label":"Total quality-filtered reads","unit":"reads","default":120000}],"outputs":{"relativeAbundanceFraction":{"expression":"taxonReadCount/totalReadCount","unit":"1"}},"assumptions":["Read counts have passed the same filtering and assignment process."],"notes":[],"version":"0.20.0"},{"id":"mb.shannon_diversity","category":"Microbial ecology & laboratory quality control","title":"Four-taxon Shannon diversity","equation":"H' = \u2212\u03a3p_i ln p_i","inputs":[{"key":"proportion1","label":"Taxon proportion 1","unit":"1","default":0.4},{"key":"proportion2","label":"Taxon proportion 2","unit":"1","default":0.3},{"key":"proportion3","label":"Taxon proportion 3","unit":"1","default":0.2},{"key":"proportion4","label":"Taxon proportion 4","unit":"1","default":0.1}],"outputs":{"shannonDiversity":{"expression":"-(proportion1*log(proportion1)+proportion2*log(proportion2)+proportion3*log(proportion3)+proportion4*log(proportion4))","unit":"nats"}},"assumptions":["Proportions are positive and sum to one."],"notes":[],"version":"0.20.0"},{"id":"mb.simpson_diversity","category":"Microbial ecology & laboratory quality control","title":"Four-taxon Simpson diversity","equation":"1\u2212D = 1\u2212\u03a3p_i\u00b2","inputs":[{"key":"proportion1","label":"Taxon proportion 1","unit":"1","default":0.4},{"key":"proportion2","label":"Taxon proportion 2","unit":"1","default":0.3},{"key":"proportion3","label":"Taxon proportion 3","unit":"1","default":0.2},{"key":"proportion4","label":"Taxon proportion 4","unit":"1","default":0.1}],"outputs":{"simpsonDiversity":{"expression":"1-(proportion1**2+proportion2**2+proportion3**2+proportion4**2)","unit":"0-1"}},"assumptions":["Proportions sum to one."],"notes":[],"version":"0.20.0"},{"id":"mb.bray_curtis_dissimilarity","category":"Microbial ecology & laboratory quality control","title":"Two-taxon Bray\u2013Curtis dissimilarity","equation":"BC = \u03a3|x_i\u2212y_i|/\u03a3(x_i+y_i)","inputs":[{"key":"sampleA1","label":"Sample A taxon 1 abundance","unit":"count","default":40},{"key":"sampleA2","label":"Sample A taxon 2 abundance","unit":"count","default":60},{"key":"sampleB1","label":"Sample B taxon 1 abundance","unit":"count","default":70},{"key":"sampleB2","label":"Sample B taxon 2 abundance","unit":"count","default":30}],"outputs":{"brayCurtisDissimilarity":{"expression":"(abs(sampleA1-sampleB1)+abs(sampleA2-sampleB2))/(sampleA1+sampleB1+sampleA2+sampleB2)","unit":"0-1"}},"assumptions":["Nonnegative comparable abundance counts."],"notes":[],"version":"0.20.0"},{"id":"mb.qpcr_efficiency","category":"Microbial ecology & laboratory quality control","title":"qPCR amplification efficiency","equation":"Efficiency = 10^(\u22121/slope) \u2212 1","inputs":[{"key":"standardCurveSlope","label":"Standard-curve slope","unit":"Ct/log10 concentration","default":-3.32}],"outputs":{"qpcrEfficiencyFraction":{"expression":"10**(-1/standardCurveSlope)-1","unit":"1"}},"assumptions":["Linear standard curve over the tested range."],"notes":[],"version":"0.20.0"},{"id":"mb.dna_concentration_a260","category":"Microbial ecology & laboratory quality control","title":"Nucleic-acid concentration from A260","equation":"Concentration = A260 \u00d7 factor \u00d7 dilution","inputs":[{"key":"absorbanceA260","label":"Absorbance at 260 nm","unit":"AU","default":0.24},{"key":"conversionFactorUgMlPerAu","label":"Conversion factor","unit":"ug/mL per AU","default":50},{"key":"dilutionFactor","label":"Reciprocal dilution factor","unit":"1","default":10}],"outputs":{"dnaConcentrationUgMl":{"expression":"absorbanceA260*conversionFactorUgMlPerAu*dilutionFactor","unit":"ug/mL"}},"assumptions":["Appropriate conversion factor and path-length correction."],"notes":[],"version":"0.20.0"},{"id":"mb.replicate_coefficient_variation","category":"Microbial ecology & laboratory quality control","title":"Replicate coefficient of variation","equation":"CV = standard deviation/mean","inputs":[{"key":"replicateMean","label":"Replicate mean","unit":"signal or concentration","default":100},{"key":"replicateStandardDeviation","label":"Replicate standard deviation","unit":"same units","default":6}],"outputs":{"coefficientOfVariation":{"expression":"replicateStandardDeviation/replicateMean","unit":"1"}},"assumptions":["Mean and standard deviation are calculated from the same replicate set."],"notes":[],"version":"0.20.0"},{"id":"mb.contamination_rate","category":"Microbial ecology & laboratory quality control","title":"Laboratory contamination rate","equation":"Rate = contaminated controls/total controls","inputs":[{"key":"contaminatedControlCount","label":"Contaminated negative controls","unit":"controls","default":3},{"key":"totalControlCount","label":"Total negative controls","unit":"controls","default":120}],"outputs":{"contaminationFraction":{"expression":"contaminatedControlCount/totalControlCount","unit":"1"}},"assumptions":["Controls use a consistent contamination decision rule."],"notes":[],"version":"0.20.0"}]};
const METHODS = new Map(CATALOG.methods.map((item) => [item.id, item]));
const CATEGORIES = [...new Set(CATALOG.methods.map((item) => item.category))];
const BENCHMARKS = [["mb.exponential_growth",{"initialPopulation":100,"specificGrowthRatePerHour":0.6931471805599453,"timeHours":1},"finalPopulation",200],["mb.specific_growth_rate",{"initialPopulation":100,"finalPopulation":200,"timeHours":1},"specificGrowthRatePerHour",0.6931471805599453],["mb.generation_time",{"specificGrowthRatePerHour":0.6931471805599453},"generationTimeHours",1],["mb.number_of_generations",{"initialPopulation":100,"finalPopulation":800},"generationCount",3],["mb.logistic_growth",{"initialPopulation":50,"carryingCapacity":100,"intrinsicGrowthRatePerHour":0,"timeHours":10},"finalPopulation",50],["mb.first_order_death",{"initialPopulation":1000,"inactivationRatePerHour":2.302585092994046,"timeHours":1},"survivingPopulation",100],["mb.population_fold_change",{"initialPopulation":100,"finalPopulation":500},"populationFoldChange",5],["mb.carrying_capacity_utilization",{"observedPopulation":80,"carryingCapacity":100},"carryingCapacityFraction",0.8],["mb.chemostat_dilution_rate",{"flowRateLPerHour":2,"reactorVolumeL":10},"dilutionRatePerHour",0.2],["mb.chemostat_residence_time",{"reactorVolumeL":10,"flowRateLPerHour":2},"residenceTimeHours",5],["mb.monod_growth_rate",{"maximumGrowthRatePerHour":1,"substrateConcentrationMgL":10,"halfSaturationMgL":10},"specificGrowthRatePerHour",0.5],["mb.chemostat_steady_substrate",{"halfSaturationMgL":10,"dilutionRatePerHour":0.2,"maximumGrowthRatePerHour":1},"steadyStateSubstrateMgL",2.5],["mb.washout_margin",{"maximumGrowthRatePerHour":1,"dilutionRatePerHour":0.2},"washoutMarginPerHour",0.8],["mb.biomass_productivity",{"dilutionRatePerHour":0.2,"biomassConcentrationGL":5},"biomassProductivityGLH",1],["mb.biomass_yield_on_substrate",{"biomassProducedG":40,"substrateConsumedG":80},"biomassYieldGPerG",0.5],["mb.oxygen_uptake_rate",{"specificOxygenUptakeMgGHour":10,"biomassConcentrationGL":5},"oxygenUptakeRateMgLHour",50],["mb.cfu_per_ml",{"colonyCount":100,"platedVolumeMl":0.1,"sampleDilution":0.001},"cfuPerMl",1000000],["mb.pfu_per_ml",{"plaqueCount":50,"platedVolumeMl":0.1,"sampleDilution":0.001},"pfuPerMl",500000],["mb.serial_dilution_factor",{"dilutionStep1":0.1,"dilutionStep2":0.1,"dilutionStep3":0.1,"dilutionStep4":0.1},"cumulativeDilution",0.0001],["mb.hemocytometer_concentration",{"averageCellCount":100,"chamberFactorPerMl":10000,"dilutionFactor":2},"cellsPerMl",2000000],["mb.viable_fraction",{"viableCellCount":80,"totalCellCount":100},"viableFraction",0.8],["mb.od_calibrated_biomass",{"opticalDensity":1,"calibrationSlopeGLPerAu":0.5,"calibrationInterceptGL":0.1},"biomassConcentrationGL",0.6],["mb.assay_recovery",{"measuredAmount":80,"spikedAmount":100},"recoveryFraction",0.8],["mb.z_prime_factor",{"positiveMean":1,"negativeMean":0,"positiveSd":0.05,"negativeSd":0.05},"zPrimeFactor",0.7],["mb.first_order_environmental_decay",{"initialConcentration":1000,"decayRatePerDay":2.302585092994046,"timeDays":1},"finalConcentration",100],["mb.log_reduction",{"initialPopulation":1000,"finalPopulation":10},"logReduction",2],["mb.removal_efficiency",{"influentConcentration":100,"effluentConcentration":20},"removalFraction",0.8],["mb.surface_loading_rate",{"concentrationPerL":100,"flowRateLPerDay":10,"surfaceAreaM2":20},"surfaceLoadingCfuM2Day",50],["mb.biofilm_surface_density",{"dryBiomassMg":100,"surfaceAreaCm2":20},"biofilmSurfaceDensityMgCm2",5],["mb.biochemical_oxygen_demand_rate",{"oxygenConsumedMg":100,"sampleVolumeL":2,"incubationTimeHours":5},"oxygenDemandMgLHour",10],["mb.temperature_adjusted_rate",{"referenceRate":1,"q10Factor":2,"temperatureC":30,"referenceTemperatureC":20},"adjustedRate",2],["mb.relative_source_contribution",{"sourceMarkerCopies":20,"totalMarkerCopies":100},"sourceContributionFraction",0.2],["mb.mic_fold_change",{"testMicMgL":8,"referenceMicMgL":2},"micFoldChange",4],["mb.fic_index",{"micACombination":1,"micAAlone":4,"micBCombination":2,"micBAlone":8},"fractionalInhibitoryConcentrationIndex",0.5],["mb.time_kill_log_change",{"initialPopulation":1000,"finalPopulation":10},"log10Change",-2],["mb.decimal_reduction_time",{"exposureTimeMinutes":6,"initialPopulation":1000,"finalPopulation":1},"decimalReductionTimeMinutes",2],["mb.z_value",{"temperature1C":60,"temperature2C":70,"dValue1Min":10,"dValue2Min":1},"zValueC",10],["mb.ct_value",{"disinfectantConcentrationMgL":2,"contactTimeMinutes":30},"ctMgMinL",60],["mb.disinfectant_decay",{"initialConcentrationMgL":10,"decayRatePerHour":0.6931471805599453,"timeHours":1},"finalConcentrationMgL",5],["mb.inhibition_zone_normalized",{"testZoneDiameterMm":20,"referenceZoneDiameterMm":10},"normalizedZoneRatio",2],["mb.relative_abundance",{"taxonReadCount":20,"totalReadCount":100},"relativeAbundanceFraction",0.2],["mb.shannon_diversity",{"proportion1":0.25,"proportion2":0.25,"proportion3":0.25,"proportion4":0.25},"shannonDiversity",1.3862943611198906],["mb.simpson_diversity",{"proportion1":0.25,"proportion2":0.25,"proportion3":0.25,"proportion4":0.25},"simpsonDiversity",0.75],["mb.bray_curtis_dissimilarity",{"sampleA1":50,"sampleA2":50,"sampleB1":100,"sampleB2":0},"brayCurtisDissimilarity",0.5],["mb.qpcr_efficiency",{"standardCurveSlope":-3.321928094887362},"qpcrEfficiencyFraction",1],["mb.dna_concentration_a260",{"absorbanceA260":0.2,"conversionFactorUgMlPerAu":50,"dilutionFactor":10},"dnaConcentrationUgMl",100],["mb.replicate_coefficient_variation",{"replicateMean":100,"replicateStandardDeviation":5},"coefficientOfVariation",0.05],["mb.contamination_rate",{"contaminatedControlCount":2,"totalControlCount":100},"contaminationFraction",0.02]];

const SAFE = {
  pi: Math.PI,
  g: 9.80665,
  sqrt: Math.sqrt,
  log: Math.log,
  log10: Math.log10,
  exp: Math.exp,
  abs: Math.abs,
  min: Math.min,
  max: Math.max,
  pow: Math.pow,
  sin: Math.sin,
  cos: Math.cos,
  tan: Math.tan,
  asin: Math.asin,
  acos: Math.acos,
  atan: Math.atan,
};

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[character]));
}

function finiteNumber(value, label) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    throw new Error(`${label} must be a finite number.`);
  }

  return number;
}

function evaluate(expression, variables) {
  if (!/^[0-9A-Za-z_+\-*/().,<>=!? :]+$/.test(expression)) {
    throw new Error('The method expression contains unsupported characters.');
  }

  const names = [...Object.keys(SAFE), ...Object.keys(variables)];
  const values = [...Object.values(SAFE), ...Object.values(variables)];

  return Function(
    ...names,
    `"use strict"; return (${expression});`
  )(...values);
}

function fingerprint(text) {
  let hash = 2166136261;

  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }

  return (hash >>> 0).toString(16).padStart(8, '0');
}

function warningsFor(methodId, outputs) {
  const warnings = [];

  if (
    methodId === 'mb.chemostat_steady_substrate'
    && outputs.steadyStateSubstrateMgL < 0
  ) {
    warnings.push(
      'The steady-state substrate result is negative; verify that dilution rate remains below maximum growth rate.'
    );
  }

  if (
    methodId === 'mb.washout_margin'
    && outputs.washoutMarginPerHour <= 0
  ) {
    warnings.push(
      'The dilution rate meets or exceeds maximum growth rate, indicating washout risk.'
    );
  }

  if (
    methodId === 'mb.viable_fraction'
    && (
      outputs.viableFraction < 0
      || outputs.viableFraction > 1
    )
  ) {
    warnings.push(
      'The viable fraction lies outside 0 to 1; review counts and background correction.'
    );
  }

  if (
    methodId === 'mb.assay_recovery'
    && (
      outputs.recoveryFraction < 0.7
      || outputs.recoveryFraction > 1.3
    )
  ) {
    warnings.push(
      'Assay recovery is outside the 70% to 130% screening interval.'
    );
  }

  if (
    methodId === 'mb.z_prime_factor'
    && outputs.zPrimeFactor < 0.5
  ) {
    warnings.push(
      'The assay Z-prime factor is below 0.5 and may not support robust screening.'
    );
  }

  if (
    methodId === 'mb.replicate_coefficient_variation'
    && outputs.coefficientOfVariation > 0.2
  ) {
    warnings.push(
      'Replicate coefficient of variation exceeds 20%.'
    );
  }

  if (
    methodId === 'mb.contamination_rate'
    && outputs.contaminationFraction > 0.05
  ) {
    warnings.push(
      'Negative-control contamination exceeds 5% in the stated record.'
    );
  }

  return warnings;
}

function run(methodId, rawInputs) {
  const method = METHODS.get(methodId);

  if (!method) {
    throw new Error(`Unknown aerospace-flight method: ${methodId}`);
  }

  const inputs = {};

  for (const field of method.inputs) {
    inputs[field.key] = finiteNumber(rawInputs[field.key], field.label);
  }

  const outputs = {};
  const outputUnits = {};
  const expressions = {};

  for (const [key, specification] of Object.entries(method.outputs)) {
    const value = Number(evaluate(specification.expression, inputs));

    if (!Number.isFinite(value)) {
      throw new Error(`${key} did not produce a finite result.`);
    }

    outputs[key] = value;
    outputUnits[key] = specification.unit;
    expressions[key] = specification.expression;
  }

  const warnings = warningsFor(methodId, outputs);

  const record = {
    schema:
      'sc-lab-microbiology-laboratory-analysis/1.0',
    version: VERSION,
    methodId: method.id,
    methodVersion: method.version || VERSION,
    category: method.category,
    title: method.title,
    equation: method.equation,
    expressions,
    inputs,
    inputUnits: Object.fromEntries(
      method.inputs.map((field) => [field.key, field.unit])
    ),
    outputs,
    outputUnits,
    assumptions: method.assumptions || [],
    notes: method.notes || [],
    warnings,
    validation: {
      status: warnings.length ? 'review' : 'screened',
      benchmarkSuite:
        'sc-lab-microbiology-laboratory-benchmarks/1.0',
    },
    audit: {
      createdAt: new Date().toISOString(),
      engine:
        'sc-lab-microbiology-laboratory-js',
      release: VERSION,
    },
  };

  record.audit.fingerprint = fingerprint(JSON.stringify(record));
  return record;
}

function runBenchmarks() {
  return BENCHMARKS.map(([methodId, inputs, key, expected]) => {
    try {
      const actual = run(methodId, inputs).outputs[key];
      const tolerance = 1e-8 * Math.max(1, Math.abs(expected));

      return {
        methodId,
        output: key,
        expected,
        actual,
        passed: Math.abs(actual - expected) <= tolerance,
      };
    } catch (error) {
      return {
        methodId,
        output: key,
        expected,
        actual: null,
        passed: false,
        error: error.message,
      };
    }
  });
}

function formulaMarkup(method) {
  return Object.entries(method.outputs).map(([key, specification]) => `
    <div class="sc-mb-formula-expression">
      <span>${escapeHtml(key)}</span>
      <code>${escapeHtml(specification.expression)}</code>
      <small>${escapeHtml(specification.unit || '')}</small>
    </div>
  `).join('');
}

function render(root = document) {
  const mounts = root.querySelectorAll(
    '[data-microbiology-laboratory-root]'
  );

  mounts.forEach((mount) => {
    if (mount.dataset.scMicrobiologyRendered === VERSION) {
      return;
    }

    mount.dataset.scMicrobiologyRendered = VERSION;

    mount.innerHTML = `
      <div class="sc-mb-workbench">
        <div class="sc-mb-controls">
          <label>
            Workspace
            <select data-mb-category>
              ${CATEGORIES.map(
                (category) => `<option>${escapeHtml(category)}</option>`
              ).join('')}
            </select>
          </label>

          <label>
            Method
            <select data-mb-method></select>
          </label>
        </div>

        <article class="sc-mb-card">
          <p class="sc-mb-kicker" data-mb-category-label></p>
          <h4 data-mb-title></h4>

          <div class="sc-mb-visible-formula">
            <span>Microbiology or laboratory formula</span>
            <code data-mb-equation></code>
          </div>

          <p data-mb-assumptions></p>

          <details class="sc-mb-expression-source" open>
            <summary>Executable output expressions</summary>
            <div data-mb-expressions></div>
          </details>

          <div class="sc-mb-inputs" data-mb-inputs></div>

          <div class="sc-mb-actions">
            <button type="button" class="button button-primary" data-mb-run>
              Run analysis
            </button>
            <button type="button" class="button" data-mb-save>
              Save to project
            </button>
            <button type="button" class="button" data-mb-note>
              Add to notebook
            </button>
            <button type="button" class="button" data-mb-visualize>
              Visualize
            </button>
          </div>

          <div class="sc-mb-status" data-mb-status role="status" aria-live="polite">
            Select a microbiology laboratory method.
          </div>

          <div class="sc-mb-results" data-mb-results></div>

          <details>
            <summary>Analysis contract</summary>
            <pre data-mb-json>{}</pre>
          </details>
        </article>

        <section class="sc-mb-validation">
          <div>
            <p class="sc-mb-kicker">VALIDATION</p>
            <h4>Microbiology laboratory benchmark suite</h4>
            <p>
              Deterministic cases cover microbial growth, continuous culture, enumeration, environmental microbiology, antimicrobial screening, microbial ecology, and laboratory quality control.
            </p>
          </div>

          <button type="button" class="button" data-mb-benchmarks>
            Run ${BENCHMARKS.length} benchmarks
          </button>

          <div data-mb-benchmark-results></div>
        </section>
      </div>
    `;
  });
}

function init(root = document, projects = Lab.Projects) {
  render(root);

  const mounts = root.querySelectorAll(
    '[data-microbiology-laboratory-root]'
  );

  mounts.forEach((mount) => {
    if (mount.dataset.scMicrobiologyInitialized === VERSION) {
      return;
    }

    mount.dataset.scMicrobiologyInitialized = VERSION;

    const categorySelect = mount.querySelector('[data-mb-category]');
    const methodSelect = mount.querySelector('[data-mb-method]');
    const inputContainer = mount.querySelector('[data-mb-inputs]');
    const status = mount.querySelector('[data-mb-status]');
    const resultContainer = mount.querySelector('[data-mb-results]');
    const jsonTarget = mount.querySelector('[data-mb-json]');
    let current = null;

    function renderMethod() {
      const selected = METHODS.get(methodSelect.value);

      if (!selected) {
        return;
      }

      mount.querySelector('[data-mb-category-label]').textContent =
        selected.category.toUpperCase();
      mount.querySelector('[data-mb-title]').textContent = selected.title;
      mount.querySelector('[data-mb-equation]').textContent =
        selected.equation || 'Formula not documented.';
      mount.querySelector('[data-mb-assumptions]').textContent =
        (selected.assumptions || []).join(' ');
      mount.querySelector('[data-mb-expressions]').innerHTML =
        formulaMarkup(selected);

      inputContainer.innerHTML = selected.inputs.map((input) => `
        <label>
          ${escapeHtml(input.label)}
          <span>${escapeHtml(input.unit)}</span>
          <input
            type="number"
            step="any"
            value="${escapeHtml(input.default)}"
            data-mb-field="${escapeHtml(input.key)}"
          >
        </label>
      `).join('');

      current = null;
      resultContainer.innerHTML = '';
      jsonTarget.textContent = '{}';
      status.textContent = 'Formula and inputs ready.';
    }

    function renderMethodOptions() {
      methodSelect.innerHTML = CATALOG.methods
        .filter((item) => item.category === categorySelect.value)
        .map((item) => `
          <option value="${escapeHtml(item.id)}">
            ${escapeHtml(item.title)}
          </option>
        `)
        .join('');

      renderMethod();
    }

    function execute() {
      try {
        const raw = {};

        inputContainer.querySelectorAll('[data-mb-field]').forEach((input) => {
          raw[input.dataset.mbField] = input.value;
        });

        current = run(methodSelect.value, raw);

        resultContainer.innerHTML = Object.entries(current.outputs)
          .map(([key, value]) => `
            <div>
              <span>${escapeHtml(key)}</span>
              <strong>${escapeHtml(Number(value).toPrecision(8))}</strong>
              <small>${escapeHtml(current.outputUnits[key] || '')}</small>
            </div>
          `)
          .join('');

        jsonTarget.textContent = JSON.stringify(current, null, 2);

        status.textContent = current.warnings.length
          ? `Completed with ${current.warnings.length} review warning(s).`
          : 'Analysis completed and screened.';

        document.dispatchEvent(
          new CustomEvent('sc-lab:analysis', { detail: current })
        );

        return current;
      } catch (error) {
        current = null;
        status.textContent = `Analysis error: ${error.message}`;
        return null;
      }
    }

    categorySelect.addEventListener('change', renderMethodOptions);
    methodSelect.addEventListener('change', renderMethod);
    mount.querySelector('[data-mb-run]').addEventListener('click', execute);

    mount.querySelector('[data-mb-save]').addEventListener('click', () => {
      const record = current || execute();

      if (!record) {
        return;
      }

      if (projects && typeof projects.add === 'function') {
        projects.add(
          'microbiologyAnalyses',
          record,
          `${record.title} saved`
        );

        projects.add(
          'microbiologyRecords',
          {
            schema: 'sc-lab-microbiology-record/1.0',
            version: VERSION,
            methodId: record.methodId,
            category: record.category,
            title: record.title,
            recordedAt: new Date().toISOString(),
            fingerprint: record.audit.fingerprint,
          },
          `Aerospace flight-systems record added: ${record.title}`
        );

        status.textContent = 'Saved to the active project.';
      } else {
        status.textContent =
          'Analysis is ready, but the project storage module is unavailable.';
      }
    });

    mount.querySelector('[data-mb-note]').addEventListener('click', () => {
      const record = current || execute();

      if (
        record
        && projects
        && typeof projects.add === 'function'
      ) {
        projects.add(
          'notes',
          {
            title: `${record.title} analysis`,
            body: JSON.stringify(record, null, 2),
            tags: [
              'microbiology',
              'laboratory',
              record.category,
              record.methodId,
            ],
          },
          `Notebook entry added: ${record.title}`
        );

        status.textContent = 'Notebook entry added.';
      }
    });

    mount.querySelector('[data-mb-visualize]').addEventListener('click', () => {
      const record = current || execute();

      if (record) {
        document.dispatchEvent(
          new CustomEvent('sc-lab:analysis', { detail: record })
        );
        status.textContent = 'Analysis sent to the visualization layer.';
      }
    });

    mount.querySelector('[data-mb-benchmarks]').addEventListener(
      'click',
      () => {
        const rows = runBenchmarks();
        const passed = rows.filter((row) => row.passed).length;

        mount.querySelector('[data-mb-benchmark-results]').innerHTML = `
          <p><strong>${passed}/${rows.length}</strong> benchmarks passed.</p>
          <div class="sc-mb-benchmark-grid">
            ${rows.map((row) => `
              <div class="${row.passed ? 'is-pass' : 'is-fail'}">
                <span>${escapeHtml(row.methodId)}</span>
                <strong>${row.passed ? 'PASS' : 'FAIL'}</strong>
              </div>
            `).join('')}
          </div>
        `;

        if (projects && typeof projects.add === 'function') {
          projects.add(
            'microbiologyValidationRecords',
            {
              schema:
                'sc-lab-microbiology-laboratory-benchmarks/1.0',
              version: VERSION,
              createdAt: new Date().toISOString(),
              passed,
              total: rows.length,
              results: rows,
            },
            `Development-systems validation: ${passed}/${rows.length}`
          );
        }
      }
    );

    renderMethodOptions();
  });
}

function autoInit() {
  init(document, Lab.Projects);
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit, { once: true });
  } else {
    autoInit();
  }

  document.addEventListener('sc-lab:module-opened', autoInit);
}

Lab.MicrobiologyLaboratory = {
  VERSION,
  catalog: CATALOG,
  definitions: CATALOG.methods,
  categories: CATEGORIES,
  benchmarks: BENCHMARKS,
  run,
  runBenchmarks,
  render,
  init,
};

})(typeof window !== 'undefined' ? window : globalThis);
