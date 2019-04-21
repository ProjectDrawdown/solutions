default: test

test: $(wildcard test_*.sh) $(wildcard *_test.sh)
	pytest -v -m "not integration" -W ignore::DeprecationWarning
	set -e; for d in $(filter test_%.sh,$^) $(filter %_test.sh,$^); do ./$$d; done

.PHONY: test
