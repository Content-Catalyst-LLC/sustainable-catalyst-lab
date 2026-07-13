(function (global) {
'use strict';

const Lab = global.SCLab = global.SCLab || {};
const VERSION = "0.15.0";
const CATALOG = {"schema":"sc-lab-sustainable-cities-resilience-catalog/1.0","version":"0.15.0","methodCount":48,"categories":["Urban metabolism & resources","Climate mitigation & decarbonization","Climate adaptation & hazards","Infrastructure resilience & continuity","Equity & social resilience","Integrated scenarios & governance"],"methods":[{"id":"sc.energy_per_capita","category":"Urban metabolism & resources","title":"Community energy use per capita","equation":"Energy per capita = annual final energy / population","inputs":[{"key":"annualEnergyMWh","label":"Annual final energy","unit":"MWh/yr","default":2400000},{"key":"population","label":"Population","unit":"persons","default":300000}],"outputs":{"energyMWhPerCapitaYear":{"expression":"annualEnergyMWh/population","unit":"MWh/(person*yr)"}},"assumptions":["Energy inventory and population use the same geographic boundary."],"notes":[],"version":"0.15.0"},{"id":"sc.water_per_capita","category":"Urban metabolism & resources","title":"Community water use per capita","equation":"Water per capita = annual water / population","inputs":[{"key":"annualWaterM3","label":"Annual water demand","unit":"m^3/yr","default":42000000},{"key":"population","label":"Population","unit":"persons","default":300000}],"outputs":{"waterM3PerCapitaYear":{"expression":"annualWaterM3/population","unit":"m^3/(person*yr)"},"waterLitersPerCapitaDay":{"expression":"annualWaterM3*1000/(population*365)","unit":"L/(person*day)"}},"assumptions":["Annual water demand and population use the same service boundary."],"notes":[],"version":"0.15.0"},{"id":"sc.waste_per_capita","category":"Urban metabolism & resources","title":"Municipal waste generation per capita","equation":"Waste per capita = annual waste / population","inputs":[{"key":"annualWasteTonnes","label":"Annual municipal waste","unit":"tonnes/yr","default":210000},{"key":"population","label":"Population","unit":"persons","default":300000}],"outputs":{"wasteKgPerCapitaDay":{"expression":"annualWasteTonnes*1000/(population*365)","unit":"kg/(person*day)"}},"assumptions":["Waste inventory and population use the same geographic boundary."],"notes":[],"version":"0.15.0"},{"id":"sc.material_circularity","category":"Urban metabolism & resources","title":"Material circularity rate","equation":"Circularity = secondary material input / total material input","inputs":[{"key":"secondaryMaterialTonnes","label":"Secondary material input","unit":"tonnes/yr","default":420000},{"key":"totalMaterialTonnes","label":"Total material input","unit":"tonnes/yr","default":1800000}],"outputs":{"circularityFraction":{"expression":"secondaryMaterialTonnes/totalMaterialTonnes","unit":"1"}},"assumptions":["Material flows use compatible lifecycle and geographic boundaries."],"notes":[],"version":"0.15.0"},{"id":"sc.resource_recovery","category":"Urban metabolism & resources","title":"Resource recovery rate","equation":"Recovery = recovered waste / generated waste","inputs":[{"key":"recoveredTonnes","label":"Recovered material","unit":"tonnes/yr","default":82000},{"key":"generatedTonnes","label":"Generated waste","unit":"tonnes/yr","default":210000}],"outputs":{"resourceRecoveryFraction":{"expression":"recoveredTonnes/generatedTonnes","unit":"1"}},"assumptions":["Recovered and generated material use the same waste-stream scope."],"notes":[],"version":"0.15.0"},{"id":"sc.food_demand","category":"Urban metabolism & resources","title":"Annual community food demand","equation":"Food demand = population \u00d7 unit food demand","inputs":[{"key":"population","label":"Population","unit":"persons","default":300000},{"key":"foodKgPerCapitaDay","label":"Food demand per capita","unit":"kg/(person*day)","default":1.8}],"outputs":{"annualFoodTonnes":{"expression":"population*foodKgPerCapitaDay*365/1000","unit":"tonnes/yr"}},"assumptions":["Unit food demand is a stated scenario assumption."],"notes":[],"version":"0.15.0"},{"id":"sc.water_energy_nexus","category":"Urban metabolism & resources","title":"Water-system electricity demand","equation":"Electricity = water volume \u00d7 energy intensity","inputs":[{"key":"annualWaterM3","label":"Annual water volume","unit":"m^3/yr","default":42000000},{"key":"energyIntensityKWhM3","label":"Water-system electricity intensity","unit":"kWh/m^3","default":0.75}],"outputs":{"waterSystemElectricityMWh":{"expression":"annualWaterM3*energyIntensityKWhM3/1000","unit":"MWh/yr"}},"assumptions":["Energy intensity includes the selected supply, treatment, and conveyance stages."],"notes":[],"version":"0.15.0"},{"id":"sc.urban_metabolism_intensity","category":"Urban metabolism & resources","title":"Composite urban metabolism intensity","equation":"Intensity = weighted normalized energy + water + waste","inputs":[{"key":"energyIndex","label":"Normalized energy index","unit":"0-100","default":62},{"key":"energyWeight","label":"Energy weight","unit":"1","default":0.4},{"key":"waterIndex","label":"Normalized water index","unit":"0-100","default":55},{"key":"waterWeight","label":"Water weight","unit":"1","default":0.3},{"key":"wasteIndex","label":"Normalized waste index","unit":"0-100","default":68},{"key":"wasteWeight","label":"Waste weight","unit":"1","default":0.3}],"outputs":{"metabolismIntensityScore":{"expression":"(energyIndex*energyWeight+waterIndex*waterWeight+wasteIndex*wasteWeight)/(energyWeight+waterWeight+wasteWeight)","unit":"0-100"}},"assumptions":["Component indices use a common normalized scale; lower or higher desirability must be declared separately."],"notes":[],"version":"0.15.0"},{"id":"sc.community_emissions","category":"Climate mitigation & decarbonization","title":"Community greenhouse-gas inventory","equation":"Emissions = electricity + fuel + transport + waste","inputs":[{"key":"electricityTonnes","label":"Electricity emissions","unit":"tCO2e/yr","default":850000},{"key":"fuelTonnes","label":"Stationary-fuel emissions","unit":"tCO2e/yr","default":620000},{"key":"transportTonnes","label":"Transport emissions","unit":"tCO2e/yr","default":710000},{"key":"wasteTonnes","label":"Waste emissions","unit":"tCO2e/yr","default":120000}],"outputs":{"totalEmissionsTonnes":{"expression":"electricityTonnes+fuelTonnes+transportTonnes+wasteTonnes","unit":"tCO2e/yr"}},"assumptions":["Sector inventories use compatible accounting methods and boundaries."],"notes":[],"version":"0.15.0"},{"id":"sc.emissions_per_capita","category":"Climate mitigation & decarbonization","title":"Community emissions per capita","equation":"Emissions per capita = annual emissions / population","inputs":[{"key":"annualEmissionsTonnes","label":"Annual community emissions","unit":"tCO2e/yr","default":2300000},{"key":"population","label":"Population","unit":"persons","default":300000}],"outputs":{"tonnesPerCapitaYear":{"expression":"annualEmissionsTonnes/population","unit":"tCO2e/(person*yr)"}},"assumptions":["Emissions and population use the same geographic boundary."],"notes":[],"version":"0.15.0"},{"id":"sc.reduction_trajectory","category":"Climate mitigation & decarbonization","title":"Constant annual emissions-reduction trajectory","equation":"Annual reduction = (baseline \u2212 target) / years","inputs":[{"key":"baselineTonnes","label":"Baseline annual emissions","unit":"tCO2e/yr","default":2300000},{"key":"targetTonnes","label":"Target annual emissions","unit":"tCO2e/yr","default":700000},{"key":"years","label":"Years to target","unit":"yr","default":12}],"outputs":{"annualReductionTonnes":{"expression":"(baselineTonnes-targetTonnes)/years","unit":"tCO2e/yr per year"},"annualReductionFractionOfBaseline":{"expression":"(baselineTonnes-targetTonnes)/(baselineTonnes*years)","unit":"1/yr"}},"assumptions":["Linear absolute reduction path without rebound or population adjustment."],"notes":[],"version":"0.15.0"},{"id":"sc.renewable_electricity_share","category":"Climate mitigation & decarbonization","title":"Renewable electricity share","equation":"Renewable share = renewable electricity / total electricity","inputs":[{"key":"renewableMWh","label":"Renewable electricity","unit":"MWh/yr","default":520000},{"key":"totalElectricityMWh","label":"Total electricity","unit":"MWh/yr","default":1300000}],"outputs":{"renewableShare":{"expression":"renewableMWh/totalElectricityMWh","unit":"1"}},"assumptions":["Renewable and total electricity use the same accounting period."],"notes":[],"version":"0.15.0"},{"id":"sc.electrification_savings","category":"Climate mitigation & decarbonization","title":"Fuel-to-electric electrification emissions savings","equation":"Savings = fuel energy \u00d7 fuel factor \u2212 electric energy \u00d7 grid factor","inputs":[{"key":"fuelEnergyMWh","label":"Displaced fuel energy","unit":"MWh/yr","default":500000},{"key":"fuelFactorKgKWh","label":"Fuel emissions factor","unit":"kgCO2e/kWh","default":0.2},{"key":"electricEnergyMWh","label":"Replacement electricity","unit":"MWh/yr","default":180000},{"key":"gridFactorKgKWh","label":"Grid emissions factor","unit":"kgCO2e/kWh","default":0.3}],"outputs":{"annualSavingsTonnes":{"expression":"(fuelEnergyMWh*1000*fuelFactorKgKWh-electricEnergyMWh*1000*gridFactorKgKWh)/1000","unit":"tCO2e/yr"}},"assumptions":["Energy quantities represent equivalent delivered services."],"notes":[],"version":"0.15.0"},{"id":"sc.modal_shift_savings","category":"Climate mitigation & decarbonization","title":"Transport modal-shift emissions savings","equation":"Savings = shifted trips \u00d7 distance \u00d7 factor difference","inputs":[{"key":"shiftedTripsPerDay","label":"Trips shifted per day","unit":"trips/day","default":24000},{"key":"averageDistanceKm","label":"Average trip distance","unit":"km","default":8},{"key":"carFactorKgPerPassengerKm","label":"Car emissions factor","unit":"kgCO2e/passenger-km","default":0.18},{"key":"newModeFactorKgPerPassengerKm","label":"New-mode emissions factor","unit":"kgCO2e/passenger-km","default":0.04},{"key":"annualDays","label":"Annual operating days","unit":"day/yr","default":300}],"outputs":{"annualSavingsTonnes":{"expression":"shiftedTripsPerDay*averageDistanceKm*(carFactorKgPerPassengerKm-newModeFactorKgPerPassengerKm)*annualDays/1000","unit":"tCO2e/yr"}},"assumptions":["Trips are genuinely shifted rather than newly induced; factors use compatible occupancy assumptions."],"notes":[],"version":"0.15.0"},{"id":"sc.retrofit_emissions_savings","category":"Climate mitigation & decarbonization","title":"Building-retrofit emissions savings","equation":"Savings = energy saved \u00d7 emissions factor","inputs":[{"key":"annualEnergySavedMWh","label":"Annual energy saved","unit":"MWh/yr","default":180000},{"key":"emissionsFactorKgKWh","label":"Avoided emissions factor","unit":"kgCO2e/kWh","default":0.32}],"outputs":{"annualSavingsTonnes":{"expression":"annualEnergySavedMWh*emissionsFactorKgKWh","unit":"tCO2e/yr"}},"assumptions":["Saved energy and emissions factor refer to the same energy carrier and marginal or average basis."],"notes":[],"version":"0.15.0"},{"id":"sc.carbon_budget_years","category":"Climate mitigation & decarbonization","title":"Carbon-budget exhaustion time","equation":"Years = remaining carbon budget / annual emissions","inputs":[{"key":"remainingBudgetTonnes","label":"Remaining carbon budget","unit":"tCO2e","default":12000000},{"key":"annualEmissionsTonnes","label":"Current annual emissions","unit":"tCO2e/yr","default":2300000}],"outputs":{"budgetYears":{"expression":"remainingBudgetTonnes/annualEmissionsTonnes","unit":"yr"}},"assumptions":["Annual emissions remain constant in this screening calculation."],"notes":[],"version":"0.15.0"},{"id":"sc.heat_exposure_rate","category":"Climate adaptation & hazards","title":"Population heat-exposure rate","equation":"Exposure = exposed population / total population","inputs":[{"key":"exposedPopulation","label":"Population above heat threshold","unit":"persons","default":82000},{"key":"totalPopulation","label":"Total population","unit":"persons","default":300000}],"outputs":{"heatExposureFraction":{"expression":"exposedPopulation/totalPopulation","unit":"1"}},"assumptions":["Exposure threshold and population data refer to the same event or scenario."],"notes":[],"version":"0.15.0"},{"id":"sc.cooling_degree_change","category":"Climate adaptation & hazards","title":"Cooling-degree-day increase","equation":"Increase = future CDD \u2212 baseline CDD","inputs":[{"key":"baselineCoolingDegreeDays","label":"Baseline cooling degree days","unit":"K*day","default":900},{"key":"futureCoolingDegreeDays","label":"Future cooling degree days","unit":"K*day","default":1250}],"outputs":{"increaseDegreeDays":{"expression":"futureCoolingDegreeDays-baselineCoolingDegreeDays","unit":"K*day"},"increaseFraction":{"expression":"(futureCoolingDegreeDays-baselineCoolingDegreeDays)/baselineCoolingDegreeDays","unit":"1"}},"assumptions":["Degree-day bases and time periods are consistent."],"notes":[],"version":"0.15.0"},{"id":"sc.flood_expected_annual_damage","category":"Climate adaptation & hazards","title":"Flood expected annual damage","equation":"EAD = probability \u00d7 damage","inputs":[{"key":"annualProbability","label":"Annual flood probability","unit":"1/yr","default":0.02},{"key":"eventDamage","label":"Estimated event damage","unit":"USD/event","default":850000000}],"outputs":{"expectedAnnualDamage":{"expression":"annualProbability*eventDamage","unit":"USD/yr"}},"assumptions":["Single-event screening approximation; full EAD requires integrating the complete damage-probability curve."],"notes":[],"version":"0.15.0"},{"id":"sc.stormwater_retention","category":"Climate adaptation & hazards","title":"Distributed stormwater retention","equation":"Retained volume = rainfall \u00d7 treated area \u00d7 retention fraction","inputs":[{"key":"stormDepthM","label":"Design storm depth","unit":"m","default":0.05},{"key":"treatedAreaM2","label":"Green-infrastructure treatment area","unit":"m^2","default":2400000},{"key":"retentionFraction","label":"Retained fraction","unit":"1","default":0.65}],"outputs":{"retainedVolumeM3":{"expression":"stormDepthM*treatedAreaM2*retentionFraction","unit":"m^3/event"}},"assumptions":["Uniform storm depth and retention performance over the treated area."],"notes":[],"version":"0.15.0"},{"id":"sc.drought_supply_ratio","category":"Climate adaptation & hazards","title":"Drought supply-demand ratio","equation":"Ratio = reliable drought supply / drought demand","inputs":[{"key":"reliableSupplyM3Day","label":"Reliable drought-period supply","unit":"m^3/day","default":98000},{"key":"droughtDemandM3Day","label":"Drought-period demand","unit":"m^3/day","default":112000}],"outputs":{"supplyDemandRatio":{"expression":"reliableSupplyM3Day/droughtDemandM3Day","unit":"1"},"dailyDeficitM3":{"expression":"max(0,droughtDemandM3Day-reliableSupplyM3Day)","unit":"m^3/day"}},"assumptions":["Supply and demand use a common drought scenario and reliability definition."],"notes":[],"version":"0.15.0"},{"id":"sc.wildfire_exposure_rate","category":"Climate adaptation & hazards","title":"Wildfire-interface exposure rate","equation":"Exposure = exposed assets / total assets","inputs":[{"key":"exposedAssets","label":"Assets in wildfire exposure area","unit":"assets","default":18000},{"key":"totalAssets","label":"Total assessed assets","unit":"assets","default":120000}],"outputs":{"wildfireExposureFraction":{"expression":"exposedAssets/totalAssets","unit":"1"}},"assumptions":["Exposure area and asset inventory use compatible spatial definitions."],"notes":[],"version":"0.15.0"},{"id":"sc.sea_level_exposure","category":"Climate adaptation & hazards","title":"Sea-level-rise population exposure","equation":"Exposure = population below elevation threshold / total population","inputs":[{"key":"populationBelowThreshold","label":"Population below threshold","unit":"persons","default":36000},{"key":"totalPopulation","label":"Total population","unit":"persons","default":300000}],"outputs":{"seaLevelExposureFraction":{"expression":"populationBelowThreshold/totalPopulation","unit":"1"}},"assumptions":["Elevation threshold, protection assumptions, and population year are explicitly documented."],"notes":[],"version":"0.15.0"},{"id":"sc.adaptation_benefit_cost","category":"Climate adaptation & hazards","title":"Adaptation benefit-cost ratio","equation":"BCR = present value of avoided loss / adaptation cost","inputs":[{"key":"avoidedLossPresentValue","label":"Present value of avoided loss","unit":"USD","default":420000000},{"key":"adaptationCost","label":"Adaptation investment cost","unit":"USD","default":180000000}],"outputs":{"benefitCostRatio":{"expression":"avoidedLossPresentValue/adaptationCost","unit":"1"},"netBenefit":{"expression":"avoidedLossPresentValue-adaptationCost","unit":"USD"}},"assumptions":["Avoided loss and adaptation cost use the same discounting and analysis period."],"notes":[],"version":"0.15.0"},{"id":"sc.critical_service_reliability","category":"Infrastructure resilience & continuity","title":"Critical-service reliability","equation":"Reliability = delivered service / required service","inputs":[{"key":"deliveredService","label":"Delivered critical service","unit":"service units","default":920},{"key":"requiredService","label":"Required critical service","unit":"service units","default":1000}],"outputs":{"serviceReliability":{"expression":"deliveredService/requiredService","unit":"1"}},"assumptions":["Delivered and required service use the same operating period and unit."],"notes":[],"version":"0.15.0"},{"id":"sc.system_redundancy","category":"Infrastructure resilience & continuity","title":"Critical-system redundancy","equation":"Redundancy = backup capacity / required capacity","inputs":[{"key":"backupCapacity","label":"Independent backup capacity","unit":"service units","default":420},{"key":"requiredCapacity","label":"Required critical capacity","unit":"service units","default":1000}],"outputs":{"redundancyFraction":{"expression":"backupCapacity/requiredCapacity","unit":"1"}},"assumptions":["Backup capacity is operationally independent and available during the stated event."],"notes":[],"version":"0.15.0"},{"id":"sc.reserve_margin","category":"Infrastructure resilience & continuity","title":"Infrastructure reserve margin","equation":"Reserve margin = (capacity \u2212 peak demand) / peak demand","inputs":[{"key":"availableCapacity","label":"Available system capacity","unit":"service units","default":1250},{"key":"peakDemand","label":"Peak demand","unit":"service units","default":1000}],"outputs":{"reserveMargin":{"expression":"(availableCapacity-peakDemand)/peakDemand","unit":"1"}},"assumptions":["Available capacity is deliverable under the stated operating condition."],"notes":[],"version":"0.15.0"},{"id":"sc.customer_outage_hours","category":"Infrastructure resilience & continuity","title":"Customer outage-hours","equation":"Outage burden = affected customers \u00d7 outage duration","inputs":[{"key":"affectedCustomers","label":"Affected customers","unit":"customers","default":48000},{"key":"outageHours","label":"Average outage duration","unit":"h","default":14}],"outputs":{"customerOutageHours":{"expression":"affectedCustomers*outageHours","unit":"customer*h"}},"assumptions":["Affected-customer count and outage duration describe the same incident."],"notes":[],"version":"0.15.0"},{"id":"sc.recovery_time","category":"Infrastructure resilience & continuity","title":"Linear service recovery time to target","equation":"Time = total recovery duration \u00d7 (target \u2212 initial)/(final \u2212 initial)","inputs":[{"key":"initialServiceFraction","label":"Initial retained service","unit":"1","default":0.3},{"key":"finalServiceFraction","label":"Final restored service","unit":"1","default":1},{"key":"targetServiceFraction","label":"Target service level","unit":"1","default":0.9},{"key":"totalRecoveryDays","label":"Total recovery duration","unit":"day","default":30}],"outputs":{"daysToTarget":{"expression":"totalRecoveryDays*(targetServiceFraction-initialServiceFraction)/(finalServiceFraction-initialServiceFraction)","unit":"day"}},"assumptions":["Service recovers linearly between the stated initial and final conditions."],"notes":[],"version":"0.15.0"},{"id":"sc.resilience_triangle_loss","category":"Infrastructure resilience & continuity","title":"Resilience-triangle service loss","equation":"Loss = duration \u00d7 [1 \u2212 average service]","inputs":[{"key":"initialServiceFraction","label":"Initial retained service","unit":"1","default":0.3},{"key":"finalServiceFraction","label":"Final restored service","unit":"1","default":1},{"key":"recoveryDays","label":"Recovery duration","unit":"day","default":30}],"outputs":{"serviceDayLoss":{"expression":"recoveryDays*(1-(initialServiceFraction+finalServiceFraction)/2)","unit":"service*day"},"averageServiceFraction":{"expression":"(initialServiceFraction+finalServiceFraction)/2","unit":"1"}},"assumptions":["Linear recovery trajectory."],"notes":[],"version":"0.15.0"},{"id":"sc.backup_autonomy","category":"Infrastructure resilience & continuity","title":"Backup-system autonomy","equation":"Autonomy = stored usable energy / critical load","inputs":[{"key":"usableStoredEnergyKWh","label":"Usable stored energy","unit":"kWh","default":24000},{"key":"criticalLoadKW","label":"Critical load","unit":"kW","default":800}],"outputs":{"autonomyHours":{"expression":"usableStoredEnergyKWh/criticalLoadKW","unit":"h"}},"assumptions":["Critical load is approximately constant and storage availability is fully represented by usable energy."],"notes":[],"version":"0.15.0"},{"id":"sc.interdependency_risk","category":"Infrastructure resilience & continuity","title":"Infrastructure interdependency risk score","equation":"Risk = probability \u00d7 consequence \u00d7 dependency multiplier","inputs":[{"key":"failureProbability","label":"Annual failure probability","unit":"1/yr","default":0.08},{"key":"consequenceScore","label":"Normalized consequence score","unit":"0-100","default":75},{"key":"dependencyMultiplier","label":"Interdependency multiplier","unit":"1","default":1.4}],"outputs":{"interdependencyRiskScore":{"expression":"failureProbability*consequenceScore*dependencyMultiplier","unit":"risk points/yr"}},"assumptions":["Probability, consequence, and dependency multiplier are explicitly documented screening inputs."],"notes":[],"version":"0.15.0"},{"id":"sc.energy_burden","category":"Equity & social resilience","title":"Household energy burden","equation":"Energy burden = annual household energy cost / annual household income","inputs":[{"key":"annualEnergyCost","label":"Annual household energy cost","unit":"USD/yr","default":2400},{"key":"annualHouseholdIncome","label":"Annual household income","unit":"USD/yr","default":42000}],"outputs":{"energyBurdenFraction":{"expression":"annualEnergyCost/annualHouseholdIncome","unit":"1"}},"assumptions":["Costs and income use compatible household and annual definitions."],"notes":[],"version":"0.15.0"},{"id":"sc.transit_access_equity","category":"Equity & social resilience","title":"Transit-access equity ratio","equation":"Equity ratio = priority-population access / citywide access","inputs":[{"key":"priorityAccessFraction","label":"Priority-population access","unit":"1","default":0.62},{"key":"citywideAccessFraction","label":"Citywide access","unit":"1","default":0.78}],"outputs":{"accessEquityRatio":{"expression":"priorityAccessFraction/citywideAccessFraction","unit":"1"},"accessGapPercentagePoints":{"expression":"100*(citywideAccessFraction-priorityAccessFraction)","unit":"percentage points"}},"assumptions":["Access fractions use the same threshold, travel mode, and opportunity definition."],"notes":[],"version":"0.15.0"},{"id":"sc.green_space_equity_gap","category":"Equity & social resilience","title":"Green-space equity gap","equation":"Gap = citywide green space per capita \u2212 priority-area value","inputs":[{"key":"citywideM2PerCapita","label":"Citywide green space","unit":"m^2/person","default":18},{"key":"priorityAreaM2PerCapita","label":"Priority-area green space","unit":"m^2/person","default":8}],"outputs":{"greenSpaceGapM2PerCapita":{"expression":"citywideM2PerCapita-priorityAreaM2PerCapita","unit":"m^2/person"},"equityRatio":{"expression":"priorityAreaM2PerCapita/citywideM2PerCapita","unit":"1"}},"assumptions":["Green-space inventories and population measures use comparable definitions."],"notes":[],"version":"0.15.0"},{"id":"sc.heat_vulnerability","category":"Equity & social resilience","title":"Weighted heat-vulnerability score","equation":"Score = weighted exposure + sensitivity + adaptive-capacity deficit","inputs":[{"key":"exposureScore","label":"Heat exposure score","unit":"0-100","default":82},{"key":"exposureWeight","label":"Exposure weight","unit":"1","default":0.4},{"key":"sensitivityScore","label":"Population sensitivity score","unit":"0-100","default":74},{"key":"sensitivityWeight","label":"Sensitivity weight","unit":"1","default":0.35},{"key":"capacityDeficitScore","label":"Adaptive-capacity deficit","unit":"0-100","default":68},{"key":"capacityWeight","label":"Capacity-deficit weight","unit":"1","default":0.25}],"outputs":{"heatVulnerabilityScore":{"expression":"(exposureScore*exposureWeight+sensitivityScore*sensitivityWeight+capacityDeficitScore*capacityWeight)/(exposureWeight+sensitivityWeight+capacityWeight)","unit":"0-100"}},"assumptions":["Component scores use a common normalization and weights are explicit planning choices."],"notes":[],"version":"0.15.0"},{"id":"sc.housing_resilience_burden","category":"Equity & social resilience","title":"Household resilience-upgrade burden","equation":"Burden = annualized resilience cost / household income","inputs":[{"key":"annualizedUpgradeCost","label":"Annualized resilience-upgrade cost","unit":"USD/yr","default":1800},{"key":"annualHouseholdIncome","label":"Annual household income","unit":"USD/yr","default":42000}],"outputs":{"resilienceBurdenFraction":{"expression":"annualizedUpgradeCost/annualHouseholdIncome","unit":"1"}},"assumptions":["Annualized costs and household income use compatible terms."],"notes":[],"version":"0.15.0"},{"id":"sc.service_deprivation","category":"Equity & social resilience","title":"Basic-service deprivation rate","equation":"Deprivation = population lacking service / total population","inputs":[{"key":"populationLackingService","label":"Population lacking reliable service","unit":"persons","default":24000},{"key":"totalPopulation","label":"Total population","unit":"persons","default":300000}],"outputs":{"serviceDeprivationFraction":{"expression":"populationLackingService/totalPopulation","unit":"1"}},"assumptions":["Service definition and population data use the same geographic boundary."],"notes":[],"version":"0.15.0"},{"id":"sc.accessibility_disparity","category":"Equity & social resilience","title":"Accessibility disparity index","equation":"Disparity = (high-access \u2212 low-access) / citywide access","inputs":[{"key":"highAccessOpportunities","label":"High-access-group opportunities","unit":"opportunities","default":78000},{"key":"lowAccessOpportunities","label":"Low-access-group opportunities","unit":"opportunities","default":32000},{"key":"citywideAverageOpportunities","label":"Citywide average opportunities","unit":"opportunities","default":56000}],"outputs":{"accessibilityDisparity":{"expression":"(highAccessOpportunities-lowAccessOpportunities)/citywideAverageOpportunities","unit":"1"}},"assumptions":["Opportunity counts use the same threshold, mode, and destination inventory."],"notes":[],"version":"0.15.0"},{"id":"sc.equitable_investment_priority","category":"Equity & social resilience","title":"Equitable resilience-investment priority","equation":"Priority = vulnerability \u00d7 service gap \u00d7 benefit potential","inputs":[{"key":"vulnerabilityScore","label":"Vulnerability score","unit":"0-100","default":78},{"key":"serviceGapScore","label":"Service-gap score","unit":"0-100","default":72},{"key":"benefitPotentialScore","label":"Benefit-potential score","unit":"0-100","default":85}],"outputs":{"priorityScore":{"expression":"(vulnerabilityScore/100)*(serviceGapScore/100)*(benefitPotentialScore/100)*100","unit":"0-100"}},"assumptions":["Scores are transparent screening inputs and do not automate allocation decisions."],"notes":[],"version":"0.15.0"},{"id":"sc.sustainable_city_score","category":"Integrated scenarios & governance","title":"Weighted sustainable-city score","equation":"Score = weighted environment + equity + economy + resilience","inputs":[{"key":"environmentScore","label":"Environmental score","unit":"0-100","default":74},{"key":"environmentWeight","label":"Environmental weight","unit":"1","default":0.3},{"key":"equityScore","label":"Equity score","unit":"0-100","default":68},{"key":"equityWeight","label":"Equity weight","unit":"1","default":0.25},{"key":"economyScore","label":"Economic score","unit":"0-100","default":72},{"key":"economyWeight","label":"Economic weight","unit":"1","default":0.2},{"key":"resilienceScore","label":"Resilience score","unit":"0-100","default":77},{"key":"resilienceWeight","label":"Resilience weight","unit":"1","default":0.25}],"outputs":{"sustainableCityScore":{"expression":"(environmentScore*environmentWeight+equityScore*equityWeight+economyScore*economyWeight+resilienceScore*resilienceWeight)/(environmentWeight+equityWeight+economyWeight+resilienceWeight)","unit":"0-100"}},"assumptions":["Component scores use a common scale and weights represent an explicit governance choice."],"notes":[],"version":"0.15.0"},{"id":"sc.sdg_localization","category":"Integrated scenarios & governance","title":"Localized SDG target-progress score","equation":"Progress = weighted achieved targets / weighted target total","inputs":[{"key":"achievedWeight","label":"Weight of achieved or on-track targets","unit":"target-weight points","default":62},{"key":"totalWeight","label":"Total assessed target weight","unit":"target-weight points","default":100}],"outputs":{"sdgProgressFraction":{"expression":"achievedWeight/totalWeight","unit":"1"}},"assumptions":["Target status and weights are documented and regularly reviewed."],"notes":[],"version":"0.15.0"},{"id":"sc.policy_implementation","category":"Integrated scenarios & governance","title":"Policy implementation rate","equation":"Implementation = completed actions / planned actions","inputs":[{"key":"completedActions","label":"Completed policy actions","unit":"actions","default":38},{"key":"plannedActions","label":"Planned policy actions","unit":"actions","default":60}],"outputs":{"implementationFraction":{"expression":"completedActions/plannedActions","unit":"1"}},"assumptions":["Actions use a documented completion definition and reporting period."],"notes":[],"version":"0.15.0"},{"id":"sc.portfolio_net_present_value","category":"Integrated scenarios & governance","title":"Sustainability portfolio net present value","equation":"NPV = annual benefit annuity \u2212 initial cost","inputs":[{"key":"initialCost","label":"Initial portfolio cost","unit":"USD","default":420000000},{"key":"annualNetBenefit","label":"Annual net benefit","unit":"USD/yr","default":62000000},{"key":"discountRate","label":"Real discount rate","unit":"1","default":0.04},{"key":"years","label":"Analysis period","unit":"yr","default":20}],"outputs":{"netPresentValue":{"expression":"annualNetBenefit*(1-(1+discountRate)**(-years))/discountRate-initialCost","unit":"USD"}},"assumptions":["Annual net benefit and real discount rate remain constant."],"notes":[],"version":"0.15.0"},{"id":"sc.emissions_target_gap","category":"Integrated scenarios & governance","title":"Emissions target gap","equation":"Gap = projected emissions \u2212 target emissions","inputs":[{"key":"projectedEmissionsTonnes","label":"Projected target-year emissions","unit":"tCO2e/yr","default":980000},{"key":"targetEmissionsTonnes","label":"Target-year emissions goal","unit":"tCO2e/yr","default":700000}],"outputs":{"targetGapTonnes":{"expression":"projectedEmissionsTonnes-targetEmissionsTonnes","unit":"tCO2e/yr"},"targetGapFraction":{"expression":"(projectedEmissionsTonnes-targetEmissionsTonnes)/targetEmissionsTonnes","unit":"1"}},"assumptions":["Projection and target use the same accounting boundary."],"notes":[],"version":"0.15.0"},{"id":"sc.resilience_target_gap","category":"Integrated scenarios & governance","title":"Resilience target gap","equation":"Gap = target resilience score \u2212 projected score","inputs":[{"key":"targetScore","label":"Target resilience score","unit":"0-100","default":85},{"key":"projectedScore","label":"Projected resilience score","unit":"0-100","default":72}],"outputs":{"resilienceGapPoints":{"expression":"targetScore-projectedScore","unit":"points"}},"assumptions":["Target and projected scores use the same indicator framework."],"notes":[],"version":"0.15.0"},{"id":"sc.co_benefit_score","category":"Integrated scenarios & governance","title":"Climate-action co-benefit score","equation":"Co-benefit = weighted health-supporting + equity + economic + ecological benefits","inputs":[{"key":"healthSupportingScore","label":"Health-supporting conditions score","unit":"0-100","default":78},{"key":"healthSupportingWeight","label":"Health-supporting weight","unit":"1","default":0.25},{"key":"equityScore","label":"Equity score","unit":"0-100","default":72},{"key":"equityWeight","label":"Equity weight","unit":"1","default":0.3},{"key":"economicScore","label":"Economic score","unit":"0-100","default":68},{"key":"economicWeight","label":"Economic weight","unit":"1","default":0.2},{"key":"ecologicalScore","label":"Ecological score","unit":"0-100","default":82},{"key":"ecologicalWeight","label":"Ecological weight","unit":"1","default":0.25}],"outputs":{"coBenefitScore":{"expression":"(healthSupportingScore*healthSupportingWeight+equityScore*equityWeight+economicScore*economicWeight+ecologicalScore*ecologicalWeight)/(healthSupportingWeight+equityWeight+economicWeight+ecologicalWeight)","unit":"0-100"}},"assumptions":["Scores are non-clinical planning indicators and weights are explicit scenario choices."],"notes":[],"version":"0.15.0"},{"id":"sc.scenario_robustness","category":"Integrated scenarios & governance","title":"Multi-scenario robustness score","equation":"Robustness = minimum scenario performance / target performance","inputs":[{"key":"scenario1Score","label":"Scenario 1 performance","unit":"0-100","default":76},{"key":"scenario2Score","label":"Scenario 2 performance","unit":"0-100","default":68},{"key":"scenario3Score","label":"Scenario 3 performance","unit":"0-100","default":72},{"key":"targetScore","label":"Target performance","unit":"0-100","default":80}],"outputs":{"robustnessFraction":{"expression":"min(scenario1Score,scenario2Score,scenario3Score)/targetScore","unit":"1"},"worstCaseScore":{"expression":"min(scenario1Score,scenario2Score,scenario3Score)","unit":"0-100"}},"assumptions":["Scenario scores use the same performance framework and target."],"notes":[],"version":"0.15.0"}]};
const CATEGORIES = ["Urban metabolism & resources","Climate mitigation & decarbonization","Climate adaptation & hazards","Infrastructure resilience & continuity","Equity & social resilience","Integrated scenarios & governance"];
const METHODS = new Map(CATALOG.methods.map((item) => [item.id, item]));
const BENCHMARKS = [["sc.energy_per_capita",{"annualEnergyMWh":8000,"population":1000},"energyMWhPerCapitaYear",8],["sc.water_per_capita",{"annualWaterM3":365000,"population":1000},"waterLitersPerCapitaDay",1000],["sc.waste_per_capita",{"annualWasteTonnes":365,"population":1000},"wasteKgPerCapitaDay",1],["sc.material_circularity",{"secondaryMaterialTonnes":25,"totalMaterialTonnes":100},"circularityFraction",0.25],["sc.community_emissions",{"electricityTonnes":1,"fuelTonnes":2,"transportTonnes":3,"wasteTonnes":4},"totalEmissionsTonnes",10],["sc.emissions_per_capita",{"annualEmissionsTonnes":8000,"population":1000},"tonnesPerCapitaYear",8],["sc.reduction_trajectory",{"baselineTonnes":1000,"targetTonnes":400,"years":6},"annualReductionTonnes",100],["sc.renewable_electricity_share",{"renewableMWh":40,"totalElectricityMWh":100},"renewableShare",0.4],["sc.heat_exposure_rate",{"exposedPopulation":200,"totalPopulation":1000},"heatExposureFraction",0.2],["sc.cooling_degree_change",{"baselineCoolingDegreeDays":1000,"futureCoolingDegreeDays":1250},"increaseFraction",0.25],["sc.flood_expected_annual_damage",{"annualProbability":0.02,"eventDamage":1000000},"expectedAnnualDamage",20000],["sc.stormwater_retention",{"stormDepthM":0.05,"treatedAreaM2":10000,"retentionFraction":0.8},"retainedVolumeM3",400],["sc.critical_service_reliability",{"deliveredService":900,"requiredService":1000},"serviceReliability",0.9],["sc.reserve_margin",{"availableCapacity":120,"peakDemand":100},"reserveMargin",0.2],["sc.customer_outage_hours",{"affectedCustomers":100,"outageHours":4},"customerOutageHours",400],["sc.backup_autonomy",{"usableStoredEnergyKWh":1000,"criticalLoadKW":100},"autonomyHours",10],["sc.energy_burden",{"annualEnergyCost":3000,"annualHouseholdIncome":50000},"energyBurdenFraction",0.06],["sc.transit_access_equity",{"priorityAccessFraction":0.6,"citywideAccessFraction":0.75},"accessEquityRatio",0.8],["sc.service_deprivation",{"populationLackingService":100,"totalPopulation":1000},"serviceDeprivationFraction",0.1],["sc.sdg_localization",{"achievedWeight":60,"totalWeight":100},"sdgProgressFraction",0.6],["sc.emissions_target_gap",{"projectedEmissionsTonnes":900,"targetEmissionsTonnes":700},"targetGapTonnes",200],["sc.scenario_robustness",{"scenario1Score":80,"scenario2Score":60,"scenario3Score":70,"targetScore":80},"robustnessFraction",0.75]];

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

  if (methodId === 'sc.drought_supply_ratio' && outputs.supplyDemandRatio < 1) {
    warnings.push('Reliable drought supply is below stated drought demand.');
  }

  if (
    methodId === 'sc.critical_service_reliability'
    && outputs.serviceReliability < 1
  ) {
    warnings.push('Critical service delivery is below the stated requirement.');
  }

  if (methodId === 'sc.energy_burden' && outputs.energyBurdenFraction > 0.06) {
    warnings.push('The stated household energy burden exceeds 6%.');
  }

  if (
    methodId === 'sc.transit_access_equity'
    && outputs.accessEquityRatio < 0.8
  ) {
    warnings.push(
      'Priority-population transit access is below 80% of the citywide level.'
    );
  }

  if (
    methodId === 'sc.emissions_target_gap'
    && outputs.targetGapTonnes > 0
  ) {
    warnings.push('Projected emissions remain above the stated target.');
  }

  if (
    methodId === 'ci.retaining_wall_overturning'
    && outputs.factorOfSafety < 1.5
  ) {
    warnings.push(
      'Overturning factor of safety is below a common preliminary screening threshold.'
    );
  }

  if (
    methodId === 'ci.slope_factor_of_safety'
    && outputs.factorOfSafety < 1.3
  ) {
    warnings.push('Slope factor of safety requires detailed geotechnical review.');
  }

  if (
    methodId === 'ci.service_reliability'
    && outputs.reliability < 1
  ) {
    warnings.push(
      'Delivered infrastructure service is below the stated requirement.'
    );
  }

  return warnings;
}

function run(methodId, rawInputs) {
  const method = METHODS.get(methodId);

  if (!method) {
    throw new Error(`Unknown method: ${methodId}`);
  }

  const inputs = {};

  for (const field of method.inputs) {
    inputs[field.key] = finiteNumber(rawInputs[field.key], field.label);
  }

  const outputs = {};
  const outputUnits = {};

  for (const [key, specification] of Object.entries(method.outputs)) {
    const value = Number(evaluate(specification.expression, inputs));

    if (!Number.isFinite(value)) {
      throw new Error(`${key} did not produce a finite result.`);
    }

    outputs[key] = value;
    outputUnits[key] = specification.unit;
  }

  const warnings = warningsFor(methodId, outputs);

  const result = {
    schema: "sc-lab-sustainable-cities-resilience-analysis/1.0",
    version: VERSION,
    methodId: method.id,
    methodVersion: method.version || VERSION,
    category: method.category,
    title: method.title,
    equation: method.equation,
    expressions: Object.fromEntries(
      Object.entries(method.outputs).map(
        ([key, specification]) => [key, specification.expression]
      )
    ),
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
      benchmarkSuite: "sc-lab-sustainable-cities-resilience-benchmarks/1.0",
    },
    audit: {
      createdAt: new Date().toISOString(),
      engine: "sc-lab-sustainable-cities-resilience-js",
      release: VERSION,
    },
  };

  result.audit.fingerprint = fingerprint(JSON.stringify(result));
  return result;
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

function expressionMarkup(method) {
  return Object.entries(method.outputs).map(([key, specification]) => `
    <div class="sc-formula-expression">
      <span>${escapeHtml(key)}</span>
      <code>${escapeHtml(specification.expression)}</code>
      <small>${escapeHtml(specification.unit || '')}</small>
    </div>
  `).join('');
}

function render(root = document) {
  const mounts = root.querySelectorAll('[data-sustainable-cities-resilience-root]');

  mounts.forEach((mount) => {
    if (mount.dataset.scSustainableCitiesResilienceLabRendered === '1') {
      return;
    }

    mount.dataset.scSustainableCitiesResilienceLabRendered = '1';

    mount.innerHTML = `
      <div class="sc-scr-workbench">
        <div class="sc-scr-controls">
          <label>
            Workspace
            <select data-scr-category>
              ${CATEGORIES.map(
                (category) => `<option>${escapeHtml(category)}</option>`
              ).join('')}
            </select>
          </label>

          <label>
            Method
            <select data-scr-method></select>
          </label>
        </div>

        <article class="sc-scr-card">
          <p class="sc-scr-kicker" data-scr-category-label></p>
          <h4 data-scr-title></h4>

          <div class="sc-visible-formula" data-scr-formula-panel>
            <span class="sc-visible-formula-label">Engineering formula</span>
            <code data-scr-equation></code>
          </div>

          <p data-scr-assumptions></p>

          <details class="sc-formula-source" open>
            <summary>Executable formula expressions</summary>
            <div data-scr-expressions></div>
          </details>

          <div class="sc-scr-inputs" data-scr-inputs></div>

          <div class="sc-scr-actions">
            <button type="button" class="button button-primary" data-scr-run>
              Run analysis
            </button>
            <button type="button" class="button" data-scr-save>
              Save to project
            </button>
            <button type="button" class="button" data-scr-note>
              Add to notebook
            </button>
            <button type="button" class="button" data-scr-visualize>
              Visualize
            </button>
          </div>

          <div
            class="sc-scr-status"
            data-scr-status
            role="status"
            aria-live="polite"
          >Select a sustainable-cities or urban-resilience method.</div>

          <div class="sc-scr-results" data-scr-results></div>

          <details>
            <summary>Analysis contract</summary>
            <pre data-scr-json>{}</pre>
          </details>
        </article>

        <section class="sc-scr-validation">
          <div>
            <p class="sc-scr-kicker">VALIDATION</p>
            <h4>Sustainable cities and urban-resilience benchmark suite</h4>
            <p>Reference cases cover urban metabolism, decarbonization, hazards, infrastructure continuity, equity, and integrated scenarios.</p>
          </div>

          <button type="button" class="button" data-scr-benchmarks>
            Run ${BENCHMARKS.length} benchmarks
          </button>

          <div data-scr-benchmark-results></div>
        </section>
      </div>
    `;
  });
}

function init(root = document, projects = Lab.Projects) {
  render(root);

  const mounts = root.querySelectorAll('[data-sustainable-cities-resilience-root]');

  mounts.forEach((mount) => {
    if (
      mount.dataset.scFormulaInterfaceInitialized
      === "SustainableCitiesResilienceLab-0.15.0"
    ) {
      return;
    }

    mount.dataset.scFormulaInterfaceInitialized =
      "SustainableCitiesResilienceLab-0.15.0";

    const categorySelect = mount.querySelector('[data-scr-category]');
    const methodSelect = mount.querySelector('[data-scr-method]');
    const inputContainer = mount.querySelector('[data-scr-inputs]');
    const status = mount.querySelector('[data-scr-status]');
    const resultContainer = mount.querySelector('[data-scr-results]');
    const jsonTarget = mount.querySelector('[data-scr-json]');
    let current = null;

    function renderMethod() {
      const selected = METHODS.get(methodSelect.value);

      if (!selected) {
        return;
      }

      mount.querySelector('[data-scr-category-label]').textContent =
        selected.category.toUpperCase();
      mount.querySelector('[data-scr-title]').textContent =
        selected.title;
      mount.querySelector('[data-scr-equation]').textContent =
        selected.equation || 'Formula not documented.';
      mount.querySelector('[data-scr-assumptions]').textContent =
        (selected.assumptions || []).join(' ');
      mount.querySelector('[data-scr-expressions]').innerHTML =
        expressionMarkup(selected);

      inputContainer.innerHTML = selected.inputs.map((input) => `
        <label>
          ${escapeHtml(input.label)}
          <span>${escapeHtml(input.unit)}</span>
          <input
            type="number"
            step="any"
            value="${escapeHtml(input.default)}"
            data-scr-field="${escapeHtml(input.key)}"
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

        inputContainer
          .querySelectorAll('[data-scr-field]')
          .forEach((input) => {
            raw[input.dataset.scrField] = input.value;
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
    mount
      .querySelector('[data-scr-run]')
      .addEventListener('click', execute);

    mount
      .querySelector('[data-scr-save]')
      .addEventListener('click', () => {
        const record = current || execute();

        if (!record) {
          return;
        }

        if (projects && typeof projects.add === 'function') {
          projects.add(
            "sustainableCitiesResilienceAnalyses",
            record,
            `${record.title} saved`
          );

          projects.add(
            "sustainableCityResilienceRecords",
            {
              schema: "sc-lab-sustainable-city-resilience-record/1.0",
              version: VERSION,
              methodId: record.methodId,
              category: record.category,
              title: record.title,
              recordedAt: new Date().toISOString(),
              fingerprint: record.audit.fingerprint,
            },
            `Index record added: ${record.title}`
          );

          status.textContent = 'Saved to the active project.';
        } else {
          status.textContent =
            'Analysis is ready, but the project storage module is unavailable.';
        }
      });

    mount
      .querySelector('[data-scr-note]')
      .addEventListener('click', () => {
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
              tags: ["sustainable-cities", "urban-resilience"].concat([
                record.category,
                record.methodId,
              ]),
            },
            `Notebook entry added: ${record.title}`
          );

          status.textContent = 'Notebook entry added.';
        }
      });

    mount
      .querySelector('[data-scr-visualize]')
      .addEventListener('click', () => {
        const record = current || execute();

        if (record) {
          document.dispatchEvent(
            new CustomEvent('sc-lab:analysis', { detail: record })
          );
          status.textContent = 'Analysis sent to the visualization layer.';
        }
      });

    mount
      .querySelector('[data-scr-benchmarks]')
      .addEventListener('click', () => {
        const rows = runBenchmarks();
        const passed = rows.filter((row) => row.passed).length;

        mount.querySelector(
          '[data-scr-benchmark-results]'
        ).innerHTML = `
          <p><strong>${passed}/${rows.length}</strong> benchmarks passed.</p>
          <div class="sc-scr-benchmark-grid">
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
            "sustainableCitiesValidationRecords",
            {
              schema: "sc-lab-sustainable-cities-resilience-benchmarks/1.0",
              version: VERSION,
              createdAt: new Date().toISOString(),
              passed,
              total: rows.length,
              results: rows,
            },
            `Validation: ${passed}/${rows.length}`
          );
        }
      });

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

Lab.SustainableCitiesResilienceLab = {
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
