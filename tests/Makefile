default: test lint

test:
	PYTHONPATH=${PYTHONPATH}:.. pytest -v --disable-pytest-warnings --strict-markers -W ignore::DeprecationWarning

lint:
	PYTHONPATH=${PYTHONPATH}:.. pylint --indent-string='  ' --disable=invalid-name *.py
