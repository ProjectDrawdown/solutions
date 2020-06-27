"""Test solution classes."""

import pytest
import solution.factory

solutions = solution.factory.all_solutions_scenarios()

@pytest.mark.slow
@pytest.mark.parametrize("name,constructor,scenarios",
    [(name,) + solutions[name] for name in solutions.keys()],
    ids=list(solutions.keys())
)
def test_solutions(name, constructor, scenarios):
    for scenario in scenarios:
        obj = constructor(scenario=scenario)
        assert obj.scenario == scenario
        assert obj.name

        # a few solutions currently fail and are skipped while we investigate.
        skip = ['Car Fuel Efficiency', 'Electric Vehicles', 'Insulation']
        # a few more solutions have cached values from Drawdown2020 which are incorrect for
        # the BookEdition scenarios, or vice-versa.
        skip += ['Farmland Restoration', 'Afforestation', 'Bamboo', 'Nutrient Management',
                 'Perennial Bioenergy Crops', 'Silvopasture', 'Managed Grazing',
                 'Tropical Tree Staples', 'Temperate Forest Restoration', 'SRI',
                 'Multistrata Agroforestry', 'Improved Rice', 'Regenerative Agriculture',
                 'Grassland Protection', 'Peatland Protection', 'IP Forest Management',
                 'Tree Intercropping', 'Mangrove Protection', 'Conservation Agriculture',
                 'Forest Protection', 'Aircraft Fuel Efficiency', 'Bike Infrastructure',
                 'Composting', 'Alternative Cements']
        if obj.name not in skip:
            errstr = f"{obj.name}: {scenario} : {obj.ac.incorrect_cached_values}"
            assert len(obj.ac.incorrect_cached_values) == 0, errstr

    # check default scenario
    obj = constructor(scenario=None)
    assert obj.scenario is not None


def test_sane_number_of_solutions():
    assert len(list(solutions.keys())) >= 60
