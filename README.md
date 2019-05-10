# Project Drawdown Model Engine

This is the [Project Drawdown](https://www.drawdown.org/) model engine. This is intended to be a replacement for the series of interconnected Excel spreadsheets currently used by the project to do climate solution modeling. The intention is to create an implementation which will allow us to broaden the use of the climate solution models to policymakers, business leaders, and other decisionmakers and interested parties.

# Getting started

You will need [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Python 3](https://docs.python.org/3/using/index.html) installed.

Get a copy of this source code:

```sh
git clone git@gitlab.com:codeearth/drawdown.git
cd drawdown
```

Create and activate a python virtual environment. We recommend [Anaconda](https://www.anaconda.com/distribution/#download-section).

```sh
$ conda create --name drawdown
$ conda activate drawdown
(drawdown) $ conda install -c conda-forge jupyterlab altair=2.3 bqplot
(drawdown) $ conda install -c conda-forge ipywidgets nodejs xlrd pytest
(drawdown) $ conda install -c conda-forge ipyvolume PIL
(drawdown) $ jupyter labextension install @jupyter-widgets/jupyterlab-manager
(drawdown) $ jupyter labextension install bqplot ipyvolume jupyter-threejs
```

Then start the Jupyter Notebook:
```sh
(drawdown) $ jupyter lab ./Drawdown.ipynb
```

# Understanding the Drawdown solution models: Reference and Summary

[Documentation of the Excel models](https://gitlab.com/codeearth/drawdown/blob/master/Documentation/RRS_Model_Framework_and_Guidelines_v1.1.pdf) has been written, as well as a [design doc](https://docs.google.com/document/d/18nUKV-qltsaSD8kZd5gHswQu82Ot9rg19KIU8_eOisY/view) of how we expect the new implementation to be completed. We refer to this development effort as a Remodel, of course.

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

### Core model complete

At this point in development (4/2019) the core model for computing adoption, costs, and benefits is substantially complete and fully handles 43 of the 78 total solutions models developed by the project. Work from this point is continuing in several areas described below.

Tasks which do not fit into an ordered list of things to be completed:

### Model enhancements

Work is beginning on enhancements to the model beyond the original Excel-based models. The first area being worked on is a more sophisticated model of CO2 impacts, using an Impulse-Response model leveraging [FAIR](https://github.com/OMS-NetZero/FAIR).

### User Interface
   The ultimate goal of this project is to produce a compelling, browser-delivered GUI. There are at least three mostly distinct audiences:
   + Researchers who want to work with the models, add data sources, etc.
   + Policy makers and deciders, who need tools to help guide effective use of resources.
   + Interested parties and the general public, to evangelize that there *are* solutions to global warming.

   UI work has focussed on the first point about the audience of researchers. This need is expected to be met using [Jupyter Notebook](https://jupyter.org), eventually hosted via an instance of [JupyterHub](https://jupyter.org/hub). An early version of this UI is available on [mybinder.org](https://mybinder.org/v2/gl/codeearth%2Fdrawdown/master?urlpath=lab/tree/Drawdown.ipynb).

### Automated testing
   One other goal for the project is to build a model implementation with good coverage by automated tests. There is a [YouTube video which demonstrates the three layers of tests](https://youtu.be/ipZrQWuMU3w) and another which [focuses on the Excel-based system test specifically](https://youtu.be/HLL7HrFcmjc).

   Tests exist at two layers:
    1. unit tests of each function
    2. a system test which starts Excel to compare the original, unmodified spreadsheet to the results from the new implementation

---

# License
This program (excluding the Excel code) is part of the &lt;code&gt;/earth project. The &lt;code&gt;/earth DD Model Engine is licensed under the GNU Affero General Public license and subject to the license terms in the LICENSE file found in the top-level directory of this distribution and at https://gitlab.com/codeearth/drawdown. No part of this Project, including this file, may be copied, modified, propagated, or distributed except according to the terms contained in the LICENSE file.

The Project Drawdown Excel model file itself will be release under a license which has not yet been decided, but is not released at the time of this writing. The small bits of code in that model file copyright Robert L. Read are released under the AGPL; since they are tightly integrated with the spreadsheet, they are likely valuable only as examples.

---

# Contribution

Contributors to the project should submit to the project using the Developer Certificate of Origin. For more information, contact Denton Gentry (dgentry@carboncaptu.re).

# Acknowledgements

Many thanks to the contributors of the &lt;code&gt;earth hackathon held at the Internet Archive on Sept. 5, 6, and 7 of 2018 which began this project. They are: Owen Barton, Denton Gentry, Greg Elin, Marc Jones, Henry Poole, Robert L. Read, Stephanie Liu and Richard Stallman, in addition to Project Drawdown scientists and volunteers, Ryan Allard, Catherine Foster, Chad Frischmann, and Nick Peters.

# Contact

Denton Gentry (dgentry@carboncaptu.re) is currently the technical point of contact for this project.
