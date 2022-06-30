
===>  This file is under construction.  <===

There are two top-level directories that contain the "meat" of the PDME:

* The `model` directory contains the code that 'powers' the solutions, for example code for converting adoption estimates into cost and emissions estimates.
* The `solution` directory contains a subdirectory for each modeled solution, with the solution-specific code and data for that solution.

# How the Modeling code works

TODO


# Anatomy of a Solution

(Reminder: Oceans are actually implemented differently, and this documentation has not been updated to reflect them; the following is accurate for RSS and Land solutions, but not for Ocean solutions.)

## The Scenario Class

Each solution contains of an `__init__.py` file which defines a class named `Scenario` (so the actual class name is like `<solution>.Scenario` for each different solution). *(Almost) all the work of the model is done by the Scenario constructor*.    When a Scenario constructor is called, it is given the "advanced controls" parameter (containing all the settings for the specific scenario) and proceeds to load the various required data and do all the calculation.  The calculation results are stored in the various fields of the resulting object.

The Scenario constructors are almost entirely boilerplate code.  *The variation between solutions lies mostly in the data; not much varies in the solution code.*

There are a couple of caveats:

* There are different boilerplate code for RSS and for Land solutions.  The Electricity sector code also has some small differences.

* For the original translation of the Excel models, the goal was set to reproduce each Excel exactly.  Since the Excel models had drifted from one another, the result is various 'quirks' in the code to match the behavior of different Excel models on a per-solution level.  Over time we expect to remedy these and get rid of the quirks.

* We expect that in the future solution models _will_ vary more, and the class definition of Scenario is where that variation code will go.  A particular solution might have a more complex way of determining adoption, or cost, based on some other input parameters that can be set per-scenario, for example.


## Solution Data

The subdirectories in a solution contain the data that it uses.  The different subdirectories are as follows (note: not every solution contains all directories)

* `ac` which stands for Advanced Controls, contains pre-defined scenarios.  There are usually at least three, always including the most recently published Plausible, Drawdown and Optimum scenarios.
* `ad` stands for Adoption, but in fact contains only one of several different types of adoption data.  The `ad` directory has published sources of adoption prognostications that can be used to derive scenario adoptions.
* `ca_ref_data` / `ca_pds_data`.  'ca' stands for Custom Adoption.  These directories, if present, contain custom adoption data for either the PDS or REF scenarios.  Custom adoptions are simply hard-coded adoption sequences.
* `tam` stands for Totabl Available Market, and contains published sources of information about demand for the product this solution produces.
* `vma_data` contains published sources of information about values of all the scalar parameters that can be defined for this solution.


## Scenario Fields

TODO -- flesh this out:

Primary Data and Analysis Fields:
* ac: Advanced Controls
* ad: (Prognosticated) Adoption Data
* ae: Agro-Ecological Zoning Allocation of the Land
* c2: CO2 Emissions Calculations & FaIR Climate Modeling
* c4: CH4 Emissions Calculations
* ef: Emissions Factors for converting to CO2eq
* fc: First Costs
* ht: Helper Tables (Final merged adoption data)
* n2o: N2O Emissions Calculations
* oc: Operating Cost
* pds_ca: Custom Adoption Data for the Project Drawdown Scenario
* ref_ca: Custom Adoption Data for the Reference Scenario
* sc: Parameters for an S-Curve Adoption
* tla_per_region: Total Land Area for each Drawdown Region
* ua: Unit Adoption (a mix of functions to calculate annual adoption)
* vmas: Variable Meta Analysis Datasets

General Information:
* name
* module_name
* scenario
* units
* base_year


# Creating new Scenarios

One way to create a new scenario is to create a new scenario file and install it in the `ac` directory.   But it is also possible to create a new scenario dynamically.

The factory method `factory.load_scenario` takes two arguments: a solution name and a `scenario` argument, which can take multiple forms.  If it is a string, it is interpreted as the name of a scenario.  But it can also be an `AdvancedControl` object or a plain python dict with the same fields as an AdvancedControl.  AdvancedControl objects are read-only, so to create a modification, you need to create a copy of one as a python dict and make modifications to that.  Putting this together:

```python
    # Get existing scenario parameters
    existing_scenario = factory.load_scenario('some-solution','some-scenario')
    scenario_params = existing_scenario.ac.as_dict()
    
    # Make one or more modifications
    scenario_params['some-ac-field'] = "new value";

    # Create new scenario
    new_scenario = factory.load_scenario('some-solution',scenario_params)
```

Of course, you could also directly read the scenario_params from one of the `ac/` JSON files rather than creating a Scenario object.

It is important to note that the scenario thus created is not permanent, nor is there any built-in way to modify an existing scenario "in place".  You can, however, serialize a scenario/Advanced Control object to a file and add it to the `ac/` directory, or save it to and reload it from any file you choose.

```python
    filename.write_text(json.dumps(scenario_params), encoding='utf-8')
```

Thusfar we can modify any of the scalar parameters of a scenario, but what about Adoption?  Of course you could add new adoption data to the solution adoption data folders (`ad/`, `ca_pds/` and `ca_ref/`), but if you don't want to modify the code, you can also load a custom adoption source from any file.  The `AdvancedControl` object has two fields, `ref_adoption_custom_source` and `pds_adoption_custom_source`.  Either or both of these may be set to filenames from which to read custom adoption data.  The data must be in the same csv format as custom adoptions.
