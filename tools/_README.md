# Guide to the Tools Directory

# Excel Extraction to Python

Most of the contents in this directory are related to extracting python code from Excel model workbooks.
They can be broken down as follows:

Top-level Instructions:
 * Extraction_Guide.md
 * Extraction_Guide.ipynb

Core Extraction code:
 * solution_xls_extract.py
 * vma_xls_extract.py
 * copy_expected_to_scenario.py: Template for updating scenarios by extracting data from from expected.zip.  Used when we make a change to scenario formats, or uncover a bug from previous extractions.

More Extraction code:
 * allocation_xls_extract.py: this has not been used or updated in a while
 * world_data_xls_extract.py: this has not been used or updated in a while
 * sma_xls_extract.py:  this is a prototype, not yet in use

Extraction support code:
 * util<area>.py:  Utilities for reading Excel workbooks
 * rrs<area>.py: Copied here from ../solution/rrs.py because python hates relative dependencies.

Creating Expected Result Sets:
 * CREATING_EXPECTED_ZIP.md: documents the process
 * export_csv.vb
 * create_expected_zip.py

Tools that are helpful for debugging:
 * multi_excel_sample.py:  Copy the same section from multiple workbooks; used to get a cross-cutting sample of how different Excel models are coded.
 * expected_ghost.py: Reconstruct Excel files from the expected.zip result set.

# Testing
 * expected_result_tester.py:  The workhorse that powers testing solutions against their expected results
 * summarize_expected_result.py: Utility that summarizes the expected results part of pytest output into something readable
 * solution_test_template.py:  The standard test file for solutions
 * diff_testruns.py:  Utility to exctract just the changed success/failure cases from two test runs.
 * skipped_tests.py: Utility to list which solutions are using the SCENARIO_SKIP or TEST_SKIP features

# Oceans
Oceans models have a completely different code base, so they also have some parallel tools:
 * ocean_solution_xls_extract.py
 * test_ocean_solution.py
 * excel_tools.py:  This is a parallel version of util.py.  We should merge these.
