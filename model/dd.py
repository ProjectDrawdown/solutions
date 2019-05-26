""" To maintain consistency, we import these common variables where they occur in the model """

REGIONS = [
    'World',  # sum of main regions
    'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',  # main regions
    'China', 'India', 'EU', 'USA'  # special countries
]
MAIN_REGIONS = REGIONS[1:6]
SPECIAL_COUNTRIES = REGIONS[6:]

# Land
THERMAL_MOISTURE_REGIMES = ['Tropical-Humid', 'Temperate/Boreal-Humid', 'Tropical-Semi-Arid',
                            'Temperate/Boreal-Semi-Arid', 'Global Arid', 'Global Arctic']

# Ocean
OCEAN_REGIONS = ['World'] + MAIN_REGIONS + ['ABNJ'] + SPECIAL_COUNTRIES  # ocean model has one extra region
THERMAL_DYNAMICAL_REGIMES = ['Shallow', 'Slopes', 'Ice', 'Deserts', 'Blooms', 'Equator', 'Transition']

