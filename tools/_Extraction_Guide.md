# Extracting Excel Models to Python

## Background

Project Drawdown has used Excel to produce models of solutions for climate change due to greenhouse gas emissions, doing complex analysis to predict the impact of the solutions under differing scenarios.  The work has outgrown Excel, however, and we are currently engaged in a process of migrating the models and underlying analytics to Python, which will become the ongoing basis for further research.

Most (but not all) of the analytic capability of the Excel workbooks has already been extracted, and is implemented in the `/model` directory.  Many individual solutions have been extracted and can be found in the `/solution` directory.  This guide mostly addresses adding more solutions to the `/solution` directory, but much of it will be relevant to extensions to `/model` directory as well.

## The Extraction Process

This is the complete extraction process.  Parts of it are coded for you in the `_Tools` notebook.

  1. Obtain one of the Project Drawdown workbooks from PD, via hackathon, etc. 
  2. Set up a development environment following the instructions in `README.md`
  3. Open your Excel workbook, find the scenario list, and shorten it to three (details below)
  4. If it hasn't been done already, create the `expected.zip` test file (see instructions below).
  5. Run through the extraction steps in the `_Tools` notebook
  6. Run the solution tests, and fix issues (see hints below)
  7. Document any modifications you had to make to solution code in a `changelog` file in the solution directory
  8. Create a PR (Pull Request) for the results.

Note: it is _not_ reqired that the tests in step (6) run clean in order to PR the results.  Some bugs that we are addressing are
systematic, and it makes more sense to commit the extracted model so they can be considered together.
But every model should be able to load cleanly: it should be possible to load every scenario (that is kept) without raising exceptions.

## Handling Issues that Come Up

For Excel Workbooks that follow the standard Project Drawdown templates, extraction can be mostly automated using the process above and is usually fairly easy to do. Even with standard workbooks, however, it is not unusual to run in to issues.  There may be issues or bugs in several places, and different ways to fix them:

1. **Modify the Excel, sometimes.** Sometimes there are typos, or clearly wrong things in the Excel.  These can be fixed (and then both the expected.zip extraction and the python extraction need to be run again).  If you aren't sure, ask.  And *log what you did*, so we can propagate the fix back to Project Drawdown.
2. **Do make changes to the generated __init__.py file, or other scenario files**.  If there is a flaw in the generated code that makes it not match the Excel results, your first course of action should be to fix it in the `__init__.py` file or other generated files. There are hints about things to check for below.
3. **Add tests to the skip list when there is good reason.**  The solution test runner has the ability to mark tests that should be skipped.  You should not add any test failures that you don't understand to the skip list, and you should comment why a test is added.
4. **Cautiously make changes to the other code.**  If you can find and fix bugs in code in the `/model`, `/tools` or `/data` directories, that is fantastic.  These fixes should be applicable to all models (you should run the entire test suite).

## Tips

* Don't forget to restart a Jupyter Notebook kernel if you have modified code. If you change code you need to either reload the library or restart the kernel.   Rather than try to figure out if it safe to reload, I just restart the kernel every time.

* When comparing to Excel, make sure you've loaded the correct Scenario. On the `ScenarioRecord` tab, cell `B9` shows the currently loaded scenario.  When a workbook is first opened, this is usally empty, meaning you don't know which scenario was last loaded.  Select the scenario you are debugging against from the dropdown, and click on 'Load Scenario'.

* Beautifier for Excel Formulas: Are you looking at an excel formula with five nested `IF(...` expressions?  Try [https://www.excelformulabeautifier.com/](https://www.excelformulabeautifier.com/).

* Two other Excel tips:  `Ctl-<backquote>` will show you all the formulas on a sheet (repeat to turn off).  This is helpful to see if there are places where the formulas have been altered, or if someone has cut-and-pasted raw data where formulas are supposed to be.  Also: click on a cell, then select `Formulas>Trace Dependents` to see where a cell value is used in other formulas.

* Read the changelog for the solution you are extracting. Bear in mind that some of the notes may be outdated.

* We now also have a log of many issues in a spreadsheet [here](https://docs.google.com/spreadsheets/d/1UyDXHyItk0aN36Q7w6oHkXHQI4t9FLxZhvAFD2aDymg/edit?usp=sharing).

* Compare your Excel solution to other solutions. If you think the python code seems to be doing the wrong thing, it may be that your Excel workbook has a different implementation than other workbooks. The best way to check this is to use the Multi-Excel-Sample tool (in the tools directory) to look at the same bit of Excel from _all_ the workbooks. (If you don't have the permissions to look at all the workbooks, ask someone who does to produce the sample for you)

* Debug 'deep' test failures in the order they occur.  Within these tests, test order follows the execution order of the process (which is also the order of the sections in the `_init_.py`), so earlier errors tend to cascade to create later ones.

* If the solution had previously skipped tests, "unskip" the tests at least temporarily to check that the behavior after a new extraction.  The test may magically work now, or there could be a deeper problem that would not be discovered without this check.

* When you have a deep test failure, look at which data values are affected: if it is specific rows or columns, or the whole table.  That can give you clues as to what might be going wrong.

### If you see...

* Errors about missing sources usually indicate old scenarios that should be deleted.
* Test failures in TAM or Adoption sections may indicate that some data got garbled.  Check that the directory file or fiels (e.g. `tam/tam_ref_sources.json`) appear well formed.  Also verify that there are no non-standard settings in the "fit" parameters (all the 3rd Poly, etc., stuff at the top of the Excel sheet).
* Test failures in Helper Tables.  This is by far the most troublesome section, because the Excel is already very complicated and because some Excel models have been hand-altered.  Usually you have to look at the formulas in the top row and left column of the two tables on the Helper Tables sheet, and compare what you see to the quirks parameters documented in HelperTables.py.
* Lots and lots of errors in Unit Adoption, and they look kinda sorta like off-by-one-row errors, but not quite... Try setting the quirks parameter replacement_period_offset to 1 and see if that helps.  I don't have a test for this yet, but you should definitely be able to tell which way is correct.
* Errors in CO2 or CH4 results:  ignore these currently.  Our code is no longer working the same as the Excel code for this, and I don't know enough to debug what is or isn't correct behavior.

### You can skip a test if...

* The Excel model itself is missing some feature, or is broken.
* The python code and Excel code have intentionally diverged.  The only place this is currently true is the new GHG model that is used in a few models that are direct emitters of N2O or CH4.
* The magnitude of the error is small, doesn't cascade, and affects only regional data.  Regional data is less thoroughly supported in both the Excel and the python code, and sometimes the data is also less reliable.

Always comment in the test file why you added a test to the skip list.

### Brand New Experimental Tool

Since many issues that arise have to do with how adoptions are calculated (culminating in the dreaded Helper Tables module), I thought: why not see if we can't short-circuit all that by directly converting the _output_ of the Excel Helper Tables tab into a "Fully Custom PDS" type adoption?  So I built a tool to do that, called `convert_to_cpds`.  This is brand-new and hasn't been battle-tested yet.  But it may be a way to make some intractable solutions tractable, at the cost of losing the history of how the adoption was derived.

## Instructions for Modifying the Workbook Before Use

We want to limit the number of scenarios that we have to deal with.  Previously we did this after extraction, but it makes more sense to do it beforehand.
To do this, open the Excel spreadsheet and switch to the ScenarioRecord tab.  Scroll to the top.  You will see that there is a gab of hidden rows between 10 and 237.  Select the rows on both sides and unhide them (`right-click-menu>Unhide`).  Now scroll to the right, and you will see a gap between columns AQ and AS.  Select those columns and Unhide again.  You have now revealed the top-secret cells that make the list in the dropdown box!  Clear the contents of all but the last three scenarios in that list.  From here you can pop straight into creating the zip file (next section), or save the workbook and do that later.

## Instructions for Using Macros for Creating Zip File

#### Step 1: Insert the export macro into the workbook.
Open the Excel workbook and access the VBA Window:
* Find and click on the "View Macros" command (on Windows it is by default to the far right of the View ribbon)
* A popup like the following should appear.  Select _any_ of the indicated macros, then click on `Edit`
    ![Image of Excel Edit Macro popup](https://github.com/projectdrawdown/solutions/blob/extracting/Documentation/images/vb_macro.jpg)
* The Visual Basic Editor should appear.  On the left are a list of macros for this workbook.  Towards the bottom of the list there is an entry labeled `Modules`.  Right click on the entry and select `Insert` > `New Module`.
![Image showing Insert-Module menu](https://github.com/projectdrawdown/solutions/blob/extracting/Documentation/images/vb_insert.jpg)
* You should see a blank page fill the main portion of the editor.

Insert the entire contents of the file `export_csv.vb` into the blank page for the module.

#### Step 2: Run the macro

Locate subroutine `do_all` at the bottom of the page.  With your cursor on the top line of that subroutine, select the `Run Macro`
command (either from the `Run` menu, or click on the run button &vrtri;).

The export process takes a while (a few minutes on my powerful laptop), during which time the Excel screen may or may not
jump around between pages a lot.  It will prompt you when it switches to a new scenario.  (It is possible to modify the notebook to disable the prompt, but I find it easier just to click OK a few times.)
If it runs successfully, there should be no errors, and control should return to your cursor.

*Save and close the workbook* (the macro updates a few things in the spreadsheet, so make sure this is the version you use for extraction).  Continue with the extraction instructions in the section above.

#### Step 3: Turn all the little files into a Zip.

Code to do this can be found in `_Tools.ipynb`