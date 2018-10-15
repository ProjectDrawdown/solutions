# Project Drawdown Model Engine

This is the [Project Drawdown](https://www.drawdown.org/) model engine. This is intended to be a replacement for the series of interconnected Excel spreadsheets currently used to do the modeling for project draw down. The intention is to create a framework that will allow us to create command line utility that can be run on the workstations of climate scientists who want to adjust the inputs to the Project Drawdown models.

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
curl -H 'Content-Type: application/json' --data @sample.json 'http://127.0.0.1:5000/unitadoption.v2'
```
# Understanding the Drawdown solution models: Reference and Summary

A formal [documentation](https://gitlab.com/codeearth/drawdown/blob/master/Documentation/Project_Drawdown_Model_Framework_and_Guide.pdf) has been written.
Need reference to Drawdown documentation here. A simplistic summary for the computer programmer is given below.

A model is the computation of three outputs from a large number of inputs. Each of the three outputs is a table which
with years as rows and regions as columns. The value of a cell in this table is scalar.

The three outputs are:
* CO2 equivalents per year per region
* Cost of solution per year per region
* Functional Units per year per region.

The Functional Unit is a type which varies and might be different for every model. A functinal unit is always a good that society needs. For example, it could be Terrawatt hours of electricity or person-miles of travel.

Every solution provides a certain number of functional units per year per region, depending on how the much the solution is adopted. For example, rooftop solar provides Terrawatt hours of electricity, in proportion to the wattage capacity which is installed. Increase adoption provides increased functional units. It may also bring with it increase CO2 emissions, in a proportion depending on its nature. Rooftop solar produces fewer emisions that burning fossil fuel, for example. Each solution also has costs (potentially negative, or benefits) in proportion to its adoption.

The input to a given model is the all of the data, such as costs per installed watt of rooftop solar and the expected adoption of the solutin.

Additionally, Solutions are typically organized into a "low adoption", "medium adoption", and "high adoption" models.

Many models may use the same model, such as electrical energy as a functional unit.

Each model and functional unit has a notion of a Total Available Market. There is no benefit to install more rooftop solar than the total market for electricity for the globe, for example. The prevents unrealistic optimisim on a single solution, for example.

Ultimately, all solutions interact with each and synergize in certain ways which are beyond the scope of the work in this repo.

Reaching the drawdown point, where humanity ceases to add greenhouses gases to the atmosphere, will require many solutions to be adopted working and to harmonize synergistically.

# Road Map

## Introduction and Methodology

This section describes the main pieces of work that need to be done to complete the port of the models from Excel to Python.
We believe each of the four "Model Kernel" pieces below can be done using the same methodology.

First, study the spreadsheets to understand the calculations being done by that tab. When you understand them thoroughly, code them in
Python, hopefully as a separate module and endpoint so that they can be tested independently. Use the numbers in the spreadsheet as a manual test and sanity test of your work.

Then improve the VBA in the spreadsheet to send data directly to your webservice endpoint from Excel and configure it to put the
resulting tables on a "test tab". This will take some simple programming, but it WILL be in VBA, and therefore perhaps difficult.

When you are fully satisfied, figure out how to chain your piece togeother in pipeline with other pieces (in Python) and then
perform a full "integration test" to make sure the numbers still match.

Feel free to contact other developers here for advice and questions and code review (a tech lead has not yet been chosen, so contact Robert L. Read until that is done.)

### Kernel

The four modules below may be thought of as the computational "kernel" of the Drawdown model. The order given is the preferred order and priority of implementation.

1. **Complete Unit Adoption Calculations module**  
   ~At the end of the code.earth hackathon 9/7/2018, a good start of the Unit Adoption Module had been made but remains to be completed.~
   The Unit Adoption module was completed 10/15/2018.

2. **First Cost module**  
   ~As with the Unit Adoption module, this should use VBAWEB to push data to the Python code.~

   ~Note that this is the first place in the spreadsheets where there are a number of custom variants, where specific models need to replace the implementation with their own. It is strongly recommended that the Python code not try to accommodate this at this point: it will be much more clear what needs to be done when more of the system is moved out of Excel, attempting to design for model specialization too early is likely to over-design for the problem.~

   The First Cost module was completed 10/7/2018.

3. **Operating Cost**  
   This module is similar to the earlier modules, where VBAWEB would push data over to the Python code for processing.

4. **Continue development by CO2 Calcs**  
   As with earlier modules, this would use the VBAWEB module to push data from the spreadsheet over to Python for processing.

   Test cases should check that the numbers match the values computed by the original (unmodified) spreadsheet.

### Preparing Input

   A lower priority than the kernel modules are the following &quot;input preparation&quot; or &quot;input processing&quot; modules. These are used to, for example, move from convenient units for data entry to standard units for computation, and to perform other input checking and preparation. In a sense the existing spreadsheet still represents a "gold standard" against which you can test. The issue of how to report errors has not been addressed; feel free to design something awesome.

5. **TAM Data tab**  
   This is the first module which makes extensive use of interpolation, where the source data is not supplied on an annual basis and so the models interpolate between data points. There are three interpolation implementations in the spreadsheet. Python will need to supply similar interpolation facilities.

   The Python implementation may not precisely match the original Excel interpolation values to the Nth bit of precision. The researchers can help determine whether the Python interpolation is reasonable.

6. **Adoption Data module with interpolation**  
   This is expected to be similar to the TAM Data tab, and also makes extensive use of interpolation.

7. **VMA Variable Meta Analysis**  
   This is far enough in the future that we are less confident that this will really be the thing to tackle next. The plan will evolve as it goes along.

8. **Other data input to be designed**  
   There are other input parameters that may require significant human-centered design. However, we don't believe these should be addressed until the other above modules have been done.

---

### Other Tasks

Tasks which do not fit into an ordered list of things to be completed:

* Dashboard  
   The ultimate goal of this project is to produce a compelling, browser-delivered GUI that will be made available to all researchers and policy makers and the general public to understand the solutions proposed by project drawdown.

   A mockup of such an interface has been produced in Java [Need to get link from Chad.]

   This work can be usefully divided into two parts, the output, which is a higher priority, which could perform the same functionality as the current spreadsheet, but perhaps much better. The second priority is to allow all inputs to be entered. This is a design task which has not yet been undertaken. Once again the spreadsheets serve as starting point for this work.

   An output media, for CO2 and Adoption and other results. There is a mockup of an interface which was shown on 9/6/2018, this should be linked from here.

   Consider using D3 or other Javascript charting packages to implement this.

* Data Pipeline Hook Strategy  
   &quot;Specialization&quot; is mentioned above as being an issue starting with the First Cost tab, where individual models have often needed to supply their own implementations and formulae. Though it is recommended that a design for this not be started too early so as to benefit from the understanding gained as the system is constructed, it will nonetheless have to be done at some point.

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
Until the whole model is computable without Excel, an simple means of testing new Python code implementing ever-greater parts of the model is to compare intermediate with results with those computed by Excel.  Furthermore, at the time of this writing, the easiest way to obtain all data need to compute a model is from within Excel.

In order to make this comparison easier, we have added the [VBA-Web](http://vba-tools.github.io/VBA-Web/) software to our spreadsheet.
(We found the installation of VBA-Web easier to do on a Windows machine than on a Mac.)
This allows us to post data to a web service implemented in Python.
We wrote some specific VBA code to take data from specific tables, convert it to CSV, send it to the service,
retrieve the results in CSV, and place the results in a rectangular range of cells on a special tab.

This allows a programmer to test that the numbers produced by the Python model match the Excel model. The particular tab is named "ExtModelCfg".

## Configuration

The ExtModelCfg tab allows a number of important parameters to be set by a user without having to modify VBA. The include flags that that allow you to test locally or remotely, a rudimentary debug level, and the URLs to reach a server hosting the Python web service.

Additionally, the "ranges" for the input data and the range of the output data are specified here.

## Code

Because the VBA editor for a Mac does not appear to allow a module name to be changed, the webservice code is in a module named "Module 2". The code is straightfoward and was written by an inexpert VBA programmer; you may be able to offer improvements. This code can presumably be easily adopted to test the next, or additional, transfers of functionality to Python. The subroutines are completely parameterized and therefore reusable.

## Use

The code is invoked by a button with red lettering: TEST FUNCTIONAL UNIT to be found near cell H247 on the tab "Unit Adoption Calculations" of the spreadsheet.

---

# Contribution

Contributors to the project should submit to the project using the Developer Certificate of Origin. For more information, contact Denton Gentry (dgentry@carboncaptu.re).

# Acknowledgements

Many thanks to the contributors of the &lt;code&gt;earth hackathon held at the Internet Archive on Sept. 5, 6, and 7 of 2018 which began this project. They are: Owen Barton, Denton Gentry, Greg Elin, Henry Poole, Robert L. Read, Stephanie Liu and Richard Stallman, in addition to Project Drawdown scientists and volunteers, Ryan Allard, Catherine Foster, Chad Frischmann, and Nick Peters.

# Contact

Denton Gentry (dgentry@carboncaptu.re) is currently the technical point of contact for this project.
