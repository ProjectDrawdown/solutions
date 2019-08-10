default: test

test:
	pytest -v -m "not slow" --strict-markers -W ignore::DeprecationWarning

alltest:
	pytest -v --cov=. --cov-report term-missing --strict-markers -W ignore::DeprecationWarning

alltests: alltest

tests: test

.PHONY: test alltest
