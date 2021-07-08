# Project Drawdown Model Engine

[Project Drawdown](https://www.drawdown.org/) is the most comprehensive plan yet published for how to solve Global Warming. Project Drawdown entered the climate conversation with the [publication of the 2017 book](https://www.drawdown.org/the-book). With [The Drawdown Review in 2020](https://drawdown.org/drawdown-framework/drawdown-review-2020), the project continues its mission to inspire and communicate solutions.

<img align="right" src="data/images/DrawdownReview2020.gif" />

The Drawdown solution models are, at their core, economic models which estimate the total global and regional demand for each solution and the percentage of that demand each year which might adopt the Drawdown solution. The monetary and emissions impacts of that adoption are then calculated.  The framework and methodology for the model was developed by a core research team at Project Drawdown with senior research fellows and visiting researchers from each of the relevant solution domains, over the course of a number of years. The models were originally constructed in some ~80 Excel files.

This repository is a conversion of the original Excel models into python.  This includes both the analytical parts of the model, and the summary data used to produce key results.
Our goal is to enable:
   + ongoing research by Project Drawdown and other researchers
   + use of this research in other projects, including a broader audience of policy makers, business leaders, and other interested parties.
Future updates to the research will be published in this repository.

Whilst this repo covers the model and analytics in the form of a python library, our [sister project](https://github.com/ProjectDrawdown/global-research-platform) develops that into a server-based solution and a researcher-aimed UI.

## Status

Conversion Status:
  * Most of the solutions (technologies) have been converted.  The remaining include some technologies (such as those related to Food systems and Oceans) that use different methodology.
  * New solutions are converted as they become released from Project Drawdown research.
  * Almost all of the "core calculations" (which generate the main results) have been completed.
  * Most of the "secondary calculations" (which are used to do solution-specific generation of, e.g. emissions factors or adoption estimates) are _not_ yet implemented.
  * The overall integration between multiple solution models (used to model, for example, the impact of adopton of one solution on demand for another) has not yet been implemented.

Other work in progress:
  * Continuing work to make the interfaces more accessible to folks outside the Project Drawdown community, both in terms of code improvements and documentation.
  * Additional and upgraded analytics for some areas (e.g. greenhouse-gas calculation updates)

For a more detailed list, see the [Issues List](https://github.com/ProjectDrawdown/solutions/issues).

---
# Using the code

## Getting the source code

1. Get a copy of this source code:
```sh
      $ git clone https://github.com/ProjectDrawdown/solutions.git
      $ cd solutions
      $ git checkout develop
```

## Development/Deployment environment

There are two requirements files, depending on how you want to set up your environment:

  1. `requirements.txt` is a [pip](https://pip.pypa.io/en/stable/user_guide/) requirements file with a minimal set of dependencies
```sh
      $ pip install -r requirements.txt
```
  2. `environment.yml` is a [conda](https://docs.conda.io/en/latest/miniconda.html) environment definition which includes a broader set of packages, notably including [Jupyter notebooks](https://jupyter-notebook.readthedocs.io/en/stable/):
```sh
      $ conda env create -f environment.yml
```

The conda environment is recommended for exploring the code and doing development, while the pip deployment is better for deployment as a package.

---

## License
The python code for the model engine is licensed under the GNU Affero General Public license and subject to the license terms in the LICENSE file found in the top-level directory of this distribution and at [https://github.com/ProjectDrawdown/solutions](https://github.com/ProjectDrawdown/solutions). No part of this Project, including this file, may be copied, modified, propagated, or distributed except according to the terms contained in the LICENSE file.

Data supplied from Project Drawdown (mostly in the form of CSV files) is licensed under the [CC-BY-NC-2.0](https://creativecommons.org/licenses/by-nc/2.0/) license for non-commercial use. The code for the model can be used (under the terms of the AGPL) to process whatever data the user wishes under whatever license the data carries. The data supplied for the Project Drawdown solutions is CC-BY-NC-2.0.

## Contributing
We would love to have your help.
Please see [CONTRIBUTING.md](Contributing.md) for guidelines for contributing to this project.

## Acknowledgements

Many thanks to the contributors of the &lt;code&gt;earth hackathon held at the Internet Archive on Sept. 5, 6, and 7 of 2018 which began this project. They are: Owen Barton, Robert L. Read, Denton Gentry, Henry Poole, Greg Elin, Marc Jones, and Stephanie Liu, in addition to Project Drawdown scientists and volunteers, Ryan Allard, Catherine Foster, Chad Frischmann, Kevin Bayuk, and Nick Peters.

Huge thanks to Beni Bienz of The Climate Foundation for his work in implementing a substantial portion of the original system, and even huger thanks to Denton Gentry for the majority of the subsequent development.


## Contact

Denise Draper (draperd@acm.org) is currently the technical point of contact for this project.

