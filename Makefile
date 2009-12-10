VIRTUALENV = ./var
SOURCES = $(wildcard pyhkal/*.py)

.PHONY: run virtualenv clean

run: virtualenv
	@cd "$(VIRTUALENV)"; \
	./bin/python -mpyhkal

virtualenv: $(VIRTUALENV) $(VIRTUALENV)/lib/python2.5/site-packages/pyhkal
$(VIRTUALENV):
	virtualenv --clear --distribute --no-site-packages "$(VIRTUALENV)"
	$(VIRTUALENV)/bin/pip -q install PyYAML
	$(VIRTUALENV)/bin/pip -q install couchdb
$(VIRTUALENV)/lib/python2.5/site-packages/pyhkal: $(SOURCES)
	$(VIRTUALENV)/bin/python setup.py install --skip-build

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf "build/"
	rm -f pip-log.txt
