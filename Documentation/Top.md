# Project Drawdown Model Engine Documentation

Overview/index of documentation:

* The first place to start is the [Main Readme](drawdown_solutions.html), which contains both an overview of the project and instructions for getting, installing and starting to use the PDME.
* [Concepts](concepts.html) contains some high-level concepts and vocabulary that are useful for understanding what models are and how they work.
* [Code](code_top.html)  Notes and concepts specifically about the code.
* The 'Start_Here' Jupyter Notebook (in the root directory of the code) is an interactive introduction to using the PDME.
* The *API Documentation* is the main content of this website, accessible from the menu at left.

The contents of this repository are organized into the following folders:

* `data/`: Data files with greenhouse gas emissions, technology usage and other data that is shared across the system.
* `Documentation/`: Additional documentation files and examples (and the source for this auto-generated website).
* `integrations/`: Advanced inter-solution modeling that takes into account how the use of some solutions changes the impact of others.  Documentation is inline in the code, at this time.
* `limbo/`: Code that isn't currently in use, but contains functionality and ideas that we may want to incorporate again later.
* `model/`: The main part of the system that defines what PD models *do*.  The *API Documentation* (left) is the documentation for the model directory.
* `solution/`: Each of the individual solutions that have been modeled to date (e.g. electric bicycles, or improved fishery emissions).  These are documented on the [Project Drawdown website](https://drawdown.org/solutions).
* `tools/`: Tools used to create, test, and maintain the code.  Documented in [Tools Readme](tools.html).


