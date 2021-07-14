This project uses [pytest](https://docs.pytest.org/en/6.2.x/contents.html) for testing.  

Usually you will want to invoke pytest from the root directory of the project.  There,
you can test the entire project with the following command:
```sh
    $ python -m pytest
```
For this project, it is better to invoke pytest via python (as above) than directly, because it will
add the top-level directory to the path, allows all the import statements to work.   (Alternatively,
if you add the root directory to your `$PYTHONPATH` environment variable, you should be able to use
pytest directly from anywhere within this project.)

The full test suite is lengthy, and takes some time to run.  You may find it worthwhile to focus testing on specific parts of the code that you are working with.

For most of the code, tests are found in a subdiretory `/tests` within the directory (e.g. `/model/tests`).
To test just the model directory, you would use the following command:
```sh
    $ python -m pytest model
```

The exception is solutions.  The tests for solutions are found in the top-level `/tests` directory.  These tests are responsible for ensuring that solutions create the correct results compared to the original Project Drawdown models.  This [youtube video](https://www.youtube.com/watch?v=K6P56qUkCrw) describes how these tests work.

To test all solutions:
```sh
    $ python -m pytest tests
```

To test one specific solution, find the name of the function you want in file `tests/test_excel_integration.py` (towards the bottom of the file), and invoke that specific test, e.g. like this:
```sh
    $ python -m pytest tests/test_excel_integration.py::test_SolarPVUtility_RRS
```

**Note**: new code should include tests to cover the new functionality, and _must_ include test
coverage for code that generates analytic results.  Please conform to the existing pattern of putting tests in a `/tests` subdirectory.
 