import math
from model import dd
import numpy as np
import pandas as pd
from enum import Enum
from model.advanced_controls import AdvancedControls
from model.unitadoption import UnitAdoption


class NetProfitMargin:
    """Implementation for the Net Profit Margin module.

      Arguments:
      ac: advanced_cost.py object, storing settings to control model operation.

      sol_trans_pd_len: float, SOLUTION  Transition Period to Full Net Profit Margin (Years)
      sol_trans_pd_type : NpmTransitionType, SOLUTION  Net Profit Margin During Transition Period
      sol_pct_during_trans_pd : float : Percent of Net Profit Margin During Transition Period

      conv_trans_pd_len: float, CONVENTIONAL Transition Period to Full Net Profit Margin (Years)
      conv_trans_pd_type : NpmTransitionType, CONVENTIONAL Net Profit Margin During Transition Period
      conv_pct_during_trans_pd : float : Percent of Net Profit Margin During Transition Period

      converting_factor : int : Converting factor (For Convert units of adoption)

    """
    FIRST_YEAR = dd.CORE_START_YEAR
    LAST_YEAR = dd.CORE_END_YEAR
    LAST_YEAR_BIG = 2140

    class TransitionPeriodType(Enum):
        FIXED_PERCENT = 1
        LINEAR = 2

    def __init__(self, ac : AdvancedControls,
                 ua : UnitAdoption,
                 sol_trans_pd_len,
                 sol_trans_pd_type,
                 conv_trans_pd_len,
                 conv_trans_pd_type,
                 sol_trans_pd_pct=1,
                 conv_trans_pd_pct=1,
                 converting_factor=1,
                 sol_heteroscedasticity=False,
                 conv_heteroscedasticity=False,
                 ):

        self.ac = ac
        self.ua = ua
        self.sol_trans_pd_len = sol_trans_pd_len
        self.sol_trans_pd_type = sol_trans_pd_type
        if self.sol_trans_pd_type == self.TransitionPeriodType.LINEAR:
            assert sol_trans_pd_pct == 1
        self.sol_trans_pd_pct= sol_trans_pd_pct
        self.conv_trans_pd_len = conv_trans_pd_len
        self.conv_trans_pd_type = conv_trans_pd_type
        if self.conv_trans_pd_type == self.TransitionPeriodType.LINEAR:
            assert conv_trans_pd_pct == 1
        self.conv_trans_pd_pct= conv_trans_pd_pct
        self.converting_factor = converting_factor
        self.conversion_factor_vom = converting_factor
        self.conversion_factor_fom = converting_factor
        self.sol_heteroscedasticity = sol_heteroscedasticity
        self.conv_heteroscedasticity = conv_heteroscedasticity

        self.index = pd.RangeIndex(self.FIRST_YEAR, self.LAST_YEAR + 1)

        self.sol_npm_per_land_unit = self.ac.soln_net_profit_margin_per_iunit

    def pds_npm_calc(self):
        """
        # PDS Technology Net Profit Margin Calculations #

        # Description of Calculations #

        The unit of measure for Net Profit Margin calculation is based on Active units (i.e. current stock in operation)
        , see Units Adoption Table: Total additional CONVENTIONAL Stock / Total additional SOLUTION Stock.  If unit of
        measure for Net Profit Margin calculation is different (e.g., energy use kWh / sq m) then please use Factoring
        for conversions/calculations, etc.
        """
        num_years = len(self.index)
        npm_per_land_unit = pd.Series([self.sol_npm_per_land_unit * self.converting_factor] * num_years)
        net_annual_land_units_adopted = self.ua.net_annual_land_units_adopted().loc[
                                        self.FIRST_YEAR:self.LAST_YEAR].World

        return pd.DataFrame({
            "Date Year": self.index,
            "Net Profit Margin per Land Unit (Functional Unit) SOLUTION": npm_per_land_unit,
            "Net Annual Land Unit (Functional Unit)s Adopted": net_annual_land_units_adopted,
            "Annual Net Profit Margin of Technology/Solution": self.annual_npm(),
            "Cumulative Net Profit Margin of Technology/Solution": 1,
            "New Land Units each Year": 1,
        })

    def lifetime_cost(self):
        """
        LIFETIME COST |  FACTORING - PDS/SOLUTION ONLY
        This table calculates the contribution of each new set of SOLUTION implementation units installed over the
        lifetime of the units, but only for new or replacement units installed during our analysis period.
        Fixed and Variable costs that are constant or changing over time are included.

        :return:
        """
        start_year = self.ac.report_start_year
        end_year = self.ac.report_end_year
        disturbance_rate = self.ac.disturbance_rate
        lifetime_savings_years = self.ac.soln_expected_lifetime
        initial_installation_year = pd.Series(self.index).values


        # Number of implementation Unit Lifetimes To End of Life =MAX(R258C1-R[4]C,0)/R258C3
        num_iul_to_eol = np.maximum(end_year - initial_installation_year, 0) / lifetime_savings_years

        # Number of Implementation Unit Lifetimes to Analysis Period =IF(R259C>R258C1,10^3,0)
        num_iul_to_analysis_pd = np.where(initial_installation_year > end_year, 1000, 0)

        # Years of Life Left at End of Period =IF(R258C3*((ROUNDUP(R[-2]C,0)-R[-2]C))=0,R258C3,(R258C3*((ROUNDUP(R[-2]C,0)-R[-2]C))))
        intermediate = lifetime_savings_years * (np.ceil(num_iul_to_eol) - num_iul_to_eol)
        years_of_life_at_end_of_pd = np.where(intermediate == 0, lifetime_savings_years, intermediate)

        # Annual Functional Units Adopted (Net) =TRANSPOSE(R[-241]C[3]:R[-196]C[3])
        net_annual_land_units_adopted = self.ua.net_annual_land_units_adopted().loc[
                                        self.FIRST_YEAR:self.LAST_YEAR].World
        net_annual_land_units_per_yr = np.insert(np.diff(net_annual_land_units_adopted), 0, [net_annual_land_units_adopted.values[0]])

        cost_at_year = np.array([np.arange(self.FIRST_YEAR, self.LAST_YEAR_BIG)]).T

        # Years since start of study or something, R1C262-...
        # =IF(RC[1]<='Advanced Controls'!R4C8,0,RC[1]-'Advanced Controls'!R4C8)
        years_since_start = np.where(cost_at_year <= start_year, 0, cost_at_year - start_year)

        cond1 = np.hstack([cost_at_year] * len(self.index)) >= initial_installation_year + np.vstack([num_iul_to_analysis_pd] * len(cost_at_year)) * lifetime_savings_years
        cond2 = years_since_start < (end_year - start_year) + years_of_life_at_end_of_pd

        # Verified
        someotherstuff = np.where(self.sol_trans_pd_type == self.TransitionPeriodType.LINEAR, (cost_at_year - initial_installation_year) /  self.sol_trans_pd_len * self.sol_npm_per_land_unit, self.sol_npm_per_land_unit * self.sol_trans_pd_pct)
        no_hetero = np.where(cost_at_year >= initial_installation_year + self.sol_trans_pd_len, self.sol_npm_per_land_unit, someotherstuff)

        part2 = self.converting_factor * net_annual_land_units_per_yr * np.where(self.sol_heteroscedasticity is False,
                                                                                  no_hetero,
                                                                                  np.nan)
        first_part = np.where(cond1, np.where(cond2, part2, 0), 0)
        cost_after_report_end = np.where(cost_at_year > end_year + years_of_life_at_end_of_pd - 1, years_of_life_at_end_of_pd % 1, 1)
        nondisturbance_rate = 1 - disturbance_rate
        lifetime_cost = first_part * cost_after_report_end * nondisturbance_rate
        print(lifetime_cost)

    def _annual_breakout(self):
        #  Here starts the real function
        # Key
        # * RC2 is initial_installation_year
        """
            =IF(
                RC2 >= R259C + R256C * R258C3, #COND1
                IF(
                    RC1 < ( ( R258C1 - R256C1 ) + R257C ), #COND2
                    R11C7 * ( R260C *
                        IF(
                            R531C2 = "N",
                            IF(
                                RC2 >= R259C + R11C4,
                                R11C2,
                                IF(
                                    R11C5 = "Linear",
                                    ( RC2 - R259C ) / ( R11C4 ) * R11C2,
                                    R11C2 * R11C6
                                )
                            ),
                            INDEX(
                                R587C2:R632C2,
                                MOD(
                                    RC2 - R259C,
                                    R258C3
                                ) + 1,
                                1
                            )
                        ) ),
                    0
                ),
                0
            ) *
            IF(
                RC2 > R258C1 + R257C - 1,
                MOD(
                    R257C,
                    1
                ),
                1
            ) * ( 1 - R260C1 )
        """

        #
        # breakout = pd.DataFrame(0, index=np.arange(self.FIRST_YEAR, self.LAST_YEAR_BIG + 1),
        #                         columns=np.arange(self.FIRST_YEAR, self.LAST_YEAR + 1), dtype='float')
        #
        # first_part = None
        # # if initial_installation_year >= N
        # second_part = (years_of_life_at_end_of_pd
        #                if initial_installation_year > end_year + years_of_life_at_end_of_pd - 1
        #                else 1)
        #
        # lifetime_cost = first_part * second_part
        #
