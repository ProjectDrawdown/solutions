"""Total Addressable Market module."""

from functools import lru_cache
import os.path
import pathlib
import re

from model import dd
from model import interpolation
from model import metaclass_cache
import numpy as np
import pandas as pd


class TAM(object, metaclass=metaclass_cache.MetaclassCache):
    """Total Addressable Market module."""

    def __init__(self, tamconfig, tam_ref_data_sources, tam_pds_data_sources,
                 main_includes_regional=None):
        """TAM module.

           Arguments
           tamconfig: Pandas dataframe with columns:
              'source_until_2014', 'source_after_2014', 'trend', 'growth', 'low_sd_mult', 'high_sd_mult'
              and rows for each region:
              'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
              'Latin America', 'China', 'India', 'EU', 'USA'
           tam_ref_data_sources: a dict() of group names which contain dicts of data source names.
             Used for Total Addressable Market and adoption calculations in the REF scenario.
             For example:
             {
               'Ambitious Cases': {'Study Name A': 'filename A', 'Study Name B': 'filename B', ...}
               'Baseline Cases': {'Study Name C': 'filename C', 'Study Name D': 'filename D', ...}
               'Conservative Cases': {'Study Name E': 'filename E', 'Study Name F': 'filename F', ...}
             }
           tam_pds_data_sources: as tam_ref_data_sources, for the PDS scenario.
           main_includes_regional: boolean of whether the global min/max/sd should include
             data from the primary regions.
        """
        self.tamconfig = tamconfig
        self.tam_ref_data_sources = tam_ref_data_sources
        self.tam_pds_data_sources = tam_pds_data_sources
        self.main_includes_regional = main_includes_regional
        self._populate_forecast_data()


    def _name_to_identifier(self, name):
        """Convert names like "Middle East and Africa" to "middle_east_and_africa"."""
        x = re.sub(r"[()]", "", name.lower())
        return re.sub(r" ", "_", x)


    def _populate_forecast_data(self):
        """Read data files in self.tam_*_data_sources to populate forecast data."""
        df_per_region = {}
        main_region = dd.REGIONS[0]
        main_region_pds = 'PDS ' + main_region
        for region in dd.REGIONS + [main_region_pds]:
            df = pd.DataFrame()
            df.name = 'forecast_data_' + self._name_to_identifier(region)
            df_per_region[region] = df
        for (groupname, group) in self.tam_ref_data_sources.items():
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
        for (groupname, group) in self.tam_pds_data_sources.items():
            for (name, value) in group.items():
                if isinstance(value, str) or isinstance(value, pathlib.Path):
                    sources = {name: value}
                else:
                    sources = value
                for name, filename in sources.items():
                    df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
                            skip_blank_lines=True, comment='#')
                    df_per_region[main_region_pds].loc[:, name] = df.loc[:, main_region]
        self._forecast_data = df_per_region


    def _min_max_sd(self, forecast, tamconfig, data_sources):
        """Return the min, max, and standard deviation for TAM data.
           Arguments:
             forecast: the TAM forecast dataframe for all sources.
             tamconfig: the row from self.tamconfig to use
             data_sources: dict of dicts of datasources, as described in tam_ref_data_sources in
               the constructor
        """
        source_until_2014 = tamconfig['source_until_2014']
        source_after_2014 = tamconfig['source_after_2014']

        result = pd.DataFrame(np.nan, index=forecast.index.copy(), columns=['Min', 'Max', 'S.D'])
        result.loc[:, 'Min'] = forecast.dropna(axis='columns', how='all').min(axis=1)
        result.loc[:, 'Max'] = forecast.max(axis=1)
        if forecast.empty:
            # Some solutions provide no data sources for PDS
            result.loc[:, 'S.D'] = np.nan
        else:
            columns = interpolation.matching_data_sources(data_sources=data_sources,
                    name=source_until_2014, groups_only=True)
            # Excel STDDEV.P is a whole population stddev, ddof=0
            m = forecast.loc[:2014, columns].dropna(axis='columns', how='all').std(axis=1, ddof=0)
            m.name = 'S.D'
            result.update(m)
            columns = interpolation.matching_data_sources(data_sources=data_sources,
                    name=source_after_2014, groups_only=True)
            m = forecast.loc[2015:, columns].dropna(axis='columns', how='all').std(axis=1, ddof=0)
            m.name = 'S.D'
            result.update(m)
        return result


    def _low_med_high(self, forecast, min_max_sd, tamconfig, data_sources):
        """Return the selected data sources as Medium, and N stddev away as Low and High.

           Arguments:
             forecast: DataFrame of all of the data sources, source name as the column name.
             min_max_sd: DataFrame with columns for the Minimum, Maxiumum, and Standard deviation.
             tamconfig: the row from self.tamconfig to use
             data_sources: dict of dicts of datasources, as described in tam_ref_data_sources in
               the constructor
        """
        result = pd.DataFrame(np.nan, index=forecast.index.copy(),
                              columns=['Low', 'Medium', 'High'])
        if forecast.empty:
            result.loc[:, 'Medium'] = np.nan
            result.loc[:, 'Low'] = np.nan
            result.loc[:, 'High'] = np.nan
            return result

        columns = interpolation.matching_data_sources(data_sources=data_sources,
                name=tamconfig['source_until_2014'], groups_only=False)
        if columns and len(columns) > 1:
            # In Excel, the Mean computation is:
            # SUM($C521:$Q521)/COUNTIF($C521:$Q521,">0")
            #
            # The intent is to skip sources which are empty, but also means that
            # a source where the real data is 0.0 will not impact the Medium result.
            #
            # See this document for more information:
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.yvwwsbvutw2j
            #
            # We're matching the Excel behavior in the initial product. This decision can
            # be revisited later, when matching results from Excel is no longer required.
            # To revert, use:    m = forecast.loc[:2014, columns].mean(axis=1)
            # and:               m = forecast.loc[2015:, columns].mean(axis=1)
            m = forecast.loc[:2014, columns].mask(lambda f: f == 0.0, np.nan).mean(axis=1)
            m.name = 'Medium'
            result.update(m)
        elif columns and len(columns) == 1:
            m = forecast.loc[:2014, columns].mean(axis=1)
            m.name = 'Medium'
            result.update(m)

        columns = interpolation.matching_data_sources(data_sources=data_sources,
                name=tamconfig['source_after_2014'], groups_only=False)
        if columns and len(columns) > 1:
            # see comment above about Mean and this lambda function
            m = forecast.loc[2015:, columns].mask(lambda f: f == 0.0, np.nan).mean(axis=1)
            m.name = 'Medium'
            result.update(m)
        elif columns and len(columns) == 1:
            m = forecast.loc[2015:, columns].mean(axis=1)
            m.name = 'Medium'
            result.update(m)

        low_sd_mult = tamconfig['low_sd_mult']
        high_sd_mult = tamconfig['high_sd_mult']
        result.loc[:, 'Low'] = result.loc[:, 'Medium'] - (min_max_sd.loc[:, 'S.D'] * low_sd_mult)
        result.loc[:, 'High'] = result.loc[:, 'Medium'] + (min_max_sd.loc[:, 'S.D'] * high_sd_mult)
        return result


    def _get_trend(self, trend, tamconfig, data_sources):
        """Decision tree to select between trend choices.

           Arguments:
             trend: explicit trend to use, if any. Pass None to have tamconfig be used.
             tamconfig: the row from self.tamconfig to use
             data_sources: dict of dicts of datasources, as described in tam_ref_data_sources in
               the constructor

           If a trend was explictly specified, use it.
           If there is only one data source, use that source without any curve fitting.
           Otherwise, use the curve fit algorithm specified in the tamconfig.
        """
        if trend:
            return trend
        if not interpolation.is_group_name(data_sources=data_sources,
                name=tamconfig['source_after_2014']):
            return 'single'
        else:
            return tamconfig['trend']


    def _get_data_sources(self, data_sources, region):
        key = "Region: " + region
        return data_sources.get(key, data_sources)


    def _forecast_data_regional_sum(self):
        """ SolarPVUtil 'TAM Data'!Q45:Q94 when B29:B30 are both 'Y' """
        regional = pd.DataFrame(columns=dd.MAIN_REGIONS)
        for region in regional.columns:
            self._set_tam_one_region(result=regional, region=region,
                    forecast_trend=self.forecast_trend(region),
                    forecast_low_med_high=self.forecast_low_med_high(region))
        regional_sum = regional.sum(axis=1)
        regional_sum.name = 'RegionalSum'
        return regional_sum


    @lru_cache()
    def forecast_data(self, region):
        """
          World: SolarPVUtil 'TAM Data'!B45:Q94
          OECD90: SolarPVUtil 'TAM Data'!B163:Q212
          Eastern Europe: SolarPVUtil 'TAM Data'!B227:Q276
          Asia (sans Japan): SolarPVUtil 'TAM Data'!B290:Q339
          Middle East and Africa: SolarPVUtil 'TAM Data'!B353:Q402
          Latin America: SolarPVUtil 'TAM Data'!B416:Q465
          China: SolarPVUtil 'TAM Data'!B479:Q528
          India: SolarPVUtil 'TAM Data'!B543:Q592
          EU: SolarPVUtil 'TAM Data'!B607:Q656
          USA: SolarPVUtil 'TAM Data'!B672:Q721
        """
        return self._forecast_data[region]


    @lru_cache()
    def forecast_min_max_sd(self, region):
        """
          World: SolarPVUtil 'TAM Data'!V45:Y94
          OECD90: SolarPVUtil 'TAM Data'!V163:Y212
          Eastern Europe: SolarPVUtil 'TAM Data'!V227:Y276
          Asia (sans Japan): SolarPVUtil 'TAM Data'!V290:Y339
          Middle East and Africa: SolarPVUtil 'TAM Data'!V353:Y402
          Latin America: SolarPVUtil 'TAM Data'!V416:Y465
          China: SolarPVUtil 'TAM Data'!V479:Y528
          India: SolarPVUtil 'TAM Data'!V543:Y592
          EU: SolarPVUtil 'TAM Data'!V607:Y656
          US: SolarPVUtil 'TAM Data'!V672:Y721
        """
        main_region = dd.REGIONS[0]
        if main_region in region and 'PDS' in region:
            data_sources = self._get_data_sources(data_sources=self.tam_pds_data_sources,
                    region=main_region)
        else:
            data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,
                    region=region)

        if region == main_region and self.main_includes_regional:
            forecast = self.forecast_data(region).copy()
            regional_sum = self._forecast_data_regional_sum()
            forecast.loc[:, 'RegionalSum'] = regional_sum
            data_sources = data_sources.copy()
            data_sources.update({'RegionalSum': {'RegionalSum': ''}})
        else:
            forecast = self.forecast_data(region)

        result = self._min_max_sd(forecast=forecast, tamconfig=self.tamconfig[region],
                data_sources=data_sources)
        result.name = 'forecast_min_max_sd_' + self._name_to_identifier(region)
        return result


    def _forecast_low_med_high_pds(self, pds_region, main_region):
        """ SolarPVUtil 'TAM Data'!AA45:AC94 """
        # In Excel, the PDS TAM calculation:
        # + uses World data for 2012-2014, unconditionally. However, many solutions
        #   make a practice of using curated data for the years 2012-2014 and paste
        #   it across all sources, so PDS and World are often the same for 2012-2014.
        # + uses PDS data for 2015+ where it exists, and uses World data where no
        #   PDS data exists.
        #
        # We implement this by calculating the World low_med_high, then update it with PDS
        # results where they exist, then concatenate PDS data for 2015+ with
        # World data for 2012-2014.
        #
        # Note that PDS min/max/sd uses PDS data for 2012-2014, not World, and this
        # makes a difference in solutions which do not paste the same curated data
        # for 2012-2014 across all sources. So this handling only exists here, not
        # forecast_min_max_sd.
        data_sources = self._get_data_sources(data_sources=self.tam_pds_data_sources,
                region=main_region)
        result_main = self.forecast_low_med_high(main_region).copy(deep=True)
        result_pds = self._low_med_high(forecast=self.forecast_data(pds_region),
                min_max_sd=self.forecast_min_max_sd(pds_region),
                tamconfig=self.tamconfig[pds_region], data_sources=data_sources)
        result_2014 = result_main.loc[:2014].copy()
        result_2015 = result_main.loc[2015:].copy()
        result_2015.update(other=result_pds, overwrite=True)
        result = pd.concat([result_2014, result_2015], sort=False)
        result.name = 'forecast_low_med_high_pds'
        return result


    @lru_cache()
    def forecast_low_med_high(self, region):
        """
          OECD90: SolarPVUtil 'TAM Data'!AA163:AC212
          Eastern Europe: SolarPVUtil 'TAM Data'!AA227:AC276
          Asia (sans Japan): SolarPVUtil 'TAM Data'!AA290:AC339
          Middle East and Africa: SolarPVUtil 'TAM Data'!AA353:AC402
          Latin America: SolarPVUtil 'TAM Data'!AA416:AC465
          China: SolarPVUtil 'TAM Data'!AA479:AC528
          India: SolarPVUtil 'TAM Data'!AA543:AC592
          EU: SolarPVUtil 'TAM Data'!AA607:AC656
          US: SolarPVUtil 'TAM Data'!AA672:AC721
        """
        main_region = dd.REGIONS[0]
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources, region=region)

        if main_region in region and 'PDS' in region:
            return self._forecast_low_med_high_pds(pds_region=region, main_region=main_region)
        elif region == main_region and self.main_includes_regional:
            forecast = self.forecast_data(region).copy()
            forecast.loc[:, 'RegionalSum'] = np.nan
            regional_sum = self._forecast_data_regional_sum()
            tamconfig = self.tamconfig[region]
            if tamconfig['source_after_2014'] == 'ALL SOURCES':
                forecast.update(regional_sum.loc[2015:])
            if tamconfig['source_until_2014'] == 'ALL SOURCES':
                forecast.update(regional_sum.loc[:2014])
            data_sources = data_sources.copy()
            data_sources.update({'RegionalSum': {'RegionalSum': ''}})
        else:
            forecast = self.forecast_data(region)

        result = self._low_med_high(forecast=forecast,
                min_max_sd=self.forecast_min_max_sd(region=region),
                tamconfig=self.tamconfig[region], data_sources=data_sources)
        result.name = 'forecast_low_med_high_' + self._name_to_identifier(region)
        return result


    @lru_cache()
    def forecast_trend(self, region, trend=None):
        """Forecast for a region via one of several interpolation algorithms.

           World:
           Linear: SolarPVUtil 'TAM Data'!BX50:BZ96       Degree2: SolarPVUtil 'TAM Data'!CE50:CH96
           Degree3: SolarPVUtil 'TAM Data'!CM50:CQ96      Exponential: SolarPVUtil 'TAM Data'!CV50:CX96

           OECD90:
           Linear: SolarPVUtil 'TAM Data'!BX168:BZ214     Degree2: SolarPVUtil 'TAM Data'!CE168:CH214
           Degree3: SolarPVUtil 'TAM Data'!CM168:CQ214    Exponential: SolarPVUtil 'TAM Data'!CV168:CX214

           Eastern Europe:
           Linear: SolarPVUtil 'TAM Data'!BX232:BZ278     Degree2: SolarPVUtil 'TAM Data'!CE232:CH278
           Degree3: SolarPVUtil 'TAM Data'!CM232:CQ278    Exponential: SolarPVUtil 'TAM Data'!CV232:CX278

           Asia (Sans Japan):
           Linear: SolarPVUtil 'TAM Data'!BX295:BZ341     Degree2: SolarPVUtil 'TAM Data'!CE295:CH341
           Degree3: SolarPVUtil 'TAM Data'!CM295:CQ341    Exponential: SolarPVUtil 'TAM Data'!CV295:CX341

           Middle East and Africa:
           Linear: SolarPVUtil 'TAM Data'!BX358:BZ404     Degree2: SolarPVUtil 'TAM Data'!CE358:CH404
           Degree3: SolarPVUtil 'TAM Data'!CM358:CQ404    Exponential: SolarPVUtil 'TAM Data'!CV358:CX404

           Latin America:
           Linear: SolarPVUtil 'TAM Data'!BX421:BZ467     Degree2: SolarPVUtil 'TAM Data'!CE421:CH467
           Degree3: SolarPVUtil 'TAM Data'!CM421:CQ467    Exponential: SolarPVUtil 'TAM Data'!CV421:CX467

           China:
           Linear: SolarPVUtil 'TAM Data'!BX484:BZ530     Degree2: SolarPVUtil 'TAM Data'!CE484:CH530
           Degree3: SolarPVUtil 'TAM Data'!CM484:CQ530    Exponential: SolarPVUtil 'TAM Data'!CV484:CX530

           India:
           Linear: SolarPVUtil 'TAM Data'!BX548:BZ594     Degree2: SolarPVUtil 'TAM Data'!CE548:CH594
           Degree3: SolarPVUtil 'TAM Data'!CM548:CQ594    Exponential: SolarPVUtil 'TAM Data'!CV548:CX594

           EU:
           Linear: SolarPVUtil 'TAM Data'!BX612:BZ658     Degree2: SolarPVUtil 'TAM Data'!CE612:CH658
           Degree3: SolarPVUtil 'TAM Data'!CM612:CQ658    Exponential: SolarPVUtil 'TAM Data'!CV612:CX658

           US:
           Linear: SolarPVUtil 'TAM Data'!BX677:BZ723     Degree2: SolarPVUtil 'TAM Data'!CE677:CH723
           Degree3: SolarPVUtil 'TAM Data'!CM677:CQ723    Exponential: SolarPVUtil 'TAM Data'!CV677:CX723
        """
        main_region = dd.REGIONS[0]
        if main_region in region and 'PDS' in region:
            data_sources = self._get_data_sources(
                    data_sources=self.tam_pds_data_sources, region=region)
        else:
            data_sources = self._get_data_sources(
                    data_sources=self.tam_ref_data_sources, region=region)
        growth = self.tamconfig.loc['growth', region]
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig[region],
                data_sources=data_sources)
        data = self.forecast_low_med_high(region).loc[:, growth]
        result = interpolation.trend_algorithm(data=data, trend=trend)
        result.name = 'forecast_trend_' + self._name_to_identifier(region) + '_' + str(trend).lower()
        return result


    def _set_tam_one_region(self, result, region, forecast_trend, forecast_low_med_high):
        """Set a single column in ref_tam_per_region."""
        result[region] = forecast_trend.loc[:, 'adoption']
        first_year = result.first_valid_index()
        result.loc[first_year, region] = forecast_low_med_high.loc[first_year, 'Medium']


    @lru_cache()
    def ref_tam_per_region(self):
        """Compiles the TAM for each of the major regions into a single dataframe.

           This isn't on the TAM Data tab of the Excel implementation, but is commonly used
           by reference from other tabs. For convenience, we supply it.
           SolarPVUtil 'Unit Adoption Calculations'!A16:K63
        """
        result = pd.DataFrame(columns=dd.REGIONS)
        for region in result.columns:
            self._set_tam_one_region(result=result, region=region,
                    forecast_trend=self.forecast_trend(region),
                    forecast_low_med_high=self.forecast_low_med_high(region))
        result.name = "ref_tam_per_region"
        return result


    @lru_cache()
    def pds_tam_per_region(self):
        """Compiles the PDS TAM for each of the major regions into a single dataframe.

           At the time of this writing (11/2018), only the World region has a PDS forecast.
           The other, smaller regions use the REF TAM.

           This isn't on the TAM Data tab of the Excel implementation, but is commonly used
           by reference from other tabs. For convenience, we supply it.
           SolarPVUtil 'Unit Adoption Calculations'!A68:K115
        """
        result = pd.DataFrame(columns=dd.REGIONS)
        for idx, region in enumerate(result.columns):
            if idx == 0:
                region_pds = 'PDS ' + region
                result[region] = self.forecast_trend(region_pds).loc[:, 'adoption']
                lmh = self.forecast_low_med_high(region)
                if result.dropna(axis=1, how='all').empty or lmh.dropna(axis=1, how='all').empty:
                    result[region] = self.forecast_trend_global().loc[:, 'adoption']
                    lmh = self.forecast_low_med_high_global()
                growth = self.tamconfig.loc['growth', region_pds]
                first_year = result.first_valid_index()
                result.loc[first_year, region] = lmh.loc[first_year, 'Medium']
            else:
                self._set_tam_one_region(result=result, region=region,
                        forecast_trend=self.forecast_trend(region),
                        forecast_low_med_high=self.forecast_low_med_high(region))
        result.name = "pds_tam_per_region"
        return result
