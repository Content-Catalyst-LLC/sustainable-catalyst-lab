(function (global) {
'use strict';

const Lab = global.SCLab = global.SCLab || {};
const VERSION = '0.17.0';
const CATALOG = {"schema":"sc-lab-comparative-economics-development-systems-catalog/1.0","version":"0.17.0","methodCount":48,"categories":["Comparative macroeconomics & national accounts","Growth, productivity & convergence","Trade & structural transformation","Labor markets, poverty & inequality","Human development & public finance","Development finance & systems scenarios"],"methods":[{"id":"de.gdp_per_capita","category":"Comparative macroeconomics & national accounts","title":"GDP per capita","equation":"GDP per capita = gross domestic product / population","inputs":[{"key":"gdpMillionUsd","label":"Gross domestic product","unit":"million USD/yr","default":48000},{"key":"population","label":"Population","unit":"persons","default":3000000}],"outputs":{"gdpPerCapitaUsd":{"expression":"gdpMillionUsd*1000000/population","unit":"USD/person"}},"assumptions":["GDP and population use the same economy and reference year."],"notes":[],"version":"0.17.0"},{"id":"de.real_gdp_growth","category":"Comparative macroeconomics & national accounts","title":"Real GDP growth rate","equation":"Growth = real GDP current / real GDP previous \u2212 1","inputs":[{"key":"previousRealGdp","label":"Previous real GDP","unit":"index or currency","default":100},{"key":"currentRealGdp","label":"Current real GDP","unit":"index or currency","default":104.2}],"outputs":{"realGdpGrowthFraction":{"expression":"currentRealGdp/previousRealGdp-1","unit":"1"}},"assumptions":["Both GDP values use constant prices and a common accounting boundary."],"notes":[],"version":"0.17.0"},{"id":"de.real_gdp_from_deflator","category":"Comparative macroeconomics & national accounts","title":"Real GDP from nominal GDP and deflator","equation":"Real GDP = nominal GDP / (GDP deflator / 100)","inputs":[{"key":"nominalGdpMillion","label":"Nominal GDP","unit":"million currency","default":62000},{"key":"gdpDeflatorIndex","label":"GDP deflator","unit":"index, base=100","default":125}],"outputs":{"realGdpMillion":{"expression":"nominalGdpMillion/(gdpDeflatorIndex/100)","unit":"million currency"}},"assumptions":["Deflator and nominal GDP refer to the same year and economy."],"notes":[],"version":"0.17.0"},{"id":"de.gdp_expenditure_identity","category":"Comparative macroeconomics & national accounts","title":"GDP expenditure identity","equation":"GDP = consumption + investment + government + exports \u2212 imports","inputs":[{"key":"consumptionMillion","label":"Consumption","unit":"million currency","default":28000},{"key":"investmentMillion","label":"Gross investment","unit":"million currency","default":9000},{"key":"governmentMillion","label":"Government consumption","unit":"million currency","default":8000},{"key":"exportsMillion","label":"Exports","unit":"million currency","default":12000},{"key":"importsMillion","label":"Imports","unit":"million currency","default":9000}],"outputs":{"gdpMillion":{"expression":"consumptionMillion+investmentMillion+governmentMillion+exportsMillion-importsMillion","unit":"million currency"}},"assumptions":["Components use compatible national-account definitions and prices."],"notes":[],"version":"0.17.0"},{"id":"de.gross_savings_rate","category":"Comparative macroeconomics & national accounts","title":"Gross national savings rate","equation":"Savings rate = gross savings / GDP","inputs":[{"key":"grossSavingsMillion","label":"Gross savings","unit":"million currency","default":10800},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"grossSavingsFraction":{"expression":"grossSavingsMillion/gdpMillion","unit":"1"}},"assumptions":["Savings and GDP use the same accounting period and price basis."],"notes":[],"version":"0.17.0"},{"id":"de.investment_rate","category":"Comparative macroeconomics & national accounts","title":"Gross capital formation rate","equation":"Investment rate = gross capital formation / GDP","inputs":[{"key":"grossCapitalFormationMillion","label":"Gross capital formation","unit":"million currency","default":9600},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"investmentFraction":{"expression":"grossCapitalFormationMillion/gdpMillion","unit":"1"}},"assumptions":["Investment and GDP use the same accounting period and price basis."],"notes":[],"version":"0.17.0"},{"id":"de.current_account_balance","category":"Comparative macroeconomics & national accounts","title":"Current-account balance as a share of GDP","equation":"Current account = balance / GDP","inputs":[{"key":"currentAccountBalanceMillion","label":"Current-account balance","unit":"million currency","default":-1200},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"currentAccountFractionOfGdp":{"expression":"currentAccountBalanceMillion/gdpMillion","unit":"1"}},"assumptions":["Balance and GDP are measured in the same currency and period."],"notes":[],"version":"0.17.0"},{"id":"de.fiscal_balance","category":"Comparative macroeconomics & national accounts","title":"General government fiscal balance","equation":"Fiscal balance = revenue \u2212 expenditure","inputs":[{"key":"governmentRevenueMillion","label":"Government revenue","unit":"million currency","default":13200},{"key":"governmentExpenditureMillion","label":"Government expenditure","unit":"million currency","default":14800},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"fiscalBalanceMillion":{"expression":"governmentRevenueMillion-governmentExpenditureMillion","unit":"million currency"},"fiscalBalanceFractionOfGdp":{"expression":"(governmentRevenueMillion-governmentExpenditureMillion)/gdpMillion","unit":"1"}},"assumptions":["Government accounts and GDP use the same institutional coverage and period."],"notes":[],"version":"0.17.0"},{"id":"de.labor_productivity","category":"Growth, productivity & convergence","title":"Labor productivity","equation":"Productivity = real output / hours worked","inputs":[{"key":"realOutputMillion","label":"Real output","unit":"million currency","default":48000},{"key":"hoursWorkedMillion","label":"Hours worked","unit":"million h/yr","default":4200}],"outputs":{"outputPerHour":{"expression":"realOutputMillion/hoursWorkedMillion","unit":"currency/h"}},"assumptions":["Output and hours refer to the same production boundary."],"notes":[],"version":"0.17.0"},{"id":"de.total_factor_productivity","category":"Growth, productivity & convergence","title":"Cobb\u2013Douglas total factor productivity","equation":"TFP = output / (capital^\u03b1 \u00d7 labor^(1\u2212\u03b1))","inputs":[{"key":"output","label":"Real output index","unit":"index","default":140},{"key":"capital","label":"Capital-services index","unit":"index","default":130},{"key":"labor","label":"Labor-input index","unit":"index","default":110},{"key":"capitalShare","label":"Capital income share","unit":"1","default":0.35}],"outputs":{"tfpIndex":{"expression":"output/(capital**capitalShare*labor**(1-capitalShare))","unit":"index"}},"assumptions":["Cobb\u2013Douglas production technology and measured factor services."],"notes":[],"version":"0.17.0"},{"id":"de.capital_deepening","category":"Growth, productivity & convergence","title":"Capital deepening","equation":"Capital deepening = capital stock / employment","inputs":[{"key":"capitalStockMillion","label":"Real productive capital stock","unit":"million currency","default":150000},{"key":"employmentPersons","label":"Employment","unit":"persons","default":1800000}],"outputs":{"capitalPerWorker":{"expression":"capitalStockMillion*1000000/employmentPersons","unit":"currency/worker"}},"assumptions":["Capital stock and employment refer to the same productive economy."],"notes":[],"version":"0.17.0"},{"id":"de.incremental_capital_output_ratio","category":"Growth, productivity & convergence","title":"Incremental capital-output ratio","equation":"ICOR = investment share / real growth rate","inputs":[{"key":"investmentFraction","label":"Investment share of GDP","unit":"1","default":0.24},{"key":"realGrowthFraction","label":"Real GDP growth rate","unit":"1","default":0.06}],"outputs":{"incrementalCapitalOutputRatio":{"expression":"investmentFraction/realGrowthFraction","unit":"1"}},"assumptions":["Screening estimate using contemporaneous investment and growth."],"notes":[],"version":"0.17.0"},{"id":"de.solow_steady_state_capital","category":"Growth, productivity & convergence","title":"Solow steady-state capital per effective worker","equation":"k* = [s / (\u03b4 + n + g)]^(1/(1\u2212\u03b1))","inputs":[{"key":"savingsRate","label":"Savings rate","unit":"1","default":0.24},{"key":"depreciationRate","label":"Depreciation rate","unit":"1/yr","default":0.05},{"key":"populationGrowthRate","label":"Population growth","unit":"1/yr","default":0.015},{"key":"technologyGrowthRate","label":"Technology growth","unit":"1/yr","default":0.02},{"key":"capitalShare","label":"Capital share","unit":"1","default":0.35}],"outputs":{"steadyStateCapital":{"expression":"(savingsRate/(depreciationRate+populationGrowthRate+technologyGrowthRate))**(1/(1-capitalShare))","unit":"effective capital units"}},"assumptions":["Standard Solow model with Cobb\u2013Douglas production and constant rates."],"notes":[],"version":"0.17.0"},{"id":"de.growth_accounting","category":"Growth, productivity & convergence","title":"Growth-accounting residual","equation":"TFP growth = output growth \u2212 \u03b1 capital growth \u2212 (1\u2212\u03b1) labor growth","inputs":[{"key":"outputGrowth","label":"Output growth","unit":"1/yr","default":0.052},{"key":"capitalGrowth","label":"Capital-services growth","unit":"1/yr","default":0.061},{"key":"laborGrowth","label":"Labor-input growth","unit":"1/yr","default":0.018},{"key":"capitalShare","label":"Capital income share","unit":"1","default":0.35}],"outputs":{"tfpGrowth":{"expression":"outputGrowth-capitalShare*capitalGrowth-(1-capitalShare)*laborGrowth","unit":"1/yr"}},"assumptions":["Growth rates are measured consistently and factor shares sum to one."],"notes":[],"version":"0.17.0"},{"id":"de.income_convergence_gap","category":"Growth, productivity & convergence","title":"Income convergence gap","equation":"Gap = benchmark income per capita \u2212 observed income per capita","inputs":[{"key":"benchmarkIncomePerCapita","label":"Benchmark income per capita","unit":"USD/person","default":42000},{"key":"observedIncomePerCapita","label":"Observed income per capita","unit":"USD/person","default":18000}],"outputs":{"incomeGapUsdPerCapita":{"expression":"benchmarkIncomePerCapita-observedIncomePerCapita","unit":"USD/person"},"incomeGapFractionOfBenchmark":{"expression":"(benchmarkIncomePerCapita-observedIncomePerCapita)/benchmarkIncomePerCapita","unit":"1"}},"assumptions":["Benchmark and observed income use comparable methods."],"notes":[],"version":"0.17.0"},{"id":"de.productivity_catch_up_rate","category":"Growth, productivity & convergence","title":"Productivity catch-up rate","equation":"Catch-up = (gap start \u2212 gap end) / gap start","inputs":[{"key":"initialProductivityGap","label":"Initial productivity gap","unit":"index points","default":45},{"key":"endingProductivityGap","label":"Ending productivity gap","unit":"index points","default":30}],"outputs":{"catchUpFraction":{"expression":"(initialProductivityGap-endingProductivityGap)/initialProductivityGap","unit":"1"}},"assumptions":["Productivity gaps use a common benchmark and index construction."],"notes":[],"version":"0.17.0"},{"id":"de.trade_openness","category":"Trade & structural transformation","title":"Trade openness","equation":"Openness = (exports + imports) / GDP","inputs":[{"key":"exportsMillion","label":"Exports","unit":"million currency","default":12000},{"key":"importsMillion","label":"Imports","unit":"million currency","default":9000},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"tradeOpennessFraction":{"expression":"(exportsMillion+importsMillion)/gdpMillion","unit":"1"}},"assumptions":["Trade flows and GDP use the same currency and period."],"notes":[],"version":"0.17.0"},{"id":"de.export_concentration","category":"Trade & structural transformation","title":"Export concentration index","equation":"HHI = \u03a3 export-share\u00b2","inputs":[{"key":"share1","label":"Export category 1 share","unit":"1","default":0.4},{"key":"share2","label":"Export category 2 share","unit":"1","default":0.3},{"key":"share3","label":"Export category 3 share","unit":"1","default":0.2},{"key":"share4","label":"Export category 4 share","unit":"1","default":0.1}],"outputs":{"exportConcentrationHhi":{"expression":"share1**2+share2**2+share3**2+share4**2","unit":"0-1"},"shareTotal":{"expression":"share1+share2+share3+share4","unit":"1"}},"assumptions":["Shares are exhaustive and mutually exclusive."],"notes":[],"version":"0.17.0"},{"id":"de.revealed_comparative_advantage","category":"Trade & structural transformation","title":"Revealed comparative advantage","equation":"RCA = country sector share / world sector share","inputs":[{"key":"countrySectorExports","label":"Country sector exports","unit":"million USD","default":3200},{"key":"countryTotalExports","label":"Country total exports","unit":"million USD","default":12000},{"key":"worldSectorExports","label":"World sector exports","unit":"million USD","default":850000},{"key":"worldTotalExports","label":"World total exports","unit":"million USD","default":24000000}],"outputs":{"revealedComparativeAdvantage":{"expression":"(countrySectorExports/countryTotalExports)/(worldSectorExports/worldTotalExports)","unit":"1"}},"assumptions":["Country and world trade data use compatible sector classifications."],"notes":[],"version":"0.17.0"},{"id":"de.terms_of_trade","category":"Trade & structural transformation","title":"Terms-of-trade index","equation":"Terms of trade = export price index / import price index \u00d7 100","inputs":[{"key":"exportPriceIndex","label":"Export price index","unit":"index","default":118},{"key":"importPriceIndex","label":"Import price index","unit":"index","default":110}],"outputs":{"termsOfTradeIndex":{"expression":"exportPriceIndex/importPriceIndex*100","unit":"index"}},"assumptions":["Export and import price indices use the same base period."],"notes":[],"version":"0.17.0"},{"id":"de.real_exchange_rate","category":"Trade & structural transformation","title":"Real exchange-rate index","equation":"RER = nominal exchange rate \u00d7 foreign price / domestic price","inputs":[{"key":"nominalExchangeRate","label":"Domestic currency per foreign currency","unit":"currency ratio","default":1.25},{"key":"foreignPriceIndex","label":"Foreign price index","unit":"index","default":115},{"key":"domesticPriceIndex","label":"Domestic price index","unit":"index","default":125}],"outputs":{"realExchangeRateIndex":{"expression":"nominalExchangeRate*foreignPriceIndex/domesticPriceIndex","unit":"index"}},"assumptions":["Price indices use compatible baskets and the exchange-rate convention is explicit."],"notes":[],"version":"0.17.0"},{"id":"de.sectoral_employment_shift","category":"Trade & structural transformation","title":"Employment shift from agriculture","equation":"Shift = agriculture employment share start \u2212 end","inputs":[{"key":"startingAgricultureShare","label":"Starting agriculture employment share","unit":"1","default":0.42},{"key":"endingAgricultureShare","label":"Ending agriculture employment share","unit":"1","default":0.28}],"outputs":{"employmentShiftFraction":{"expression":"startingAgricultureShare-endingAgricultureShare","unit":"1"}},"assumptions":["Employment shares use a common labor-force definition."],"notes":[],"version":"0.17.0"},{"id":"de.manufacturing_value_added_share","category":"Trade & structural transformation","title":"Manufacturing value-added share","equation":"Share = manufacturing value added / GDP","inputs":[{"key":"manufacturingValueAddedMillion","label":"Manufacturing value added","unit":"million currency","default":9200},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"manufacturingShare":{"expression":"manufacturingValueAddedMillion/gdpMillion","unit":"1"}},"assumptions":["Manufacturing value added and GDP use compatible prices and classifications."],"notes":[],"version":"0.17.0"},{"id":"de.structural_transformation_index","category":"Trade & structural transformation","title":"Structural transformation index","equation":"Index = 0.5 \u00d7 \u03a3|sector share end \u2212 start|","inputs":[{"key":"agricultureStart","label":"Agriculture share, start","unit":"1","default":0.32},{"key":"agricultureEnd","label":"Agriculture share, end","unit":"1","default":0.22},{"key":"industryStart","label":"Industry share, start","unit":"1","default":0.26},{"key":"industryEnd","label":"Industry share, end","unit":"1","default":0.3},{"key":"servicesStart","label":"Services share, start","unit":"1","default":0.42},{"key":"servicesEnd","label":"Services share, end","unit":"1","default":0.48}],"outputs":{"structuralTransformationIndex":{"expression":"0.5*(abs(agricultureEnd-agricultureStart)+abs(industryEnd-industryStart)+abs(servicesEnd-servicesStart))","unit":"0-1"}},"assumptions":["Sector shares exhaust the economy in each period."],"notes":[],"version":"0.17.0"},{"id":"de.employment_rate","category":"Labor markets, poverty & inequality","title":"Employment-to-population rate","equation":"Employment rate = employed / working-age population","inputs":[{"key":"employedPersons","label":"Employed persons","unit":"persons","default":1800000},{"key":"workingAgePopulation","label":"Working-age population","unit":"persons","default":2600000}],"outputs":{"employmentRate":{"expression":"employedPersons/workingAgePopulation","unit":"1"}},"assumptions":["Employment and working-age population use consistent definitions."],"notes":[],"version":"0.17.0"},{"id":"de.unemployment_rate","category":"Labor markets, poverty & inequality","title":"Unemployment rate","equation":"Unemployment rate = unemployed / labor force","inputs":[{"key":"unemployedPersons","label":"Unemployed persons","unit":"persons","default":160000},{"key":"laborForcePersons","label":"Labor force","unit":"persons","default":1960000}],"outputs":{"unemploymentRate":{"expression":"unemployedPersons/laborForcePersons","unit":"1"}},"assumptions":["Unemployment and labor force use the same survey definition."],"notes":[],"version":"0.17.0"},{"id":"de.labor_force_participation","category":"Labor markets, poverty & inequality","title":"Labor-force participation rate","equation":"Participation = labor force / working-age population","inputs":[{"key":"laborForcePersons","label":"Labor force","unit":"persons","default":1960000},{"key":"workingAgePopulation","label":"Working-age population","unit":"persons","default":2600000}],"outputs":{"participationRate":{"expression":"laborForcePersons/workingAgePopulation","unit":"1"}},"assumptions":["Labor force and working-age population use a common age range."],"notes":[],"version":"0.17.0"},{"id":"de.labor_income_share","category":"Labor markets, poverty & inequality","title":"Labor income share","equation":"Labor share = employee compensation / gross value added","inputs":[{"key":"employeeCompensationMillion","label":"Employee compensation","unit":"million currency","default":21000},{"key":"grossValueAddedMillion","label":"Gross value added","unit":"million currency","default":45000}],"outputs":{"laborIncomeShare":{"expression":"employeeCompensationMillion/grossValueAddedMillion","unit":"1"}},"assumptions":["Compensation and value added use the same production boundary."],"notes":[],"version":"0.17.0"},{"id":"de.grouped_gini","category":"Labor markets, poverty & inequality","title":"Three-group Gini approximation","equation":"Gini = 1 \u2212 \u03a3[(Y_i + Y_i\u22121)(X_i \u2212 X_i\u22121)]","inputs":[{"key":"populationShare1","label":"Bottom group population share","unit":"1","default":0.4},{"key":"incomeShare1","label":"Bottom group income share","unit":"1","default":0.15},{"key":"populationShare2","label":"Middle group population share","unit":"1","default":0.4},{"key":"incomeShare2","label":"Middle group income share","unit":"1","default":0.35},{"key":"populationShare3","label":"Top group population share","unit":"1","default":0.2},{"key":"incomeShare3","label":"Top group income share","unit":"1","default":0.5}],"outputs":{"groupedGini":{"expression":"1-(incomeShare1*populationShare1+(incomeShare1+(incomeShare1+incomeShare2))*populationShare2+((incomeShare1+incomeShare2)+1)*populationShare3)","unit":"0-1"},"populationShareTotal":{"expression":"populationShare1+populationShare2+populationShare3","unit":"1"},"incomeShareTotal":{"expression":"incomeShare1+incomeShare2+incomeShare3","unit":"1"}},"assumptions":["Groups are ordered from lowest to highest income and shares sum to one."],"notes":[],"version":"0.17.0"},{"id":"de.palma_ratio","category":"Labor markets, poverty & inequality","title":"Palma ratio","equation":"Palma ratio = top 10% income share / bottom 40% income share","inputs":[{"key":"topTenIncomeShare","label":"Top 10% income share","unit":"1","default":0.34},{"key":"bottomFortyIncomeShare","label":"Bottom 40% income share","unit":"1","default":0.16}],"outputs":{"palmaRatio":{"expression":"topTenIncomeShare/bottomFortyIncomeShare","unit":"1"}},"assumptions":["Income shares use the same welfare concept and household weighting."],"notes":[],"version":"0.17.0"},{"id":"de.poverty_gap_index","category":"Labor markets, poverty & inequality","title":"Poverty gap index","equation":"Poverty gap = poor population \u00d7 normalized income shortfall / total population","inputs":[{"key":"poorPopulation","label":"Population below poverty line","unit":"persons","default":420000},{"key":"averagePoorIncome","label":"Average income of poor population","unit":"currency/person","default":1800},{"key":"povertyLineIncome","label":"Poverty-line income","unit":"currency/person","default":3000},{"key":"totalPopulation","label":"Total population","unit":"persons","default":3000000}],"outputs":{"povertyGapIndex":{"expression":"poorPopulation*((povertyLineIncome-averagePoorIncome)/povertyLineIncome)/totalPopulation","unit":"0-1"}},"assumptions":["Average poor income and poverty line use the same period and price basis."],"notes":[],"version":"0.17.0"},{"id":"de.gender_wage_ratio","category":"Labor markets, poverty & inequality","title":"Gender wage ratio","equation":"Wage ratio = comparison-group wage / reference-group wage","inputs":[{"key":"comparisonGroupAverageWage","label":"Comparison-group average wage","unit":"currency/month","default":3200},{"key":"referenceGroupAverageWage","label":"Reference-group average wage","unit":"currency/month","default":4000}],"outputs":{"genderWageRatio":{"expression":"comparisonGroupAverageWage/referenceGroupAverageWage","unit":"1"},"wageGapFraction":{"expression":"1-comparisonGroupAverageWage/referenceGroupAverageWage","unit":"1"}},"assumptions":["Wages are adjusted for the same period and compensation concept."],"notes":[],"version":"0.17.0"},{"id":"de.human_development_index","category":"Human development & public finance","title":"Human development geometric mean","equation":"HDI = (health \u00d7 education \u00d7 income)^(1/3)","inputs":[{"key":"healthIndex","label":"Health index","unit":"0-1","default":0.78},{"key":"educationIndex","label":"Education index","unit":"0-1","default":0.72},{"key":"incomeIndex","label":"Income index","unit":"0-1","default":0.68}],"outputs":{"humanDevelopmentIndex":{"expression":"(healthIndex*educationIndex*incomeIndex)**(1/3)","unit":"0-1"}},"assumptions":["Component indices are normalized consistently."],"notes":[],"version":"0.17.0"},{"id":"de.education_attainment","category":"Human development & public finance","title":"Upper-secondary attainment rate","equation":"Attainment = credentialed population / relevant population","inputs":[{"key":"credentialedPopulation","label":"Population with credential","unit":"persons","default":1200000},{"key":"relevantPopulation","label":"Relevant adult population","unit":"persons","default":1800000}],"outputs":{"attainmentRate":{"expression":"credentialedPopulation/relevantPopulation","unit":"1"}},"assumptions":["Credential and population definitions are consistent."],"notes":[],"version":"0.17.0"},{"id":"de.life_expectancy_index","category":"Human development & public finance","title":"Life-expectancy index","equation":"Index = (life expectancy \u2212 minimum) / (maximum \u2212 minimum)","inputs":[{"key":"lifeExpectancyYears","label":"Life expectancy","unit":"yr","default":74},{"key":"minimumYears","label":"Minimum goalpost","unit":"yr","default":20},{"key":"maximumYears","label":"Maximum goalpost","unit":"yr","default":85}],"outputs":{"lifeExpectancyIndex":{"expression":"(lifeExpectancyYears-minimumYears)/(maximumYears-minimumYears)","unit":"0-1"}},"assumptions":["Goalposts are explicit scenario or reporting choices."],"notes":[],"version":"0.17.0"},{"id":"de.health_spending_per_capita","category":"Human development & public finance","title":"Health spending per capita","equation":"Spending per capita = health expenditure / population","inputs":[{"key":"healthExpenditureMillion","label":"Health expenditure","unit":"million currency/yr","default":4200},{"key":"population","label":"Population","unit":"persons","default":3000000}],"outputs":{"healthSpendingPerCapita":{"expression":"healthExpenditureMillion*1000000/population","unit":"currency/person"}},"assumptions":["Health expenditure and population use the same jurisdiction and year."],"notes":[],"version":"0.17.0"},{"id":"de.tax_to_gdp","category":"Human development & public finance","title":"Tax-to-GDP ratio","equation":"Tax ratio = tax revenue / GDP","inputs":[{"key":"taxRevenueMillion","label":"Tax revenue","unit":"million currency","default":9600},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"taxToGdpFraction":{"expression":"taxRevenueMillion/gdpMillion","unit":"1"}},"assumptions":["Tax revenue and GDP use a common period and institutional boundary."],"notes":[],"version":"0.17.0"},{"id":"de.public_debt_to_gdp","category":"Human development & public finance","title":"Public debt-to-GDP ratio","equation":"Debt ratio = gross public debt / GDP","inputs":[{"key":"publicDebtMillion","label":"Gross public debt","unit":"million currency","default":28800},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"debtToGdpFraction":{"expression":"publicDebtMillion/gdpMillion","unit":"1"}},"assumptions":["Debt and GDP use the same currency and reporting-date convention."],"notes":[],"version":"0.17.0"},{"id":"de.debt_service_burden","category":"Human development & public finance","title":"External debt-service burden","equation":"Debt service burden = debt service / export earnings","inputs":[{"key":"annualDebtServiceMillion","label":"Annual external debt service","unit":"million USD","default":1800},{"key":"exportEarningsMillion","label":"Export earnings","unit":"million USD","default":12000}],"outputs":{"debtServiceBurdenFraction":{"expression":"annualDebtServiceMillion/exportEarningsMillion","unit":"1"}},"assumptions":["Debt service and export earnings use the same period and currency."],"notes":[],"version":"0.17.0"},{"id":"de.social_protection_coverage","category":"Human development & public finance","title":"Social protection coverage","equation":"Coverage = protected population / target population","inputs":[{"key":"protectedPopulation","label":"Population receiving qualifying protection","unit":"persons","default":1800000},{"key":"targetPopulation","label":"Target population","unit":"persons","default":2600000}],"outputs":{"socialProtectionCoverage":{"expression":"protectedPopulation/targetPopulation","unit":"1"}},"assumptions":["Protected and target populations use a common program definition."],"notes":[],"version":"0.17.0"},{"id":"de.oda_per_capita","category":"Development finance & systems scenarios","title":"Official development assistance per capita","equation":"ODA per capita = net ODA / population","inputs":[{"key":"netOdaMillionUsd","label":"Net official development assistance","unit":"million USD/yr","default":720},{"key":"population","label":"Population","unit":"persons","default":3000000}],"outputs":{"odaPerCapitaUsd":{"expression":"netOdaMillionUsd*1000000/population","unit":"USD/person"}},"assumptions":["ODA and population refer to the same recipient geography and year."],"notes":[],"version":"0.17.0"},{"id":"de.fdi_to_gdp","category":"Development finance & systems scenarios","title":"Foreign direct investment inflows as a share of GDP","equation":"FDI share = net FDI inflows / GDP","inputs":[{"key":"fdiInflowsMillion","label":"Net FDI inflows","unit":"million currency","default":2400},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"fdiToGdpFraction":{"expression":"fdiInflowsMillion/gdpMillion","unit":"1"}},"assumptions":["FDI and GDP use compatible currency and period definitions."],"notes":[],"version":"0.17.0"},{"id":"de.remittances_to_gdp","category":"Development finance & systems scenarios","title":"Personal remittances as a share of GDP","equation":"Remittance share = remittance receipts / GDP","inputs":[{"key":"remittanceReceiptsMillion","label":"Personal remittance receipts","unit":"million currency","default":3600},{"key":"gdpMillion","label":"Gross domestic product","unit":"million currency","default":48000}],"outputs":{"remittancesToGdpFraction":{"expression":"remittanceReceiptsMillion/gdpMillion","unit":"1"}},"assumptions":["Remittances and GDP use compatible currency and period definitions."],"notes":[],"version":"0.17.0"},{"id":"de.infrastructure_financing_gap","category":"Development finance & systems scenarios","title":"Infrastructure financing gap","equation":"Gap = required investment \u2212 available financing","inputs":[{"key":"requiredInvestmentMillion","label":"Required infrastructure investment","unit":"million currency","default":12000},{"key":"availableFinancingMillion","label":"Available financing","unit":"million currency","default":8200}],"outputs":{"infrastructureFinancingGapMillion":{"expression":"requiredInvestmentMillion-availableFinancingMillion","unit":"million currency"},"gapFractionOfRequirement":{"expression":"(requiredInvestmentMillion-availableFinancingMillion)/requiredInvestmentMillion","unit":"1"}},"assumptions":["Requirement and available financing use the same investment period and scope."],"notes":[],"version":"0.17.0"},{"id":"de.sdg_financing_gap","category":"Development finance & systems scenarios","title":"Sustainable development financing gap","equation":"Gap = annual SDG financing need \u2212 committed finance","inputs":[{"key":"annualNeedMillion","label":"Annual financing need","unit":"million currency","default":9200},{"key":"committedFinanceMillion","label":"Committed finance","unit":"million currency","default":6100}],"outputs":{"sdgFinancingGapMillion":{"expression":"annualNeedMillion-committedFinanceMillion","unit":"million currency"}},"assumptions":["Need and committed finance use the same SDG scope and year."],"notes":[],"version":"0.17.0"},{"id":"de.inclusive_growth_score","category":"Development finance & systems scenarios","title":"Inclusive growth score","equation":"Score = weighted growth + employment + poverty reduction + equality","inputs":[{"key":"growthScore","label":"Growth score","unit":"0-100","default":74},{"key":"growthWeight","label":"Growth weight","unit":"1","default":0.25},{"key":"employmentScore","label":"Employment score","unit":"0-100","default":70},{"key":"employmentWeight","label":"Employment weight","unit":"1","default":0.25},{"key":"povertyReductionScore","label":"Poverty-reduction score","unit":"0-100","default":68},{"key":"povertyWeight","label":"Poverty-reduction weight","unit":"1","default":0.25},{"key":"equalityScore","label":"Equality score","unit":"0-100","default":64},{"key":"equalityWeight","label":"Equality weight","unit":"1","default":0.25}],"outputs":{"inclusiveGrowthScore":{"expression":"(growthScore*growthWeight+employmentScore*employmentWeight+povertyReductionScore*povertyWeight+equalityScore*equalityWeight)/(growthWeight+employmentWeight+povertyWeight+equalityWeight)","unit":"0-100"}},"assumptions":["Scores use a common scale and weights are explicit governance choices."],"notes":[],"version":"0.17.0"},{"id":"de.resilience_adjusted_development","category":"Development finance & systems scenarios","title":"Resilience-adjusted development score","equation":"Adjusted score = development score \u00d7 resilience factor","inputs":[{"key":"developmentScore","label":"Development performance score","unit":"0-100","default":76},{"key":"resilienceFraction","label":"Resilience factor","unit":"0-1","default":0.82}],"outputs":{"resilienceAdjustedScore":{"expression":"developmentScore*resilienceFraction","unit":"0-100"}},"assumptions":["Development score and resilience factor are transparently documented."],"notes":[],"version":"0.17.0"},{"id":"de.development_scenario_robustness","category":"Development finance & systems scenarios","title":"Development scenario robustness","equation":"Robustness = minimum scenario performance / target performance","inputs":[{"key":"baselineScenarioScore","label":"Baseline scenario score","unit":"0-100","default":72},{"key":"tradeShockScenarioScore","label":"Trade-shock scenario score","unit":"0-100","default":61},{"key":"climateShockScenarioScore","label":"Climate-shock scenario score","unit":"0-100","default":65},{"key":"targetScore","label":"Target performance","unit":"0-100","default":80}],"outputs":{"robustnessFraction":{"expression":"min(baselineScenarioScore,tradeShockScenarioScore,climateShockScenarioScore)/targetScore","unit":"1"},"worstCaseScore":{"expression":"min(baselineScenarioScore,tradeShockScenarioScore,climateShockScenarioScore)","unit":"0-100"}},"assumptions":["Scenario scores use the same indicator framework and target."],"notes":[],"version":"0.17.0"}]};
const METHODS = new Map(CATALOG.methods.map((item) => [item.id, item]));
const CATEGORIES = [...new Set(CATALOG.methods.map((item) => item.category))];
const BENCHMARKS = [["de.gdp_per_capita",{"gdpMillionUsd":12,"population":1000},"gdpPerCapitaUsd",12000],["de.real_gdp_growth",{"previousRealGdp":100,"currentRealGdp":105},"realGdpGrowthFraction",0.05],["de.real_gdp_from_deflator",{"nominalGdpMillion":125,"gdpDeflatorIndex":125},"realGdpMillion",100],["de.gdp_expenditure_identity",{"consumptionMillion":60,"investmentMillion":20,"governmentMillion":15,"exportsMillion":10,"importsMillion":5},"gdpMillion",100],["de.gross_savings_rate",{"grossSavingsMillion":20,"gdpMillion":100},"grossSavingsFraction",0.2],["de.labor_productivity",{"realOutputMillion":100,"hoursWorkedMillion":20},"outputPerHour",5],["de.incremental_capital_output_ratio",{"investmentFraction":0.24,"realGrowthFraction":0.06},"incrementalCapitalOutputRatio",4],["de.growth_accounting",{"outputGrowth":0.05,"capitalGrowth":0.06,"laborGrowth":0.02,"capitalShare":0.4},"tfpGrowth",0.014],["de.productivity_catch_up_rate",{"initialProductivityGap":40,"endingProductivityGap":30},"catchUpFraction",0.25],["de.trade_openness",{"exportsMillion":30,"importsMillion":20,"gdpMillion":100},"tradeOpennessFraction",0.5],["de.export_concentration",{"share1":0.4,"share2":0.3,"share3":0.2,"share4":0.1},"exportConcentrationHhi",0.3],["de.revealed_comparative_advantage",{"countrySectorExports":20,"countryTotalExports":100,"worldSectorExports":100,"worldTotalExports":1000},"revealedComparativeAdvantage",2],["de.terms_of_trade",{"exportPriceIndex":120,"importPriceIndex":100},"termsOfTradeIndex",120],["de.structural_transformation_index",{"agricultureStart":0.4,"agricultureEnd":0.2,"industryStart":0.2,"industryEnd":0.3,"servicesStart":0.4,"servicesEnd":0.5},"structuralTransformationIndex",0.2],["de.employment_rate",{"employedPersons":700,"workingAgePopulation":1000},"employmentRate",0.7],["de.unemployment_rate",{"unemployedPersons":50,"laborForcePersons":1000},"unemploymentRate",0.05],["de.palma_ratio",{"topTenIncomeShare":0.3,"bottomFortyIncomeShare":0.15},"palmaRatio",2],["de.poverty_gap_index",{"poorPopulation":200,"averagePoorIncome":50,"povertyLineIncome":100,"totalPopulation":1000},"povertyGapIndex",0.1],["de.human_development_index",{"healthIndex":0.8,"educationIndex":0.8,"incomeIndex":0.8},"humanDevelopmentIndex",0.8],["de.tax_to_gdp",{"taxRevenueMillion":20,"gdpMillion":100},"taxToGdpFraction",0.2],["de.infrastructure_financing_gap",{"requiredInvestmentMillion":100,"availableFinancingMillion":70},"infrastructureFinancingGapMillion",30],["de.development_scenario_robustness",{"baselineScenarioScore":80,"tradeShockScenarioScore":60,"climateShockScenarioScore":70,"targetScore":80},"robustnessFraction",0.75]];

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

function warningsFor(methodId, outputs) {
  const warnings = [];

  if (methodId === 'de.current_account_balance' && outputs.currentAccountFractionOfGdp < -0.05) {
    warnings.push('The current-account deficit exceeds 5% of GDP in the stated scenario.');
  }

  if (methodId === 'de.fiscal_balance' && outputs.fiscalBalanceFractionOfGdp < -0.03) {
    warnings.push('The fiscal deficit exceeds 3% of GDP in the stated scenario.');
  }

  if (methodId === 'de.export_concentration' && outputs.exportConcentrationHhi > 0.25) {
    warnings.push('The export basket is highly concentrated under this screening threshold.');
  }

  if (methodId === 'de.grouped_gini' && (Math.abs(outputs.populationShareTotal - 1) > 0.02 || Math.abs(outputs.incomeShareTotal - 1) > 0.02)) {
    warnings.push('Grouped population and income shares should each sum to approximately 1.0.');
  }

  if (methodId === 'de.debt_service_burden' && outputs.debtServiceBurdenFraction > 0.2) {
    warnings.push('External debt service exceeds 20% of export earnings.');
  }

  if (methodId === 'de.development_scenario_robustness' && outputs.robustnessFraction < 0.8) {
    warnings.push('Worst-case development performance is below 80% of the stated target.');
  }

  return warnings;
}

function run(methodId, rawInputs) {
  const method = METHODS.get(methodId);

  if (!method) {
    throw new Error(`Unknown development-economics method: ${methodId}`);
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
      'sc-lab-comparative-economics-development-analysis/1.0',
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
        'sc-lab-comparative-economics-development-systems-benchmarks/1.0',
    },
    audit: {
      createdAt: new Date().toISOString(),
      engine:
        'sc-lab-comparative-economics-development-systems-js',
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
    <div class="sc-de-formula-expression">
      <span>${escapeHtml(key)}</span>
      <code>${escapeHtml(specification.expression)}</code>
      <small>${escapeHtml(specification.unit || '')}</small>
    </div>
  `).join('');
}

function render(root = document) {
  const mounts = root.querySelectorAll(
    '[data-comparative-economics-development-systems-root]'
  );

  mounts.forEach((mount) => {
    if (mount.dataset.scDevelopmentSystemsRendered === VERSION) {
      return;
    }

    mount.dataset.scDevelopmentSystemsRendered = VERSION;

    mount.innerHTML = `
      <div class="sc-de-workbench">
        <div class="sc-de-controls">
          <label>
            Workspace
            <select data-de-category>
              ${CATEGORIES.map(
                (category) => `<option>${escapeHtml(category)}</option>`
              ).join('')}
            </select>
          </label>

          <label>
            Method
            <select data-de-method></select>
          </label>
        </div>

        <article class="sc-de-card">
          <p class="sc-de-kicker" data-de-category-label></p>
          <h4 data-de-title></h4>

          <div class="sc-de-visible-formula">
            <span>Economic or development-systems formula</span>
            <code data-de-equation></code>
          </div>

          <p data-de-assumptions></p>

          <details class="sc-de-expression-source" open>
            <summary>Executable output expressions</summary>
            <div data-de-expressions></div>
          </details>

          <div class="sc-de-inputs" data-de-inputs></div>

          <div class="sc-de-actions">
            <button type="button" class="button button-primary" data-de-run>
              Run analysis
            </button>
            <button type="button" class="button" data-de-save>
              Save to project
            </button>
            <button type="button" class="button" data-de-note>
              Add to notebook
            </button>
            <button type="button" class="button" data-de-visualize>
              Visualize
            </button>
          </div>

          <div class="sc-de-status" data-de-status role="status" aria-live="polite">
            Select a comparative-economics or development-systems method.
          </div>

          <div class="sc-de-results" data-de-results></div>

          <details>
            <summary>Analysis contract</summary>
            <pre data-de-json>{}</pre>
          </details>
        </article>

        <section class="sc-de-validation">
          <div>
            <p class="sc-de-kicker">VALIDATION</p>
            <h4>Comparative economics and development systems benchmark suite</h4>
            <p>
              Deterministic cases cover national accounts, growth, productivity, trade, structural transformation, labor, inequality, human development, public finance, and development scenarios.
            </p>
          </div>

          <button type="button" class="button" data-de-benchmarks>
            Run ${BENCHMARKS.length} benchmarks
          </button>

          <div data-de-benchmark-results></div>
        </section>
      </div>
    `;
  });
}

function init(root = document, projects = Lab.Projects) {
  render(root);

  const mounts = root.querySelectorAll(
    '[data-comparative-economics-development-systems-root]'
  );

  mounts.forEach((mount) => {
    if (mount.dataset.scDevelopmentSystemsInitialized === VERSION) {
      return;
    }

    mount.dataset.scDevelopmentSystemsInitialized = VERSION;

    const categorySelect = mount.querySelector('[data-de-category]');
    const methodSelect = mount.querySelector('[data-de-method]');
    const inputContainer = mount.querySelector('[data-de-inputs]');
    const status = mount.querySelector('[data-de-status]');
    const resultContainer = mount.querySelector('[data-de-results]');
    const jsonTarget = mount.querySelector('[data-de-json]');
    let current = null;

    function renderMethod() {
      const selected = METHODS.get(methodSelect.value);

      if (!selected) {
        return;
      }

      mount.querySelector('[data-de-category-label]').textContent =
        selected.category.toUpperCase();
      mount.querySelector('[data-de-title]').textContent = selected.title;
      mount.querySelector('[data-de-equation]').textContent =
        selected.equation || 'Formula not documented.';
      mount.querySelector('[data-de-assumptions]').textContent =
        (selected.assumptions || []).join(' ');
      mount.querySelector('[data-de-expressions]').innerHTML =
        formulaMarkup(selected);

      inputContainer.innerHTML = selected.inputs.map((input) => `
        <label>
          ${escapeHtml(input.label)}
          <span>${escapeHtml(input.unit)}</span>
          <input
            type="number"
            step="any"
            value="${escapeHtml(input.default)}"
            data-de-field="${escapeHtml(input.key)}"
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

        inputContainer.querySelectorAll('[data-de-field]').forEach((input) => {
          raw[input.dataset.deField] = input.value;
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
    mount.querySelector('[data-de-run]').addEventListener('click', execute);

    mount.querySelector('[data-de-save]').addEventListener('click', () => {
      const record = current || execute();

      if (!record) {
        return;
      }

      if (projects && typeof projects.add === 'function') {
        projects.add(
          'comparativeEconomicsDevelopmentAnalyses',
          record,
          `${record.title} saved`
        );

        projects.add(
          'developmentEconomicsRecords',
          {
            schema: 'sc-lab-development-systems-record/1.0',
            version: VERSION,
            methodId: record.methodId,
            category: record.category,
            title: record.title,
            recordedAt: new Date().toISOString(),
            fingerprint: record.audit.fingerprint,
          },
          `Comparative-economics record added: ${record.title}`
        );

        status.textContent = 'Saved to the active project.';
      } else {
        status.textContent =
          'Analysis is ready, but the project storage module is unavailable.';
      }
    });

    mount.querySelector('[data-de-note]').addEventListener('click', () => {
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
              'comparative-economics',
              'development-systems',
              record.category,
              record.methodId,
            ],
          },
          `Notebook entry added: ${record.title}`
        );

        status.textContent = 'Notebook entry added.';
      }
    });

    mount.querySelector('[data-de-visualize]').addEventListener('click', () => {
      const record = current || execute();

      if (record) {
        document.dispatchEvent(
          new CustomEvent('sc-lab:analysis', { detail: record })
        );
        status.textContent = 'Analysis sent to the visualization layer.';
      }
    });

    mount.querySelector('[data-de-benchmarks]').addEventListener(
      'click',
      () => {
        const rows = runBenchmarks();
        const passed = rows.filter((row) => row.passed).length;

        mount.querySelector('[data-de-benchmark-results]').innerHTML = `
          <p><strong>${passed}/${rows.length}</strong> benchmarks passed.</p>
          <div class="sc-de-benchmark-grid">
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
            'developmentSystemsValidationRecords',
            {
              schema:
                'sc-lab-comparative-economics-development-systems-benchmarks/1.0',
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

Lab.ComparativeEconomicsDevelopmentSystemsLab = {
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
