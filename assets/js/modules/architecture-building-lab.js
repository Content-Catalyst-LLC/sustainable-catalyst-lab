(function (global) {
'use strict';

const Lab = global.SCLab = global.SCLab || {};
const VERSION = '0.13.0';
const CATALOG = {"schema":"sc-lab-architecture-building-catalog/1.0","version":"0.13.0","methodCount":48,"categories":["Energy & HVAC","Envelope & thermal","Geometry & program","Solar & daylight","Ventilation & IEQ","Water, carbon & resilience"],"methods":[{"id":"ab.floor_area","category":"Geometry & program","title":"Gross floor area","equation":"A = sum(length \u00d7 width \u00d7 count)","inputs":[{"key":"lengthM","label":"Representative floor length","unit":"m","default":30},{"key":"widthM","label":"Representative floor width","unit":"m","default":20},{"key":"floorCount","label":"Number of floors","unit":"1","default":4}],"outputs":{"grossFloorAreaM2":{"expression":"lengthM*widthM*floorCount","unit":"m^2"}},"assumptions":["Rectangular representative floor plates."],"notes":[],"version":"0.13.0"},{"id":"ab.building_volume","category":"Geometry & program","title":"Conditioned building volume","equation":"V = A \u00d7 h","inputs":[{"key":"grossFloorAreaM2","label":"Gross floor area","unit":"m^2","default":2400},{"key":"averageFloorHeightM","label":"Average floor-to-floor height","unit":"m","default":3.6}],"outputs":{"volumeM3":{"expression":"grossFloorAreaM2*averageFloorHeightM","unit":"m^3"}},"assumptions":["Average floor-to-floor height represents the conditioned volume."],"notes":[],"version":"0.13.0"},{"id":"ab.floor_area_ratio","category":"Geometry & program","title":"Floor area ratio","equation":"FAR = gross floor area / site area","inputs":[{"key":"grossFloorAreaM2","label":"Gross floor area","unit":"m^2","default":8000},{"key":"siteAreaM2","label":"Site area","unit":"m^2","default":4000}],"outputs":{"floorAreaRatio":{"expression":"grossFloorAreaM2/siteAreaM2","unit":"1"}},"assumptions":["Site and floor areas use the same measurement basis."],"notes":[],"version":"0.13.0"},{"id":"ab.site_coverage","category":"Geometry & program","title":"Site coverage","equation":"Coverage = footprint / site area","inputs":[{"key":"footprintM2","label":"Building footprint","unit":"m^2","default":1600},{"key":"siteAreaM2","label":"Site area","unit":"m^2","default":4000}],"outputs":{"siteCoverage":{"expression":"footprintM2/siteAreaM2","unit":"1"}},"assumptions":["Building footprint excludes uncovered site elements."],"notes":[],"version":"0.13.0"},{"id":"ab.surface_volume_ratio","category":"Geometry & program","title":"Envelope surface-to-volume ratio","equation":"S/V = envelope area / volume","inputs":[{"key":"envelopeAreaM2","label":"Exterior envelope area","unit":"m^2","default":4200},{"key":"volumeM3","label":"Conditioned volume","unit":"m^3","default":16000}],"outputs":{"surfaceVolumeRatio":{"expression":"envelopeAreaM2/volumeM3","unit":"1/m"}},"assumptions":["Envelope area and volume use consistent conditioned boundaries."],"notes":[],"version":"0.13.0"},{"id":"ab.window_wall_ratio","category":"Geometry & program","title":"Window-to-wall ratio","equation":"WWR = glazing area / gross wall area","inputs":[{"key":"glazingAreaM2","label":"Glazing area","unit":"m^2","default":900},{"key":"grossWallAreaM2","label":"Gross exterior wall area","unit":"m^2","default":3000}],"outputs":{"windowWallRatio":{"expression":"glazingAreaM2/grossWallAreaM2","unit":"1"}},"assumptions":["Gross wall area includes glazed and opaque wall surfaces."],"notes":[],"version":"0.13.0"},{"id":"ab.occupant_density","category":"Geometry & program","title":"Occupant density","equation":"Density = occupants / floor area","inputs":[{"key":"occupants","label":"Design occupants","unit":"persons","default":320},{"key":"floorAreaM2","label":"Occupied floor area","unit":"m^2","default":4000}],"outputs":{"occupantsPerM2":{"expression":"occupants/floorAreaM2","unit":"persons/m^2"}},"assumptions":["Occupants and area refer to the same design condition."],"notes":[],"version":"0.13.0"},{"id":"ab.form_compactness","category":"Geometry & program","title":"Building form compactness","equation":"Compactness = V^(2/3) / A_envelope","inputs":[{"key":"volumeM3","label":"Conditioned volume","unit":"m^3","default":16000},{"key":"envelopeAreaM2","label":"Exterior envelope area","unit":"m^2","default":4200}],"outputs":{"compactnessIndex":{"expression":"volumeM3**(2/3)/envelopeAreaM2","unit":"1"}},"assumptions":["This is a comparative geometric indicator, not a code metric."],"notes":[],"version":"0.13.0"},{"id":"ab.assembly_r_value","category":"Envelope & thermal","title":"Layered assembly R-value","equation":"R_total = R_si + \u03a3(t/k) + R_se","inputs":[{"key":"insideFilmM2KW","label":"Interior film resistance","unit":"m^2*K/W","default":0.12},{"key":"layer1ThicknessM","label":"Layer 1 thickness","unit":"m","default":0.1},{"key":"layer1ConductivityWmK","label":"Layer 1 conductivity","unit":"W/(m*K)","default":0.04},{"key":"layer2ThicknessM","label":"Layer 2 thickness","unit":"m","default":0.15},{"key":"layer2ConductivityWmK","label":"Layer 2 conductivity","unit":"W/(m*K)","default":0.8},{"key":"outsideFilmM2KW","label":"Exterior film resistance","unit":"m^2*K/W","default":0.03}],"outputs":{"rValueM2KW":{"expression":"insideFilmM2KW+layer1ThicknessM/layer1ConductivityWmK+layer2ThicknessM/layer2ConductivityWmK+outsideFilmM2KW","unit":"m^2*K/W"},"uValueWm2K":{"expression":"1/(insideFilmM2KW+layer1ThicknessM/layer1ConductivityWmK+layer2ThicknessM/layer2ConductivityWmK+outsideFilmM2KW)","unit":"W/(m^2*K)"}},"assumptions":["One-dimensional steady heat flow through homogeneous layers."],"notes":[],"version":"0.13.0"},{"id":"ab.conduction_heat_loss","category":"Envelope & thermal","title":"Envelope conductive heat transfer","equation":"Q = U \u00d7 A \u00d7 \u0394T","inputs":[{"key":"uValueWm2K","label":"Assembly U-value","unit":"W/(m^2*K)","default":0.35},{"key":"areaM2","label":"Assembly area","unit":"m^2","default":2500},{"key":"temperatureDifferenceK","label":"Indoor-outdoor temperature difference","unit":"K","default":25}],"outputs":{"heatTransferW":{"expression":"uValueWm2K*areaM2*temperatureDifferenceK","unit":"W"}},"assumptions":["Steady one-dimensional heat transfer."],"notes":[],"version":"0.13.0"},{"id":"ab.thermal_bridge","category":"Envelope & thermal","title":"Linear thermal-bridge heat transfer","equation":"Q = \u03c8 \u00d7 L \u00d7 \u0394T","inputs":[{"key":"psiWmK","label":"Linear thermal transmittance","unit":"W/(m*K)","default":0.12},{"key":"lengthM","label":"Thermal-bridge length","unit":"m","default":180},{"key":"temperatureDifferenceK","label":"Temperature difference","unit":"K","default":25}],"outputs":{"heatTransferW":{"expression":"psiWmK*lengthM*temperatureDifferenceK","unit":"W"}},"assumptions":["Linear thermal transmittance represents the junction detail."],"notes":[],"version":"0.13.0"},{"id":"ab.parallel_path_u_value","category":"Envelope & thermal","title":"Parallel-path effective U-value","equation":"U_eff = f1U1 + f2U2","inputs":[{"key":"fraction1","label":"Path 1 area fraction","unit":"1","default":0.2},{"key":"uValue1Wm2K","label":"Path 1 U-value","unit":"W/(m^2*K)","default":1.5},{"key":"fraction2","label":"Path 2 area fraction","unit":"1","default":0.8},{"key":"uValue2Wm2K","label":"Path 2 U-value","unit":"W/(m^2*K)","default":0.25}],"outputs":{"effectiveUValueWm2K":{"expression":"fraction1*uValue1Wm2K+fraction2*uValue2Wm2K","unit":"W/(m^2*K)"}},"assumptions":["Area fractions represent parallel heat-flow paths."],"notes":[],"version":"0.13.0"},{"id":"ab.sol_air_temperature","category":"Envelope & thermal","title":"Sol-air temperature","equation":"T_sol-air = T_out + \u03b1I/h_o \u2212 \u03b5\u0394R/h_o","inputs":[{"key":"outdoorTempC","label":"Outdoor air temperature","unit":"degC","default":32},{"key":"solarAbsorptance","label":"Surface solar absorptance","unit":"1","default":0.7},{"key":"solarIrradianceWm2","label":"Incident solar irradiance","unit":"W/m^2","default":700},{"key":"outsideCoefficientWm2K","label":"Exterior heat-transfer coefficient","unit":"W/(m^2*K)","default":18},{"key":"longwaveCorrectionWm2","label":"Net longwave correction","unit":"W/m^2","default":40}],"outputs":{"solAirTempC":{"expression":"outdoorTempC+(solarAbsorptance*solarIrradianceWm2-longwaveCorrectionWm2)/outsideCoefficientWm2K","unit":"degC"}},"assumptions":["Steady exterior surface energy-balance approximation."],"notes":[],"version":"0.13.0"},{"id":"ab.opaque_heat_capacity","category":"Envelope & thermal","title":"Areal heat capacity","equation":"C_A = \u03a3(\u03c1 c_p t)","inputs":[{"key":"density1KgM3","label":"Layer 1 density","unit":"kg/m^3","default":2200},{"key":"specificHeat1JkgK","label":"Layer 1 specific heat","unit":"J/(kg*K)","default":880},{"key":"thickness1M","label":"Layer 1 thickness","unit":"m","default":0.15},{"key":"density2KgM3","label":"Layer 2 density","unit":"kg/m^3","default":35},{"key":"specificHeat2JkgK","label":"Layer 2 specific heat","unit":"J/(kg*K)","default":1400},{"key":"thickness2M","label":"Layer 2 thickness","unit":"m","default":0.1}],"outputs":{"arealHeatCapacityJm2K":{"expression":"density1KgM3*specificHeat1JkgK*thickness1M+density2KgM3*specificHeat2JkgK*thickness2M","unit":"J/(m^2*K)"}},"assumptions":["Layers participate uniformly in the stated heat-capacity inventory."],"notes":[],"version":"0.13.0"},{"id":"ab.surface_temperature","category":"Envelope & thermal","title":"Interior surface temperature","equation":"T_si = T_i \u2212 qR_si","inputs":[{"key":"indoorTempC","label":"Indoor air temperature","unit":"degC","default":21},{"key":"heatFluxWm2","label":"Heat flux toward exterior","unit":"W/m^2","default":10},{"key":"insideFilmM2KW","label":"Interior film resistance","unit":"m^2*K/W","default":0.12}],"outputs":{"surfaceTempC":{"expression":"indoorTempC-heatFluxWm2*insideFilmM2KW","unit":"degC"}},"assumptions":["Positive heat flux is directed from indoors toward outdoors."],"notes":[],"version":"0.13.0"},{"id":"ab.condensation_margin","category":"Envelope & thermal","title":"Surface condensation margin","equation":"Margin = T_surface \u2212 T_dewpoint","inputs":[{"key":"surfaceTempC","label":"Interior surface temperature","unit":"degC","default":16},{"key":"dewPointC","label":"Indoor-air dew point","unit":"degC","default":12}],"outputs":{"condensationMarginK":{"expression":"surfaceTempC-dewPointC","unit":"K"}},"assumptions":["A positive margin indicates the surface is above the stated dew point."],"notes":[],"version":"0.13.0"},{"id":"ab.window_solar_gain","category":"Solar & daylight","title":"Window solar heat gain","equation":"Q_solar = A \u00d7 SHGC \u00d7 I","inputs":[{"key":"glazingAreaM2","label":"Glazing area","unit":"m^2","default":120},{"key":"shgc","label":"Solar heat-gain coefficient","unit":"1","default":0.35},{"key":"irradianceWm2","label":"Incident solar irradiance","unit":"W/m^2","default":600}],"outputs":{"solarGainW":{"expression":"glazingAreaM2*shgc*irradianceWm2","unit":"W"}},"assumptions":["SHGC represents the full glazing system at the stated condition."],"notes":[],"version":"0.13.0"},{"id":"ab.overhang_projection","category":"Solar & daylight","title":"Required horizontal overhang projection","equation":"P = H / tan(\u03b1)","inputs":[{"key":"verticalShadeHeightM","label":"Vertical distance to shade","unit":"m","default":1.8},{"key":"solarAltitudeDeg","label":"Design solar altitude","unit":"deg","default":55}],"outputs":{"projectionM":{"expression":"verticalShadeHeightM/tan(solarAltitudeDeg*pi/180)","unit":"m"}},"assumptions":["Facade is normal to the sun azimuth for the screening condition."],"notes":[],"version":"0.13.0"},{"id":"ab.daylight_factor","category":"Solar & daylight","title":"Daylight factor","equation":"DF = E_inside / E_outside","inputs":[{"key":"insideIlluminanceLux","label":"Indoor daylight illuminance","unit":"lux","default":450},{"key":"outsideIlluminanceLux","label":"Simultaneous exterior illuminance","unit":"lux","default":12000}],"outputs":{"daylightFactor":{"expression":"insideIlluminanceLux/outsideIlluminanceLux","unit":"1"}},"assumptions":["Interior and exterior illuminance are measured simultaneously."],"notes":[],"version":"0.13.0"},{"id":"ab.lumen_method","category":"Solar & daylight","title":"Electric-lighting illuminance","equation":"E = N \u00d7 F \u00d7 CU \u00d7 LLF / A","inputs":[{"key":"luminaireCount","label":"Luminaire count","unit":"1","default":40},{"key":"lumensPerLuminaire","label":"Lumens per luminaire","unit":"lm","default":4200},{"key":"coefficientUtilization","label":"Coefficient of utilization","unit":"1","default":0.65},{"key":"lightLossFactor","label":"Light loss factor","unit":"1","default":0.8},{"key":"floorAreaM2","label":"Illuminated area","unit":"m^2","default":300}],"outputs":{"averageIlluminanceLux":{"expression":"luminaireCount*lumensPerLuminaire*coefficientUtilization*lightLossFactor/floorAreaM2","unit":"lux"}},"assumptions":["Average maintained illuminance using the lumen method."],"notes":[],"version":"0.13.0"},{"id":"ab.lighting_power_density","category":"Solar & daylight","title":"Lighting power density","equation":"LPD = lighting power / floor area","inputs":[{"key":"lightingPowerW","label":"Installed lighting power","unit":"W","default":18000},{"key":"floorAreaM2","label":"Floor area","unit":"m^2","default":3000}],"outputs":{"lightingPowerDensityWm2":{"expression":"lightingPowerW/floorAreaM2","unit":"W/m^2"}},"assumptions":["Installed power and area use the same space boundary."],"notes":[],"version":"0.13.0"},{"id":"ab.daylight_autonomy_proxy","category":"Solar & daylight","title":"Daylight autonomy proxy","equation":"DA = hours above threshold / occupied hours","inputs":[{"key":"hoursAboveThreshold","label":"Occupied hours above target","unit":"h","default":1500},{"key":"occupiedHours","label":"Total occupied hours","unit":"h","default":2500}],"outputs":{"daylightAutonomy":{"expression":"hoursAboveThreshold/occupiedHours","unit":"1"}},"assumptions":["Screening proxy based on counted occupied hours."],"notes":[],"version":"0.13.0"},{"id":"ab.visible_transmittance_gain","category":"Solar & daylight","title":"Transmitted visible luminous flux","equation":"\u03a6_t = \u03a6_i \u00d7 VT","inputs":[{"key":"incidentLumens","label":"Incident luminous flux","unit":"lm","default":50000},{"key":"visibleTransmittance","label":"Visible transmittance","unit":"1","default":0.62}],"outputs":{"transmittedLumens":{"expression":"incidentLumens*visibleTransmittance","unit":"lm"}},"assumptions":["Visible transmittance is representative of the glazing system."],"notes":[],"version":"0.13.0"},{"id":"ab.glare_contrast_ratio","category":"Solar & daylight","title":"Luminance contrast ratio","equation":"C = L_bright / L_background","inputs":[{"key":"brightLuminanceCdm2","label":"Bright-source luminance","unit":"cd/m^2","default":1600},{"key":"backgroundLuminanceCdm2","label":"Background luminance","unit":"cd/m^2","default":200}],"outputs":{"contrastRatio":{"expression":"brightLuminanceCdm2/backgroundLuminanceCdm2","unit":"1"}},"assumptions":["Simple contrast screening; not a complete glare index."],"notes":[],"version":"0.13.0"},{"id":"ab.air_changes","category":"Ventilation & IEQ","title":"Air changes per hour","equation":"ACH = 3600Q / V","inputs":[{"key":"airflowM3S","label":"Outdoor or total airflow","unit":"m^3/s","default":2.4},{"key":"volumeM3","label":"Zone volume","unit":"m^3","default":7200}],"outputs":{"airChangesPerHour":{"expression":"3600*airflowM3S/volumeM3","unit":"1/h"}},"assumptions":["Airflow and volume refer to the same zone."],"notes":[],"version":"0.13.0"},{"id":"ab.ventilation_per_person","category":"Ventilation & IEQ","title":"Outdoor airflow per person","equation":"q_p = Q / N","inputs":[{"key":"outdoorAirflowM3S","label":"Outdoor airflow","unit":"m^3/s","default":1.8},{"key":"occupants","label":"Occupants","unit":"persons","default":180}],"outputs":{"litersPerSecondPerson":{"expression":"1000*outdoorAirflowM3S/occupants","unit":"L/(s*person)"}},"assumptions":["Occupancy and airflow represent the same operating condition."],"notes":[],"version":"0.13.0"},{"id":"ab.infiltration_heat_load","category":"Ventilation & IEQ","title":"Sensible infiltration heat load","equation":"Q = \u03c1 c_p Vdot \u0394T","inputs":[{"key":"airDensityKgM3","label":"Air density","unit":"kg/m^3","default":1.2},{"key":"specificHeatJkgK","label":"Air specific heat","unit":"J/(kg*K)","default":1006},{"key":"infiltrationM3S","label":"Infiltration airflow","unit":"m^3/s","default":0.8},{"key":"temperatureDifferenceK","label":"Indoor-outdoor temperature difference","unit":"K","default":25}],"outputs":{"sensibleLoadW":{"expression":"airDensityKgM3*specificHeatJkgK*infiltrationM3S*temperatureDifferenceK","unit":"W"}},"assumptions":["Steady airflow and sensible-only load."],"notes":[],"version":"0.13.0"},{"id":"ab.steady_co2","category":"Ventilation & IEQ","title":"Steady-state indoor CO\u2082","equation":"C_i = C_o + G/Q","inputs":[{"key":"outdoorCo2Ppm","label":"Outdoor CO2 concentration","unit":"ppm","default":420},{"key":"co2GenerationLps","label":"Occupant CO2 generation","unit":"L/s","default":0.9},{"key":"outdoorAirflowM3S","label":"Outdoor airflow","unit":"m^3/s","default":1.8}],"outputs":{"indoorCo2Ppm":{"expression":"outdoorCo2Ppm+1000*co2GenerationLps/outdoorAirflowM3S","unit":"ppm"}},"assumptions":["Perfect mixing and steady generation and ventilation."],"notes":[],"version":"0.13.0"},{"id":"ab.contaminant_decay","category":"Ventilation & IEQ","title":"Well-mixed contaminant decay","equation":"C(t) = C0 exp(\u2212ACH t)","inputs":[{"key":"initialConcentration","label":"Initial excess concentration","unit":"relative","default":1000},{"key":"airChangesPerHour","label":"Air changes per hour","unit":"1/h","default":2},{"key":"timeHours","label":"Elapsed time","unit":"h","default":1.5}],"outputs":{"remainingConcentration":{"expression":"initialConcentration*exp(-airChangesPerHour*timeHours)","unit":"relative"}},"assumptions":["Well-mixed zone and no continuing source."],"notes":[],"version":"0.13.0"},{"id":"ab.ventilation_effectiveness","category":"Ventilation & IEQ","title":"Air-change effectiveness","equation":"\u03b5 = nominal age / measured age","inputs":[{"key":"nominalAgeMinutes","label":"Nominal air age","unit":"min","default":30},{"key":"measuredAgeMinutes","label":"Measured local mean age","unit":"min","default":25}],"outputs":{"airChangeEffectiveness":{"expression":"nominalAgeMinutes/measuredAgeMinutes","unit":"1"}},"assumptions":["Nominal and measured ages use comparable definitions."],"notes":[],"version":"0.13.0"},{"id":"ab.moisture_generation","category":"Ventilation & IEQ","title":"Occupant moisture generation","equation":"m = N \u00d7 g","inputs":[{"key":"occupants","label":"Occupants","unit":"persons","default":120},{"key":"generationKgPerPersonHour","label":"Moisture generation per person","unit":"kg/(person*h)","default":0.06}],"outputs":{"moistureKgPerHour":{"expression":"occupants*generationKgPerPersonHour","unit":"kg/h"}},"assumptions":["Uniform representative occupant moisture generation."],"notes":[],"version":"0.13.0"},{"id":"ab.thermal_comfort_operating_temp","category":"Ventilation & IEQ","title":"Approximate operative temperature","equation":"T_op = (T_air + T_mrt)/2","inputs":[{"key":"airTempC","label":"Air temperature","unit":"degC","default":23},{"key":"meanRadiantTempC","label":"Mean radiant temperature","unit":"degC","default":25}],"outputs":{"operativeTempC":{"expression":"(airTempC+meanRadiantTempC)/2","unit":"degC"}},"assumptions":["Low air speed and similar radiative and convective coefficients."],"notes":[],"version":"0.13.0"},{"id":"ab.energy_use_intensity","category":"Energy & HVAC","title":"Site energy use intensity","equation":"EUI = annual site energy / floor area","inputs":[{"key":"annualEnergyKWh","label":"Annual site energy","unit":"kWh","default":720000},{"key":"floorAreaM2","label":"Gross floor area","unit":"m^2","default":6000}],"outputs":{"euiKWhM2Year":{"expression":"annualEnergyKWh/floorAreaM2","unit":"kWh/(m^2*yr)"}},"assumptions":["Energy and area use the same building boundary."],"notes":[],"version":"0.13.0"},{"id":"ab.annual_energy","category":"Energy & HVAC","title":"Annual energy from EUI","equation":"E = EUI \u00d7 A","inputs":[{"key":"euiKWhM2Year","label":"Energy use intensity","unit":"kWh/(m^2*yr)","default":120},{"key":"floorAreaM2","label":"Gross floor area","unit":"m^2","default":6000}],"outputs":{"annualEnergyKWh":{"expression":"euiKWhM2Year*floorAreaM2","unit":"kWh/yr"}},"assumptions":["EUI and floor area share the same boundary."],"notes":[],"version":"0.13.0"},{"id":"ab.degree_day_heating","category":"Energy & HVAC","title":"Degree-day conductive heating energy","equation":"E = UA \u00d7 HDD \u00d7 24 / 1000","inputs":[{"key":"uaWK","label":"Building heat-loss coefficient UA","unit":"W/K","default":18000},{"key":"heatingDegreeDaysKDay","label":"Heating degree days","unit":"K*day","default":3200}],"outputs":{"heatingEnergyKWh":{"expression":"uaWK*heatingDegreeDaysKDay*24/1000","unit":"kWh"}},"assumptions":["Linear steady-state degree-day approximation."],"notes":[],"version":"0.13.0"},{"id":"ab.cooling_cop","category":"Energy & HVAC","title":"Cooling electrical demand","equation":"P_electric = Q_cooling / COP","inputs":[{"key":"coolingLoadKW","label":"Cooling load","unit":"kW","default":420},{"key":"cop","label":"Cooling coefficient of performance","unit":"1","default":3.5}],"outputs":{"electricDemandKW":{"expression":"coolingLoadKW/cop","unit":"kW"}},"assumptions":["COP represents the same operating condition as the load."],"notes":[],"version":"0.13.0"},{"id":"ab.boiler_fuel","category":"Energy & HVAC","title":"Boiler fuel input","equation":"Q_fuel = Q_useful / \u03b7","inputs":[{"key":"usefulHeatKW","label":"Useful heating output","unit":"kW","default":500},{"key":"efficiency","label":"Boiler efficiency","unit":"1","default":0.9}],"outputs":{"fuelInputKW":{"expression":"usefulHeatKW/efficiency","unit":"kW"}},"assumptions":["Efficiency is based on a compatible heating-value basis."],"notes":[],"version":"0.13.0"},{"id":"ab.peak_load_density","category":"Energy & HVAC","title":"Peak load density","equation":"q_peak = Q_peak / A","inputs":[{"key":"peakLoadKW","label":"Peak building load","unit":"kW","default":600},{"key":"floorAreaM2","label":"Conditioned floor area","unit":"m^2","default":6000}],"outputs":{"peakLoadWm2":{"expression":"1000*peakLoadKW/floorAreaM2","unit":"W/m^2"}},"assumptions":["Load and area use the same conditioned boundary."],"notes":[],"version":"0.13.0"},{"id":"ab.load_factor","category":"Energy & HVAC","title":"Electrical load factor","equation":"LF = annual energy / (peak demand \u00d7 annual hours)","inputs":[{"key":"annualElectricityKWh","label":"Annual electricity","unit":"kWh","default":900000},{"key":"peakDemandKW","label":"Peak electrical demand","unit":"kW","default":220},{"key":"annualHours","label":"Annual hours","unit":"h","default":8760}],"outputs":{"loadFactor":{"expression":"annualElectricityKWh/(peakDemandKW*annualHours)","unit":"1"}},"assumptions":["Peak demand and annual energy refer to the same meter boundary."],"notes":[],"version":"0.13.0"},{"id":"ab.heat_recovery","category":"Energy & HVAC","title":"Heat-recovery sensible savings","equation":"Q_saved = \u03b5 \u03c1 c_p Vdot \u0394T","inputs":[{"key":"effectiveness","label":"Sensible effectiveness","unit":"1","default":0.72},{"key":"airDensityKgM3","label":"Air density","unit":"kg/m^3","default":1.2},{"key":"specificHeatJkgK","label":"Air specific heat","unit":"J/(kg*K)","default":1006},{"key":"airflowM3S","label":"Outdoor airflow","unit":"m^3/s","default":3},{"key":"temperatureDifferenceK","label":"Temperature difference","unit":"K","default":22}],"outputs":{"recoveredHeatW":{"expression":"effectiveness*airDensityKgM3*specificHeatJkgK*airflowM3S*temperatureDifferenceK","unit":"W"}},"assumptions":["Steady sensible-only heat recovery."],"notes":[],"version":"0.13.0"},{"id":"ab.water_use_intensity","category":"Water, carbon & resilience","title":"Building water use intensity","equation":"WUI = annual water / floor area","inputs":[{"key":"annualWaterM3","label":"Annual potable water","unit":"m^3","default":7200},{"key":"floorAreaM2","label":"Gross floor area","unit":"m^2","default":6000}],"outputs":{"waterUseIntensityM3M2Year":{"expression":"annualWaterM3/floorAreaM2","unit":"m^3/(m^2*yr)"}},"assumptions":["Water and floor area use the same building boundary."],"notes":[],"version":"0.13.0"},{"id":"ab.rainwater_capture","category":"Water, carbon & resilience","title":"Annual rainwater capture","equation":"V = P \u00d7 A \u00d7 C","inputs":[{"key":"annualRainfallM","label":"Annual rainfall depth","unit":"m","default":0.9},{"key":"catchmentAreaM2","label":"Roof catchment area","unit":"m^2","default":1800},{"key":"runoffCoefficient","label":"Collection efficiency","unit":"1","default":0.8}],"outputs":{"capturedWaterM3":{"expression":"annualRainfallM*catchmentAreaM2*runoffCoefficient","unit":"m^3/yr"}},"assumptions":["Annual screening estimate without storage-overflow simulation."],"notes":[],"version":"0.13.0"},{"id":"ab.operational_carbon","category":"Water, carbon & resilience","title":"Annual operational carbon","equation":"CO2e = electricity \u00d7 factor_e + fuel \u00d7 factor_f","inputs":[{"key":"electricityKWh","label":"Annual electricity","unit":"kWh","default":900000},{"key":"electricityFactorKgKWh","label":"Electricity emissions factor","unit":"kgCO2e/kWh","default":0.35},{"key":"fuelKWh","label":"Annual fuel energy","unit":"kWh","default":450000},{"key":"fuelFactorKgKWh","label":"Fuel emissions factor","unit":"kgCO2e/kWh","default":0.2}],"outputs":{"annualEmissionsKgCO2e":{"expression":"electricityKWh*electricityFactorKgKWh+fuelKWh*fuelFactorKgKWh","unit":"kgCO2e/yr"}},"assumptions":["Factors and energy quantities use compatible accounting boundaries."],"notes":[],"version":"0.13.0"},{"id":"ab.embodied_carbon_intensity","category":"Water, carbon & resilience","title":"Embodied carbon intensity","equation":"ECI = embodied carbon / floor area","inputs":[{"key":"embodiedCarbonKgCO2e","label":"Upfront embodied carbon","unit":"kgCO2e","default":4200000},{"key":"floorAreaM2","label":"Gross floor area","unit":"m^2","default":6000}],"outputs":{"embodiedCarbonIntensityKgM2":{"expression":"embodiedCarbonKgCO2e/floorAreaM2","unit":"kgCO2e/m^2"}},"assumptions":["Carbon and area use the same project boundary."],"notes":[],"version":"0.13.0"},{"id":"ab.carbon_payback","category":"Water, carbon & resilience","title":"Carbon payback period","equation":"Payback = added embodied carbon / annual operational savings","inputs":[{"key":"addedEmbodiedKgCO2e","label":"Added embodied carbon","unit":"kgCO2e","default":180000},{"key":"annualSavingsKgCO2e","label":"Annual operational-carbon savings","unit":"kgCO2e/yr","default":45000}],"outputs":{"paybackYears":{"expression":"addedEmbodiedKgCO2e/annualSavingsKgCO2e","unit":"yr"}},"assumptions":["Annual savings remain approximately constant."],"notes":[],"version":"0.13.0"},{"id":"ab.reverberation_time","category":"Water, carbon & resilience","title":"Sabine reverberation time","equation":"RT60 = 0.161 V / A_abs","inputs":[{"key":"roomVolumeM3","label":"Room volume","unit":"m^3","default":750},{"key":"equivalentAbsorptionM2","label":"Equivalent absorption area","unit":"m^2 sabin","default":180}],"outputs":{"reverberationTimeS":{"expression":"0.161*roomVolumeM3/equivalentAbsorptionM2","unit":"s"}},"assumptions":["Diffuse-field Sabine approximation."],"notes":[],"version":"0.13.0"},{"id":"ab.composite_transmission_loss","category":"Water, carbon & resilience","title":"Composite facade transmission loss","equation":"TL = \u221210 log10(\u03a3 A_i \u03c4_i / \u03a3 A_i)","inputs":[{"key":"opaqueAreaM2","label":"Opaque wall area","unit":"m^2","default":800},{"key":"opaqueTlDb","label":"Opaque wall transmission loss","unit":"dB","default":50},{"key":"windowAreaM2","label":"Window area","unit":"m^2","default":200},{"key":"windowTlDb","label":"Window transmission loss","unit":"dB","default":30}],"outputs":{"compositeTransmissionLossDb":{"expression":"-10*log10((opaqueAreaM2*10**(-opaqueTlDb/10)+windowAreaM2*10**(-windowTlDb/10))/(opaqueAreaM2+windowAreaM2))","unit":"dB"}},"assumptions":["Area-weighted diffuse-field transmission screening."],"notes":[],"version":"0.13.0"},{"id":"ab.passive_survivability","category":"Water, carbon & resilience","title":"Passive survivability autonomy","equation":"Autonomy = habitable hours / outage hours","inputs":[{"key":"habitableHours","label":"Hours within stated habitability limits","unit":"h","default":60},{"key":"outageHours","label":"Total outage duration","unit":"h","default":72}],"outputs":{"autonomyFraction":{"expression":"habitableHours/outageHours","unit":"1"}},"assumptions":["Habitability limits must be defined separately for the project."],"notes":[],"version":"0.13.0"}]};
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
      /area|volume|height|length|width|count|occupants|airflow|energy|water|hours|conductivity|resistance|coefficient|efficiency|cop|factor|irradiance|illuminance|luminance|capacity|demand|load|power|temperatureDifference/i.test(key)
      && value <= 0
    ) {
      warnings.push(`${key} should normally be greater than zero.`);
    }
  }

  if (
    methodId === 'ab.condensation_margin'
    && outputs.condensationMarginK < 2
  ) {
    warnings.push(
      'The surface condensation margin is below 2 K and requires hygrothermal review.'
    );
  }

  if (
    methodId === 'ab.window_wall_ratio'
    && outputs.windowWallRatio > 0.5
  ) {
    warnings.push(
      'The window-to-wall ratio exceeds 0.50; evaluate solar, thermal, glare, and envelope tradeoffs.'
    );
  }

  if (
    methodId === 'ab.steady_co2'
    && outputs.indoorCo2Ppm > 1200
  ) {
    warnings.push(
      'The steady-state CO2 screening result exceeds 1200 ppm.'
    );
  }

  if (
    methodId === 'ab.passive_survivability'
    && outputs.autonomyFraction < 0.8
  ) {
    warnings.push(
      'Passive survivability autonomy is below 80% of the stated outage period.'
    );
  }

  return warnings;
}

function run(methodId, rawInputs) {
  const method = METHODS.get(methodId);

  if (!method) {
    throw new Error(`Unknown architecture/building method: ${methodId}`);
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
    schema: 'sc-lab-architecture-building-analysis/1.0',
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
      benchmarkSuite: 'sc-lab-architecture-building-benchmarks/1.0',
    },
    audit: {
      createdAt: new Date().toISOString(),
      engine: 'sc-lab-architecture-building-js',
      release: VERSION,
    },
  };

  record.audit.fingerprint = fingerprint(JSON.stringify(record));
  return record;
}

const BENCHMARKS = [
  ['ab.floor_area', { lengthM: 10, widthM: 5, floorCount: 2 }, 'grossFloorAreaM2', 100],
  ['ab.floor_area_ratio', { grossFloorAreaM2: 2000, siteAreaM2: 1000 }, 'floorAreaRatio', 2],
  ['ab.window_wall_ratio', { glazingAreaM2: 20, grossWallAreaM2: 100 }, 'windowWallRatio', 0.2],
  ['ab.assembly_r_value', { insideFilmM2KW: 0.1, layer1ThicknessM: 0.1, layer1ConductivityWmK: 0.05, layer2ThicknessM: 0.1, layer2ConductivityWmK: 0.1, outsideFilmM2KW: 0.1 }, 'rValueM2KW', 3.2],
  ['ab.conduction_heat_loss', { uValueWm2K: 1, areaM2: 10, temperatureDifferenceK: 5 }, 'heatTransferW', 50],
  ['ab.thermal_bridge', { psiWmK: 0.1, lengthM: 10, temperatureDifferenceK: 20 }, 'heatTransferW', 20],
  ['ab.window_solar_gain', { glazingAreaM2: 10, shgc: 0.5, irradianceWm2: 400 }, 'solarGainW', 2000],
  ['ab.daylight_factor', { insideIlluminanceLux: 500, outsideIlluminanceLux: 10000 }, 'daylightFactor', 0.05],
  ['ab.lighting_power_density', { lightingPowerW: 1000, floorAreaM2: 100 }, 'lightingPowerDensityWm2', 10],
  ['ab.air_changes', { airflowM3S: 1, volumeM3: 3600 }, 'airChangesPerHour', 1],
  ['ab.ventilation_per_person', { outdoorAirflowM3S: 1, occupants: 100 }, 'litersPerSecondPerson', 10],
  ['ab.infiltration_heat_load', { airDensityKgM3: 1.2, specificHeatJkgK: 1000, infiltrationM3S: 1, temperatureDifferenceK: 10 }, 'sensibleLoadW', 12000],
  ['ab.energy_use_intensity', { annualEnergyKWh: 100000, floorAreaM2: 1000 }, 'euiKWhM2Year', 100],
  ['ab.cooling_cop', { coolingLoadKW: 300, cop: 3 }, 'electricDemandKW', 100],
  ['ab.load_factor', { annualElectricityKWh: 438000, peakDemandKW: 100, annualHours: 8760 }, 'loadFactor', 0.5],
  ['ab.rainwater_capture', { annualRainfallM: 1, catchmentAreaM2: 100, runoffCoefficient: 0.8 }, 'capturedWaterM3', 80],
  ['ab.embodied_carbon_intensity', { embodiedCarbonKgCO2e: 100000, floorAreaM2: 1000 }, 'embodiedCarbonIntensityKgM2', 100],
  ['ab.reverberation_time', { roomVolumeM3: 1000, equivalentAbsorptionM2: 161 }, 'reverberationTimeS', 1],
  ['ab.passive_survivability', { habitableHours: 60, outageHours: 72 }, 'autonomyFraction', 5 / 6],
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
  const mount = root.querySelector('[data-architecture-building-root]');

  if (!mount || mount.dataset.scArchitectureRendered === '1') {
    return;
  }

  mount.dataset.scArchitectureRendered = '1';

  mount.innerHTML = `
    <div class="sc-ab-workbench">
      <div class="sc-ab-controls">
        <label>
          Workspace
          <select data-ab-category>
            ${CATEGORIES.map(
              (category) => `<option>${escapeHtml(category)}</option>`
            ).join('')}
          </select>
        </label>
        <label>
          Method
          <select data-ab-method></select>
        </label>
      </div>

      <article class="sc-ab-card">
        <p class="sc-ab-kicker" data-ab-category-label></p>
        <h4 data-ab-title></h4>
        <code data-ab-equation></code>
        <p data-ab-assumptions></p>

        <div class="sc-ab-inputs" data-ab-inputs></div>

        <div class="sc-ab-actions">
          <button type="button" class="button button-primary" data-ab-run>
            Run analysis
          </button>
          <button type="button" class="button" data-ab-save>
            Save to project
          </button>
          <button type="button" class="button" data-ab-note>
            Add to notebook
          </button>
          <button type="button" class="button" data-ab-visualize>
            Visualize
          </button>
        </div>

        <div class="sc-ab-status" data-ab-status role="status" aria-live="polite">
          Select an architecture or building-performance method.
        </div>

        <div class="sc-ab-results" data-ab-results></div>

        <details>
          <summary>Analysis contract</summary>
          <pre data-ab-json>{}</pre>
        </details>
      </article>

      <section class="sc-ab-validation">
        <div>
          <p class="sc-ab-kicker">VALIDATION</p>
          <h4>Architecture and building-performance benchmark suite</h4>
          <p>
            Deterministic reference cases cover geometry, envelope heat transfer,
            daylight, ventilation, HVAC energy, water, carbon, acoustics, and resilience.
          </p>
        </div>
        <button type="button" class="button" data-ab-benchmarks>
          Run ${BENCHMARKS.length} benchmarks
        </button>
        <div data-ab-benchmark-results></div>
      </section>
    </div>
  `;
}

function init(root = document, projects = Lab.Projects) {
  render(root);

  const mounts = root.querySelectorAll('[data-architecture-building-root]');

  mounts.forEach((mount) => {
    if (mount.dataset.scArchitectureInitialized === '1') {
      return;
    }

    mount.dataset.scArchitectureInitialized = '1';

    const categorySelect = mount.querySelector('[data-ab-category]');
    const methodSelect = mount.querySelector('[data-ab-method]');
    const inputContainer = mount.querySelector('[data-ab-inputs]');
    const status = mount.querySelector('[data-ab-status]');
    const resultContainer = mount.querySelector('[data-ab-results]');
    const jsonTarget = mount.querySelector('[data-ab-json]');
    let current = null;

    function renderMethod() {
      const selected = METHODS.get(methodSelect.value);

      if (!selected) {
        return;
      }

      mount.querySelector('[data-ab-category-label]').textContent =
        selected.category.toUpperCase();
      mount.querySelector('[data-ab-title]').textContent = selected.title;
      mount.querySelector('[data-ab-equation]').textContent = selected.equation;
      mount.querySelector('[data-ab-assumptions]').textContent =
        selected.assumptions.join(' ');

      inputContainer.innerHTML = selected.inputs.map((field) => `
        <label>
          ${escapeHtml(field.label)}
          <span>${escapeHtml(field.unit)}</span>
          <input
            type="number"
            step="any"
            value="${escapeHtml(field.default)}"
            data-ab-field="${escapeHtml(field.key)}"
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

        inputContainer.querySelectorAll('[data-ab-field]').forEach((input) => {
          raw[input.dataset.abField] = input.value;
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

    mount.querySelector('[data-ab-run]').addEventListener('click', execute);

    mount.querySelector('[data-ab-save]').addEventListener('click', () => {
      const record = current || execute();

      if (!record) {
        return;
      }

      if (projects && typeof projects.add === 'function') {
        projects.add(
          'architectureBuildingAnalyses',
          record,
          `${record.title} saved`
        );

        projects.add(
          'buildingPerformanceRecords',
          {
            schema: 'sc-lab-building-performance-record/1.0',
            version: VERSION,
            methodId: record.methodId,
            category: record.category,
            title: record.title,
            recordedAt: new Date().toISOString(),
            fingerprint: record.audit.fingerprint,
          },
          `Building-performance record added: ${record.title}`
        );

        status.textContent = 'Saved to the active project.';
      } else {
        status.textContent =
          'Analysis is ready, but the project storage module is unavailable.';
      }
    });

    mount.querySelector('[data-ab-note]').addEventListener('click', () => {
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
              'architecture-building',
              record.category,
              record.methodId,
            ],
          },
          `Notebook entry added: ${record.title}`
        );

        status.textContent = 'Notebook entry added.';
      }
    });

    mount.querySelector('[data-ab-visualize]').addEventListener('click', () => {
      const record = current || execute();

      if (record) {
        document.dispatchEvent(
          new CustomEvent('sc-lab:analysis', { detail: record })
        );
        status.textContent = 'Analysis sent to the visualization layer.';
      }
    });

    mount.querySelector('[data-ab-benchmarks]').addEventListener(
      'click',
      () => {
        const rows = runBenchmarks();
        const passed = rows.filter((row) => row.passed).length;

        mount.querySelector('[data-ab-benchmark-results]').innerHTML = `
          <p><strong>${passed}/${rows.length}</strong> benchmarks passed.</p>
          <div class="sc-ab-benchmark-grid">
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
            'buildingPerformanceValidationRecords',
            {
              schema:
                'sc-lab-architecture-building-validation/1.0',
              version: VERSION,
              createdAt: new Date().toISOString(),
              passed,
              total: rows.length,
              results: rows,
            },
            `Building-performance validation: ${passed}/${rows.length}`
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

Lab.ArchitectureBuildingLab = {
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
