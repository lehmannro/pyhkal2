VIRTUALENV = ./var
SOURCES = $(wildcard pyhkal/*.py) $(wildcard contrib/*.py) $(wildbard bin/*) \
		  setup.py pyhkal/service.tac

.PHONY: run test virtualenv clean

run: virtualenv
	@echo "Running PyHKAL.."
	@cd "$(VIRTUALENV)"; \
	./bin/twistd -ny lib/python2.5/site-packages/pyhkal/service.tac

test: virtualenv
	@PYTHONPATH="$(VIRTUALENV)/lib/python2.5/site-packages" \
	cd "$(VIRTUALENV)"; \
	./bin/trial pyhkal.test

virtualenv: $(VIRTUALENV) $(VIRTUALENV)/lib/python2.5/site-packages/pyhkal
$(VIRTUALENV):
	virtualenv --clear --distribute --no-site-packages "$(VIRTUALENV)"
	$(VIRTUALENV)/bin/pip -q install couchdb
	$(VIRTUALENV)/bin/pip -q install twisted
$(VIRTUALENV)/lib/python2.5/site-packages/pyhkal: $(SOURCES)
	$(VIRTUALENV)/bin/python setup.py --quiet install

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf "build/"
	rm -f pip-log.txt
