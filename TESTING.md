## Running Tests

This project uses [pytest](https://docs.pytest.org/en/6.2.x/contents.html) for testing.  You can test the entire project simply by running the command `pytest` from the project root directory.

The full test suite is lengthy, and takes some time to run.  You may find it worthwhile to focus testing on specific parts of the code that you are working with.  For example, to test just the model directory, or just a single solution, you would use the following commands&mdash;pytest automatically knows to search for the tests within the directory you select.
```sh
    $ pytest model
    $ pytest solution/afforestation
```

You can also execute test functions directly in python (or jupyter notebook), which can be more convenient in some cases.
In particular, each solution's tests consists of three functions: `test_loader`, `test_key_results` and `test_deep_results`.
So if you want to manually run the deep result tester for afforestation, you would do this:
```python
    import solution.afforestation.tests.test_afforestation as taff
    taff.test_deep_results()
```
One of the advantages of doing this is that you can set _which_ deep tests you want to run or skip as an argument to the `test_deep_results`
function. See the documentation for `tools.expected_results_tester.one_solution_tester` for details.

The `test_deep_results` functions test many intermediate results of the solution code against the Excel, as well as final results.
This should be done when working on something that changes anything in `model`, and for a given solution if working on that solution.
But it doesn't need to be done for all solutions all the time.  You can skip it with the mark functionality of pytest:
```sh
   $ pytest -m "not deep"
```


## Writing Tests

New code should include tests to cover the new functionality, and _must_ include test
coverage for code that generates analytic results.  Please conform to the existing pattern of putting tests in a `/tests` subdirectory.
 