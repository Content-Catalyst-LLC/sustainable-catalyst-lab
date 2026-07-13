(function (global) {
'use strict';

const Lab = global.SCLab = global.SCLab || {};
const VERSION = '0.19.0';
const CATALOG = {"schema":"sc-lab-rocket-propulsion-spaceflight-catalog/1.0","version":"0.19.0","methodCount":48,"categories":["Rocket propulsion fundamentals","Nozzle flow & engine performance","Launch vehicle mass & staging","Ascent & launch dynamics","Orbital mechanics & transfers","Spacecraft & mission systems"],"methods":[{"id":"rp.effective_exhaust_velocity","category":"Rocket propulsion fundamentals","title":"Effective exhaust velocity","equation":"c = I_sp g\u2080","inputs":[{"key":"specificImpulseS","label":"Specific impulse","unit":"s","default":320},{"key":"standardGravityMps2","label":"Standard gravity","unit":"m/s^2","default":9.80665}],"outputs":{"effectiveExhaustVelocityMps":{"expression":"specificImpulseS*standardGravityMps2","unit":"m/s"}},"assumptions":["Specific impulse is referenced to standard gravity."],"notes":[],"version":"0.19.0"},{"id":"rp.specific_impulse","category":"Rocket propulsion fundamentals","title":"Specific impulse","equation":"I_sp = F/(\u1e41g\u2080)","inputs":[{"key":"thrustN","label":"Thrust","unit":"N","default":760000},{"key":"massFlowKgS","label":"Propellant mass flow","unit":"kg/s","default":250},{"key":"standardGravityMps2","label":"Standard gravity","unit":"m/s^2","default":9.80665}],"outputs":{"specificImpulseS":{"expression":"thrustN/(massFlowKgS*standardGravityMps2)","unit":"s"}},"assumptions":["Thrust and mass flow are steady and measured at the same operating point."],"notes":[],"version":"0.19.0"},{"id":"rp.momentum_thrust","category":"Rocket propulsion fundamentals","title":"Momentum thrust","equation":"F_m = \u1e41V_e","inputs":[{"key":"massFlowKgS","label":"Propellant mass flow","unit":"kg/s","default":250},{"key":"exitVelocityMps","label":"Effective exit velocity","unit":"m/s","default":3100}],"outputs":{"momentumThrustN":{"expression":"massFlowKgS*exitVelocityMps","unit":"N"}},"assumptions":["Pressure thrust is excluded from this component."],"notes":[],"version":"0.19.0"},{"id":"rp.mass_flow_from_thrust","category":"Rocket propulsion fundamentals","title":"Mass flow from thrust and specific impulse","equation":"\u1e41 = F/(I_sp g\u2080)","inputs":[{"key":"thrustN","label":"Thrust","unit":"N","default":760000},{"key":"specificImpulseS","label":"Specific impulse","unit":"s","default":310},{"key":"standardGravityMps2","label":"Standard gravity","unit":"m/s^2","default":9.80665}],"outputs":{"massFlowKgS":{"expression":"thrustN/(specificImpulseS*standardGravityMps2)","unit":"kg/s"}},"assumptions":["Specific impulse and thrust refer to the same operating condition."],"notes":[],"version":"0.19.0"},{"id":"rp.ideal_rocket_delta_v","category":"Rocket propulsion fundamentals","title":"Tsiolkovsky ideal delta-v","equation":"\u0394v = c ln(m\u2080/m_f)","inputs":[{"key":"effectiveExhaustVelocityMps","label":"Effective exhaust velocity","unit":"m/s","default":3200},{"key":"initialMassKg","label":"Initial mass","unit":"kg","default":500000},{"key":"finalMassKg","label":"Final mass","unit":"kg","default":150000}],"outputs":{"idealDeltaVMps":{"expression":"effectiveExhaustVelocityMps*log(initialMassKg/finalMassKg)","unit":"m/s"}},"assumptions":["Ideal impulsive-equivalent rocket equation; gravity, drag, and steering losses excluded."],"notes":[],"version":"0.19.0"},{"id":"rp.required_mass_ratio","category":"Rocket propulsion fundamentals","title":"Required ideal mass ratio","equation":"m\u2080/m_f = exp(\u0394v/c)","inputs":[{"key":"requiredDeltaVMps","label":"Required ideal delta-v","unit":"m/s","default":4500},{"key":"effectiveExhaustVelocityMps","label":"Effective exhaust velocity","unit":"m/s","default":3200}],"outputs":{"requiredMassRatio":{"expression":"exp(requiredDeltaVMps/effectiveExhaustVelocityMps)","unit":"1"}},"assumptions":["Constant effective exhaust velocity and ideal rocket equation."],"notes":[],"version":"0.19.0"},{"id":"rp.propellant_mass_fraction","category":"Rocket propulsion fundamentals","title":"Propellant mass fraction","equation":"f_p = (m\u2080 \u2212 m_f)/m\u2080","inputs":[{"key":"initialMassKg","label":"Initial mass","unit":"kg","default":500000},{"key":"finalMassKg","label":"Final mass after burn","unit":"kg","default":150000}],"outputs":{"propellantMassFraction":{"expression":"(initialMassKg-finalMassKg)/initialMassKg","unit":"1"}},"assumptions":["Mass decrease during the segment is treated as consumed propellant."],"notes":[],"version":"0.19.0"},{"id":"rp.mixture_ratio","category":"Rocket propulsion fundamentals","title":"Oxidizer-to-fuel mixture ratio","equation":"O/F = \u1e41_ox/\u1e41_fuel","inputs":[{"key":"oxidizerMassFlowKgS","label":"Oxidizer mass flow","unit":"kg/s","default":180},{"key":"fuelMassFlowKgS","label":"Fuel mass flow","unit":"kg/s","default":70}],"outputs":{"mixtureRatio":{"expression":"oxidizerMassFlowKgS/fuelMassFlowKgS","unit":"1"}},"assumptions":["Oxidizer and fuel flows are measured over the same interval."],"notes":[],"version":"0.19.0"},{"id":"rp.nozzle_throat_area","category":"Nozzle flow & engine performance","title":"Circular nozzle throat area","equation":"A_t = \u03c0d_t\u00b2/4","inputs":[{"key":"throatDiameterM","label":"Throat diameter","unit":"m","default":0.35}],"outputs":{"throatAreaM2":{"expression":"pi*throatDiameterM**2/4","unit":"m^2"}},"assumptions":["Circular throat geometry."],"notes":[],"version":"0.19.0"},{"id":"rp.nozzle_expansion_ratio","category":"Nozzle flow & engine performance","title":"Nozzle expansion ratio","equation":"\u03b5 = A_e/A_t","inputs":[{"key":"exitAreaM2","label":"Nozzle exit area","unit":"m^2","default":3.2},{"key":"throatAreaM2","label":"Nozzle throat area","unit":"m^2","default":0.096}],"outputs":{"expansionRatio":{"expression":"exitAreaM2/throatAreaM2","unit":"1"}},"assumptions":["Exit and throat areas use the same geometric convention."],"notes":[],"version":"0.19.0"},{"id":"rp.exit_mach_from_pressure_ratio","category":"Nozzle flow & engine performance","title":"Isentropic exit Mach number from pressure ratio","equation":"M_e = \u221a{2/(\u03b3\u22121)[(p_c/p_e)^((\u03b3\u22121)/\u03b3)\u22121]}","inputs":[{"key":"chamberPressurePa","label":"Chamber stagnation pressure","unit":"Pa","default":7000000},{"key":"exitPressurePa","label":"Exit static pressure","unit":"Pa","default":40000},{"key":"specificHeatRatio","label":"Specific-heat ratio","unit":"1","default":1.22}],"outputs":{"exitMachNumber":{"expression":"sqrt(2/(specificHeatRatio-1)*((chamberPressurePa/exitPressurePa)**((specificHeatRatio-1)/specificHeatRatio)-1))","unit":"1"}},"assumptions":["Calorically perfect gas and isentropic expansion from chamber stagnation conditions."],"notes":[],"version":"0.19.0"},{"id":"rp.exit_temperature","category":"Nozzle flow & engine performance","title":"Isentropic nozzle exit temperature","equation":"T_e = T_c/[1 + (\u03b3\u22121)M_e\u00b2/2]","inputs":[{"key":"chamberTemperatureK","label":"Chamber stagnation temperature","unit":"K","default":3500},{"key":"specificHeatRatio","label":"Specific-heat ratio","unit":"1","default":1.22},{"key":"exitMachNumber","label":"Exit Mach number","unit":"1","default":3.2}],"outputs":{"exitTemperatureK":{"expression":"chamberTemperatureK/(1+(specificHeatRatio-1)*exitMachNumber**2/2)","unit":"K"}},"assumptions":["Calorically perfect gas and isentropic nozzle flow."],"notes":[],"version":"0.19.0"},{"id":"rp.isentropic_exit_velocity","category":"Nozzle flow & engine performance","title":"Ideal isentropic exit velocity","equation":"V_e = \u221a{2\u03b3RT_c/(\u03b3\u22121)[1\u2212(p_e/p_c)^((\u03b3\u22121)/\u03b3)]}","inputs":[{"key":"specificHeatRatio","label":"Specific-heat ratio","unit":"1","default":1.22},{"key":"specificGasConstantJkgK","label":"Specific gas constant","unit":"J/(kg*K)","default":355},{"key":"chamberTemperatureK","label":"Chamber stagnation temperature","unit":"K","default":3500},{"key":"chamberPressurePa","label":"Chamber pressure","unit":"Pa","default":7000000},{"key":"exitPressurePa","label":"Exit pressure","unit":"Pa","default":40000}],"outputs":{"idealExitVelocityMps":{"expression":"sqrt(2*specificHeatRatio/(specificHeatRatio-1)*specificGasConstantJkgK*chamberTemperatureK*(1-(exitPressurePa/chamberPressurePa)**((specificHeatRatio-1)/specificHeatRatio)))","unit":"m/s"}},"assumptions":["Calorically perfect gas, adiabatic isentropic expansion, and negligible chamber velocity."],"notes":[],"version":"0.19.0"},{"id":"rp.nozzle_total_thrust","category":"Nozzle flow & engine performance","title":"Nozzle momentum and pressure thrust","equation":"F = \u1e41V_e + (p_e\u2212p_a)A_e","inputs":[{"key":"massFlowKgS","label":"Propellant mass flow","unit":"kg/s","default":250},{"key":"exitVelocityMps","label":"Exit velocity","unit":"m/s","default":3100},{"key":"exitPressurePa","label":"Exit pressure","unit":"Pa","default":40000},{"key":"ambientPressurePa","label":"Ambient pressure","unit":"Pa","default":101325},{"key":"exitAreaM2","label":"Exit area","unit":"m^2","default":3.2}],"outputs":{"momentumThrustN":{"expression":"massFlowKgS*exitVelocityMps","unit":"N"},"pressureThrustN":{"expression":"(exitPressurePa-ambientPressurePa)*exitAreaM2","unit":"N"},"totalThrustN":{"expression":"massFlowKgS*exitVelocityMps+(exitPressurePa-ambientPressurePa)*exitAreaM2","unit":"N"}},"assumptions":["One-dimensional steady nozzle flow."],"notes":[],"version":"0.19.0"},{"id":"rp.thrust_coefficient","category":"Nozzle flow & engine performance","title":"Thrust coefficient","equation":"C_F = F/(p_cA_t)","inputs":[{"key":"thrustN","label":"Thrust","unit":"N","default":760000},{"key":"chamberPressurePa","label":"Chamber pressure","unit":"Pa","default":7000000},{"key":"throatAreaM2","label":"Throat area","unit":"m^2","default":0.096}],"outputs":{"thrustCoefficient":{"expression":"thrustN/(chamberPressurePa*throatAreaM2)","unit":"1"}},"assumptions":["Chamber pressure and throat area use consistent effective values."],"notes":[],"version":"0.19.0"},{"id":"rp.characteristic_velocity","category":"Nozzle flow & engine performance","title":"Characteristic velocity","equation":"c* = p_cA_t/\u1e41","inputs":[{"key":"chamberPressurePa","label":"Chamber pressure","unit":"Pa","default":7000000},{"key":"throatAreaM2","label":"Throat area","unit":"m^2","default":0.096},{"key":"massFlowKgS","label":"Propellant mass flow","unit":"kg/s","default":250}],"outputs":{"characteristicVelocityMps":{"expression":"chamberPressurePa*throatAreaM2/massFlowKgS","unit":"m/s"}},"assumptions":["Steady chamber pressure, choked throat, and consistent effective flow area."],"notes":[],"version":"0.19.0"},{"id":"rp.stage_mass_ratio","category":"Launch vehicle mass & staging","title":"Stage mass ratio","equation":"MR = m_initial/m_final","inputs":[{"key":"initialStageMassKg","label":"Initial stage mass","unit":"kg","default":450000},{"key":"finalStageMassKg","label":"Post-burn stage mass","unit":"kg","default":130000}],"outputs":{"stageMassRatio":{"expression":"initialStageMassKg/finalStageMassKg","unit":"1"}},"assumptions":["Masses correspond to the same stage and burn segment."],"notes":[],"version":"0.19.0"},{"id":"rp.structural_coefficient","category":"Launch vehicle mass & staging","title":"Stage structural coefficient","equation":"\u03b5_s = m_dry/(m_dry + m_propellant)","inputs":[{"key":"dryMassKg","label":"Stage dry mass","unit":"kg","default":30000},{"key":"propellantMassKg","label":"Usable propellant mass","unit":"kg","default":320000}],"outputs":{"structuralCoefficient":{"expression":"dryMassKg/(dryMassKg+propellantMassKg)","unit":"1"}},"assumptions":["Dry and propellant masses exclude payload and upper stages."],"notes":[],"version":"0.19.0"},{"id":"rp.payload_fraction","category":"Launch vehicle mass & staging","title":"Launch vehicle payload fraction","equation":"f_payload = m_payload/m_liftoff","inputs":[{"key":"payloadMassKg","label":"Payload mass","unit":"kg","default":18000},{"key":"liftoffMassKg","label":"Liftoff mass","unit":"kg","default":550000}],"outputs":{"payloadFraction":{"expression":"payloadMassKg/liftoffMassKg","unit":"1"}},"assumptions":["Payload and liftoff mass use the same mission configuration."],"notes":[],"version":"0.19.0"},{"id":"rp.propellant_loading_fraction","category":"Launch vehicle mass & staging","title":"Propellant loading fraction","equation":"f_prop = m_propellant/m_wet","inputs":[{"key":"propellantMassKg","label":"Loaded propellant mass","unit":"kg","default":390000},{"key":"wetMassKg","label":"Stage wet mass","unit":"kg","default":450000}],"outputs":{"propellantLoadingFraction":{"expression":"propellantMassKg/wetMassKg","unit":"1"}},"assumptions":["Wet mass includes the loaded propellant quantity."],"notes":[],"version":"0.19.0"},{"id":"rp.stage_ideal_delta_v","category":"Launch vehicle mass & staging","title":"Ideal stage delta-v","equation":"\u0394v_stage = I_sp g\u2080 ln(m_i/m_f)","inputs":[{"key":"specificImpulseS","label":"Stage specific impulse","unit":"s","default":310},{"key":"standardGravityMps2","label":"Standard gravity","unit":"m/s^2","default":9.80665},{"key":"initialStageMassKg","label":"Initial stage mass","unit":"kg","default":450000},{"key":"finalStageMassKg","label":"Final stage mass","unit":"kg","default":130000}],"outputs":{"stageIdealDeltaVMps":{"expression":"specificImpulseS*standardGravityMps2*log(initialStageMassKg/finalStageMassKg)","unit":"m/s"}},"assumptions":["Ideal rocket equation with constant effective specific impulse."],"notes":[],"version":"0.19.0"},{"id":"rp.two_stage_total_delta_v","category":"Launch vehicle mass & staging","title":"Two-stage ideal delta-v","equation":"\u0394v_total = \u0394v\u2081 + \u0394v\u2082","inputs":[{"key":"stage1DeltaVMps","label":"Stage 1 ideal delta-v","unit":"m/s","default":3800},{"key":"stage2DeltaVMps","label":"Stage 2 ideal delta-v","unit":"m/s","default":5200}],"outputs":{"totalIdealDeltaVMps":{"expression":"stage1DeltaVMps+stage2DeltaVMps","unit":"m/s"}},"assumptions":["Stage delta-v values use compatible ideal assumptions."],"notes":[],"version":"0.19.0"},{"id":"rp.burnout_acceleration","category":"Launch vehicle mass & staging","title":"Burnout axial acceleration","equation":"a = T/m_b \u2212 g","inputs":[{"key":"thrustN","label":"Thrust near burnout","unit":"N","default":760000},{"key":"burnoutMassKg","label":"Vehicle mass near burnout","unit":"kg","default":60000},{"key":"localGravityMps2","label":"Local gravity","unit":"m/s^2","default":9.3}],"outputs":{"netAccelerationMps2":{"expression":"thrustN/burnoutMassKg-localGravityMps2","unit":"m/s^2"},"netAccelerationG":{"expression":"(thrustN/burnoutMassKg-localGravityMps2)/9.80665","unit":"g"}},"assumptions":["Axial thrust, vertical flight, and neglected drag for screening."],"notes":[],"version":"0.19.0"},{"id":"rp.engine_burn_duration","category":"Launch vehicle mass & staging","title":"Engine burn duration","equation":"t_burn = m_propellant/\u1e41","inputs":[{"key":"usablePropellantMassKg","label":"Usable propellant mass","unit":"kg","default":320000},{"key":"massFlowKgS","label":"Total engine mass flow","unit":"kg/s","default":2500}],"outputs":{"burnDurationS":{"expression":"usablePropellantMassKg/massFlowKgS","unit":"s"}},"assumptions":["Constant mass flow and declared usable propellant."],"notes":[],"version":"0.19.0"},{"id":"rp.liftoff_thrust_to_weight","category":"Ascent & launch dynamics","title":"Liftoff thrust-to-weight ratio","equation":"T/W = T/(mg)","inputs":[{"key":"liftoffThrustN","label":"Total liftoff thrust","unit":"N","default":7600000},{"key":"liftoffMassKg","label":"Liftoff mass","unit":"kg","default":550000},{"key":"localGravityMps2","label":"Local gravity","unit":"m/s^2","default":9.80665}],"outputs":{"thrustToWeightRatio":{"expression":"liftoffThrustN/(liftoffMassKg*localGravityMps2)","unit":"1"}},"assumptions":["All engines operating at the stated thrust."],"notes":[],"version":"0.19.0"},{"id":"rp.initial_vertical_acceleration","category":"Ascent & launch dynamics","title":"Initial vertical acceleration","equation":"a\u2080 = T/m \u2212 g","inputs":[{"key":"liftoffThrustN","label":"Total thrust","unit":"N","default":7600000},{"key":"liftoffMassKg","label":"Vehicle mass","unit":"kg","default":550000},{"key":"localGravityMps2","label":"Local gravity","unit":"m/s^2","default":9.80665}],"outputs":{"initialAccelerationMps2":{"expression":"liftoffThrustN/liftoffMassKg-localGravityMps2","unit":"m/s^2"}},"assumptions":["Vertical ascent at release with drag neglected."],"notes":[],"version":"0.19.0"},{"id":"rp.ascent_dynamic_pressure","category":"Ascent & launch dynamics","title":"Ascent dynamic pressure","equation":"q = \u00bd\u03c1V\u00b2","inputs":[{"key":"atmosphericDensityKgM3","label":"Atmospheric density","unit":"kg/m^3","default":0.41},{"key":"vehicleSpeedMps","label":"Vehicle speed","unit":"m/s","default":650}],"outputs":{"dynamicPressurePa":{"expression":"0.5*atmosphericDensityKgM3*vehicleSpeedMps**2","unit":"Pa"}},"assumptions":["Continuum-flow dynamic-pressure screening."],"notes":[],"version":"0.19.0"},{"id":"rp.ballistic_coefficient","category":"Ascent & launch dynamics","title":"Vehicle ballistic coefficient","equation":"\u03b2 = m/(C_DA)","inputs":[{"key":"vehicleMassKg","label":"Vehicle mass","unit":"kg","default":300000},{"key":"dragCoefficient","label":"Drag coefficient","unit":"1","default":0.35},{"key":"referenceAreaM2","label":"Reference area","unit":"m^2","default":10.5}],"outputs":{"ballisticCoefficientKgM2":{"expression":"vehicleMassKg/(dragCoefficient*referenceAreaM2)","unit":"kg/m^2"}},"assumptions":["Constant reference drag coefficient and frontal area."],"notes":[],"version":"0.19.0"},{"id":"rp.ascent_drag_force","category":"Ascent & launch dynamics","title":"Ascent aerodynamic drag","equation":"D = qC_DA","inputs":[{"key":"dynamicPressurePa","label":"Dynamic pressure","unit":"Pa","default":45000},{"key":"dragCoefficient","label":"Drag coefficient","unit":"1","default":0.35},{"key":"referenceAreaM2","label":"Reference area","unit":"m^2","default":10.5}],"outputs":{"dragForceN":{"expression":"dynamicPressurePa*dragCoefficient*referenceAreaM2","unit":"N"}},"assumptions":["Reference drag coefficient and area correspond to the stated condition."],"notes":[],"version":"0.19.0"},{"id":"rp.gravity_loss","category":"Ascent & launch dynamics","title":"Gravity loss screening","equation":"\u0394v_g = g_eff t sin \u03b3","inputs":[{"key":"effectiveGravityMps2","label":"Effective gravity","unit":"m/s^2","default":9.2},{"key":"burnTimeS","label":"Ascent burn time","unit":"s","default":150},{"key":"flightPathAngleDeg","label":"Average flight-path angle","unit":"deg","default":55}],"outputs":{"gravityLossMps":{"expression":"effectiveGravityMps2*burnTimeS*sin(flightPathAngleDeg*pi/180)","unit":"m/s"}},"assumptions":["Constant effective gravity and average flight-path angle."],"notes":[],"version":"0.19.0"},{"id":"rp.drag_loss","category":"Ascent & launch dynamics","title":"Integrated drag-loss screening","equation":"\u0394v_D = D_avg t/m_avg","inputs":[{"key":"averageDragN","label":"Average drag force","unit":"N","default":180000},{"key":"lossDurationS","label":"Effective drag-loss duration","unit":"s","default":110},{"key":"averageMassKg","label":"Average vehicle mass","unit":"kg","default":320000}],"outputs":{"dragLossMps":{"expression":"averageDragN*lossDurationS/averageMassKg","unit":"m/s"}},"assumptions":["Average-force and average-mass impulse approximation."],"notes":[],"version":"0.19.0"},{"id":"rp.net_ascent_delta_v","category":"Ascent & launch dynamics","title":"Net delivered ascent delta-v","equation":"\u0394v_net = \u0394v_ideal \u2212 \u0394v_gravity \u2212 \u0394v_drag \u2212 \u0394v_steering","inputs":[{"key":"idealDeltaVMps","label":"Ideal vehicle delta-v","unit":"m/s","default":10500},{"key":"gravityLossMps","label":"Gravity loss","unit":"m/s","default":1450},{"key":"dragLossMps","label":"Drag loss","unit":"m/s","default":180},{"key":"steeringLossMps","label":"Steering and control loss","unit":"m/s","default":120}],"outputs":{"netAscentDeltaVMps":{"expression":"idealDeltaVMps-gravityLossMps-dragLossMps-steeringLossMps","unit":"m/s"}},"assumptions":["Loss components are estimated consistently and not double-counted."],"notes":[],"version":"0.19.0"},{"id":"rp.circular_orbit_velocity","category":"Orbital mechanics & transfers","title":"Circular-orbit velocity","equation":"v_c = \u221a(\u03bc/r)","inputs":[{"key":"gravitationalParameterM3S2","label":"Central-body gravitational parameter","unit":"m^3/s^2","default":398600441800000},{"key":"orbitalRadiusM","label":"Orbital radius from center","unit":"m","default":6771000}],"outputs":{"circularVelocityMps":{"expression":"sqrt(gravitationalParameterM3S2/orbitalRadiusM)","unit":"m/s"}},"assumptions":["Two-body point-mass gravity and circular orbit."],"notes":[],"version":"0.19.0"},{"id":"rp.escape_velocity","category":"Orbital mechanics & transfers","title":"Local escape velocity","equation":"v_esc = \u221a(2\u03bc/r)","inputs":[{"key":"gravitationalParameterM3S2","label":"Central-body gravitational parameter","unit":"m^3/s^2","default":398600441800000},{"key":"radiusM","label":"Distance from central-body center","unit":"m","default":6371000}],"outputs":{"escapeVelocityMps":{"expression":"sqrt(2*gravitationalParameterM3S2/radiusM)","unit":"m/s"}},"assumptions":["Two-body point-mass gravity and zero hyperbolic excess speed."],"notes":[],"version":"0.19.0"},{"id":"rp.orbital_period","category":"Orbital mechanics & transfers","title":"Keplerian orbital period","equation":"T = 2\u03c0\u221a(a\u00b3/\u03bc)","inputs":[{"key":"semiMajorAxisM","label":"Semi-major axis","unit":"m","default":6771000},{"key":"gravitationalParameterM3S2","label":"Central-body gravitational parameter","unit":"m^3/s^2","default":398600441800000}],"outputs":{"orbitalPeriodS":{"expression":"2*pi*sqrt(semiMajorAxisM**3/gravitationalParameterM3S2)","unit":"s"}},"assumptions":["Two-body Keplerian orbit."],"notes":[],"version":"0.19.0"},{"id":"rp.vis_viva_velocity","category":"Orbital mechanics & transfers","title":"Vis-viva orbital speed","equation":"v = \u221a[\u03bc(2/r \u2212 1/a)]","inputs":[{"key":"gravitationalParameterM3S2","label":"Central-body gravitational parameter","unit":"m^3/s^2","default":398600441800000},{"key":"radiusM","label":"Current orbital radius","unit":"m","default":7000000},{"key":"semiMajorAxisM","label":"Orbit semi-major axis","unit":"m","default":10000000}],"outputs":{"orbitalSpeedMps":{"expression":"sqrt(gravitationalParameterM3S2*(2/radiusM-1/semiMajorAxisM))","unit":"m/s"}},"assumptions":["Two-body Keplerian orbit."],"notes":[],"version":"0.19.0"},{"id":"rp.hohmann_departure_delta_v","category":"Orbital mechanics & transfers","title":"Hohmann transfer departure delta-v","equation":"\u0394v\u2081 = \u221a(\u03bc/r\u2081)[\u221a(2r\u2082/(r\u2081+r\u2082))\u22121]","inputs":[{"key":"gravitationalParameterM3S2","label":"Gravitational parameter","unit":"m^3/s^2","default":398600441800000},{"key":"initialOrbitRadiusM","label":"Initial circular-orbit radius","unit":"m","default":6771000},{"key":"finalOrbitRadiusM","label":"Final circular-orbit radius","unit":"m","default":42164000}],"outputs":{"departureDeltaVMps":{"expression":"sqrt(gravitationalParameterM3S2/initialOrbitRadiusM)*(sqrt(2*finalOrbitRadiusM/(initialOrbitRadiusM+finalOrbitRadiusM))-1)","unit":"m/s"}},"assumptions":["Coplanar impulsive transfer between circular orbits."],"notes":[],"version":"0.19.0"},{"id":"rp.hohmann_arrival_delta_v","category":"Orbital mechanics & transfers","title":"Hohmann transfer arrival delta-v","equation":"\u0394v\u2082 = \u221a(\u03bc/r\u2082)[1\u2212\u221a(2r\u2081/(r\u2081+r\u2082))]","inputs":[{"key":"gravitationalParameterM3S2","label":"Gravitational parameter","unit":"m^3/s^2","default":398600441800000},{"key":"initialOrbitRadiusM","label":"Initial circular-orbit radius","unit":"m","default":6771000},{"key":"finalOrbitRadiusM","label":"Final circular-orbit radius","unit":"m","default":42164000}],"outputs":{"arrivalDeltaVMps":{"expression":"sqrt(gravitationalParameterM3S2/finalOrbitRadiusM)*(1-sqrt(2*initialOrbitRadiusM/(initialOrbitRadiusM+finalOrbitRadiusM)))","unit":"m/s"}},"assumptions":["Coplanar impulsive transfer between circular orbits."],"notes":[],"version":"0.19.0"},{"id":"rp.hohmann_total_delta_v","category":"Orbital mechanics & transfers","title":"Total Hohmann transfer delta-v","equation":"\u0394v_H = |\u0394v\u2081| + |\u0394v\u2082|","inputs":[{"key":"departureDeltaVMps","label":"Departure burn delta-v","unit":"m/s","default":2450},{"key":"arrivalDeltaVMps","label":"Arrival burn delta-v","unit":"m/s","default":1470}],"outputs":{"totalTransferDeltaVMps":{"expression":"abs(departureDeltaVMps)+abs(arrivalDeltaVMps)","unit":"m/s"}},"assumptions":["Impulsive coplanar burns and no plane change."],"notes":[],"version":"0.19.0"},{"id":"rp.plane_change_delta_v","category":"Orbital mechanics & transfers","title":"Impulsive plane-change delta-v","equation":"\u0394v = 2v sin(\u0394i/2)","inputs":[{"key":"orbitalSpeedMps","label":"Orbital speed at maneuver","unit":"m/s","default":7500},{"key":"inclinationChangeDeg","label":"Plane-change angle","unit":"deg","default":10}],"outputs":{"planeChangeDeltaVMps":{"expression":"2*orbitalSpeedMps*sin(inclinationChangeDeg*pi/360)","unit":"m/s"}},"assumptions":["Instantaneous pure plane change at constant speed magnitude."],"notes":[],"version":"0.19.0"},{"id":"rp.mission_delta_v_budget","category":"Spacecraft & mission systems","title":"Mission delta-v budget","equation":"\u0394v_budget = \u03a3 maneuvers + reserve","inputs":[{"key":"insertionDeltaVMps","label":"Orbit insertion delta-v","unit":"m/s","default":1800},{"key":"transferDeltaVMps","label":"Transfer delta-v","unit":"m/s","default":3200},{"key":"correctionDeltaVMps","label":"Trajectory correction delta-v","unit":"m/s","default":180},{"key":"attitudeAndStationkeepingDeltaVMps","label":"Attitude and stationkeeping delta-v","unit":"m/s","default":220},{"key":"reserveDeltaVMps","label":"Contingency reserve","unit":"m/s","default":350}],"outputs":{"missionDeltaVBudgetMps":{"expression":"insertionDeltaVMps+transferDeltaVMps+correctionDeltaVMps+attitudeAndStationkeepingDeltaVMps+reserveDeltaVMps","unit":"m/s"}},"assumptions":["Maneuver categories are mutually exclusive and consistently estimated."],"notes":[],"version":"0.19.0"},{"id":"rp.propellant_reserve_fraction","category":"Spacecraft & mission systems","title":"Propellant reserve fraction","equation":"f_reserve = m_reserve/m_loaded","inputs":[{"key":"reservePropellantMassKg","label":"Reserved propellant","unit":"kg","default":180},{"key":"loadedPropellantMassKg","label":"Loaded propellant","unit":"kg","default":1200}],"outputs":{"propellantReserveFraction":{"expression":"reservePropellantMassKg/loadedPropellantMassKg","unit":"1"}},"assumptions":["Reserve and loaded propellant use the same usable-mass convention."],"notes":[],"version":"0.19.0"},{"id":"rp.solar_array_area","category":"Spacecraft & mission systems","title":"Required solar-array area","equation":"A = P/[G\u03b7f_d f_i]","inputs":[{"key":"requiredElectricalPowerW","label":"Required electrical power","unit":"W","default":4200},{"key":"solarFluxWm2","label":"Incident solar flux","unit":"W/m^2","default":1361},{"key":"cellEfficiency","label":"Beginning-of-life cell efficiency","unit":"1","default":0.3},{"key":"degradationFactor","label":"End-of-life degradation factor","unit":"1","default":0.82},{"key":"incidenceFactor","label":"Average incidence factor","unit":"1","default":0.9}],"outputs":{"requiredSolarArrayAreaM2":{"expression":"requiredElectricalPowerW/(solarFluxWm2*cellEfficiency*degradationFactor*incidenceFactor)","unit":"m^2"}},"assumptions":["Constant representative flux, incidence, conversion efficiency, and degradation factor."],"notes":[],"version":"0.19.0"},{"id":"rp.battery_capacity","category":"Spacecraft & mission systems","title":"Required battery capacity","equation":"C_Ah = Pt/(V DOD \u03b7)","inputs":[{"key":"eclipsePowerW","label":"Eclipse electrical load","unit":"W","default":2800},{"key":"eclipseDurationH","label":"Eclipse duration","unit":"h","default":0.62},{"key":"busVoltageV","label":"Battery bus voltage","unit":"V","default":100},{"key":"allowableDepthOfDischarge","label":"Allowable depth of discharge","unit":"1","default":0.6},{"key":"dischargeEfficiency","label":"Discharge efficiency","unit":"1","default":0.92}],"outputs":{"requiredBatteryCapacityAh":{"expression":"eclipsePowerW*eclipseDurationH/(busVoltageV*allowableDepthOfDischarge*dischargeEfficiency)","unit":"Ah"}},"assumptions":["Constant eclipse load and stated usable depth of discharge."],"notes":[],"version":"0.19.0"},{"id":"rp.radiator_area","category":"Spacecraft & mission systems","title":"Radiator area for net heat rejection","equation":"A = Q/[\u03b5\u03c3(T_r\u2074\u2212T_sink\u2074)]","inputs":[{"key":"heatRejectionW","label":"Required heat rejection","unit":"W","default":1800},{"key":"emissivity","label":"Radiator emissivity","unit":"1","default":0.85},{"key":"stefanBoltzmannWm2K4","label":"Stefan\u2013Boltzmann constant","unit":"W/(m^2*K^4)","default":5.670374419e-08},{"key":"radiatorTemperatureK","label":"Radiator temperature","unit":"K","default":320},{"key":"sinkTemperatureK","label":"Effective sink temperature","unit":"K","default":3}],"outputs":{"radiatorAreaM2":{"expression":"heatRejectionW/(emissivity*stefanBoltzmannWm2K4*(radiatorTemperatureK**4-sinkTemperatureK**4))","unit":"m^2"}},"assumptions":["Diffuse-grey radiation and negligible non-radiative heat rejection."],"notes":[],"version":"0.19.0"},{"id":"rp.radiative_equilibrium_temperature","category":"Spacecraft & mission systems","title":"Radiative equilibrium temperature","equation":"T = [P_abs/(\u03b5\u03c3A)]^(1/4)","inputs":[{"key":"absorbedPowerW","label":"Absorbed environmental and internal power","unit":"W","default":1200},{"key":"emissivity","label":"Effective emissivity","unit":"1","default":0.82},{"key":"stefanBoltzmannWm2K4","label":"Stefan\u2013Boltzmann constant","unit":"W/(m^2*K^4)","default":5.670374419e-08},{"key":"radiatingAreaM2","label":"Effective radiating area","unit":"m^2","default":6}],"outputs":{"equilibriumTemperatureK":{"expression":"(absorbedPowerW/(emissivity*stefanBoltzmannWm2K4*radiatingAreaM2))**0.25","unit":"K"}},"assumptions":["Steady lumped thermal balance and diffuse-grey emission."],"notes":[],"version":"0.19.0"},{"id":"rp.free_space_path_loss","category":"Spacecraft & mission systems","title":"Free-space path loss","equation":"FSPL = 20log\u2081\u2080(4\u03c0df/c)","inputs":[{"key":"distanceM","label":"Link distance","unit":"m","default":400000},{"key":"frequencyHz","label":"Carrier frequency","unit":"Hz","default":2200000000},{"key":"speedOfLightMps","label":"Speed of light","unit":"m/s","default":299792458}],"outputs":{"freeSpacePathLossDb":{"expression":"20*log10(4*pi*distanceM*frequencyHz/speedOfLightMps)","unit":"dB"}},"assumptions":["Far-field free-space propagation without atmospheric or pointing losses."],"notes":[],"version":"0.19.0"},{"id":"rp.series_mission_reliability","category":"Spacecraft & mission systems","title":"Series mission reliability","equation":"R_mission = R_launch R_prop R_power R_thermal R_comm","inputs":[{"key":"launchReliability","label":"Launch phase reliability","unit":"0-1","default":0.985},{"key":"propulsionReliability","label":"Propulsion reliability","unit":"0-1","default":0.99},{"key":"powerReliability","label":"Power-system reliability","unit":"0-1","default":0.995},{"key":"thermalReliability","label":"Thermal-control reliability","unit":"0-1","default":0.997},{"key":"communicationsReliability","label":"Communications reliability","unit":"0-1","default":0.996}],"outputs":{"missionReliability":{"expression":"launchReliability*propulsionReliability*powerReliability*thermalReliability*communicationsReliability","unit":"0-1"}},"assumptions":["Independent phase and subsystem failures with all elements required for mission success."],"notes":[],"version":"0.19.0"}]};
const METHODS = new Map(CATALOG.methods.map((item) => [item.id, item]));
const CATEGORIES = [...new Set(CATALOG.methods.map((item) => item.category))];
const BENCHMARKS = [["rp.effective_exhaust_velocity",{"specificImpulseS":100,"standardGravityMps2":10},"effectiveExhaustVelocityMps",1000],["rp.specific_impulse",{"thrustN":1000,"massFlowKgS":10,"standardGravityMps2":10},"specificImpulseS",10],["rp.momentum_thrust",{"massFlowKgS":10,"exitVelocityMps":100},"momentumThrustN",1000],["rp.mass_flow_from_thrust",{"thrustN":1000,"specificImpulseS":10,"standardGravityMps2":10},"massFlowKgS",10],["rp.ideal_rocket_delta_v",{"effectiveExhaustVelocityMps":1000,"initialMassKg":2.718281828459045,"finalMassKg":1},"idealDeltaVMps",1000],["rp.required_mass_ratio",{"requiredDeltaVMps":693.1471805599452,"effectiveExhaustVelocityMps":1000},"requiredMassRatio",2],["rp.propellant_mass_fraction",{"initialMassKg":100,"finalMassKg":60},"propellantMassFraction",0.4],["rp.mixture_ratio",{"oxidizerMassFlowKgS":20,"fuelMassFlowKgS":5},"mixtureRatio",4],["rp.nozzle_throat_area",{"throatDiameterM":2},"throatAreaM2",3.141592653589793],["rp.nozzle_expansion_ratio",{"exitAreaM2":10,"throatAreaM2":2},"expansionRatio",5],["rp.exit_mach_from_pressure_ratio",{"chamberPressurePa":4,"exitPressurePa":1,"specificHeatRatio":2},"exitMachNumber",1.4142135623730951],["rp.exit_temperature",{"chamberTemperatureK":1000,"specificHeatRatio":2,"exitMachNumber":1},"exitTemperatureK",666.6666666666666],["rp.isentropic_exit_velocity",{"specificHeatRatio":2,"specificGasConstantJkgK":1,"chamberTemperatureK":1,"chamberPressurePa":4,"exitPressurePa":1},"idealExitVelocityMps",1.4142135623730951],["rp.nozzle_total_thrust",{"massFlowKgS":10,"exitVelocityMps":100,"exitPressurePa":2,"ambientPressurePa":1,"exitAreaM2":5},"totalThrustN",1005],["rp.thrust_coefficient",{"thrustN":1000,"chamberPressurePa":100,"throatAreaM2":2},"thrustCoefficient",5],["rp.characteristic_velocity",{"chamberPressurePa":100,"throatAreaM2":2,"massFlowKgS":10},"characteristicVelocityMps",20],["rp.stage_mass_ratio",{"initialStageMassKg":100,"finalStageMassKg":20},"stageMassRatio",5],["rp.structural_coefficient",{"dryMassKg":20,"propellantMassKg":80},"structuralCoefficient",0.2],["rp.payload_fraction",{"payloadMassKg":10,"liftoffMassKg":100},"payloadFraction",0.1],["rp.propellant_loading_fraction",{"propellantMassKg":80,"wetMassKg":100},"propellantLoadingFraction",0.8],["rp.stage_ideal_delta_v",{"specificImpulseS":100,"standardGravityMps2":10,"initialStageMassKg":2.718281828459045,"finalStageMassKg":1},"stageIdealDeltaVMps",1000],["rp.two_stage_total_delta_v",{"stage1DeltaVMps":1000,"stage2DeltaVMps":2000},"totalIdealDeltaVMps",3000],["rp.burnout_acceleration",{"thrustN":200,"burnoutMassKg":10,"localGravityMps2":10},"netAccelerationMps2",10],["rp.engine_burn_duration",{"usablePropellantMassKg":100,"massFlowKgS":10},"burnDurationS",10],["rp.liftoff_thrust_to_weight",{"liftoffThrustN":200,"liftoffMassKg":10,"localGravityMps2":10},"thrustToWeightRatio",2],["rp.initial_vertical_acceleration",{"liftoffThrustN":200,"liftoffMassKg":10,"localGravityMps2":10},"initialAccelerationMps2",10],["rp.ascent_dynamic_pressure",{"atmosphericDensityKgM3":1,"vehicleSpeedMps":10},"dynamicPressurePa",50],["rp.ballistic_coefficient",{"vehicleMassKg":100,"dragCoefficient":0.5,"referenceAreaM2":10},"ballisticCoefficientKgM2",20],["rp.ascent_drag_force",{"dynamicPressurePa":100,"dragCoefficient":0.5,"referenceAreaM2":10},"dragForceN",500],["rp.gravity_loss",{"effectiveGravityMps2":10,"burnTimeS":10,"flightPathAngleDeg":30},"gravityLossMps",50],["rp.drag_loss",{"averageDragN":100,"lossDurationS":10,"averageMassKg":100},"dragLossMps",10],["rp.net_ascent_delta_v",{"idealDeltaVMps":1000,"gravityLossMps":100,"dragLossMps":50,"steeringLossMps":25},"netAscentDeltaVMps",825],["rp.circular_orbit_velocity",{"gravitationalParameterM3S2":100,"orbitalRadiusM":4},"circularVelocityMps",5],["rp.escape_velocity",{"gravitationalParameterM3S2":100,"radiusM":4},"escapeVelocityMps",7.0710678118654755],["rp.orbital_period",{"semiMajorAxisM":1,"gravitationalParameterM3S2":1},"orbitalPeriodS",6.283185307179586],["rp.vis_viva_velocity",{"gravitationalParameterM3S2":100,"radiusM":10,"semiMajorAxisM":20},"orbitalSpeedMps",3.872983346207417],["rp.hohmann_departure_delta_v",{"gravitationalParameterM3S2":100,"initialOrbitRadiusM":10,"finalOrbitRadiusM":10},"departureDeltaVMps",0],["rp.hohmann_arrival_delta_v",{"gravitationalParameterM3S2":100,"initialOrbitRadiusM":10,"finalOrbitRadiusM":10},"arrivalDeltaVMps",0],["rp.hohmann_total_delta_v",{"departureDeltaVMps":100,"arrivalDeltaVMps":-50},"totalTransferDeltaVMps",150],["rp.plane_change_delta_v",{"orbitalSpeedMps":100,"inclinationChangeDeg":60},"planeChangeDeltaVMps",100],["rp.mission_delta_v_budget",{"insertionDeltaVMps":1,"transferDeltaVMps":2,"correctionDeltaVMps":3,"attitudeAndStationkeepingDeltaVMps":4,"reserveDeltaVMps":5},"missionDeltaVBudgetMps",15],["rp.propellant_reserve_fraction",{"reservePropellantMassKg":10,"loadedPropellantMassKg":100},"propellantReserveFraction",0.1],["rp.solar_array_area",{"requiredElectricalPowerW":100,"solarFluxWm2":100,"cellEfficiency":0.5,"degradationFactor":1,"incidenceFactor":1},"requiredSolarArrayAreaM2",2],["rp.battery_capacity",{"eclipsePowerW":100,"eclipseDurationH":1,"busVoltageV":10,"allowableDepthOfDischarge":0.5,"dischargeEfficiency":1},"requiredBatteryCapacityAh",20],["rp.series_mission_reliability",{"launchReliability":0.9,"propulsionReliability":0.9,"powerReliability":0.9,"thermalReliability":0.9,"communicationsReliability":0.9},"missionReliability",0.59049]];

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
    methodId === 'rp.required_mass_ratio'
    && outputs.requiredMassRatio > 10
  ) {
    warnings.push(
      'The ideal required mass ratio exceeds 10; staging or a different mission architecture should be examined.'
    );
  }

  if (
    methodId === 'rp.liftoff_thrust_to_weight'
    && outputs.thrustToWeightRatio <= 1
  ) {
    warnings.push(
      'Liftoff thrust-to-weight is not greater than one in the stated condition.'
    );
  }

  if (
    methodId === 'rp.ascent_dynamic_pressure'
    && outputs.dynamicPressurePa > 50000
  ) {
    warnings.push(
      'Dynamic pressure exceeds 50 kPa; structural and trajectory constraints require review.'
    );
  }

  if (
    methodId === 'rp.burnout_acceleration'
    && outputs.netAccelerationG > 5
  ) {
    warnings.push(
      'Net burnout acceleration exceeds 5 g in this screening calculation.'
    );
  }

  if (
    methodId === 'rp.plane_change_delta_v'
    && outputs.planeChangeDeltaVMps > 1000
  ) {
    warnings.push(
      'The impulsive plane change requires more than 1 km/s; alternate maneuver geometry should be considered.'
    );
  }

  if (
    methodId === 'rp.propellant_reserve_fraction'
    && outputs.propellantReserveFraction < 0.1
  ) {
    warnings.push(
      'Propellant reserve is below 10% of loaded propellant.'
    );
  }

  if (
    methodId === 'rp.series_mission_reliability'
    && outputs.missionReliability < 0.95
  ) {
    warnings.push(
      'Series mission reliability is below 0.95 for the stated independent-element model.'
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
      'sc-lab-rocket-propulsion-spaceflight-analysis/1.0',
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
        'sc-lab-rocket-propulsion-spaceflight-benchmarks/1.0',
    },
    audit: {
      createdAt: new Date().toISOString(),
      engine:
        'sc-lab-rocket-propulsion-spaceflight-js',
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
    <div class="sc-rp-formula-expression">
      <span>${escapeHtml(key)}</span>
      <code>${escapeHtml(specification.expression)}</code>
      <small>${escapeHtml(specification.unit || '')}</small>
    </div>
  `).join('');
}

function render(root = document) {
  const mounts = root.querySelectorAll(
    '[data-rocket-propulsion-spaceflight-root]'
  );

  mounts.forEach((mount) => {
    if (mount.dataset.scRocketSpaceflightRendered === VERSION) {
      return;
    }

    mount.dataset.scRocketSpaceflightRendered = VERSION;

    mount.innerHTML = `
      <div class="sc-rp-workbench">
        <div class="sc-rp-controls">
          <label>
            Workspace
            <select data-rp-category>
              ${CATEGORIES.map(
                (category) => `<option>${escapeHtml(category)}</option>`
              ).join('')}
            </select>
          </label>

          <label>
            Method
            <select data-rp-method></select>
          </label>
        </div>

        <article class="sc-rp-card">
          <p class="sc-rp-kicker" data-rp-category-label></p>
          <h4 data-rp-title></h4>

          <div class="sc-rp-visible-formula">
            <span>Rocket-propulsion or spaceflight formula</span>
            <code data-rp-equation></code>
          </div>

          <p data-rp-assumptions></p>

          <details class="sc-rp-expression-source" open>
            <summary>Executable output expressions</summary>
            <div data-rp-expressions></div>
          </details>

          <div class="sc-rp-inputs" data-rp-inputs></div>

          <div class="sc-rp-actions">
            <button type="button" class="button button-primary" data-rp-run>
              Run analysis
            </button>
            <button type="button" class="button" data-rp-save>
              Save to project
            </button>
            <button type="button" class="button" data-rp-note>
              Add to notebook
            </button>
            <button type="button" class="button" data-rp-visualize>
              Visualize
            </button>
          </div>

          <div class="sc-rp-status" data-rp-status role="status" aria-live="polite">
            Select a rocket-propulsion or spaceflight method.
          </div>

          <div class="sc-rp-results" data-rp-results></div>

          <details>
            <summary>Analysis contract</summary>
            <pre data-rp-json>{}</pre>
          </details>
        </article>

        <section class="sc-rp-validation">
          <div>
            <p class="sc-rp-kicker">VALIDATION</p>
            <h4>Rocket propulsion and spaceflight benchmark suite</h4>
            <p>
              Deterministic cases cover propulsion fundamentals, nozzle flow, staging, ascent, orbital transfers, and spacecraft mission systems.
            </p>
          </div>

          <button type="button" class="button" data-rp-benchmarks>
            Run ${BENCHMARKS.length} benchmarks
          </button>

          <div data-rp-benchmark-results></div>
        </section>
      </div>
    `;
  });
}

function init(root = document, projects = Lab.Projects) {
  render(root);

  const mounts = root.querySelectorAll(
    '[data-rocket-propulsion-spaceflight-root]'
  );

  mounts.forEach((mount) => {
    if (mount.dataset.scRocketSpaceflightInitialized === VERSION) {
      return;
    }

    mount.dataset.scRocketSpaceflightInitialized = VERSION;

    const categorySelect = mount.querySelector('[data-rp-category]');
    const methodSelect = mount.querySelector('[data-rp-method]');
    const inputContainer = mount.querySelector('[data-rp-inputs]');
    const status = mount.querySelector('[data-rp-status]');
    const resultContainer = mount.querySelector('[data-rp-results]');
    const jsonTarget = mount.querySelector('[data-rp-json]');
    let current = null;

    function renderMethod() {
      const selected = METHODS.get(methodSelect.value);

      if (!selected) {
        return;
      }

      mount.querySelector('[data-rp-category-label]').textContent =
        selected.category.toUpperCase();
      mount.querySelector('[data-rp-title]').textContent = selected.title;
      mount.querySelector('[data-rp-equation]').textContent =
        selected.equation || 'Formula not documented.';
      mount.querySelector('[data-rp-assumptions]').textContent =
        (selected.assumptions || []).join(' ');
      mount.querySelector('[data-rp-expressions]').innerHTML =
        formulaMarkup(selected);

      inputContainer.innerHTML = selected.inputs.map((input) => `
        <label>
          ${escapeHtml(input.label)}
          <span>${escapeHtml(input.unit)}</span>
          <input
            type="number"
            step="any"
            value="${escapeHtml(input.default)}"
            data-rp-field="${escapeHtml(input.key)}"
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

        inputContainer.querySelectorAll('[data-rp-field]').forEach((input) => {
          raw[input.dataset.rpField] = input.value;
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
    mount.querySelector('[data-rp-run]').addEventListener('click', execute);

    mount.querySelector('[data-rp-save]').addEventListener('click', () => {
      const record = current || execute();

      if (!record) {
        return;
      }

      if (projects && typeof projects.add === 'function') {
        projects.add(
          'rocketPropulsionSpaceflightAnalyses',
          record,
          `${record.title} saved`
        );

        projects.add(
          'spaceflightSystemsRecords',
          {
            schema: 'sc-lab-spaceflight-systems-record/1.0',
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

    mount.querySelector('[data-rp-note]').addEventListener('click', () => {
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
              'rocket-propulsion',
              'spaceflight',
              record.category,
              record.methodId,
            ],
          },
          `Notebook entry added: ${record.title}`
        );

        status.textContent = 'Notebook entry added.';
      }
    });

    mount.querySelector('[data-rp-visualize]').addEventListener('click', () => {
      const record = current || execute();

      if (record) {
        document.dispatchEvent(
          new CustomEvent('sc-lab:analysis', { detail: record })
        );
        status.textContent = 'Analysis sent to the visualization layer.';
      }
    });

    mount.querySelector('[data-rp-benchmarks]').addEventListener(
      'click',
      () => {
        const rows = runBenchmarks();
        const passed = rows.filter((row) => row.passed).length;

        mount.querySelector('[data-rp-benchmark-results]').innerHTML = `
          <p><strong>${passed}/${rows.length}</strong> benchmarks passed.</p>
          <div class="sc-rp-benchmark-grid">
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
            'rocketSpaceflightValidationRecords',
            {
              schema:
                'sc-lab-rocket-propulsion-spaceflight-benchmarks/1.0',
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

Lab.RocketPropulsionSpaceflightLab = {
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
