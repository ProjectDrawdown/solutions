"""
An end-to-end test which pulls data from the original Excel models, not just the final answers
but each intermediate step. It then compares the Python result at each step of the calculation,
to ensure that the new implementation not only gets the same answers but does so for the
same reasons.
"""
# pylint: disable=line-too-long

import functools
import pathlib
import re
import numpy as np
import pandas as pd
import pytest
import zipfile


solutiondir = pathlib.Path(__file__).parents[1].joinpath('solution')


def cell_to_offsets(cell):
    """Convert an Excel reference like C33 to (row, col)."""
    (col, row) = filter(None, re.split(r'(\d+)', cell))
    colnum = 0
    for i, c in enumerate(col):
        colnum = (colnum + min(i, 1)) * 26 + (ord(c.upper()) - ord('A'))
    return (colnum, int(row) - 1)


def get_pd_read_excel_args(r):
    """Convert 'A11:G55' notation to (usecols, skiprows, nrows) for pd.read_excel."""
    (start, end) = r.split(':')
    (startcol, startrow) = cell_to_offsets(start)
    startrow = int(startrow)
    (endcol, endrow) = cell_to_offsets(end)
    endrow = int(endrow)
    usecols = range(startcol, endcol + 1)
    skiprows = startrow
    nrows = endrow - startrow + 1
    return (usecols, skiprows, nrows)


def verify_aez_data(obj, verify, cohort):
    """Verified tables in AEZ Data."""
    if cohort == 2018:
        verify['AEZ Data'] = [
                ('A48:H53', obj.ae.get_land_distribution().reset_index().iloc[:6, :], None, None),
                ('A55:H58', obj.ae.get_land_distribution().reset_index().iloc[6:, :], None, None)
        ]
    elif cohort == 2019:
        # Cohort 2019 added more solutions which shifted rows downward
        verify['AEZ Data'] = [
                ('A53:H58', obj.ae.get_land_distribution().reset_index().iloc[:6, :], None, None),
                ('A60:H63', obj.ae.get_land_distribution().reset_index().iloc[6:, :], None, None)
        ]
    elif cohort == 2020:
        # Eight Thermal Moisture Regimes
        verify['AEZ Data'] = [
                ('A53:J58', obj.ae.get_land_distribution().reset_index().iloc[:6, :], None, None),
                ('A60:J63', obj.ae.get_land_distribution().reset_index().iloc[6:, :], None, None)
        ]

    else:
        raise ValueError(f"unknown cohort {cohort}")
    return verify


def _get_interpolation_trend_masks(func):
    """If the TAM/Adoption data being analyzed is very close to linear, then the 2nd/3rd order
       polynomial and exponential curve fits degenerate to where only the x^1 and constant terms
       matter and the higher order terms do not.

       For example in biochar, Excel and Python both come up with {x}=1.57e+07 & const=1.049e+09
       For degree2, Python comes up with -1.15e-09 while Excel decides it is -1.32e-09, but
       it doesn't matter because they are 16 orders of magnitude less than the {x} term.

       If the data is very close to linear, skip comparing the higher order curve fits.
    """
    degree2 = func(trend='Degree2')
    d2_mask = d3_mask = exp_mask = None
    if abs(degree2.loc[2015, 'x'] / degree2.loc[2015, 'x^2']) > 1e12:
        d2_mask = degree2.reset_index(drop=True).copy(deep=True)
        d2_mask.loc[:, :] = False
        d2_mask['x^2'] = True
        d3_mask = func(trend='Degree3').reset_index(drop=True).copy(deep=True)
        d3_mask.loc[:, :] = False
        d3_mask['x^2'] = True
        d3_mask['x^3'] = True
        exp_mask = func(trend='Exponential').reset_index(
            drop=True).copy(deep=True)
        exp_mask.loc[:, :] = False
        exp_mask['e^x'] = True
    return (d2_mask, d3_mask, exp_mask)


def verify_tam_data(obj, verify):
    """Verified tables in TAM Data."""
    func = functools.partial(obj.tm.forecast_trend, region='World')
    (d2_mask, d3_mask, exp_mask) = _get_interpolation_trend_masks(func=func)
    verify['TAM Data'] = [
            ('W46:Y94', obj.tm.forecast_min_max_sd(region='World').reset_index(drop=True), None, None),
            ('AA46:AC94', obj.tm.forecast_low_med_high(region='World').reset_index(drop=True), None, None),
            ('BX50:BZ96', obj.tm.forecast_trend(region='World', trend='Linear').reset_index(drop=True), None, None),
            ('CE50:CH96', obj.tm.forecast_trend(region='World', trend='Degree2').reset_index(drop=True), d2_mask, None),
            ('CM50:CQ96', obj.tm.forecast_trend(region='World', trend='Degree3').reset_index(drop=True), d3_mask, None),
            ('CV50:CX96', obj.tm.forecast_trend(region='World', trend='Exponential').reset_index(drop=True), exp_mask, None),
            ('DZ45:EA91', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'World']], None, None),
            # TODO Figure out PDS TAM handling
            ('W164:Y212', obj.tm.forecast_min_max_sd(region='OECD90').reset_index(drop=True), None, None),
            ('AA164:AC212', obj.tm.forecast_low_med_high(region='OECD90').reset_index(drop=True), None, None),
            ('BX168:BZ214', obj.tm.forecast_trend(region='OECD90', trend='Linear').reset_index(drop=True), None, None),
            ('CE168:CH214', obj.tm.forecast_trend(region='OECD90', trend='Degree2').reset_index(drop=True), None, None),
            ('CM168:CQ214', obj.tm.forecast_trend(region='OECD90', trend='Degree3').reset_index(drop=True), None, None),
            ('CV168:CX214', obj.tm.forecast_trend(region='OECD90', trend='Exponential').reset_index(drop=True), None, None),
            ('DZ163:EA209', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'OECD90']], None, None),
            ('W228:Y276', obj.tm.forecast_min_max_sd(region='Eastern Europe').reset_index(drop=True), None, None),
            ('AA228:AC276', obj.tm.forecast_low_med_high(region='Eastern Europe').reset_index(drop=True), None, None),
            ('BX232:BZ278', obj.tm.forecast_trend(region='Eastern Europe', trend='Linear').reset_index(drop=True), None, None),
            ('CE232:CH278', obj.tm.forecast_trend(region='Eastern Europe', trend='Degree2').reset_index(drop=True), None, None),
            ('CM232:CQ278', obj.tm.forecast_trend(region='Eastern Europe', trend='Degree3').reset_index(drop=True), None, None),
            ('CV232:CX278', obj.tm.forecast_trend(region='Eastern Europe', trend='Exponential').reset_index(drop=True), None, None),
            ('DZ227:EA273', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'Eastern Europe']], None, None),
            ('W291:Y339', obj.tm.forecast_min_max_sd(region='Asia (Sans Japan)').reset_index(drop=True), None, None),
            ('AA291:AC339', obj.tm.forecast_low_med_high(region='Asia (Sans Japan)').reset_index(drop=True), None, None),
            ('BX295:BZ341', obj.tm.forecast_trend(region='Asia (Sans Japan)', trend='Linear').reset_index(drop=True), None, None),
            ('CE295:CH341', obj.tm.forecast_trend(region='Asia (Sans Japan)', trend='Degree2').reset_index(drop=True), None, None),
            ('CM295:CQ341', obj.tm.forecast_trend(region='Asia (Sans Japan)', trend='Degree3').reset_index(drop=True), None, None),
            ('CV295:CX341', obj.tm.forecast_trend(region='Asia (Sans Japan)', trend='Exponential').reset_index(drop=True), None, None),
            ('DZ290:EA336', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'Asia (Sans Japan)']], None, None),
            ('W354:Y402', obj.tm.forecast_min_max_sd(region='Middle East and Africa').reset_index(drop=True), None, None),
            ('AA354:AC402', obj.tm.forecast_low_med_high(region='Middle East and Africa').reset_index(drop=True), None, None),
            ('BX358:BZ404', obj.tm.forecast_trend(region='Middle East and Africa', trend='Linear').reset_index(drop=True), None, None),
            ('CE358:CH404', obj.tm.forecast_trend(region='Middle East and Africa', trend='Degree2').reset_index(drop=True), None, None),
            ('CM358:CQ404', obj.tm.forecast_trend(region='Middle East and Africa', trend='Degree3').reset_index(drop=True), None, None),
            ('CV358:CX404', obj.tm.forecast_trend(region='Middle East and Africa', trend='Exponential').reset_index(drop=True), None, None),
            ('DZ353:EA399', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'Middle East and Africa']], None, None),
            ('W417:Y465', obj.tm.forecast_min_max_sd(region='Latin America').reset_index(drop=True), None, None),
            ('AA417:AC465', obj.tm.forecast_low_med_high(region='Latin America').reset_index(drop=True), None, None),
            ('BX421:BZ467', obj.tm.forecast_trend(region='Latin America', trend='Linear').reset_index(drop=True), None, None),
            ('CE421:CH467', obj.tm.forecast_trend(region='Latin America', trend='Degree2').reset_index(drop=True), None, None),
            ('CM421:CQ467', obj.tm.forecast_trend(region='Latin America', trend='Degree3').reset_index(drop=True), None, None),
            ('CV421:CX467', obj.tm.forecast_trend(region='Latin America', trend='Exponential').reset_index(drop=True), None, None),
            ('DZ416:EA462', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'Latin America']], None, None),
            ('W480:Y528', obj.tm.forecast_min_max_sd(region='China').reset_index(drop=True), None, None),
            ('AA480:AC528', obj.tm.forecast_low_med_high(region='China').reset_index(drop=True), None, None),
            ('BX484:BZ530', obj.tm.forecast_trend(region='China', trend='Linear').reset_index(drop=True), None, None),
            ('CE484:CH530', obj.tm.forecast_trend(region='China', trend='Degree2').reset_index(drop=True), None, None),
            ('CM484:CQ530', obj.tm.forecast_trend(region='China', trend='Degree3').reset_index(drop=True), None, None),
            ('CV484:CX530', obj.tm.forecast_trend(region='China', trend='Exponential').reset_index(drop=True), None, None),
            ('DZ479:EA525', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'China']], None, None),
            ('W544:Y592', obj.tm.forecast_min_max_sd(region='India').reset_index(drop=True), None, None),
            ('AA544:AC592', obj.tm.forecast_low_med_high(region='India').reset_index(drop=True), None, None),
            ('BX548:BZ594', obj.tm.forecast_trend(region='India', trend='Linear').reset_index(drop=True), None, None),
            ('CE548:CH594', obj.tm.forecast_trend(region='India', trend='Degree2').reset_index(drop=True), None, None),
            ('CM548:CQ594', obj.tm.forecast_trend(region='India', trend='Degree3').reset_index(drop=True), None, None),
            ('CV548:CX594', obj.tm.forecast_trend(region='India', trend='Exponential').reset_index(drop=True), None, None),
            ('DZ543:EA589', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'India']], None, None),
            ('W608:Y656', obj.tm.forecast_min_max_sd(region='EU').reset_index(drop=True), None, None),
            ('AA608:AC656', obj.tm.forecast_low_med_high(region='EU').reset_index(drop=True), None, None),
            ('BX612:BZ658', obj.tm.forecast_trend(region='EU', trend='Linear').reset_index(drop=True), None, None),
            ('CE612:CH658', obj.tm.forecast_trend(region='EU', trend='Degree2').reset_index(drop=True), None, None),
            ('CM612:CQ658', obj.tm.forecast_trend(region='EU', trend='Degree3').reset_index(drop=True), None, None),
            ('CV612:CX658', obj.tm.forecast_trend(region='EU', trend='Exponential').reset_index(drop=True), None, None),
            ('DZ607:EA653', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'EU']], None, None),
            ('W673:Y721', obj.tm.forecast_min_max_sd(region='USA').reset_index(drop=True), None, None),
            ('AA673:AC721', obj.tm.forecast_low_med_high(region='USA').reset_index(drop=True), None, None),
            ('BX677:BZ723', obj.tm.forecast_trend(region='USA', trend='Linear').reset_index(drop=True), None, None),
            ('CE677:CH723', obj.tm.forecast_trend(region='USA', trend='Degree2').reset_index(drop=True), None, None),
            ('CM677:CQ723', obj.tm.forecast_trend(region='USA', trend='Degree3').reset_index(drop=True), None, None),
            ('CV677:CX723', obj.tm.forecast_trend(region='USA', trend='Exponential').reset_index(drop=True), None, None),
            ('DZ672:EA718', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'USA']], None, None),
            ]
    return verify


def verify_tam_data_eleven_sources(obj, verify):
    """Verified tables in TAM Data, with smaller source data area.

          Some solutions, first noticed with ImprovedCookStoves, have a smaller set of
          columns to hold data sources and this shifts all of the rest of the columns to
          the left. This test specifies the columns for this narrower layout.
    """
    func = functools.partial(obj.tm.forecast_trend, region='World')
    (d2_mask, d3_mask, exp_mask) = _get_interpolation_trend_masks(func=func)
    verify['TAM Data'] = [
            ('S46:U94', obj.tm.forecast_min_max_sd(region='World').reset_index(drop=True), None, None),
            ('W46:Y94', obj.tm.forecast_low_med_high(region='World').reset_index(drop=True), None, None),
            ('BT50:BV96', obj.tm.forecast_trend(region='World', trend='Linear').reset_index(drop=True), None, None),
            ('CA50:CD96', obj.tm.forecast_trend(region='World', trend='Degree2').reset_index(drop=True), d2_mask, None),
            ('CI50:CM96', obj.tm.forecast_trend(region='World', trend='Degree3').reset_index(drop=True), d3_mask, None),
            ('CR50:CT96', obj.tm.forecast_trend(region='World', trend='Exponential').reset_index(drop=True), exp_mask, None),
            # ('DV45:DW91', obj.tm.forecast_trend(region='World', ).reset_index().loc[:, ['Year', 'adoption']], None), first year differs
            # TODO Figure out PDS TAM handling
            ('S164:U212', obj.tm.forecast_min_max_sd(region='OECD90').reset_index(drop=True), None, None),
            ('W164:Y212', obj.tm.forecast_low_med_high(region='OECD90').reset_index(drop=True), None, None),
            ('BT168:BV214', obj.tm.forecast_trend(region='OECD90', trend='Linear').reset_index(drop=True), None, None),
            ('CA168:CD214', obj.tm.forecast_trend(region='OECD90', trend='Degree2').reset_index(drop=True), None, None),
            ('CI168:CM214', obj.tm.forecast_trend(region='OECD90', trend='Degree3').reset_index(drop=True), None, None),
            ('CR168:CT214', obj.tm.forecast_trend(region='OECD90', trend='Exponential').reset_index(drop=True), None, None),
            # ('DV163:DW209', obj.tm.forecast_trend(region='OECD90', ).reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S228:U276', obj.tm.forecast_min_max_sd(region='Eastern Europe').reset_index(drop=True), None, None),
            ('W228:Y276', obj.tm.forecast_low_med_high(region='Eastern Europe').reset_index(drop=True), None, None),
            ('BT232:BV278', obj.tm.forecast_trend(region='Eastern Europe', trend='Linear').reset_index(drop=True), None, None),
            ('CA232:CD278', obj.tm.forecast_trend(region='Eastern Europe', trend='Degree2').reset_index(drop=True), None, None),
            ('CI232:CM278', obj.tm.forecast_trend(region='Eastern Europe', trend='Degree3').reset_index(drop=True), None, None),
            ('CR232:CT278', obj.tm.forecast_trend(region='Eastern Europe', trend='Exponential').reset_index(drop=True), None, None),
            # ('DV227:DW273', obj.tm.forecast_trend(region='Eastern Europe', ).reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S291:U339', obj.tm.forecast_min_max_sd(region='Asia (Sans Japan)').reset_index(drop=True), None, None),
            ('W291:Y339', obj.tm.forecast_low_med_high(region='Asia (Sans Japan)').reset_index(drop=True), None, None),
            ('BT295:BV341', obj.tm.forecast_trend(region='Asia (Sans Japan)', trend='Linear').reset_index(drop=True), None, None),
            ('CA295:CD341', obj.tm.forecast_trend(region='Asia (Sans Japan)', trend='Degree2').reset_index(drop=True), None, None),
            ('CI295:CM341', obj.tm.forecast_trend(region='Asia (Sans Japan)', trend='Degree3').reset_index(drop=True), None, None),
            ('CR295:CT341', obj.tm.forecast_trend(region='Asia (Sans Japan)', trend='Exponential').reset_index(drop=True), None, None),
            # ('DV290:DW336', obj.tm.forecast_trend(region='Asia (Sans Japan)', ).reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S354:U402', obj.tm.forecast_min_max_sd(region='Middle East and Africa').reset_index(drop=True), None, None),
            ('W354:Y402', obj.tm.forecast_low_med_high(region='Middle East and Africa').reset_index(drop=True), None, None),
            ('BT358:BV404', obj.tm.forecast_trend(region='Middle East and Africa', trend='Linear').reset_index(drop=True), None, None),
            ('CA358:CD404', obj.tm.forecast_trend(region='Middle East and Africa', trend='Degree2').reset_index(drop=True), None, None),
            ('CI358:CM404', obj.tm.forecast_trend(region='Middle East and Africa', trend='Degree3').reset_index(drop=True), None, None),
            ('CR358:CT404', obj.tm.forecast_trend(region='Middle East and Africa', trend='Exponential').reset_index(drop=True), None, None),
            # ('DV353:DW399', obj.tm.forecast_trend(region='Middle East and Africa', ).reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S417:U465', obj.tm.forecast_min_max_sd(region='Latin America').reset_index(drop=True), None, None),
            ('W417:Y465', obj.tm.forecast_low_med_high(region='Latin America').reset_index(drop=True), None, None),
            ('BT421:BV467', obj.tm.forecast_trend(region='Latin America', trend='Linear').reset_index(drop=True), None, None),
            ('CA421:CD467', obj.tm.forecast_trend(region='Latin America', trend='Degree2').reset_index(drop=True), None, None),
            ('CI421:CM467', obj.tm.forecast_trend(region='Latin America', trend='Degree3').reset_index(drop=True), None, None),
            ('CR421:CT467', obj.tm.forecast_trend(region='Latin America', trend='Exponential').reset_index(drop=True), None, None),
            # ('DV416:DW465', obj.tm.forecast_trend(region='Latin America', ).reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S480:U528', obj.tm.forecast_min_max_sd(region='China').reset_index(drop=True), None, None),
            ('W480:Y528', obj.tm.forecast_low_med_high(region='China').reset_index(drop=True), None, None),
            ('BT484:BV530', obj.tm.forecast_trend(region='China', trend='Linear').reset_index(drop=True), None, None),
            ('CA484:CD530', obj.tm.forecast_trend(region='China', trend='Degree2').reset_index(drop=True), None, None),
            ('CI484:CM530', obj.tm.forecast_trend(region='China', trend='Degree3').reset_index(drop=True), None, None),
            ('CR484:CT530', obj.tm.forecast_trend(region='China', trend='Exponential').reset_index(drop=True), None, None),
            # ('DV479:DW525', obj.tm.forecast_trend(region='China', ).reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S544:U592', obj.tm.forecast_min_max_sd(region='India').reset_index(drop=True), None, None),
            ('W544:Y592', obj.tm.forecast_low_med_high(region='India').reset_index(drop=True), None, None),
            ('BT548:BV594', obj.tm.forecast_trend(region='India', trend='Linear').reset_index(drop=True), None, None),
            ('CA548:CD594', obj.tm.forecast_trend(region='India', trend='Degree2').reset_index(drop=True), None, None),
            ('CI548:CM594', obj.tm.forecast_trend(region='India', trend='Degree3').reset_index(drop=True), None, None),
            ('CR548:CT594', obj.tm.forecast_trend(region='India', trend='Exponential').reset_index(drop=True), None, None),
            # ('DV543:DW591', obj.tm.forecast_trend(region='India', ).reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S608:U656', obj.tm.forecast_min_max_sd(region='EU').reset_index(drop=True), None, None),
            ('W608:Y656', obj.tm.forecast_low_med_high(region='EU').reset_index(drop=True), None, None),
            ('BT612:BV658', obj.tm.forecast_trend(region='EU', trend='Linear').reset_index(drop=True), None, None),
            ('CA612:CD658', obj.tm.forecast_trend(region='EU', trend='Degree2').reset_index(drop=True), None, None),
            ('CI612:CM658', obj.tm.forecast_trend(region='EU', trend='Degree3').reset_index(drop=True), None, None),
            ('CR612:CT658', obj.tm.forecast_trend(region='EU', trend='Exponential').reset_index(drop=True), None, None),
            # ('DV607:DW653', obj.tm.forecast_trend(region='EU', ).reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S673:U721', obj.tm.forecast_min_max_sd(region='USA').reset_index(drop=True), None, None),
            ('W673:Y721', obj.tm.forecast_low_med_high(region='USA').reset_index(drop=True), None, None),
            ('BT677:BV723', obj.tm.forecast_trend(region='USA', trend='Linear').reset_index(drop=True), None, None),
            ('CA677:CD723', obj.tm.forecast_trend(region='USA', trend='Degree2').reset_index(drop=True), None, None),
            ('CI677:CM723', obj.tm.forecast_trend(region='USA', trend='Degree3').reset_index(drop=True), None, None),
            ('CR677:CT723', obj.tm.forecast_trend(region='USA', trend='Exponential').reset_index(drop=True), None, None),
            # ('DV672:DW718', obj.tm.forecast_trend(region='USA', ).reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ]
    return verify


def verify_adoption_data(obj, verify):
    """Verified tables in Adoption Data."""
    func = functools.partial(obj.ad.adoption_trend, region='World')
    (d2_mask, d3_mask, exp_mask) = _get_interpolation_trend_masks(func=func)
    verify['Adoption Data'] = [
            ('X46:Z94', obj.ad.adoption_min_max_sd(region='World').reset_index(drop=True), None, None),
            ('AB46:AD94', obj.ad.adoption_low_med_high(region='World').reset_index(drop=True), None, None),
            ('BY50:CA96', obj.ad.adoption_trend(region='World', trend='Linear').reset_index(drop=True), None, None),
            ('CF50:CI96', obj.ad.adoption_trend(region='World', trend='Degree2').reset_index(drop=True), d2_mask, None),
            ('CN50:CR96', obj.ad.adoption_trend(region='World', trend='Degree3').reset_index(drop=True), d3_mask, None),
            ('CW50:CY96', obj.ad.adoption_trend(region='World', trend='Exponential').reset_index(drop=True), exp_mask, None),
            #('EA45:EB91', obj.ad.adoption_trend(region='World').reset_index().loc[:, ['Year', 'adoption']], None),
            ('X106:Z154', obj.ad.adoption_min_max_sd(region='OECD90').reset_index(drop=True), None, None),
            ('AB106:AD154', obj.ad.adoption_low_med_high(region='OECD90').reset_index(drop=True), None, None),
            ('BY110:CA156', obj.ad.adoption_trend(region='OECD90', trend='Linear').reset_index(drop=True), None, None),
            ('CF110:CI156', obj.ad.adoption_trend(region='OECD90', trend='Degree2').reset_index(drop=True), None, None),
            ('CN110:CR156', obj.ad.adoption_trend(region='OECD90', trend='Degree3').reset_index(drop=True), None, None),
            ('CW110:CY156', obj.ad.adoption_trend(region='OECD90', trend='Exponential').reset_index(drop=True), None, None),
            #('EA105:EB151', obj.ad.adoption_trend(region='OECD90').reset_index().loc[:, ['Year', 'adoption']], None),
            ('X170:Z218', obj.ad.adoption_min_max_sd(region='Eastern Europe').reset_index(drop=True), None, None),
            ('AB170:AD218', obj.ad.adoption_low_med_high(region='Eastern Europe').reset_index(drop=True), None, None),
            ('BY174:CA220', obj.ad.adoption_trend(region='Eastern Europe', trend='Linear').reset_index(drop=True), None, None),
            ('CF174:CI220', obj.ad.adoption_trend(region='Eastern Europe', trend='Degree2').reset_index(drop=True), None, None),
            ('CN174:CR220', obj.ad.adoption_trend(region='Eastern Europe', trend='Degree3').reset_index(drop=True), None, None),
            ('CW174:CY220', obj.ad.adoption_trend(region='Eastern Europe', trend='Exponential').reset_index(drop=True), None, None),
            #('EA169:EB217', obj.ad.adoption_trend(region='Eastern Europe').reset_index().loc[:, ['Year', 'adoption']], None),
            ('X233:Z281', obj.ad.adoption_min_max_sd(region='Asia (Sans Japan)').reset_index(drop=True), None, None),
            ('AB233:AD281', obj.ad.adoption_low_med_high(region='Asia (Sans Japan)').reset_index(drop=True), None, None),
            ('BY237:CA283', obj.ad.adoption_trend(region='Asia (Sans Japan)', trend='Linear').reset_index(drop=True), None, None),
            ('CF237:CI283', obj.ad.adoption_trend(region='Asia (Sans Japan)', trend='Degree2').reset_index(drop=True), None, None),
            ('CN237:CR283', obj.ad.adoption_trend(region='Asia (Sans Japan)', trend='Degree3').reset_index(drop=True), None, None),
            ('CW237:CY283', obj.ad.adoption_trend(region='Asia (Sans Japan)', trend='Exponential').reset_index(drop=True), None, None),
            #('EA232:EB278', obj.ad.adoption_trend(region='Asia (Sans Japan)').reset_index().loc[:, ['Year', 'adoption']], None),
            ('X296:Z344', obj.ad.adoption_min_max_sd(region='Middle East and Africa').reset_index(drop=True), None, None),
            ('AB296:AD344', obj.ad.adoption_low_med_high(region='Middle East and Africa').reset_index(drop=True), None, None),
            ('BY300:CA346', obj.ad.adoption_trend(region='Middle East and Africa', trend='Linear').reset_index(drop=True), None, None),
            ('CF300:CI346', obj.ad.adoption_trend(region='Middle East and Africa', trend='Degree2').reset_index(drop=True), None, None),
            ('CN300:CR346', obj.ad.adoption_trend(region='Middle East and Africa', trend='Degree3').reset_index(drop=True), None, None),
            ('CW300:CY346', obj.ad.adoption_trend(region='Middle East and Africa', trend='Exponential').reset_index(drop=True), None, None),
            #('EA295:EB341', obj.ad.adoption_trend(region='Middle East and Africa').reset_index().loc[:, ['Year', 'adoption']], None),
            ('X359:Z407', obj.ad.adoption_min_max_sd(region='Latin America').reset_index(drop=True), None, None),
            ('AB359:AD407', obj.ad.adoption_low_med_high(region='Latin America').reset_index(drop=True), None, None),
            ('BY363:CA409', obj.ad.adoption_trend(region='Latin America', trend='Linear').reset_index(drop=True), None, None),
            ('CF363:CI409', obj.ad.adoption_trend(region='Latin America', trend='Degree2').reset_index(drop=True), None, None),
            ('CN363:CR409', obj.ad.adoption_trend(region='Latin America', trend='Degree3').reset_index(drop=True), None, None),
            ('CW363:CY409', obj.ad.adoption_trend(region='Latin America', trend='Exponential').reset_index(drop=True), None, None),
            #('EA358:EB404', obj.ad.adoption_trend(region='Latin America').reset_index().loc[:, ['Year', 'adoption']], None),
            ('X422:Z470', obj.ad.adoption_min_max_sd(region='China').reset_index(drop=True), None, None),
            ('AB422:AD470', obj.ad.adoption_low_med_high(region='China').reset_index(drop=True), None, None),
            ('BY426:CA472', obj.ad.adoption_trend(region='China', trend='Linear').reset_index(drop=True), None, None),
            ('CF426:CI472', obj.ad.adoption_trend(region='China', trend='Degree2').reset_index(drop=True), None, None),
            ('CN426:CR472', obj.ad.adoption_trend(region='China', trend='Degree3').reset_index(drop=True), None, None),
            ('CW426:CY472', obj.ad.adoption_trend(region='China', trend='Exponential').reset_index(drop=True), None, None),
            #('EA421:EB467', obj.ad.adoption_trend(region='China').reset_index().loc[:, ['Year', 'adoption']], None),
            ('X486:Z534', obj.ad.adoption_min_max_sd(region='India').reset_index(drop=True), None, None),
            ('AB486:AD534', obj.ad.adoption_low_med_high(region='India').reset_index(drop=True), None, None),
            ('BY490:CA536', obj.ad.adoption_trend(region='India', trend='Linear').reset_index(drop=True), None, None),
            ('CF490:CI536', obj.ad.adoption_trend(region='India', trend='Degree2').reset_index(drop=True), None, None),
            ('CN490:CR536', obj.ad.adoption_trend(region='India', trend='Degree3').reset_index(drop=True), None, None),
            ('CW490:CY536', obj.ad.adoption_trend(region='India', trend='Exponential').reset_index(drop=True), None, None),
            #('EA485:EB531', obj.ad.adoption_trend(region='India').reset_index().loc[:, ['Year', 'adoption']], None),
            ('X550:Z598', obj.ad.adoption_min_max_sd(region='EU').reset_index(drop=True), None, None),
            ('AB550:AD598', obj.ad.adoption_low_med_high(region='EU').reset_index(drop=True), None, None),
            ('BY554:CA600', obj.ad.adoption_trend(region='EU', trend='Linear').reset_index(drop=True), None, None),
            ('CF554:CI600', obj.ad.adoption_trend(region='EU', trend='Degree2').reset_index(drop=True), None, None),
            ('CN554:CR600', obj.ad.adoption_trend(region='EU', trend='Degree3').reset_index(drop=True), None, None),
            ('CW554:CY600', obj.ad.adoption_trend(region='EU', trend='Exponential').reset_index(drop=True), None, None),
            #('EA549:EB595', obj.ad.adoption_trend(region='EU').reset_index().loc[:, ['Year', 'adoption']], None),
            ('X615:Z663', obj.ad.adoption_min_max_sd(region='USA').reset_index(drop=True), None, None),
            ('AB615:AD663', obj.ad.adoption_low_med_high(region='USA').reset_index(drop=True), None, None),
            ('BY619:CA665', obj.ad.adoption_trend(region='USA', trend='Linear').reset_index(drop=True), None, None),
            ('CF619:CI665', obj.ad.adoption_trend(region='USA', trend='Degree2').reset_index(drop=True), None, None),
            ('CN619:CR665', obj.ad.adoption_trend(region='USA', trend='Degree3').reset_index(drop=True), None, None),
            ('CW619:CY665', obj.ad.adoption_trend(region='USA', trend='Exponential').reset_index(drop=True), None, None),
            #('EA614:EB660', obj.ad.adoption_trend(region='USA').reset_index().loc[:, ['Year', 'adoption']], None, None),
            ]
    return verify


def verify_custom_adoption(obj, verify):
    """Verified tables in Custom * Adoption.
       Note: regional data is ignored as there are issues in the xls sheet that have
       not been replicated. See documentation of issues here:
       https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.kjrqk1o5e46m
    """
    verify['Custom PDS Adoption'] = [
            ('A23:B71', obj.pds_ca.adoption_data_per_region()['World'].reset_index(), None, "Excel_NaN")
    ]
    # verify['Custom REF Adoption'] = []  # not yet implemented
    return verify


def verify_adoption_data_eleven_sources(obj, verify):
    """Verified tables in Adoption Data.

          Some solutions, first noticed with ImprovedCookStoves, have a smaller set of
          columns to hold data sources and this shifts all of the rest of the columns to
          the left. This test specifies the columns for this narrower layout.
    """
    func = functools.partial(obj.ad.adoption_trend, region='World')
    (d2_mask, d3_mask, exp_mask) = _get_interpolation_trend_masks(func=func)
    verify['Adoption Data'] = [
            ('S46:U94', obj.ad.adoption_min_max_sd(region='World').reset_index(drop=True), None, None),
            ('W46:Y94', obj.ad.adoption_low_med_high(region='World').reset_index(drop=True), None, None),
            ('BT50:BV96', obj.ad.adoption_trend(region='World', trend='Linear').reset_index(drop=True), None, None),
            ('CA50:CD96', obj.ad.adoption_trend(region='World', trend='Degree2').reset_index(drop=True), d2_mask, None),
            ('CI50:CM96', obj.ad.adoption_trend(region='World', trend='Degree3').reset_index(drop=True), d3_mask, None),
            ('CR50:CT96', obj.ad.adoption_trend(region='World', trend='Exponential').reset_index(drop=True), exp_mask, None),
            #('DV45:DW91', obj.ad.adoption_trend(region='World').reset_index().loc[:, ['Year', 'adoption']], None),
            ('S106:U154', obj.ad.adoption_min_max_sd(region='OECD90').reset_index(drop=True), None, None),
            ('W106:Y154', obj.ad.adoption_low_med_high(region='OECD90').reset_index(drop=True), None, None),
            ('BT110:BV156', obj.ad.adoption_trend(region='OECD90', trend='Linear').reset_index(drop=True), None, None),
            ('CA110:CD156', obj.ad.adoption_trend(region='OECD90', trend='Degree2').reset_index(drop=True), None, None),
            ('CI110:CM156', obj.ad.adoption_trend(region='OECD90', trend='Degree3').reset_index(drop=True), None, None),
            ('CR110:CT156', obj.ad.adoption_trend(region='OECD90', trend='Exponential').reset_index(drop=True), None, None),
            #('EA105:EB151', obj.ad.adoption_trend(region='OECD90').reset_index().loc[:, ['Year', 'adoption']], None),
            ('S170:U218', obj.ad.adoption_min_max_sd(region='Eastern Europe').reset_index(drop=True), None, None),
            ('W170:Y218', obj.ad.adoption_low_med_high(region='Eastern Europe').reset_index(drop=True), None, None),
            ('BT174:BV220', obj.ad.adoption_trend(region='Eastern Europe', trend='Linear').reset_index(drop=True), None, None),
            ('CA174:CD220', obj.ad.adoption_trend(region='Eastern Europe', trend='Degree2').reset_index(drop=True), None, None),
            ('CI174:CM220', obj.ad.adoption_trend(region='Eastern Europe', trend='Degree3').reset_index(drop=True), None, None),
            ('CR174:CT220', obj.ad.adoption_trend(region='Eastern Europe', trend='Exponential').reset_index(drop=True), None, None),
            #('EA169:EB217', obj.ad.adoption_trend(region='Eastern Europe').reset_index().loc[:, ['Year', 'adoption']], None),
            ('S233:U281', obj.ad.adoption_min_max_sd(region='Asia (Sans Japan)').reset_index(drop=True), None, None),
            ('W233:Y281', obj.ad.adoption_low_med_high(region='Asia (Sans Japan)').reset_index(drop=True), None, None),
            ('BT237:BV283', obj.ad.adoption_trend(region='Asia (Sans Japan)', trend='Linear').reset_index(drop=True), None, None),
            ('CA237:CD283', obj.ad.adoption_trend(region='Asia (Sans Japan)', trend='Degree2').reset_index(drop=True), None, None),
            ('CI237:CM283', obj.ad.adoption_trend(region='Asia (Sans Japan)', trend='Degree3').reset_index(drop=True), None, None),
            ('CR237:CT283', obj.ad.adoption_trend(region='Asia (Sans Japan)', trend='Exponential').reset_index(drop=True), None, None),
            #('EA232:EB278', obj.ad.adoption_trend(region='Asia (Sans Japan)').reset_index().loc[:, ['Year', 'adoption']], None),
            ('S296:U344', obj.ad.adoption_min_max_sd(region='Middle East and Africa').reset_index(drop=True), None, None),
            ('W296:Y344', obj.ad.adoption_low_med_high(region='Middle East and Africa').reset_index(drop=True), None, None),
            ('BT300:BV346', obj.ad.adoption_trend(region='Middle East and Africa', trend='Linear').reset_index(drop=True), None, None),
            ('CA300:CD346', obj.ad.adoption_trend(region='Middle East and Africa', trend='Degree2').reset_index(drop=True), None, None),
            ('CI300:CM346', obj.ad.adoption_trend(region='Middle East and Africa', trend='Degree3').reset_index(drop=True), None, None),
            ('CR300:CT346', obj.ad.adoption_trend(region='Middle East and Africa', trend='Exponential').reset_index(drop=True), None, None),
            #('EA295:EB341', obj.ad.adoption_trend(region='Middle East and Africa').reset_index().loc[:, ['Year', 'adoption']], None),
            ('S359:U407', obj.ad.adoption_min_max_sd(region='Latin America').reset_index(drop=True), None, None),
            ('W359:Y407', obj.ad.adoption_low_med_high(region='Latin America').reset_index(drop=True), None, None),
            ('BT363:BV409', obj.ad.adoption_trend(region='Latin America', trend='Linear').reset_index(drop=True), None, None),
            ('CA363:CD409', obj.ad.adoption_trend(region='Latin America', trend='Degree2').reset_index(drop=True), None, None),
            ('CI363:CM409', obj.ad.adoption_trend(region='Latin America', trend='Degree3').reset_index(drop=True), None, None),
            ('CR363:CT409', obj.ad.adoption_trend(region='Latin America', trend='Exponential').reset_index(drop=True), None, None),
            #('EA358:EB404', obj.ad.adoption_trend(region='Latin America').reset_index().loc[:, ['Year', 'adoption']], None),
            ('S422:U470', obj.ad.adoption_min_max_sd(region='China').reset_index(drop=True), None, None),
            ('W422:Y470', obj.ad.adoption_low_med_high(region='China').reset_index(drop=True), None, None),
            ('BT426:BV472', obj.ad.adoption_trend(region='China', trend='Linear').reset_index(drop=True), None, None),
            ('CA426:CD472', obj.ad.adoption_trend(region='China', trend='Degree2').reset_index(drop=True), None, None),
            ('CI426:CM472', obj.ad.adoption_trend(region='China', trend='Degree3').reset_index(drop=True), None, None),
            ('CR426:CT472', obj.ad.adoption_trend(region='China', trend='Exponential').reset_index(drop=True), None, None),
            #('EA421:EB467', obj.ad.adoption_trend(region='China').reset_index().loc[:, ['Year', 'adoption']], None),
            ('S486:U534', obj.ad.adoption_min_max_sd(region='India').reset_index(drop=True), None, None),
            ('W486:Y534', obj.ad.adoption_low_med_high(region='India').reset_index(drop=True), None, None),
            ('BT490:BV536', obj.ad.adoption_trend(region='India', trend='Linear').reset_index(drop=True), None, None),
            ('CA490:CD536', obj.ad.adoption_trend(region='India', trend='Degree2').reset_index(drop=True), None, None),
            ('CI490:CM536', obj.ad.adoption_trend(region='India', trend='Degree3').reset_index(drop=True), None, None),
            ('CR490:CT536', obj.ad.adoption_trend(region='India', trend='Exponential').reset_index(drop=True), None, None),
            #('EA485:EB531', obj.ad.adoption_trend(region='India').reset_index().loc[:, ['Year', 'adoption']], None),
            ('S550:U598', obj.ad.adoption_min_max_sd(region='EU').reset_index(drop=True), None, None),
            ('W550:Y598', obj.ad.adoption_low_med_high(region='EU').reset_index(drop=True), None, None),
            ('BT554:BV600', obj.ad.adoption_trend(region='EU', trend='Linear').reset_index(drop=True), None, None),
            ('CA554:CD600', obj.ad.adoption_trend(region='EU', trend='Degree2').reset_index(drop=True), None, None),
            ('CI554:CM600', obj.ad.adoption_trend(region='EU', trend='Degree3').reset_index(drop=True), None, None),
            ('CR554:CT600', obj.ad.adoption_trend(region='EU', trend='Exponential').reset_index(drop=True), None, None),
            #('EA549:EB595', obj.ad.adoption_trend(region='EU').reset_index().loc[:, ['Year', 'adoption']], None),
            ('S615:U663', obj.ad.adoption_min_max_sd(region='USA').reset_index(drop=True), None, None),
            ('W615:Y663', obj.ad.adoption_low_med_high(region='USA').reset_index(drop=True), None, None),
            ('BT619:BV665', obj.ad.adoption_trend(region='USA', trend='Linear').reset_index(drop=True), None, None),
            ('CA619:CD665', obj.ad.adoption_trend(region='USA', trend='Degree2').reset_index(drop=True), None, None),
            ('CI619:CM665', obj.ad.adoption_trend(region='USA', trend='Degree3').reset_index(drop=True), None, None),
            ('CR619:CT665', obj.ad.adoption_trend(region='USA', trend='Exponential').reset_index(drop=True), None, None),
            #('EA614:EB660', obj.ad.adoption_trend(region='USA').reset_index().loc[:, ['Year', 'adoption']], None),
            ]
    return verify


def verify_logistic_s_curve(obj, verify):
    """Verified tables in S-Curve Adoption."""
    verify['S-Curve Adoption'] = [
            ('A24:K70', obj.sc.logistic_adoption().reset_index(), None, None),
            ]
    return verify


def verify_bass_diffusion_s_curve(obj, verify):
    """Verified tables in S-Curve Adoption."""
    verify['S-Curve Adoption'] = [
            ('A130:K176', obj.sc.bass_diffusion_adoption().reset_index(), None, None),
            ]
    return verify


def verify_unit_adoption_calculations(obj, verify, include_regional_data=True, soln_type='RRS'):
    """Verified tables in Unit Adoption Calculations."""
    if hasattr(obj, 'tm'):
        ref_tam_mask = obj.tm.ref_tam_per_region().reset_index().isna()
        verify['Unit Adoption Calculations'] = [
                ('A17:K63', obj.tm.ref_tam_per_region().reset_index(), None, None),
                ('A69:K115', obj.tm.pds_tam_per_region().reset_index(), None, None)]
    else:
        ref_tam_mask = None
        verify['Unit Adoption Calculations'] = []

    if not include_regional_data or is_custom_ad_with_no_regional_data(obj):
        regional_mask = obj.ua.soln_pds_cumulative_funits().reset_index()
        regional_mask.loc[:, :] = True
        regional_mask.loc[:, ['Year', 'World']] = False
    else:
        regional_mask = None

    if ref_tam_mask is not None and regional_mask is not None:
        regional_mask |= ref_tam_mask

    # BikeInfra-RRSv1.1c-7Oct2019.xlsm catastrophic subtraction in one scenario,
    # Carpool-RRSv1.1b-Jan2020.xlsm also catastrophic cancellation in multiple scenarios.
    baseline = obj.ua.soln_net_annual_funits_adopted().mean() * 1e-6
    s = obj.ua.soln_net_annual_funits_adopted().reset_index()
    m = s.mask(s < baseline, other=True).where(s < baseline, other=False)
    soln_net_annual_funits_adopted_mask = (m | regional_mask) if regional_mask is not None else m

    verify['Unit Adoption Calculations'].extend([
            ('P17:Z63', obj.ua.ref_population().reset_index(), None, None),
            ('AB17:AL63', obj.ua.ref_gdp().reset_index(), None, None),
            ('AN17:AX63', obj.ua.ref_gdp_per_capita().reset_index(), None, None),
            ('P69:Z115', obj.ua.pds_population().reset_index(), None, None),
            ('AB69:AL115', obj.ua.pds_gdp().reset_index(), None, None),
            ('AN69:AX115', obj.ua.pds_gdp_per_capita().reset_index(), None, None),
            ('AG199:AQ244', obj.ua.soln_ref_new_iunits_reqd().reset_index(), None, None),
            ('B252:L298', obj.ua.soln_net_annual_funits_adopted().reset_index(), soln_net_annual_funits_adopted_mask, None),
            ('Q252:AA298', obj.ua.conv_ref_tot_iunits().reset_index(), ref_tam_mask, None),
    ])

    if soln_type == 'RRS':
        # Some solutions, notably HighSpeedRail, have regional results which drop to near zero
        # for a year and then bounce back. The ~0 results are the result of catastrophic
        # subtraction with only a few bits of precision, not close enough for pytest.approx.
        # Just mask those cells off.
        s = obj.ua.soln_ref_cumulative_funits().reset_index()
        soln_ref_cumulative_funits_mask = s.mask(s < 1e-11, other=True).where(s < 1e-11, other=False)

        baseline = obj.ua.soln_pds_cumulative_funits().mean() * 1e-6
        s = obj.ua.soln_pds_cumulative_funits().reset_index()
        m = s.mask(s < baseline, other=True).where(s < baseline, other=False)
        soln_pds_cumulative_funits_mask = m | regional_mask if regional_mask is not None else m

        # Carpool-RRSv1.1b-Jan2020.xlsm catastrophic cancellation in multiple scenarios.
        baseline = obj.ua.conv_ref_annual_tot_iunits().mean() * 1e-6
        s = obj.ua.conv_ref_annual_tot_iunits().reset_index()
        m = s.mask(s < baseline, other=True).where(s < baseline, other=False)
        conv_ref_annual_tot_iunits_mask = (m | regional_mask) if regional_mask is not None else m
        baseline = obj.ua.soln_pds_fuel_units_avoided().mean() * 1e-6
        s = obj.ua.soln_pds_fuel_units_avoided().reset_index()
        m = s.mask(s < baseline, other=True).where(s < baseline, other=False)
        soln_pds_fuel_units_avoided_mask = (m | regional_mask) if regional_mask is not None else m

        # Alternative Cement
        baseline = obj.ua.conv_ref_new_iunits().mean() * 1e-6
        s = obj.ua.conv_ref_new_iunits().reset_index()
        m = s.mask(s < baseline, other=True).where(s < baseline, other=False)
        conv_ref_new_iunits_mask = (m | regional_mask) if regional_mask is not None else m
        baseline = obj.ua.soln_pds_direct_co2_emissions_saved().mean() * 1e-6
        s = obj.ua.soln_pds_direct_co2_emissions_saved().reset_index()
        m = s.mask(s < baseline, other=True).where(s < baseline, other=False)
        soln_pds_direct_co2_emissions_saved_mask = (m | regional_mask) if regional_mask is not None else m

        verify['Unit Adoption Calculations'].extend([
                ('BA17:BK63', obj.ua.ref_tam_per_capita().reset_index(), None, None),
                ('BM17:BW63', obj.ua.ref_tam_per_gdp_per_capita().reset_index(), None, None),
                ('BY17:CI63', obj.ua.ref_tam_growth().reset_index(), None, None),
                ('BA69:BK115', obj.ua.pds_tam_per_capita().reset_index(), None, None),
                ('BM69:BW115', obj.ua.pds_tam_per_gdp_per_capita().reset_index(), None, None),
                ('BY69:CI115', obj.ua.pds_tam_growth().reset_index(), None, None),
                # ('B135:L181' tested in 'Helper Tables'!C91)
                ('Q135:AA181', obj.ua.soln_pds_cumulative_funits().reset_index(), soln_pds_cumulative_funits_mask, "Excel_NaN"),
                ('AX136:BH182', obj.ua.soln_pds_tot_iunits_reqd().reset_index(), regional_mask, None),
                ('AG137:AQ182', obj.ua.soln_pds_new_iunits_reqd().reset_index(), regional_mask, None),
                # ('BN136:BS182', obj.ua.soln_pds_big4_iunits_reqd().reset_index(), None, None),
                # ('B198:L244' tested in 'Helper Tables'!C27)
                ('Q198:AA244', obj.ua.soln_ref_cumulative_funits().reset_index(), soln_ref_cumulative_funits_mask, None),
                ('AX198:BH244', obj.ua.soln_ref_tot_iunits_reqd().reset_index(), None, None),
                ('AG253:AQ298', obj.ua.conv_ref_new_iunits().reset_index(), conv_ref_new_iunits_mask, None),
                ('AX252:BH298', obj.ua.conv_ref_annual_tot_iunits().reset_index(), conv_ref_annual_tot_iunits_mask, None),
                ('B308:L354', obj.ua.soln_pds_net_grid_electricity_units_saved().reset_index(), regional_mask, None),
                ('Q308:AA354', obj.ua.soln_pds_net_grid_electricity_units_used().reset_index(), regional_mask, None),
                ('AD308:AN354', obj.ua.soln_pds_fuel_units_avoided().reset_index(), soln_pds_fuel_units_avoided_mask, None),
                ('AT308:BD354', obj.ua.soln_pds_direct_co2_emissions_saved().reset_index(), soln_pds_direct_co2_emissions_saved_mask, None),
                ('BF308:BP354', obj.ua.soln_pds_direct_ch4_co2_emissions_saved().reset_index(), regional_mask, None),
                ('BR308:CB354', obj.ua.soln_pds_direct_n2o_co2_emissions_saved().reset_index(), regional_mask, None),
                ])
    elif soln_type == 'LAND_PROTECT':
        verify['Unit Adoption Calculations'].extend([
                ('CG136:CH182', obj.ua.pds_cumulative_degraded_land_unprotected().loc[:, 'World'].reset_index(), None, None),
                # ('CZ136:DA182', Not implemented
                ('DR136:DS182', obj.ua.pds_total_undegraded_land().loc[:, 'World'].reset_index(), None, None),
                ('EI136:EJ182', obj.ua.pds_cumulative_degraded_land_protected().loc[:, 'World'].reset_index(), None, None),
                ('CG198:CH244', obj.ua.ref_cumulative_degraded_land_unprotected().loc[:, 'World'].reset_index(), None, None),
                # ('CZ198:DA244', Not implemented
                ('DR198:DS244', obj.ua.ref_total_undegraded_land().loc[:, 'World'].reset_index(), None, None),
                ('EI198:EJ244', obj.ua.ref_cumulative_degraded_land_protected().loc[:, 'World'].reset_index(), None, None),
                ('B252:C298', obj.ua.net_annual_land_units_adopted().loc[:, 'World'].reset_index(), None, None),
                ('Q252:R298', obj.ua.conv_ref_tot_iunits().loc[:, 'World'].reset_index(), None, None),
                ('AG253:AH298', obj.ua.conv_ref_new_iunits().loc[:, 'World'].reset_index(), None, None),
                # ('BO252:BP298', Not implemented
                ('CG252:CH298', obj.ua.annual_reduction_in_total_degraded_land().loc[:, 'World'].reset_index(), None, None),
                # ('CZ252:DA298', Not implemented
                ('DR252:DS298', obj.ua.cumulative_reduction_in_total_degraded_land().loc[:, 'World'].reset_index(), None, None),
                ('EI252:EJ298', obj.ua.net_land_units_after_emissions_lifetime().loc[:, 'World'].reset_index(), None, None),
                ('B308:C354', obj.ua.soln_pds_net_grid_electricity_units_saved().loc[:, 'World'].reset_index(), regional_mask, None),
                ('Q308:R354', obj.ua.soln_pds_net_grid_electricity_units_used().loc[:, 'World'].reset_index(), regional_mask, None),
                ('AD308:AE354', obj.ua.soln_pds_fuel_units_avoided().loc[:, 'World'].reset_index(), regional_mask, None),
                ('AT308:AU354', obj.ua.direct_co2eq_emissions_saved_land().loc[:, 'World'].reset_index(), None, None),
                ('BF308:BG354', obj.ua.direct_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None, None),
                ('BR308:BS354', obj.ua.direct_n2o_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None, None),
                ('CD308:CE354', obj.ua.direct_ch4_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None, None),
                ])
    elif soln_type == 'LAND_BIOSEQ':
        verify['Unit Adoption Calculations'].extend([
                ('EH137:EI182', obj.ua.soln_pds_annual_land_area_harvested().loc[:, 'World'].reset_index(), None, None),
                ('EI253:EJ298', obj.ua.net_land_units_after_emissions_lifetime().loc[2015:, 'World'].reset_index(), None, None),
                ('B308:C354', obj.ua.soln_pds_net_grid_electricity_units_saved().loc[:, 'World'].reset_index(), regional_mask, None),
                ('Q308:R354', obj.ua.soln_pds_net_grid_electricity_units_used().loc[:, 'World'].reset_index(), regional_mask, None),
                ('AD308:AE354', obj.ua.soln_pds_fuel_units_avoided().loc[:, 'World'].reset_index(), regional_mask, None),
                ('AT308:AU354', obj.ua.direct_co2eq_emissions_saved_land().loc[:, 'World'].reset_index(), None, None),
                ('BF308:BG354', obj.ua.direct_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None, None),
                ('BR308:BS354', obj.ua.direct_n2o_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None, None),
                ('CD308:CE354', obj.ua.direct_ch4_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None, None),
                ])
    return verify


def verify_helper_tables(obj, verify, include_regional_data=True):
    """Verified tables in Helper Tables."""
    verify['Helper Tables'] = []
    if include_regional_data:
        verify['Helper Tables'].append(
                ('B91:L137', obj.ht.soln_pds_funits_adopted().reset_index(), None, None))
    else:
        verify['Helper Tables'].append(
                ('B91:C137', obj.ht.soln_pds_funits_adopted().loc[:, 'World'].reset_index(), None, None))
    verify['Helper Tables'].append(
            ('B27:L73', obj.ht.soln_ref_funits_adopted().reset_index(), None, None))

    return verify


def verify_emissions_factors(obj, verify):
    """Verified tables in Emissions Factors."""
    verify['Emissions Factors'] = [
            ('A12:K57', obj.ef.conv_ref_grid_CO2eq_per_KWh().reset_index(), None, None),
            ('A67:K112', obj.ef.conv_ref_grid_CO2_per_KWh().reset_index(), None, None),
            ]
    return verify


def verify_first_cost(obj, verify):
    """Verified tables in First Cost."""
    verify['First Cost'] = [
            ('C37:C82', obj.fc.soln_pds_install_cost_per_iunit().loc[2015:].to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            # ('D37:D82', checked by 'Unit Adoption Calculations'!AH137
            ('E37:E82', obj.fc.soln_pds_annual_world_first_cost().loc[2015:].to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('F37:F82', obj.fc.soln_pds_cumulative_install().loc[2015:].to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('L37:L82', obj.fc.soln_ref_install_cost_per_iunit().loc[2015:].to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            # ('M37:M82', checked by 'Unit Adoption Calculations'!AH199
            ('N37:N82', obj.fc.soln_ref_annual_world_first_cost().loc[2015:].to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('O37:O82', obj.fc.conv_ref_install_cost_per_iunit().loc[2015:].to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            # ('P37:P82', checked by 'Unit Adoption Calculations'!AH253
            ('Q37:Q82', obj.fc.conv_ref_annual_world_first_cost().loc[2015:].to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('R37:R82', obj.fc.ref_cumulative_install().loc[2015:].to_frame().reset_index(drop=True), None, "Excel_one_cent")
            ]
    return verify


def verify_operating_cost(obj, verify):
    """Verified tables in Operating Cost."""
    # This has been a pain point: the last year of each column in the annual_breakout has a tiny
    # remaining_lifetime which is the result of catastrophic substraction between the previous
    # values and therefore has only a few bits of precision. pytest.approx() checks for 6 digits,
    # and there aren't enough bits to even meet that requirement.
    #
    # We mask off all cells where the value is less than one cent. We assert that being off by
    # a penny at the end of the equipment lifetime is acceptable.
    s = obj.oc.soln_pds_annual_breakout().reset_index().abs()
    soln_breakout_mask = s.mask(s < 0.01, other=True).where(s < 0.01, other=False)
    s = obj.oc.conv_ref_annual_breakout().reset_index().abs()
    conv_breakout_mask = s.mask(s < 0.01, other=True).where(s < 0.01, other=False)

    baseline = obj.oc.soln_pds_new_funits_per_year().loc[2015:, 'World'].mean() * 1e-6
    s = obj.oc.soln_pds_new_funits_per_year().loc[2015:, ['World']].reset_index(drop=True)
    soln_pds_new_funits_per_year_mask = s.mask(s < baseline, other=True).where(s < baseline, other=False)

    verify['Operating Cost'] = [
            ('B262:AV386', obj.oc.soln_pds_annual_breakout().reset_index(), soln_breakout_mask, None),
            ('B399:AV523', obj.oc.conv_ref_annual_breakout().reset_index(), conv_breakout_mask, None),
            # ('B19:B64', Not implemented, model never uses it.
            # ('C19:C64', checked by 'Unit Adoption Calculations'!C253
            ('D19:D64', obj.oc.soln_pds_annual_operating_cost().loc[2015:2060].to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('E19:E64', obj.oc.soln_pds_cumulative_operating_cost().loc[2015:2060].to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('F19:F64', obj.oc.soln_pds_new_funits_per_year().loc[2015:, ['World']].reset_index(drop=True), soln_pds_new_funits_per_year_mask, None),
            # ('I19:I64', Not implemented, model never uses it.
            # ('J19:J64', checked by 'Unit Adoption Calculations'!C253
            ('K19:K64', obj.oc.conv_ref_annual_operating_cost().to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('L19:L64', obj.oc.conv_ref_cumulative_operating_cost().to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            # ('B69:B114', equal to D19:D64,
            # ('C69:C114', equal to K19:K64,
            ('D69:D114', obj.oc.marginal_annual_operating_cost().to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('B126:B250', obj.oc.soln_marginal_first_cost().to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('C126:C250', obj.oc.soln_marginal_operating_cost_savings().to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('D126:D250', obj.oc.soln_net_cash_flow().to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('E126:E250', obj.oc.soln_net_present_value().to_frame().reset_index(drop=True), None, "Excel_one_cent"),
            ('I126:I250', obj.oc.soln_vs_conv_single_iunit_cashflow().to_frame().reset_index(drop=True), None, None),
            ('J126:J250', obj.oc.soln_vs_conv_single_iunit_npv().to_frame().reset_index(drop=True), None, None),
            #('K126:K250', obj.oc.soln_vs_conv_single_iunit_payback().to_frame().reset_index(drop=True), None, None),
            #('L126:L250', obj.oc.soln_vs_conv_single_iunit_payback_discounted().to_frame().reset_index(drop=True), None, None),
            ('M126:M250', obj.oc.soln_only_single_iunit_cashflow().to_frame().reset_index(drop=True), None, None),
            ('N126:N250', obj.oc.soln_only_single_iunit_npv().to_frame().reset_index(drop=True), None, None),
            #('O126:O250', obj.oc.soln_only_single_iunit_payback().to_frame().reset_index(drop=True), None, None),
            #('P126:P250', obj.oc.soln_only_single_iunit_payback_discounted().to_frame().reset_index(drop=True), None, None),
            ]
    return verify


def verify_co2_calcs(obj, verify, shifted=False, include_regional_data=True,
        is_rrs=True, cohort=2018):
    """Verified tables in CO2 Calcs."""
    if include_regional_data == False:
        regional_mask = obj.c2.co2_mmt_reduced().loc[2015:].reset_index()
        regional_mask.loc[:, :] = True
        regional_mask.loc[:, ['Year', 'World']] = False
    else:
        regional_mask = None

    # similar to operating cost, some co2 calcs values are very slightly offset from zero due to
    # floating point errors. We mask the problematic tables when they are close to 0.
    s = obj.c2.co2eq_mmt_reduced().reset_index().abs()
    near_zero_mask = s.mask(s < 0.01, other=True).where(s < 0.01, other=False)
    if regional_mask is not None:
        near_zero_mask = near_zero_mask | regional_mask

    # Alternative Cement
    baseline = obj.c2.co2eq_direct_reduced_emissions().loc[2015:].mean() * 1e-6
    s = obj.c2.co2eq_direct_reduced_emissions().loc[2015:].reset_index()
    mask = s.mask(s < baseline, other=True).where(s < baseline, other=False)
    if regional_mask is not None:
        mask = mask | regional_mask
    co2eq_direct_reduced_emissions_mask = mask
    baseline = obj.c2.co2eq_reduced_fuel_emissions().loc[2015:].mean() * 1e-6
    s = obj.c2.co2eq_reduced_fuel_emissions().loc[2015:].reset_index()
    mask = s.mask(s < baseline, other=True).where(s < baseline, other=False)
    if regional_mask is not None:
        mask = mask | regional_mask
    co2eq_reduced_fuel_emissions_mask = mask


    if is_rrs:
        verify['CO2 Calcs'] = [
                ('A235:K280', obj.c2.co2_reduced_grid_emissions().loc[2015:].reset_index(), regional_mask, None),
                ('R235:AB280', obj.c2.co2_replaced_grid_emissions().loc[2015:].reset_index(), regional_mask, None),
                ('AI235:AS280', obj.c2.co2_increased_grid_usage_emissions().loc[2015:].reset_index(), regional_mask, None),
                ('A289:K334', obj.c2.co2eq_reduced_grid_emissions().loc[2015:].reset_index(), regional_mask, None),
                ('R289:AB334', obj.c2.co2eq_replaced_grid_emissions().loc[2015:].reset_index(), regional_mask, None),
                ('AI289:AS334', obj.c2.co2eq_increased_grid_usage_emissions().loc[2015:].reset_index(), regional_mask, None),
                ('A345:K390', obj.c2.co2eq_direct_reduced_emissions().loc[2015:].reset_index(), co2eq_direct_reduced_emissions_mask, None),
                ]

        if shifted:
            # Some spreadsheets have the last two blocks shifted by several cells
            verify['CO2 Calcs'].extend([
                    ('R345:AB390', obj.c2.co2eq_reduced_fuel_emissions().loc[2015:].reset_index(), co2eq_reduced_fuel_emissions_mask, None),
                    ('AM345:AW390', obj.c2.co2eq_net_indirect_emissions().loc[2015:].reset_index(), regional_mask, None)
                    ])
        else:
            verify['CO2 Calcs'].extend([
                    ('U345:AE390', obj.c2.co2eq_reduced_fuel_emissions().loc[2015:].reset_index(), co2eq_reduced_fuel_emissions_mask, None),
                    ('AP345:AZ390', obj.c2.co2eq_net_indirect_emissions().loc[2015:].reset_index(), regional_mask, None)
                    ])

        verify['CO2 Calcs'].extend([
                ('A10:K55', obj.c2.co2_mmt_reduced().loc[2015:].reset_index(), regional_mask, None),
                ('A120:AW165', obj.c2.co2_ppm_calculator().loc[2015:].reset_index(), None, None),
                ('A65:K110', obj.c2.co2eq_mmt_reduced().loc[2015:].reset_index(), regional_mask, None),
                ('A172:F217', obj.c2.co2eq_ppm_calculator().loc[2015:].reset_index(), None, None),
                ])

    else:
        s = obj.c2.co2_ppm_calculator().loc[2015:].reset_index().abs()
        ppm_near_zero_mask = s.mask(s < 1e-8, other=True).where(s < 1e-8, other=False)
        s = obj.c2.co2_sequestered_global().loc[2015:].reset_index().abs()
        seq_near_zero_mask = s.mask(s < 1e-8, other=True).where(s < 1e-8, other=False)

        co2_sequestered_global = obj.c2.co2_sequestered_global().copy().reset_index()
        co2_sequestered_global.drop(columns=['Global Arctic'], inplace=True)
        if cohort >= 2020:
            # 8 Thermal-Moisture Regimes in model, but Excel CO2 Calcs did not update from 6 TMRs.
            co2_sequestered_global['Temperate/Boreal-Humid'] = (
                    co2_sequestered_global['Temperate-Humid'] +
                    co2_sequestered_global['Boreal-Humid'])
            co2_sequestered_global.drop(columns=['Temperate-Humid', 'Boreal-Humid'], inplace=True)
            co2_sequestered_global['Temperate/Boreal-Semi-Arid'] = (
                    co2_sequestered_global['Temperate-Semi-Arid'] +
                    co2_sequestered_global['Boreal-Semi-Arid'])
            co2_sequestered_global.drop(columns=['Temperate-Semi-Arid',
                'Boreal-Semi-Arid'], inplace=True)
        # Put columns in the same order as Excel.
        co2_sequestered_global = co2_sequestered_global[["Year", "All", "Tropical-Humid",
            "Temperate/Boreal-Humid", "Tropical-Semi-Arid", "Temperate/Boreal-Semi-Arid",
            "Global Arid"]]

        verify['CO2 Calcs'] = [
                ('A65:K110', obj.c2.co2eq_mmt_reduced().loc[2015:].reset_index(), near_zero_mask, None),
                ('A121:G166', co2_sequestered_global, seq_near_zero_mask, None),
                ('A173:AW218', obj.c2.co2_ppm_calculator().loc[2015:].reset_index(), ppm_near_zero_mask, None),
                # CO2 eq table has an N20 column for LAND xls sheets that doesn't appear to be used, so we ignore it
                ('A225:C270', obj.c2.co2eq_ppm_calculator().loc[2015:, ['CO2-eq PPM', 'CO2 PPM']].reset_index(), None, None),
                ('E225:G270', obj.c2.co2eq_ppm_calculator().loc[2015:, ['CH4 PPB', 'CO2 RF', 'CH4 RF']].reset_index(drop=True), near_zero_mask, None)
                # All other tables are not implemented as they appear to be all 0
        ]


def verify_ch4_calcs_rrs(obj, verify):
    """Verified tables in CH4 Calcs."""
    verify['CH4 Calcs'] = [
            ('A11:K56', obj.c4.ch4_tons_reduced().loc[2015:, :].reset_index(), None, None),
            ('A65:AW110', obj.c4.ch4_ppb_calculator().loc[2015:, :].reset_index(), None, None),
            ]
    return verify


def verify_ch4_calcs_land(obj, verify):
    """Verified tables in CH4 Calcs."""
    verify['CH4 Calcs'] = [
            ('A13:B58', obj.c4.avoided_direct_emissions_ch4_land().loc[2015:, 'World'].reset_index(), None, None),
            ('A67:AW112', obj.c4.ch4_ppb_calculator().loc[2015:, :].reset_index(), None, None),
            ]
    return verify


def is_custom_ad_with_no_regional_data(obj):
    """Check for Custom PDS adoption with no regional adoption data.

       This situation is not handled well in Excel:
       https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.9rp1qn24t2vi
       and results in unrealistically large regional adoption equal to the
       Total Addressable Market of that region, which will generally exceed
       the World adoption. This is impossible, the World is supposed to be
       strictly greater than the sum of all regions.

       We do not implement this handling in Python, instead the regional result
       will be NaN. For the test, if there is Custom PDS Adoption and it
       contains no regional data, we skip checking the regional results.
    """
    if obj.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
        data = obj.pds_ca.adoption_data_per_region()
        if all(pd.isnull(data.drop(columns='World'))):
            return True
    if obj.ac.soln_ref_adoption_basis == 'Custom':
        data = obj.ref_ca.adoption_data_per_region()
        if all(pd.isnull(data.drop(columns='World'))):
            return True
    return False


def excel_read_cell_any_scenario(zip_f, sheetname, cell):
    """Find the first instance of sheetname, and return the value of cell."""
    for name in zip_f.namelist():
        if sheetname in name:
            zip_csv_f = zip_f.open(name=name)
            (col, row) = cell_to_offsets(cell)
            df = pd.read_csv(filepath_or_buffer=zip_csv_f, header=None, index_col=None,
                    usecols=[col], skiprows=row, nrows=1)
            return df.loc[0, col]
    return None


def RRS_solution_verify_list(obj, zip_f):
    """Assemble verification for the modules used in RRS solutions.
          Arguments:
              obj: a solution object to be verified.
              zip_f: expected.zip of the Excel file to verify against.
    """
    verify = {}
    include_regional_data = not is_custom_ad_with_no_regional_data(obj)

    cell = excel_read_cell_any_scenario(
        zip_f=zip_f, sheetname='TAM Data', cell='N45')
    if cell == 'Functional Unit':
        verify_tam_data_eleven_sources(obj, verify)
    else:
        verify_tam_data(obj, verify)

    if obj.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
        cell = excel_read_cell_any_scenario(
            zip_f=zip_f, sheetname='Adoption Data', cell='N45')
        if cell == 'Functional Unit':
            verify_adoption_data_eleven_sources(obj, verify)
        else:
            verify_adoption_data(obj, verify)
    elif obj.ac.soln_pds_adoption_basis == 'Logistic S-Curve':
        verify_logistic_s_curve(obj, verify)
    elif obj.ac.soln_pds_adoption_basis == 'Bass Diffusion S-Curve':
        verify_bass_diffusion_s_curve(obj, verify)

    verify_helper_tables(
        obj, verify, include_regional_data=include_regional_data)
    verify_emissions_factors(obj, verify)
    verify_unit_adoption_calculations(obj, verify, include_regional_data=include_regional_data,
                    soln_type='RRS')
    verify_first_cost(obj, verify)
    verify_operating_cost(obj, verify)

    cell = excel_read_cell_any_scenario(
        zip_f=zip_f, sheetname='CO2 Calcs', cell='S343')
    if cell == 'Reduced Fuel Emissions':
        verify_co2_calcs(obj, verify, shifted=True,
                         include_regional_data=include_regional_data)
    else:
        verify_co2_calcs(
            obj, verify, include_regional_data=include_regional_data)
    verify_ch4_calcs_rrs(obj, verify)
    return verify


def LAND_solution_verify_list(obj, zip_f):
    """
    Assemble verification for the modules used in LAND solutions.
    Note: Due to known bugs in regional data in the xls not being recreated
    in python, it is necessary to exclude regional data for a number of tables
    in order for LAND solutions to pass this integration test.

    Arguments:
        obj: a solution object to be verified.
        zip_f: expected.zip of the Excel file to verify against.
    """
    verify = {}

    cell = str(excel_read_cell_any_scenario(zip_f=zip_f, sheetname='AEZ Data', cell='A47'))
    if cell.startswith('2014 Land Distribution'):
        cohort = 2018
    else:
        cell = str(excel_read_cell_any_scenario(zip_f=zip_f, sheetname='AEZ Data', cell='A52'))
        assert cell.startswith('2014 Land Distribution')
        cell = str(excel_read_cell_any_scenario(zip_f=zip_f, sheetname='AEZ Data', cell='D52'))
        if cell == 'Boreal-Humid':
            cohort = 2020
        else:
            cohort = 2019

    verify_aez_data(obj, verify, cohort=cohort)

    if obj.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
        verify_adoption_data(obj, verify)
    elif obj.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
        verify_custom_adoption(obj, verify)
    verify_helper_tables(obj, verify, include_regional_data=False)
    verify_emissions_factors(obj, verify)

    cell = excel_read_cell_any_scenario(zip_f=zip_f, sheetname='Unit Adoption Calculations',
                    cell='CG124')
    if cell == 'Cumulative Degraded Land that is Unprotected in the PDS':
        soln_type = 'LAND_PROTECT'
    else:
        soln_type = 'LAND_BIOSEQ'
    verify_unit_adoption_calculations(
        obj, verify, include_regional_data=False, soln_type=soln_type)

    verify_first_cost(obj, verify)
    verify_operating_cost(obj, verify)
    verify_co2_calcs(obj, verify, is_rrs=False, include_regional_data=False, cohort=cohort)
    verify_ch4_calcs_land(obj, verify)
    return verify


def compare_dataframes(actual_df, expected_df, description='', mask=None, absignore=None):
    """Compare two dataframes and print where they differ."""
    nerrors = 0
    if actual_df.shape != expected_df.shape:
        raise AssertionError(description + '\nDataFrames differ in shape: ' +
                str(actual_df.shape) + " versus " + str(expected_df.shape))
    (nrows, ncols) = actual_df.shape
    msg = ''
    rel = 1e-6 if absignore else None  # if abs & !rel, rel is ignored. We want rel.
    for r in range(nrows):
        for c in range(ncols):
            if mask is not None:
                mask.iloc[r, c]
            if mask is not None and mask.iloc[r, c]:
                continue
            matches = True
            act = actual_df.iloc[r, c]
            exp = expected_df.iloc[r, c]
            if isinstance(act, str) and isinstance(exp, str):
                matches = (act == exp)
            elif (pd.isna(act) or act == '' or act is None or act == 0 or act == pytest.approx(0.0)
                    or exp == pytest.approx(0.0)):
                matches = (pd.isna(exp) or exp == '' or exp is None or exp == 0 or
                        exp == pytest.approx(0.0, abs=1e-7))
            elif np.isinf(act):
                # Excel #DIV/0! turns into NaN.
                matches = pd.isna(exp) or np.isinf(exp)
            else:
                matches = (act == pytest.approx(exp, rel=rel, abs=absignore))
            if not matches:
                msg += "Err [" + str(r) + "][" + str(c) + "] : " + \
                        "'" + str(act) + "' != '" + str(exp) + "'\n"
                nerrors += 1
            if nerrors > 10:
                break
    if msg:
        raise AssertionError(description + '\nDataFrames differ:\n' + msg)


def check_excel_against_object(obj, zip_f, scenario, verify):
    print("Checking " + scenario)
    descr_base = "Solution: " + obj.name + " Scenario: " + scenario + " "
    for sheetname in verify.keys():
        print(sheetname)
        for (cellrange, actual_df, actual_mask, expected_mask) in verify[sheetname]:
            (usecols, skiprows, nrows) = get_pd_read_excel_args(cellrange)
            arcname = f'{scenario}/{sheetname}'
            zip_csv_f = zip_f.open(name=arcname)
            expected_df = pd.read_csv(filepath_or_buffer=zip_csv_f, header=None,
                index_col=None, usecols=usecols, skiprows=skiprows, nrows=nrows)
            absignore = None
            if expected_mask is not None:
                if isinstance(expected_mask, str) and expected_mask == "Excel_NaN":
                    expected_mask = expected_df.isna()
                elif isinstance(expected_mask, str) and expected_mask == "Excel_one_cent":
                    # Due to floating point precision, sometimes subtracting ~identical values for
                    # unit adoption is not zero it is 0.000000000000007105427357601000 which,
                    # when multiplied by a large unit cost, can result in a First Cost of (say) 2.5e-6
                    # instead of the zero which might otherwise be expected.
                    # Mask off absolute values less than one penny.
                    s = expected_df.abs()
                    expected_mask = s.mask(s < 0.01, other=True).where(s < 0.01, other=False) | expected_df.isna()
                    absignore = 0.01
            if actual_mask is not None and expected_mask is not None:
                mask = actual_mask | expected_mask
            elif actual_mask is not None:
                mask = actual_mask
            else:
                mask = expected_mask
            description = descr_base + sheetname + " " + cellrange
            compare_dataframes(actual_df=actual_df, expected_df=expected_df,
                    description=description, mask=mask, absignore=absignore)


@pytest.mark.slow
def test_Afforestation_LAND():
    from solution import afforestation
    zipfilename = str(solutiondir.joinpath(
        'afforestation', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in afforestation.scenarios.keys():
        obj = afforestation.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Airplanes_RRS():
    from solution import airplanes
    zipfilename = str(solutiondir.joinpath(
        'airplanes', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in airplanes.scenarios.keys():
        obj = airplanes.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_AltCement_RRS():
    from solution import altcement
    zipfilename = str(solutiondir.joinpath(
        'altcement', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in altcement.scenarios.keys():
        obj = altcement.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_BikeInfrastructure_RRS():
    from solution import bikeinfrastructure
    zipfilename = str(solutiondir.joinpath(
        'bikeinfrastructure', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in bikeinfrastructure.scenarios.keys():
        obj = bikeinfrastructure.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Bamboo_LAND():
    from solution import bamboo
    zipfilename = str(solutiondir.joinpath(
        'bamboo', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in bamboo.scenarios.keys():
        obj = bamboo.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Biochar_RRS():
    from solution import biochar
    zipfilename = str(solutiondir.joinpath(
        'biochar', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in biochar.scenarios.keys():
        obj = biochar.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Biogas_RRS():
    from solution import biogas
    zipfilename = str(solutiondir.joinpath(
        'biogas', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in biogas.scenarios.keys():
        obj = biogas.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Biogas_Small_RRS():
    from solution import biogas_small
    zipfilename = str(solutiondir.joinpath(
        'biogas_small', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in biogas_small.scenarios.keys():
        obj = biogas_small.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Biomass_RRS():
    from solution import biomass
    zipfilename = str(solutiondir.joinpath(
        'biomass', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in biomass.scenarios.keys():
        obj = biomass.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Bioplastic_RRS():
    from solution import bioplastic
    zipfilename = str(solutiondir.joinpath(
        'bioplastic', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in ['PDS1-33p2050-Feedstock Limit-385MMT (Book Ed.1)']:
        obj = bioplastic.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_BuildingAutomation_RRS():
    from solution import buildingautomation
    zipfilename = str(solutiondir.joinpath(
        'buildingautomation', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in buildingautomation.scenarios.keys():
        obj = buildingautomation.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Carpooling_RRS():
    from solution import carpooling
    zipfilename = str(solutiondir.joinpath(
        'carpooling', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in carpooling.scenarios.keys():
        obj = carpooling.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Composting_RRS():
    from solution import composting
    zipfilename = str(solutiondir.joinpath(
        'composting', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in composting.scenarios.keys():
        obj = composting.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ConcentratedSolar_RRS():
    from solution import concentratedsolar
    zipfilename = str(solutiondir.joinpath(
        'concentratedsolar', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in concentratedsolar.scenarios.keys():
        obj = concentratedsolar.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ConservationAgriculture_LAND():
    from solution import conservationagriculture
    zipfilename = str(solutiondir.joinpath(
        'conservationagriculture', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in conservationagriculture.scenarios.keys():
        obj = conservationagriculture.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_CoolRoofs_RRS():
    from solution import coolroofs
    zipfilename = str(solutiondir.joinpath(
        'coolroofs', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in coolroofs.scenarios.keys():
        obj = coolroofs.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_DistrictHeating_RRS():
    from solution import districtheating
    zipfilename = str(solutiondir.joinpath(
        'districtheating', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in districtheating.scenarios.keys():
        obj = districtheating.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ElectricBikes_RRS():
    from solution import electricbikes
    zipfilename = str(solutiondir.joinpath(
        'electricbikes', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in electricbikes.scenarios.keys():
        obj = electricbikes.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ElectricVehicles_RRS():
    from solution import electricvehicles
    zipfilename = str(solutiondir.joinpath(
        'electricvehicles', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in electricvehicles.scenarios.keys():
        obj = electricvehicles.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_FarmlandRestoration_LAND():
    from solution import farmlandrestoration
    zipfilename = str(solutiondir.joinpath(
        'farmlandrestoration', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in farmlandrestoration.scenarios.keys():
        obj = farmlandrestoration.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ForestProtection_LAND():
    from solution import forestprotection
    zipfilename = str(solutiondir.joinpath(
        'forestprotection', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in forestprotection.scenarios.keys():
        obj = forestprotection.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Geothermal_RRS():
    from solution import geothermal
    zipfilename = str(solutiondir.joinpath(
        'geothermal', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in geothermal.scenarios.keys():
        obj = geothermal.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_GrasslandProtection_LAND():
    from solution import grasslandprotection
    zipfilename = str(solutiondir.joinpath(
        'grasslandprotection', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in grasslandprotection.scenarios.keys():
        obj = grasslandprotection.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_GreenRoofs_RRS():
    from solution import greenroofs
    zipfilename = str(solutiondir.joinpath(
        'greenroofs', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in greenroofs.scenarios.keys():
        obj = greenroofs.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_HeatPumps_RRS():
    from solution import heatpumps
    zipfilename = str(solutiondir.joinpath(
        'heatpumps', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in heatpumps.scenarios.keys():
        obj = heatpumps.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_HighSpeedRail_RRS():
    from solution import highspeedrail
    zipfilename = str(solutiondir.joinpath(
        'highspeedrail', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in highspeedrail.scenarios.keys():
        obj = highspeedrail.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_HybridCars_RRS():
    from solution import hybridcars
    zipfilename = str(solutiondir.joinpath(
        'hybridcars', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in hybridcars.scenarios.keys():
        obj = hybridcars.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ImprovedCookStoves_RRS():
    from solution import improvedcookstoves
    zipfilename = str(solutiondir.joinpath(
        'improvedcookstoves', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in improvedcookstoves.scenarios.keys():
        obj = improvedcookstoves.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ImprovedRice_LAND():
    from solution import improvedrice
    zipfilename = str(solutiondir.joinpath(
        'improvedrice', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in improvedrice.scenarios.keys():
        obj = improvedrice.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_IndigenousPeoplesLand_LAND():
    from solution import indigenouspeoplesland
    zipfilename = str(solutiondir.joinpath(
        'indigenouspeoplesland', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in indigenouspeoplesland.scenarios.keys():
        obj = indigenouspeoplesland.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_InstreamHydro_RRS():
    from solution import instreamhydro
    zipfilename = str(solutiondir.joinpath(
        'instreamhydro', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in instreamhydro.scenarios.keys():
        obj = instreamhydro.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Insulation_RRS():
    from solution import insulation
    zipfilename = str(solutiondir.joinpath(
        'insulation', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in insulation.scenarios.keys():
        obj = insulation.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_IrrigationEfficiency_LAND():
    from solution import irrigationefficiency
    zipfilename = str(solutiondir.joinpath(
        'irrigationefficiency', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in irrigationefficiency.scenarios.keys():
        obj = irrigationefficiency.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_LandfillMethane_RRS():
    from solution import landfillmethane
    zipfilename = str(solutiondir.joinpath(
        'landfillmethane', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in landfillmethane.scenarios.keys():
        obj = landfillmethane.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_LEDCommercialLighting_RRS():
    from solution import leds_commercial
    zipfilename = str(solutiondir.joinpath(
        'leds_commercial', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in leds_commercial.scenarios.keys():
        obj = leds_commercial.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_LEDResidentialLighting_RRS():
    from solution import leds_residential
    zipfilename = str(solutiondir.joinpath(
        'leds_residential', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in leds_residential.scenarios.keys():
        obj = leds_residential.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ManagedGrazing_LAND():
    from solution import managedgrazing
    zipfilename = str(solutiondir.joinpath(
        'managedgrazing', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in managedgrazing.scenarios.keys():
        obj = managedgrazing.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_MangroveRestoration_LAND():
    from solution import mangroverestoration
    zipfilename = str(solutiondir.joinpath(
        'mangroverestoration', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in mangroverestoration.scenarios.keys():
        obj = mangroverestoration.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_MassTransit_RRS():
    from solution import masstransit
    zipfilename = str(solutiondir.joinpath(
        'masstransit', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in masstransit.scenarios.keys():
        obj = masstransit.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_MicroWind_RRS():
    from solution import microwind
    zipfilename = str(solutiondir.joinpath(
        'microwind', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in microwind.scenarios.keys():
        obj = microwind.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        # Drawdown 2020 version of MicroWind rearranged the entire Adoption Data tab. Since
        # none of the regions actually has any data and the World region is adequately tested
        # by later stages of the model, we just skip checking it.
        del verify['Adoption Data']
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_MultistrataAgroforestry_LAND():
    from solution import multistrataagroforestry
    zipfilename = str(solutiondir.joinpath(
        'multistrataagroforestry', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in multistrataagroforestry.scenarios.keys():
        obj = multistrataagroforestry.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Nuclear_RRS():
    from solution import nuclear
    zipfilename = str(solutiondir.joinpath(
        'nuclear', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in nuclear.scenarios.keys():
        obj = nuclear.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_NutrientManagement_LAND():
    from solution import nutrientmanagement
    zipfilename = str(solutiondir.joinpath(
        'nutrientmanagement', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in nutrientmanagement.scenarios.keys():
        obj = nutrientmanagement.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_OffshoreWind_RRS():
    from solution import offshorewind
    zipfilename = str(solutiondir.joinpath(
        'offshorewind', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in offshorewind.scenarios.keys():
        obj = offshorewind.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_OnshoreWind_RRS():
    from solution import onshorewind
    zipfilename = str(solutiondir.joinpath(
        'onshorewind', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in onshorewind.scenarios.keys():
        obj = onshorewind.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Peatlands_LAND():
    from solution import peatlands
    zipfilename = str(solutiondir.joinpath(
        'peatlands', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in peatlands.scenarios.keys():
        obj = peatlands.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_PerennialBioenergy_LAND():
    from solution import perennialbioenergy
    zipfilename = str(solutiondir.joinpath(
        'perennialbioenergy', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in perennialbioenergy.scenarios.keys():
        obj = perennialbioenergy.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_RecycledPaper_RRS():
    from solution import recycledpaper
    zipfilename = str(solutiondir.joinpath(
        'recycledpaper', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in recycledpaper.scenarios.keys():
        obj = recycledpaper.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Refrigerants_RRS():
    from solution import refrigerants
    zipfilename = str(solutiondir.joinpath(
        'refrigerants', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in refrigerants.scenarios.keys():
        obj = refrigerants.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_RegenerativeAgriculture_LAND():
    from solution import regenerativeagriculture
    zipfilename = str(solutiondir.joinpath(
        'regenerativeagriculture', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in regenerativeagriculture.scenarios.keys():
        obj = regenerativeagriculture.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_RiceIntensification_LAND():
    from solution import riceintensification
    zipfilename = str(solutiondir.joinpath(
        'riceintensification', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in riceintensification.scenarios.keys():
        obj = riceintensification.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Ships_RRS():
    from solution import ships
    zipfilename = str(solutiondir.joinpath(
        'ships', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in ships.scenarios.keys():
        obj = ships.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Silvopasture_LAND():
    from solution import silvopasture
    zipfilename = str(solutiondir.joinpath(
        'silvopasture', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in silvopasture.scenarios.keys():
        obj = silvopasture.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        del verify['CH4 Calcs']
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SmartGlass_RRS():
    from solution import smartglass
    zipfilename = str(solutiondir.joinpath(
        'smartglass', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in smartglass.scenarios.keys():
        obj = smartglass.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SmartThermostats_RRS():
    from solution import smartthermostats
    zipfilename = str(solutiondir.joinpath(
        'smartthermostats', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in smartthermostats.scenarios.keys():
        obj = smartthermostats.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SolarHotWater_RRS():
    from solution import solarhotwater
    zipfilename = str(solutiondir.joinpath(
        'solarhotwater', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    # Need to figure out how to handle 'Aggressive, High Growth, early' source in
    # PDS CustomAdoption, which varies according to data coming from UnitAdoption.
    # The checked-in CSV file is a snapshot of the first scenario values.
    for scenario in ['PDS1-25p2050-Low of Custom Scen. (Book Ed.1)']:
        obj = solarhotwater.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SolarRooftop_RRS():
    from solution import solarpvroof
    zipfilename = str(solutiondir.joinpath(
        'solarpvroof', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in solarpvroof.scenarios.keys():
        obj = solarpvroof.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SolarPVUtility_RRS():
    from solution import solarpvutil
    zipfilename = str(solutiondir.joinpath(
        'solarpvutil', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in solarpvutil.scenarios.keys():
        obj = solarpvutil.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Telepresence_RRS():
    from solution import telepresence
    zipfilename = str(solutiondir.joinpath(
        'telepresence', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in telepresence.scenarios.keys():
        obj = telepresence.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_TemperateForests_LAND():
    from solution import temperateforests
    zipfilename = str(solutiondir.joinpath(
        'temperateforests', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario, ac in temperateforests.scenarios.items():
        obj = temperateforests.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_TreeIntercropping_LAND():
    from solution import treeintercropping
    zipfilename = str(solutiondir.joinpath(
        'treeintercropping', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in treeintercropping.scenarios.keys():
        obj = treeintercropping.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Trains_RRS():
    from solution import trains
    zipfilename = str(solutiondir.joinpath(
        'trains', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in trains.scenarios.keys():
        obj = trains.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_TropicalForests_LAND():
    from solution import tropicalforests
    zipfilename = str(solutiondir.joinpath(
        'tropicalforests', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario, ac in tropicalforests.scenarios.items():
        obj = tropicalforests.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_TropicalTreeStaples_LAND():
    from solution import tropicaltreestaples
    zipfilename = str(solutiondir.joinpath(
        'tropicaltreestaples', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in tropicaltreestaples.scenarios.keys():
        obj = tropicaltreestaples.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Trucks_RRS():
    from solution import trucks
    zipfilename = str(solutiondir.joinpath(
        'trucks', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in trucks.scenarios.keys():
        obj = trucks.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WalkableCities_RRS():
    from solution import walkablecities
    zipfilename = str(solutiondir.joinpath(
        'walkablecities', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in walkablecities.scenarios.keys():
        obj = walkablecities.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WasteToEnergy_RRS():
    from solution import wastetoenergy
    zipfilename = str(solutiondir.joinpath(
        'wastetoenergy', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in wastetoenergy.scenarios.keys():
        obj = wastetoenergy.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WaterDistribution_RRS():
    from solution import waterdistribution
    zipfilename = str(solutiondir.joinpath(
        'waterdistribution', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in waterdistribution.scenarios.keys():
        obj = waterdistribution.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WaterEfficiency_RRS():
    from solution import waterefficiency
    zipfilename = str(solutiondir.joinpath(
        'waterefficiency', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in waterefficiency.scenarios.keys():
        obj = waterefficiency.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WaveAndTidal_RRS():
    from solution import waveandtidal
    zipfilename = str(solutiondir.joinpath(
        'waveandtidal', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in waveandtidal.scenarios.keys():
        obj = waveandtidal.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WomenSmallholders_LAND():
    from solution import womensmallholders
    zipfilename = str(solutiondir.joinpath(
        'womensmallholders', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in womensmallholders.scenarios.keys():
        obj = womensmallholders.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(
            obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)
