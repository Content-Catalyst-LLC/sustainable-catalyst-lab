(function (global) {
'use strict';

const Lab = global.SCLab = global.SCLab || {};
const VERSION = '0.14.0';
const CATALOG = {"schema":"sc-lab-urban-planning-spatial-catalog/1.0","version":"0.14.0","methodCount":48,"categories":["Land use & development","Accessibility & mobility","Networks & spatial systems","GIS & spatial analysis","Public services & infrastructure","Resilience, equity & scenarios"],"methods":[{"id":"up.gross_population_density","category":"Land use & development","title":"Gross population density","equation":"Density = population / gross land area","inputs":[{"key":"population","label":"Population","unit":"persons","default":25000},{"key":"grossAreaHa","label":"Gross land area","unit":"ha","default":500}],"outputs":{"personsPerHa":{"expression":"population/grossAreaHa","unit":"persons/ha"}},"assumptions":["Population and land area refer to the same planning boundary."],"notes":[],"version":"0.14.0"},{"id":"up.net_residential_density","category":"Land use & development","title":"Net residential density","equation":"Density = dwellings / residential land area","inputs":[{"key":"dwellingUnits","label":"Dwelling units","unit":"units","default":4800},{"key":"residentialAreaHa","label":"Net residential land","unit":"ha","default":160}],"outputs":{"dwellingsPerHa":{"expression":"dwellingUnits/residentialAreaHa","unit":"units/ha"}},"assumptions":["Net residential area excludes non-residential and major right-of-way land."],"notes":[],"version":"0.14.0"},{"id":"up.floor_area_ratio","category":"Land use & development","title":"Floor area ratio","equation":"FAR = gross floor area / site area","inputs":[{"key":"grossFloorAreaM2","label":"Gross floor area","unit":"m^2","default":24000},{"key":"siteAreaM2","label":"Site area","unit":"m^2","default":8000}],"outputs":{"floorAreaRatio":{"expression":"grossFloorAreaM2/siteAreaM2","unit":"1"}},"assumptions":["Floor area and site area use the same development parcel boundary."],"notes":[],"version":"0.14.0"},{"id":"up.land_use_mix","category":"Land use & development","title":"Normalized land-use mix","equation":"Mix = -\u03a3(p ln p) / ln(n)","inputs":[{"key":"residentialShare","label":"Residential share","unit":"1","default":0.5},{"key":"employmentShare","label":"Employment share","unit":"1","default":0.3},{"key":"amenityShare","label":"Amenity share","unit":"1","default":0.2}],"outputs":{"normalizedMixIndex":{"expression":"-(residentialShare*log(residentialShare)+employmentShare*log(employmentShare)+amenityShare*log(amenityShare))/log(3)","unit":"0-1"},"shareTotal":{"expression":"residentialShare+employmentShare+amenityShare","unit":"1"}},"assumptions":["Shares are positive and describe the same land-use classification."],"notes":[],"version":"0.14.0"},{"id":"up.jobs_housing_balance","category":"Land use & development","title":"Jobs-housing balance","equation":"Balance = jobs / employed residents","inputs":[{"key":"jobs","label":"Jobs","unit":"jobs","default":18000},{"key":"employedResidents","label":"Employed residents","unit":"persons","default":15000}],"outputs":{"jobsHousingRatio":{"expression":"jobs/employedResidents","unit":"jobs/employed resident"},"balanceDeviation":{"expression":"abs(jobs/employedResidents-1)","unit":"1"}},"assumptions":["Jobs and employed residents use the same geography and time period."],"notes":[],"version":"0.14.0"},{"id":"up.development_capacity","category":"Land use & development","title":"Remaining development capacity","equation":"Capacity = site area \u00d7 permitted FAR \u2212 existing floor area","inputs":[{"key":"siteAreaM2","label":"Site area","unit":"m^2","default":12000},{"key":"permittedFar","label":"Permitted FAR","unit":"1","default":4},{"key":"existingFloorAreaM2","label":"Existing floor area","unit":"m^2","default":18000}],"outputs":{"remainingFloorAreaM2":{"expression":"max(0,siteAreaM2*permittedFar-existingFloorAreaM2)","unit":"m^2"}},"assumptions":["Permitted FAR is applied uniformly to the stated site area."],"notes":[],"version":"0.14.0"},{"id":"up.impervious_cover","category":"Land use & development","title":"Impervious-cover ratio","equation":"Impervious ratio = impervious area / site area","inputs":[{"key":"imperviousAreaM2","label":"Impervious area","unit":"m^2","default":520000},{"key":"siteAreaM2","label":"Site area","unit":"m^2","default":1000000}],"outputs":{"imperviousFraction":{"expression":"imperviousAreaM2/siteAreaM2","unit":"1"}},"assumptions":["Impervious and total site areas use the same mapped boundary."],"notes":[],"version":"0.14.0"},{"id":"up.open_space_per_capita","category":"Land use & development","title":"Public open space per capita","equation":"Open space per capita = public open-space area / population","inputs":[{"key":"openSpaceM2","label":"Public open-space area","unit":"m^2","default":360000},{"key":"population","label":"Population","unit":"persons","default":30000}],"outputs":{"openSpaceM2PerPerson":{"expression":"openSpaceM2/population","unit":"m^2/person"}},"assumptions":["Open-space inventory and population refer to the same service area."],"notes":[],"version":"0.14.0"},{"id":"up.weighted_travel_time","category":"Accessibility & mobility","title":"Trip-weighted average travel time","equation":"Average = \u03a3(trips \u00d7 time) / \u03a3(trips)","inputs":[{"key":"tripsMode1","label":"Trips in group 1","unit":"trips","default":4000},{"key":"timeMode1Min","label":"Mean group 1 time","unit":"min","default":22},{"key":"tripsMode2","label":"Trips in group 2","unit":"trips","default":2500},{"key":"timeMode2Min","label":"Mean group 2 time","unit":"min","default":38},{"key":"tripsMode3","label":"Trips in group 3","unit":"trips","default":1500},{"key":"timeMode3Min","label":"Mean group 3 time","unit":"min","default":18}],"outputs":{"averageTravelTimeMin":{"expression":"(tripsMode1*timeMode1Min+tripsMode2*timeMode2Min+tripsMode3*timeMode3Min)/(tripsMode1+tripsMode2+tripsMode3)","unit":"min"}},"assumptions":["Trip groups are mutually exclusive and use a common time definition."],"notes":[],"version":"0.14.0"},{"id":"up.cumulative_opportunities","category":"Accessibility & mobility","title":"Cumulative-opportunities accessibility","equation":"Accessibility = \u03a3 opportunities within threshold","inputs":[{"key":"opportunitiesZone1","label":"Zone 1 opportunities","unit":"opportunities","default":12000},{"key":"timeZone1Min","label":"Zone 1 travel time","unit":"min","default":18},{"key":"opportunitiesZone2","label":"Zone 2 opportunities","unit":"opportunities","default":8000},{"key":"timeZone2Min","label":"Zone 2 travel time","unit":"min","default":32},{"key":"opportunitiesZone3","label":"Zone 3 opportunities","unit":"opportunities","default":15000},{"key":"timeZone3Min","label":"Zone 3 travel time","unit":"min","default":24},{"key":"thresholdMin","label":"Travel-time threshold","unit":"min","default":30}],"outputs":{"accessibleOpportunities":{"expression":"opportunitiesZone1*(timeZone1Min<=thresholdMin)+opportunitiesZone2*(timeZone2Min<=thresholdMin)+opportunitiesZone3*(timeZone3Min<=thresholdMin)","unit":"opportunities"}},"assumptions":["Opportunities and travel times use a common destination set and travel mode."],"notes":[],"version":"0.14.0"},{"id":"up.gravity_accessibility","category":"Accessibility & mobility","title":"Gravity accessibility","equation":"A = \u03a3(O_j e^(\u2212\u03b2t_j))","inputs":[{"key":"opportunities1","label":"Zone 1 opportunities","unit":"opportunities","default":12000},{"key":"time1Min","label":"Zone 1 travel time","unit":"min","default":18},{"key":"opportunities2","label":"Zone 2 opportunities","unit":"opportunities","default":8000},{"key":"time2Min","label":"Zone 2 travel time","unit":"min","default":32},{"key":"opportunities3","label":"Zone 3 opportunities","unit":"opportunities","default":15000},{"key":"time3Min","label":"Zone 3 travel time","unit":"min","default":24},{"key":"decayPerMin","label":"Exponential decay parameter","unit":"1/min","default":0.08}],"outputs":{"gravityAccessibility":{"expression":"opportunities1*exp(-decayPerMin*time1Min)+opportunities2*exp(-decayPerMin*time2Min)+opportunities3*exp(-decayPerMin*time3Min)","unit":"weighted opportunities"}},"assumptions":["The decay parameter is calibrated or explicitly treated as a scenario assumption."],"notes":[],"version":"0.14.0"},{"id":"up.transit_frequency","category":"Accessibility & mobility","title":"Transit service frequency","equation":"Frequency = 60 / headway","inputs":[{"key":"headwayMinutes","label":"Scheduled headway","unit":"min","default":12}],"outputs":{"vehiclesPerHour":{"expression":"60/headwayMinutes","unit":"vehicles/h"}},"assumptions":["Headway is regular over the stated analysis period."],"notes":[],"version":"0.14.0"},{"id":"up.walkshed_area","category":"Accessibility & mobility","title":"Idealized walkshed area","equation":"Area = \u03c0r\u00b2","inputs":[{"key":"walkingDistanceM","label":"Walking-distance threshold","unit":"m","default":800},{"key":"networkEfficiency","label":"Network-to-circle efficiency","unit":"1","default":0.65}],"outputs":{"idealCircleAreaKm2":{"expression":"pi*walkingDistanceM**2/1000000","unit":"km^2"},"estimatedNetworkWalkshedKm2":{"expression":"pi*walkingDistanceM**2*networkEfficiency/1000000","unit":"km^2"}},"assumptions":["Network efficiency approximates barriers and street-network geometry."],"notes":[],"version":"0.14.0"},{"id":"up.intersection_density","category":"Accessibility & mobility","title":"Intersection density","equation":"Density = intersections / area","inputs":[{"key":"intersectionCount","label":"Eligible intersections","unit":"intersections","default":420},{"key":"areaKm2","label":"Analysis area","unit":"km^2","default":6}],"outputs":{"intersectionsPerKm2":{"expression":"intersectionCount/areaKm2","unit":"intersections/km^2"}},"assumptions":["Intersection definition and area boundary are applied consistently."],"notes":[],"version":"0.14.0"},{"id":"up.mode_share","category":"Accessibility & mobility","title":"Mode share","equation":"Share = mode trips / total trips","inputs":[{"key":"modeTrips","label":"Trips by selected mode","unit":"trips","default":22000},{"key":"totalTrips","label":"Total trips","unit":"trips","default":80000}],"outputs":{"modeShare":{"expression":"modeTrips/totalTrips","unit":"1"}},"assumptions":["Trip counts use a common population, purpose, and time period."],"notes":[],"version":"0.14.0"},{"id":"up.vehicle_distance_per_capita","category":"Accessibility & mobility","title":"Vehicle distance traveled per capita","equation":"VKT per capita = total vehicle-km / population","inputs":[{"key":"vehicleKilometers","label":"Total vehicle distance","unit":"vehicle-km/day","default":1250000},{"key":"population","label":"Population","unit":"persons","default":100000}],"outputs":{"vehicleKmPerCapitaDay":{"expression":"vehicleKilometers/population","unit":"vehicle-km/(person*day)"}},"assumptions":["Vehicle distance and population use the same geography and period."],"notes":[],"version":"0.14.0"},{"id":"up.network_circuity","category":"Networks & spatial systems","title":"Network circuity","equation":"Circuity = network distance / straight-line distance","inputs":[{"key":"networkDistanceKm","label":"Network distance","unit":"km","default":7.2},{"key":"straightDistanceKm","label":"Straight-line distance","unit":"km","default":5.5}],"outputs":{"circuity":{"expression":"networkDistanceKm/straightDistanceKm","unit":"1"}},"assumptions":["Both distances connect the same origin and destination."],"notes":[],"version":"0.14.0"},{"id":"up.network_beta_index","category":"Networks & spatial systems","title":"Network beta index","equation":"\u03b2 = edges / vertices","inputs":[{"key":"edges","label":"Network edges","unit":"edges","default":180},{"key":"vertices","label":"Network vertices","unit":"vertices","default":120}],"outputs":{"betaIndex":{"expression":"edges/vertices","unit":"1"}},"assumptions":["Network graph uses a consistent edge and vertex definition."],"notes":[],"version":"0.14.0"},{"id":"up.network_gamma_index","category":"Networks & spatial systems","title":"Planar-network gamma index","equation":"\u03b3 = E / [3(V\u22122)]","inputs":[{"key":"edges","label":"Network edges","unit":"edges","default":180},{"key":"vertices","label":"Network vertices","unit":"vertices","default":120}],"outputs":{"gammaIndex":{"expression":"edges/(3*(vertices-2))","unit":"0-1"}},"assumptions":["Planar connected network with at least three vertices."],"notes":[],"version":"0.14.0"},{"id":"up.network_alpha_index","category":"Networks & spatial systems","title":"Planar-network alpha index","equation":"\u03b1 = (E\u2212V+1)/(2V\u22125)","inputs":[{"key":"edges","label":"Network edges","unit":"edges","default":180},{"key":"vertices","label":"Network vertices","unit":"vertices","default":120}],"outputs":{"alphaIndex":{"expression":"(edges-vertices+1)/(2*vertices-5)","unit":"0-1"}},"assumptions":["Single connected planar network."],"notes":[],"version":"0.14.0"},{"id":"up.average_node_degree","category":"Networks & spatial systems","title":"Average node degree","equation":"Average degree = 2E / V","inputs":[{"key":"edges","label":"Network edges","unit":"edges","default":180},{"key":"vertices","label":"Network vertices","unit":"vertices","default":120}],"outputs":{"averageDegree":{"expression":"2*edges/vertices","unit":"links/node"}},"assumptions":["Undirected network graph."],"notes":[],"version":"0.14.0"},{"id":"up.degree_centrality","category":"Networks & spatial systems","title":"Node degree centrality","equation":"Centrality = node degree / (V\u22121)","inputs":[{"key":"nodeDegree","label":"Selected node degree","unit":"links","default":8},{"key":"vertices","label":"Network vertices","unit":"vertices","default":120}],"outputs":{"degreeCentrality":{"expression":"nodeDegree/(vertices-1)","unit":"0-1"}},"assumptions":["Simple undirected graph without self-loops."],"notes":[],"version":"0.14.0"},{"id":"up.network_redundancy","category":"Networks & spatial systems","title":"Network cycle redundancy","equation":"Redundancy = (E\u2212V+1)/E","inputs":[{"key":"edges","label":"Network edges","unit":"edges","default":180},{"key":"vertices","label":"Network vertices","unit":"vertices","default":120}],"outputs":{"cycleRedundancy":{"expression":"max(0,(edges-vertices+1)/edges)","unit":"0-1"}},"assumptions":["Single connected graph; metric is a screening indicator."],"notes":[],"version":"0.14.0"},{"id":"up.service_network_coverage","category":"Networks & spatial systems","title":"Service-network population coverage","equation":"Coverage = served population / total population","inputs":[{"key":"servedPopulation","label":"Population within network service area","unit":"persons","default":84000},{"key":"totalPopulation","label":"Total population","unit":"persons","default":100000}],"outputs":{"coverageFraction":{"expression":"servedPopulation/totalPopulation","unit":"1"}},"assumptions":["Served and total population use the same reference year and geography."],"notes":[],"version":"0.14.0"},{"id":"up.haversine_distance","category":"GIS & spatial analysis","title":"Great-circle distance","equation":"d = 2R asin(\u221aa)","inputs":[{"key":"latitude1Deg","label":"Origin latitude","unit":"deg","default":41.8781},{"key":"longitude1Deg","label":"Origin longitude","unit":"deg","default":-87.6298},{"key":"latitude2Deg","label":"Destination latitude","unit":"deg","default":41.8818},{"key":"longitude2Deg","label":"Destination longitude","unit":"deg","default":-87.6231}],"outputs":{"distanceKm":{"expression":"2*6371*asin(sqrt(sin((latitude2Deg-latitude1Deg)*pi/360)**2+cos(latitude1Deg*pi/180)*cos(latitude2Deg*pi/180)*sin((longitude2Deg-longitude1Deg)*pi/360)**2))","unit":"km"}},"assumptions":["Coordinates use decimal degrees on a spherical Earth approximation."],"notes":[],"version":"0.14.0"},{"id":"up.coordinate_rectangle_area","category":"GIS & spatial analysis","title":"Projected rectangular area","equation":"Area = |x\u2082\u2212x\u2081| \u00d7 |y\u2082\u2212y\u2081|","inputs":[{"key":"x1M","label":"Minimum easting","unit":"m","default":500000},{"key":"y1M","label":"Minimum northing","unit":"m","default":4640000},{"key":"x2M","label":"Maximum easting","unit":"m","default":501200},{"key":"y2M","label":"Maximum northing","unit":"m","default":4640800}],"outputs":{"areaM2":{"expression":"abs(x2M-x1M)*abs(y2M-y1M)","unit":"m^2"},"areaHa":{"expression":"abs(x2M-x1M)*abs(y2M-y1M)/10000","unit":"ha"}},"assumptions":["Coordinates use a projected coordinate system with meter units."],"notes":[],"version":"0.14.0"},{"id":"up.point_density","category":"GIS & spatial analysis","title":"Spatial point density","equation":"Density = points / area","inputs":[{"key":"pointCount","label":"Mapped points","unit":"points","default":850},{"key":"areaKm2","label":"Analysis area","unit":"km^2","default":25}],"outputs":{"pointsPerKm2":{"expression":"pointCount/areaKm2","unit":"points/km^2"}},"assumptions":["Point inventory and area boundary use a common spatial definition."],"notes":[],"version":"0.14.0"},{"id":"up.weighted_suitability","category":"GIS & spatial analysis","title":"Weighted suitability score","equation":"Score = \u03a3(w_i s_i) / \u03a3w_i","inputs":[{"key":"accessScore","label":"Accessibility score","unit":"0-100","default":82},{"key":"accessWeight","label":"Accessibility weight","unit":"1","default":0.35},{"key":"environmentScore","label":"Environmental score","unit":"0-100","default":68},{"key":"environmentWeight","label":"Environmental weight","unit":"1","default":0.25},{"key":"infrastructureScore","label":"Infrastructure score","unit":"0-100","default":76},{"key":"infrastructureWeight","label":"Infrastructure weight","unit":"1","default":0.25},{"key":"equityScore","label":"Equity score","unit":"0-100","default":70},{"key":"equityWeight","label":"Equity weight","unit":"1","default":0.15}],"outputs":{"suitabilityScore":{"expression":"(accessScore*accessWeight+environmentScore*environmentWeight+infrastructureScore*infrastructureWeight+equityScore*equityWeight)/(accessWeight+environmentWeight+infrastructureWeight+equityWeight)","unit":"0-100"}},"assumptions":["Scores are normalized to a common scale and weights are explicit scenario choices."],"notes":[],"version":"0.14.0"},{"id":"up.ndvi","category":"GIS & spatial analysis","title":"Normalized Difference Vegetation Index","equation":"NDVI = (NIR\u2212Red)/(NIR+Red)","inputs":[{"key":"nirReflectance","label":"Near-infrared reflectance","unit":"1","default":0.52},{"key":"redReflectance","label":"Red reflectance","unit":"1","default":0.18}],"outputs":{"ndvi":{"expression":"(nirReflectance-redReflectance)/(nirReflectance+redReflectance)","unit":"-1 to 1"}},"assumptions":["Reflectance values are atmospherically and radiometrically comparable."],"notes":[],"version":"0.14.0"},{"id":"up.ndbi","category":"GIS & spatial analysis","title":"Normalized Difference Built-up Index","equation":"NDBI = (SWIR\u2212NIR)/(SWIR+NIR)","inputs":[{"key":"swirReflectance","label":"Shortwave-infrared reflectance","unit":"1","default":0.42},{"key":"nirReflectance","label":"Near-infrared reflectance","unit":"1","default":0.32}],"outputs":{"ndbi":{"expression":"(swirReflectance-nirReflectance)/(swirReflectance+nirReflectance)","unit":"-1 to 1"}},"assumptions":["Reflectance values use compatible imagery and preprocessing."],"notes":[],"version":"0.14.0"},{"id":"up.spatial_entropy","category":"GIS & spatial analysis","title":"Normalized spatial-distribution entropy","equation":"Entropy = -\u03a3(p ln p)/ln(n)","inputs":[{"key":"zoneShare1","label":"Zone 1 share","unit":"1","default":0.4},{"key":"zoneShare2","label":"Zone 2 share","unit":"1","default":0.35},{"key":"zoneShare3","label":"Zone 3 share","unit":"1","default":0.25}],"outputs":{"normalizedEntropy":{"expression":"-(zoneShare1*log(zoneShare1)+zoneShare2*log(zoneShare2)+zoneShare3*log(zoneShare3))/log(3)","unit":"0-1"},"shareTotal":{"expression":"zoneShare1+zoneShare2+zoneShare3","unit":"1"}},"assumptions":["Zone shares are positive and exhaust the mapped distribution."],"notes":[],"version":"0.14.0"},{"id":"up.location_quotient","category":"GIS & spatial analysis","title":"Location quotient","equation":"LQ = (local sector/local total)/(regional sector/regional total)","inputs":[{"key":"localSector","label":"Local sector employment","unit":"jobs","default":4200},{"key":"localTotal","label":"Local total employment","unit":"jobs","default":18000},{"key":"regionalSector","label":"Regional sector employment","unit":"jobs","default":85000},{"key":"regionalTotal","label":"Regional total employment","unit":"jobs","default":600000}],"outputs":{"locationQuotient":{"expression":"(localSector/localTotal)/(regionalSector/regionalTotal)","unit":"1"}},"assumptions":["Local and regional employment use comparable industry definitions and periods."],"notes":[],"version":"0.14.0"},{"id":"up.school_capacity_gap","category":"Public services & infrastructure","title":"School capacity gap","equation":"Gap = projected enrollment \u2212 available seats","inputs":[{"key":"projectedEnrollment","label":"Projected enrollment","unit":"students","default":6800},{"key":"availableSeats","label":"Available seats","unit":"seats","default":6200}],"outputs":{"seatGap":{"expression":"projectedEnrollment-availableSeats","unit":"seats"},"utilization":{"expression":"projectedEnrollment/availableSeats","unit":"1"}},"assumptions":["Enrollment and capacity represent the same grade bands and planning year."],"notes":[],"version":"0.14.0"},{"id":"up.park_service_coverage","category":"Public services & infrastructure","title":"Park service-area coverage","equation":"Coverage = population within service areas / total population","inputs":[{"key":"servedPopulation","label":"Population within park service areas","unit":"persons","default":76000},{"key":"totalPopulation","label":"Total population","unit":"persons","default":100000}],"outputs":{"coverageFraction":{"expression":"servedPopulation/totalPopulation","unit":"1"},"unservedPopulation":{"expression":"max(0,totalPopulation-servedPopulation)","unit":"persons"}},"assumptions":["Service-area method and population year are consistent."],"notes":[],"version":"0.14.0"},{"id":"up.district_water_demand","category":"Public services & infrastructure","title":"District average water demand","equation":"Q = population \u00d7 unit demand","inputs":[{"key":"population","label":"Population","unit":"persons","default":100000},{"key":"litersPerCapitaDay","label":"Unit water demand","unit":"L/(person*day)","default":220}],"outputs":{"waterDemandM3Day":{"expression":"population*litersPerCapitaDay/1000","unit":"m^3/day"}},"assumptions":["Unit demand represents the selected planning scenario."],"notes":[],"version":"0.14.0"},{"id":"up.wastewater_generation","category":"Public services & infrastructure","title":"District wastewater generation","equation":"Wastewater = water demand \u00d7 return fraction","inputs":[{"key":"waterDemandM3Day","label":"Water demand","unit":"m^3/day","default":22000},{"key":"returnFraction","label":"Wastewater return fraction","unit":"1","default":0.82}],"outputs":{"wastewaterM3Day":{"expression":"waterDemandM3Day*returnFraction","unit":"m^3/day"}},"assumptions":["Return fraction captures consumptive use and system losses."],"notes":[],"version":"0.14.0"},{"id":"up.solid_waste_generation","category":"Public services & infrastructure","title":"Municipal solid-waste generation","equation":"Waste = population \u00d7 unit generation","inputs":[{"key":"population","label":"Population","unit":"persons","default":100000},{"key":"kgPerCapitaDay","label":"Unit waste generation","unit":"kg/(person*day)","default":1.2}],"outputs":{"wasteTonnesPerDay":{"expression":"population*kgPerCapitaDay/1000","unit":"tonnes/day"}},"assumptions":["Unit generation represents the selected waste stream and year."],"notes":[],"version":"0.14.0"},{"id":"up.emergency_response_time","category":"Public services & infrastructure","title":"Emergency response-time estimate","equation":"Time = dispatch delay + distance/speed","inputs":[{"key":"dispatchDelayMin","label":"Dispatch and turnout delay","unit":"min","default":2.5},{"key":"networkDistanceKm","label":"Network travel distance","unit":"km","default":6},{"key":"averageSpeedKmH","label":"Average response speed","unit":"km/h","default":36}],"outputs":{"responseTimeMin":{"expression":"dispatchDelayMin+60*networkDistanceKm/averageSpeedKmH","unit":"min"}},"assumptions":["Average speed represents response conditions on the stated route."],"notes":[],"version":"0.14.0"},{"id":"up.facility_utilization","category":"Public services & infrastructure","title":"Public-facility utilization","equation":"Utilization = demand / capacity","inputs":[{"key":"dailyDemand","label":"Daily service demand","unit":"service units/day","default":840},{"key":"dailyCapacity","label":"Daily service capacity","unit":"service units/day","default":1000}],"outputs":{"utilizationFraction":{"expression":"dailyDemand/dailyCapacity","unit":"1"},"reserveCapacity":{"expression":"dailyCapacity-dailyDemand","unit":"service units/day"}},"assumptions":["Demand and capacity use the same service definition and operating period."],"notes":[],"version":"0.14.0"},{"id":"up.infrastructure_cost_per_capita","category":"Public services & infrastructure","title":"Infrastructure capital cost per capita","equation":"Cost per capita = capital cost / served population","inputs":[{"key":"capitalCost","label":"Infrastructure capital cost","unit":"USD","default":125000000},{"key":"servedPopulation","label":"Served population","unit":"persons","default":100000}],"outputs":{"costPerCapita":{"expression":"capitalCost/servedPopulation","unit":"USD/person"}},"assumptions":["Capital cost and served population use the same project boundary."],"notes":[],"version":"0.14.0"},{"id":"up.urban_heat_island","category":"Resilience, equity & scenarios","title":"Urban heat-island intensity","equation":"UHI = urban temperature \u2212 reference temperature","inputs":[{"key":"urbanTempC","label":"Urban air temperature","unit":"degC","default":34.5},{"key":"referenceTempC","label":"Reference air temperature","unit":"degC","default":31}],"outputs":{"heatIslandIntensityK":{"expression":"urbanTempC-referenceTempC","unit":"K"}},"assumptions":["Urban and reference temperatures are observed at comparable times and heights."],"notes":[],"version":"0.14.0"},{"id":"up.tree_canopy_per_capita","category":"Resilience, equity & scenarios","title":"Tree-canopy area per capita","equation":"Canopy per capita = canopy area / population","inputs":[{"key":"canopyAreaM2","label":"Mapped tree-canopy area","unit":"m^2","default":4800000},{"key":"population","label":"Population","unit":"persons","default":120000}],"outputs":{"canopyM2PerPerson":{"expression":"canopyAreaM2/population","unit":"m^2/person"}},"assumptions":["Canopy map and population use the same geography and reference year."],"notes":[],"version":"0.14.0"},{"id":"up.community_carbon_per_capita","category":"Resilience, equity & scenarios","title":"Community emissions per capita","equation":"Emissions per capita = annual emissions / population","inputs":[{"key":"annualEmissionsTonnes","label":"Annual community emissions","unit":"tCO2e/yr","default":850000},{"key":"population","label":"Population","unit":"persons","default":120000}],"outputs":{"tonnesPerCapitaYear":{"expression":"annualEmissionsTonnes/population","unit":"tCO2e/(person*yr)"}},"assumptions":["Emissions inventory and population share a common geographic boundary."],"notes":[],"version":"0.14.0"},{"id":"up.flood_exposure","category":"Resilience, equity & scenarios","title":"Population flood-exposure rate","equation":"Exposure = exposed population / total population","inputs":[{"key":"exposedPopulation","label":"Population in flood-exposure area","unit":"persons","default":18000},{"key":"totalPopulation","label":"Total population","unit":"persons","default":120000}],"outputs":{"exposureFraction":{"expression":"exposedPopulation/totalPopulation","unit":"1"}},"assumptions":["Exposure area, population data, and hazard scenario use compatible spatial units."],"notes":[],"version":"0.14.0"},{"id":"up.housing_cost_burden","category":"Resilience, equity & scenarios","title":"Housing cost-burden ratio","equation":"Burden = monthly housing cost / monthly household income","inputs":[{"key":"monthlyHousingCost","label":"Monthly housing cost","unit":"USD/month","default":1800},{"key":"monthlyHouseholdIncome","label":"Monthly household income","unit":"USD/month","default":5000}],"outputs":{"costBurdenFraction":{"expression":"monthlyHousingCost/monthlyHouseholdIncome","unit":"1"}},"assumptions":["Housing cost and household income use compatible definitions."],"notes":[],"version":"0.14.0"},{"id":"up.displacement_risk","category":"Resilience, equity & scenarios","title":"Weighted displacement-risk index","equation":"Risk = \u03a3(weight \u00d7 normalized indicator)","inputs":[{"key":"rentIncreaseScore","label":"Rent-increase score","unit":"0-100","default":78},{"key":"rentWeight","label":"Rent-increase weight","unit":"1","default":0.35},{"key":"incomeVulnerabilityScore","label":"Income-vulnerability score","unit":"0-100","default":72},{"key":"incomeWeight","label":"Income-vulnerability weight","unit":"1","default":0.3},{"key":"tenureRiskScore","label":"Tenure-risk score","unit":"0-100","default":65},{"key":"tenureWeight","label":"Tenure-risk weight","unit":"1","default":0.2},{"key":"developmentPressureScore","label":"Development-pressure score","unit":"0-100","default":80},{"key":"developmentWeight","label":"Development-pressure weight","unit":"1","default":0.15}],"outputs":{"displacementRiskScore":{"expression":"(rentIncreaseScore*rentWeight+incomeVulnerabilityScore*incomeWeight+tenureRiskScore*tenureWeight+developmentPressureScore*developmentWeight)/(rentWeight+incomeWeight+tenureWeight+developmentWeight)","unit":"0-100"}},"assumptions":["Indicators are normalized to a common scale and weights are explicit policy assumptions."],"notes":[],"version":"0.14.0"},{"id":"up.population_growth_rate","category":"Resilience, equity & scenarios","title":"Compound annual population growth rate","equation":"CAGR = (P_end/P_start)^(1/n) \u2212 1","inputs":[{"key":"startPopulation","label":"Starting population","unit":"persons","default":100000},{"key":"endPopulation","label":"Ending population","unit":"persons","default":115000},{"key":"years","label":"Elapsed years","unit":"yr","default":10}],"outputs":{"annualGrowthRate":{"expression":"(endPopulation/startPopulation)**(1/years)-1","unit":"1/yr"}},"assumptions":["Population boundaries and definitions remain comparable over the interval."],"notes":[],"version":"0.14.0"},{"id":"up.scenario_score","category":"Resilience, equity & scenarios","title":"Weighted urban scenario score","equation":"Scenario score = \u03a3(weight \u00d7 score) / \u03a3weights","inputs":[{"key":"accessibilityScore","label":"Accessibility score","unit":"0-100","default":80},{"key":"accessibilityWeight","label":"Accessibility weight","unit":"1","default":0.25},{"key":"housingScore","label":"Housing score","unit":"0-100","default":68},{"key":"housingWeight","label":"Housing weight","unit":"1","default":0.25},{"key":"climateScore","label":"Climate score","unit":"0-100","default":74},{"key":"climateWeight","label":"Climate weight","unit":"1","default":0.25},{"key":"fiscalScore","label":"Fiscal score","unit":"0-100","default":72},{"key":"fiscalWeight","label":"Fiscal weight","unit":"1","default":0.25}],"outputs":{"scenarioScore":{"expression":"(accessibilityScore*accessibilityWeight+housingScore*housingWeight+climateScore*climateWeight+fiscalScore*fiscalWeight)/(accessibilityWeight+housingWeight+climateWeight+fiscalWeight)","unit":"0-100"}},"assumptions":["Scores use a common scale and weights represent an explicit planning scenario."],"notes":[],"version":"0.14.0"}]};
const METHODS = new Map(CATALOG.methods.map((item) => [item.id, item]));
const CATEGORIES = [...new Set(CATALOG.methods.map((item) => item.category))];

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

function warningsFor(methodId, inputs, outputs) {
  const warnings = [];

  for (const [key, value] of Object.entries(inputs)) {
    if (
      /population|area|distance|time|trips|opportunities|headway|edges|vertices|count|capacity|demand|cost|income|hours|years|employment|jobs|residents|water|waste|speed|weight/i.test(key)
      && value <= 0
    ) {
      warnings.push(`${key} should normally be greater than zero.`);
    }
  }

  if (
    methodId === 'up.land_use_mix'
    && Math.abs(outputs.shareTotal - 1) > 0.02
  ) {
    warnings.push('Land-use shares do not sum to approximately 1.0.');
  }

  if (
    methodId === 'up.spatial_entropy'
    && Math.abs(outputs.shareTotal - 1) > 0.02
  ) {
    warnings.push('Zone shares do not sum to approximately 1.0.');
  }

  if (
    methodId === 'up.housing_cost_burden'
    && outputs.costBurdenFraction > 0.3
  ) {
    warnings.push(
      'Housing costs exceed 30% of the stated monthly household income.'
    );
  }

  if (
    methodId === 'up.flood_exposure'
    && outputs.exposureFraction > 0.2
  ) {
    warnings.push(
      'More than 20% of the stated population is exposed in this hazard scenario.'
    );
  }

  if (
    methodId === 'up.facility_utilization'
    && outputs.utilizationFraction > 0.9
  ) {
    warnings.push(
      'Facility utilization exceeds 90%; evaluate peak demand and resilience capacity.'
    );
  }

  if (
    methodId === 'up.school_capacity_gap'
    && outputs.seatGap > 0
  ) {
    warnings.push(
      'Projected enrollment exceeds the stated available school capacity.'
    );
  }

  return warnings;
}

function run(methodId, rawInputs) {
  const method = METHODS.get(methodId);

  if (!method) {
    throw new Error(`Unknown urban planning method: ${methodId}`);
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

  const warnings = warningsFor(methodId, inputs, outputs);

  const record = {
    schema: 'sc-lab-urban-planning-spatial-analysis/1.0',
    version: VERSION,
    methodId: method.id,
    methodVersion: VERSION,
    category: method.category,
    title: method.title,
    equation: method.equation,
    inputs,
    inputUnits: Object.fromEntries(
      method.inputs.map((field) => [field.key, field.unit])
    ),
    outputs,
    outputUnits,
    assumptions: method.assumptions,
    notes: method.notes || [],
    warnings,
    validation: {
      status: warnings.length ? 'review' : 'screened',
      benchmarkSuite: 'sc-lab-urban-planning-spatial-benchmarks/1.0',
    },
    audit: {
      createdAt: new Date().toISOString(),
      engine: 'sc-lab-urban-planning-spatial-js',
      release: VERSION,
    },
  };

  record.audit.fingerprint = fingerprint(JSON.stringify(record));
  return record;
}

const BENCHMARKS = [
  ['up.gross_population_density', { population: 1000, grossAreaHa: 20 }, 'personsPerHa', 50],
  ['up.net_residential_density', { dwellingUnits: 600, residentialAreaHa: 20 }, 'dwellingsPerHa', 30],
  ['up.floor_area_ratio', { grossFloorAreaM2: 2000, siteAreaM2: 1000 }, 'floorAreaRatio', 2],
  ['up.development_capacity', { siteAreaM2: 1000, permittedFar: 3, existingFloorAreaM2: 1000 }, 'remainingFloorAreaM2', 2000],
  ['up.open_space_per_capita', { openSpaceM2: 12000, population: 1000 }, 'openSpaceM2PerPerson', 12],
  ['up.weighted_travel_time', { tripsMode1: 2, timeMode1Min: 10, tripsMode2: 1, timeMode2Min: 20, tripsMode3: 1, timeMode3Min: 30 }, 'averageTravelTimeMin', 17.5],
  ['up.cumulative_opportunities', { opportunitiesZone1: 100, timeZone1Min: 10, opportunitiesZone2: 200, timeZone2Min: 40, opportunitiesZone3: 300, timeZone3Min: 20, thresholdMin: 30 }, 'accessibleOpportunities', 400],
  ['up.transit_frequency', { headwayMinutes: 12 }, 'vehiclesPerHour', 5],
  ['up.walkshed_area', { walkingDistanceM: 1000, networkEfficiency: 0.5 }, 'estimatedNetworkWalkshedKm2', Math.PI * 0.5],
  ['up.mode_share', { modeTrips: 250, totalTrips: 1000 }, 'modeShare', 0.25],
  ['up.network_circuity', { networkDistanceKm: 6, straightDistanceKm: 5 }, 'circuity', 1.2],
  ['up.network_beta_index', { edges: 30, vertices: 20 }, 'betaIndex', 1.5],
  ['up.average_node_degree', { edges: 30, vertices: 20 }, 'averageDegree', 3],
  ['up.service_network_coverage', { servedPopulation: 800, totalPopulation: 1000 }, 'coverageFraction', 0.8],
  ['up.coordinate_rectangle_area', { x1M: 0, y1M: 0, x2M: 100, y2M: 50 }, 'areaM2', 5000],
  ['up.point_density', { pointCount: 200, areaKm2: 10 }, 'pointsPerKm2', 20],
  ['up.ndvi', { nirReflectance: 0.6, redReflectance: 0.2 }, 'ndvi', 0.5],
  ['up.location_quotient', { localSector: 20, localTotal: 100, regionalSector: 100, regionalTotal: 1000 }, 'locationQuotient', 2],
  ['up.district_water_demand', { population: 1000, litersPerCapitaDay: 200 }, 'waterDemandM3Day', 200],
  ['up.emergency_response_time', { dispatchDelayMin: 2, networkDistanceKm: 6, averageSpeedKmH: 36 }, 'responseTimeMin', 12],
  ['up.population_growth_rate', { startPopulation: 100, endPopulation: 121, years: 2 }, 'annualGrowthRate', 0.1],
];

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

function render(root) {
  const mounts = root.querySelectorAll('[data-urban-planning-spatial-root]');

  mounts.forEach((mount) => {
    if (mount.dataset.scUrbanRendered === '1') {
      return;
    }

    mount.dataset.scUrbanRendered = '1';

    mount.innerHTML = `
      <div class="sc-up-workbench">
        <div class="sc-up-controls">
          <label>
            Workspace
            <select data-up-category>
              ${CATEGORIES.map(
                (category) => `<option>${escapeHtml(category)}</option>`
              ).join('')}
            </select>
          </label>

          <label>
            Method
            <select data-up-method></select>
          </label>
        </div>

        <article class="sc-up-card">
          <p class="sc-up-kicker" data-up-category-label></p>
          <h4 data-up-title></h4>
          <code data-up-equation></code>
          <p data-up-assumptions></p>

          <div class="sc-up-inputs" data-up-inputs></div>

          <div class="sc-up-actions">
            <button type="button" class="button button-primary" data-up-run>
              Run analysis
            </button>
            <button type="button" class="button" data-up-save>
              Save to project
            </button>
            <button type="button" class="button" data-up-note>
              Add to notebook
            </button>
            <button type="button" class="button" data-up-visualize>
              Visualize
            </button>
          </div>

          <div class="sc-up-status" data-up-status role="status" aria-live="polite">
            Select an urban planning or spatial-systems method.
          </div>

          <div class="sc-up-results" data-up-results></div>

          <details>
            <summary>Analysis contract</summary>
            <pre data-up-json>{}</pre>
          </details>
        </article>

        <section class="sc-up-validation">
          <div>
            <p class="sc-up-kicker">VALIDATION</p>
            <h4>Urban planning and spatial-systems benchmark suite</h4>
            <p>
              Reference cases cover density, accessibility, networks, GIS,
              public services, equity, resilience, and scenario analysis.
            </p>
          </div>

          <button type="button" class="button" data-up-benchmarks>
            Run ${BENCHMARKS.length} benchmarks
          </button>

          <div data-up-benchmark-results></div>
        </section>
      </div>
    `;
  });
}

function init(root = document, projects = Lab.Projects) {
  render(root);

  const mounts = root.querySelectorAll('[data-urban-planning-spatial-root]');

  mounts.forEach((mount) => {
    if (mount.dataset.scUrbanInitialized === '1') {
      return;
    }

    mount.dataset.scUrbanInitialized = '1';

    const categorySelect = mount.querySelector('[data-up-category]');
    const methodSelect = mount.querySelector('[data-up-method]');
    const inputContainer = mount.querySelector('[data-up-inputs]');
    const status = mount.querySelector('[data-up-status]');
    const resultContainer = mount.querySelector('[data-up-results]');
    const jsonTarget = mount.querySelector('[data-up-json]');
    let current = null;

    function renderMethod() {
      const selected = METHODS.get(methodSelect.value);

      if (!selected) {
        return;
      }

      mount.querySelector('[data-up-category-label]').textContent =
        selected.category.toUpperCase();
      mount.querySelector('[data-up-title]').textContent = selected.title;
      mount.querySelector('[data-up-equation]').textContent = selected.equation;
      mount.querySelector('[data-up-assumptions]').textContent =
        selected.assumptions.join(' ');

      inputContainer.innerHTML = selected.inputs.map((input) => `
        <label>
          ${escapeHtml(input.label)}
          <span>${escapeHtml(input.unit)}</span>
          <input
            type="number"
            step="any"
            value="${escapeHtml(input.default)}"
            data-up-field="${escapeHtml(input.key)}"
          >
        </label>
      `).join('');

      current = null;
      resultContainer.innerHTML = '';
      jsonTarget.textContent = '{}';
      status.textContent = 'Inputs ready.';
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

        inputContainer.querySelectorAll('[data-up-field]').forEach((input) => {
          raw[input.dataset.upField] = input.value;
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
    mount.querySelector('[data-up-run]').addEventListener('click', execute);

    mount.querySelector('[data-up-save]').addEventListener('click', () => {
      const record = current || execute();

      if (!record) {
        return;
      }

      if (projects && typeof projects.add === 'function') {
        projects.add(
          'urbanPlanningSpatialAnalyses',
          record,
          `${record.title} saved`
        );

        projects.add(
          'urbanSpatialRecords',
          {
            schema: 'sc-lab-urban-spatial-record/1.0',
            version: VERSION,
            methodId: record.methodId,
            category: record.category,
            title: record.title,
            recordedAt: new Date().toISOString(),
            fingerprint: record.audit.fingerprint,
          },
          `Urban spatial record added: ${record.title}`
        );

        status.textContent = 'Saved to the active project.';
      } else {
        status.textContent =
          'Analysis is ready, but the project storage module is unavailable.';
      }
    });

    mount.querySelector('[data-up-note]').addEventListener('click', () => {
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
              'urban-planning-spatial',
              record.category,
              record.methodId,
            ],
          },
          `Notebook entry added: ${record.title}`
        );

        status.textContent = 'Notebook entry added.';
      }
    });

    mount.querySelector('[data-up-visualize]').addEventListener('click', () => {
      const record = current || execute();

      if (record) {
        document.dispatchEvent(
          new CustomEvent('sc-lab:analysis', { detail: record })
        );
        status.textContent = 'Analysis sent to the visualization layer.';
      }
    });

    mount.querySelector('[data-up-benchmarks]').addEventListener(
      'click',
      () => {
        const rows = runBenchmarks();
        const passed = rows.filter((row) => row.passed).length;

        mount.querySelector('[data-up-benchmark-results]').innerHTML = `
          <p><strong>${passed}/${rows.length}</strong> benchmarks passed.</p>
          <div class="sc-up-benchmark-grid">
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
            'urbanPlanningValidationRecords',
            {
              schema: 'sc-lab-urban-planning-spatial-validation/1.0',
              version: VERSION,
              createdAt: new Date().toISOString(),
              passed,
              total: rows.length,
              results: rows,
            },
            `Urban planning validation: ${passed}/${rows.length}`
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
}

Lab.UrbanPlanningSpatialLab = {
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
