from __future__ import annotations

import math

from app.comparative_economics_development_systems import METHODS, VERSION, public_catalog, run_method

def test_catalog_has_48_methods() -> None:
    assert VERSION == '0.17.0'
    assert public_catalog()['methodCount'] == 48
    assert len(METHODS) == 48

def test_macro_growth_and_trade() -> None:
    gdp=run_method('de.gdp_expenditure_identity',{'consumptionMillion':60,'investmentMillion':20,'governmentMillion':15,'exportsMillion':10,'importsMillion':5})
    assert gdp['outputs']['gdpMillion']==100
    growth=run_method('de.growth_accounting',{'outputGrowth':0.05,'capitalGrowth':0.06,'laborGrowth':0.02,'capitalShare':0.4})
    assert math.isclose(growth['outputs']['tfpGrowth'],0.014)
    rca=run_method('de.revealed_comparative_advantage',{'countrySectorExports':20,'countryTotalExports':100,'worldSectorExports':100,'worldTotalExports':1000})
    assert rca['outputs']['revealedComparativeAdvantage']==2

def test_labor_human_development_and_scenarios() -> None:
    unemployment=run_method('de.unemployment_rate',{'unemployedPersons':50,'laborForcePersons':1000})
    assert unemployment['outputs']['unemploymentRate']==0.05
    hdi=run_method('de.human_development_index',{'healthIndex':0.8,'educationIndex':0.8,'incomeIndex':0.8})
    assert math.isclose(hdi['outputs']['humanDevelopmentIndex'],0.8)
    robust=run_method('de.development_scenario_robustness',{'baselineScenarioScore':80,'tradeShockScenarioScore':60,'climateShockScenarioScore':70,'targetScore':80})
    assert robust['outputs']['robustnessFraction']==0.75
