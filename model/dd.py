""" To maintain consistency, we import these common variables where they occur in the model """

REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China',
           'India', 'EU', 'USA']

# Land
THERMAL_MOISTURE_REGIMES = ['Tropical-Humid', 'Temperate/Boreal-Humid', 'Tropical-Semi-Arid',
                            'Temperate/Boreal-Semi-Arid', 'Global Arid', 'Global Arctic']

# Ocean
OCEAN_REGIONS = REGIONS[:6] + ['ABNJ'] + REGIONS[6:]  # ocean model has one extra region
THERMAL_DYNAMICAL_REGIMES = ['Shallow', 'Slopes', 'Ice', 'Deserts', 'Blooms', 'Equator', 'Transition']

