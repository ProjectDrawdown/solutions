default: test lint

test: $(wildcard test_*.py)
	set -e; \
	for d in $(filter test_%.py,$^); do \
		echo "Testing $$d"; PYTHONPATH=${PYTHONPATH}:.. python $$d; \
	done

lint:
	PYTHONPATH=${PYTHONPATH}:.. pylint --indent-string='  ' --disable=invalid-name *.py
