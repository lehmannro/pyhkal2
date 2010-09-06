PYLINTOPTIONS = -E
INSTALLOPTS = --quiet
PIPOPTIONS = -q
VIRTUALENV = var

SOURCES = $(wildcard pyhkal/*.py) $(wildcard contrib/*.py) $(wildcard bin/*) \
		  setup.py
ifdef WIN32
	BIN = Scripts
else
	BIN = bin
endif
VIRTUAL = $(VIRTUALENV)/$(BIN)/

.PHONY: run test virtualenv clean

run: install
	@echo "Running PyHKAL.."
	$(VIRTUAL)twistd -n $(T) pyhkal config.yaml

test: install
	cd $(VIRTUALENV) && $(BIN)/trial pyhkal.test
# trial runs pyhkal/ directory otherwise

pylint: install
	$(VIRTUAL)pip install pylint
	cd $(VIRTUALENV) && $(BIN)/pylint $(PYLINTOPTIONS) pyhkal

# line 2: pip on Windows installs twisted/ folder otherwise
virtualenv:
	python -mvirtualenv --distribute --no-site-packages "$(VIRTUALENV)"
	cd $(VIRTUALENV) && $(BIN)/pip $(PIPOPTIONS) install Twisted
	$(VIRTUAL)pip $(PIPOPTIONS) install paisley
	$(VIRTUAL)pip $(PIPOPTIONS) install pyopenssl
	$(VIRTUAL)pip $(PIPOPTIONS) install oauth
	$(VIRTUAL)pip $(PIPOPTIONS) install twittytwister
	$(VIRTUAL)pip $(PIPOPTIONS) install PyYAML
$(VIRTUALENV):
	make virtualenv
install: $(VIRTUALENV) $(SOURCES)
	$(VIRTUAL)python setup.py $(INSTALLOPTS) sdist
	$(VIRTUAL)python setup.py $(INSTALLOPTS) install

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf build/ dist/
	rm -f pip-log.txt MANIFEST twistd.pid
