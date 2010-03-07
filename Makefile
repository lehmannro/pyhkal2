VIRTUALENV = var
SOURCES = $(wildcard pyhkal/*.py) $(wildcard contrib/*.py) $(wildcard bin/*) \
		  setup.py pyhkal/service.tac
PYVER = $(shell python -V 2>&1 | grep -o '[0-9].[0-9]')

.PHONY: run test virtualenv clean yaml

run: virtualenv
	@echo "Running PyHKAL.."
	@cd "$(VIRTUALENV)"; \
	./bin/twistd -ny lib/python$(PYVER)/site-packages/pyhkal/service.tac

test: virtualenv
	@PYTHONPATH="$(VIRTUALENV)/lib/python$(PYVER)/site-packages" \
	cd "$(VIRTUALENV)"; \
	./bin/trial pyhkal.test

virtualenv: $(VIRTUALENV) \
		$(VIRTUALENV)/src/twisted \
		$(VIRTUALENV)/src/couchdb \
		$(VIRTUALENV)/lib/python$(PYVER)/site-packages/pyhkal
$(VIRTUALENV):
	python -mvirtualenv --clear --distribute --no-site-packages "$(VIRTUALENV)"
$(VIRTUALENV)/src/twisted:
	$(VIRTUALENV)/bin/pip -q install -e "svn+svn://svn.twistedmatrix.com/svn/Twisted/trunk/"
$(VIRTUALENV)/src/couchdb:
	$(VIRTUALENV)/bin/pip -q install -e "hg+https://couchdb-python.googlecode.com/hg/#egg=couchdb"
$(VIRTUALENV)/lib/python$(PYVER)/site-packages/yaml:
	$(VIRTUALENV)/bin/pip -q install PyYAML
$(VIRTUALENV)/lib/python$(PYVER)/site-packages/pyhkal: $(SOURCES)
	$(VIRTUALENV)/bin/python setup.py --quiet install

yaml: $(VIRTUALENV)/lib/python$(PYVER)/site-packages/yaml

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf "build/"
	rm -f pip-log.txt
