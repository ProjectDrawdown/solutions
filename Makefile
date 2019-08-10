default: test

test: $(wildcard test_*.sh) $(wildcard *_test.sh)
	pytest -v -m "not slow" --cov=. --cov-report term-missing --strict-markers -W ignore::DeprecationWarning
	set -e; for d in $(filter test_%.sh,$^) $(filter %_test.sh,$^); do ./$$d; done

.PHONY: test
