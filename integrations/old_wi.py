            from pathlib import Path
            import pandas as pd
            from model import sma
            from model import tam
            from model import dd
            from .integration_base import *

            THISDIR = Path(__file__).parent
            DATADIR = THISDIR/"data"/"msw"

            # Excel notes: Excel references refer to the Sheet MSW Integration Calcs (PDS1, 2 or 3) unless
            # otherwise noted.  Also, not all Integration Calcs tables are implemented, if their results
            # are used in only one location, or if their results are not used by the integration results or
            # other featured calculations.

            # ########################################################################################################################
            #                                              INPUTS
            # These values are writable, so experimentation may be done by setting them to other values before calling the
            # integration functions.  Values initialized to None here are set to default values by the function 
            # load_default_values().

            waste_tam : pd.DataFrame = None
            """Total addressable market for waste products.  Years x Regions df
            Units: Million tonnes generated."""
            # Excel Table 1

            # COMPOST

            compost_adoption : pd.DataFrame = None
            """Worldwide compost adoption for three scenarios.  Years x PDS.
            Retrieved from composting model.
            Units: Million tonnes waste composted."""
            # Excel Compost!B
            composting_scenario_names = ["PDS1","PDS2","PDS3"]

            compostable_proportion : pd.Series = None
            """Estimate of proportion of waste worldwide that is compostable. Years series.
            Units: % (i.e fraction * 100)"""
            # Excel Compost!J

            regional_organic_fraction = pd.Series({
                'OECD90': 0.39236288,
                'Eastern Europe': 0.02820816,
                'Asia (Sans Japan)': 0.16053698,
                'Middle East and Africa': 0.28956111,
                'Latin America': 0.12904009,
                'China': 0.13109840,
                'India': 0.16185183,
                'EU': 0.12005864,
                'USA': 0.07888291
            })
            """Regional proportion of organic waste.  Regions series.
            Derived the Intergovernmental Panel on Climate Change (IPCC), 2006 and Hoornweg & Bhada-Tata (2012).
            Units: fraction"""
            # Excel P5:X5
            # Note the regional waste values are not actually used.  They are provided for informational value only.

            # RECYCLING

            recycling_adoption: pd.DataFrame = None
            recycling_scenario_names = ["PDS1","PDS2","PDS3"]

            recyclable_proportion: pd.Series = None
            """Estimate of proportion of waste worldwide that is recyclable.  Years series.
            Units: % (i.e fraction * 100)"""
            # Excel 'H&C Recycling'!K

            regional_recyclable_fraction = pd.Series({
                'OECD90': 0.295212,
                'Eastern Europe': 0.047083,
                'Asia (Sans Japan)': 0.144916,
                'Middle East and Africa': 0.395601,
                'Latin America': 0.117187,
            })
            """Regional portion of recyclable waste.  Regions series.
            Units: fraction"""
            # Excel AC5:AG5
            # Note the regional waste values are not actually used.  They are provided for informational value only.

            # PAPER

            paper_tam: pd.DataFrame = None
            """Worldwide paper collected (and available for recycling) by year.  Years series.
            Retrieved from recycledpaper model."""
            # Excel Paper!C

            paper_adoption: pd.DataFrame = None
            """Worldwide paper recycled in three scenarios.  Years x PDS.
            Retreived from recycledpaper model."""
            # Excel Paper!F
            paper_scenario_names = ["PDS1","PDS2","PDS3"]

            paper_recycling_ratio = pd.Series({'PDS1': 1.29666666666667, 'PDS2': 1.29666666666667, 'PDS3': 1.1154056516757})
            """Amount of recovered paper required to produce 1 unit of recycled paper product,
            over three scenarios"""
            # Excel Paper!G3, G58, G113
            # Should be obtained from recycledpaper model

            # INSULATION

            insulation_msw_consumption: pd.DataFrame = None
            """Amount of cellulose material consumed for insulation adoption for three scenarios.  Years x PDS.
            Units: Million tonnes."""
            # Excel Paper!I, derived from
            # Insulation solution model: Biomass!I, Biomass!L, Biomass!O
            insulation_scenario_names = ["PDS1","PDS2","PDS3"]

            # PLASTICS

            plastics_tam : pd.Series = None
            """Total plastics market worldwide. Years series.
            From bioplastics model.
            Units: Million tonnes."""
            # Excel Table 5

            proportion_plastics_in_waste = 0.69
            """Proportion of yearly plastic production that ends up in waste.
            Estimated from waste TAM, plastics TAM and What a Waste 2.0 estimate that 12% of waste in 2016 is plastic.
            (1932.45927 * 0.12) / 335 = 0.6922
            Units: fraction"""
            # Excel Bioplastics!AI12
            # Note: the excel had a mistake here: while the text clearly indicates an intent to divide by the Waste TAM[2016],
            # the Excel divides by the Waste TAM[2014].  I have corrected that mistake.  This drops the estimate from 78% to 69%
            # If you want to match the Excel behavior, substitute 0.78 for this value.

            bioplastics_adoption : pd.DataFrame = None
            """Worldwide bioplastics adoption for three scenarios.  Years x PDS df.
            Units: Million tonnes"""
            # Excel Table 10
            bioplastics_scenario_names = ["PDS1","PDS2","PDS3"]

            # bioplastic_maximum_production: pd.DataFrame = None
            # """Maximum Bioplastic Production.  Years x PDS.
            # Units Million tonnes"""
            # # Excel Bioplastics!C

            proportion_bioplastics_compostable : pd.Series = None
            """Proportion of bioplastics that are compostable worldwide.  Years series.
            Units: fraction."""
            # Excel Table 11

            # FOOD

            food_waste : pd.DataFrame = None
            """Food waste worldwide for three scenarios.  Years x PDS df.
            Units: Million tonnes."""
            # Excel 'Food System Summary'!G, E, H

            food_waste_reduction : pd.DataFrame = None
            """Worldwide food waste reduction for three scenarios.  Years x PDS df.
            Includes only food waste reduction in 'Distribution' and 'Consumption' stages of Food System.
            Units: Million tonnes"""
            # Excel Table 7.


            # WASTE TO ENERGY

            waste_to_energy_adoption : pd.DataFrame = None
            """Adoption of waste to energy technologies for three scenarios.  Years x PDS df.
            Units: Terawatt Hours"""
            waste_to_energy_scenario_names = ["PDS1","PDS2","PDS3"]

            waste_to_energy_msw_consumption: pd.DataFrame = None
            """Waste-to-Energy consumption expressed in tons MSW.  Years x """

            weighted_average_DOC_fraction = pd.Series({'organic': 0.198253844, 'recyclable': 0.280060046, 'remainder': 0.342912545})
            """DOC is dissolved carbon content?? Not sure."""
            # In the Excel workbook, these are derived from formulae.  Values 'WTE Tonnes and Composition'!R31:R33

            weighted_average_LHV = pd.Series({'organic': 1.499261376, 'recyclable': 3.549477827, 'remainder': 2.120720855})
            """Lower heating value of different types of waste materials."""   

            waste_to_energy_efficiency_factor = 0.2367
            # Excel 'WTE Tonnes and Composition'!D62

            # LANDFILL METHANE

            landfill_methane_adoption : pd.DataFrame = None
            landfill_methane_scenario_names = ["PDS1","PDS2","PDS3"]


            # END INPUTS ----------------------------

            def load_default_values(forceAll=False):
                """Load values for inputs.  
                If the input is already set to a value, it is not overwritten, unless forceAll is True"""

                global waste_tam
                if waste_tam is None or forceAll:
                    # NOTE: should be obtained from waste model when we have it.
                    tamconfig = tam.make_tam_config()
                    tamsources = sma.SMA.read( DATADIR, "waste_tam", read_data=False ).as_tamsources( DATADIR )
                    waste_tam = tam.TAM(tamconfig, tamsources, tamsources).ref_tam_per_region()


                global compost_adoption
                if compost_adoption is None or forceAll:
                    compost_adoption = load_solution_adoptions("composting", composting_scenario_names)   
                global compostable_proportion
                if compostable_proportion is None or forceAll:
                    # This is represented in a part of the composting model that we don't represent yet.
                    # When we do, we should fetch it from there.
                    compostable_proportion = sma.SMA.read( DATADIR, "organic_compost_sma" ).summary(case='S1')['World']


                global recycling_adoption
                if recycling_adoption is None or forceAll:
                    recycling_adoption = load_solution_adoptions("hcrecycling", recycling_scenario_names)
                global recyclable_proportion
                if recyclable_proportion is None or forceAll:
                    # This is represented in a part of hcrecycling model that we don't represent yet.
                    # When we do, we should fetch it from there.
                    recyclable_proportion = sma.SMA.read( DATADIR, "hc_percent_recyclable_sma" ).summary(case='S1')['World']


                global paper_tam
                if paper_tam is None or forceAll:
                    paper_tam = load_solution_tam("recycledpaper", paper_scenario_names[1])
                global paper_adoption
                if paper_adoption is None or forceAll:
                    paper_adoption = load_solution_adoptions("recycledpaper", paper_scenario_names)
                
                global insulation_msw_consumption
                if insulation_msw_consumption is None or forceAll:
                    pds1 = factory.load_scenario("insulation",insulation_scenario_names[0])
                    pds2 = factory.load_scenario("insulation",insulation_scenario_names[1])
                    pds3 = factory.load_scenario("insulation",insulation_scenario_names[2])
                    insulation_msw_consumption = pd.DataFrame({'PDS1': pds1.adoption_as_material_mass(),
                                                            'PDS2': pds2.adoption_as_material_mass(),
                                                            'PDS3': pds3.adoption_as_material_mass()})

                global plastics_tam
                if plastics_tam is None or forceAll:
                    # Load from bioplastics model
                    plastics_tam = load_solution_tam("bioplastic", bioplastics_scenario_names[1])
                global bioplastics_adoption
                if bioplastics_adoption is None or forceAll:
                    # Load from bioplastics model
                    # NOTE: bioplastic is currently failing adoption tests, so these results are suspect.
                    bioplastics_adoption = load_solution_adoptions("bioplastic", bioplastics_scenario_names)
                global proportion_bioplastics_compostable
                if proportion_bioplastics_compostable is None or forceAll:
                    # The excel claims this comes from the bioplastics model, but I don't see it there.
                    # Even if it were there that would be a part of the model we haven't implemented yet.
                    # NOTE: should be obtained from bioplastics model, if/when it is implemented there.
                    ppc_sma = sma.SMA.read( DATADIR, "percent_plastic_compostable_sma" )
                    proportion_bioplastics_compostable = ppc_sma.summary(case='S1')['World']
                # Omitting maximum production because it doesn't seem to affect results currently, and I don't
                # really understand it.
                # global bioplastic_maximum_production
                # if bioplastic_maximum_production is None or forceAll:
                #     bioplastic_maximum_production = pd.read_csv( DATADIR/"maximum_bioplastic_production.csv" )


                global food_waste
                if food_waste is None or forceAll:
                    # NOTE: should be obtained from food model when we have it.
                    food_waste = pd.read_csv( DATADIR / "food_waste.csv", index_col="Year" )   
                global food_waste_reduction
                if food_waste_reduction is None or forceAll:
                    # NOTE: should be obtained from food model when we have it.
                    food_waste_reduction = pd.read_csv( DATADIR / "food_waste_reduction.csv", index_col="Year" )


                global waste_to_energy_adoption
                if waste_to_energy_adoption is None or forceAll:
                    waste_to_energy_adoption = load_solution_adoptions("wastetoenergy", waste_to_energy_scenario_names)
                global waste_to_energy_msw_consumption
                if waste_to_energy_msw_consumption is None or forceAll:
                    # default initialization will be updated with more LHV specificity later.
                    waste_to_energy_msw_consumption = waste_to_energy_adoption * weighted_average_LHV.mean() * waste_to_energy_efficiency_factor
                
                global landfill_methane_adoption
                if landfill_methane_adoption is None or forceAll:
                    landfill_methane_adoption = load_solution_adoptions("landfillmethane", landfill_methane_scenario_names)



            # #########################################################################################################################
            #  
            #                                            Intermediate Calculations
            # 

            def get_base_organic_waste() -> pd.DataFrame:
                """Total amount of organic waste.  Years x Regions df.
                Using waste fraction data from the Intergovernmental
                Panel on Climate Change (IPCC), 2006 and Hoornweg & Bhada-Tata (2012) a forecast for the
                organic fraction of MSW is devloped for Drawdown regions and the World. Food waste and
                "green material" is considered organic fraction. Soiled paper may be considered "green
                material" in some regions, but paper waste is allocated elsewhere. Green material includes
                landscape waste and certain debris. This forecast becomes the TAM for Composting and is
                directly affected by reductions in food waste and an increase in Bioplastics production and
                a simulataneous, but distinct forecast in compostability of bioplastic. When bioplastic is
                considered compostable it moves to the organic fraction.
                Units: Million tonnes."""
                # Excel Table 2
                # Note the regional waste values are not actually used.  They are provided for informational value only.
                
                # column A:
                compost_organic_fraction_world = waste_tam['World'] * compostable_proportion / 100
                # the regional columns are an outer product with regional_organic_fraction
                op = series_outer_product(compost_organic_fraction_world, regional_organic_fraction)
                return pd.concat([compost_organic_fraction_world,op], axis=1).loc[2014:]


            def get_base_recyclable_waste() -> pd.DataFrame:
                """Total amount of recyclable waste, excluding paper.  Years x Regions df.
                This is developed from multiple sources including  the Intergovernmental
                Panel on Climate Change (IPCC), 2006; Hoornweg & Bhada-Tata (2012);Bahor, et al(2009);
                Hoornweg et al (2015).
                Units: Million tonnes."""
                # Excel Table 3
                # Note the regional waste values are not actually used.  They are provided for informational value only.

                # table 3, column A
                recyclable_portion_world = waste_tam['World'] * recyclable_proportion / 100
                # the regional columns are an outer product with regional_recyclable_fraction
                op = series_outer_product(recyclable_portion_world, regional_recyclable_fraction)
                return pd.concat([recyclable_portion_world,op], axis=1).loc[2014:]

            def get_waste_remainder_1() -> pd.DataFrame:
                """Waste TAM less organics and recyclables.  Years x Regions df.
                This includes paper.
                Units: Million tonnes."""
                # Excel Table 4
                # Note the regional waste values are not actually used.  They are provided for informational value only.
                remainder = waste_tam - get_base_organic_waste() - get_base_recyclable_waste()
                return remainder.reindex(columns=dd.REGIONS)

            def get_base_plastic_waste() -> pd.Series:
                """Amount of worldwide plastic waste per year.  Years series.
                Not all plastic produced each year enters MSW.  This estimates
                plastic in MSW based on benchmark from World Bank 2018. 12% of MSW is plastics.
                Units: million tonnes."""
                # Excel Table 5
                return plastics_tam * proportion_plastics_in_waste

            def get_waste_less_food_reduction() -> pd.DataFrame:
                """The worldwide waste tam corrected for food waste reduction for three scenarios.
                Year x (PDS1,PDS2,PDS3) df.
                Units: Million tonnes."""
                # Excel Table 8, 12
                return series_sub_df(waste_tam['World'], food_waste_reduction)

            def get_updated_organic_waste() -> pd.DataFrame:
                """Total World Organic MSW after reduction in Food Waste and with addition of a % of
                bioplastics for three scenarios.  Years x PDS df
                This impacts the TAM for Composting.
                Units: Million tonnes."""
                # Excel Table 13 (including computation for Table 9)
                organic_waste_portion = get_base_organic_waste()['World']
                organic_msw_less_food_reduction = series_sub_df(organic_waste_portion, food_waste_reduction)
                compostable_bioplastics = df_mult_series(bioplastics_adoption, proportion_bioplastics_compostable)
                return  organic_msw_less_food_reduction + compostable_bioplastics

            def get_updated_recyclable_waste() -> pd.DataFrame:
                """Total World Recyclable MSW after reduction of compostible share of bioplastics for three
                scenarios.  Years x PDS df.
                Assumes that all bioplastics would have been categorized as recyclable.
                Units: Million tonnes."""
                # Excel Table 14
                compostable_msw = get_base_recyclable_waste()['World']
                compostable_bioplastics = df_mult_series(bioplastics_adoption, proportion_bioplastics_compostable)
                return series_sub_df(compostable_msw, compostable_bioplastics)

            def get_waste_remainder_2() -> pd.DataFrame:
                """Total World Remainder MSW after subtraction of reduced food waste and fraction mix change due
                to bioplastics (not Organics and Not Recyclables) for three scenarios. DOES include Paper.
                Years x PDS df.
                Units: Million tonnes."""
                # Excel Table 15
                x = get_waste_less_food_reduction()
                y = get_updated_organic_waste()
                z = get_updated_recyclable_waste()
                return x - y - z


            def get_recyclable_paper_msw_consumption() -> pd.DataFrame:
                """Return the amount of waste paper consumed in order to produce the amount of recycled paper adopted,
                for three scenarios"""
                # Excel Table 21 column S
                # This should be moved into recycledpaper model instead of being here.
                return paper_recycling_ratio * paper_adoption


            def get_waste_remainder_proportions() -> pd.DataFrame:
                """Return proportions of waste that are organic, recyclable or other, _after_ accounting for
                waste removed for composting and recycling (including paper recycling and insulation).
                Year x (PDS x (organic,recyclable,other)):  columns are a PDS, waste-type multi-index"""
                # Excel Table 22
                # Note: adoptions here should be *post* any feedstock limitation adjustment
                remaining_organic_waste = get_updated_organic_waste() - compost_adoption
                remaining_recyclable_waste = get_updated_recyclable_waste() - recycling_adoption
                remainder_waste = get_waste_remainder_2() - get_recyclable_paper_msw_consumption() - insulation_msw_consumption
                total = remaining_organic_waste + remaining_recyclable_waste + remainder_waste  # This also equals get_waste_remainder_3()
                
                # convert from sums to proportions
                remaining_organic_proportion = remaining_organic_waste / total
                remaining_recyclable_proportion = remaining_recyclable_waste / total
                remainder_proportion = remainder_waste / total

                # put it all together
                return pd.concat({'organic': remaining_organic_proportion, 
                                'recyclable': remaining_recyclable_proportion,
                                'remainder': remainder_proportion}, axis=1) .swaplevel(axis=1).sort_index(axis=1)


            def get_waste_remainder_3() -> pd.DataFrame:
                """Total World Remainder MSW after previous adjustments, and after accounting for MSW consumed by composting,
                hcrecycling, recycledpaper and insulation"""
                # Excel Table 22 col V
                x = compost_adoption
                y = recycling_adoption
                z = get_recyclable_paper_msw_consumption()
                q = insulation_msw_consumption
                return get_waste_less_food_reduction() - x - y - z - q



            def get_expected_waste_lhv() -> pd.DataFrame:
                """Return the expected LHV value for the updated waste tam, based on LHV values for its organic, recyclable and
                other components"""
                # Excel Table 23  
                # The calculation is: multiply each column by the appropriate LHV for the waste type, then sum across all waste types,
                # to yield an average.
                # I'm sure there's some super elegant pandas way to do this, but this works.
                breakout_lhv = get_waste_remainder_proportions()
                fn = lambda col : (breakout_lhv[col]*weighted_average_LHV).sum(axis=1)
                return pd.concat( {'PDS1': fn('PDS1'), 'PDS2': fn('PDS2'), 'PDS3': fn('PDS3')}, axis=1 )


            # #########################################################################################################################
            #  
            #                                                Integration Steps
            # 

            def check_feedstock_limited_solutions() -> dict:
                """Return a dictionary mapping solutions to their overshoot (the degree to which their adoption exceeds
                available feedstock).   Note this does not take into account the interactions between them, """
                pairs = {"composting" : (compost_adoption, get_updated_organic_waste()),
                        "recycling" : (recycling_adoption, get_updated_recyclable_waste()),
                        "wte": (waste_to_energy_msw_consumption, get_waste_remainder_3())}
                result = {}
                for solution in pairs:
                    (adoption, feedstock) = pairs[solution]
                    overshoot = (adoption-feedstock)
                    if (overshoot > 0).any(axis=None):
                        result[solution] = overshoot.clip(lower=0.0)
                return result


            def update_feedstock_limited_adoptions():
                """Update the _in memory_ adoptions of any feedstock limited solutions to max out at the feedstock
                limitation.  Does not affect actual solution scenarios.  The order of updates is important;
                earlier updates may affect results for later updates.  The results *should* be a fixed point, however
                (i.e. running update multiple times should yield the same result)."""

                global compost_adoption
                feedstock = get_updated_organic_waste()
                newadoption = compost_adoption.combine(feedstock, np.minimum)
                if not df_isclose(compost_adoption, newadoption):
                    print("compost adoption updated")
                    compost_adoption = newadoption

                global recycling_adoption
                feedstock = get_updated_recyclable_waste()
                newadoption = recycling_adoption.combine(feedstock, np.minimum)
                if not df_isclose(recycling_adoption, newadoption):
                    print("recycling adoption updated")
                    recycling_adoption = newadoption
                
                # The excel model doesn't have feedstock limitation checks for paper or insulation.
                # We should add those, I think.

                global waste_to_energy_adoption
                global waste_to_energy_msw_consumption
                # waste_to_energy_adoption is expressed in TwH, msw_consumption in MMT.
                # we compare consumption first, then update adoption accordingly
                feedstock = get_waste_remainder_3()
                lhvprojection = get_expected_waste_lhv()
                waste_to_energy_consumption = waste_to_energy_adoption * lhvprojection * waste_to_energy_efficiency_factor
                newconsumption = waste_to_energy_consumption.combine(feedstock, np.minimum)
                if not df_isclose(waste_to_energy_msw_consumption, newconsumption):
                    print("wastetoenergy adoption updated")
                    waste_to_energy_msw_consumption = newconsumption
                    waste_to_energy_adoption = waste_to_energy_msw_consumption / (lhvprojection * waste_to_energy_efficiency_factor)


            def update_solutions():
                """Push updated results back to solutions, updating adoptions and scenarios."""

                from solution import composting
                composting.Scenario.update_adoptions(composting_scenario_names, compost_adoption)

                from solution import hcrecycling
                hcrecycling.Scenario.update_adoptions(recycling_scenario_names, recycling_adoption)

                from solution import wastetoenergy
                wastetoenergy.Scenario.update_adoptions(waste_to_energy_scenario_names, waste_to_energy_adoption)
                

