default: test

test:
	pytest -v

.PHONY: $(SUBTESTS) test
