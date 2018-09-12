default: test lint

test: *_test.py
	set -e; \
	for d in $(filter %_test.py,$^); do \
		echo; \
		echo "Testing $$d"; \
		PYTHONPATH=${PYTHONPATH}:.. python $$d; \
	done

lint:
	pylint --indent-string='  ' --disable=invalid-name *.py
