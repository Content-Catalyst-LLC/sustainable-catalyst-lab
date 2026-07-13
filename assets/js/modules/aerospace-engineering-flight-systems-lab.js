(function (global) {
'use strict';

const Lab = global.SCLab = global.SCLab || {};
const VERSION = '0.18.0';
const CATALOG = {"schema":"sc-lab-aerospace-engineering-flight-systems-catalog/1.0","version":"0.18.0","methodCount":48,"categories":["Aerodynamics & atmosphere","Flight mechanics & performance","Stability, control & handling qualities","Propulsion integration & energy","Structures, loads & aeroelastic screening","Navigation, mission & flight systems"],"methods":[{"id":"af.atmosphere_density_exponential","category":"Aerodynamics & atmosphere","title":"Exponential atmosphere density","equation":"\u03c1 = \u03c1\u2080 exp(\u2212h/H)","inputs":[{"key":"seaLevelDensityKgM3","label":"Reference density","unit":"kg/m^3","default":1.225},{"key":"altitudeM","label":"Geometric altitude","unit":"m","default":3000},{"key":"scaleHeightM","label":"Atmospheric scale height","unit":"m","default":8500}],"outputs":{"densityKgM3":{"expression":"seaLevelDensityKgM3*exp(-altitudeM/scaleHeightM)","unit":"kg/m^3"}},"assumptions":["Isothermal exponential-atmosphere approximation.","Use a standard-atmosphere model for certification or detailed performance work."],"notes":[],"version":"0.18.0"},{"id":"af.dynamic_pressure","category":"Aerodynamics & atmosphere","title":"Dynamic pressure","equation":"q = \u00bd\u03c1V\u00b2","inputs":[{"key":"densityKgM3","label":"Air density","unit":"kg/m^3","default":1.225},{"key":"trueAirspeedMps","label":"True airspeed","unit":"m/s","default":70}],"outputs":{"dynamicPressurePa":{"expression":"0.5*densityKgM3*trueAirspeedMps**2","unit":"Pa"}},"assumptions":["Steady incompressible-flow screening approximation."],"notes":[],"version":"0.18.0"},{"id":"af.lift_force","category":"Aerodynamics & atmosphere","title":"Aerodynamic lift","equation":"L = qSC_L","inputs":[{"key":"dynamicPressurePa","label":"Dynamic pressure","unit":"Pa","default":3000},{"key":"wingAreaM2","label":"Reference wing area","unit":"m^2","default":16.2},{"key":"liftCoefficient","label":"Lift coefficient","unit":"1","default":0.65}],"outputs":{"liftN":{"expression":"dynamicPressurePa*wingAreaM2*liftCoefficient","unit":"N"}},"assumptions":["Coefficient and reference area use the same aerodynamic convention."],"notes":[],"version":"0.18.0"},{"id":"af.drag_force","category":"Aerodynamics & atmosphere","title":"Aerodynamic drag","equation":"D = qSC_D","inputs":[{"key":"dynamicPressurePa","label":"Dynamic pressure","unit":"Pa","default":3000},{"key":"referenceAreaM2","label":"Reference area","unit":"m^2","default":16.2},{"key":"dragCoefficient","label":"Drag coefficient","unit":"1","default":0.038}],"outputs":{"dragN":{"expression":"dynamicPressurePa*referenceAreaM2*dragCoefficient","unit":"N"}},"assumptions":["Coefficient and reference area use the same aerodynamic convention."],"notes":[],"version":"0.18.0"},{"id":"af.wing_aspect_ratio","category":"Aerodynamics & atmosphere","title":"Wing aspect ratio","equation":"AR = b\u00b2/S","inputs":[{"key":"wingSpanM","label":"Wing span","unit":"m","default":11},{"key":"wingAreaM2","label":"Wing area","unit":"m^2","default":16.2}],"outputs":{"aspectRatio":{"expression":"wingSpanM**2/wingAreaM2","unit":"1"}},"assumptions":["Planform reference area and span are consistent."],"notes":[],"version":"0.18.0"},{"id":"af.induced_drag_coefficient","category":"Aerodynamics & atmosphere","title":"Induced drag coefficient","equation":"C_Di = C_L\u00b2/(\u03c0eAR)","inputs":[{"key":"liftCoefficient","label":"Lift coefficient","unit":"1","default":0.65},{"key":"oswaldEfficiency","label":"Oswald efficiency factor","unit":"1","default":0.82},{"key":"aspectRatio","label":"Aspect ratio","unit":"1","default":7.5}],"outputs":{"inducedDragCoefficient":{"expression":"liftCoefficient**2/(pi*oswaldEfficiency*aspectRatio)","unit":"1"}},"assumptions":["Subsonic finite-wing induced-drag approximation."],"notes":[],"version":"0.18.0"},{"id":"af.lift_to_drag_ratio","category":"Aerodynamics & atmosphere","title":"Lift-to-drag ratio","equation":"L/D = C_L/C_D","inputs":[{"key":"liftCoefficient","label":"Lift coefficient","unit":"1","default":0.65},{"key":"dragCoefficient","label":"Drag coefficient","unit":"1","default":0.038}],"outputs":{"liftToDragRatio":{"expression":"liftCoefficient/dragCoefficient","unit":"1"}},"assumptions":["Lift and drag coefficients describe the same flight condition."],"notes":[],"version":"0.18.0"},{"id":"af.reynolds_number","category":"Aerodynamics & atmosphere","title":"Reynolds number","equation":"Re = \u03c1Vc/\u03bc","inputs":[{"key":"densityKgM3","label":"Air density","unit":"kg/m^3","default":1.225},{"key":"trueAirspeedMps","label":"True airspeed","unit":"m/s","default":70},{"key":"referenceLengthM","label":"Reference length","unit":"m","default":1.5},{"key":"dynamicViscosityPaS","label":"Dynamic viscosity","unit":"Pa*s","default":1.79e-05}],"outputs":{"reynoldsNumber":{"expression":"densityKgM3*trueAirspeedMps*referenceLengthM/dynamicViscosityPaS","unit":"1"}},"assumptions":["Fluid properties are evaluated at the stated flight condition."],"notes":[],"version":"0.18.0"},{"id":"af.stall_speed","category":"Flight mechanics & performance","title":"Level-flight stall speed","equation":"V_s = \u221a[2W/(\u03c1SC_Lmax)]","inputs":[{"key":"weightN","label":"Aircraft weight","unit":"N","default":11000},{"key":"densityKgM3","label":"Air density","unit":"kg/m^3","default":1.225},{"key":"wingAreaM2","label":"Wing area","unit":"m^2","default":16.2},{"key":"maximumLiftCoefficient","label":"Maximum lift coefficient","unit":"1","default":1.5}],"outputs":{"stallSpeedMps":{"expression":"sqrt(2*weightN/(densityKgM3*wingAreaM2*maximumLiftCoefficient))","unit":"m/s"}},"assumptions":["Steady, wings-level, one-g stall with the stated maximum lift coefficient."],"notes":[],"version":"0.18.0"},{"id":"af.level_flight_thrust_required","category":"Flight mechanics & performance","title":"Level-flight thrust required","equation":"T_required = D = qSC_D","inputs":[{"key":"dynamicPressurePa","label":"Dynamic pressure","unit":"Pa","default":3000},{"key":"referenceAreaM2","label":"Reference area","unit":"m^2","default":16.2},{"key":"dragCoefficient","label":"Drag coefficient","unit":"1","default":0.038}],"outputs":{"thrustRequiredN":{"expression":"dynamicPressurePa*referenceAreaM2*dragCoefficient","unit":"N"}},"assumptions":["Steady unaccelerated level flight."],"notes":[],"version":"0.18.0"},{"id":"af.power_required","category":"Flight mechanics & performance","title":"Propulsive power required","equation":"P_required = DV","inputs":[{"key":"dragN","label":"Aerodynamic drag","unit":"N","default":1847},{"key":"trueAirspeedMps","label":"True airspeed","unit":"m/s","default":70}],"outputs":{"powerRequiredW":{"expression":"dragN*trueAirspeedMps","unit":"W"}},"assumptions":["Power is evaluated at the aircraft force-velocity plane."],"notes":[],"version":"0.18.0"},{"id":"af.excess_power_climb_rate","category":"Flight mechanics & performance","title":"Rate of climb from excess power","equation":"ROC = (P_available \u2212 P_required)/W","inputs":[{"key":"powerAvailableW","label":"Propulsive power available","unit":"W","default":180000},{"key":"powerRequiredW","label":"Power required","unit":"W","default":130000},{"key":"weightN","label":"Aircraft weight","unit":"N","default":11000}],"outputs":{"rateOfClimbMps":{"expression":"(powerAvailableW-powerRequiredW)/weightN","unit":"m/s"}},"assumptions":["Quasi-steady climb with power expressed at a consistent reference plane."],"notes":[],"version":"0.18.0"},{"id":"af.glide_angle","category":"Flight mechanics & performance","title":"Best-glide flight-path angle","equation":"\u03b3 = arctan[1/(L/D)]","inputs":[{"key":"liftToDragRatio","label":"Lift-to-drag ratio","unit":"1","default":17}],"outputs":{"glideAngleRad":{"expression":"atan(1/liftToDragRatio)","unit":"rad"},"glideAngleDeg":{"expression":"atan(1/liftToDragRatio)*180/pi","unit":"deg"}},"assumptions":["Small-angle, steady, power-off glide approximation."],"notes":[],"version":"0.18.0"},{"id":"af.coordinated_turn_load_factor","category":"Flight mechanics & performance","title":"Coordinated level-turn load factor","equation":"n = 1/cos \u03c6","inputs":[{"key":"bankAngleDeg","label":"Bank angle","unit":"deg","default":45}],"outputs":{"loadFactor":{"expression":"1/cos(bankAngleDeg*pi/180)","unit":"g"}},"assumptions":["Coordinated constant-altitude turn."],"notes":[],"version":"0.18.0"},{"id":"af.coordinated_turn_radius","category":"Flight mechanics & performance","title":"Coordinated level-turn radius","equation":"R = V\u00b2/(g tan \u03c6)","inputs":[{"key":"trueAirspeedMps","label":"True airspeed","unit":"m/s","default":70},{"key":"bankAngleDeg","label":"Bank angle","unit":"deg","default":30}],"outputs":{"turnRadiusM":{"expression":"trueAirspeedMps**2/(g*tan(bankAngleDeg*pi/180))","unit":"m"}},"assumptions":["Coordinated, constant-speed, level turn."],"notes":[],"version":"0.18.0"},{"id":"af.breguet_jet_range","category":"Flight mechanics & performance","title":"Breguet jet range","equation":"R = (V/c_t)(L/D) ln(W_i/W_f)","inputs":[{"key":"trueAirspeedMps","label":"True airspeed","unit":"m/s","default":220},{"key":"thrustSpecificFuelConsumptionPerS","label":"TSFC","unit":"1/s","default":1.6e-05},{"key":"liftToDragRatio","label":"Lift-to-drag ratio","unit":"1","default":16},{"key":"initialWeightN","label":"Initial weight","unit":"N","default":620000},{"key":"finalWeightN","label":"Final weight","unit":"N","default":520000}],"outputs":{"rangeM":{"expression":"(trueAirspeedMps/thrustSpecificFuelConsumptionPerS)*liftToDragRatio*log(initialWeightN/finalWeightN)","unit":"m"},"rangeKm":{"expression":"(trueAirspeedMps/thrustSpecificFuelConsumptionPerS)*liftToDragRatio*log(initialWeightN/finalWeightN)/1000","unit":"km"}},"assumptions":["Constant speed, TSFC, and lift-to-drag ratio over the segment."],"notes":[],"version":"0.18.0"},{"id":"af.static_margin","category":"Stability, control & handling qualities","title":"Longitudinal static margin","equation":"SM = (x_np \u2212 x_cg)/c\u0304","inputs":[{"key":"neutralPointM","label":"Neutral-point station","unit":"m","default":3.25},{"key":"centerOfGravityM","label":"Center-of-gravity station","unit":"m","default":3.05},{"key":"meanAerodynamicChordM","label":"Mean aerodynamic chord","unit":"m","default":1.5}],"outputs":{"staticMarginFraction":{"expression":"(neutralPointM-centerOfGravityM)/meanAerodynamicChordM","unit":"1"}},"assumptions":["Stations use the same datum and positive direction."],"notes":[],"version":"0.18.0"},{"id":"af.horizontal_tail_volume","category":"Stability, control & handling qualities","title":"Horizontal-tail volume coefficient","equation":"V_H = S_H l_H/(S c\u0304)","inputs":[{"key":"tailAreaM2","label":"Horizontal-tail area","unit":"m^2","default":4.2},{"key":"tailArmM","label":"Horizontal-tail moment arm","unit":"m","default":4.5},{"key":"wingAreaM2","label":"Wing reference area","unit":"m^2","default":16.2},{"key":"meanAerodynamicChordM","label":"Mean aerodynamic chord","unit":"m","default":1.5}],"outputs":{"horizontalTailVolume":{"expression":"tailAreaM2*tailArmM/(wingAreaM2*meanAerodynamicChordM)","unit":"1"}},"assumptions":["Tail arm and areas use conventional aerodynamic reference points."],"notes":[],"version":"0.18.0"},{"id":"af.vertical_tail_volume","category":"Stability, control & handling qualities","title":"Vertical-tail volume coefficient","equation":"V_V = S_V l_V/(Sb)","inputs":[{"key":"verticalTailAreaM2","label":"Vertical-tail area","unit":"m^2","default":2.1},{"key":"verticalTailArmM","label":"Vertical-tail moment arm","unit":"m","default":4.2},{"key":"wingAreaM2","label":"Wing reference area","unit":"m^2","default":16.2},{"key":"wingSpanM","label":"Wing span","unit":"m","default":11}],"outputs":{"verticalTailVolume":{"expression":"verticalTailAreaM2*verticalTailArmM/(wingAreaM2*wingSpanM)","unit":"1"}},"assumptions":["Tail arm and areas use conventional aerodynamic reference points."],"notes":[],"version":"0.18.0"},{"id":"af.trim_elevator_deflection","category":"Stability, control & handling qualities","title":"Linearized trim elevator deflection","equation":"\u03b4_e = \u2212(C_m0 + C_m\u03b1 \u03b1)/C_m\u03b4e","inputs":[{"key":"zeroLiftMomentCoefficient","label":"Zero-lift pitching moment","unit":"1","default":-0.04},{"key":"pitchMomentSlopePerRad","label":"Pitching-moment slope","unit":"1/rad","default":-0.75},{"key":"angleOfAttackDeg","label":"Angle of attack","unit":"deg","default":4},{"key":"elevatorControlDerivativePerRad","label":"Elevator control derivative","unit":"1/rad","default":-1.1}],"outputs":{"elevatorDeflectionRad":{"expression":"-(zeroLiftMomentCoefficient+pitchMomentSlopePerRad*angleOfAttackDeg*pi/180)/elevatorControlDerivativePerRad","unit":"rad"},"elevatorDeflectionDeg":{"expression":"-(zeroLiftMomentCoefficient+pitchMomentSlopePerRad*angleOfAttackDeg*pi/180)/elevatorControlDerivativePerRad*180/pi","unit":"deg"}},"assumptions":["Linear small-disturbance pitching-moment model."],"notes":[],"version":"0.18.0"},{"id":"af.short_period_natural_frequency","category":"Stability, control & handling qualities","title":"Short-period natural-frequency screening","equation":"\u03c9_n \u2248 \u221a(\u2212M_\u03b1)","inputs":[{"key":"pitchStiffnessDerivativePerS2","label":"Pitch stiffness derivative M_alpha","unit":"1/s^2","default":-4}],"outputs":{"naturalFrequencyRadS":{"expression":"sqrt(-pitchStiffnessDerivativePerS2)","unit":"rad/s"}},"assumptions":["Reduced-order short-period approximation requiring negative M_alpha."],"notes":[],"version":"0.18.0"},{"id":"af.short_period_damping_ratio","category":"Stability, control & handling qualities","title":"Short-period damping ratio screening","equation":"\u03b6 \u2248 \u2212M_q/(2\u03c9_n)","inputs":[{"key":"pitchDampingDerivativePerS","label":"Pitch damping derivative M_q","unit":"1/s","default":-1.6},{"key":"naturalFrequencyRadS","label":"Natural frequency","unit":"rad/s","default":2}],"outputs":{"dampingRatio":{"expression":"-pitchDampingDerivativePerS/(2*naturalFrequencyRadS)","unit":"1"}},"assumptions":["Reduced-order second-order short-period approximation."],"notes":[],"version":"0.18.0"},{"id":"af.phugoid_period","category":"Stability, control & handling qualities","title":"Phugoid period screening","equation":"T_p \u2248 2\u03c0V/(g\u221a2)","inputs":[{"key":"trimSpeedMps","label":"Trim speed","unit":"m/s","default":70}],"outputs":{"phugoidPeriodS":{"expression":"2*pi*trimSpeedMps/(g*sqrt(2))","unit":"s"}},"assumptions":["Classical lightly damped phugoid approximation."],"notes":[],"version":"0.18.0"},{"id":"af.roll_helix_angle","category":"Stability, control & handling qualities","title":"Nondimensional roll helix angle","equation":"p\u0302 = pb/(2V)","inputs":[{"key":"rollRateRadS","label":"Roll rate","unit":"rad/s","default":0.35},{"key":"wingSpanM","label":"Wing span","unit":"m","default":11},{"key":"trueAirspeedMps","label":"True airspeed","unit":"m/s","default":70}],"outputs":{"rollHelixAngle":{"expression":"rollRateRadS*wingSpanM/(2*trueAirspeedMps)","unit":"1"}},"assumptions":["Body-axis roll rate and reference span use a consistent sign convention."],"notes":[],"version":"0.18.0"},{"id":"af.propulsive_power","category":"Propulsion integration & energy","title":"Useful propulsive power","equation":"P_p = TV","inputs":[{"key":"thrustN","label":"Net propulsive thrust","unit":"N","default":2500},{"key":"flightSpeedMps","label":"Flight speed","unit":"m/s","default":70}],"outputs":{"propulsivePowerW":{"expression":"thrustN*flightSpeedMps","unit":"W"}},"assumptions":["Thrust and speed are evaluated in the same flight condition."],"notes":[],"version":"0.18.0"},{"id":"af.propeller_efficiency","category":"Propulsion integration & energy","title":"Propeller propulsive efficiency","equation":"\u03b7_p = TV/P_shaft","inputs":[{"key":"thrustN","label":"Propeller thrust","unit":"N","default":2200},{"key":"flightSpeedMps","label":"Flight speed","unit":"m/s","default":65},{"key":"shaftPowerW","label":"Shaft power","unit":"W","default":180000}],"outputs":{"propellerEfficiency":{"expression":"thrustN*flightSpeedMps/shaftPowerW","unit":"1"}},"assumptions":["Shaft and propulsive powers use the same time-averaged condition."],"notes":[],"version":"0.18.0"},{"id":"af.thrust_to_weight","category":"Propulsion integration & energy","title":"Thrust-to-weight ratio","equation":"T/W = thrust / weight","inputs":[{"key":"availableThrustN","label":"Available thrust","unit":"N","default":3200},{"key":"weightN","label":"Aircraft weight","unit":"N","default":11000}],"outputs":{"thrustToWeightRatio":{"expression":"availableThrustN/weightN","unit":"1"}},"assumptions":["Thrust and weight refer to the same operating condition."],"notes":[],"version":"0.18.0"},{"id":"af.jet_fuel_flow","category":"Propulsion integration & energy","title":"Jet fuel flow from TSFC","equation":"\u1e41_f = c_t T","inputs":[{"key":"thrustSpecificFuelConsumptionKgNs","label":"Thrust-specific fuel consumption","unit":"kg/(N*s)","default":1.6e-05},{"key":"thrustN","label":"Net thrust","unit":"N","default":40000}],"outputs":{"fuelFlowKgS":{"expression":"thrustSpecificFuelConsumptionKgNs*thrustN","unit":"kg/s"},"fuelFlowKgH":{"expression":"thrustSpecificFuelConsumptionKgNs*thrustN*3600","unit":"kg/h"}},"assumptions":["TSFC and thrust are evaluated at the same altitude and throttle condition."],"notes":[],"version":"0.18.0"},{"id":"af.electric_endurance","category":"Propulsion integration & energy","title":"Battery-electric flight endurance","equation":"E = usable battery energy / electrical power","inputs":[{"key":"batteryEnergyKWh","label":"Installed battery energy","unit":"kWh","default":220},{"key":"usableFraction","label":"Usable battery fraction","unit":"1","default":0.8},{"key":"electricalPowerKW","label":"Electrical power demand","unit":"kW","default":160},{"key":"requiredMissionHours","label":"Required mission duration","unit":"h","default":0.8}],"outputs":{"enduranceHours":{"expression":"batteryEnergyKWh*usableFraction/electricalPowerKW","unit":"h"},"enduranceMargin":{"expression":"(batteryEnergyKWh*usableFraction/electricalPowerKW)/requiredMissionHours","unit":"1"}},"assumptions":["Constant electrical power and declared usable battery fraction."],"notes":[],"version":"0.18.0"},{"id":"af.hybrid_energy_fraction","category":"Propulsion integration & energy","title":"Hybrid-electric energy fraction","equation":"Hybrid fraction = electric mission energy / total mission energy","inputs":[{"key":"electricEnergyKWh","label":"Electric mission energy","unit":"kWh","default":180},{"key":"fuelEnergyKWh","label":"Fuel-derived mission energy","unit":"kWh","default":720}],"outputs":{"electricEnergyFraction":{"expression":"electricEnergyKWh/(electricEnergyKWh+fuelEnergyKWh)","unit":"1"}},"assumptions":["Energy carriers are converted to a common energy basis."],"notes":[],"version":"0.18.0"},{"id":"af.propeller_advance_ratio","category":"Propulsion integration & energy","title":"Propeller advance ratio","equation":"J = V/(nD)","inputs":[{"key":"flightSpeedMps","label":"Flight speed","unit":"m/s","default":65},{"key":"rotationRateRevS","label":"Propeller rotation rate","unit":"rev/s","default":35},{"key":"propellerDiameterM","label":"Propeller diameter","unit":"m","default":2.1}],"outputs":{"advanceRatio":{"expression":"flightSpeedMps/(rotationRateRevS*propellerDiameterM)","unit":"1"}},"assumptions":["Rotation rate is revolutions per second and diameter is the aerodynamic diameter."],"notes":[],"version":"0.18.0"},{"id":"af.propeller_tip_mach","category":"Propulsion integration & energy","title":"Propeller helical tip Mach number","equation":"M_tip = \u221a[(\u03c0Dn)\u00b2 + V\u00b2]/a","inputs":[{"key":"propellerDiameterM","label":"Propeller diameter","unit":"m","default":2.1},{"key":"rotationRateRevS","label":"Rotation rate","unit":"rev/s","default":35},{"key":"flightSpeedMps","label":"Flight speed","unit":"m/s","default":65},{"key":"speedOfSoundMps","label":"Local speed of sound","unit":"m/s","default":340}],"outputs":{"tipMachNumber":{"expression":"sqrt((pi*propellerDiameterM*rotationRateRevS)**2+flightSpeedMps**2)/speedOfSoundMps","unit":"1"}},"assumptions":["Rigid propeller and local speed of sound at the operating condition."],"notes":[],"version":"0.18.0"},{"id":"af.wing_loading","category":"Structures, loads & aeroelastic screening","title":"Wing loading","equation":"W/S = weight / wing area","inputs":[{"key":"weightN","label":"Aircraft weight","unit":"N","default":11000},{"key":"wingAreaM2","label":"Wing area","unit":"m^2","default":16.2}],"outputs":{"wingLoadingPa":{"expression":"weightN/wingAreaM2","unit":"N/m^2"}},"assumptions":["Weight and reference area correspond to the stated configuration."],"notes":[],"version":"0.18.0"},{"id":"af.maneuver_load_factor","category":"Structures, loads & aeroelastic screening","title":"Maneuver load factor","equation":"n = lift / weight","inputs":[{"key":"liftN","label":"Aerodynamic lift","unit":"N","default":27500},{"key":"weightN","label":"Aircraft weight","unit":"N","default":11000}],"outputs":{"loadFactor":{"expression":"liftN/weightN","unit":"g"}},"assumptions":["Quasi-steady maneuver and consistent force reference."],"notes":[],"version":"0.18.0"},{"id":"af.limit_load_force","category":"Structures, loads & aeroelastic screening","title":"Design limit load","equation":"L_limit = n_limit W","inputs":[{"key":"limitLoadFactor","label":"Limit load factor","unit":"g","default":3.8},{"key":"weightN","label":"Aircraft weight","unit":"N","default":11000}],"outputs":{"limitLoadN":{"expression":"limitLoadFactor*weightN","unit":"N"}},"assumptions":["Limit factor is selected from the applicable design basis."],"notes":[],"version":"0.18.0"},{"id":"af.ultimate_load_force","category":"Structures, loads & aeroelastic screening","title":"Design ultimate load","equation":"L_ultimate = safety factor \u00d7 L_limit","inputs":[{"key":"limitLoadN","label":"Limit load","unit":"N","default":41800},{"key":"ultimateSafetyFactor","label":"Ultimate safety factor","unit":"1","default":1.5}],"outputs":{"ultimateLoadN":{"expression":"limitLoadN*ultimateSafetyFactor","unit":"N"}},"assumptions":["Safety factor is selected from the applicable design standard."],"notes":[],"version":"0.18.0"},{"id":"af.bending_stress","category":"Structures, loads & aeroelastic screening","title":"Elastic bending stress","equation":"\u03c3 = Mc/I","inputs":[{"key":"bendingMomentNm","label":"Bending moment","unit":"N*m","default":240000},{"key":"extremeFiberDistanceM","label":"Extreme-fiber distance","unit":"m","default":0.18},{"key":"secondMomentAreaM4","label":"Second moment of area","unit":"m^4","default":0.00042}],"outputs":{"bendingStressPa":{"expression":"bendingMomentNm*extremeFiberDistanceM/secondMomentAreaM4","unit":"Pa"}},"assumptions":["Linear-elastic beam theory and valid section properties."],"notes":[],"version":"0.18.0"},{"id":"af.torsional_shear_stress","category":"Structures, loads & aeroelastic screening","title":"Circular-section torsional shear stress","equation":"\u03c4 = Tr/J","inputs":[{"key":"torqueNm","label":"Applied torque","unit":"N*m","default":12000},{"key":"outerRadiusM","label":"Outer radius","unit":"m","default":0.08},{"key":"polarMomentM4","label":"Polar second moment","unit":"m^4","default":1.2e-05}],"outputs":{"torsionalShearStressPa":{"expression":"torqueNm*outerRadiusM/polarMomentM4","unit":"Pa"}},"assumptions":["Saint-Venant torsion for a compatible section."],"notes":[],"version":"0.18.0"},{"id":"af.simply_supported_beam_deflection","category":"Structures, loads & aeroelastic screening","title":"Midspan point-load beam deflection","equation":"\u03b4_max = PL\u00b3/(48EI)","inputs":[{"key":"pointLoadN","label":"Midspan point load","unit":"N","default":5000},{"key":"spanM","label":"Beam span","unit":"m","default":3},{"key":"elasticModulusPa","label":"Elastic modulus","unit":"Pa","default":70000000000},{"key":"secondMomentAreaM4","label":"Second moment of area","unit":"m^4","default":4e-06}],"outputs":{"maximumDeflectionM":{"expression":"pointLoadN*spanM**3/(48*elasticModulusPa*secondMomentAreaM4)","unit":"m"}},"assumptions":["Euler\u2013Bernoulli beam, small deflection, central point load."],"notes":[],"version":"0.18.0"},{"id":"af.torsional_divergence_speed","category":"Structures, loads & aeroelastic screening","title":"Wing torsional-divergence screening speed","equation":"q_div = K_\u03b8/(SeC_L\u03b1), V_div = \u221a(2q_div/\u03c1)","inputs":[{"key":"torsionalStiffnessNmRad","label":"Equivalent torsional stiffness","unit":"N*m/rad","default":180000},{"key":"wingAreaM2","label":"Wing reference area","unit":"m^2","default":16.2},{"key":"aerodynamicMomentArmM","label":"Elastic-axis aerodynamic arm","unit":"m","default":0.12},{"key":"liftCurveSlopePerRad","label":"Lift-curve slope","unit":"1/rad","default":5.7},{"key":"densityKgM3","label":"Air density","unit":"kg/m^3","default":1.225},{"key":"referenceFlightSpeedMps","label":"Reference flight speed","unit":"m/s","default":70}],"outputs":{"divergenceDynamicPressurePa":{"expression":"torsionalStiffnessNmRad/(wingAreaM2*aerodynamicMomentArmM*liftCurveSlopePerRad)","unit":"Pa"},"divergenceSpeedMps":{"expression":"sqrt(2*(torsionalStiffnessNmRad/(wingAreaM2*aerodynamicMomentArmM*liftCurveSlopePerRad))/densityKgM3)","unit":"m/s"},"divergenceSpeedMargin":{"expression":"sqrt(2*(torsionalStiffnessNmRad/(wingAreaM2*aerodynamicMomentArmM*liftCurveSlopePerRad))/densityKgM3)/referenceFlightSpeedMps","unit":"1"}},"assumptions":["Single-degree-of-freedom static aeroelastic screening model.","Not a substitute for finite-element or certified aeroelastic analysis."],"notes":[],"version":"0.18.0"},{"id":"af.wind_triangle_ground_speed","category":"Navigation, mission & flight systems","title":"Wind-triangle ground speed","equation":"V_g = \u221a[(V_a cos \u03c8 + W_x)\u00b2 + (V_a sin \u03c8 + W_y)\u00b2]","inputs":[{"key":"trueAirspeedMps","label":"True airspeed","unit":"m/s","default":70},{"key":"headingDeg","label":"Aircraft heading","unit":"deg","default":90},{"key":"windEastMps","label":"East wind component","unit":"m/s","default":8},{"key":"windNorthMps","label":"North wind component","unit":"m/s","default":-4}],"outputs":{"groundSpeedMps":{"expression":"sqrt((trueAirspeedMps*cos(headingDeg*pi/180)+windEastMps)**2+(trueAirspeedMps*sin(headingDeg*pi/180)+windNorthMps)**2)","unit":"m/s"}},"assumptions":["Planar wind triangle with east and north vector components."],"notes":[],"version":"0.18.0"},{"id":"af.wind_correction_angle","category":"Navigation, mission & flight systems","title":"Wind-correction angle","equation":"WCA = arcsin(W_cross/V_a)","inputs":[{"key":"crosswindMps","label":"Crosswind component","unit":"m/s","default":8},{"key":"trueAirspeedMps","label":"True airspeed","unit":"m/s","default":70}],"outputs":{"windCorrectionAngleRad":{"expression":"asin(crosswindMps/trueAirspeedMps)","unit":"rad"},"windCorrectionAngleDeg":{"expression":"asin(crosswindMps/trueAirspeedMps)*180/pi","unit":"deg"}},"assumptions":["Crosswind magnitude is less than true airspeed."],"notes":[],"version":"0.18.0"},{"id":"af.great_circle_distance","category":"Navigation, mission & flight systems","title":"Great-circle distance","equation":"d = R arccos[sin \u03c6\u2081 sin \u03c6\u2082 + cos \u03c6\u2081 cos \u03c6\u2082 cos(\u0394\u03bb)]","inputs":[{"key":"latitude1Deg","label":"Start latitude","unit":"deg","default":41.8781},{"key":"longitude1Deg","label":"Start longitude","unit":"deg","default":-87.6298},{"key":"latitude2Deg","label":"End latitude","unit":"deg","default":40.7128},{"key":"longitude2Deg","label":"End longitude","unit":"deg","default":-74.006},{"key":"earthRadiusKm","label":"Earth radius","unit":"km","default":6371}],"outputs":{"greatCircleDistanceKm":{"expression":"earthRadiusKm*acos(sin(latitude1Deg*pi/180)*sin(latitude2Deg*pi/180)+cos(latitude1Deg*pi/180)*cos(latitude2Deg*pi/180)*cos((longitude2Deg-longitude1Deg)*pi/180))","unit":"km"}},"assumptions":["Spherical Earth approximation."],"notes":[],"version":"0.18.0"},{"id":"af.time_to_waypoint","category":"Navigation, mission & flight systems","title":"Time to waypoint","equation":"t = distance / ground speed","inputs":[{"key":"distanceKm","label":"Distance to waypoint","unit":"km","default":250},{"key":"groundSpeedMps","label":"Ground speed","unit":"m/s","default":70}],"outputs":{"timeSeconds":{"expression":"distanceKm*1000/groundSpeedMps","unit":"s"},"timeHours":{"expression":"distanceKm*1000/groundSpeedMps/3600","unit":"h"}},"assumptions":["Ground speed remains constant over the segment."],"notes":[],"version":"0.18.0"},{"id":"af.mission_fuel_fraction","category":"Navigation, mission & flight systems","title":"Mission fuel fraction","equation":"Fuel fraction = (W_i \u2212 W_f)/W_i","inputs":[{"key":"initialWeightN","label":"Initial mission weight","unit":"N","default":620000},{"key":"finalWeightN","label":"Final mission weight","unit":"N","default":520000}],"outputs":{"fuelWeightFraction":{"expression":"(initialWeightN-finalWeightN)/initialWeightN","unit":"1"}},"assumptions":["Weight reduction is attributed to consumed fuel for this screening calculation."],"notes":[],"version":"0.18.0"},{"id":"af.payload_fraction","category":"Navigation, mission & flight systems","title":"Payload fraction","equation":"Payload fraction = payload weight / takeoff weight","inputs":[{"key":"payloadWeightN","label":"Payload weight","unit":"N","default":110000},{"key":"takeoffWeightN","label":"Takeoff weight","unit":"N","default":620000}],"outputs":{"payloadFraction":{"expression":"payloadWeightN/takeoffWeightN","unit":"1"}},"assumptions":["Payload and takeoff weights use the same loading definition."],"notes":[],"version":"0.18.0"},{"id":"af.series_system_reliability","category":"Navigation, mission & flight systems","title":"Series flight-system reliability","equation":"R_series = R\u2081R\u2082R\u2083R\u2084","inputs":[{"key":"reliability1","label":"Subsystem 1 reliability","unit":"0-1","default":0.995},{"key":"reliability2","label":"Subsystem 2 reliability","unit":"0-1","default":0.992},{"key":"reliability3","label":"Subsystem 3 reliability","unit":"0-1","default":0.998},{"key":"reliability4","label":"Subsystem 4 reliability","unit":"0-1","default":0.997}],"outputs":{"seriesReliability":{"expression":"reliability1*reliability2*reliability3*reliability4","unit":"0-1"}},"assumptions":["Independent subsystem failures and all subsystems required for success."],"notes":[],"version":"0.18.0"},{"id":"af.dual_channel_reliability","category":"Navigation, mission & flight systems","title":"Independent dual-channel reliability","equation":"R_parallel = 1 \u2212 (1\u2212R\u2081)(1\u2212R\u2082)","inputs":[{"key":"channel1Reliability","label":"Channel 1 reliability","unit":"0-1","default":0.98},{"key":"channel2Reliability","label":"Channel 2 reliability","unit":"0-1","default":0.98}],"outputs":{"dualChannelReliability":{"expression":"1-(1-channel1Reliability)*(1-channel2Reliability)","unit":"0-1"}},"assumptions":["Independent channels and successful operation when either channel remains available."],"notes":[],"version":"0.18.0"}]};
const METHODS = new Map(CATALOG.methods.map((item) => [item.id, item]));
const CATEGORIES = [...new Set(CATALOG.methods.map((item) => item.category))];
const BENCHMARKS = [["af.atmosphere_density_exponential",{"seaLevelDensityKgM3":1.2,"altitudeM":0,"scaleHeightM":8500},"densityKgM3",1.2],["af.dynamic_pressure",{"densityKgM3":1,"trueAirspeedMps":10},"dynamicPressurePa",50],["af.lift_force",{"dynamicPressurePa":100,"wingAreaM2":10,"liftCoefficient":0.5},"liftN",500],["af.drag_force",{"dynamicPressurePa":100,"referenceAreaM2":10,"dragCoefficient":0.1},"dragN",100],["af.wing_aspect_ratio",{"wingSpanM":10,"wingAreaM2":20},"aspectRatio",5],["af.induced_drag_coefficient",{"liftCoefficient":1,"oswaldEfficiency":1,"aspectRatio":1},"inducedDragCoefficient",0.3183098861837907],["af.lift_to_drag_ratio",{"liftCoefficient":0.6,"dragCoefficient":0.03},"liftToDragRatio",20],["af.reynolds_number",{"densityKgM3":1,"trueAirspeedMps":10,"referenceLengthM":2,"dynamicViscosityPaS":2e-05},"reynoldsNumber",1000000],["af.stall_speed",{"weightN":1000,"densityKgM3":1,"wingAreaM2":10,"maximumLiftCoefficient":2},"stallSpeedMps",10],["af.power_required",{"dragN":100,"trueAirspeedMps":20},"powerRequiredW",2000],["af.excess_power_climb_rate",{"powerAvailableW":3000,"powerRequiredW":2000,"weightN":1000},"rateOfClimbMps",1],["af.coordinated_turn_load_factor",{"bankAngleDeg":60},"loadFactor",2],["af.coordinated_turn_radius",{"trueAirspeedMps":10,"bankAngleDeg":45},"turnRadiusM",10.197162129779283],["af.static_margin",{"neutralPointM":3.2,"centerOfGravityM":3.0,"meanAerodynamicChordM":2},"staticMarginFraction",0.1],["af.horizontal_tail_volume",{"tailAreaM2":4,"tailArmM":5,"wingAreaM2":20,"meanAerodynamicChordM":2},"horizontalTailVolume",0.5],["af.short_period_natural_frequency",{"pitchStiffnessDerivativePerS2":-4},"naturalFrequencyRadS",2],["af.short_period_damping_ratio",{"pitchDampingDerivativePerS":-1.6,"naturalFrequencyRadS":2},"dampingRatio",0.4],["af.propulsive_power",{"thrustN":1000,"flightSpeedMps":50},"propulsivePowerW",50000],["af.propeller_efficiency",{"thrustN":1000,"flightSpeedMps":50,"shaftPowerW":62500},"propellerEfficiency",0.8],["af.thrust_to_weight",{"availableThrustN":2500,"weightN":10000},"thrustToWeightRatio",0.25],["af.electric_endurance",{"batteryEnergyKWh":100,"usableFraction":0.8,"electricalPowerKW":40,"requiredMissionHours":1},"enduranceHours",2],["af.wing_loading",{"weightN":10000,"wingAreaM2":20},"wingLoadingPa",500],["af.bending_stress",{"bendingMomentNm":1000,"extremeFiberDistanceM":0.1,"secondMomentAreaM4":0.0001},"bendingStressPa",1000000],["af.payload_fraction",{"payloadWeightN":2000,"takeoffWeightN":10000},"payloadFraction",0.2],["af.series_system_reliability",{"reliability1":0.9,"reliability2":0.9,"reliability3":0.9,"reliability4":0.9},"seriesReliability",0.6561],["af.dual_channel_reliability",{"channel1Reliability":0.9,"channel2Reliability":0.9},"dualChannelReliability",0.99]];

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
    methodId === 'af.coordinated_turn_load_factor'
    && outputs.loadFactor > 3
  ) {
    warnings.push(
      'The calculated turn load factor exceeds 3 g; verify structural and operating limits.'
    );
  }

  if (
    methodId === 'af.static_margin'
    && (
      outputs.staticMarginFraction <= 0
      || outputs.staticMarginFraction > 0.25
    )
  ) {
    warnings.push(
      'The static margin is outside the usual positive screening range; review stability and controllability.'
    );
  }

  if (
    methodId === 'af.short_period_damping_ratio'
    && outputs.dampingRatio < 0.3
  ) {
    warnings.push(
      'Short-period damping is below a common preliminary handling-quality screening value.'
    );
  }

  if (
    methodId === 'af.electric_endurance'
    && outputs.enduranceMargin < 1.2
  ) {
    warnings.push(
      'Battery endurance margin is below 20% for the stated mission duration.'
    );
  }

  if (
    methodId === 'af.propeller_tip_mach'
    && outputs.tipMachNumber > 0.85
  ) {
    warnings.push(
      'Propeller helical tip Mach exceeds 0.85; compressibility and acoustic effects require review.'
    );
  }

  if (
    methodId === 'af.torsional_divergence_speed'
    && outputs.divergenceSpeedMargin < 1.2
  ) {
    warnings.push(
      'The screening divergence-speed margin is below 20% above the reference flight speed.'
    );
  }

  if (
    methodId === 'af.series_system_reliability'
    && outputs.seriesReliability < 0.9
  ) {
    warnings.push(
      'Series flight-system reliability is below 0.90 for the stated mission interval.'
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
      'sc-lab-aerospace-engineering-flight-analysis/1.0',
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
        'sc-lab-aerospace-engineering-flight-systems-benchmarks/1.0',
    },
    audit: {
      createdAt: new Date().toISOString(),
      engine:
        'sc-lab-aerospace-engineering-flight-systems-js',
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
    <div class="sc-af-formula-expression">
      <span>${escapeHtml(key)}</span>
      <code>${escapeHtml(specification.expression)}</code>
      <small>${escapeHtml(specification.unit || '')}</small>
    </div>
  `).join('');
}

function render(root = document) {
  const mounts = root.querySelectorAll(
    '[data-aerospace-engineering-flight-systems-root]'
  );

  mounts.forEach((mount) => {
    if (mount.dataset.scAerospaceFlightRendered === VERSION) {
      return;
    }

    mount.dataset.scAerospaceFlightRendered = VERSION;

    mount.innerHTML = `
      <div class="sc-af-workbench">
        <div class="sc-af-controls">
          <label>
            Workspace
            <select data-af-category>
              ${CATEGORIES.map(
                (category) => `<option>${escapeHtml(category)}</option>`
              ).join('')}
            </select>
          </label>

          <label>
            Method
            <select data-af-method></select>
          </label>
        </div>

        <article class="sc-af-card">
          <p class="sc-af-kicker" data-af-category-label></p>
          <h4 data-af-title></h4>

          <div class="sc-af-visible-formula">
            <span>Aeronautical or flight-systems formula</span>
            <code data-af-equation></code>
          </div>

          <p data-af-assumptions></p>

          <details class="sc-af-expression-source" open>
            <summary>Executable output expressions</summary>
            <div data-af-expressions></div>
          </details>

          <div class="sc-af-inputs" data-af-inputs></div>

          <div class="sc-af-actions">
            <button type="button" class="button button-primary" data-af-run>
              Run analysis
            </button>
            <button type="button" class="button" data-af-save>
              Save to project
            </button>
            <button type="button" class="button" data-af-note>
              Add to notebook
            </button>
            <button type="button" class="button" data-af-visualize>
              Visualize
            </button>
          </div>

          <div class="sc-af-status" data-af-status role="status" aria-live="polite">
            Select an aerospace-engineering or flight-systems method.
          </div>

          <div class="sc-af-results" data-af-results></div>

          <details>
            <summary>Analysis contract</summary>
            <pre data-af-json>{}</pre>
          </details>
        </article>

        <section class="sc-af-validation">
          <div>
            <p class="sc-af-kicker">VALIDATION</p>
            <h4>Aerospace engineering and flight-systems benchmark suite</h4>
            <p>
              Deterministic cases cover aerodynamics, performance, stability, propulsion integration, structures, navigation, and flight-system reliability.
            </p>
          </div>

          <button type="button" class="button" data-af-benchmarks>
            Run ${BENCHMARKS.length} benchmarks
          </button>

          <div data-af-benchmark-results></div>
        </section>
      </div>
    `;
  });
}

function init(root = document, projects = Lab.Projects) {
  render(root);

  const mounts = root.querySelectorAll(
    '[data-aerospace-engineering-flight-systems-root]'
  );

  mounts.forEach((mount) => {
    if (mount.dataset.scAerospaceFlightInitialized === VERSION) {
      return;
    }

    mount.dataset.scAerospaceFlightInitialized = VERSION;

    const categorySelect = mount.querySelector('[data-af-category]');
    const methodSelect = mount.querySelector('[data-af-method]');
    const inputContainer = mount.querySelector('[data-af-inputs]');
    const status = mount.querySelector('[data-af-status]');
    const resultContainer = mount.querySelector('[data-af-results]');
    const jsonTarget = mount.querySelector('[data-af-json]');
    let current = null;

    function renderMethod() {
      const selected = METHODS.get(methodSelect.value);

      if (!selected) {
        return;
      }

      mount.querySelector('[data-af-category-label]').textContent =
        selected.category.toUpperCase();
      mount.querySelector('[data-af-title]').textContent = selected.title;
      mount.querySelector('[data-af-equation]').textContent =
        selected.equation || 'Formula not documented.';
      mount.querySelector('[data-af-assumptions]').textContent =
        (selected.assumptions || []).join(' ');
      mount.querySelector('[data-af-expressions]').innerHTML =
        formulaMarkup(selected);

      inputContainer.innerHTML = selected.inputs.map((input) => `
        <label>
          ${escapeHtml(input.label)}
          <span>${escapeHtml(input.unit)}</span>
          <input
            type="number"
            step="any"
            value="${escapeHtml(input.default)}"
            data-af-field="${escapeHtml(input.key)}"
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

        inputContainer.querySelectorAll('[data-af-field]').forEach((input) => {
          raw[input.dataset.afField] = input.value;
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
    mount.querySelector('[data-af-run]').addEventListener('click', execute);

    mount.querySelector('[data-af-save]').addEventListener('click', () => {
      const record = current || execute();

      if (!record) {
        return;
      }

      if (projects && typeof projects.add === 'function') {
        projects.add(
          'aerospaceEngineeringFlightAnalyses',
          record,
          `${record.title} saved`
        );

        projects.add(
          'aerospaceFlightSystemsRecords',
          {
            schema: 'sc-lab-aerospace-flight-systems-record/1.0',
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

    mount.querySelector('[data-af-note]').addEventListener('click', () => {
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
              'aerospace-engineering',
              'flight-systems',
              record.category,
              record.methodId,
            ],
          },
          `Notebook entry added: ${record.title}`
        );

        status.textContent = 'Notebook entry added.';
      }
    });

    mount.querySelector('[data-af-visualize]').addEventListener('click', () => {
      const record = current || execute();

      if (record) {
        document.dispatchEvent(
          new CustomEvent('sc-lab:analysis', { detail: record })
        );
        status.textContent = 'Analysis sent to the visualization layer.';
      }
    });

    mount.querySelector('[data-af-benchmarks]').addEventListener(
      'click',
      () => {
        const rows = runBenchmarks();
        const passed = rows.filter((row) => row.passed).length;

        mount.querySelector('[data-af-benchmark-results]').innerHTML = `
          <p><strong>${passed}/${rows.length}</strong> benchmarks passed.</p>
          <div class="sc-af-benchmark-grid">
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
            'aerospaceFlightValidationRecords',
            {
              schema:
                'sc-lab-aerospace-engineering-flight-systems-benchmarks/1.0',
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

Lab.AerospaceEngineeringFlightSystemsLab = {
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
