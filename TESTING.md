## Running Tests

This project uses [pytest](https://docs.pytest.org/en/6.2.x/contents.html) for testing.  You can test the entire project simply by running the command `pytest` from the project root directory.

The full test suite is lengthy, and takes some time to run.  You may find it worthwhile to focus testing on specific parts of the code that you are working with.  For example, to test just the model directory, or just a single solution, you would use the following commands&mdash;pytest automatically knows to search for the tests within the directory you select.
```sh
    $ pytest model
    $ pytest solution/afforestation
```

You can also execute test functions directly in python (or jupyter notebook), which can be more convenient in some cases.
For example, to compare the computed results for the afforestation solution to the saved excel results,
you can execute
```python
    import solution.afforestation.tests.test_afforestation as taff
    taff.test_afforestation_results()
```

The `test_`_solution_`_results` functions take arguments that let you select which subtests to run.  See the 
documentation for `tools.expected_result_tester.one_solution_tester` for the details.  Currently this customization is
only available via direct execution from python, not via pytest.  (If someone would like to convert into a fixture pytest can use,
that would be great!)

## Writing Tests

New code should include tests to cover the new functionality, and _must_ include test
coverage for code that generates analytic results.  Please conform to the existing pattern of putting tests in a `/tests` subdirectory.
 