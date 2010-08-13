VIRTUALENV = var
SOURCES = $(wildcard pyhkal/*.py) $(wildcard contrib/*.py) $(wildcard bin/*) \
		  setup.py

.PHONY: run test virtualenv clean

run: install
	@echo "Running PyHKAL.."
	$(VIRTUALENV)/bin/twistd -n $(T) pyhkal config.yaml

test: install
	cd "$(VIRTUALENV)"; ./bin/activate; trial pyhkal.test

virtualenv:
	python -mvirtualenv --distribute --no-site-packages "$(VIRTUALENV)"
	$(VIRTUALENV)/bin/pip -q install Twisted
	$(VIRTUALENV)/bin/pip -q install paisley
	$(VIRTUALENV)/bin/pip -q install PyYAML
$(VIRTUALENV):
	make virtualenv
install: $(VIRTUALENV) $(SOURCES)
	$(VIRTUALENV)/bin/python setup.py --quiet sdist
	$(VIRTUALENV)/bin/python setup.py --quiet install

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf "build/"
	rm -f pip-log.txt
