# Creating the expected.zip file

The expected zip file contains a dump of (most of) the contents of a solution Excel workbook and is used
to run tests.  We do the dump this way for a couple of reasons:

 * The Excel workbook may contain proprietary data that we cannot publish with the code
 * We need access to the results for each scenario, which means running the Excel workbook to load the scenario, which means that 
 Excel.exe must be present.

 The expected.zip file contains an archive that is structured as follows:
 
 ```
     + scenario-1-name
         . Advanced Controls.csv
         . ScenarioRecord.csv
         . <all the other tabs>
     + scenario-2-name
         . <all the tabs>
```
etc.

## First Part: Export all the relevant tabs as csv files

This step requires Excel to run, and thus must be done on a Windows or Mac machine.   It is run from within Excel itself.
It is recommended to do this step with a copy of the Excel workbook in a clean, temporary directory.

### Step 1: Unprotect and Macro-Enable the workbook

If it has not already been done, follow instructions 1-7 in [this document](https://docs.google.com/document/d/1OiKg3_OOGjYOUdnHTQuZggsko5n31qv_YV4h77E3LHk/edit?usp=sharing).

### Step 2: Insert the export macro into the workbook.
Open the Excel workbook and access the VBA Window:
    * Find and click on the "View Macros" command (on Windows it is by default to the far right of the View ribbon)
    * A popup like the following should appear.  Select _any_ of the indicated macros, then click on `Edit`
    ![Image of Excel Edit Macro popup](https://github.com/projectdrawdown/solutions/blob/extracting/Documentation/images/vb_macro.jpg)
    * The Visual Basic Editor should appear.  On the left are a list of macros for this workbook.  Towards the bottom of
    the list there is an entry labeled `Modules`.  Right click on the entry and select `Insert` > `New Module`.
    ![Image showing Insert-Module menu](https://github.com/projectdrawdown/solutions/blob/extracting/Documentation/images/vb_insert.jpg)
    * You should see a blank page fill the main portion of the editor.

Insert the entire contents of the file `export_csv.vb` into the blank page for the module.

### Step 3: Run the macro

Locate subroutine `Generate_Scenario_Records` in the page.  With your cursor on the top line of that subroutine, select the `Run Macro`
command (either from the `Run` menu, or click on the run button &vrtri;).

The export process takes a while (a few minutes on my powerful laptop), during which time the Excel screen may or may not
jump around between pages a lot.
If it runs successfully, there should be no errors, and control should return to your cursor.

At this point, you should be able to see that there are a number of csv files in your directory, and you can close the VBA editor and the
Excel workbook.  (You don't need to save the macro or the workbook, though there is no harm in doing so)

## Second Part: Build the expected.zip

Run the code in `create_expected_zip.py`, either from the command line, or from within a python interpreter or Jupyter notebook
(in the latter case, the function you are looking for is `create_expected_zip.create_expected_zip(directory)`).

This should result in a file `expected.zip` being created in your directory.

The last step is to move the `expected.zip` to the `testdata` subdirectory of your solution directory (look at other solutions
for examples)
