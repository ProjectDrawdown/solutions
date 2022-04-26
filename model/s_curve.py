"""Sigmoid Curve adoption implementation."""
import math
import numpy as np
import pandas as pd
import model.dd as dd
from model.data_handler import DataHandler
from model.decorators import data_func

def make_scurve_config(base_year, tamdata, configdict, last_year=2050, use_tam_2014=False):
    """Create a configuration for a standard S-Curve or Bass Diffusion S-Curve.  Configdict should contain required parameters
    'ref_base_adoption', 'pds_adoption_final_percentage', and for Bass Diffusion S-Curves may also contain 'pds_adoption_s_curve_innovation'
    and 'pds_adoption_s_curve_imitation'.  These are all AC fields, and can be obtained via ac.asdict().
    Parameter use_tam_2014 is a quirks parameter to match a bug in the Excel that uses the TAM from the year 2014 instead of base_year
    as it ought to."""
    sconfig = pd.DataFrame({'base_year': base_year, 'last_year': last_year}, index=dd.REGIONS)
    sconfig['base_adoption'] = pd.Series(configdict['ref_base_adoption'])
    sconfig['base_percent'] = sconfig['base_adoption'] / tamdata.loc[base_year]
    sconfig['last_percent'] = pd.Series(configdict['pds_adoption_final_percentage'])
    sconfig['last_pds_tam'] = tamdata.loc[[last_year]].T
    if 'pds_adoption_s_curve_innovation' in configdict:
        sconfig['innovation'] = pd.Series(configdict['pds_adoption_s_curve_innovation'])
    if 'pds_adoption_s_curve_imitation' in configdict:
        sconfig['imitation'] = pd.Series(configdict['pds_adoption_s_curve_imitation'])
    
    if use_tam_2014:
        # Excel bug calulates base_adoption from TAM[2014] instead of TAM[base_year].  For compatibility, we can do the same
        sconfig['base_adoption'] = sconfig['base_percent'] *  tamdata.loc[2014]
    return sconfig

class SCurve(DataHandler):
    def __init__(self, sconfig, transition_period=16):
        """S-Curve (sigmoid adoption forecast) implementation.
         Arguments:
           transition_period (int): number of years of transition period, must be an even number.
           sconfig: Pandas dataframe with columns:
             'base_year', 'last_year', 'base_percent', 'last_percent',
             'base_adoption', 'last_pds_tam',
             (needed for Bass Diffusion model): 'M', 'P', 'Q'
            and rows for each region:
             'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', etc
        """
        self.transition_period = transition_period
        self.sconfig = sconfig

    @data_func
    def _sigmoid_logistic(self, base_year, last_year, base_percent, last_percent,
                          base_adoption, last_pds_tam):
        """Logistic sigmoid for market growth estimation.

        Appendix 4 of Documentation/RRS_Model_Framework_and_Guidelines_v1.1.pdf
        describes the S-Curve implementations. This is the first one, the logistic sigmoid.
        Though this sigmoid resembles other market growth sigmoid functions, it was developed
        by and is unique to Drawdown. We have directly converted the Excel implementation
        to Python, with comments noting what was done and why.

        Arguments:
          base_year (int): base year of the calculation, Yb in Appendix 4.
              last_year (int): Ymax in Appendix 4. The last_year is the ending target of the
              sigmoid, the second half is supposed to cross through last_percent at last_year.
          base_percent (float): percentage adoption at base_year.
          last_percent (float): percentage adoption at last_year.
          base_adoption (float): number of funits adopted at base_year.
          last_pds_tam (float): total addressible market in the last year.
        """
        result = pd.DataFrame(dtype=np.float64)
        for year in range(dd.AD_START_YEAR, dd.AD_END_YEAR + 1):
            # the First Half function from Building Automation Systems "S Curve"!AH24:
            # =(((1-AH$18)/(1+EXP(-((LN(1/AH$18-1)-LN(1/AH$21-1))/(AH$20-AH$17))
            #     *($AG24-(LN(1/AH$18-1)/((LN(1/AH$18-1)-LN(1/AH$21-1))/(AH$20-AH$17))+AH$17))))
            #     *'Unit Adoption Calculations'!B$105)+AH$21*AH$18*'Unit Adoption Calculations'!B$105)
            #  *
            # ((($AG$60-$AG$24)-($AG$60-$AG24))/($AG$60-$AG$24))
            #  +
            # ((($AG$60-$AG24)/($AG$60-base_year))*AH$19)
            # where:
            #   $AG24 = year
            #   AH$17 = $AG$24 = 2014 = base_year
            #   AH$18 = base_percent
            #   AH$19 = base_adoption
            #   AH$20 = $AG$60 = 2050 = last_year
            #   AH$21 = last_percent
            #   'Unit Adoption Calculations'!B$105 = last_pds_tam

            #
            # In Excel models last_percent is set to 0.999999999999999 to mean 100% adoption
            # (which Excel helpfully displays as 100%).
            # LN(1/AH$21-1) = LN(1/1-1) = LN(0) (which doesn't exist), so being asymptotically
            # close to 100% ends up being approximately LN(0.0000000000000009) instead of LN(0).
            # We pull in the value which Excel comes up with, -34.65735902799730.
            magic = -34.65735902799730
            np_err_settings = np.seterr(divide='raise')
            try:
                # lcot == log change over time
                # =((LN(1/AH$18-1)-LN(1/AH$21-1))/(AH$20-AH$17))
                last_percent_log_term = magic if last_percent >= 0.999999 else math.log(
                    1.0 / last_percent - 1.0)
                lcot = ((math.log(1.0 / base_percent - 1.0) - last_percent_log_term) /
                    (last_year - base_year))

                # term1a = ((1-AH$18)/(1+EXP(-((LN(1/AH$18-1)-LN(1/AH$21-1))/(AH$20-AH$17))*
                #     ($AG24-(LN(1/AH$18-1)/((LN(1/AH$18-1)-LN(1/AH$21-1))/(AH$20-AH$17))+AH$17))
                #     ))*'Unit Adoption Calculations'!B$105)
                term1a = ((1.0 - base_percent) / (1.0 + math.exp(-lcot * (year - (math.log(
                    1.0 / base_percent - 1.0) / lcot + base_year)))) * last_pds_tam)

                # term1b = AH$21*AH$18*'Unit Adoption Calculations'!B$105
                term1b = last_percent * base_percent * last_pds_tam

                # term2 = ((($AG$60-$AG$24)-($AG$60-$AG24))/($AG$60-$AG$24))
                term2 = ((last_year - base_year) - (last_year - year)) / (last_year - base_year)

                # term3 = ((($AG$60-$AG24)/($AG$60-base_year))*AH$19)
                term3 = ((last_year - year) / (last_year - base_year)) * base_adoption

                firstHalf = (term1a + term1b) * term2 + term3

                # The Second Half function from Building Automation Systems "S Curve"!AI24:
                # =((1-AH$18)/(1+EXP(-((LN(1/AH$18-1)-LN(1/AH$21-1))/(AH$20-AH$17))
                #    *($AG24-(LN(1/AH$18-1)/((LN(1/AH$18-1)-LN(1/AH$21-1))/(AH$20-AH$17))+AH$17))))
                #    *'Unit Adoption Calculations'!B$105+AH$19/AH$21)
                #
                # using the same definitions for the cells as in the First Half function above.
                # This is the same as term1a plus (AH$19/AH$21)
                secondHalf = term1a + (base_adoption / last_percent)
            except (ZeroDivisionError, FloatingPointError):
                firstHalf = np.nan
                secondHalf = np.nan
            np.seterr(**np_err_settings)
            result.loc[year, 'first_half'] = firstHalf
            result.loc[year, 'second_half'] = secondHalf

        result.index.name = 'Year'
        return result

    @data_func
    def logistic_adoption(self):
        """Calculate Logistic S-Curve for a solution."""
        result = pd.DataFrame()
        for region in self.sconfig.index:
            last_year = self.sconfig.loc[region, 'last_year']
            last_percent = self.sconfig.loc[region, 'last_percent']
            df = self._sigmoid_logistic(
                base_year=self.sconfig.loc[region, 'base_year'],
                last_year=last_year,
                base_percent=self.sconfig.loc[region, 'base_percent'],
                last_percent=last_percent,
                base_adoption=self.sconfig.loc[region, 'base_adoption'],
                last_pds_tam=self.sconfig.loc[region, 'last_pds_tam'])
            for year, row in df.iterrows():
                if last_percent == 0.0:
                    result.loc[year, region] = np.nan
                elif (year <= (last_year - (self.transition_period / 2))):
                    result.loc[year, region] = row['first_half']
                elif (year < (last_year + (self.transition_period / 2))):
                    a = ((last_year + self.transition_period / 2 - year) /
                         self.transition_period) * row['first_half']
                    b = ((year - (last_year - self.transition_period / 2)) /
                         self.transition_period) * row['second_half']
                    result.loc[year, region] = a + b
                else:
                    result.loc[year, region] = row['second_half']
        result.name = 'logistic_adoption'
        result.index.name = 'Year'
        return result

    @data_func
    def bass_diffusion_adoption(self):
        """Calculate Bass Diffusion S-Curve for a solution."""
        result = pd.DataFrame()
        for region in self.sconfig.index:
            M = self.sconfig.loc[region, 'last_pds_tam']
            P = self.sconfig.loc[region, 'innovation']
            Q = self.sconfig.loc[region, 'imitation']
            base_year = self.sconfig.loc[region, 'base_year']
            result.loc[base_year, region] = prev = self.sconfig.loc[region, 'base_adoption']
            for year in range(base_year + 1, dd.AD_END_YEAR + 1):
                b = prev + (P + (Q * prev / M)) * (M - prev)
                result.loc[year, region] = b
                prev = b
            if base_year > dd.AD_START_YEAR:
                prev = self.sconfig.loc[region, 'base_adoption']
                for year in range(base_year-1,dd.AD_START_YEAR-1,-1):
                    b = prev - (P + (Q * prev / M)) * (M - prev)
                    result.loc[year, region] = b
                    prev = b       
                result.sort_index(inplace=True)         
        result.name = 'bass_diffusion_adoption'
        result.index.name = 'Year'
        return result
