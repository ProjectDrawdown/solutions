default: test lint

SUBTESTS= tests model/tests
$(SUBTESTS):
	$(MAKE) -C $@

test: $(SUBTESTS) $(wildcard *_test.py) $(wildcard *_test.sh)
	set -e; \
	for d in $(filter %_test.py,$^); do \
		echo "Testing $$d"; PYTHONPATH=${PYTHONPATH}:. python $$d; \
	done
	set -e; for d in $(filter %_test.sh,$^); do echo "Testing $$d"; ./$$d; done

lint:
	pylint --indent-string='  ' --disable=invalid-name *.py

.PHONY: $(SUBTESTS) test lint
