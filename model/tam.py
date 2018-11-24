"""Total Addressible Market module.
"""

import os.path

import data_sources
from model import interpolation
import pandas as pd


class TAM:
  """Total Addressible Market module.
     Arguments:
       datadir: directory where CSV files can be found.
  """
  def __init__(self, datadir, tamconfig):
    """TAM module.

       Arguments
       datadir: directory where CSV files for this solution can be found.
       tamconfig: Pandas dataframe with columns:
          'source_until_2014', 'source_after_2014', 'trend', 'growth', 'low_sd_mult', 'high_sd_mult'
          and rows for each region:
          'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
          'Latin America', 'China', 'India', 'EU', 'USA'
    """
    self.datadir = datadir
    self.tamconfig = tamconfig
    super()

  def _min_max_sd(self, forecast, tamconfig):
    """Return the min, max, and standard deviation for TAM data.
       Arguments:
         forecast: the TAM forecast dataframe for all sources.
         tamconfig: the row from self.tamconfig to use
    """
    source_until_2014 = tamconfig['source_until_2014']
    source_after_2014 = tamconfig['source_after_2014']

    result = pd.DataFrame(0, index=forecast.index.copy(), columns=['Min', 'Max', 'S.D'])
    result.loc[:, 'Min'] = forecast.min(axis=1)
    result.loc[:, 'Max'] = forecast.max(axis=1)
    # Excel STDDEV.P is a whole population stddev, ddof=0
    columns = data_sources.matching_columns(forecast.columns, source_until_2014, groups_only=True)
    m = forecast.loc[:2014, columns].std(axis=1, ddof=0)
    m.name = 'S.D'
    result.update(m)
    columns = data_sources.matching_columns(forecast.columns, source_after_2014, groups_only=True)
    m = forecast.loc[2015:, columns].std(axis=1, ddof=0)
    m.name = 'S.D'
    result.update(m)

    return result

  def _low_med_high(self, forecast, min_max_sd, tamconfig):
    """Return the selected data sources as Medium, and N stddev away as Low and High.

       Arguments:
         forecast: DataFrame of all of the data sources, source name as the column name.
         min_max_sd: DataFrame with columns for the Minimum, Maxiumum, and Standard deviation.
         tamconfig: the row from self.tamconfig to use
    """
    source_until_2014 = tamconfig['source_until_2014']
    source_after_2014 = tamconfig['source_after_2014']
    low_sd_mult = tamconfig['low_sd_mult']
    high_sd_mult = tamconfig['high_sd_mult']

    result = pd.DataFrame(0, index=forecast.index.copy(), columns=['Low', 'Medium', 'High'])
    columns = data_sources.matching_columns(forecast.columns, source_until_2014)
    m = forecast.loc[:2014, columns].mean(axis=1)
    m.name = 'Medium'
    result.update(m)
    columns = data_sources.matching_columns(forecast.columns, source_after_2014)
    m = forecast.loc[2015:, columns].mean(axis=1)
    m.name = 'Medium'
    result.update(m)

    result.loc[:, 'Low'] = result.loc[:, 'Medium'] - (min_max_sd.loc[:, 'S.D'] * low_sd_mult)
    result.loc[:, 'High'] = result.loc[:, 'Medium'] + (min_max_sd.loc[:, 'S.D'] * high_sd_mult)
    return result

  def forecast_data_global(self):
    """ 'TAM Data'!B45:Q94 """
    filename = os.path.join(self.datadir, 'tam_forecast_global.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_global"
    return result

  def forecast_min_max_sd_global(self):
    """ 'TAM Data'!V45:Y94 """
    result = self._min_max_sd(forecast=self.forecast_data_global(),
        tamconfig=self.tamconfig['World'])
    result.name = 'forecast_min_max_sd_global'
    return result

  def forecast_low_med_high_global(self):
    """ 'TAM Data'!AA45:AC94 """
    result = self._low_med_high(forecast=self.forecast_data_global(),
        min_max_sd=self.forecast_min_max_sd_global(),
        tamconfig=self.tamconfig['World'])
    result.name = 'forecast_low_med_high_global'
    return result

  def forecast_trend_global(self, trend=None):
    """Forecast for the 'World' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX50:BZ96     Degree2: 'TAM Data'!CE50:CH96
       Degree3: 'TAM Data'!CM50:CQ96    Exponential: 'TAM Data'!CV50:CX96
    """
    growth = self.tamconfig.loc['growth', 'World']
    if not trend:
      trend = self.tamconfig.loc['trend', 'World']
    data = self.forecast_low_med_high_global().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_global_' + trend.lower()
    return result

  def forecast_data_oecd90(self):
    """ 'TAM Data'!B163:Q212 """
    filename = os.path.join(self.datadir, 'tam_forecast_oecd90.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_oecd90"
    return result

  def forecast_min_max_sd_oecd90(self):
    """ 'TAM Data'!V163:Y212 """
    result = self._min_max_sd(forecast=self.forecast_data_oecd90(),
        tamconfig=self.tamconfig['OECD90'])
    result.name = 'forecast_min_max_sd_oecd90'
    return result

  def forecast_low_med_high_oecd90(self):
    """ 'TAM Data'!AA163:AC212 """
    result = self._low_med_high(forecast=self.forecast_data_oecd90(),
        min_max_sd=self.forecast_min_max_sd_oecd90(),
        tamconfig=self.tamconfig['OECD90'])
    result.name = 'forecast_low_med_high_oecd90'
    return result

  def forecast_trend_oecd90(self, trend=None):
    """Forecast for the 'OECD90' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX168:BZ214     Degree2: 'TAM Data'!CE168:CH214
       Degree3: 'TAM Data'!CM168:CQ214    Exponential: 'TAM Data'!CV168:CX214
    """
    growth = self.tamconfig.loc['growth', 'OECD90']
    if not trend:
      trend = self.tamconfig.loc['trend', 'OECD90']
    data = self.forecast_low_med_high_oecd90().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_oecd90_' + trend.lower()
    return result

  def forecast_data_eastern_europe(self):
    """ 'TAM Data'!B227:Q276 """
    filename = os.path.join(self.datadir, 'tam_forecast_eastern_europe.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_eastern_europe"
    return result

  def forecast_min_max_sd_eastern_europe(self):
    """ 'TAM Data'!V227:Y276 """
    result = self._min_max_sd(forecast=self.forecast_data_eastern_europe(),
        tamconfig=self.tamconfig['Eastern Europe'])
    result.name = 'forecast_min_max_sd_eastern_europe'
    return result

  def forecast_low_med_high_eastern_europe(self):
    """ 'TAM Data'!AA227:AC276 """
    result = self._low_med_high(forecast=self.forecast_data_eastern_europe(),
        min_max_sd=self.forecast_min_max_sd_eastern_europe(),
        tamconfig=self.tamconfig['Eastern Europe'])
    result.name = 'forecast_low_med_high_eastern_europe'
    return result

  def forecast_trend_eastern_europe(self, trend=None):
    """Forecast for the 'Eastern Europe' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX232:BZ278     Degree2: 'TAM Data'!CE232:CH278
       Degree3: 'TAM Data'!CM232:CQ278    Exponential: 'TAM Data'!CV232:CX278
    """
    growth = self.tamconfig.loc['growth', 'Eastern Europe']
    if not trend:
      trend = self.tamconfig.loc['trend', 'Eastern Europe']
    data = self.forecast_low_med_high_eastern_europe().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_eastern_europe_' + trend.lower()
    return result

  def forecast_data_asia_sans_japan(self):
    """ 'TAM Data'!B290:Q339 """
    filename = os.path.join(self.datadir, 'tam_forecast_asia_sans_japan.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_asia_sans_japan"
    return result

  def forecast_min_max_sd_asia_sans_japan(self):
    """ 'TAM Data'!V290:Y339 """
    result = self._min_max_sd(forecast=self.forecast_data_asia_sans_japan(),
        tamconfig=self.tamconfig['Asia (Sans Japan)'])
    result.name = 'forecast_min_max_sd_asia_sans_japan'
    return result

  def forecast_low_med_high_asia_sans_japan(self):
    """ 'TAM Data'!AA290:AC339 """
    result = self._low_med_high(forecast=self.forecast_data_asia_sans_japan(),
        min_max_sd=self.forecast_min_max_sd_asia_sans_japan(),
        tamconfig=self.tamconfig['Asia (Sans Japan)'])
    result.name = 'forecast_low_med_high_asia_sans_japan'
    return result

  def forecast_trend_asia_sans_japan(self, trend=None):
    """Forecast for the 'Asia (Sans Japan)' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX295:BZ341     Degree2: 'TAM Data'!CE295:CH341
       Degree3: 'TAM Data'!CM295:CQ341    Exponential: 'TAM Data'!CV295:CX341
    """
    growth = self.tamconfig.loc['growth', 'Asia (Sans Japan)']
    if not trend:
      trend = self.tamconfig.loc['trend', 'Asia (Sans Japan)']
    data = self.forecast_low_med_high_asia_sans_japan().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_asia_sans_japan_' + trend.lower()
    return result

  def forecast_data_middle_east_and_africa(self):
    """ 'TAM Data'!B353:Q402 """
    filename = os.path.join(self.datadir, 'tam_forecast_middle_east_and_africa.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_middle_east_and_africa"
    return result

  def forecast_min_max_sd_middle_east_and_africa(self):
    """ 'TAM Data'!V353:Y402 """
    result = self._min_max_sd(forecast=self.forecast_data_middle_east_and_africa(),
        tamconfig=self.tamconfig['Middle East and Africa'])
    result.name = 'forecast_min_max_sd_middle_east_and_africa'
    return result

  def forecast_low_med_high_middle_east_and_africa(self):
    """ 'TAM Data'!AA353:AC402 """
    result = self._low_med_high(forecast=self.forecast_data_middle_east_and_africa(),
        min_max_sd=self.forecast_min_max_sd_middle_east_and_africa(),
        tamconfig=self.tamconfig['Middle East and Africa'])
    result.name = 'forecast_low_med_high_middle_east_and_africa'
    return result

  def forecast_trend_middle_east_and_africa(self, trend=None):
    """Forecast for the 'Middle East and Africa' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX358:BZ404     Degree2: 'TAM Data'!CE358:CH404
       Degree3: 'TAM Data'!CM358:CQ404    Exponential: 'TAM Data'!CV358:CX404
    """
    growth = self.tamconfig.loc['growth', 'Middle East and Africa']
    if not trend:
      trend = self.tamconfig.loc['trend', 'Middle East and Africa']
    data = self.forecast_low_med_high_middle_east_and_africa().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_middle_east_and_africa_' + trend.lower()
    return result

  def forecast_data_latin_america(self):
    """ 'TAM Data'!B416:Q465 """
    filename = os.path.join(self.datadir, 'tam_forecast_latin_america.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_latin_america"
    return result

  def forecast_min_max_sd_latin_america(self):
    """ 'TAM Data'!V416:Y465 """
    result = self._min_max_sd(forecast=self.forecast_data_latin_america(),
        tamconfig=self.tamconfig['Latin America'])
    result.name = 'forecast_min_max_sd_latin_america'
    return result

  def forecast_low_med_high_latin_america(self):
    """ 'TAM Data'!AA416:AC465 """
    result = self._low_med_high(forecast=self.forecast_data_latin_america(),
        min_max_sd=self.forecast_min_max_sd_latin_america(),
        tamconfig=self.tamconfig['Latin America'])
    result.name = 'forecast_low_med_high_latin_america'
    return result

  def forecast_trend_latin_america(self, trend=None):
    """Forecast for the 'Latin America' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX421:BZ467     Degree2: 'TAM Data'!CE421:CH467
       Degree3: 'TAM Data'!CM421:CQ467    Exponential: 'TAM Data'!CV421:CX467
    """
    growth = self.tamconfig.loc['growth', 'Latin America']
    if not trend:
      trend = self.tamconfig.loc['trend', 'Latin America']
    data = self.forecast_low_med_high_latin_america().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_latin_america_' + trend.lower()
    return result

  def forecast_data_china(self):
    """ 'TAM Data'!B479:Q528 """
    filename = os.path.join(self.datadir, 'tam_forecast_china.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_china"
    return result

  def forecast_min_max_sd_china(self):
    """ 'TAM Data'!V479:Y528 """
    result = self._min_max_sd(forecast=self.forecast_data_china(),
        tamconfig=self.tamconfig['China'])
    result.name = 'forecast_min_max_sd_china'
    return result

  def forecast_low_med_high_china(self):
    """ 'TAM Data'!AA479:AC528 """
    result = self._low_med_high(forecast=self.forecast_data_china(),
        min_max_sd=self.forecast_min_max_sd_china(),
        tamconfig=self.tamconfig['China'])
    result.name = 'forecast_low_med_high_china'
    return result

  def forecast_trend_china(self, trend=None):
    """Forecast for the 'China' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX484:BZ530     Degree2: 'TAM Data'!CE484:CH530
       Degree3: 'TAM Data'!CM484:CQ530    Exponential: 'TAM Data'!CV484:CX530
    """
    growth = self.tamconfig.loc['growth', 'China']
    if not trend:
      trend = self.tamconfig.loc['trend', 'China']
    data = self.forecast_low_med_high_china().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_china_' + trend.lower()
    return result

  def forecast_data_india(self):
    """ 'TAM Data'!B543:Q592 """
    filename = os.path.join(self.datadir, 'tam_forecast_india.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_india"
    return result

  def forecast_min_max_sd_india(self):
    """ 'TAM Data'!V543:Y592 """
    result = self._min_max_sd(forecast=self.forecast_data_india(),
        tamconfig=self.tamconfig['India'])
    result.name = 'forecast_min_max_sd_india'
    return result

  def forecast_low_med_high_india(self):
    """ 'TAM Data'!AA543:AC592 """
    result = self._low_med_high(forecast=self.forecast_data_india(),
        min_max_sd=self.forecast_min_max_sd_india(),
        tamconfig=self.tamconfig['India'])
    result.name = 'forecast_low_med_high_india'
    return result

  def forecast_trend_india(self, trend=None):
    """Forecast for the 'India' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX548:BZ594     Degree2: 'TAM Data'!CE548:CH594
       Degree3: 'TAM Data'!CM548:CQ594    Exponential: 'TAM Data'!CV548:CX594
    """
    growth = self.tamconfig.loc['growth', 'India']
    if not trend:
      trend = self.tamconfig.loc['trend', 'India']
    data = self.forecast_low_med_high_india().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_india_' + trend.lower()
    return result

  def forecast_data_eu(self):
    """ 'TAM Data'!B607:Q656 """
    filename = os.path.join(self.datadir, 'tam_forecast_eu.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_eu"
    return result

  def forecast_min_max_sd_eu(self):
    """ 'TAM Data'!V607:Y656 """
    result = self._min_max_sd(forecast=self.forecast_data_eu(), tamconfig=self.tamconfig['EU'])
    result.name = 'forecast_min_max_sd_eu'
    return result

  def forecast_low_med_high_eu(self):
    """ 'TAM Data'!AA607:AC656 """
    result = self._low_med_high(forecast=self.forecast_data_eu(),
        min_max_sd=self.forecast_min_max_sd_eu(), tamconfig=self.tamconfig['EU'])
    result.name = 'forecast_low_med_high_eu'
    return result

  def forecast_trend_eu(self, trend=None):
    """Forecast for the 'EU' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX612:BZ658     Degree2: 'TAM Data'!CE612:CH658
       Degree3: 'TAM Data'!CM612:CQ658    Exponential: 'TAM Data'!CV612:CX658
    """
    growth = self.tamconfig.loc['growth', 'EU']
    if not trend:
      trend = self.tamconfig.loc['trend', 'EU']
    data = self.forecast_low_med_high_eu().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_eu_' + trend.lower()
    return result

  def forecast_data_usa(self):
    """ 'TAM Data'!B672:Q721 """
    filename = os.path.join(self.datadir, 'tam_forecast_usa.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.name = "forecast_data_usa"
    return result

  def forecast_min_max_sd_usa(self):
    """ 'TAM Data'!V672:Y721 """
    result = self._min_max_sd(forecast=self.forecast_data_usa(), tamconfig=self.tamconfig['USA'])
    result.name = 'forecast_min_max_sd_usa'
    return result

  def forecast_low_med_high_usa(self):
    """ 'TAM Data'!AA672:AC721 """
    result = self._low_med_high(forecast=self.forecast_data_usa(),
        min_max_sd=self.forecast_min_max_sd_usa(), tamconfig=self.tamconfig['USA'])
    result.name = 'forecast_low_med_high_usa'
    return result

  def forecast_trend_usa(self, trend=None):
    """Forecast for the 'USA' region via one of several interpolation algorithms.
       Linear: 'TAM Data'!BX677:BZ723     Degree2: 'TAM Data'!CE677:CH723
       Degree3: 'TAM Data'!CM677:CQ723    Exponential: 'TAM Data'!CV677:CX723
    """
    growth = self.tamconfig.loc['growth', 'USA']
    if not trend:
      trend = self.tamconfig.loc['trend', 'USA']
    data = self.forecast_low_med_high_usa().loc[:, growth]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'forecast_trend_usa_' + trend.lower()
    return result
