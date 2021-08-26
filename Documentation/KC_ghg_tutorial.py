#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# This document is meant to help teach how to use the Drawdown Solutions Python Model
# and to demonstrate the use of the FaIR model.

# Creator: Kristina Colbert
# Last Updated: May 26, 2021

# Table of Contents:
    # Set up your Python Environment
    # Basic Usage of the Drawdown Model
    # Accessing the Results of a Scenario Run
    # Using the Methane Module
    # Multigas Emissions Reductions
    # FaIR Tutorial
    # Using the FaIR Model within Drawdown




###########----############----############----############----############
# SET UP YOUR PYTHON ENVIRONMENT

# 1. Download the Drawdown Python Code from Github:
   # https://github.com/ProjectDrawdown/solutions
    git clone https://github.com/ProjectDrawdown/solutions.git
    
# This only downloads it to your computer, you'll need to tell Python that it's a
# module that will be called. There are two options:
  # a.) Everytime you open python, you will need to input on the console:
      import sys
      #sys.path.append('/Users/kristinacolbert/Box/Kristina Colbert/Python/solutions')
      sys.path.append('/Users/kristinacolbert/Box/Kristina Colbert/GHG_Accounting/Python/Models/PD_Model/edited_copy/solutions')
  # b.) Alternatively, you can make it permanent within the .bash_profile by 
  # finding your .bash_profile (for me it's located in /Users/kristinacolbert/). 
  # Make sure bash is the prescribed shell. For a Mac you can change this by:
      chsh -s /bin/bash
  # Once you have located your .bash_profile, open it, and add to the end:
      export PYTHONPATH="/Users/kristinacolbert/Box/Kristina Colbert/Python/solutions"
  # c.) If you are using Spyder as an IDE, you can go up to the menu bar and select python. Scroll down to 
        PYTHONPATH manager. From there you can let it know where the solutions module path is located.

# 2. Install the FaIR Simple Climate Model within Python:
   # https://github.com/OMS-NetZero/FAIR
    pip install fair
    
# Now you have the two most important modules installed. There may be a few more you need
# and they are listed in the requirements.txt file within the solutions directory.

# 3. Install required modules:
    cd solutions
    pip install -r requirements.txt
"""       




##########----############----############----############----############
# BASIC USAGE OF THE DRAWDOWN MODEL


# First thing to do is import the solutions module, and more specifically 
# the script called "factory" which will be the "workhorse" of the python code
import solution.factory

# Running the following code will save all the included solutions to a dictionary
# for an easy lookup.
solutions = solution.factory.all_solutions_scenarios()

# If you look at the saved variable "solutions", you'll find a list of solution nicknames
# and each of the possible Project Drawdown Scenarios (PDS) associated with the solution

# A full list can be overwhelming, so to focus on just one let's save Improved Rice
solution1 = solution.factory.one_solution_scenarios("improvedrice")

# For demonstration purposes, we are interested in running the one PDS scenario called
# "PDS-86p2050-Plausible-Custom PDS-Avg" under the Improved Rice solution.
# This is how we will run the single scenario:
rice = solutions["improvedrice"][0](scenario="PDS-86p2050-Plausible-Custom PDS-Avg")

# It should be super quick. So what's happening behind the scenes? 
# Well, the line of code is calling on a specific script. The script is hidden at:
# /solutions/solution/improvedrice/__init__.py 
# About halfway down the "__init__.py" is a line that says "class Scenario:"
# Below that line is all of the subscripts that are being run to produce our results!
# If you're interested in checking out each subscript you can go into the 
# /solutions/model/ directory to check each one out.




##########----############----############----############----############
# ACCESSING THE RESULTS OF A SCENARIO RUN

# How about we check out a few cool results after running our scenario?
# If you are on Spyder, which I recommend you use for your Python IDE software,
# You can double-click on the last saved variable "rice" in the Variable explorer tab
# When the object window opens, there will be a lot of drop down options like 
# "ac", "ad", "ae", "c2", etc.. Each of these is one of those drop down options
# stores the results of the subscripts we were calling in the "__init__.py"

# Not every nickname is descriptive so here is a list of a few important ones:
    # ac: Advanced Controls
    # ad: Adoption Data
    # ae: Agro-Ecological Zoning Allocation of the Land
    # c2: CO2 Emissions Calculations & FaIR Climate Modeling
    # c4: CH4 Emissions Calculations
    # ef: Emissions Factors for converting to CO2eq
    # fc: First Costs
    # ht: Helper Tables
    # n2o: N2O Emissions Calculations
    # name: Naming Convention of the Solution
    # oc: Operating Cost
    # pds_ca: Custom Adoption Data for the Project Drawdown Scenario
    # ref_ca: Custom Adoption Data for the Reference Scenario
    # scenario: Naming Convention of the Scenario
    # solution_category: LAND
    # tla_per_region: Total Land Area for each Drawdown Region
    # ua: Unit Adoption (a mix of functions to calculate annual adoption)
    # units: Units for first cost, functional unit, implementation unit, operating cost
    # vmas: Variable Meta Analysis Datasets
    
# The way to call on these is in the naming convention:
# solutionname.subscriptname.variablename

# Let's explore and practice calling the results, here's one for the operating cost per implementation unit
rice.ac.soln_fixed_oper_cost_per_iunit
# Output: 384.34648706769167

# Sequestration rate
rice.ac.seq_rate_global
# Output: 1.45484

# PDS functional units adopted
rice.ua.soln_pds_funits_adopted
# Output is a dataframe of size (47,10) for each region and year

# Methane (land) emissions avoided in tons-CH4 per year
rice.c4.avoided_direct_emissions_ch4_land()
# Note you need to place the () at the end to make the object callable

# Total CO2eq emission redution in units of MMT
rice_mmt = rice.c2.co2_mmt_reduced()

#--#--#--#--#--#--#--#--#--#--#--#--#--#--#

# For fun let's try making a figure of the CO2eq results
# Import the plotting module called matplotlib
import matplotlib.pyplot as plt

# Setup the figure axes and labels
x = list(range(2014,2061))
fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
ax1.plot(x,rice_mmt['World'], c = "b", label="Drawdown")
ax1.set_ylabel('CO2eq Emission Reductions (MMT)')




##########----############----############----############----############
# USING THE METHANE MODULE 

# Let's load another solution and scenario that is important for 
# reducting methane emissions; Landfill Methane
landfill = solutions["landfillmethane"][0](scenario="PDS-0p2050-Drawdown2020")

# The methane module/subscript is located at:
# /solutions/model/ch4calcs.py

# In this subscript, there are a couple important inputs coming from other subscripts.
# Those inputs include the advanced controls and functional units adopted, and if
# previously calculated, the co2-eq emissions saved.
       # ac
       # soln_net_annual_funits_adopted
       # soln_pds_direct_ch4_co2_emissions_saved

# Take a look at these inputs if you're curious about what they look like:
landfill.ua.soln_net_annual_funits_adopted() # Net Annual Adopted Units
landfill.ua.soln_pds_direct_ch4_co2_emissions_saved() # CO2eq methane avoided
landfill.ac.ch4_co2_per_funit # CO2eq methane emitted per functional unit

#--#--#--#--#--#--#--#--#--#--#--#--#--#--#

# Callable results for the methane module, without relying on CO2eq:

# 1.) CH4 reduced by the RRS (not in CO2eq)
landfill.c4.ch4_tons_reduced()

# 2.) CH4 avoided by the LAND (not in CO2eq), let's use the improved rice solution
rice.c4.avoided_direct_emissions_ch4_land()

# 3.) Annual CH4 avoided or reduced by Land or RRS model (converted into Megatons CH4)
# ** A very useful result. **
landfill.c4.ch4_megatons_avoided_or_reduced()

# 4.) A simple way to calculate the CH4 concentration (in ppb) avoided or reduced
# We don't recommend this calculation method, it is a simplistic concentration calculation
# Using the FaIR model is more accurate
landfill.c4.ch4_ppb_calculator_avoided_or_reduced()
    
#--#--#--#--#--#--#--#--#--#--#--#--#--#--#

# Callable results for the methane module, using CO2eq:
    
# 1.) CO2eq methane reduced (for the RRS model)
# The prior code seems to multiply out the dataset in zeros, no explanation why. 
# We don't recommend using this calculation method.
landfill.c4.ch4_co2eq_tons_reduced()

# 2.) CO2eq methane avoided (for the LAND model), let's use the improved rice solution
rice.c4.avoided_direct_emissions_ch4_co2eq_land()

# 3.) A technically incorrect way to calculate methane concentration based on CO2eq emissions
# We don't recommend this calculation method, but it is saved due to prior coding expertise
# It is also hard-coded into the CO2 Calculations module
landfill.c4.ch4_ppb_calculator()

#--#--#--#--#--#--#--#--#--#--#--#--#--#--#

# For fun let's try making a figure of the CH4 reduction results:
y = landfill.c4.ch4_megatons_avoided_or_reduced()
x = list(range(2014,2061))
fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
ax1.plot(x,y['World'], c = "b", label="Drawdown")
ax1.set_ylabel('CH4 Emission Reductions (Mt-CH4)')




##########----############----############----############----############
# MULTIGAS EMISSIONS REDUCTIONS

emisreduction_annual = landfill.c2.ghg_emissions_reductions_global_annual()
emisreduction_cummulative = landfill.c2.ghg_emissions_reductions_global_cummulative()








##########----############----############----############----############
# FaIR TUTORIAL

# FaIR (Finite-amplitude Impulse Response) Model is a simple climate-carbon cycle
# model written in the python coding language. FaIR takes emissions of greenhouse 
# gases, aerosol and ozone precursors, and converts these into atmospheric
# concentrations, radiative forcing and temperature change.

# First make sure you had installed the FaIR module from the github repository
# pip install fair

# Next load the module
import fair

# Let's also load the "numpy" module for some basic scientific computing tools
# We will nickname this module "np" for shorthand (this is pretty common practice)
import numpy as np

# The "workhorse" of the FaIR python code is the "forward.py" 
# Let's take a very specific function, "fair_scm" built into forward.py and load it
from fair.forward import fair_scm

# Let's also import the Representative Concentration Pathway (RCP) Emissions and load it
# And give it a shorthand name, "emissions"
from fair.RCPs import rcp85
emissions = rcp85.Emissions.emissions

# If you take a look into our new object, emissions, its a big array of 736 rows and 40 columns!
# The first column is year from 1765 to 2500. 
# The subsequent columns are emissions of greenhouse gases and other forcing agents.
# Just to focus on a few in "emissions":
    # Column 0: Year
    # Column 1: Fossil CO2 (Gt-C)
    # Column 2: Other CO2 (Gt-C)
    # Column 3: CH4 (Mt-CH4)
    # Column 4: N2O (Mt-N2O)

# Now the magic happens in one single line! We input the emissions data into the "fair_scm"
# function that we loaded just before.
C,F,T = fair_scm(emissions=emissions)

# The outputs are a tuple of (C, F, T) arrays
    # C: Concentrations (nt, 31) in multigas mode
        # Column 0: CO2
        # Column 1: CH4
        # Column 2: N2O
        # For other columns see: https://github.com/OMS-NetZero/FAIR
    # F: Radiative forcing (nt, 13) in Watts per meter squared
    # T: Temperature change anomaly (nt,) in Celsius
    
# "Behind the curtain" of the fair_scm function a lot of calculations are occuring. Emissions
# are being converted over to increased concentrations. And then concentrations are depleted on
# and annual timestep as "sinks" uptake and reduce atmospheric constituents. On each timestep, the
# radiative forcing or "efficiency at absorbing heat" is being calculated for each ghg or species.
# Once the radiative forcing is calculated for the 39 species, they are aggreagated as a total 
# radiative forcing. The last step calculates the global atmospheric temperature from the total
# forcing.

# A few cool features are built into the FaIR model. For one, the carbon cycle is temperature
# sensitive. As more CO2 stays in the atmosphere, it causes global temperatures to rise. But the
# higher temperatures weaken the carbon sinks of the ocean and land. It becomes harder for the ocean
# and vegetation on the land to absorb/sequester CO2. The FaIR model captures this "positive" feedback

# A second cool feature is the FaIR model is tuned to replicate historic observations of concentrations
# and global temperature.

# And third, it prescribes natural emissions of methane and nitrous oxide. Although, the natural emissions
# timeseries are slightly unusual and unrealistic as they calculated them back from the balance of 
# concentration observations and prescribed historical anthropogenic emissions. This is worth noting as the
# developers are aware of the flawed assumptions.

#--#--#--#--#--#--#--#--#--#--#--#--#--#--#
# Okay so let's have fun and make a plot of the FaIR outputs (C,F,T).

# Setup the plotting area
from matplotlib import pyplot as plt
import pandas as pd
plt.style.use('seaborn-darkgrid')
plt.rcParams['figure.figsize'] = (16, 9)

# Setup an arrry
rcpemissions = pd.DataFrame(emissions, index = range(1765,2501),
                                       columns=['Year','FossilCO2 (Gt-C)', 'OtherCO2 (Gt-C)', 'CH4 (Mt-CH4)',
                                                'N2O (Mt-N2O)', 'SOx (Mt-S)', 'CO (Mt-CO)', 'NMVOC (Mt)',
                                                'NOx (Mt-N)', 'BC (Mt)', 'OC (Mt)', 'NH3 (Mt-N)', 'CF4 (kt)',
                                                'C2F6 (kt)', 'C6F14 (kt)', 'HFC23 (kt)', 'HFC32 (kt)',
                                                'HFC43_10 (kt)', 'HFC125 (kt)', 'HFC134a (kt)', 'HFC143a (kt)',
                                                'HFC227ea (kt)', 'HFC245fa (kt)', 'SF6 (kt)', 'CFC_11 (kt)',
                                                'CFC_12 (kt)', 'CFC_113 (kt)','CFC_114 (kt)','CFC_115 (kt)',
                                                'CARB_TET (kt)', 'MCF (kt)', 'HCFC_22 (kt)', 'HCFC_141B (kt)',
                                                'HCFC_142B (kt)', 'HALON1211 (kt)', 'HALON1202 (kt)', 
                                                'HALON1301 (kt)', 'HALON2404 (kt)', 'CH3BR (kt)', 'CH3CL (kt)'])
rcpemissions.index.name="Year"
result1 = pd.DataFrame({'CO2(ppm)': C[:,0,], 'CH4(ppb)': C[:,1,], 'N2O(ppb)': C[:,2,]}, index=rcp85.Emissions.year)
result1.index.name="Year"
result2 = pd.DataFrame({'CO2(Wm-2)': F[:,0,], 'CH4(Wm-2)': F[:,1,], 'N2O(Wm-2)': F[:,2,], 'others(Wm-2)': np.sum(F, axis=1)-F[:,0,]-F[:,1,]-F[:,2,], 'total(Wm-2)': np.sum(F, axis=1)}, index=rcp85.Emissions.year)
result2.index.name="Year"
result3 = pd.DataFrame({'TempAnomaly(C)': T}, index=rcp85.Emissions.year)
result3.index.name="Year"

# Make the four panel figure of emissions and concentrations
fig = plt.figure()
ax1 = fig.add_subplot(221)
ax1.plot(rcpemissions.index, rcpemissions.iloc[:,3], color='black')
ax1.set_ylabel('CH$_4$ Emissions (Mt-CH$_4$)')
ax2 = fig.add_subplot(222)
ax2.plot(rcpemissions.index, rcpemissions.iloc[:,1], color='blue')
ax2.set_ylabel('CO$_2$ Emissions (Gt-C)')
ax3 = fig.add_subplot(223)
ax3.plot(result2.index, result2.iloc[:,1],  color='orange')
ax3.set_ylabel('CH$_4$ concentrations (ppb)')
ax4 = fig.add_subplot(224)
ax4.plot(result2.index, result2.iloc[:,0],  color='red')
ax4.set_ylabel('CO$_2$ concentrations (ppm)')




##########----############----############----############----############
# USING THE FaIR MODEL WITHIN DRAWDOWN









# Test out the new functionality of the co2calcs.py
landfill.c2.FaIR_CFT_baseline_co2eq()
C3=landfill.c2.FaIR_CFT_baseline_RCP3()[0]
F3=landfill.c2.FaIR_CFT_baseline_RCP3()[1]
T3=landfill.c2.FaIR_CFT_baseline_RCP3()[2]
E3=landfill.c2.FaIR_CFT_baseline_RCP3()[3]

C45=landfill.c2.FaIR_CFT_baseline_RCP45()[0]
F45=landfill.c2.FaIR_CFT_baseline_RCP45()[1]
T45=landfill.c2.FaIR_CFT_baseline_RCP45()[2]
E45=landfill.c2.FaIR_CFT_baseline_RCP45()[3]

C6=landfill.c2.FaIR_CFT_baseline_RCP6()[0]
F6=landfill.c2.FaIR_CFT_baseline_RCP6()[1]
T6=landfill.c2.FaIR_CFT_baseline_RCP6()[2]
E6=landfill.c2.FaIR_CFT_baseline_RCP6()[3]

C85=landfill.c2.FaIR_CFT_baseline_RCP85()[0]
F85=landfill.c2.FaIR_CFT_baseline_RCP85()[1]
T85=landfill.c2.FaIR_CFT_baseline_RCP85()[2]
E85=landfill.c2.FaIR_CFT_baseline_RCP85()[3]

# Plot the default RCPs in the FaIR model
# The Drawdown code will run the default FaIR model
plt.style.use('seaborn-darkgrid')
plt.rcParams['figure.figsize'] = (16, 9)
plt.rcParams['figure.constrained_layout.use'] = True
fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(8, 4))

ax1.plot(C3.index,C3['CO2(ppm)'], c = "green", label="RCP3PD")
ax1.plot(C45.index,C45['CO2(ppm)'], c = "blue",  label="RCP4.5")
ax1.plot(C6.index,C6['CO2(ppm)'], c = "red",  label="RCP6.0")
ax1.plot(C85.index,C85['CO2(ppm)'], c = "black",  label="RCP8.5")
ax1.set_ylabel('CO2 Concentration (ppm)')
ax1.set_xlim([1800, 2100])
ax1.set_ylim([250, 1000])
ax1.legend(loc='upper left');

ax2.plot(C3.index,C3['CH4(ppb)'], c = "green", label="RCP3PD")
ax2.plot(C45.index,C45['CH4(ppb)'], c = "blue",  label="RCP4.5")
ax2.plot(C6.index,C6['CH4(ppb)'], c = "red",  label="RCP6.0")
ax2.plot(C85.index,C85['CH4(ppb)'], c = "black",  label="RCP8.5")
ax2.set_ylabel('CH4 Concentration (ppb)')
ax2.set_xlim([1800, 2100])
ax2.set_ylim([700, 4000])

ax3.plot(T3.index,T3['TempAnomaly(C)'], c = "green", label="RCP3PD")
ax3.plot(T45.index,T45['TempAnomaly(C)'], c = "blue",  label="RCP4.5")
ax3.plot(T6.index,T6['TempAnomaly(C)'], c = "red",  label="RCP6.5")
ax3.plot(T85.index,T85['TempAnomaly(C)'], c = "black",  label="RCP8.5")
ax3.set_ylabel('Temperature Anomaly (C)')
ax3.set_xlim([1800, 2100])
ax3.set_ylim([-2, 6])

C3d=landfill.c2.FaIR_CFT_Drawdown_RCP3()[0]
F3d=landfill.c2.FaIR_CFT_Drawdown_RCP3()[1]
T3d=landfill.c2.FaIR_CFT_Drawdown_RCP3()[2]
E3d=landfill.c2.FaIR_CFT_Drawdown_RCP3()[3]

C45d=landfill.c2.FaIR_CFT_Drawdown_RCP45()[0]
F45d=landfill.c2.FaIR_CFT_Drawdown_RCP45()[1]
T45d=landfill.c2.FaIR_CFT_Drawdown_RCP45()[2]
E45d=landfill.c2.FaIR_CFT_Drawdown_RCP45()[3]

C6d=landfill.c2.FaIR_CFT_Drawdown_RCP6()[0]
F6d=landfill.c2.FaIR_CFT_Drawdown_RCP6()[1]
T6d=landfill.c2.FaIR_CFT_Drawdown_RCP6()[2]
E6d=landfill.c2.FaIR_CFT_Drawdown_RCP6()[3]

C85d=landfill.c2.FaIR_CFT_Drawdown_RCP85()[0]
F85d=landfill.c2.FaIR_CFT_Drawdown_RCP85()[1]
T85d=landfill.c2.FaIR_CFT_Drawdown_RCP85()[2]
E85d=landfill.c2.FaIR_CFT_Drawdown_RCP85()[3]








