default: test lint

test:
	PYTHONPATH=${PYTHONPATH}:.. pytest -v --disable-pytest-warnings --strict-markers -W ignore::DeprecationWarning
	set -e; for d in $(filter test_%.sh,$^) $(filter %_test.sh,$^); do ./$$d; done

lint:
	PYTHONPATH=${PYTHONPATH}:.. pylint --indent-string='  ' --disable=invalid-name *.py
