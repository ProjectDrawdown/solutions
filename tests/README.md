excel_integration_test is an end-to-end test which starts a Python flask
HTTP server, starts up a copy of Microsoft Excel, sets the spreadsheet
to reference the local HTTP server for its calculations, fetches key
results from the spreadsheet, and compares them to expected golden
values.


To use, create and activate a python virtual environment as described
in the README.md one level up.

Install Microsoft Excel (which you have to obtain separately). At the
time of this writing, only the 2016 Mac version has been tested.
