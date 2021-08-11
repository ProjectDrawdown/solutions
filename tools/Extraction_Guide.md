# Extracting Excel Models to Python

## Background

Project Drawdown has used Excel to produce models of solutions for climate change due to greenhouse gas emissions, doing complex analysis to predict the impact of the solutions under differing scenarios.  The work has outgrown Excel, however, and we are currently engaged in a process of migrating the models and underlying analytics to Python, which will become the ongoing basis for further research.

Most (but not all) of the analytic capability of the Excel workbooks has already been extracted, and is implemented in the `/model` directory.  Many individual solutions have been extracted and can be found in the `/solution` directory.  This guide mostly addresses adding more solutions to the `/solution` directory, but much of it will be relevant to extensions to `/model` directory as well.
The accompanying Jupyter Notebook `Extraction_Guide.ipynb` will help you through the steps outlined here.

Please note that the Excel workbooks contain sensitive, non-public material that cannot be shared.  Please protect them accordingly.

## What's in a Model?

The other files in this Documentation directory give an overview of what models are for and some of their
moving parts.
Even with that information, your first look at one of the Excel Workbooks, or at the python code generated from one, can be overwhelming.  (Typical onboarding
time to really understand these things is at least three months, and that is for research professionals in the field.)
The good news is that you can do a lot of the work required without understanding all the details of what the inputs mean or
what the analysis is doing.  You just need a bit of a holistic grasp of the overall process and a good ability to "follow the code".

## The Extraction Process

The Jupyter Notebook `Extraction_Guide.ipynb` walks you through steps 4-7 below.

  1. Obtain one of the Project Drawdown workbooks from PD, via hackathon, etc. 
  2. Prepare the workbook for extraction following the instructions below.
  3. Set up a development environment following the instructions in `README.md`
  4. Run the extraction step defined in `tools/solution_xls_extract.py`
  5. Verify that the resulting solution code can be loaded and run
  6. Create the `expected.zip` test file following the steps described in the Jupyter notebook and in `tools/CREATE_EXPECTED_ZIP.md`
  7. Generate a new solution test file with the function `output_solution_test_file` in `tools/solution_xls_extract.py`
  8. Run the new solution tests and observe the results.
  9. Document any modifications you had to make to solution code in a `changelog` file in the solution directory
  10. Create a PR (Pull Request) for the results.

Note: it is _not_ reqired that the tests in step (8) run clean in order to PR the results.  Some bugs that we are addressing are
systematic, and it makes more sense to upload the extracted model so they can be considered together.
You should, however, complete all the steps in the list.

## Preparing an Excel Workbook for Extraction

Make sure that you can open and run the Excel workbook:  on the `Basic Controls` tab, find the 'Scenario to Customize' dropdown at cell C5.  Select one of the scenarios from the dropdown (scroll up if the list appears empty), and then click the 'Load Scenario Inputs' button.  You should see numbers appear in the other fields, and a graph appear to the right.

Several changes need to be made to the workbook itself to enable other extraction processes to work correctly.  Follow instructions 1-7 in [this document](https://docs.google.com/document/d/1OiKg3_OOGjYOUdnHTQuZggsko5n31qv_YV4h77E3LHk/edit?usp=sharing).

## Handling Issues that Come Up

For Excel Workbooks that follow the standard Project Drawdown templates, extraction can be mostly automated using the process above and is usually fairly easy to do.  (A few workbooks, for example in the Oceans sector, are very different and may not be able to use the same automated approach at all.)  Even with standard workbooks, however, it is not unusual to run in to issues.  There may be issues or bugs in several places:
 * Issues in the extraction code
 * Issues in the model code
 * Issues in the test code
 * Issues or variations in the Excel workbook itself

Identifying and fixing these issues is part of the extraction process.  When doing this, please note the following:
 1. **Do not make changes to the Excel workbooks without signoff from someone from Project Drawdown.**  Even if you are convinced the Excel is incorrect.  Do document your findings (open a github issue).
 We need "official signoff" from Project Drawdown both to verify accuracy and to make sure that the master copies of the workbooks are also upated.
 Instead of changing the Excel, consider solution-specific hacks to the extraction code (see next item).
 2. **Do make changes to the generated __init__.py file**.  If there is a flaw in the generated code that makes it not match the Excel results, your first course of action should be to fix it in the `__init__.py` file.
 3. **Do make changes to the extraction code.**  It is also acceptable to put solution-specific code into `solution_xls_extract.py` or related files.
 Even hacky work-arounds are accepted here, since once extraction is complete, we will be done with it.
 4. **Cautiously make changes to the model code.**  If you can find and fix bugs in code in the `/model`, `/tools` or `/data` directories, that is fantastic.  These fixes should stand the test of time, however, not be hacks.
 5. **Changes to the test code accepted, but not required.** If there are problems that you are certain _are in the tests_, skipping those tests is acceptable.  In this case, please open an issue describing the failing test, and why you believe the test is at fault.

In all cases if you make customizations to *any* code, be sure to add comments inline next to the changes with your name, a date, and the
reason for the change.  Include all changed code in your pull request.
We will use this information to determine which changes get into the code and which become issues that require further 
investigation and fixes.

Here's an example:
```python
        # NOTE: Denise added 7/21; was running into divide-by-zero; need to check if this is appropriate
        if self.soln_avg_annual_use == 0:
            return 0.0
        return self.soln_lifetime_capacity / self.soln_avg_annual_use
```

## Helpful Hints

The Jupyter Notebook contains additional helpful hints for finding and addressing issues in the models.
