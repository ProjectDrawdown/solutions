pythonFieldMetadataArray = [
    ["solution_category", {}, "typing.Any"],
    ["vmas", {}, "typing.Dict"],
    ["vma_values", {}, "typing.Dict"],
    ["name", {}, "<class 'str'>"],
    ["description", {}, "<class 'str'>"],
    ["js", {}, "<class 'str'>"],
    ["jsfile", {}, "<class 'str'>"],
    ["pds_2014_cost", {
        "vma_titles": ["SOLUTION First Cost per Implementation Unit"],
        "subtitle": "(implementation/land units)",
        "tooltip": "SOLUTION First Cost per Implementation Unit\n\nNOTE: This is the cost of acquisition and the cost of installation (sometimes one and the same) or the cost of initiating a program/practice (for solutions where there is no direct artifact to acquire and install) per Implementation unit of the SOLUTION.\n\nE.g. What is the cost to acquire and install rooftop solar PV?",
        "excelref": "SolarPVUtil \"Advanced Controls\"!B128"
    }, "typing.Any"],
    ["ref_2014_cost", {
        "vma_titles": ["SOLUTION First Cost per Implementation Unit"],
        "subtitle": "(implementation/land units)",
        "tooltip": "SOLUTION First Cost per Implementation Unit\n\nNOTE: This is the cost of acquisition and the cost of installation (sometimes one and the same) or the cost of initiating a program/practice (for solutions where there is no direct artifact to acquire and install) per Implementation unit of the SOLUTION.\n\nE.g. What is the cost to acquire and install rooftop solar PV?",
        "excelref": "SolarPVUtil \"Advanced Controls\"!B128"
    }, "typing.Any"],
    ["conv_2014_cost", {
        "vma_titles": ["CONVENTIONAL First Cost per Implementation Unit"],
        "subtitle": "(implementation units)",
        "tooltip": "CONVENTIONAL First Cost per Implementation Unit for replaced practices/technologies\n\nNOTE: This is the cost of acquisition and the cost of installation (sometimes one and the same) or the cost of initiating a program/practice (for solutions where there is no direct artifact to acquire and install) per Unit of Implementation of the CONVENTIONAL mix of practices (those practices that do not include the technology in question.\n\nE.g. What is the cost to purchase an internal combustion engine (ICE) vehicle?",
        "excelref": "SolarPVUtil \"Advanced Controls\"!B95"
    }, "typing.Any"],
    ["soln_first_cost_efficiency_rate", {
        "vma_titles": [],
        "subtitle": "(Rates are usually Close to 0%)",
        "tooltip": "First Cost Learning Rate\nNOTE: Learning curves (sometimes called experience curves) are used to analyze a well-known and easily observed phenomena: humans become increasingly efficient with experience. The first time a product is manufactured or a service provided, costs are high, work is inefficient, quality is marginal, and time is wasted. As experience is acquired, costs decline, efficiency and quality improve, and waste is reduced.\n\nIn many situations, this pattern of improvement follows a predictable pattern: for every doubling of (or some multiple of) production of units, the \"cost\" of production (measured in dollars, hours, or in terms of other inputs) declines to some fraction of previous costs.\n\nThis learning rate will be applied to the technology in question for both the Optimal and BusinessAsUsual scenario.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!C128"
    }, "<class 'float'>"],
    ["conv_first_cost_efficiency_rate", {
        "vma_titles": [],
        "subtitle": "(Rates are usually Close to 0%)",
        "tooltip": "First Cost Learning Rate\nNOTE: Learning curves (sometimes called experience curves) are used to analyze a well-known and easily observed phenomena: humans become increasingly efficient with experience. The first time a product is manufactured or a service provided, costs are high, work is inefficient, quality is marginal, and time is wasted. As experience is acquired, costs decline, efficiency and quality improve, and waste is reduced.\n\nIn many situations, this pattern of improvement follows a predictable pattern: for every doubling of (or some multiple of) production of units, the \"cost\" of production (measured in dollars, hours, or in terms of other inputs) declines to some fraction of previous costs. \n\nThis would be the learning rate or efficiency rate for the CONVENTIONAL mix of practices. In many/most cases this will be 0% if the market is mature.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!C95"
    }, "<class 'float'>"],
    ["soln_first_cost_below_conv", {
        "vma_titles": [],
        "subtitle": "",
        "tooltip": ["Allow solution First Cost to go Below Conventional?\n", "NOTE: The Solution First Cost may decline below that of the Conventional due to the learning rate chosen. This may be acceptable in some cases for instance when the projections in the literature indicate so. In other cases, it may not be likely for the Solution to become cheaper than the Conventional."],
        "excelref": "SolarPVUtil \"Advanced Controls\"!C132"
    }, "<class 'bool'>"],
    ["soln_energy_efficiency_factor", {
        "vma_titles": ["SOLUTION Energy Efficiency Factor"],
        "subtitle": "",
        "tooltip": "Energy Efficiency Factor SOLUTION\nsoln_energy_efficiency_factor: Units of energy reduced per year per functional unit installed.\n\nFOR CLEAN RENEWABLE ENERGY SOLUTIONS: enter 0 (e.g. implementing solar PV fully replaces existing fossil fuel-based generation, but does not reduce the amount of energy generated)\n\nFOR ENERGY EFFICIENCY SOLUTIONS: enter positive number representing total energy reduced, 0 < X < 1 (e.g. HVAC efficiencies reduce the average annual energy consumption of buildings, by square meters of floor space; they still use the electric grid, but significantly less)\n\nFOR SOLUTIONS THAT CONSUME MORE ENERGY THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE: Use the next input, Total Annual Energy Used SOLUTION (e.g. electric vehicles use energy from the electric grid, whereas conventional vehicles use only fuel)",
        "excelref": "SolarPVUtil \"Advanced Controls\"!C159; Silvopasture \"Advanced Controls\"!C123"
    }, "<class 'float'>"],
    ["conv_annual_energy_used", {
        "vma_titles": ["CONVENTIONAL Total Energy Used per Functional Unit"],
        "subtitle": "",
        "tooltip": "Average Electricty Used CONVENTIONAL\nNOTE: for solutions that reduce electricity consumption per functional unit, enter the average electricity used per functional unit of the conventional technologies/practices.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!B159; Silvopasture \"Advanced Controls\"!B123"
    }, "<class 'float'>"],
    ["soln_annual_energy_used", {
        "vma_titles": ["SOLUTION Total Energy Used per Functional Unit"],
        "subtitle": "",
        "tooltip": "ALTERNATIVE APPROACH Annual Energy Used SOLUTION\nThis refers to the units of average energy used per year per functional unit installed.\n\nThis is an optional variable to be used in cases where a) the literature reports the energy use of the solution rather than energy efficiency; or b) the solution uses more electricity than the conventional technologies/practices.\n\nE.g. electric vehicles use energy from the electric grid, whereas conventional vehicles use only fuel",
        "excelref": "SolarPVUtil \"Advanced Controls\"!D159"
    }, "<class 'float'>"],
    ["conv_fuel_consumed_per_funit", {
        "vma_titles": ["CONVENTIONAL Fuel Consumed per Functional Unit"],
        "subtitle": "",
        "tooltip": "Fuel Consumed per CONVENTIONAL Functional Unit\nThis refers to the unit (default is Liters) of FUEL used per year per cumulative unit installed. The equation may need to be edited if your energy savings depend on the marginal unit installed rather than the cumulative units.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!F159; Silvopasture \"Advanced Controls\"!F123"
    }, "<class 'float'>"],
    ["soln_fuel_efficiency_factor", {
        "vma_titles": ["SOLUTION Fuel Efficiency Factor"],
        "subtitle": "",
        "tooltip": "Fuel Efficiency Factor - SOLUTION\nThis refers to the % fuel reduced by the SOLUTION relative to the CONVENTIONAL mix of technologies/practices. The Percent reduction is assumed to apply to the Conventional Fuel Unit, if different to the Solution Fuel Unit.\n\nFOR REPLACEMENT SOLUTIONS: enter 1 (e.g. electric vehicles fully replace fuel consumption with electricity use -- but be sure to add a negative value for Annual Energy Reduced from Electric Grid Mix!)\n\nFOR FUEL EFFICIENCY SOLUTIONS: enter positive number representing total fuel reduced, 0 < X < 1  (e.g. hybrid-electric vehicles partially replace fuel consumption with electricity use, it thus uses less fuel compared to conventional vehicles)\n\nFOR SOLUTIONS THAT CONSUME MORE FUEL THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE: enter negative number representing total additional fuel used, X < 0 (e.g. we hope solutions do not actually consume more fuel than the conventional practice, check with the senior research team if you run into this)",
        "excelref": "SolarPVUtil \"Advanced Controls\"!G159; Silvopasture \"Advanced Controls\"!G123"
    }, "<class 'float'>"],
    ["conv_fuel_emissions_factor", {
        "vma_titles": [],
        "subtitle": "",
        "tooltip": "direct fuel emissions per funit, conventional",
        "excelref": "SolarPVUtil \"Advanced Controls\"!I159"
    }, "<class 'float'>"],
    ["soln_fuel_emissions_factor", {
        "vma_titles": [],
        "subtitle": "",
        "tooltip": "direct fuel emissions per funit, solution",
        "excelref": "SolarPVUtil \"Advanced Controls\"!I163; DistrictHeating \"Advanced Controls\"!I144"
    }, "<class 'float'>"],
    ["conv_emissions_per_funit", {
        "vma_titles": ["CONVENTIONAL Direct Emissions per Functional Unit"],
        "subtitle": "",
        "tooltip": "Direct Emissions per CONVENTIONAL Functional Unit\nThis represents the direct CO2-eq emissions that result per functional unit that are not accounted for by use of the electric grid or fuel consumption.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!C174"
    }, "<class 'float'>"],
    ["soln_emissions_per_funit", {
        "vma_titles": ["SOLUTION Direct Emissions per Functional Unit"],
        "subtitle": "",
        "tooltip": "Direct Emissions per SOLUTION Functional Unit\nThis represents the direct CO2-eq emissions that result per functional unit that are not accounted for by use of the electric grid or fuel consumption.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!D174"
    }, "<class 'float'>"],
    ["ch4_is_co2eq", {}, "<class 'bool'>"],
    ["n2o_is_co2eq", {}, "<class 'bool'>"],
    ["co2eq_conversion_source", {}, "<class 'str'>"],
    ["ch4_co2_per_funit", {
        "vma_titles": ["CH4-CO2eq Tons Reduced"],
        "subtitle": "",
        "tooltip": "CH4-CO2eq Tons Reduced\nCO2-equivalent CH4 emitted per functional unit, in tons.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!I174"
    }, "<class 'float'>"],
    ["n2o_co2_per_funit", {
        "vma_titles": ["N2O-CO2eq Tons Reduced"],
        "subtitle": "",
        "tooltip": "N2O-CO2eq Tons Reduced\nCO2-equivalent N2O emitted per functional unit, in tons.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!J174"
    }, "<class 'float'>"],
    ["soln_indirect_co2_per_iunit", {
        "vma_titles": ["SOLUTION Indirect CO2 Emissions per Unit"],
        "subtitle": "",
        "tooltip": "Indirect CO2 Emissions per SOLUTION Implementation Unit\nCO2-equivalent indirect emissions per iunit, in tons.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!G174"
    }, "<class 'float'>"],
    ["conv_indirect_co2_per_unit", {
        "vma_titles": ["CONVENTIONAL Indirect CO2 Emissions per Unit"],
        "subtitle": "",
        "tooltip": "Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit\nNOTE: this represents the indirect CO2 emissions that result per implementation unit installed. The production, distribution, and installation of technologies/practices often generate their own emissions that are not associated with their function.\n\nE.g. the production of ICE vehicles is an energy- and resource-intensive endeavor that generates indirect emissions that must be accounted for.\n",
        "excelref": "SolarPVUtil \"Advanced Controls\"!F174"
    }, "<class 'float'>"],
    ["conv_indirect_co2_is_iunits", {}, "<class 'bool'>"],
    ["soln_lifetime_capacity", {
        "vma_titles": ["SOLUTION Lifetime Capacity"],
        "subtitle": "(use until replacement is required)",
        "tooltip": "Lifetime Capacity - SOLUTION\n\nNOTE: This is the average expected number of functional units generated by the SOLUTION throughout their lifetime before replacement is required. If no replacement time is discovered or applicable the fellow will default to 100 years.\n\nE.g. an electric vehicle will have an average number of passenger kilometers it can travel until it can no longer be used and a new vehicle is required. Another example would be an efficient HVAC system, which can only service a certain amount of floor space over a period of time before it will require replacement.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!E128"
    }, "<class 'float'>"],
    ["soln_avg_annual_use", {
        "vma_titles": ["SOLUTION Average Annual Use"],
        "subtitle": "(annual use)",
        "tooltip": "Average Annual Use - SOLUTION\n\nNOTE:  Average Annual Use is the average annual use of the technology/practice, in functional units per implementation unit. This will likely differ significantly based on location, be sure to note which region the data is coming from. If data varies substantially by region, a weighted average may need to be used.\n\nE.g. the average annual number of passenger kilometers (pkm) traveled per electric vehicle.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!F128"
    }, "<class 'float'>"],
    ["conv_lifetime_capacity", {
        "vma_titles": ["CONVENTIONAL Lifetime Capacity"],
        "subtitle": "(use until replacement is required)",
        "tooltip": "Lifetime Capacity - CONVENTIONAL\n\nNOTE: This is the average expected number of functional units generated by the CONVENTIONAL mix of technologies/practices throughout their lifetime before replacement is required.  If no replacement time is discovered or applicable, please use 100 years.\n\nE.g. a vehicle will have an average number of passenger kilometers it can travel until it can no longer be used and a new vehicle is required. Another example would be an HVAC system, which can only service a certain amount of floor space over a period of time before it will require replacement.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!E95"
    }, "<class 'float'>"],
    ["conv_avg_annual_use", {
        "vma_titles": ["CONVENTIONAL Average Annual Use"],
        "subtitle": "(annual use)",
        "tooltip": "Average Annual Use - CONVENTIONAL\n\nNOTE:  Average Annual Use is the average annual use of the technology/practice, in functional units per implementation unit. This will likely differ significantly based on location, be sure to note which region the data is coming from. If data varies substantially by region, a weighted average may need to be used.\n\nE.g. the average annual number of passenger kilometers (pkm) traveled per conventional vehicle.\n",
        "excelref": "SolarPVUtil \"Advanced Controls\"!F95"
    }, "<class 'float'>"],
    ["report_start_year", {}, "<class 'int'>"],
    ["report_end_year", {}, "<class 'int'>"],
    ["soln_var_oper_cost_per_funit", {
        "vma_titles": ["SOLUTION Variable Operating Cost (VOM) per Functional Unit"],
        "subtitle": "(functional units)",
        "tooltip": "SOLUTION Variable Operating Cost (VOM)\nNOTE: This is the annual operating cost per functional unit, derived from the SOLUTION. In most cases this will be expressed as a cost per 'some unit of energy'.\n\nE.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this can be considered the weighted average price of fuel per passenger kilometer.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!H128"
    }, "<class 'float'>"],
    ["soln_fixed_oper_cost_per_iunit", {
        "vma_titles": ["SOLUTION Operating Cost per Functional Unit per Annum", "SOLUTION Fixed Operating Cost (FOM)"],
        "subtitle": "(per ha per annum)",
        "tooltip": "SOLUTION Operating Cost per Functional Unit per Annum\n\nNOTE: This is the Operating Cost per functional unit, derived from the SOLUTION. In most cases this will be expressed as a cost per 'hectare of land'.\n\nThis annualized value should capture both the variable costs for maintaining the SOLUTION practice as well as the fixed costs. The value should reflect the average over the reasonable lifetime of the practice.",
        "tooltipFIXME": "SOLUTION Operating Cost per Functional Unit per Annum\n\nNOTE: This is the annual operating cost per implementation unit, derived from the SOLUTION.  In most cases this will be expressed as a cost per 'some unit of installation size' E.g., $10,000 per kw. In terms of transportation, this can be considered the total insurance, and maintenance cost per car.\n\nPurchase costs can be amortized here or included as a first cost, but not both.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!I128; Silvopasture \"Advanced Controls\"!C92"
    }, "typing.Any"],
    ["soln_fuel_cost_per_funit", {}, "<class 'float'>"],
    ["conv_var_oper_cost_per_funit", {
        "vma_titles": ["CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit"],
        "subtitle": "(functional units)",
        "tooltip": "CONVENTIONAL Variable Operating Cost (VOM)\n\nNOTE: This is the annual operating cost per functional unit, derived from the CONVENTIONAL mix of technologies. In most cases this will be expressed as a cost per 'some unit of energy'.\n\nE.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this can be considered the weighted average price of fuel per passenger kilometer.",
        "excelref": "SolarPVUtil \"Advanced Controls\"!H95"
    }, "<class 'float'>"],
    ["conv_fixed_oper_cost_per_iunit", {
        "vma_titles": ["CONVENTIONAL Operating Cost per Functional Unit per Annum", "CONVENTIONAL Fixed Operating Cost (FOM)"],
        "subtitle": "(per ha per annum)",
        "tooltip": "CONVENTIONAL Operating Cost per Functional Unit per Annum\n\nNOTE: This is the Operating Cost per functional unit, derived from the CONVENTIONAL mix of technologies/practices.  In most cases this will be expressed as a cost per 'hectare of land'.\n\nThis annualized value should capture the variable costs for maintaining the CONVENTIONAL practice, as well as  fixed costs. The value should reflect the average over the reasonable lifetime of the practice.\n\n",
        "excelref": "SolarPVUtil \"Advanced Controls\"!I95; Silvopasture \"Advanced Controls\"!C77"
    }, "typing.Any"],
    ["conv_fuel_cost_per_funit", {}, "<class 'float'>"],
    ["npv_discount_rate", {}, "<class 'float'>"],
    ["emissions_use_co2eq", {}, "<class 'bool'>"],
    ["emissions_grid_source", {}, "<class 'str'>"],
    ["emissions_grid_range", {}, "<class 'str'>"],
    ["soln_ref_adoption_regional_data", {}, "<class 'bool'>"],
    ["soln_pds_adoption_regional_data", {}, "<class 'bool'>"],
    ["soln_ref_adoption_basis", {}, "<class 'str'>"],
    ["soln_ref_adoption_custom_name", {}, "<class 'str'>"],
    ["soln_pds_adoption_basis", {}, "<class 'str'>"],
    ["soln_pds_adoption_custom_name", {}, "<class 'str'>"],
    ["soln_pds_adoption_custom_high_sd_mult", {}, "<class 'float'>"],
    ["soln_pds_adoption_custom_low_sd_mult", {}, "<class 'float'>"],
    ["soln_pds_adoption_prognostication_source", {}, "<class 'str'>"],
    ["soln_pds_adoption_prognostication_trend", {}, "<class 'str'>"],
    ["soln_pds_adoption_prognostication_growth", {}, "<class 'str'>"],
    ["pds_source_post_2014", {}, "<class 'str'>"],
    ["ref_source_post_2014", {}, "<class 'str'>"],
    ["source_until_2014", {}, "<class 'str'>"],
    ["ref_adoption_use_pds_years", {}, "typing.List[int]"],
    ["pds_adoption_use_ref_years", {}, "typing.List[int]"],
    ["pds_base_adoption", {}, "typing.List[tuple]"],
    ["ref_base_adoption", {}, "typing.Dict"],
    ["pds_adoption_final_percentage", {}, "typing.List[tuple]"],
    ["pds_adoption_s_curve_innovation", {}, "typing.List[tuple]"],
    ["pds_adoption_s_curve_imitation", {}, "typing.List[tuple]"],
    ["tco2eq_reduced_per_land_unit", {
        "vma_titles": ["t CO2-eq (Aggregate emissions) Reduced per Land Unit"],
        "subtitle": "(t CO2-eq / ha)",
        "tooltip": "t CO2-eq (Aggregate emissions) Reduced per Land Unit\nNOTE: This is the CO2-equivalent reduced per land unit (million Hectare).",
        "excelref": "ForestProtection \"Advanced Controls\"!B138"
    }, "typing.Any"],
    ["tco2eq_rplu_rate", {}, "<class 'str'>"],
    ["tco2_rplu_rate", {}, "<class 'str'>"],
    ["tn2o_co2_rplu_rate", {}, "<class 'str'>"],
    ["tch4_co2_rplu_rate", {}, "<class 'str'>"],
    ["tco2_reduced_per_land_unit", {
        "vma_titles": ["t CO2 Reduced per Land Unit"],
        "subtitle": "(t CO2 / ha)",
        "tooltip": "t CO2 Reduced per Land Unit\nNOTE: This is the CO2 reduced per land unit (million Hectare).",
        "excelref": "ForestProtection \"Advanced Controls\"!C148"
    }, "typing.Any"],
    ["tn2o_co2_reduced_per_land_unit", {
        "vma_titles": ["t N2O-CO2-eq Reduced per Land Unit"],
        "subtitle": "(t N2O-CO2-eq / ha)",
        "tooltip": "t N2O-CO2-eq Reduced per Land Unit\nNOTE: This is the N2O reduced per land unit (million Hectare) but converted to CO2-eq.",
        "excelref": "ForestProtection \"Advanced Controls\"!D148"
    }, "typing.Any"],
    ["tch4_co2_reduced_per_land_unit", {
        "vma_titles": ["t CH4-CO2-eq Reduced per Land Unit"],
        "subtitle": "",
        "tooltip": "t CH4-CO2-eq Reduced per Land Unit\nNOTE: This is the CH4 reduced per land unit (million Hectare) but converted to CO2-eq.",
        "excelref": "ForestProtection \"Advanced Controls\"!E148"
    }, "typing.Any"],
    ["emissions_use_agg_co2eq", {}, "<class 'bool'>"],
    ["seq_rate_global", {
        "vma_titles": ["Sequestration Rates"],
        "subtitle": "(t C / ha /year)",
        "tooltip": "Sequestration Rate for All Land or All of Special Land\nNOTE: Once a  Rate is entered here, it would be used. If rates are available for each Thermal-Humidity Regime, leave this blank.",
        "ecelref": "\"Advanced Controls\"!B173 (Land models)"
    }, "typing.Any"],
    ["seq_rate_per_regime", {}, "typing.Dict"],
    ["degradation_rate", {
        "vma_titles": ["Growth Rate of Land Degradation"],
        "subtitle": "",
        "tooltip": "Growth Rate of Land Degradation\nNOTE: This is the rate of degradation of unprotected land (or \"At Risk\" land that is neither protected nor already degraded. This number should exclude the Disturbance Rate if that is also entered.",
        "excelref": "ForestProtection \"Advanced Controls\"!B187"
    }, "typing.Any"],
    ["disturbance_rate", {
        "vma_titles": ["Disturbance Rate"],
        "subtitle": "",
        "tooltip": "Disturbance Rate\nNOTE: This is the annual percent of some output that fails for some reason (possibly due to weather, human activities, etc). It applies ONLY to land adopted/protected with the SOLUTION, and affects degraded land, direct emissions, sequestration and  yield. The SOLUTION adoption remains unaffected.\n\nEnsure that the Growth Rate of Land degradation does not already account for the Disturbance Rate if it is entered here.",
        "excelref": "TropicalForests. \"Advanced Controls\"!I173"
    }, "typing.Any"],
    ["global_multi_for_regrowth", {}, "<class 'float'>"],
    ["soln_expected_lifetime", {}, "<class 'float'>"],
    ["conv_expected_lifetime", {}, "<class 'float'>"],
    ["yield_from_conv_practice", {
        "vma_titles": ["Yield from CONVENTIONAL Practice"],
        "subtitle": "(kg / ha /yr)",
        "tooltip": "Yield from CONVENTIONAL Practice",
        "excelref": "\"Advanced Controls\"!G77 (Land models)"
    }, "typing.Any"],
    ["yield_gain_from_conv_to_soln", {
        "vma_titles": ["Yield Gain (% Increase from CONVENTIONAL to SOLUTION)"],
        "subtitle": "%",
        "tooltip": "Yield Gain (% Increase from CONVENTIONAL to SOLUTION)",
        "excelref": "\"Advanced Controls\"!G92 (Land models)"
    }, "typing.Any"],
    ["use_custom_tla", {}, "<class 'bool'>"],
    ["custom_tla_fixed_value", {}, "<class 'float'>"],
    ["harvest_frequency", {}, "<class 'float'>"],
    ["carbon_not_emitted_after_harvesting", {
        "vma_titles": ["Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing"],
        "subtitle": "(t C/ha)",
        "tooltip": "Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing\n",
        "excelref": "Afforestation \"Advanced Controls\"!H173"
    }, "typing.Any"],
    ["avoided_deforest_with_intensification", {
        "vma_titles": ["Avoided Deforested Area With Increase in Agricultural Intensification"],
        "subtitle": "",
        "tooltip": "Avoided Deforested Area With Increase in Agricultural Intensification",
        "excelref": "Women Smallholders \"Advanced Controls\"!E205"
    }, "typing.Any"],
    ["delay_protection_1yr", {}, "<class 'bool'>"],
    ["delay_regrowth_1yr", {}, "<class 'bool'>"],
    ["include_unprotected_land_in_regrowth_calcs", {}, "<class 'bool'>"],
    ["land_annual_emissons_lifetime", {}, "<class 'bool'>"],
    ["tC_storage_in_protected_land_type", {
        "vma_titles": ["t C storage in Protected Landtype"],
        "subtitle": "",
        "tooltip": "t C storage in Protected Landtype",
        "excelref": ""
    }, "typing.Any"]
]

