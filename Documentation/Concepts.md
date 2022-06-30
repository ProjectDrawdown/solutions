
Click to jump to an phrase or acronym: [AC](#advanced-controls-and-vmas), AEZ, [C2/CO2](#CO2), [C4/CH4](#C4), [CA](#ca), [FC](#FC), [Integration](#integrations), [OC](#OC), [PDS](#ref-vs-pds-tamadoption), [REF](#ref-vs-pds-tamadoption), [RRS](#rrs-vs-land-vs-ocean), [Solution](#what-is-a-solution), [Scenario](#solution-vs-scenario-vs-model), [TAM](#tam-total-addressable-market-and-adoption-modeling), [TLA](#tla), UA, [VMA](#vmas)


# What is a Solution?

In the Project Drawdown Model Engine (PDME), Solutions are models that calculate the economic cost and greenhouse gas impact of a specific technology under differing input assumptions.  Examples of solutions are "Rooftop Solar Energy" or "Mangrove Restoration".  All solutions share a core set of inputs and outputs, and use the same modeling techniques.

The _core inputs_ to a Solution are:
 * A "Total Addressable Market" (TAM) for RRS models, or a <span id="TLA">"Total Land Allocation" (TLA)</span> for Land models.  These express the maximum possible deployment of the technology in question.  For electricity generation models, for example, the TAM is the anticipated demand for electricity over time.  For Land models, the TLA is the total land suitable for the solution.
 * Adoption of the solution.  Adoption is often thought of as a percentage of the TAM/TLA over time.  That is, the input might include the idea that "solar utilities generate 20% of all the required electricity in the year 2030".   More on how adoptions are modeled below.
 * A set of scalar parameters describing things like costs to develop and use each unit of the solution, the effective lifetime of a unit, greenhouse gasses emitted per unit, etc.  These are collectively known as Advanced Controls (AC).

The _core results_ of a Solution are:
 * The <span id="FC">"First Cost" (FC)</span>: the capital expenditure over time given the adoption and other assumptions.
 * The <span id="OC">"Operating Cost" (OC)</span>: the ongoing expenses of operating the technology over time.
 * The <span id="CO2">CO2e emissions</span> or sequestration (C2) resulting from the technology use over time.  Some models also separately compute a <span id="C4">methane emission (C4)</span> result..

While most AC parameters are scalar, other parameters are time sequences, typically out to 2050.   In some solutions, these inputs and outputs may also be provided by region, but for most solutions all inputs and outputs are global.

## Solution vs. Scenario vs. Model

The terms "Solution" and "Model" are sometimes used interchangeably at the conceptual level.  In the code, "Model" refers to the code which is common across all solutions, while "a solution" refers to code that is specific to a particular solution technology.

A Scenario is a set of core inputs to a Solution, and the outputs that result from those inputs.  That is, a Scenario is a specific instance of a Solution for a given set of assumptions.

In this code repository, each Solution comes with a specific set of Scenarios that have been designed and published by Project Drawdown researchers.  These can be used as a starting point for analysis, or for designing new scenarios.


## RRS vs. Land vs. Ocean

RRS (Reduction and Replacement) solutions focus on reducing the demand for some GHG-producing product (e.g. electricity), or on replacing the production of a product with a cleaner method or alternative.

Land solutions may perform RRS-like functions, but their distinguishing characteristic is that they also require land, and usually land of a certain type or climate.

The primary distinction in the models is that RRS models model adoption as a proportion of the TAM, while Land models model adoption as a proportion of available (suitable) land.

Oceans are yet another set of models, similar to Land models, but naturally using ocean areas instead.  Note: The Oceans models have been implemented entirely differently from the Land/RSS models (in fact they are a prototype for the eventual future of all models), so much of the documentation here may not fully apply to them.  See (TBD) for a high-level discussion of the Ocean model implementation.

# TAM (Total Addressable Market) and Adoption modeling

Probably the most complex set of interactions in the system take place around deriving the TAM and Adoption for a solution.  The first step is accumulating published data and demand and/or projected adoption.  Published estimates are consulted and their data is put into individual time sequences, then combined.  Some of the complexities of combination include:

 * Sources may be global or regional.  Some sources may contain only global data or only regional, or even only for one specific region.  There's magickery about how to integrate these.   Many solutions have only global data.
 * Sources may publish data for specific time intervals (e.g. an estimate for each decade vs an estimate for each year).  Interpolation is used to turn all sources into a per-year estimations.  (This is a one-time process that then gets copied into the source data.)
 * Sources are categorized into 'Base', 'Conservative' and 'Ambitious' cases.  This determination is made by whomever enters the data.  Then, during analysis, the researcher can elect to use average data from one of those specific categories, or the average of all of them (ALL SOURCES).
 * Some solutions contain additional constraints to enforce common-sense boundaries (such as adoption must not exceed TAM, or REF scenarios must have less adoption than PDS scenarios (see next section))

 The code to do all these different kinds of combination is part of the modeling shared by all solutions.  The net result is always a TAM (or TLA) sequence out to 2050, and an adoption sequence out to 2050.

 In addition to the published data estimates, some Scenarios may use a <span id="CA">"Custom Adoption" (CA)</span>, which is just a directly specified time-sequence, bypassing all the complexities above.

## REF vs PDS (TAM/Adoption)

In each scenario, there are actually **two** TAMs and **two** Adoptions:  The "Ref" TAM/Adoption and the "PDS" TAM/Adoption.  The Ref version is the TAM/Adoption assuming that "nothing changes" and the "PDS" TAM/Adoption assumes that the technology has some interesting curve of adoption.  

This is a legacy effect of translating the Excel models: in Excel researchers typically want to compare the scenario's unique adoption to the baseline, so they are both represented simultaneously.  In the future we plan to separate these so that there is a single baseline REF scenario for each solution, and comparison can be made between any two scenarios.

## Interpreting levels/cases

There are two kinds of adoption "levels" that are very similar (and highly correlated), but use two different sets of names, which can lead to confusion:

TAM and Adoption _source data_ are always placed on a scale of four different kinds of _cases_:  baseline, conservative, ambitious and 100%.

Adoption curves and Scenarios are sometimes but not always placed on a scale of three: 
 * PD1, aka Plausible: solutions are adopted at a realistically vigorous rate
 * PD2, aka Drawdown: adoption of solutions is optimized to achieve drawdown by 2050.
 * PD3, aka Optimum: solutions achieve their maximum potential.


# Advanced Controls and VMAs

"Advanced Controls" is the collection of parameters that control a solution output.  An assignment of Advanced Controls is essentially the same thing as a scenario.

## VMAs

The term VMA stands for Variable Meta Analysis.  The idea behind Variable Meta Analysis is to search the available literature for suitable estimates for some specific parameter (such as cost to build a power plant), and record them.   These are always scalar values.  (Sometimes there are VMAs for "growth factors" to allow for variation over time).   

A VMA can be thought of as providing a background source for a specific input parameter, or justification for why a particular value was used.  A researcher has the option to select from low, high or average of these estimates when doing analysis.  Most, but not all, scalar Advanced Control parameters will be backed by a corresponding VMA.


# Total Land Area (TLA) and Agroecological Zones (AEZ)

TODO

# First and Operational Costs

TODO

# CO2 and CH4 emission models

TODO

# Integrations

Important note: you don't need to use or understand integrations in order to use or understand solution models.  Integrations are a modeling process that exists outside of/ on top of, the solutions.

Integrations compute interactions between multiple solutions.  The current design of integrations follows the process used by Project Drawdown researchers to update the Excel models in response to new data (e.g. to new climate or population estimates).  There are documents that describe that Excel integration process in detail [find ref].

Each integration covers a single domain, such as electricity generation or buildings.  Each integration may take as input some new assumptions about the world, as well as the output of other, existing, scenarios that alter those assumptions.  An example is that solutions that decrease waste output would decrease the waste available for electricity generation (the biogas solution).

The output of an integration are typically new data files (especially new TAMs) that will be used by the solutions thereafter.

The architecture of integrations in the Python code introduces the concept of an "integration mode".  While in integration mode, all of the solution computations will use the the integration versions of tiles.  This enables multiple integrations to feed off of each other, be modified and run again, as needed, before any of the integrations are "committed".  The final process would be to "accept" the result of all the integrations by moving the temporary integration-mode files to their permanent locations (and making a github commit of the result).  This acceptance part of the process has not been automated yet.

More information can be found in the integrations [README file](https://github.com/ProjectDrawdown/solutions/blob/develop/integrations/_README.md).


# Want to go Deeper?

The files `Drawdown_Model_Platform_Proposal.pdf` and `Drawdown_First_Hackathon_Proposal.pdf` which are historical documents that cover the original python code design in some depth.


<br style="padding-top:3em">
### Note to editors

Include links directly into the code auto-doc _only when there is good content there_.  Conversely, when you write some good autodoc, consider if it should be linked somewhere here.
