(function (global) {
'use strict';

const Lab = global.SCLab = global.SCLab || {};
const VERSION = "0.15.0";
const CATALOG = {"schema":"sc-lab-civil-infrastructure-catalog/1.0","version":"0.12.0","methodCount":48,"methods":[{"id":"ci.uniform_beam_reactions","category":"Structures","title":"Uniform-load beam reactions","equation":"RA = RB = wL/2","inputs":[{"key":"loadNPerM","label":"Uniform load","unit":"N/m","default":12000},{"key":"spanM","label":"Span","unit":"m","default":6}],"outputs":{"reactionAN":{"expression":"loadNPerM*spanM/2","unit":"N"},"reactionBN":{"expression":"loadNPerM*spanM/2","unit":"N"}},"assumptions":["Simply supported beam with full-span uniform load."],"version":"0.12.0"},{"id":"ci.uniform_beam_moment","category":"Structures","title":"Uniform-load maximum moment","equation":"Mmax = wL^2/8","inputs":[{"key":"loadNPerM","label":"Uniform load","unit":"N/m","default":12000},{"key":"spanM","label":"Span","unit":"m","default":6}],"outputs":{"maxMomentNm":{"expression":"loadNPerM*spanM**2/8","unit":"N*m"}},"assumptions":["Simply supported beam with full-span uniform load."],"version":"0.12.0"},{"id":"ci.section_modulus","category":"Structures","title":"Elastic section modulus","equation":"S = I/c","inputs":[{"key":"inertiaM4","label":"Second moment of area","unit":"m^4","default":0.002},{"key":"extremeDistanceM","label":"Extreme-fiber distance","unit":"m","default":0.3}],"outputs":{"sectionModulusM3":{"expression":"inertiaM4/extremeDistanceM","unit":"m^3"}},"assumptions":["Elastic bending about the stated axis."],"version":"0.12.0"},{"id":"ci.concrete_cylinder_strength","category":"Structures","title":"Concrete cylinder strength","equation":"fc = P/A","inputs":[{"key":"failureLoadN","label":"Failure load","unit":"N","default":900000},{"key":"diameterM","label":"Cylinder diameter","unit":"m","default":0.15}],"outputs":{"strengthPa":{"expression":"failureLoadN/(pi*diameterM**2/4)","unit":"Pa"}},"assumptions":["Uniform compressive stress at failure."],"version":"0.12.0"},{"id":"ci.rebar_area","category":"Structures","title":"Reinforcement area","equation":"As = n*pi*d^2/4","inputs":[{"key":"barCount","label":"Bar count","unit":"1","default":6},{"key":"barDiameterM","label":"Bar diameter","unit":"m","default":0.02}],"outputs":{"steelAreaM2":{"expression":"barCount*pi*barDiameterM**2/4","unit":"m^2"}},"assumptions":["All bars have the same nominal diameter."],"version":"0.12.0"},{"id":"ci.wind_pressure","category":"Structures","title":"Velocity wind pressure","equation":"q = 0.5*rho*V^2*Cd","inputs":[{"key":"airDensityKgM3","label":"Air density","unit":"kg/m^3","default":1.225},{"key":"windSpeedMps","label":"Wind speed","unit":"m/s","default":40},{"key":"dragCoefficient","label":"Pressure coefficient","unit":"1","default":1.2}],"outputs":{"pressurePa":{"expression":"0.5*airDensityKgM3*windSpeedMps**2*dragCoefficient","unit":"Pa"}},"assumptions":["Steady representative wind speed and coefficient."],"version":"0.12.0"},{"id":"ci.seismic_base_shear","category":"Structures","title":"Equivalent lateral base shear","equation":"V = Cs*W","inputs":[{"key":"seismicCoefficient","label":"Seismic response coefficient","unit":"1","default":0.12},{"key":"effectiveWeightN","label":"Effective seismic weight","unit":"N","default":25000000.0}],"outputs":{"baseShearN":{"expression":"seismicCoefficient*effectiveWeightN","unit":"N"}},"assumptions":["Screening-level equivalent lateral force method."],"version":"0.12.0"},{"id":"ci.retaining_wall_overturning","category":"Structures","title":"Retaining-wall overturning ratio","equation":"FS = Mr/Mo","inputs":[{"key":"resistingMomentNm","label":"Resisting moment","unit":"N*m","default":1800000.0},{"key":"overturningMomentNm","label":"Overturning moment","unit":"N*m","default":700000.0}],"outputs":{"factorOfSafety":{"expression":"resistingMomentNm/overturningMomentNm","unit":"1"}},"assumptions":["Moments are taken about the same toe and load combination."],"version":"0.12.0"},{"id":"ci.vertical_effective_stress","category":"Geotechnical","title":"Vertical effective stress","equation":"sigma' = gamma*z - u","inputs":[{"key":"unitWeightNPerM3","label":"Total unit weight","unit":"N/m^3","default":19000},{"key":"depthM","label":"Depth","unit":"m","default":5},{"key":"porePressurePa","label":"Pore-water pressure","unit":"Pa","default":30000}],"outputs":{"effectiveStressPa":{"expression":"unitWeightNPerM3*depthM-porePressurePa","unit":"Pa"}},"assumptions":["One-dimensional overburden screening."],"version":"0.12.0"},{"id":"ci.rankine_active_coefficient","category":"Geotechnical","title":"Rankine active earth coefficient","equation":"Ka = tan^2(45-phi/2)","inputs":[{"key":"frictionAngleDeg","label":"Friction angle","unit":"deg","default":32}],"outputs":{"activeCoefficient":{"expression":"tan((45-frictionAngleDeg/2)*pi/180)**2","unit":"1"}},"assumptions":["Level backfill, vertical wall, no wall friction."],"version":"0.12.0"},{"id":"ci.rankine_passive_coefficient","category":"Geotechnical","title":"Rankine passive earth coefficient","equation":"Kp = tan^2(45+phi/2)","inputs":[{"key":"frictionAngleDeg","label":"Friction angle","unit":"deg","default":32}],"outputs":{"passiveCoefficient":{"expression":"tan((45+frictionAngleDeg/2)*pi/180)**2","unit":"1"}},"assumptions":["Level backfill, vertical wall, no wall friction."],"version":"0.12.0"},{"id":"ci.active_earth_force","category":"Geotechnical","title":"Triangular active earth force","equation":"Pa = 0.5*Ka*gamma*H^2","inputs":[{"key":"activeCoefficient","label":"Active coefficient","unit":"1","default":0.307},{"key":"unitWeightNPerM3","label":"Soil unit weight","unit":"N/m^3","default":18000},{"key":"heightM","label":"Retained height","unit":"m","default":4}],"outputs":{"forceNPerM":{"expression":"0.5*activeCoefficient*unitWeightNPerM3*heightM**2","unit":"N/m"}},"assumptions":["Dry cohesionless soil without surcharge."],"version":"0.12.0"},{"id":"ci.terzaghi_bearing_capacity","category":"Geotechnical","title":"Strip-footing ultimate capacity","equation":"qult = cNc + qNq + 0.5*gamma*B*Ngamma","inputs":[{"key":"cohesionPa","label":"Cohesion","unit":"Pa","default":20000},{"key":"Nc","label":"Nc","unit":"1","default":25.1},{"key":"surchargePa","label":"Surcharge q","unit":"Pa","default":36000},{"key":"Nq","label":"Nq","unit":"1","default":12.7},{"key":"unitWeightNPerM3","label":"Unit weight","unit":"N/m^3","default":18000},{"key":"widthM","label":"Footing width","unit":"m","default":2},{"key":"Ngamma","label":"N-gamma","unit":"1","default":9.7}],"outputs":{"ultimateCapacityPa":{"expression":"cohesionPa*Nc+surchargePa*Nq+0.5*unitWeightNPerM3*widthM*Ngamma","unit":"Pa"}},"assumptions":["Strip footing and supplied bearing-capacity factors."],"version":"0.12.0"},{"id":"ci.consolidation_settlement","category":"Geotechnical","title":"Normally consolidated settlement","equation":"S = Cc*H/(1+e0)*log10((p0+dp)/p0)","inputs":[{"key":"compressionIndex","label":"Compression index","unit":"1","default":0.25},{"key":"layerThicknessM","label":"Layer thickness","unit":"m","default":4},{"key":"initialVoidRatio","label":"Initial void ratio","unit":"1","default":0.9},{"key":"initialEffectivePa","label":"Initial effective stress","unit":"Pa","default":100000},{"key":"stressIncreasePa","label":"Stress increase","unit":"Pa","default":60000}],"outputs":{"settlementM":{"expression":"compressionIndex*layerThicknessM/(1+initialVoidRatio)*log10((initialEffectivePa+stressIncreasePa)/initialEffectivePa)","unit":"m"}},"assumptions":["One-dimensional normally consolidated response."],"version":"0.12.0"},{"id":"ci.slope_factor_of_safety","category":"Geotechnical","title":"Infinite-slope factor of safety","equation":"FS = resistance/driving","inputs":[{"key":"cohesionPa","label":"Cohesion","unit":"Pa","default":8000},{"key":"unitWeightNPerM3","label":"Unit weight","unit":"N/m^3","default":19000},{"key":"depthM","label":"Failure depth","unit":"m","default":2},{"key":"slopeDeg","label":"Slope angle","unit":"deg","default":25},{"key":"porePressurePa","label":"Pore pressure","unit":"Pa","default":5000},{"key":"frictionAngleDeg","label":"Friction angle","unit":"deg","default":30}],"outputs":{"factorOfSafety":{"expression":"(cohesionPa+(unitWeightNPerM3*depthM*cos(slopeDeg*pi/180)**2-porePressurePa)*tan(frictionAngleDeg*pi/180))/(unitWeightNPerM3*depthM*sin(slopeDeg*pi/180)*cos(slopeDeg*pi/180))","unit":"1"}},"assumptions":["Infinite slope with a planar failure surface."],"version":"0.12.0"},{"id":"ci.seepage_discharge","category":"Geotechnical","title":"Darcy seepage discharge","equation":"Q = k*i*A","inputs":[{"key":"hydraulicConductivityMps","label":"Hydraulic conductivity","unit":"m/s","default":2e-05},{"key":"hydraulicGradient","label":"Hydraulic gradient","unit":"1","default":0.3},{"key":"areaM2","label":"Flow area","unit":"m^2","default":40}],"outputs":{"flowM3S":{"expression":"hydraulicConductivityMps*hydraulicGradient*areaM2","unit":"m^3/s"}},"assumptions":["Saturated laminar seepage."],"version":"0.12.0"},{"id":"ci.rational_peak_runoff","category":"Hydrology & drainage","title":"Rational-method peak runoff","equation":"Q = C*i*A","inputs":[{"key":"runoffCoefficient","label":"Runoff coefficient","unit":"1","default":0.65},{"key":"intensityMps","label":"Rainfall intensity","unit":"m/s","default":2.5e-05},{"key":"areaM2","label":"Drainage area","unit":"m^2","default":250000}],"outputs":{"peakFlowM3S":{"expression":"runoffCoefficient*intensityMps*areaM2","unit":"m^3/s"}},"assumptions":["Rainfall duration equals or exceeds time of concentration."],"version":"0.12.0"},{"id":"ci.curve_number_runoff","category":"Hydrology & drainage","title":"SCS curve-number runoff depth","equation":"Q = (P-0.2S)^2/(P+0.8S)","inputs":[{"key":"rainfallMm","label":"Storm rainfall","unit":"mm","default":80},{"key":"curveNumber","label":"Curve number","unit":"1","default":78}],"outputs":{"retentionMm":{"expression":"25400/curveNumber-254","unit":"mm"},"runoffMm":{"expression":"max(0,(rainfallMm-0.2*(25400/curveNumber-254))**2/(rainfallMm+0.8*(25400/curveNumber-254)))","unit":"mm"}},"assumptions":["Standard initial abstraction ratio of 0.2."],"version":"0.12.0"},{"id":"ci.manning_open_channel","category":"Hydrology & drainage","title":"Manning open-channel flow","equation":"Q = (1/n) A R^(2/3) S^(1/2)","inputs":[{"key":"manningN","label":"Manning roughness","unit":"1","default":0.015},{"key":"areaM2","label":"Flow area","unit":"m^2","default":3},{"key":"hydraulicRadiusM","label":"Hydraulic radius","unit":"m","default":0.75},{"key":"slope","label":"Energy slope","unit":"1","default":0.002}],"outputs":{"flowM3S":{"expression":"areaM2*hydraulicRadiusM**(2/3)*sqrt(slope)/manningN","unit":"m^3/s"}},"assumptions":["Uniform steady flow."],"version":"0.12.0"},{"id":"ci.rectangular_channel_radius","category":"Hydrology & drainage","title":"Rectangular-channel hydraulic radius","equation":"R = by/(b+2y)","inputs":[{"key":"widthM","label":"Bottom width","unit":"m","default":4},{"key":"depthM","label":"Flow depth","unit":"m","default":1.2}],"outputs":{"areaM2":{"expression":"widthM*depthM","unit":"m^2"},"hydraulicRadiusM":{"expression":"widthM*depthM/(widthM+2*depthM)","unit":"m"}},"assumptions":["Rectangular prismatic channel."],"version":"0.12.0"},{"id":"ci.broad_crested_weir","category":"Hydrology & drainage","title":"Broad-crested weir flow","equation":"Q = C*b*H^(3/2)","inputs":[{"key":"coefficient","label":"Discharge coefficient","unit":"1","default":1.705},{"key":"widthM","label":"Crest width","unit":"m","default":3},{"key":"headM","label":"Head","unit":"m","default":0.8}],"outputs":{"flowM3S":{"expression":"coefficient*widthM*headM**1.5","unit":"m^3/s"}},"assumptions":["Free modular flow."],"version":"0.12.0"},{"id":"ci.detention_storage","category":"Hydrology & drainage","title":"Detention storage estimate","equation":"V = (Qin-Qout)*t","inputs":[{"key":"inflowM3S","label":"Peak inflow","unit":"m^3/s","default":8},{"key":"outflowM3S","label":"Permitted outflow","unit":"m^3/s","default":3},{"key":"durationS","label":"Critical duration","unit":"s","default":3600}],"outputs":{"storageM3":{"expression":"max(0,(inflowM3S-outflowM3S)*durationS)","unit":"m^3"}},"assumptions":["Rectangular hydrograph screening approximation."],"version":"0.12.0"},{"id":"ci.kirpich_time_concentration","category":"Hydrology & drainage","title":"Kirpich time of concentration","equation":"Tc = 0.01947 L^0.77 S^-0.385","inputs":[{"key":"lengthM","label":"Flow-path length","unit":"m","default":1200},{"key":"slope","label":"Watershed slope","unit":"1","default":0.025}],"outputs":{"timeMinutes":{"expression":"0.01947*lengthM**0.77*slope**(-0.385)","unit":"min"}},"assumptions":["Small rural watershed and SI form."],"version":"0.12.0"},{"id":"ci.return_period_probability","category":"Hydrology & drainage","title":"At-least-one exceedance probability","equation":"P = 1-(1-1/T)^n","inputs":[{"key":"returnPeriodYears","label":"Return period","unit":"yr","default":100},{"key":"serviceYears","label":"Service period","unit":"yr","default":30}],"outputs":{"exceedanceProbability":{"expression":"1-(1-1/returnPeriodYears)**serviceYears","unit":"1"}},"assumptions":["Independent annual exceedance probability."],"version":"0.12.0"},{"id":"ci.stopping_sight_distance","category":"Transportation","title":"Stopping sight distance","equation":"SSD = vt + v^2/(2ga)","inputs":[{"key":"speedMps","label":"Speed","unit":"m/s","default":27.8},{"key":"reactionTimeS","label":"Perception-reaction time","unit":"s","default":2.5},{"key":"decelerationG","label":"Deceleration fraction of g","unit":"1","default":0.35}],"outputs":{"distanceM":{"expression":"speedMps*reactionTimeS+speedMps**2/(2*g*decelerationG)","unit":"m"}},"assumptions":["Level grade and constant deceleration."],"version":"0.12.0"},{"id":"ci.horizontal_curve_radius","category":"Transportation","title":"Horizontal curve radius","equation":"R = v^2/(g(e+f))","inputs":[{"key":"speedMps","label":"Design speed","unit":"m/s","default":25},{"key":"superelevation","label":"Superelevation","unit":"1","default":0.06},{"key":"sideFriction","label":"Side-friction factor","unit":"1","default":0.14}],"outputs":{"radiusM":{"expression":"speedMps**2/(g*(superelevation+sideFriction))","unit":"m"}},"assumptions":["Steady-state lateral equilibrium."],"version":"0.12.0"},{"id":"ci.traffic_flow","category":"Transportation","title":"Fundamental traffic flow","equation":"q = k*v","inputs":[{"key":"densityVehPerKm","label":"Density","unit":"veh/km","default":35},{"key":"speedKmH","label":"Mean speed","unit":"km/h","default":70}],"outputs":{"flowVehPerH":{"expression":"densityVehPerKm*speedKmH","unit":"veh/h"}},"assumptions":["Homogeneous lane flow."],"version":"0.12.0"},{"id":"ci.greenshields_speed","category":"Transportation","title":"Greenshields speed-density","equation":"v = vf(1-k/kj)","inputs":[{"key":"freeFlowKmH","label":"Free-flow speed","unit":"km/h","default":100},{"key":"densityVehPerKm","label":"Density","unit":"veh/km","default":45},{"key":"jamDensityVehPerKm","label":"Jam density","unit":"veh/km","default":160}],"outputs":{"speedKmH":{"expression":"max(0,freeFlowKmH*(1-densityVehPerKm/jamDensityVehPerKm))","unit":"km/h"}},"assumptions":["Linear speed-density relation."],"version":"0.12.0"},{"id":"ci.webster_cycle","category":"Transportation","title":"Webster optimum signal cycle","equation":"C0 = (1.5L+5)/(1-Y)","inputs":[{"key":"lostTimeS","label":"Total lost time","unit":"s","default":16},{"key":"criticalFlowRatio","label":"Critical flow-ratio sum","unit":"1","default":0.72}],"outputs":{"cycleS":{"expression":"(1.5*lostTimeS+5)/(1-criticalFlowRatio)","unit":"s"}},"assumptions":["Undersaturated isolated intersection."],"version":"0.12.0"},{"id":"ci.queue_storage","category":"Transportation","title":"Queue storage length","equation":"L = N*(vehicle length + gap)","inputs":[{"key":"queuedVehicles","label":"Queued vehicles","unit":"veh","default":18},{"key":"vehicleLengthM","label":"Average vehicle length","unit":"m","default":5.5},{"key":"standstillGapM","label":"Standstill gap","unit":"m","default":2}],"outputs":{"storageLengthM":{"expression":"queuedVehicles*(vehicleLengthM+standstillGapM)","unit":"m"}},"assumptions":["Uniform average vehicle length and gap."],"version":"0.12.0"},{"id":"ci.esal_equivalency","category":"Transportation","title":"Equivalent single-axle loads","equation":"ESAL = N*(W/Wstd)^4","inputs":[{"key":"axleApplications","label":"Axle applications","unit":"1","default":200000},{"key":"axleLoadKN","label":"Axle load","unit":"kN","default":100},{"key":"standardLoadKN","label":"Standard axle load","unit":"kN","default":80}],"outputs":{"esal":{"expression":"axleApplications*(axleLoadKN/standardLoadKN)**4","unit":"1"}},"assumptions":["Fourth-power screening law."],"version":"0.12.0"},{"id":"ci.pedestrian_clearance","category":"Transportation","title":"Pedestrian clearance time","equation":"t = L/v","inputs":[{"key":"crossingLengthM","label":"Crossing length","unit":"m","default":24},{"key":"walkingSpeedMps","label":"Walking speed","unit":"m/s","default":1.0},{"key":"startupS","label":"Startup allowance","unit":"s","default":3}],"outputs":{"clearanceTimeS":{"expression":"startupS+crossingLengthM/walkingSpeedMps","unit":"s"}},"assumptions":["Constant walking speed."],"version":"0.12.0"},{"id":"ci.average_water_demand","category":"Water & wastewater","title":"Average water demand","equation":"Q = population*demand/86400","inputs":[{"key":"population","label":"Population","unit":"persons","default":50000},{"key":"demandLPerCapitaDay","label":"Unit demand","unit":"L/(capita*d)","default":240}],"outputs":{"flowM3S":{"expression":"population*demandLPerCapitaDay/1000/86400","unit":"m^3/s"}},"assumptions":["Average-day demand without losses."],"version":"0.12.0"},{"id":"ci.peak_water_demand","category":"Water & wastewater","title":"Peak water demand","equation":"Qpeak = PF*Qavg","inputs":[{"key":"averageFlowM3S","label":"Average flow","unit":"m^3/s","default":0.14},{"key":"peakFactor","label":"Peak factor","unit":"1","default":2.5}],"outputs":{"peakFlowM3S":{"expression":"averageFlowM3S*peakFactor","unit":"m^3/s"}},"assumptions":["Supplied peak factor represents the design condition."],"version":"0.12.0"},{"id":"ci.hazen_williams_headloss","category":"Water & wastewater","title":"Hazen-Williams head loss","equation":"hf = 10.67 L Q^1.852/(C^1.852 D^4.87)","inputs":[{"key":"lengthM","label":"Pipe length","unit":"m","default":1200},{"key":"flowM3S","label":"Flow","unit":"m^3/s","default":0.08},{"key":"coefficientC","label":"Hazen-Williams C","unit":"1","default":130},{"key":"diameterM","label":"Diameter","unit":"m","default":0.3}],"outputs":{"headLossM":{"expression":"10.67*lengthM*flowM3S**1.852/(coefficientC**1.852*diameterM**4.87)","unit":"m"}},"assumptions":["Water-like fluid and SI form."],"version":"0.12.0"},{"id":"ci.chlorine_dose","category":"Water & wastewater","title":"Chlorine mass dose","equation":"m = dose*volume","inputs":[{"key":"doseMgL","label":"Dose","unit":"mg/L","default":2.5},{"key":"volumeM3","label":"Volume treated","unit":"m^3","default":10000}],"outputs":{"massKg":{"expression":"doseMgL*volumeM3/1000","unit":"kg"}},"assumptions":["Uniform applied dose."],"version":"0.12.0"},{"id":"ci.sedimentation_overflow","category":"Water & wastewater","title":"Surface overflow rate","equation":"SOR = Q/A","inputs":[{"key":"flowM3Day","label":"Flow","unit":"m^3/d","default":12000},{"key":"surfaceAreaM2","label":"Basin surface area","unit":"m^2","default":600}],"outputs":{"overflowMPerDay":{"expression":"flowM3Day/surfaceAreaM2","unit":"m/d"}},"assumptions":["Idealized basin surface loading."],"version":"0.12.0"},{"id":"ci.activated_sludge_fm","category":"Water & wastewater","title":"Activated-sludge F/M ratio","equation":"F/M = Q*S0/(V*X)","inputs":[{"key":"flowM3Day","label":"Flow","unit":"m^3/d","default":10000},{"key":"influentBodKgM3","label":"Influent BOD","unit":"kg/m^3","default":0.22},{"key":"aerationVolumeM3","label":"Aeration volume","unit":"m^3","default":5000},{"key":"mlvssKgM3","label":"MLVSS","unit":"kg/m^3","default":3}],"outputs":{"fmPerDay":{"expression":"flowM3Day*influentBodKgM3/(aerationVolumeM3*mlvssKgM3)","unit":"1/d"}},"assumptions":["Steady representative loading."],"version":"0.12.0"},{"id":"ci.solids_retention_time","category":"Water & wastewater","title":"Solids retention time","equation":"SRT = VX/(QwXw+QeXe)","inputs":[{"key":"aerationVolumeM3","label":"Aeration volume","unit":"m^3","default":5000},{"key":"mlssKgM3","label":"MLSS","unit":"kg/m^3","default":3.5},{"key":"wasteFlowM3Day","label":"Waste flow","unit":"m^3/d","default":80},{"key":"wasteSolidsKgM3","label":"Waste solids","unit":"kg/m^3","default":9},{"key":"effluentFlowM3Day","label":"Effluent flow","unit":"m^3/d","default":10000},{"key":"effluentSolidsKgM3","label":"Effluent solids","unit":"kg/m^3","default":0.015}],"outputs":{"srtDays":{"expression":"aerationVolumeM3*mlssKgM3/(wasteFlowM3Day*wasteSolidsKgM3+effluentFlowM3Day*effluentSolidsKgM3)","unit":"d"}},"assumptions":["Steady solids inventory."],"version":"0.12.0"},{"id":"ci.bod_removal","category":"Water & wastewater","title":"BOD removal efficiency","equation":"eta = (Sin-Sout)/Sin","inputs":[{"key":"influentMgL","label":"Influent BOD","unit":"mg/L","default":220},{"key":"effluentMgL","label":"Effluent BOD","unit":"mg/L","default":20}],"outputs":{"removalEfficiency":{"expression":"(influentMgL-effluentMgL)/influentMgL","unit":"1"}},"assumptions":["Comparable sampling bases."],"version":"0.12.0"},{"id":"ci.condition_index","category":"Infrastructure systems","title":"Weighted asset condition index","equation":"CI = sum(w*s)/sum(w)","inputs":[{"key":"structuralScore","label":"Structural score","unit":"0-100","default":72},{"key":"structuralWeight","label":"Structural weight","unit":"1","default":0.5},{"key":"serviceScore","label":"Service score","unit":"0-100","default":84},{"key":"serviceWeight","label":"Service weight","unit":"1","default":0.3},{"key":"safetyScore","label":"Safety score","unit":"0-100","default":90},{"key":"safetyWeight","label":"Safety weight","unit":"1","default":0.2}],"outputs":{"conditionIndex":{"expression":"(structuralScore*structuralWeight+serviceScore*serviceWeight+safetyScore*safetyWeight)/(structuralWeight+serviceWeight+safetyWeight)","unit":"0-100"}},"assumptions":["Scores share a common scale."],"version":"0.12.0"},{"id":"ci.risk_score","category":"Infrastructure systems","title":"Consequence-risk score","equation":"R = probability*consequence","inputs":[{"key":"annualProbability","label":"Annual failure probability","unit":"1/yr","default":0.04},{"key":"consequenceCost","label":"Consequence cost","unit":"USD","default":8000000.0}],"outputs":{"annualizedRisk":{"expression":"annualProbability*consequenceCost","unit":"USD/yr"}},"assumptions":["Same failure mode and basis."],"version":"0.12.0"},{"id":"ci.expected_annual_loss","category":"Infrastructure systems","title":"Expected annual loss","equation":"EAL = sum(p_i*L_i)","inputs":[{"key":"minorProbability","label":"Minor-event probability","unit":"1/yr","default":0.15},{"key":"minorLoss","label":"Minor-event loss","unit":"USD","default":200000},{"key":"majorProbability","label":"Major-event probability","unit":"1/yr","default":0.02},{"key":"majorLoss","label":"Major-event loss","unit":"USD","default":5000000.0}],"outputs":{"expectedAnnualLoss":{"expression":"minorProbability*minorLoss+majorProbability*majorLoss","unit":"USD/yr"}},"assumptions":["Event classes are appropriately partitioned."],"version":"0.12.0"},{"id":"ci.service_reliability","category":"Infrastructure systems","title":"Service reliability","equation":"R = delivered/required","inputs":[{"key":"deliveredService","label":"Delivered service","unit":"unit/d","default":920},{"key":"requiredService","label":"Required service","unit":"unit/d","default":1000}],"outputs":{"reliability":{"expression":"deliveredService/requiredService","unit":"1"}},"assumptions":["Same service basis."],"version":"0.12.0"},{"id":"ci.redundancy_index","category":"Infrastructure systems","title":"Capacity redundancy index","equation":"RI = (total-critical)/critical","inputs":[{"key":"totalCapacity","label":"Total network capacity","unit":"unit","default":1500},{"key":"criticalDemand","label":"Critical demand","unit":"unit","default":1000}],"outputs":{"redundancyIndex":{"expression":"(totalCapacity-criticalDemand)/criticalDemand","unit":"1"}},"assumptions":["Capacity components are substitutable."],"version":"0.12.0"},{"id":"ci.lifecycle_npv","category":"Infrastructure systems","title":"Lifecycle net present cost","equation":"NPC = C0 + annual factor + terminal","inputs":[{"key":"initialCost","label":"Initial cost","unit":"USD","default":5000000.0},{"key":"annualCost","label":"Annual O&M cost","unit":"USD/yr","default":180000},{"key":"discountRate","label":"Discount rate","unit":"1","default":0.04},{"key":"years","label":"Analysis period","unit":"yr","default":30},{"key":"terminalCost","label":"Terminal cost","unit":"USD","default":500000}],"outputs":{"netPresentCost":{"expression":"initialCost+annualCost*(1-(1+discountRate)**(-years))/discountRate+terminalCost/(1+discountRate)**years","unit":"USD"}},"assumptions":["Constant real discount rate."],"version":"0.12.0"},{"id":"ci.embodied_carbon","category":"Infrastructure systems","title":"Embodied carbon inventory","equation":"E = sum(quantity*factor)","inputs":[{"key":"concreteM3","label":"Concrete volume","unit":"m^3","default":1200},{"key":"concreteFactorKgM3","label":"Concrete factor","unit":"kgCO2e/m^3","default":320},{"key":"steelKg","label":"Steel mass","unit":"kg","default":180000},{"key":"steelFactorKgKg","label":"Steel factor","unit":"kgCO2e/kg","default":1.8}],"outputs":{"emissionsKgCO2e":{"expression":"concreteM3*concreteFactorKgM3+steelKg*steelFactorKgKg","unit":"kgCO2e"}},"assumptions":["Compatible lifecycle boundaries."],"version":"0.12.0"},{"id":"ci.recovery_performance","category":"Infrastructure systems","title":"Post-event recovery performance","equation":"Linear recovery service loss","inputs":[{"key":"initialService","label":"Initial retained service","unit":"1","default":0.35},{"key":"finalService","label":"Final service","unit":"1","default":1},{"key":"recoveryDays","label":"Recovery duration","unit":"d","default":45}],"outputs":{"averageService":{"expression":"(initialService+finalService)/2","unit":"1"},"serviceDayLoss":{"expression":"recoveryDays*(1-(initialService+finalService)/2)","unit":"service*d"}},"assumptions":["Linear recovery trajectory."],"version":"0.12.0"}]};
const CATEGORIES = ["Structures","Geotechnical","Hydrology & drainage","Transportation","Water & wastewater","Infrastructure systems"];
const METHODS = new Map(CATALOG.methods.map((item) => [item.id, item]));
const BENCHMARKS = [["ci.uniform_beam_reactions",{"loadNPerM":10,"spanM":4},"reactionAN",20],["ci.uniform_beam_moment",{"loadNPerM":10,"spanM":4},"maxMomentNm",20],["ci.section_modulus",{"inertiaM4":2,"extremeDistanceM":4},"sectionModulusM3",0.5],["ci.wind_pressure",{"airDensityKgM3":1,"windSpeedMps":10,"dragCoefficient":2},"pressurePa",100],["ci.vertical_effective_stress",{"unitWeightNPerM3":20,"depthM":5,"porePressurePa":30},"effectiveStressPa",70],["ci.rational_peak_runoff",{"runoffCoefficient":0.5,"intensityMps":2,"areaM2":10},"peakFlowM3S",10],["ci.average_water_demand",{"population":1000,"demandLPerCapitaDay":200},"flowM3S",0.0023148148148148147],["ci.embodied_carbon",{"concreteM3":10,"concreteFactorKgM3":100,"steelKg":100,"steelFactorKgKg":2},"emissionsKgCO2e",1200]];

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
    schema: "sc-lab-civil-infrastructure-analysis/1.0",
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
      benchmarkSuite: "sc-lab-civil-infrastructure-validation/1.0",
    },
    audit: {
      createdAt: new Date().toISOString(),
      engine: "sc-lab-civil-infrastructure-js-v0150-repair",
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
  const mounts = root.querySelectorAll('[data-civil-infrastructure-root]');

  mounts.forEach((mount) => {
    if (mount.dataset.scCivilRepairVersion === '0.15.0') {
      return;
    }

    mount.dataset.scCivilRepairVersion = '0.15.0';

    mount.innerHTML = `
      <div class="sc-ci-workbench">
        <div class="sc-ci-controls">
          <label>
            Workspace
            <select data-ci-category>
              ${CATEGORIES.map(
                (category) => `<option>${escapeHtml(category)}</option>`
              ).join('')}
            </select>
          </label>

          <label>
            Method
            <select data-ci-method></select>
          </label>
        </div>

        <article class="sc-ci-card">
          <p class="sc-ci-kicker" data-ci-category-label></p>
          <h4 data-ci-title></h4>

          <div class="sc-visible-formula" data-ci-formula-panel>
            <span class="sc-visible-formula-label">Engineering formula</span>
            <code data-ci-equation></code>
          </div>

          <p data-ci-assumptions></p>

          <details class="sc-formula-source" open>
            <summary>Executable formula expressions</summary>
            <div data-ci-expressions></div>
          </details>

          <div class="sc-ci-inputs" data-ci-inputs></div>

          <div class="sc-ci-actions">
            <button type="button" class="button button-primary" data-ci-run>
              Run analysis
            </button>
            <button type="button" class="button" data-ci-save>
              Save to project
            </button>
            <button type="button" class="button" data-ci-note>
              Add to notebook
            </button>
            <button type="button" class="button" data-ci-visualize>
              Visualize
            </button>
          </div>

          <div
            class="sc-ci-status"
            data-ci-status
            role="status"
            aria-live="polite"
          >Select a civil or infrastructure formula.</div>

          <div class="sc-ci-results" data-ci-results></div>

          <details>
            <summary>Analysis contract</summary>
            <pre data-ci-json>{}</pre>
          </details>
        </article>

        <section class="sc-ci-validation">
          <div>
            <p class="sc-ci-kicker">VALIDATION</p>
            <h4>Civil and infrastructure interface verification</h4>
            <p>The repair verifies formula rendering, executable expressions, structural calculations, drainage, demand, and embodied carbon.</p>
          </div>

          <button type="button" class="button" data-ci-benchmarks>
            Run ${BENCHMARKS.length} benchmarks
          </button>

          <div data-ci-benchmark-results></div>
        </section>
      </div>
    `;
  });
}

function init(root = document, projects = Lab.Projects) {
  render(root);

  const mounts = root.querySelectorAll('[data-civil-infrastructure-root]');

  mounts.forEach((mount) => {
    if (
      mount.dataset.scFormulaInterfaceInitialized
      === "CivilInfrastructureLab-0.15.0"
    ) {
      return;
    }

    mount.dataset.scFormulaInterfaceInitialized =
      "CivilInfrastructureLab-0.15.0";

    const categorySelect = mount.querySelector('[data-ci-category]');
    const methodSelect = mount.querySelector('[data-ci-method]');
    const inputContainer = mount.querySelector('[data-ci-inputs]');
    const status = mount.querySelector('[data-ci-status]');
    const resultContainer = mount.querySelector('[data-ci-results]');
    const jsonTarget = mount.querySelector('[data-ci-json]');
    let current = null;

    function renderMethod() {
      const selected = METHODS.get(methodSelect.value);

      if (!selected) {
        return;
      }

      mount.querySelector('[data-ci-category-label]').textContent =
        selected.category.toUpperCase();
      mount.querySelector('[data-ci-title]').textContent =
        selected.title;
      mount.querySelector('[data-ci-equation]').textContent =
        selected.equation || 'Formula not documented.';
      mount.querySelector('[data-ci-assumptions]').textContent =
        (selected.assumptions || []).join(' ');
      mount.querySelector('[data-ci-expressions]').innerHTML =
        expressionMarkup(selected);

      inputContainer.innerHTML = selected.inputs.map((input) => `
        <label>
          ${escapeHtml(input.label)}
          <span>${escapeHtml(input.unit)}</span>
          <input
            type="number"
            step="any"
            value="${escapeHtml(input.default)}"
            data-ci-field="${escapeHtml(input.key)}"
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
          .querySelectorAll('[data-ci-field]')
          .forEach((input) => {
            raw[input.dataset.ciField] = input.value;
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
      .querySelector('[data-ci-run]')
      .addEventListener('click', execute);

    mount
      .querySelector('[data-ci-save]')
      .addEventListener('click', () => {
        const record = current || execute();

        if (!record) {
          return;
        }

        if (projects && typeof projects.add === 'function') {
          projects.add(
            "civilInfrastructureAnalyses",
            record,
            `${record.title} saved`
          );

          projects.add(
            "infrastructureRecords",
            {
              schema: "sc-lab-civil-infrastructure-record/1.0",
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
      .querySelector('[data-ci-note]')
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
              tags: ["civil-infrastructure", "formula-interface-repair"].concat([
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
      .querySelector('[data-ci-visualize]')
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
      .querySelector('[data-ci-benchmarks]')
      .addEventListener('click', () => {
        const rows = runBenchmarks();
        const passed = rows.filter((row) => row.passed).length;

        mount.querySelector(
          '[data-ci-benchmark-results]'
        ).innerHTML = `
          <p><strong>${passed}/${rows.length}</strong> benchmarks passed.</p>
          <div class="sc-ci-benchmark-grid">
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
            "infrastructureValidationRecords",
            {
              schema: "sc-lab-civil-infrastructure-validation/1.0",
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

Lab.CivilInfrastructureLab = {
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
