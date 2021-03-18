# Project Drawdown Model Engine
[Project Drawdown](https://www.drawdown.org/) is the most comprehensive plan yet published for how to solve Global Warming. Project Drawdown entered the climate conversation with the [publication of the 2017 book](https://www.drawdown.org/the-book). With [The Drawdown Review in 2020](https://drawdown.org/drawdown-framework/drawdown-review-2020), the project continues its mission to inspire and communicate solutions.

<img align="right" src="data/images/DrawdownReview2020.gif" />

This repository is an in-progress rewrite of the Project Drawdown model engine. This is intended to be a replacement for the series of interconnected Excel spreadsheets currently used by the project to do climate solution modeling. The intention is to create an implementation which will allow us to broaden the use of the climate solution models to policymakers, business leaders, and other decisionmakers and interested parties.

The codebase has some momentum already, has been continuously developed since September of 2018, and implements a substantial portion of the desired functionality. Planned deliverables and current status are listed below. We have also [recorded a video of the goals](https://youtu.be/Ffmx9KS-fW8), which allows demonstration where prototypes exist.

---

## Background

+ The Drawdown solution models are, at their core, economic models which estimate the total global and regional demand for each solution and the percentage of that demand each year which might adopt the Drawdown solution. The monetary and emissions impacts of that adoption are then calculated.

+ The framework and methodology for the model was developed by a core research team at Project Drawdown with a Head of Research and a set of Senior researchers who have worked with the project for several years.

+ The solutions have been developed by [annual cohorts of researchers](https://www.drawdown.org/research-fellows), mostly graduate and postdoctoral students working six month stints to vet new data inputs and implement targeted model improvements.

+ Project Drawdown's solution models were constructed in Excel, with a large number of Excel files now. There are two releases of the Excel models which are relevant to this effort:
    + 2019: released to the public in January 2019
    + 2020: extended from the 2019 models by a new cohort of researchers, released as The Drawdown Review in March 2020.

---

## Overview of the Project
Planned efforts include:

+ **Combined Model Implementation**  
Having copies of the underlying model in ~80 Excel files is no longer tenable, the level of toil involved in making substantial changes to the model is prohibitive. The project intends to deliver a single implementation in Python which can model the current ~80 solutions developed by Project Drawdown and allow easier development of more solution models in the future.
Current status:  
    + Python currently implements 70 out of the 80 Excel solution models of the 2019 version. The design doc for this effort was: [Drawdown Software Remodeling: backend models](https://docs.google.com/document/d/1X9X-61CG26m0XTUmqKeGJwU-HinPELD9HwBO064b5dA/edit) (now considered complete).
    + The remaining 10 of the 80 are solutions which differ more extensively from the rest, like Food Waste and Family Planning. Python implementations of the remaining 10 solutions have not been started. There is nothing blocking effort on these, just lack of cycles.
    + Updates to the Python code to support the 2020 versions of the 70 solutions has begun, and several solutions from the 2020 Excel update are working.
    + Automated testing is a key goal of the Python effort, to enable future work on the model to proceed with confidence. To ensure the new implementation faithfully reproduces the original, there is a test which runs the Excel any Python models for a given solution and checks that their results match within a floating point margin of error at every step of the model calculation. There is a [YouTube video describing the levels](https://www.youtube.com/watch?v=K6P56qUkCrw) of automated testing.
    + A nightly GitHub Action updates a [model health dashboard](https://projectdrawdown.github.io/solutions/), showing information about the solutions and their use of model features.

+ **UI aimed at researchers**  
We need a user interface aimed at individual solutions or a small handful of solutions, primarily for use by researchers looking to work with the model but additionally potentially of use to decisionmakers and policymakers in specific topics.  
Current status:  
    + There is a Jupyter UI to examine individual solutions, with a hosted instance running at https://solutions.geekhold.com/. There is a [video demonstrating its use](https://www.youtube.com/watch?v=MMrQwObdEZ4).
    + [Issue #13, "UI for Researcher use"](https://github.com/ProjectDrawdown/solutions/issues/13) tracks details.

+ **Solution Integration**  
 The individual solutions are modelled, but have to take the other solutions into account to produce final results. For example the set of energy solutions cannot add up to more than the total global demand for energy, and the land solutions cannot use more than the available land area of the planet. With the Excel models this is a manually intensive process. After a cohort of researchers finishes their work on the individual solutions, the senior researchers then spend several months combining, rationalizing, and finalizing the results.  

   The set of things to be done is varied:  

    + the sum of all Energy solutions must add up to the world demand for energy
    + the transportation solutions must be rationalized, though not the same way as energy as transport demand is somewhat elastic
    + some solutions provide feedstock for subsequent solutions, like biochar which needs wood scrap
    + World land area is allocated to the different land use solutions
    + Etc

   Much of this can be automated, by being able to run all of the solutions and incorporate a control loop with some simple rules for arbitrating between solutions. This effort has not been started, but could begin at any time. The ~70 completed Python solutions are believed to be sufficient to start such an effort.  

+ **UI aimed at broader audiences**  
We need better ways for people to explore the overall set of climate solutions and Drawdown results. This would be aimed at the complete set of solutions, or possibly to focus on an individual sector like Energy or Transportation. We also need ways to produce graphs, collateral for talks, and other presentable materials to further the mission of solutions for climate change. [Issue #12, "UI for multiple solutions"](https://github.com/ProjectDrawdown/solutions/issues/12) tracks details.

---

![status](https://github.com/ProjectDrawdown/solutions/workflows/Drawdown%20Solutions%20Python%20application/badge.svg)
[![codecov](https://codecov.io/gh/ProjectDrawdown/solutions/branch/master/graph/badge.svg)](https://codecov.io/gh/ProjectDrawdown/solutions) [![Join the chat at https://gitter.im/Solutions_platform/Engineering](https://badges.gitter.im/Solutions_platform/Engineering.svg)](https://gitter.im/Solutions_platform/Engineering?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Getting started

You will need [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git), [git-lfs](https://git-lfs.github.com/), and [Python 3](https://docs.python.org/3/using/index.html) (>= 3.8) installed. The jupyter labextensions require [nodejs](https://nodejs.org/) and [npm](https://www.npmjs.com/).

Get a copy of this source code:

```sh
$ git clone https://github.com/ProjectDrawdown/solutions.git
$ cd solutions
```

Tests are based on [tox](https://tox.readthedocs.org/). The default test target runs in about two minutes.
```
$ tox

# The "ci" (continuous integration) target runs all tests, and takes roughly two hours to finish.
$ tox -e ci

# to run a specific test:
$ tox -- tools/tests/test_vma_xls_extract.py::test_read_xls
```

The main user interface is a Jupyter Notebook intended to run in the cloud via [Jupyterhub](https://jupyter.org/hub). To run Jupyter locally we recommend using [pipenv](https://github.com/pypa/pipenv) for a virtual environment. As we use tox to run tests within virtual environments, we set the WORKON_HOME environment variable to have pipenv not re-install the same support in a new location:
```sh
$ WORKON_HOME="${PWD}/.tox/common" pipenv shell
(solutions) $ pipenv install -r requirements.txt
(solutions) $ jupyter labextension install @jupyter-widgets/jupyterlab-manager
(solutions) $ jupyter labextension install bqplot ipyvolume jupyter-threejs qgrid
(solutions) $ jupyter lab ./Drawdown.ipynb
```

To use with [Voilà](https://blog.jupyter.org/and-voil%C3%A0-f6a2c08a4a93):
```sh
$ WORKON_HOME="${PWD}/.tox/common" pipenv shell
(solutions) $ pipenv install -r requirements.txt
(solutions) $ jupyter nbextension install --py --sys-prefix vega
(solutions) $ jupyter nbextension enable vega --py --sys-prefix
(solutions) $ voila --enable_nbextensions=True --VoilaConfiguration.file_whitelist="['.*\.(png|jpg|gif|svg|csv|json|ico|js)']" ./VoilaDrawdown.ipynb
```

---

## License
The python code for the model engine is licensed under the GNU Affero General Public license and subject to the license terms in the LICENSE file found in the top-level directory of this distribution and at [https://github.com/ProjectDrawdown/solutions](https://github.com/ProjectDrawdown/solutions). No part of this Project, including this file, may be copied, modified, propagated, or distributed except according to the terms contained in the LICENSE file.

Data supplied from Project Drawdown (mostly in the form of CSV files) is licensed under the [CC-BY-NC-2.0](https://creativecommons.org/licenses/by-nc/2.0/) license for non-commercial use. The code for the model can be used (under the terms of the AGPL) to process whatever data the user wishes under whatever license the data carries. The data supplied for the Project Drawdown solutions is CC-BY-NC-2.0.

---

## Acknowledgements

Many thanks to the contributors of the &lt;code&gt;earth hackathon held at the Internet Archive on Sept. 5, 6, and 7 of 2018 which began this project. They are: Owen Barton, Robert L. Read, Denton Gentry, Henry Poole, Greg Elin, Marc Jones, and Stephanie Liu, in addition to Project Drawdown scientists and volunteers, Ryan Allard, Catherine Foster, Chad Frischmann, Kevin Bayuk, and Nick Peters.

Huge thanks to Beni Bienz of The Climate Foundation for his work in implementing a substantial portion of the system.

---

## Contact

Denton Gentry (dgentry@carboncaptu.re) is currently the technical point of contact for this project.
