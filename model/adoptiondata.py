"""'Adoption' is the amount or degree of use of a solution over time (typically increasing, sometimes decreasing).
Adoption may be global or specific to a particular reagon.  The units of adoption are defined by the
solution that uses it (and are sometimes shared across multiple solutions, e.g. TeraWatts for energy).

There are multiple ways of representing adoption: `AdoptionData` (this module), `CustomAdoption`,
and pure functions `Linear` or `S-Curve`.  The `HelperTables` module mediates between the different
options to provide the final adoption data for a solution/scenario.

`AdoptionData` represents adoption as a statistical combination, interpolation and/or extrapolation
of some number of published studies (the 'source data', also called 'Existing Prognostications').
That is, the data from the existing study or studies is represented
in data files, then the adoption is configured by how to aggregate that data. 

Data sources are represented in a multi-level hierarchy, organized by region and by an assessment of
whether the study is baseline (representing no change), conservative (representing modest change),
or ambitious (most change).
For example:
```
{
    'Ambitious Cases': {'Study Name A': 'filename A', 'Study Name B': 'filename B', ...},
    'Baseline Cases': {'Study Name C': 'filename C', 'Study Name D': 'filename D', ...},
    'Conservative Cases': {'Study Name E': 'filename E', 'Study Name F': 'filename F', ...}
}
```

Regional is somewhat awkwardly added in parallel to these, so you *actually* get data structures like this:
```
{
    'Ambitious Cases': { ... },
    'Baseline Cases': { ... },
    'Conservative Cases': { ... },
    'Region: OECD90': {
        'Ambitious Cases: { ... },
        ...
    },
    'Region: India': {
        'Ambitious Cases: { ... },
        ...
    },
    ....
}
```
These structures are serialized as JSON in a file named 'ad_sources.json' in the 'ad' subdirectory of solutions that
use AdoptionData representations.

The configuration is represented by an multi-dimensional array of parameters which have the following meanings:

 * `trend`: Which fitting curve to use to interpolate/extrapolate missing data.  Choices are linear, 2nd order
 polynomial, 3rd order polynomial, or exponential. 
 * `growth`: Whether a lower, medium or higher estimate of growth should be used.
 * `low_sd_mult`: Values below mean(data) - `low_sd_mult`*(stdev(data)) are discarded before fitting.  (deprecated.)
 * `high_sd_mult`: Values above mean(data) + `high_sd_mult`*(stdev(data)) are discarded before fitting. (deprecated.)
 """

from functools import lru_cache
import pathlib
import re

from model import interpolation
from model import dd
from model.metaclass_cache import MetaclassCache
import numpy as np
import pandas as pd

from model.data_handler import DataHandler
from model.decorators import data_func

default_adoption_config_array = [
    ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
        'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
        ['trend'] + ['3rd Poly'] * 10,
        ['growth'] + ['Medium'] * 10,
        ['low_sd_mult'] + [1.0] * 10,
        ['high_sd_mult'] + [1.0] * 10
    ]
def make_adoption_config(adoption_config_array=None, overrides=None) -> pd.DataFrame:
    """Create an adoption configuration.

    The configuration values all have standard defaults, but may be overridden.
    Overrides, if provided, should be in the form of a list of tuples  `(param, region, value)`.
    An override may be applied to a specific region (if the region value is non-empty), or to
    all regions (if the region value is None).
    
    Example: this call will create a standard configuration that uses a 2nd degree polynomial fit
    for all regions, and a high growth adjustment for China and India:
    ```
        make_adoption_config(overrides=[
            ('trend',None,'2nd Poly'),
            ('growth','India','High'),
            ('growth','China','High')
        ])
    ```
    """
    ad_config_array = adoption_config_array or default_adoption_config_array
    adconfig = pd.DataFrame(ad_config_array[1:], columns=ad_config_array[0]).set_index('param')
    if overrides is not None:
        for (param,region,val) in overrides:
            if region is None:
                adconfig.loc[param] = val
            else:
                adconfig.loc[param,region] = val
    return adconfig


class AdoptionData(DataHandler, object, metaclass=MetaclassCache):
    """Adoption of a solution, estimated from existing data (aka 'Existing Prognostications')."""

    def __init__(self, ac, data_sources, adconfig, main_includes_regional=None,
                 groups_include_hundred_percent=True):
        """Create AdoptionData object from data sources and configuration.
        
        Args:
            ac: advanced controls object.
            data_sources: a data structure organizing source data, as contained in an ad_sources.json file
            adconfig: Configuration of statistical analysis, as returned by `make_adoption_config`.
            main_includes_regional (boolean): whether the global min/max/sd should include
               data from the primary regions.

        Quirks Parameters:
            groups_include_hundred_percent (boolean):  Some models included the 100% / maximum case as
            a group when computing S.D., others (Electricity Generation) do not.  Defaults to True.
        """
        self.ac = ac
        self.data_sources = data_sources
        self.adconfig = adconfig
        self.main_includes_regional = main_includes_regional
        self.groups_include_hundred_percent = groups_include_hundred_percent
        self._populate_adoption_data()

    @lru_cache()
    def adoption_sources(self, region):
        """Return source adoption data for the specified region, as a dataframe with one column per source.
        """
        # World: SolarPVUtil 'Adoption Data'!B45:R94
        # etc.
        return self._adoption_data[region]

    @lru_cache()
    @data_func
    def adoption_data_per_region(self):
        """Return a dataframe of adoption data, one column per region."""
        growth = self.ac.soln_pds_adoption_prognostication_growth
        main_region = dd.REGIONS[0]
        if growth is None:
            tmp = self.adoption_low_med_high(region=main_region)
            df = pd.DataFrame(np.nan, columns=dd.REGIONS, index=tmp.index)
        else:
            df = pd.DataFrame(columns=dd.REGIONS)
            for region in df.columns:
                df.loc[:, region] = self.adoption_low_med_high(region)[growth]
        df.name = 'adoption_data_per_region'
        return df

    def _name_to_identifier(self, name):
        """Convert names like "Middle East and Africa" to "middle_east_and_africa"."""
        x = re.sub(r"[()]", "", name.lower())
        return re.sub(r" ", "_", x)


    def _populate_adoption_data(self):
        """Read data files in self.tam_*_data_sources to populate forecast data."""
        df_per_region = {}
        main_region = dd.REGIONS[0]
        main_region_pds = 'PDS ' + main_region
        for region in dd.REGIONS + [main_region_pds]:
            df = pd.DataFrame()
            df.name = 'forecast_data_' + self._name_to_identifier(region)
            df_per_region[region] = df
        for (groupname, group) in self.data_sources.items():
            for (name, value) in group.items():
                if (isinstance(value, str) or isinstance(value, pathlib.Path) or
                        isinstance(value, pathlib.PurePath)):
                    sources = {name: value}
                else:
                    sources = value
                for name, filename in sources.items():
                    df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
                            skip_blank_lines=True, comment='#')
                    for region in dd.REGIONS:
                        df_per_region[region].loc[:, name] = df.loc[:, region]
        self._adoption_data = df_per_region


    def _min_max_sd(self, adoption_data, source, data_sources, region):
        """Return the min, max, and standard deviation for adoption data."""
        result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Min', 'Max', 'S.D'])
        result.loc[:, 'Min'] = adoption_data.min(axis=1)
        result.loc[:, 'Max'] = adoption_data.max(axis=1)

        region_key = None if region is None else f'Region: {region}'
        columns = interpolation.matching_data_sources(data_sources=data_sources, name=source,
                groups_only=False, region_key=region_key)
        if columns is None:
            result.loc[:, 'S.D'] = np.nan
        elif len(columns) > 1:
            # Excel STDDEV.P is a whole population stddev, ddof=0
            result.loc[:, 'S.D'] = adoption_data.loc[:, columns].std(axis=1, ddof=0)
        else:
            # The need to do a quirks adjustment here means we have to hack is_group_name:
            is_group = self._quirky_is_group_name(data_sources=data_sources, name=source)
            
            # Excel treats single named columns differently from groups containing only a single column.
            # For a single named column, the SD is taken over all sources.  For a group, it is taken over
            # the group, even though there is only a single member, yielding 0
            # #EXCEL-BAD-BEHAVIOR
            if is_group:
                result.loc[:,'S.D'] = 0.0
            else:
                result.loc[:, 'S.D'] = adoption_data.std(axis=1, ddof=0)
        return result

    def _quirky_is_group_name(self, data_sources, name):
        is_group = interpolation.is_group_name(data_sources, name)
        if self.groups_include_hundred_percent or not is_group:
            return is_group
        # otherwise, we must exclude the 100% or maximum case.  Since we don't know what it will
        # be named, we test for the standard groups instead
        name = name.lower()
        return ('conservative' in name) or ('baseline' in name) or ('ambitious' in name)

    def _low_med_high(self, adoption_data, min_max_sd, adconfig, source, data_sources, region):
        """Return the selected data sources as Medium, and N stddev away as Low and High."""
        result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Low', 'Medium', 'High'])
        region_key = None if region is None else f'Region: {region}'
        columns = interpolation.matching_data_sources(data_sources=data_sources, name=source,
                groups_only=False, region_key=region_key)
        if columns is None:
            result.loc[:, 'Medium'] = np.nan
            result.loc[:, 'Low'] = np.nan
            result.loc[:, 'High'] = np.nan
        else:
            if len(columns) == 1:
                is_group = interpolation.is_group_name(data_sources=data_sources, name=columns[0])
            else:
                is_group = True

            if is_group:
                # In Excel, the Mean computation is:
                # SUM($C46:$Q46)/COUNTIF($C46:$Q46,">0")
                #
                # The intent is to skip sources which are empty, but also means that
                # a source where the real data is 0.0 will not impact the Medium result.
                #
                # See this document for more information:
                # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.yvwwsbvutw2j
                #
                # We're matching the Excel behavior in the initial product. This decision can
                # be revisited later, when matching results from Excel is no longer required.
                # To revert, use:    medium = adoption_data.loc[:, columns].mean(axis=1)
                # EXCEL-BAD-BEHAVIOR
                medium = adoption_data.loc[:, columns].mask(lambda f: f == 0.0, np.nan).mean(axis=1)
            else:
                # if there is only a single source, Excel uses it directly without taking a Mean.
                medium = adoption_data.loc[:, columns[0]]
            result.loc[:, 'Medium'] = medium
            result.loc[:, 'Low'] = medium - (min_max_sd.loc[:, 'S.D'] * adconfig.loc['low_sd_mult'])
            result.loc[:, 'High'] = medium + (
                min_max_sd.loc[:, 'S.D'] * adconfig.loc['high_sd_mult'])
        return result


    def _adoption_trend(self, low_med_high, growth, trend):
        """Adoption prediction via one of several interpolation algorithms."""
        if growth is None or trend is None:
            result = pd.DataFrame(np.nan, index=low_med_high.index.copy(), columns=['adoption'])
        else:
            data = low_med_high[growth]
            result = interpolation.trend_algorithm(data=data, trend=trend)
        return result


    def _get_data_sources(self, region):
        key = "Region: " + region
        return self.data_sources.get(key, self.data_sources)



    @lru_cache()
    @data_func
    def _adoption_data_with_regional(self):
        """Return adoption data for the 'World' region with regional data added in."""
        # World: SolarPVUtil 'Adoption Data'!B45:R94
        # etc.
        main_region = dd.REGIONS[0]
        regional = pd.DataFrame(columns=dd.MAIN_REGIONS)
        for region in regional.columns:
            regional[region] = self.adoption_trend(region=region).loc[:, 'adoption']
        regional_sum = regional.sum(axis=1)
        regional_sum.name = 'RegionalSum'
        adoption = self.adoption_sources(region=main_region).copy()
        adoption.loc[:, 'RegionalSum'] = np.nan
        if self.ac.soln_pds_adoption_prognostication_source == 'ALL SOURCES':
            adoption.update(regional_sum)
        return adoption


    @lru_cache()
    def adoption_min_max_sd(self, region):
        """Return the min, max, and standard deviation for the adoption data for the specified region."""
        #    World: SolarPVUtil 'Adoption Data'!X45:Z94
        #    etc.
        data_sources = self._get_data_sources(region=region)
        main_region = dd.REGIONS[0]  # first columns, ex: 'World'
        if region == main_region:
            if self.main_includes_regional:
                adoption = self._adoption_data_with_regional()
                data_sources = data_sources.copy()
                data_sources.update({'RegionalSum': {'RegionalSum': ''}})
            else:
                adoption = self.adoption_sources(region)
            source = self.ac.soln_pds_adoption_prognostication_source
        else:
            adoption = self.adoption_sources(region)
            source = "ALL SOURCES"
        result = self._min_max_sd(adoption_data=adoption, source=source,
                data_sources=data_sources, region=region)
        result.name = 'adoption_min_max_sd_' + self._name_to_identifier(region)
        return result


    @lru_cache()
    def adoption_low_med_high(self, region):
        """Return the selected data sources as Medium, and N stddev away as Low and High."""
        #    World: SolarPVUtil 'Adoption Data'!AB45:AD94
        #    etc.
        data_sources = self._get_data_sources(region=region)
        main_region = dd.REGIONS[0]  # first columns, ex: 'World'
        if region == main_region:
            if self.main_includes_regional:
                adoption = self._adoption_data_with_regional()
                data_sources = data_sources.copy()
                data_sources.update({'RegionalSum': {'RegionalSum': ''}})
            else:
                adoption = self.adoption_sources(region)
            source = self.ac.soln_pds_adoption_prognostication_source
        else:
            adoption = self.adoption_sources(region=region)
            source = "ALL SOURCES"
        result = self._low_med_high(adoption_data=adoption,
                min_max_sd=self.adoption_min_max_sd(region), adconfig=self.adconfig[region],
                source=source, data_sources=data_sources, region=region)
        result.name = 'adoption_low_med_high_' + self._name_to_identifier(region)
        return result


    @lru_cache()
    def adoption_trend(self, region, trend=None):
        """Adoption prediction via one of several interpolation algorithms in the region."""
        # World:
        # Linear: SolarPVUtil 'Adoption Data'!BY50:CA96     Degree2: 'Adoption Data'!CF50:CI96
        # Degree3: SolarPVUtil 'Adoption Data'!CN50:CR96    Exponential: 'Adoption Data'!CW50:CY96,
        # etc
        main_region = dd.REGIONS[0]  # first columns, ex: 'World'
        if not trend:
            trend = self.adconfig.loc['trend', region]
        if region == main_region:
            growth = self.ac.soln_pds_adoption_prognostication_growth
        else:
            growth = self.adconfig.loc['growth', region]
        result = self._adoption_trend(self.adoption_low_med_high(region), growth, trend)
        result.name = 'adoption_trend_' + self._name_to_identifier(region) + '_' + str(trend).lower()
        return result

    @lru_cache()
    @data_func
    def adoption_is_single_source(self):
        """Whether the source data selected is one source or multiple."""
        return not interpolation.is_group_name(data_sources=self.data_sources,
                                               name=self.ac.soln_pds_adoption_prognostication_source)

    def _set_adoption_one_region(self, result, region, adoption_trend, adoption_low_med_high):
        result[region] = adoption_trend.loc[:, 'adoption']
        first_year = result.index[0]
        result.loc[first_year, region] = adoption_low_med_high.loc[first_year, 'Medium']


    @lru_cache()
    @data_func
    def adoption_trend_per_region(self):
        """Return a dataframe of adoption trends, one column per region."""
        df = pd.DataFrame(columns=dd.REGIONS)
        for region in df.columns:
            adoption_trend = self.adoption_trend(region=region)
            adoption_low_med_high = self.adoption_low_med_high(region=region)
            self._set_adoption_one_region(result=df, region=region, adoption_trend=adoption_trend,
                    adoption_low_med_high=adoption_low_med_high)
        return df
