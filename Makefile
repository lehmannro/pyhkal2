PYLINTOPTIONS = -E
INSTALLOPTS = --quiet
PIPOPTIONS = -q
VIRTUALENV = var

SOURCES = $(wildcard pyhkal/*.py) $(wildcard contrib/*.py) $(wildcard bin/*) \
		  setup.py
VIRTUAL = . $(VIRTUALENV)/bin/activate &&

.PHONY: run test pylint clean

run: install
	@echo "Running PyHKAL.."
	$(VIRTUAL) twistd -n $(T) pyhkal config.yaml

test: install
	$(VIRTUAL) cd $(VIRTUALENV) && trial pyhkal.test
# trial runs pyhkal/ directory otherwise

pylint: install
	$(VIRTUAL) pip install pylint
	$(VIRTUAL) cd $(VIRTUALENV) && pylint $(PYLINTOPTIONS) pyhkal

$(VIRTUALENV):
	virtualenv --distribute --no-site-packages "$(VIRTUALENV)"
install: $(VIRTUALENV) $(SOURCES)
	$(VIRTUAL) python setup.py $(INSTALLOPTS) install

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf build/ dist/ PyHKAL.egg-info/
	rm -f pip-log.txt MANIFEST twistd.pid
