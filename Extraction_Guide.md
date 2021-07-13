# Extracting Excel Models to Python

This a brief introduction to and guideline for extracting Excel models to Python.  The accompanying Jupyter Notebook `Extraction_Guide.ipynb`
will help you through the steps outlined here.

## Background

Project Drawdown has used Excel to produce models of solutions for climate change due to greenhouse gas emissions, doing complex analysis to predict the impact of the solutions under differing scenarios.  The work has outgrown Excel, however, and we are currently engaged in a process of migrating the models and underlying analytics to Python, which will become the ongoing basis for further research.

Most (but not all) of the analytic capability of the Excel workbooks has already been extracted, and is implemented in the `/model` directory.  Many individual solutions have been extracted and can be found in the `/solution` directory.  This guide mostly addresses adding more solutions to the `/solution` directory, but much of it will be relevant to extensions to `/model` directory as well.

Please note that the Excel workbooks contain sensitive, non-public material that cannot be shared.  Please protect them accordingly.

## What's in a Model?

A first look at one of the Excel Workbooks, or at the python code generated from one, can be overwhelming.  (Typical onboarding time to really
understand these things is at least three months, and that is for research professionals in the field.)  The good news is that you can do a lot 
of the work required without understanding all the details of what the inputs mean or what the analysis is doing.  You just need a bit of a holistic 
grasp of the overall process and a good ability to "follow the code".

TODO: Explain inputs, outputs, scenarios, ScenarioRecord.   LAND vs. RSS

## The Extraction Process

The Jupyter Notebook `Extraction_Guide.ipynb` covers steps 3-6 below.

  1. Obtain one of the Project Drawdown workbooks from PD, via hackathon, etc.
  2. Set up a development environment following the instructions in `README.md`
  3. Run the extraction step defined in `tools/extract/solution_xls_extract.py`
  4. Verify that the resulting solution code can be loaded and run
  5. Create the `expected_results.zip` file following the steps described in the Jupyter notebook or in `tools/extraction/expected_results.md`
  6. Add a test case for the new solution to `tests/test_excel_integration.py` and run the result
  7. Package up _all_ code changes (including your Jupyter notebook with output, if you used it) into your pull request.

## Handling Issues that Come Up

For Excel Workbooks that follow the standard Project Drawdown templates, extraction can be mostly automated using the process above and is usually fairly easy to do.  (A few workbooks, for example in the Oceans sector, are very different and may not be able to use the same automated approach at all.)  Even with standard workbooks, however, it is not unusual to run in to issues.  There may be issues or bugs in several places:
 * Issues in the extraction code
 * Issues in the model code
 * Issues in the test code
 * Issues or variations in the Excel workbook itself

Identifying and fixing these issues is part of the extraction process.  When doing this, please note the following:
 1. **Do not make changes to the Excel workbooks without signoff from someone from Project Drawdown.**  Even if it is just a typo.
 We need "official signoff" both to verify accuracy and to make sure that the master copies of the workbooks are also upated.
 Instead of changing the Excel, consider solution-specific hacks to the extraction code (see next item).
 2. **Do make changes to the extraction code.**  It is acceptable to put solution-specific code into `solution_xls_extract.py` or related files.
 Even hacky work-arounds are accepted here, since once extraction is complete, we will be done with it.
 3. **Cautiously make changes to the model code.**  If you can find and fix bugs in code in the `/model` directory, or in the generated code
 for your solution, that is fantastic.  These fixes should stand the test of time, however, not be hacks.
 4. **Changes to the test code accepted, but not necessary.** If the standardized tests fail on your model _and it is the test code that is at fault_,
 you may fix the test code, or simply hack around it (e.g. commenting out failing tests) 

In all cases if you make customizations to *any* code, be sure to add comments inline next to the changes with your name, a rough date, and the
reason for the change, and include that changed code in your pull request.
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

When trying to debug code that you might not understand, it can be very helpful to have code that you know is already working to compare it to.  So we recommend working with (at least) two Excel workbooks at a time: one you are extracting and another one or more that have already been extracted.  That way you can compare the workbooks to each other to see if there are differences, and also compare the previously-extracted workbook to the result to see what the code was supposed to have produced.

TODO: What else?