"""
An end-to-end test which pulls data from the original Excel models, not just the final answers
but each intermediate step. It then compares the Python result at each step of the calculation,
to ensure that the new implementation not only gets the same answers but does so for the
same reasons.
"""

import os.path
import pathlib
import re
import shutil
import sys
import time
import tempfile
import numpy as np
import pandas as pd
import pytest
import zipfile

from solution import afforestation
from solution import airplanes
from solution import altcement
from solution import bikeinfrastructure
from solution import bamboo
from solution import biochar
from solution import biogas
from solution import biomass
from solution import bioplastic
from solution import buildingautomation
from solution import carpooling
from solution import cars
from solution import composting
from solution import concentratedsolar
from solution import conservationagriculture
from solution import coolroofs
from solution import districtheating
from solution import electricbikes
from solution import electricvehicles
from solution import farmlandrestoration
from solution import forestprotection
from solution import geothermal
from solution import greenroofs
from solution import heatpumps
from solution import highspeedrail
from solution import improvedcookstoves
from solution import improvedrice
from solution import indigenouspeoplesland
from solution import instreamhydro
from solution import insulation
from solution import irrigationefficiency
from solution import landfillmethane
from solution import leds_commercial
from solution import leds_residential
from solution import managedgrazing
from solution import masstransit
from solution import microwind
from solution import multistrataagroforestry
from solution import nuclear
from solution import nutrientmanagement
from solution import offshorewind
from solution import onshorewind
from solution import peatlands
from solution import perennialbioenergy
from solution import recycledpaper
from solution import refrigerants
from solution import regenerativeagriculture
from solution import riceintensification
from solution import ships
from solution import silvopasture
from solution import smartglass
from solution import smartthermostats
from solution import solarhotwater
from solution import solarpvutil
from solution import solarpvroof
from solution import temperateforests
from solution import telepresence
from solution import treeintercropping
from solution import trains
from solution import trucks
from solution import tropicalforests
from solution import tropicaltreestaples
from solution import walkablecities
from solution import waterdistribution
from solution import waterefficiency
from solution import waveandtidal
from solution import womensmallholders

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
        usecols = range(startcol, endcol+1)
        skiprows = startrow
        nrows = endrow - startrow + 1
        return (usecols, skiprows, nrows)


def verify_aez_data(obj, verify=None):
    """Verified tables in AEZ Data."""
    if verify is None:
        verify = {}
    verify['AEZ Data'] = [
            ('A48:H53', obj.ae.get_land_distribution().reset_index().iloc[:6, :], None),
            ('A55:H58', obj.ae.get_land_distribution().reset_index().iloc[6:, :], None)
    ]
    return verify


def _get_tam_trend_masks(obj):
    """If the TAM data being analyzed is very close to linear, then the 2nd/3rd order polynomial
          and exponential curve fits degenerate to where only the x^1 and constant terms matter and
          the higher order terms do not.
    
          For example in biochar, Excel and Python both come up with {x}=1.57e+07 & const=1.049e+09
          For degree2, Python comes up with -1.15e-09 while Excel decides it is -1.32e-09, but
          it doesn't matter because they are 16 orders of magnitude less than the {x} term.
    
          If the TAM Data is very close to linear, skip comparing the higher order curve fits.
    """
    degree2 = obj.tm.forecast_trend_global(trend='Degree2')
    d2_mask = d3_mask = exp_mask = None
    if abs(degree2.loc[2015, 'x'] / degree2.loc[2015, 'x^2']) > 1e12:
        d2_mask = degree2.reset_index(drop=True).copy(deep=True)
        d2_mask.loc[:, :] = False
        d2_mask['x^2'] = True
        d3_mask = obj.tm.forecast_trend_global(trend='Degree3').reset_index(drop=True).copy(deep=True)
        d3_mask.loc[:, :] = False
        d3_mask['x^2'] = True
        d3_mask['x^3'] = True
        exp_mask = obj.tm.forecast_trend_global(trend='Exponential').reset_index(drop=True).copy(deep=True)
        exp_mask.loc[:, :] = False
        exp_mask['e^x'] = True
    return (d2_mask, d3_mask, exp_mask)


def verify_tam_data(obj, verify=None):
    """Verified tables in TAM Data."""
    if verify is None:
        verify = {}

    (d2_mask, d3_mask, exp_mask) = _get_tam_trend_masks(obj=obj)
    verify['TAM Data'] = [
            ('W46:Y94', obj.tm.forecast_min_max_sd_global().reset_index(drop=True), None),
            ('AA46:AC94', obj.tm.forecast_low_med_high_global().reset_index(drop=True), None),
            ('BX50:BZ96', obj.tm.forecast_trend_global(trend='Linear').reset_index(drop=True), None),
            ('CE50:CH96', obj.tm.forecast_trend_global(trend='Degree2').reset_index(drop=True), d2_mask),
            ('CM50:CQ96', obj.tm.forecast_trend_global(trend='Degree3').reset_index(drop=True), d3_mask),
            ('CV50:CX96', obj.tm.forecast_trend_global(trend='Exponential').reset_index(drop=True), exp_mask),
            ('DZ45:EA91', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'World']], None),
            # TODO Figure out PDS TAM handling
            ('W164:Y212', obj.tm.forecast_min_max_sd_oecd90().reset_index(drop=True), None),
            ('AA164:AC212', obj.tm.forecast_low_med_high_oecd90().reset_index(drop=True), None),
            ('BX168:BZ214', obj.tm.forecast_trend_oecd90(trend='Linear').reset_index(drop=True), None),
            ('CE168:CH214', obj.tm.forecast_trend_oecd90(trend='Degree2').reset_index(drop=True), None),
            ('CM168:CQ214', obj.tm.forecast_trend_oecd90(trend='Degree3').reset_index(drop=True), None),
            ('CV168:CX214', obj.tm.forecast_trend_oecd90(trend='Exponential').reset_index(drop=True), None),
            ('DZ163:EA209', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'OECD90']], None),
            ('W228:Y276', obj.tm.forecast_min_max_sd_eastern_europe().reset_index(drop=True), None),
            ('AA228:AC276', obj.tm.forecast_low_med_high_eastern_europe().reset_index(drop=True), None),
            ('BX232:BZ278', obj.tm.forecast_trend_eastern_europe(trend='Linear').reset_index(drop=True), None),
            ('CE232:CH278', obj.tm.forecast_trend_eastern_europe(trend='Degree2').reset_index(drop=True), None),
            ('CM232:CQ278', obj.tm.forecast_trend_eastern_europe(trend='Degree3').reset_index(drop=True), None),
            ('CV232:CX278', obj.tm.forecast_trend_eastern_europe(trend='Exponential').reset_index(drop=True), None),
            ('DZ227:EA273', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'Eastern Europe']], None),
            ('W291:Y339', obj.tm.forecast_min_max_sd_asia_sans_japan().reset_index(drop=True), None),
            ('AA291:AC339', obj.tm.forecast_low_med_high_asia_sans_japan().reset_index(drop=True), None),
            ('BX295:BZ341', obj.tm.forecast_trend_asia_sans_japan(trend='Linear').reset_index(drop=True), None),
            ('CE295:CH341', obj.tm.forecast_trend_asia_sans_japan(trend='Degree2').reset_index(drop=True), None),
            ('CM295:CQ341', obj.tm.forecast_trend_asia_sans_japan(trend='Degree3').reset_index(drop=True), None),
            ('CV295:CX341', obj.tm.forecast_trend_asia_sans_japan(trend='Exponential').reset_index(drop=True), None),
            ('DZ290:EA336', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'Asia (Sans Japan)']], None),
            ('W354:Y402', obj.tm.forecast_min_max_sd_middle_east_and_africa().reset_index(drop=True), None),
            ('AA354:AC402', obj.tm.forecast_low_med_high_middle_east_and_africa().reset_index(drop=True), None),
            ('BX358:BZ404', obj.tm.forecast_trend_middle_east_and_africa(trend='Linear').reset_index(drop=True), None),
            ('CE358:CH404', obj.tm.forecast_trend_middle_east_and_africa(trend='Degree2').reset_index(drop=True), None),
            ('CM358:CQ404', obj.tm.forecast_trend_middle_east_and_africa(trend='Degree3').reset_index(drop=True), None),
            ('CV358:CX404', obj.tm.forecast_trend_middle_east_and_africa(trend='Exponential').reset_index(drop=True), None),
            ('DZ353:EA399', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'Middle East and Africa']], None),
            ('W417:Y465', obj.tm.forecast_min_max_sd_latin_america().reset_index(drop=True), None),
            ('AA417:AC465', obj.tm.forecast_low_med_high_latin_america().reset_index(drop=True), None),
            ('BX421:BZ467', obj.tm.forecast_trend_latin_america(trend='Linear').reset_index(drop=True), None),
            ('CE421:CH467', obj.tm.forecast_trend_latin_america(trend='Degree2').reset_index(drop=True), None),
            ('CM421:CQ467', obj.tm.forecast_trend_latin_america(trend='Degree3').reset_index(drop=True), None),
            ('CV421:CX467', obj.tm.forecast_trend_latin_america(trend='Exponential').reset_index(drop=True), None),
            ('DZ416:EA462', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'Latin America']], None),
            ('W480:Y528', obj.tm.forecast_min_max_sd_china().reset_index(drop=True), None),
            ('AA480:AC528', obj.tm.forecast_low_med_high_china().reset_index(drop=True), None),
            ('BX484:BZ530', obj.tm.forecast_trend_china(trend='Linear').reset_index(drop=True), None),
            ('CE484:CH530', obj.tm.forecast_trend_china(trend='Degree2').reset_index(drop=True), None),
            ('CM484:CQ530', obj.tm.forecast_trend_china(trend='Degree3').reset_index(drop=True), None),
            ('CV484:CX530', obj.tm.forecast_trend_china(trend='Exponential').reset_index(drop=True), None),
            ('DZ479:EA525', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'China']], None),
            ('W544:Y592', obj.tm.forecast_min_max_sd_india().reset_index(drop=True), None),
            ('AA544:AC592', obj.tm.forecast_low_med_high_india().reset_index(drop=True), None),
            ('BX548:BZ594', obj.tm.forecast_trend_india(trend='Linear').reset_index(drop=True), None),
            ('CE548:CH594', obj.tm.forecast_trend_india(trend='Degree2').reset_index(drop=True), None),
            ('CM548:CQ594', obj.tm.forecast_trend_india(trend='Degree3').reset_index(drop=True), None),
            ('CV548:CX594', obj.tm.forecast_trend_india(trend='Exponential').reset_index(drop=True), None),
            ('DZ543:EA589', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'India']], None),
            ('W608:Y656', obj.tm.forecast_min_max_sd_eu().reset_index(drop=True), None),
            ('AA608:AC656', obj.tm.forecast_low_med_high_eu().reset_index(drop=True), None),
            ('BX612:BZ658', obj.tm.forecast_trend_eu(trend='Linear').reset_index(drop=True), None),
            ('CE612:CH658', obj.tm.forecast_trend_eu(trend='Degree2').reset_index(drop=True), None),
            ('CM612:CQ658', obj.tm.forecast_trend_eu(trend='Degree3').reset_index(drop=True), None),
            ('CV612:CX658', obj.tm.forecast_trend_eu(trend='Exponential').reset_index(drop=True), None),
            ('DZ607:EA653', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'EU']], None),
            ('W673:Y721', obj.tm.forecast_min_max_sd_usa().reset_index(drop=True), None),
            ('AA673:AC721', obj.tm.forecast_low_med_high_usa().reset_index(drop=True), None),
            ('BX677:BZ723', obj.tm.forecast_trend_usa(trend='Linear').reset_index(drop=True), None),
            ('CE677:CH723', obj.tm.forecast_trend_usa(trend='Degree2').reset_index(drop=True), None),
            ('CM677:CQ723', obj.tm.forecast_trend_usa(trend='Degree3').reset_index(drop=True), None),
            ('CV677:CX723', obj.tm.forecast_trend_usa(trend='Exponential').reset_index(drop=True), None),
            ('DZ672:EA718', obj.tm.ref_tam_per_region().reset_index().loc[:, ['Year', 'USA']], None),
            ]
    return verify

def verify_tam_data_eleven_sources(obj, verify=None):
    """Verified tables in TAM Data, with smaller source data area.

          Some solutions, first noticed with ImprovedCookStoves, have a smaller set of
          columns to hold data sources and this shifts all of the rest of the columns to
          the left. This test specifies the columns for this narrower layout.
    """
    if verify is None:
        verify = {}

    (d2_mask, d3_mask, exp_mask) = _get_tam_trend_masks(obj=obj)
    verify['TAM Data'] = [
            ('S46:U94', obj.tm.forecast_min_max_sd_global().reset_index(drop=True), None),
            ('W46:Y94', obj.tm.forecast_low_med_high_global().reset_index(drop=True), None),
            ('BT50:BV96', obj.tm.forecast_trend_global(trend='Linear').reset_index(drop=True), None),
            ('CA50:CD96', obj.tm.forecast_trend_global(trend='Degree2').reset_index(drop=True), d2_mask),
            ('CI50:CM96', obj.tm.forecast_trend_global(trend='Degree3').reset_index(drop=True), d3_mask),
            ('CR50:CT96', obj.tm.forecast_trend_global(trend='Exponential').reset_index(drop=True), exp_mask),
            #('DV45:DW91', obj.tm.forecast_trend_global().reset_index().loc[:, ['Year', 'adoption']], None), first year differs
            # TODO Figure out PDS TAM handling
            ('S164:U212', obj.tm.forecast_min_max_sd_oecd90().reset_index(drop=True), None),
            ('W164:Y212', obj.tm.forecast_low_med_high_oecd90().reset_index(drop=True), None),
            ('BT168:BV214', obj.tm.forecast_trend_oecd90(trend='Linear').reset_index(drop=True), None),
            ('CA168:CD214', obj.tm.forecast_trend_oecd90(trend='Degree2').reset_index(drop=True), None),
            ('CI168:CM214', obj.tm.forecast_trend_oecd90(trend='Degree3').reset_index(drop=True), None),
            ('CR168:CT214', obj.tm.forecast_trend_oecd90(trend='Exponential').reset_index(drop=True), None),
            #('DV163:DW209', obj.tm.forecast_trend_oecd90().reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S228:U276', obj.tm.forecast_min_max_sd_eastern_europe().reset_index(drop=True), None),
            ('W228:Y276', obj.tm.forecast_low_med_high_eastern_europe().reset_index(drop=True), None),
            ('BT232:BV278', obj.tm.forecast_trend_eastern_europe(trend='Linear').reset_index(drop=True), None),
            ('CA232:CD278', obj.tm.forecast_trend_eastern_europe(trend='Degree2').reset_index(drop=True), None),
            ('CI232:CM278', obj.tm.forecast_trend_eastern_europe(trend='Degree3').reset_index(drop=True), None),
            ('CR232:CT278', obj.tm.forecast_trend_eastern_europe(trend='Exponential').reset_index(drop=True), None),
            #('DV227:DW273', obj.tm.forecast_trend_eastern_europe().reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S291:U339', obj.tm.forecast_min_max_sd_asia_sans_japan().reset_index(drop=True), None),
            ('W291:Y339', obj.tm.forecast_low_med_high_asia_sans_japan().reset_index(drop=True), None),
            ('BT295:BV341', obj.tm.forecast_trend_asia_sans_japan(trend='Linear').reset_index(drop=True), None),
            ('CA295:CD341', obj.tm.forecast_trend_asia_sans_japan(trend='Degree2').reset_index(drop=True), None),
            ('CI295:CM341', obj.tm.forecast_trend_asia_sans_japan(trend='Degree3').reset_index(drop=True), None),
            ('CR295:CT341', obj.tm.forecast_trend_asia_sans_japan(trend='Exponential').reset_index(drop=True), None),
            #('DV290:DW336', obj.tm.forecast_trend_asia_sans_japan().reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S354:U402', obj.tm.forecast_min_max_sd_middle_east_and_africa().reset_index(drop=True), None),
            ('W354:Y402', obj.tm.forecast_low_med_high_middle_east_and_africa().reset_index(drop=True), None),
            ('BT358:BV404', obj.tm.forecast_trend_middle_east_and_africa(trend='Linear').reset_index(drop=True), None),
            ('CA358:CD404', obj.tm.forecast_trend_middle_east_and_africa(trend='Degree2').reset_index(drop=True), None),
            ('CI358:CM404', obj.tm.forecast_trend_middle_east_and_africa(trend='Degree3').reset_index(drop=True), None),
            ('CR358:CT404', obj.tm.forecast_trend_middle_east_and_africa(trend='Exponential').reset_index(drop=True), None),
            #('DV353:DW399', obj.tm.forecast_trend_middle_east_and_africa().reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S417:U465', obj.tm.forecast_min_max_sd_latin_america().reset_index(drop=True), None),
            ('W417:Y465', obj.tm.forecast_low_med_high_latin_america().reset_index(drop=True), None),
            ('BT421:BV467', obj.tm.forecast_trend_latin_america(trend='Linear').reset_index(drop=True), None),
            ('CA421:CD467', obj.tm.forecast_trend_latin_america(trend='Degree2').reset_index(drop=True), None),
            ('CI421:CM467', obj.tm.forecast_trend_latin_america(trend='Degree3').reset_index(drop=True), None),
            ('CR421:CT467', obj.tm.forecast_trend_latin_america(trend='Exponential').reset_index(drop=True), None),
            #('DV416:DW465', obj.tm.forecast_trend_latin_america().reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S480:U528', obj.tm.forecast_min_max_sd_china().reset_index(drop=True), None),
            ('W480:Y528', obj.tm.forecast_low_med_high_china().reset_index(drop=True), None),
            ('BT484:BV530', obj.tm.forecast_trend_china(trend='Linear').reset_index(drop=True), None),
            ('CA484:CD530', obj.tm.forecast_trend_china(trend='Degree2').reset_index(drop=True), None),
            ('CI484:CM530', obj.tm.forecast_trend_china(trend='Degree3').reset_index(drop=True), None),
            ('CR484:CT530', obj.tm.forecast_trend_china(trend='Exponential').reset_index(drop=True), None),
            #('DV479:DW525', obj.tm.forecast_trend_china().reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S544:U592', obj.tm.forecast_min_max_sd_india().reset_index(drop=True), None),
            ('W544:Y592', obj.tm.forecast_low_med_high_india().reset_index(drop=True), None),
            ('BT548:BV594', obj.tm.forecast_trend_india(trend='Linear').reset_index(drop=True), None),
            ('CA548:CD594', obj.tm.forecast_trend_india(trend='Degree2').reset_index(drop=True), None),
            ('CI548:CM594', obj.tm.forecast_trend_india(trend='Degree3').reset_index(drop=True), None),
            ('CR548:CT594', obj.tm.forecast_trend_india(trend='Exponential').reset_index(drop=True), None),
            #('DV543:DW591', obj.tm.forecast_trend_india().reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S608:U656', obj.tm.forecast_min_max_sd_eu().reset_index(drop=True), None),
            ('W608:Y656', obj.tm.forecast_low_med_high_eu().reset_index(drop=True), None),
            ('BT612:BV658', obj.tm.forecast_trend_eu(trend='Linear').reset_index(drop=True), None),
            ('CA612:CD658', obj.tm.forecast_trend_eu(trend='Degree2').reset_index(drop=True), None),
            ('CI612:CM658', obj.tm.forecast_trend_eu(trend='Degree3').reset_index(drop=True), None),
            ('CR612:CT658', obj.tm.forecast_trend_eu(trend='Exponential').reset_index(drop=True), None),
            #('DV607:DW653', obj.tm.forecast_trend_eu().reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ('S673:U721', obj.tm.forecast_min_max_sd_usa().reset_index(drop=True), None),
            ('W673:Y721', obj.tm.forecast_low_med_high_usa().reset_index(drop=True), None),
            ('BT677:BV723', obj.tm.forecast_trend_usa(trend='Linear').reset_index(drop=True), None),
            ('CA677:CD723', obj.tm.forecast_trend_usa(trend='Degree2').reset_index(drop=True), None),
            ('CI677:CM723', obj.tm.forecast_trend_usa(trend='Degree3').reset_index(drop=True), None),
            ('CR677:CT723', obj.tm.forecast_trend_usa(trend='Exponential').reset_index(drop=True), None),
            #('DV672:DW718', obj.tm.forecast_trend_usa().reset_index().loc[:, ['Uear', 'adoption']], None), first year differs
            ]
    return verify


def verify_adoption_data(obj, verify=None):
    """Verified tables in Adoption Data."""
    if verify is None:
        verify = {}
    verify['Adoption Data'] = [
            ('X46:Z94', obj.ad.adoption_min_max_sd_global().reset_index(drop=True), None),
            ('AB46:AD94', obj.ad.adoption_low_med_high_global().reset_index(drop=True), None),
            ('BY50:CA96', obj.ad.adoption_trend_global(trend='Linear').reset_index(drop=True), None),
            ('CF50:CI96', obj.ad.adoption_trend_global(trend='Degree2').reset_index(drop=True), None),
            ('CN50:CR96', obj.ad.adoption_trend_global(trend='Degree3').reset_index(drop=True), None),
            ('CW50:CY96', obj.ad.adoption_trend_global(trend='Exponential').reset_index(drop=True), None),
            #('EA45:EB91', obj.ad.adoption_trend_global().reset_index().loc[:, ['Year', 'adoption']], None),
            ('X106:Z154', obj.ad.adoption_min_max_sd_oecd90().reset_index(drop=True), None),
            ('AB106:AD154', obj.ad.adoption_low_med_high_oecd90().reset_index(drop=True), None),
            ('BY110:CA156', obj.ad.adoption_trend_oecd90(trend='Linear').reset_index(drop=True), None),
            ('CF110:CI156', obj.ad.adoption_trend_oecd90(trend='Degree2').reset_index(drop=True), None),
            ('CN110:CR156', obj.ad.adoption_trend_oecd90(trend='Degree3').reset_index(drop=True), None),
            ('CW110:CY156', obj.ad.adoption_trend_oecd90(trend='Exponential').reset_index(drop=True), None),
            #('EA105:EB151', obj.ad.adoption_trend_oecd90().reset_index().loc[:, ['Year', 'adoption']], None),
            ('X170:Z218', obj.ad.adoption_min_max_sd_eastern_europe().reset_index(drop=True), None),
            ('AB170:AD218', obj.ad.adoption_low_med_high_eastern_europe().reset_index(drop=True), None),
            ('BY174:CA220', obj.ad.adoption_trend_eastern_europe(trend='Linear').reset_index(drop=True), None),
            ('CF174:CI220', obj.ad.adoption_trend_eastern_europe(trend='Degree2').reset_index(drop=True), None),
            ('CN174:CR220', obj.ad.adoption_trend_eastern_europe(trend='Degree3').reset_index(drop=True), None),
            ('CW174:CY220', obj.ad.adoption_trend_eastern_europe(trend='Exponential').reset_index(drop=True), None),
            #('EA169:EB217', obj.ad.adoption_trend_eastern_europe().reset_index().loc[:, ['Year', 'adoption']], None),
            ('X233:Z281', obj.ad.adoption_min_max_sd_asia_sans_japan().reset_index(drop=True), None),
            ('AB233:AD281', obj.ad.adoption_low_med_high_asia_sans_japan().reset_index(drop=True), None),
            ('BY237:CA283', obj.ad.adoption_trend_asia_sans_japan(trend='Linear').reset_index(drop=True), None),
            ('CF237:CI283', obj.ad.adoption_trend_asia_sans_japan(trend='Degree2').reset_index(drop=True), None),
            ('CN237:CR283', obj.ad.adoption_trend_asia_sans_japan(trend='Degree3').reset_index(drop=True), None),
            ('CW237:CY283', obj.ad.adoption_trend_asia_sans_japan(trend='Exponential').reset_index(drop=True), None),
            #('EA232:EB278', obj.ad.adoption_trend_asia_sans_japan().reset_index().loc[:, ['Year', 'adoption']], None),
            ('X296:Z344', obj.ad.adoption_min_max_sd_middle_east_and_africa().reset_index(drop=True), None),
            ('AB296:AD344', obj.ad.adoption_low_med_high_middle_east_and_africa().reset_index(drop=True), None),
            ('BY300:CA346', obj.ad.adoption_trend_middle_east_and_africa(trend='Linear').reset_index(drop=True), None),
            ('CF300:CI346', obj.ad.adoption_trend_middle_east_and_africa(trend='Degree2').reset_index(drop=True), None),
            ('CN300:CR346', obj.ad.adoption_trend_middle_east_and_africa(trend='Degree3').reset_index(drop=True), None),
            ('CW300:CY346', obj.ad.adoption_trend_middle_east_and_africa(trend='Exponential').reset_index(drop=True), None),
            #('EA295:EB341', obj.ad.adoption_trend_middle_east_and_africa().reset_index().loc[:, ['Year', 'adoption']], None),
            ('X359:Z407', obj.ad.adoption_min_max_sd_latin_america().reset_index(drop=True), None),
            ('AB359:AD407', obj.ad.adoption_low_med_high_latin_america().reset_index(drop=True), None),
            ('BY363:CA409', obj.ad.adoption_trend_latin_america(trend='Linear').reset_index(drop=True), None),
            ('CF363:CI409', obj.ad.adoption_trend_latin_america(trend='Degree2').reset_index(drop=True), None),
            ('CN363:CR409', obj.ad.adoption_trend_latin_america(trend='Degree3').reset_index(drop=True), None),
            ('CW363:CY409', obj.ad.adoption_trend_latin_america(trend='Exponential').reset_index(drop=True), None),
            #('EA358:EB404', obj.ad.adoption_trend_latin_america().reset_index().loc[:, ['Year', 'adoption']], None),
            ('X422:Z470', obj.ad.adoption_min_max_sd_china().reset_index(drop=True), None),
            ('AB422:AD470', obj.ad.adoption_low_med_high_china().reset_index(drop=True), None),
            ('BY426:CA472', obj.ad.adoption_trend_china(trend='Linear').reset_index(drop=True), None),
            ('CF426:CI472', obj.ad.adoption_trend_china(trend='Degree2').reset_index(drop=True), None),
            ('CN426:CR472', obj.ad.adoption_trend_china(trend='Degree3').reset_index(drop=True), None),
            ('CW426:CY472', obj.ad.adoption_trend_china(trend='Exponential').reset_index(drop=True), None),
            #('EA421:EB467', obj.ad.adoption_trend_china().reset_index().loc[:, ['Year', 'adoption']], None),
            ('X486:Z534', obj.ad.adoption_min_max_sd_india().reset_index(drop=True), None),
            ('AB486:AD534', obj.ad.adoption_low_med_high_india().reset_index(drop=True), None),
            ('BY490:CA536', obj.ad.adoption_trend_india(trend='Linear').reset_index(drop=True), None),
            ('CF490:CI536', obj.ad.adoption_trend_india(trend='Degree2').reset_index(drop=True), None),
            ('CN490:CR536', obj.ad.adoption_trend_india(trend='Degree3').reset_index(drop=True), None),
            ('CW490:CY536', obj.ad.adoption_trend_india(trend='Exponential').reset_index(drop=True), None),
            #('EA485:EB531', obj.ad.adoption_trend_india().reset_index().loc[:, ['Year', 'adoption']], None),
            ('X550:Z598', obj.ad.adoption_min_max_sd_eu().reset_index(drop=True), None),
            ('AB550:AD598', obj.ad.adoption_low_med_high_eu().reset_index(drop=True), None),
            ('BY554:CA600', obj.ad.adoption_trend_eu(trend='Linear').reset_index(drop=True), None),
            ('CF554:CI600', obj.ad.adoption_trend_eu(trend='Degree2').reset_index(drop=True), None),
            ('CN554:CR600', obj.ad.adoption_trend_eu(trend='Degree3').reset_index(drop=True), None),
            ('CW554:CY600', obj.ad.adoption_trend_eu(trend='Exponential').reset_index(drop=True), None),
            #('EA549:EB595', obj.ad.adoption_trend_eu().reset_index().loc[:, ['Year', 'adoption']], None),
            ('X615:Z663', obj.ad.adoption_min_max_sd_usa().reset_index(drop=True), None),
            ('AB615:AD663', obj.ad.adoption_low_med_high_usa().reset_index(drop=True), None),
            ('BY619:CA665', obj.ad.adoption_trend_usa(trend='Linear').reset_index(drop=True), None),
            ('CF619:CI665', obj.ad.adoption_trend_usa(trend='Degree2').reset_index(drop=True), None),
            ('CN619:CR665', obj.ad.adoption_trend_usa(trend='Degree3').reset_index(drop=True), None),
            ('CW619:CY665', obj.ad.adoption_trend_usa(trend='Exponential').reset_index(drop=True), None),
            #('EA614:EB660', obj.ad.adoption_trend_usa().reset_index().loc[:, ['Year', 'adoption']], None),
            ]
    return verify


def verify_custom_adoption(obj, verify=None):
        """Verified tables in Custom * Adoption.
              Note: regional data is ignored as there are issues in the xls sheet that have
              not been replicated. See documentation of issues here:
              https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.kjrqk1o5e46m
              """
        if verify is None:
            verify = {}
        verify['Custom PDS Adoption'] = [
                ('A23:B71', obj.pds_ca.adoption_data_per_region()['World'].reset_index(), None)
        ]
        # verify['Custom REF Adoption'] = []  # not yet implemented
        return verify


def verify_adoption_data_eleven_sources(obj, verify=None):
    """Verified tables in Adoption Data.

          Some solutions, first noticed with ImprovedCookStoves, have a smaller set of
          columns to hold data sources and this shifts all of the rest of the columns to
          the left. This test specifies the columns for this narrower layout.
    """
    if verify is None:
        verify = {}
    verify['Adoption Data'] = [
            ('S46:U94', obj.ad.adoption_min_max_sd_global().reset_index(drop=True), None),
            ('W46:Y94', obj.ad.adoption_low_med_high_global().reset_index(drop=True), None),
            ('BT50:BV96', obj.ad.adoption_trend_global(trend='Linear').reset_index(drop=True), None),
            ('CA50:CD96', obj.ad.adoption_trend_global(trend='Degree2').reset_index(drop=True), None),
            ('CI50:CM96', obj.ad.adoption_trend_global(trend='Degree3').reset_index(drop=True), None),
            ('CR50:CT96', obj.ad.adoption_trend_global(trend='Exponential').reset_index(drop=True), None),
            #('DV45:DW91', obj.ad.adoption_trend_global().reset_index().loc[:, ['Year', 'adoption']], None),
            ]
    return verify


def verify_logistic_s_curve(obj, verify=None):
    """Verified tables in S-Curve Adoption."""
    if verify is None:
        verify = {}
    verify['S-Curve Adoption'] = [
            ('A24:K70', obj.sc.logistic_adoption().reset_index(), None),
            ]
    return verify


def verify_bass_diffusion_s_curve(obj, verify=None):
    """Verified tables in S-Curve Adoption."""
    if verify is None:
        verify = {}
    verify['S-Curve Adoption'] = [
            ('A130:K176', obj.sc.bass_diffusion_adoption().reset_index(), None),
            ]
    return verify



def verify_unit_adoption_calculations(obj, verify=None, include_regional_data=True,
                soln_type='RRS'):
    """Verified tables in Unit Adoption Calculations."""
    if verify is None:
        verify = {}

    if hasattr(obj, 'tm'):
        ref_tam_mask = obj.tm.ref_tam_per_region().reset_index().isna()
        verify['Unit Adoption Calculations'] = [
                ('A17:K63', obj.tm.ref_tam_per_region().reset_index(), None),
                ('A69:K115', obj.tm.pds_tam_per_region().reset_index(), None)]
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

    verify['Unit Adoption Calculations'].extend([
            ('P17:Z63', obj.ua.ref_population().reset_index(), None),
            ('AB17:AL63', obj.ua.ref_gdp().reset_index(), None),
            ('AN17:AX63', obj.ua.ref_gdp_per_capita().reset_index(), None),
            ('P69:Z115', obj.ua.pds_population().reset_index(), None),
            ('AB69:AL115', obj.ua.pds_gdp().reset_index(), None),
            ('AN69:AX115', obj.ua.pds_gdp_per_capita().reset_index(), None),
            ('AG199:AQ244', obj.ua.soln_ref_new_iunits_reqd().reset_index(), None),
            ('B252:L298', obj.ua.soln_net_annual_funits_adopted().reset_index(), regional_mask),
            ('Q252:AA298', obj.ua.conv_ref_tot_iunits().reset_index(), ref_tam_mask),
    ])

    if soln_type == 'RRS':
            pds_cumulative_funit_mask = regional_mask if regional_mask is not None else "Excel_NaN"
            # Some solutions, notably HighSpeedRail, have regional results which drop to near zero
            # for a year and then bounce back. The ~0 results are the result of catastrophic
            # subtraction with only a few bits of precision, not close enough for pytest.approx.
            # Just mask those cells off.
            s = obj.ua.soln_ref_cumulative_funits().reset_index()
            soln_ref_cumulative_funits_mask = s.mask(s < 1e-11, other=True).where(s < 1e-11, other=False)
            verify['Unit Adoption Calculations'].extend([
                    ('BA17:BK63', obj.ua.ref_tam_per_capita().reset_index(), None),
                    ('BM17:BW63', obj.ua.ref_tam_per_gdp_per_capita().reset_index(), None),
                    ('BY17:CI63', obj.ua.ref_tam_growth().reset_index(), None),
                    ('BA69:BK115', obj.ua.pds_tam_per_capita().reset_index(), None),
                    ('BM69:BW115', obj.ua.pds_tam_per_gdp_per_capita().reset_index(), None),
                    ('BY69:CI115', obj.ua.pds_tam_growth().reset_index(), None),
                    #('B135:L181' tested in 'Helper Tables'!C91)
                    ('Q135:AA181', obj.ua.soln_pds_cumulative_funits().reset_index(), pds_cumulative_funit_mask),
                    ('AX136:BH182', obj.ua.soln_pds_tot_iunits_reqd().reset_index(), regional_mask),
                    ('AG137:AQ182', obj.ua.soln_pds_new_iunits_reqd().reset_index(), regional_mask),
                    #('BN136:BS182', obj.ua.soln_pds_big4_iunits_reqd().reset_index(), None),
                    #('B198:L244' tested in 'Helper Tables'!C27)
                    ('Q198:AA244', obj.ua.soln_ref_cumulative_funits().reset_index(), soln_ref_cumulative_funits_mask),
                    ('AX198:BH244', obj.ua.soln_ref_tot_iunits_reqd().reset_index(), None),
                    ('AG253:AQ298', obj.ua.conv_ref_new_iunits().reset_index(), regional_mask),
                    ('AX252:BH298', obj.ua.conv_ref_annual_tot_iunits().reset_index(), regional_mask),
                    ('B308:L354', obj.ua.soln_pds_net_grid_electricity_units_saved().reset_index(), regional_mask),
                    ('Q308:AA354', obj.ua.soln_pds_net_grid_electricity_units_used().reset_index(), regional_mask),
                    ('AD308:AN354', obj.ua.soln_pds_fuel_units_avoided().reset_index(), regional_mask),
                    ('AT308:BD354', obj.ua.soln_pds_direct_co2_emissions_saved().reset_index(), regional_mask),
                    ('BF308:BP354', obj.ua.soln_pds_direct_ch4_co2_emissions_saved().reset_index(), regional_mask),
                    ('BR308:CB354', obj.ua.soln_pds_direct_n2o_co2_emissions_saved().reset_index(), regional_mask),
                    ])
    elif soln_type == 'LAND_PROTECT':
            verify['Unit Adoption Calculations'].extend([
                    ('CG136:CH182', obj.ua.pds_cumulative_degraded_land_unprotected().loc[:, 'World'].reset_index(), None),
                    #('CZ136:DA182', Not implemented
                    ('DR136:DS182', obj.ua.pds_total_undegraded_land().loc[:, 'World'].reset_index(), None),
                    ('EI136:EJ182', obj.ua.pds_cumulative_degraded_land_protected().loc[:, 'World'].reset_index(), None),
                    ('CG198:CH244', obj.ua.ref_cumulative_degraded_land_unprotected().loc[:, 'World'].reset_index(), None),
                    #('CZ198:DA244', Not implemented
                    ('DR198:DS244', obj.ua.ref_total_undegraded_land().loc[:, 'World'].reset_index(), None),
                    ('EI198:EJ244', obj.ua.ref_cumulative_degraded_land_protected().loc[:, 'World'].reset_index(), None),
                    ('B252:C298', obj.ua.net_annual_land_units_adopted().loc[:, 'World'].reset_index(), None),
                    ('Q252:R298', obj.ua.conv_ref_tot_iunits().loc[:, 'World'].reset_index(), None),
                    ('AG253:AH298', obj.ua.conv_ref_new_iunits().loc[:, 'World'].reset_index(), None),
                    #('BO252:BP298', Not implemented
                    ('CG252:CH298', obj.ua.annual_reduction_in_total_degraded_land().loc[:, 'World'].reset_index(), None),
                    #('CZ252:DA298', Not implemented
                    ('DR252:DS298', obj.ua.cumulative_reduction_in_total_degraded_land().loc[:, 'World'].reset_index(), None),
                    ('EI252:EJ298', obj.ua.net_land_units_after_emissions_lifetime().loc[:, 'World'].reset_index(), None),
                    ('B308:C354', obj.ua.soln_pds_net_grid_electricity_units_saved().loc[:, 'World'].reset_index(), regional_mask),
                    ('Q308:R354', obj.ua.soln_pds_net_grid_electricity_units_used().loc[:, 'World'].reset_index(), regional_mask),
                    ('AD308:AE354', obj.ua.soln_pds_fuel_units_avoided().loc[:, 'World'].reset_index(), regional_mask),
                    ('AT308:AU354', obj.ua.direct_co2eq_emissions_saved_land().loc[:, 'World'].reset_index(), None),
                    ('BF308:BG354', obj.ua.direct_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None),
                    ('BR308:BS354', obj.ua.direct_n2o_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None),
                    ('CD308:CE354', obj.ua.direct_ch4_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None),
                    ])
    elif soln_type == 'LAND_BIOSEQ':
            verify['Unit Adoption Calculations'].extend([
                    ('EH137:EI182', obj.ua.soln_pds_annual_land_area_harvested().loc[:, 'World'].reset_index(), None),
                    ('EI253:EJ298', obj.ua.net_land_units_after_emissions_lifetime().loc[2015:, 'World'].reset_index(), None),
                    ('B308:C354', obj.ua.soln_pds_net_grid_electricity_units_saved().loc[:, 'World'].reset_index(), regional_mask),
                    ('Q308:R354', obj.ua.soln_pds_net_grid_electricity_units_used().loc[:, 'World'].reset_index(), regional_mask),
                    ('AD308:AE354', obj.ua.soln_pds_fuel_units_avoided().loc[:, 'World'].reset_index(), regional_mask),
                    ('AT308:AU354', obj.ua.direct_co2eq_emissions_saved_land().loc[:, 'World'].reset_index(), None),
                    ('BF308:BG354', obj.ua.direct_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None),
                    ('BR308:BS354', obj.ua.direct_n2o_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None),
                    ('CD308:CE354', obj.ua.direct_ch4_co2_emissions_saved_land().loc[:, 'World'].reset_index(), None),
                    ])
    return verify


def verify_helper_tables(obj, verify=None, include_regional_data=True):
    """Verified tables in Helper Tables."""
    if verify is None:
        verify = {}
    verify['Helper Tables'] = [
            ('B27:L73', obj.ht.soln_ref_funits_adopted().reset_index(), None),
            ]

    if include_regional_data:
            verify['Helper Tables'].append(
                    ('B91:L137', obj.ht.soln_pds_funits_adopted().reset_index(), None))
    else:
            verify['Helper Tables'].append(
                    ('B91:C137', obj.ht.soln_pds_funits_adopted().loc[:, 'World'].reset_index(), None))
    return verify


def verify_emissions_factors(obj, verify=None):
    """Verified tables in Emissions Factors."""
    if verify is None:
        verify = {}
    verify['Emissions Factors'] = [
            ('A12:K57', obj.ef.conv_ref_grid_CO2eq_per_KWh().reset_index(), None),
            ('A67:K112', obj.ef.conv_ref_grid_CO2_per_KWh().reset_index(), None),
            ]
    return verify


def verify_first_cost(obj, verify=None):
    """Verified tables in First Cost."""
    if verify is None:
        verify = {}

    verify['First Cost'] = [
            ('C37:C82', obj.fc.soln_pds_install_cost_per_iunit().loc[2015:].to_frame().reset_index(drop=True), "Excel_one_cent"),
            #('D37:D82', checked by 'Unit Adoption Calculations'!AH137
            ('E37:E82', obj.fc.soln_pds_annual_world_first_cost().loc[2015:].to_frame().reset_index(drop=True), "Excel_one_cent"),
            ('F37:F82', obj.fc.soln_pds_cumulative_install().loc[2015:].to_frame().reset_index(drop=True), "Excel_one_cent"),
            ('L37:L82', obj.fc.soln_ref_install_cost_per_iunit().loc[2015:].to_frame().reset_index(drop=True), "Excel_one_cent"),
            #('M37:M82', checked by 'Unit Adoption Calculations'!AH199
            ('N37:N82', obj.fc.soln_ref_annual_world_first_cost().loc[2015:].to_frame().reset_index(drop=True), "Excel_one_cent"),
            ('O37:O82', obj.fc.conv_ref_install_cost_per_iunit().loc[2015:].to_frame().reset_index(drop=True), "Excel_one_cent"),
            #('P37:P82', checked by 'Unit Adoption Calculations'!AH253
            ('Q37:Q82', obj.fc.conv_ref_annual_world_first_cost().loc[2015:].to_frame().reset_index(drop=True), "Excel_one_cent"),
            ('R37:R82', obj.fc.ref_cumulative_install().loc[2015:].to_frame().reset_index(drop=True), "Excel_one_cent")
            ]
    return verify


def verify_operating_cost(obj, verify=None):
    """Verified tables in Operating Cost."""
    if verify is None:
        verify = {}

    # This has been a pain point: the last year of each column in the annual_breakout has a tiny
    # remaining_lifetime which is the result of catastrophic substraction between the previous
    # values and therefore has only a few bits of precision. pytest.approx() checks for 6 digits,
    # and there aren't enough bits to even meet that requirement.
    #
    # We mask off all cells where the value is less than one cent. We assert that being off by a penny at
    # the end of the equipment lifetime is acceptable.
    s = obj.oc.soln_pds_annual_breakout().reset_index()
    soln_breakout_mask = s.mask(s < 0.01, other=True).where(s < 0.01, other=False)
    s = obj.oc.conv_ref_annual_breakout().reset_index()
    conv_breakout_mask = s.mask(s < 0.01, other=True).where(s < 0.01, other=False)

    verify['Operating Cost'] = [
            ('B262:AV386', obj.oc.soln_pds_annual_breakout().reset_index(), soln_breakout_mask),
            ('B399:AV523', obj.oc.conv_ref_annual_breakout().reset_index(), conv_breakout_mask),
            #('B19:B64', Not implemented
            #('C19:C64', checked by 'Unit Adoption Calculations'!C253
            ('D19:D64', obj.oc.soln_pds_annual_operating_cost().loc[2015:2060].to_frame().reset_index(drop=True), None),
            ('E19:E64', obj.oc.soln_pds_cumulative_operating_cost().loc[2015:2060].to_frame().reset_index(drop=True), None),
            ('F19:F64', obj.oc.soln_pds_new_funits_per_year().loc[2015:, ['World']].reset_index(drop=True), None),
            #('I19:I64', Not implemented
            #('J19:J64', checked by 'Unit Adoption Calculations'!C253
            ('K19:K64', obj.oc.conv_ref_annual_operating_cost().to_frame().reset_index(drop=True), None),
            ('L19:L64', obj.oc.conv_ref_cumulative_operating_cost().to_frame().reset_index(drop=True), None),
            #('B69:B114', equal to D19:D64,
            #('C69:C114', equal to K19:K64,
            ('D69:D114', obj.oc.marginal_annual_operating_cost().to_frame().reset_index(drop=True), None),
            ('B126:B250', obj.oc.soln_marginal_first_cost().to_frame().reset_index(drop=True), None),
            ('C126:C250', obj.oc.soln_marginal_operating_cost_savings().to_frame().reset_index(drop=True), None),
            ('D126:D250', obj.oc.soln_net_cash_flow().to_frame().reset_index(drop=True), None),
            ('E126:E250', obj.oc.soln_net_present_value().to_frame().reset_index(drop=True), None),
            ('I126:I250', obj.oc.soln_vs_conv_single_iunit_cashflow().to_frame().reset_index(drop=True), None),
            ('J126:J250', obj.oc.soln_vs_conv_single_iunit_npv().to_frame().reset_index(drop=True), None),
            #('K126:K250', obj.oc.soln_vs_conv_single_iunit_payback().to_frame().reset_index(drop=True), None),
            #('L126:L250', obj.oc.soln_vs_conv_single_iunit_payback_discounted().to_frame().reset_index(drop=True), None),
            ('M126:M250', obj.oc.soln_only_single_iunit_cashflow().to_frame().reset_index(drop=True), None),
            ('N126:N250', obj.oc.soln_only_single_iunit_npv().to_frame().reset_index(drop=True), None),
            #('O126:O250', obj.oc.soln_only_single_iunit_payback().to_frame().reset_index(drop=True), None),
            #('P126:P250', obj.oc.soln_only_single_iunit_payback_discounted().to_frame().reset_index(drop=True), None),
            ]
    return verify


def verify_co2_calcs(obj, verify=None, shifted=False, include_regional_data=True, is_rrs=True):
    """Verified tables in CO2 Calcs."""
    if verify is None:
        verify = {}

    if include_regional_data == False:
        regional_mask = obj.c2.co2_mmt_reduced().loc[2015:].reset_index()
        regional_mask.loc[:, :] = True
        regional_mask.loc[:, ['Year', 'World']] = False
    else:
        regional_mask = None

    # similar to operating cost, some co2 calcs values are very slightly offset from zero due to
    # floating point errors. We mask the problematic tables when they are close to 0.
    s = obj.c2.co2eq_mmt_reduced().reset_index()
    near_zero_mask = s.mask(s < 0.01, other=True).where(s < 0.01, other=False)
    if regional_mask is not None:
        near_zero_mask = near_zero_mask | regional_mask

    if is_rrs:
        verify['CO2 Calcs'] = [
                ('A235:K280', obj.c2.co2_reduced_grid_emissions().loc[2015:].reset_index(), regional_mask),
                ('R235:AB280', obj.c2.co2_replaced_grid_emissions().loc[2015:].reset_index(), regional_mask),
                ('AI235:AS280', obj.c2.co2_increased_grid_usage_emissions().loc[2015:].reset_index(), regional_mask),
                ('A289:K334', obj.c2.co2eq_reduced_grid_emissions().loc[2015:].reset_index(), regional_mask),
                ('R289:AB334', obj.c2.co2eq_replaced_grid_emissions().loc[2015:].reset_index(), regional_mask),
                ('AI289:AS334', obj.c2.co2eq_increased_grid_usage_emissions().loc[2015:].reset_index(), regional_mask),
                ('A345:K390', obj.c2.co2eq_direct_reduced_emissions().loc[2015:].reset_index(), regional_mask),
                ]

        if shifted:
            # Some spreadsheets have the last two blocks shifted by several cells
            verify['CO2 Calcs'].extend([
                    ('R345:AB390', obj.c2.co2eq_reduced_fuel_emissions().loc[2015:].reset_index(), regional_mask),
                    ('AM345:AW390', obj.c2.co2eq_net_indirect_emissions().loc[2015:].reset_index(), regional_mask)])
        else:
            verify['CO2 Calcs'].extend([
                    ('U345:AE390', obj.c2.co2eq_reduced_fuel_emissions().loc[2015:].reset_index(), regional_mask),
                    ('AP345:AZ390', obj.c2.co2eq_net_indirect_emissions().loc[2015:].reset_index(), regional_mask)])

        verify['CO2 Calcs'].extend([
                ('A10:K55', obj.c2.co2_mmt_reduced().loc[2015:].reset_index(), regional_mask),
                ('A120:AW165', obj.c2.co2_ppm_calculator().loc[2015:].reset_index(), None),
                ('A65:K110', obj.c2.co2eq_mmt_reduced().loc[2015:].reset_index(), regional_mask),
                ('A172:F217', obj.c2.co2eq_ppm_calculator().loc[2015:].reset_index(), None),])

    else:
        verify['CO2 Calcs'] = [
                ('A65:K110', obj.c2.co2eq_mmt_reduced().loc[2015:].reset_index(), near_zero_mask),
                ('A121:G166', obj.c2.co2_sequestered_global().reset_index().drop(columns=['Global Arctic']), None),
                ('A173:AW218', obj.c2.co2_ppm_calculator().loc[2015:].reset_index(), None),
                # CO2 eq table has an N20 column for LAND xls sheets that doesn't appear to be used, so we ignore it
                ('A225:C270', obj.c2.co2eq_ppm_calculator().loc[2015:, ['CO2-eq PPM', 'CO2 PPM']].reset_index(), None),
                ('E225:G270', obj.c2.co2eq_ppm_calculator().loc[2015:, ['CH4 PPB', 'CO2 RF', 'CH4 RF']].reset_index(drop=True),
                        near_zero_mask)
                # All other tables are not implemented as they appear to be all 0
        ]

def verify_ch4_calcs_rrs(obj, verify=None):
    """Verified tables in CH4 Calcs."""
    if verify is None:
        verify = {}
    verify['CH4 Calcs'] = [
            ('A11:K56', obj.c4.ch4_tons_reduced().loc[2015:, :].reset_index(), None),
            ('A65:AW110', obj.c4.ch4_ppb_calculator().loc[2015:, :].reset_index(), None),
            ]
    return verify

def verify_ch4_calcs_land(obj, verify=None):
    """Verified tables in CH4 Calcs."""
    if verify is None:
        verify = {}
    verify['CH4 Calcs'] = [
            ('A13:B58', obj.c4.avoided_direct_emissions_ch4_land().loc[2015:, 'World'].reset_index(), None),
            ('A67:AW112', obj.c4.ch4_ppb_calculator().loc[2015:, :].reset_index(), None),
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

    cell = excel_read_cell_any_scenario(zip_f=zip_f, sheetname='TAM Data', cell='N45')
    print(f'TAM Data:N45 = {cell}')
    if cell == 'Functional Unit':
        verify_tam_data_eleven_sources(obj, verify)
    else:
        verify_tam_data(obj, verify)

    if obj.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
        cell = excel_read_cell_any_scenario(zip_f=zip_f, sheetname='Adoption Data', cell='N45')
        if cell == 'Functional Unit':
            verify_adoption_data_eleven_sources(obj, verify)
        else:
            verify_adoption_data(obj, verify)
    elif obj.ac.soln_pds_adoption_basis == 'Logistic S-Curve':
        verify_logistic_s_curve(obj, verify)
    elif obj.ac.soln_pds_adoption_basis == 'Bass Diffusion S-Curve':
        verify_bass_diffusion_s_curve(obj, verify)

    verify_helper_tables(obj, verify, include_regional_data=include_regional_data)
    verify_emissions_factors(obj, verify)
    verify_unit_adoption_calculations(obj, verify, include_regional_data=include_regional_data,
                    soln_type='RRS')
    verify_first_cost(obj, verify)
    verify_operating_cost(obj, verify)

    cell = excel_read_cell_any_scenario(zip_f=zip_f, sheetname='CO2 Calcs', cell='S343')
    if cell == 'Reduced Fuel Emissions':
        verify_co2_calcs(obj, verify, shifted=True, include_regional_data=include_regional_data)
    else:
        verify_co2_calcs(obj, verify, include_regional_data=include_regional_data)
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
    verify_aez_data(obj, verify)
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
    verify_unit_adoption_calculations(obj, verify, include_regional_data=False, soln_type=soln_type)

    verify_first_cost(obj, verify)
    verify_operating_cost(obj, verify)
    verify_co2_calcs(obj, verify, is_rrs=False, include_regional_data=False)
    verify_ch4_calcs_land(obj, verify)
    return verify


def compare_dataframes(actual_df, expected_df, description='', mask=None):
    """Compare two dataframes and print where they differ."""
    nerrors = 0
    if actual_df.shape != expected_df.shape:
        raise AssertionError(description + '\nDataFrames differ in shape: ' + \
                str(actual_df.shape) + " versus " + str(expected_df.shape))
    (nrows, ncols) = actual_df.shape
    msg = ''
    for r in range(nrows):
        for c in range(ncols):
            if mask is not None:
                mask.iloc[r,c]
            if mask is not None and mask.iloc[r,c]:
                continue
            matches = True
            act = actual_df.iloc[r,c]
            exp = expected_df.iloc[r,c]
            if isinstance(act, str) and isinstance(exp, str):
                matches = (act == exp)
            elif pd.isna(act) or act == '' or act is None or act == 0 or act == pytest.approx(0.0):
                matches = pd.isna(exp) or exp == '' or exp is None or exp == 0 or exp == pytest.approx(0.0)
            elif np.isinf(act):
                matches = pd.isna(exp) or np.isinf(exp)  # Excel #DIV/0! turns into NaN.
            else:
                matches = (act == pytest.approx(exp))
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
        for (cellrange, actual_df, mask) in verify[sheetname]:
            (usecols, skiprows, nrows) = get_pd_read_excel_args(cellrange)
            arcname = f'{scenario}/{sheetname}'
            zip_csv_f = zip_f.open(name=arcname)
            expected_df = pd.read_csv(filepath_or_buffer=zip_csv_f, header=None,
                index_col=None, usecols=usecols, skiprows=skiprows, nrows=nrows)
            if isinstance(mask, str):
                if mask == "Excel_NaN":
                    mask = expected_df.isna()
                elif mask == "Excel_one_cent":
                    # Due to floating point precision, sometimes subtracting identical values for
                    # unit adoption is not zero it is 0.000000000000007105427357601000 which,
                    # when multiplied by a large unit cost, can result in a First Cost of (say) 2.5e-6
                    # instead of the zero which might otherwise be expected.
                    # Mask off values less than one penny.
                    s = expected_df
                    mask = s.mask(s < 0.01, other=True).where(s < 0.01, other=False)
            description = descr_base + sheetname + " " + cellrange
            compare_dataframes(actual_df=actual_df, expected_df=expected_df,
                    description=description, mask=mask)


@pytest.mark.slow
def test_Afforestation_LAND():
    zipfilename = str(solutiondir.joinpath('afforestation', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in afforestation.scenarios.keys():
        obj = afforestation.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_AltCement_RRS():
    zipfilename = str(solutiondir.joinpath('altcement', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in altcement.scenarios.keys():
        obj = altcement.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Airplanes_RRS():
    zipfilename = str(solutiondir.joinpath('airplanes', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in airplanes.scenarios.keys():
        obj = airplanes.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_BikeInfrastructure_RRS():
    zipfilename = str(solutiondir.joinpath('bikeinfrastructure', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in bikeinfrastructure.scenarios.keys():
        obj = bikeinfrastructure.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Bamboo_LAND():
    zipfilename = str(solutiondir.joinpath('bamboo', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in bamboo.scenarios.keys():
        obj = bamboo.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Biochar_RRS():
    zipfilename = str(solutiondir.joinpath('biochar', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in biochar.scenarios.keys():
        obj = biochar.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Biogas_RRS():
    zipfilename = str(solutiondir.joinpath('biogas', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in biogas.scenarios.keys():
        obj = biogas.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Biomass_RRS():
    zipfilename = str(solutiondir.joinpath('biomass', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in biomass.scenarios.keys():
        obj = biomass.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Bioplastic_RRS():
    zipfilename = str(solutiondir.joinpath('bioplastic', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in ['PDS1-33p2050-Feedstock Limit-385MMT (Book Ed.1)']:
        obj = bioplastic.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_BuildingAutomation_RRS():
    zipfilename = str(solutiondir.joinpath('buildingautomation', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in buildingautomation.scenarios.keys():
        obj = buildingautomation.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Carpooling_RRS():
    zipfilename = str(solutiondir.joinpath('carpooling', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in carpooling.scenarios.keys():
        obj = carpooling.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Cars_RRS():
    zipfilename = str(solutiondir.joinpath('cars', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in cars.scenarios.keys():
        obj = cars.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Composting_RRS():
    zipfilename = str(solutiondir.joinpath('composting', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in composting.scenarios.keys():
        obj = composting.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.skip(reason='not working yet')
#E  AssertionError: Solution: Concentrated Solar Power (CSP) Scenario: \
#        PDS-8p2050-Drawdown (Book Ed.1) Adoption Data X359:Z407
#E  DataFrames differ:
#E  Err [8][0] : '2.9834091228442275e-06' != 'nan'
#E  Err [8][2] : '0.0' != '1.2918540451326751e-06'
@pytest.mark.slow
def test_ConcentratedSolar_RRS():
    zipfilename = str(solutiondir.joinpath('concentratedsolar', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in concentratedsolar.scenarios.keys():
        obj = concentratedsolar.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ConservationAgriculture_LAND():
    zipfilename = str(solutiondir.joinpath('conservationagriculture', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in conservationagriculture.scenarios.keys():
        obj = conservationagriculture.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_CoolRoofs_RRS():
    zipfilename = str(solutiondir.joinpath('coolroofs', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in coolroofs.scenarios.keys():
        obj = coolroofs.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_DistrictHeating_RRS():
    zipfilename = str(solutiondir.joinpath('districtheating', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in districtheating.scenarios.keys():
        obj = districtheating.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ElectricBikes_RRS():
    zipfilename = str(solutiondir.joinpath('electricbikes', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in electricbikes.scenarios.keys():
        obj = electricbikes.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ElectricVehicles_RRS():
    zipfilename = str(solutiondir.joinpath('electricvehicles', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in electricvehicles.scenarios.keys():
        obj = electricvehicles.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_FarmlandRestoration_LAND():
    zipfilename = str(solutiondir.joinpath('farmlandrestoration', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in farmlandrestoration.scenarios.keys():
        obj = farmlandrestoration.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ForestProtection_LAND():
    zipfilename = str(solutiondir.joinpath('forestprotection', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in forestprotection.scenarios.keys():
        obj = forestprotection.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Geothermal_RRS():
    zipfilename = str(solutiondir.joinpath('geothermal', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in geothermal.scenarios.keys():
        obj = geothermal.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_GreenRoofs_RRS():
    zipfilename = str(solutiondir.joinpath('greenroofs', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in greenroofs.scenarios.keys():
        obj = greenroofs.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_HeatPumps_RRS():
    zipfilename = str(solutiondir.joinpath('heatpumps', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in heatpumps.scenarios.keys():
        obj = heatpumps.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_HighSpeedRail_RRS():
    zipfilename = str(solutiondir.joinpath('highspeedrail', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in highspeedrail.scenarios.keys():
        obj = highspeedrail.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ImprovedCookStoves_RRS():
    zipfilename = str(solutiondir.joinpath('improvedcookstoves', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in improvedcookstoves.scenarios.keys():
        obj = improvedcookstoves.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_IndigenousPeoplesLand_LAND():
    zipfilename = str(solutiondir.joinpath('indigenouspeoplesland', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in indigenouspeoplesland.scenarios.keys():
        obj = indigenouspeoplesland.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ImprovedRice_LAND():
    zipfilename = str(solutiondir.joinpath('improvedrice', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in improvedrice.scenarios.keys():
        obj = improvedrice.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_InstreamHydro_RRS():
    zipfilename = str(solutiondir.joinpath('instreamhydro', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in instreamhydro.scenarios.keys():
        obj = instreamhydro.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Insulation_RRS():
    zipfilename = str(solutiondir.joinpath('insulation', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in insulation.scenarios.keys():
        obj = insulation.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_IrrigationEfficiency_LAND():
    zipfilename = str(solutiondir.joinpath('irrigationefficiency', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in irrigationefficiency.scenarios.keys():
        obj = irrigationefficiency.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_LandfillMethane_RRS():
    zipfilename = str(solutiondir.joinpath('landfillmethane', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in landfillmethane.scenarios.keys():
        obj = landfillmethane.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_LEDCommercialLighting_RRS():
    zipfilename = str(solutiondir.joinpath('leds_commercial', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in leds_commercial.scenarios.keys():
        obj = leds_commercial.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_LEDResidentialLighting_RRS():
    zipfilename = str(solutiondir.joinpath('leds_residential', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in leds_residential.scenarios.keys():
        obj = leds_residential.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_ManagedGrazing_LAND():
    zipfilename = str(solutiondir.joinpath('managedgrazing', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in managedgrazing.scenarios.keys():
        obj = managedgrazing.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_MassTransit_RRS():
    zipfilename = str(solutiondir.joinpath('masstransit', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in masstransit.scenarios.keys():
        obj = masstransit.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_MicroWind_RRS():
    zipfilename = str(solutiondir.joinpath('microwind', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in microwind.scenarios.keys():
        obj = microwind.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_MultistrataAgroforestry_LAND():
    zipfilename = str(solutiondir.joinpath('multistrataagroforestry', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in multistrataagroforestry.scenarios.keys():
        obj = multistrataagroforestry.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Nuclear_RRS():
    zipfilename = str(solutiondir.joinpath('nuclear', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in nuclear.scenarios.keys():
        obj = nuclear.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_NutrientManagement_LAND():
    zipfilename = str(solutiondir.joinpath('nutrientmanagement', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in nutrientmanagement.scenarios.keys():
        obj = nutrientmanagement.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_OffshoreWind_RRS():
    zipfilename = str(solutiondir.joinpath('offshorewind', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in offshorewind.scenarios.keys():
        obj = offshorewind.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_OnshoreWind_RRS():
    zipfilename = str(solutiondir.joinpath('onshorewind', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in onshorewind.scenarios.keys():
        obj = onshorewind.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Peatlands_LAND():
    zipfilename = str(solutiondir.joinpath('peatlands', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in peatlands.scenarios.keys():
        obj = peatlands.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_PerennialBioenergy_LAND():
    zipfilename = str(solutiondir.joinpath('perennialbioenergy', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in perennialbioenergy.scenarios.keys():
        obj = perennialbioenergy.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_RecycledPaper_RRS():
    zipfilename = str(solutiondir.joinpath('recycledpaper', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in recycledpaper.scenarios.keys():
        obj = recycledpaper.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Refrigerants_RRS():
    zipfilename = str(solutiondir.joinpath('refrigerants', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in refrigerants.scenarios.keys():
        obj = refrigerants.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_RegenerativeAgriculture_LAND():
    zipfilename = str(solutiondir.joinpath('regenerativeagriculture', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in regenerativeagriculture.scenarios.keys():
        obj = regenerativeagriculture.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_RiceIntensification_LAND():
    zipfilename = str(solutiondir.joinpath('riceintensification', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in riceintensification.scenarios.keys():
        obj = riceintensification.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Ships_RRS():
    zipfilename = str(solutiondir.joinpath('ships', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in ships.scenarios.keys():
        obj = ships.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Silvopasture_LAND():
    zipfilename = str(solutiondir.joinpath('silvopasture', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in silvopasture.scenarios.keys():
        obj = silvopasture.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        del verify['CH4 Calcs']
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SmartGlass_RRS():
    zipfilename = str(solutiondir.joinpath('smartglass', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in smartglass.scenarios.keys():
        obj = smartglass.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SmartThermostats_RRS():
    zipfilename = str(solutiondir.joinpath('smartthermostats', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in smartthermostats.scenarios.keys():
        obj = smartthermostats.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SolarHotWater_RRS():
    zipfilename = str(solutiondir.joinpath('solarhotwater', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    # Need to figure out how to handle 'Aggressive, High Growth, early' source in
    # PDS CustomAdoption, which varies according to data coming from UnitAdoption.
    # The checked-in CSV file isa snapshot of the first scenario values.
    for scenario in ['PDS1-25p2050-Low of Custom Scen. (Book Ed.1)']:
        obj = solarhotwater.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SolarRooftop_RRS():
    zipfilename = str(solutiondir.joinpath('solarpvroof', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in solarpvroof.scenarios.keys():
        obj = solarpvroof.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_SolarPVUtility_RRS():
    zipfilename = str(solutiondir.joinpath('solarpvutil', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in solarpvutil.scenarios.keys():
        obj = solarpvutil.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Telepresence_RRS():
    zipfilename = str(solutiondir.joinpath('telepresence', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in telepresence.scenarios.keys():
        obj = telepresence.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_TreeIntercropping_LAND():
    zipfilename = str(solutiondir.joinpath('treeintercropping', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in treeintercropping.scenarios.keys():
        obj = treeintercropping.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_TemperateForests_LAND():
    zipfilename = str(solutiondir.joinpath('temperateforests', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario, ac in temperateforests.scenarios.items():
        if not ac.use_custom_tla:
            # Temperate Forests has a custom TLA very similar to the allocated TLA. Some of the
            # custom adoption data arbitrarily links to the value for World TLA in Advanced Controls,
            # causing them to vary very slightly if 'Use Customized TLA' is switched on. The saved
            # CSV files for Custom PDS Adoption are a snapshot of the avg book version scenario,
            # which uses custom TLA. Thus, we only test scenarios which also use custom TLA. We
            # will figure out how to deal with linked custom adoption values later, although in the
            # case of this solution the values do not change a significant amount anyway (it is
            # questionable whether there is a good reason for having a custom TLA in the first place).
            continue
        obj = temperateforests.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_Trains_RRS():
    zipfilename = str(solutiondir.joinpath('trains', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in trains.scenarios.keys():
        obj = trains.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_TropicalForests_LAND():
    zipfilename = str(solutiondir.joinpath('tropicalforests', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario, ac in tropicalforests.scenarios.items():
        if not ac.use_custom_tla:
            # Tropical Forests has a custom TLA very similar to the allocated TLA. Some of the
            # custom adoption data arbitrarily links to the value for World TLA in Advanced Controls,
            # causing them to vary very slightly if 'Use Customized TLA' is switched on. The saved
            # CSV files for Custom PDS Adoption are a snapshot of the avg book version scenario,
            # which uses custom TLA. Thus, we only test scenarios which also use custom TLA. We
            # will figure out how to deal with linked custom adoption values later, although in the
            # case of this solution the values do not change a significant amount anyway (it is
            # questionable whether there is a good reason for having a custom TLA in the first place).
            continue
        obj = tropicalforests.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)

@pytest.mark.skip(reason='not working yet')
#E  AssertionError: Solution: Tropical Tree Staples Scenario: \
#        PDS-68p2050-Drawdown-PDScustom-avg-Bookedition1 AEZ Data A48:H53
#E  DataFrames differ:
#E  Err [0][1] : '0.7741767271389345' != '0.6403723426998094'
#E  Err [0][3] : '47.486010369393426' != '46.75147627014513'
#E  Err [0][7] : '48.26018709653236' != '47.39184861284495'
#E  Err [1][3] : '19.427374069559573' != '18.710751455339448'
#E  Err [1][7] : '19.427374069559573' != '18.710751455339448'
#E  Err [2][1] : '14.588253243431556' != '5.598240017676885'
#E  Err [2][3] : '18.377241461720473' != '17.698427206190168'
#E  Err [2][7] : '32.965494705152025' != '23.29666722386705'
#E  Err [3][1] : '15.464239719095678' != '8.329095464315026'
#E  Err [3][3] : '52.292101397294076' != '51.52077106665038'
#E  Err [3][7] : '67.75634111638975' != '59.84986653096539'
@pytest.mark.slow
def test_TropicalTreeStaples_LAND():
    zipfilename = str(solutiondir.joinpath('tropicaltreestaples', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in tropicaltreestaples.scenarios.keys():
        obj = tropicaltreestaples.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)

@pytest.mark.slow
def test_Trucks_RRS():
    zipfilename = str(solutiondir.joinpath('trucks', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in trucks.scenarios.keys():
        obj = trucks.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WalkableCities_RRS():
    zipfilename = str(solutiondir.joinpath('walkablecities', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in walkablecities.scenarios.keys():
        obj = walkablecities.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WaterDistribution_RRS():
    zipfilename = str(solutiondir.joinpath('waterdistribution', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in waterdistribution.scenarios.keys():
        obj = waterdistribution.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WaterEfficiency_RRS():
    zipfilename = str(solutiondir.joinpath('waterefficiency', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in waterefficiency.scenarios.keys():
        obj = waterefficiency.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WaveAndTidal_RRS():
    zipfilename = str(solutiondir.joinpath('waveandtidal', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in waveandtidal.scenarios.keys():
        obj = waveandtidal.Scenario(scenario=scenario)
        verify = RRS_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)


@pytest.mark.slow
def test_WomenSmallholders_LAND():
    zipfilename = str(solutiondir.joinpath('womensmallholders', 'testdata', 'expected.zip'))
    zip_f = zipfile.ZipFile(file=zipfilename)
    for scenario in womensmallholders.scenarios.keys():
        obj = womensmallholders.Scenario(scenario=scenario)
        verify = LAND_solution_verify_list(obj=obj, zip_f=zip_f)
        check_excel_against_object(obj=obj, zip_f=zip_f, scenario=scenario, verify=verify)
