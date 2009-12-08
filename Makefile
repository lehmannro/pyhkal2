PYTHON = python
VIRTUALENV = ./var
SOURCES = $(wildcard pyhkal/*.py)

.PHONY: run virtualenv clean

run: virtualenv
	$(VIRTUALENV)/bin/python -mpyhkal example.yaml

virtualenv: $(VIRTUALENV) $(VIRTUALENV)/lib/python2.5/site-packages/pyhkal
$(VIRTUALENV):
	virtualenv --clear --distribute --no-site-packages "$(VIRTUALENV)"
	$(VIRTUALENV)/bin/pip -q install PyYAML
	$(VIRTUALENV)/bin/pip -q install couchdb
$(VIRTUALENV)/lib/python2.5/site-packages/pyhkal: $(SOURCES)
	$(VIRTUALENV)/bin/python setup.py install --skip-build

clean:
	rm -rf "$(VIRTUALENV)"