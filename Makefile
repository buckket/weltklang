sdist:
	python setup.py sdist

dist/PyRfK-0.1.tar.gz: sdist

all: sdist

.PHONY: sdist all