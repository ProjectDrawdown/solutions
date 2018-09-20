default: test lint

test:
	PYTHONPATH=${PYTHONPATH}:../.. pytest -v

lint:
	PYTHONPATH=${PYTHONPATH}:../.. pylint --disable=no-self-use --indent-string='  ' --disable=invalid-name *.py
