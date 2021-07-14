# What's in a Solution Anyway?

This file is a quick and dirty introduction / glossary / FAQ to how the solution models work, both in the Excel and python.
This needs to be extended and improved.  We welcome contributions!


## What does a solution model do?

Models calculate the economic cost and greenhouse gas impact of a technology under differing assumptions.  The most important assumption is an estimate of how much the technology is adopted over a time horizon (out to 2050).  Again, the _use_ of the technology is an _input_ to the model, not an output.

The _core inputs_ to a solution are:
 * For RSS models, a "Total Addressable Market" (TAM) and for Land models a "Total Land Allocation" (TLA).  These express the total demand for the technoogy.  For exectricity generation models, it is something like anticipated need for electricity over time.
 * For all models, some form of Adoption is specified as an input.  Adoption is generally specified as a percentage of the TAM/TLA.  That is, the input might include the idea that "solar utilites generate 20% of all the required electricity in the year 2030".   More on how adoptions are modeled below.

In addition to these inputs, each model has other parameters which are used to do the calculations.  For example, for a kind of power generation a parameter would be the cost of building a power plant.  These are captured in VMAs (see below).

The _core results_ of a solution are:
 * The "First Cost" (FC).  This captures the capital expenditure over time
 * The "Operating Cost" (OC).  This captures the ongoing expenses of operating the technology over time.
 * The CO2 emissions resulting from the technology use (C2).  {Need to clarify where this is positive vs. negative.}


## VMAs

The term VMA stands for Variable Meta Analysis.  The idea behind Variable Meta Analysis is to search the available literature for suitable estimates for some specific parameter (such as cost to build a power plant), and record them.   These are always scalar values.  (Sometimes there are VMAs for "growth factors" to allow for variation over time).   A researcher has the option to select from low, high or average of these estimates when doing analysis.

Think of VMA as "parameter of the model".

## RSS vs. Land

RSS (Reduction and Replacement) solutions focus on reducing the demand for some GHG-producing product (e.g. electricity), or on replacing the production with a cleaner method or alternative.

Land solutions may perform RSS-like functions, but they also require land, and usually land of a certain type or climate.

The primary distinction in the models is that RSS models model adoption as a proportion of the TAM, while Land models model adoption as a
proportion of available (suitable) land.


## TAM/TLA and Adoption modeling

Probably the most complex set of interactions in the system take place around deriving the TAM and especially the Adoption for a solution.  The first step is accumulating published data, much like a VMA.  Published estimates are consulted and their data is input into the model (sometimes there are "extra" tabs just for this purpose).  These TAM/Adoption sources are more complex than a VMA in a couple of ways:

 * Sources may be global or regional.  Some sources may contain only global data or only regional, or even only for one specific region.  There's magickery about how to integrate these.   Many solutions have only global data.
 * Sources may publish data for specific time intervals (e.g. an estimate for each decade).  Interpolation is used to turn this into a per-year estimation.  (This is a one-time process that then gets copied into the source data.)
 * Sources are categorized into 'Base', 'Conservative' and 'Ambitous' cases.  This determination is made by whomever enters the data.  Then, during analysis, the researcher can elect to use average data from one of those specific categories, or the average of all of them (ALL SOURCES).

In python these sources will appear in `tam` or `ad` subfolders of the solutions.

It is also possible to specify a "Custom TAM" and/or "Custom Adoption", which amount to simply specifiying the table of data (in python the custom adoptions are stored in the `ca_*` directories.

There are some other even more complex options available for Adoption.  The "Helper Tables" module/tab is the final step of selecting the actual, used Adoption based on all the choices made on other tabs. ==> This is where the actual REF and PDS Adoption are available.

For a researcher using the solution, all the settings they have access to can be found on the 'Advanced Controls' tab (which in python translates to the settings in a scenario file in the ac subdirectory).  These include chosing from available TAM/Adoption options and any parameters that modify them.

{Say something about Adoption as TAM % vs. Unit Adoption.  This is covered pretty well in the general PD docs.}

## REF vs PDS (TAM/Adoption)

There are actually **two** TAMs and **two** Adoptions:  The "Ref" TAM/Adoption and the "PDS" TAM/Adoption.  The Ref version is the TAM/Adoption assuming that "nothing changes" and the "PDS" TAM/Adoption assumes that the technology has some interesting curve of adoption.  The reason for this is that researchers are typically wanting to learn the delta that a solution can have, so the PDS and REF sub-models are the two that are being compared.

## Scenarios

A scenario is a saved computation that includes all the inputs that went in to it, and the outputs that results from it.   It is a snapshot of 
the solution with a certain set of assumptions.   In the python code, these are found in the `ac` subdirectory, in json format.
Each solution includes a set of scenarios that have been designed by Project Drawdown researchers.  In the future, there will be more tools (both in this code and at the UI level) that support browsing/creating/analyzing scenarios.

## How do I change the parameters of the solution?

**In the python system, this is not fully implemented**.  The python code doesn't yet have an interface that allows you to create a new scenario.  It can be faked by using this constructor found in factory_2.  The `j` argument would be a dictionary having the same structure as the scenario files.

```python
        def one_solution_scenarios(solution, j=None):
            """Load the scenarios for a single solution, optionally overriding
            the advanced controls for a single scenario"""
```

Even so, there are scenario parameters that will have no effect because they are solution-specific VMAs that have not been implemented yet.

## Integrations

You may encounter the phrase "integrations" in documentation or, for example, in the names of some scenarios or TAM sources.  Integration is a process theat Project Drawdown uses to model the interactions between multiple solutions.  For example, increased use of bicycles decreases the demand for cars.  We have not yet implemented any of the integration functionality in python yet.