""" To maintain consistency, we import these common variables where they occur in the model """

import pandas.api.types

REGIONS = [
    'World',  # sum of main regions
    'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',  # main regions
    'China', 'India', 'EU', 'USA'  # special countries
]
MAIN_REGIONS = REGIONS[1:6]
SPECIAL_COUNTRIES = REGIONS[6:]
COUNTRY_REGION_MAP = {'China': 'Asia (Sans Japan)', 'India': 'Asia (Sans Japan)', 'EU': 'OECD90', 'USA': 'OECD90'}

# Land
THERMAL_MOISTURE_REGIMES = ['Tropical-Humid', 'Temperate/Boreal-Humid', 'Tropical-Semi-Arid',
                            'Temperate/Boreal-Semi-Arid', 'Global Arid', 'Global Arctic']

AEZS = ['AEZ1: Forest, prime, minimal', 'AEZ2: Forest, good, minimal', 'AEZ3: Forest, good, moderate',
        'AEZ4: Forest, good, steep', 'AEZ5: Forest, marginal, minimal', 'AEZ6: Forest, marginal, moderate',
        'AEZ7: Forest, marginal, steep', 'AEZ8: Grassland, prime, minimal', 'AEZ9: Grassland, good, minimal',
        'AEZ10: Grassland, good, moderate', 'AEZ11: Grassland, good, steep', 'AEZ12: Grassland, marginal, minimal',
        'AEZ13: Grassland, marginal, moderate', 'AEZ14: Grassland, marginal, steep',
        'AEZ15: Irrigated Cropland, prime, minimal', 'AEZ16: Irrigated Cropland, good, minimal',
        'AEZ17: Irrigated Cropland, good, moderate', 'AEZ18: Irrigated Cropland, good, steep',
        'AEZ19: Irrigated Cropland, marginal, minimal', 'AEZ20: Irrigated Cropland, marginal, moderate',
        'AEZ21: Irrigated Cropland, marginal, steep', 'AEZ22: Rainfed Cropland, prime, minimal',
        'AEZ23: Rainfed Cropland, good, minimal', 'AEZ24: Rainfed Cropland, good, moderate',
        'AEZ25: Rainfed Cropland, good, steep', 'AEZ26: Rainfed Cropland, marginal, minimal',
        'AEZ27: Rainfed Cropland, marginal, moderate', 'AEZ28: Rainfed Cropland, marginal, steep',
        'AEZ29: All Barren Land']

AEZ_LAND_COVER_MAP = {'Forest': AEZS[:7], 'Grassland': AEZS[7:14], 'Irrigated Cropland': AEZS[14:21],
                      'Rainfed Cropland': AEZS[21:28]}

# Ocean
OCEAN_REGIONS = ['World'] + MAIN_REGIONS + ['ABNJ'] + SPECIAL_COUNTRIES  # ocean model has one extra region
THERMAL_DYNAMICAL_REGIMES = ['Shallow', 'Slopes', 'Ice', 'Deserts', 'Blooms', 'Equator', 'Transition']

rgn_cat_dtype = pandas.api.types.CategoricalDtype(categories=OCEAN_REGIONS + [''], ordered=True)
tmr_cat_dtype = pandas.api.types.CategoricalDtype(categories=THERMAL_MOISTURE_REGIMES + [''], ordered=True)
tdr_cat_dtype = pandas.api.types.CategoricalDtype(categories=THERMAL_DYNAMICAL_REGIMES + [''], ordered=True)


# time ranges
CORE_START_YEAR = 2015
CORE_END_YEAR = 2060
