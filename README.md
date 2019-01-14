# Project Drawdown Model Engine

This is the [Project Drawdown](https://www.drawdown.org/) model engine. This is intended to be a replacement for the series of interconnected Excel spreadsheets currently used by the project to do climate solution modeling. The intention is to create an implementation which will allow us to broaden the use of the climate solution models to policymakers, business leaders, and other decisionmakers and interested parties.

# Getting started

You will need [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Python 3](https://docs.python.org/3/using/index.html) installed.

Get a copy of this source code:

```sh
git clone git@gitlab.com:codeearth/drawdown.git
cd drawdown
```

Create and activate a python virtual environment:

```sh
python3 -m venv venv
. venv/bin/activate
```

Install dependencies:

```sh
pip install -r requirements.txt
```

Start the application:

```sh
FLASK_APP=app.py FLASK_ENV=development flask run
```

Test Query
```sh
curl -H 'Content-Type: application/json' --data "{}" "http://127.0.0.1:5000/solarpvutil"
```

Jupyter Notebook
```sh
./venv/bin/jupyter lab ./solution/solarpvutil/SolarPVUtil.ipynb
```

# Understanding the Drawdown solution models: Reference and Summary

[Documentation of the Excel models](https://gitlab.com/codeearth/drawdown/blob/master/Documentation/Project_Drawdown_Model_Framework_and_Guide.pdf) has been written, as well as a [design doc](https://docs.google.com/document/d/18nUKV-qltsaSD8kZd5gHswQu82Ot9rg19KIU8_eOisY/view) of how we expect the new implementation to be completed. We refer to this development effort as a Remodel, of course.

A model is the computation of three outputs from a large number of inputs. Each of the three outputs is a table with years as rows and regions as columns. The value of a cell in this table is scalar.

The three outputs are:
* CO2 equivalents per year per region
* Cost of solution per year per region
* Functional Units per year per region.

The Functional Unit is a type which varies and might be different for every model. A functional unit is always a good that society needs. For example, it could be Terawatt hours of electricity or person-miles of travel.

Every solution provides a certain number of functional units per year per region, depending on how the much the solution is adopted. For example, rooftop solar provides Terawatt hours of electricity, in proportion to the wattage capacity which is installed. Increased adoption provides increased functional units. It may also bring with it increased CO2 emissions, in a proportion depending on its nature. Rooftop solar produces fewer emissions that burning fossil fuel, for example. Each solution also has costs (potentially negative, or benefits) in proportion to its adoption.

The input to a given model is various data such as costs per installed watt of rooftop solar and the expected adoption of the solution. Additionally, Solutions are typically organized into "low adoption", "medium adoption", and "high adoption" models. Many solutions may use the same model, such as electrical energy as a functional unit.

Each model and functional unit has a notion of a Total Available Market. There is no benefit to install more rooftop solar than the total market for electricity for the globe, for example. The prevents unrealistic optimism on a single solution, for example.

Reaching the drawdown point, where humanity ceases to add greenhouses gases to the atmosphere, will require many solutions to be adopted and to harmonize synergistically.

# Road Map

### Kernel

The four modules below may be thought of as the computational "kernel" of the Drawdown model. The order given is the preferred order and priority of implementation.

1. **Complete Unit Adoption Calculations module**  
   ~~At the end of the code.earth hackathon 9/7/2018, a good start of the Unit Adoption Module had been made but remains to be completed.~~

   The Unit Adoption module was completed Oct 15, 2018.

2. **First Cost module**  
   ~~As with the Unit Adoption module, this should use VBAWEB to push data to the Python code.~~

   ~~Note that this is the first place in the spreadsheets where there are a number of custom variants, where specific models need to replace the implementation with their own. It is strongly recommended that the Python code not try to accommodate this at this point: it will be much more clear what needs to be done when more of the system is moved out of Excel, attempting to design for model specialization too early is likely to over-design for the problem.~~

   The First Cost module was completed Oct 7, 2018.

3. **Operating Cost**  
   ~~This module is similar to the earlier modules, where VBAWEB would push data over to the Python code for processing.~~

   The Operating Cost module was completed Nov 3, 2018.

4. **Continue development by CO2 Calcs**  
   ~~As with earlier modules, this would use the VBAWEB module to push data from the spreadsheet over to Python for processing.~~

   ~~Test cases should check that the numbers match the values computed by the original (unmodified) spreadsheet.~~

   The CO2 Calcs and CH4 Calcs modules were completed Nov 17, 2018.

### Preparing Input

   A lower priority than the kernel modules are the following &quot;input preparation&quot; or &quot;input processing&quot; modules. These are used to, for example, move from convenient units for data entry to standard units for computation, and to perform other input checking and preparation. In a sense the existing spreadsheet still represents a "gold standard" against which you can test. The issue of how to report errors has not been addressed; feel free to design something awesome.

5. **TAM Data**  
   ~~This is the first module which makes extensive use of interpolation, where the source data is not supplied on an annual basis and so the models interpolate between data points. There are three interpolation implementations in the spreadsheet. Python will need to supply similar interpolation facilities.~~

   ~~The Python implementation may not precisely match the original Excel interpolation values to the Nth bit of precision. The researchers can help determine whether the Python interpolation is reasonable.~~

   The different interpolation methods (linear growth, 2nd order polynomial, 3rd order polynomial, and exponential) were completed Nov 4, 2018. The Python result matches the Excel within the normal tolerances for floating point operations.

   The data tables and other calculations supplied by the TAM Data module were implemented Nov 21, 2018.

6. **Adoption Data module with interpolation**  
   ~~This is expected to be similar to the TAM Data tab, and also makes extensive use of interpolation.~~

   The Adoption Data module was completed 11/5/2018.

7. **VMA Variable Meta Analysis**  
   ~~The Variable Meta-Analysis tab provides a variety of calculations which are not handled elsewhere. For example in the various solar solutions like Utility-Scale or Rooftop, the Variable Meta-Analysis module provides estimates of what percentage of overall solar adoption should be applied to each. More than most, the VMA module is customized according to the needs of each inndividual solution. For the Remodel we will supply code to use as building blocks, but expect that much of the Variable Meta Analysis handling will be done as code for individual solutions or classes of solutions.~~

   Implementation of the VMA module was substantially completed 1/7/2019. There will always be more variables to add.

8. **Other data input to be designed**  
   There are other input parameters that may require significant human-centered design. However, we don't believe these should be addressed until the other above modules have been done.

---

### Other Tasks

Tasks which do not fit into an ordered list of things to be completed:

* **Dashboard**  
   The ultimate goal of this project is to produce a compelling, browser-delivered GUI. There are at least three mostly distinct audiences:
   + Researchers who want to work with the models, add data sources, etc.
   + Policy makers and deciders, who need tools to help guide effective use of resources.
   + Interested parties and the general public, to evangelize that there *are* solutions to global warming.

   As of 1/2019, UI work has focussed on the first point about the audience of researchers. This need is expected to be met using [Jupyter Notebook](https://jupyter.org), eventually hosted via an instance of [JupyterHub](https://jupyter.org/hub). An early version of this UI is available on [mybinder.org](https://mybinder.org/v2/gl/codeearth%2Fdrawdown/master?urlpath=lab/tree/solution/solarpvutil/SolarPVUtil.ipynb).

* **Data Pipeline Hook Strategy**  
   &quot;Specialization&quot; is mentioned above as being an issue starting with the First Cost tab, where individual models have often needed to supply their own implementations and formulae. Though it is recommended that a design for this not be started too early so as to benefit from the understanding gained as the system is constructed, it will nonetheless have to be done at some point.

* **Automated testing**  
   One other goal for the project is to build a model implementation with good coverage by automated tests. There is a [YouTube video which demonstrates the three layers of tests](https://youtu.be/ipZrQWuMU3w) and another which [focuses on the Excel-based system test specifically](https://youtu.be/HLL7HrFcmjc).

   Tests are being constructed at three layers:
    1. unit tests of each function
    2. an integration test which starts the webserver and runs test cases
    3. a system test which starts Excel to compare the original, unmodified spreadsheet to the results from the new implementation

---

# License
This program (excluding the Excel code) is part of the &lt;code&gt;/earth project. The &lt;code&gt;/earth DD Model Engine is licensed under the GNU Affero General Public license and subject to the license terms in the LICENSE file found in the top-level directory of this distribution and at https://gitlab.com/codeearth/drawdown. No part of this Project, including this file, may be copied, modified, propagated, or distributed except according to the terms contained in the LICENSE file.

The Excel VBA code found in ddexel_models contains [VBA-Web](http://vba-tools.github.io/VBA-Web/) which is released under the MIT License.

The Project Drawdown Excel model file itself will be release under a license which has not yet been decided, but is not released at the time of this writing.

The small bits of code in that model file copyright Robert L. Read are released under the AGPL; since they are tightly integrated with the spreadsheet, they are likely valuable only as examples.

---

# The VBA-Web empowered Excel Spreadsheet

## Goals

The current goal of Project Drawdown and this repository is to liberate the data and model methodology from Microsoft Excel and make it freely transparent and hackable in Python.

## Comparing

However, in order to do this gracefully and iteratively, programmers must be able to check their work.
Until the whole model is computable without Excel, a simple means of testing new Python code implementing ever-greater parts of the model is to compare intermediate with results with those computed by Excel.  Furthermore, at the time of this writing, the easiest way to obtain all data need to compute a model is from within Excel.

In order to make this comparison easier, we have added the [VBA-Web](http://vba-tools.github.io/VBA-Web/) software to our spreadsheet.
(We found the installation of VBA-Web easier to do on a Windows machine than on a Mac.)
This allows us to post data to a web service implemented in Python.  We wrote some specific VBA code to take data from specific tables, send it to the service, retrieve the results in CSV, and place the results in a rectangular range of cells on a special tab.

This allows a programmer to test that the numbers produced by the Python model match the Excel model.


The code is invoked by a button with red lettering: TEST FUNCTIONAL UNIT to be found near cell H247 on the tab "Unit Adoption Calculations" of the spreadsheet.

---

# Contribution

Contributors to the project should submit to the project using the Developer Certificate of Origin. For more information, contact Denton Gentry (dgentry@carboncaptu.re).

# Acknowledgements

Many thanks to the contributors of the &lt;code&gt;earth hackathon held at the Internet Archive on Sept. 5, 6, and 7 of 2018 which began this project. They are: Owen Barton, Denton Gentry, Greg Elin, Henry Poole, Robert L. Read, Stephanie Liu and Richard Stallman, in addition to Project Drawdown scientists and volunteers, Ryan Allard, Catherine Foster, Chad Frischmann, and Nick Peters.

# Contact

Denton Gentry (dgentry@carboncaptu.re) is currently the technical point of contact for this project.
