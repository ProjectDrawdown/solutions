default: test

test:
	tox

alltest:
	tox -e all

alltests: alltest

tests: test

.PHONY: test alltest