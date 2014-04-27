sdist:
	python setup.py sdist

dist/PyRfK-0.1.tar.gz: sdist

upload: dist/PyRfK-0.1.tar.gz
	scp dist/PyRfK-0.1.tar.gz rfk@radio.krautchan.net:

all: sdist upload

.PHONY: sdist all