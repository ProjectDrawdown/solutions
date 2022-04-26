# Guide to the Tools Directory

The Jupyter notebook `_Tools.ipynb` has examples of using many of the utilities in this folder.

# Excel Extraction to Python

Most of the contents in this directory are related to extracting python code from Excel model workbooks.
They can be broken down as follows:

Top-level Instructions:
 * _Extraction_Guide.md

Core Extraction code:
 * solution_xls_extract.py
 * vma_xls_extract.py

Additional supporting code and sripts:
 * allocation_xls_extract.py: this has not been used or updated in a while
 * world_data_xls_extract.py: this has not been used or updated in a while
 * util<area>.py:  Library of utilities for reading Excel workbooks
 * convert_to_cpds.py: Script for converting some or all scenarios of a solution to Custom PDS adoption type.  This may be useful to get rid of certain kinds of errors.  It is also an example of how you can use the expected.zip file to alter solutions programatically based on the original Excel data, but without requiring access to the Excel file.

Creating Expected Result Sets: (instructions are in `_Extraction_Guide.md`)
 * export_csv.vb
 * create_expected_zip.py

Tools that are helpful for debugging:
 * multi_excel_sample.py:  Script for converting the same section from multiple workbooks; used to get a cross-cutting sample of how different Excel models are coded.
 * expected_ghost.py: Script for reconstructing Excel files from the expected.zip result set.

# Testing
 * expected_result_tester.py:  The workhorse that powers testing solutions against their expected results
 * solution_test_template.py:  The standard test file for solutions

Testing utilities:
 * diff_testruns.py:  Script to exctract just the changed success/failure cases from two test runs.
 * skipped_tests.py: Script that lists which solutions are using the SCENARIO_SKIP or TEST_SKIP features
 * summarize_expected_result.py: Script that summarizes the expected results part of pytest output into something readable

# Oceans
Oceans models have a completely different code base, so they also have some parallel tools:
 * ocean_solution_xls_extract.py
 * test_ocean_solution.py
 * excel_tools.py:  This is a parallel version of util.py.  We should merge these.
