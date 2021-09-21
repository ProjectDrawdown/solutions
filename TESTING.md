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

## Executing and debugging unit tests from the vs code environment

Problems can occur when using VS Code with pytest and anaconda. The unit testing framework within VS Code either takes a few minutes to collect all the tests, or just hangs.

The following solution should work on a set-up using Windows10 and WSL (Ubuntu):

In the project directory, create .vscode/conda-pytest.sh:

#!/usr/bin/env bash
. /path/to/miniconda3/etc/profile.d/conda.sh
conda activate my_env && pytest "$@"

and then, in the project's .vscode/settings.json:
{
    "python.testing.pytestPath": "/path/to/project/.vscode/conda-pytest.sh"
}
Remember to set conda-pytest.sh as executable.

For a pure Windows setup, perhaps an equivalent batch/powershell script could be written in place of conda-pytest.sh.

To reduce collection time further, consider adding a entry to Pytest Args such as ./solution/mysolution/. Note however that this would need to be changed when switching between solutions.

## Writing Tests

New code should include tests to cover the new functionality, and _must_ include test
coverage for code that generates analytic results.  Please conform to the existing pattern of putting tests in a `/tests` subdirectory.

## Test Policy

At this time, there are a number of failing tests in the system, so we don't have a 'check in clean' policy.  However, we do ask that you check that your tests aren't causing any additional regressions: no new test failures outside of your own code.  We have started including a test result log with each release (you can find it by clicking on the 'latest' release label on the main github page, or look at other releases in the system as appropriate).  There's a new tool in tools called `diff_testruns.py` that will highlight the changes between two test runs.
 