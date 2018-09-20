default: test lint

test:
	PYTHONPATH=${PYTHONPATH}:.. pytest -v

lint:
	PYTHONPATH=${PYTHONPATH}:.. pylint --indent-string='  ' --disable=invalid-name *.py
