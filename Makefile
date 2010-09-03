PYLINTOPTIONS = -E
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
	cd $(VIRTUALENV); $(BIN)/trial pyhkal.test
# trial runs pyhkal/ directory otherwise

pylint: install
	$(VIRTUAL)pip install pylint
	cd $(VIRTUALENV); $(BIN)/pylint $(PYLINTOPTIONS) pyhkal

# line 2: pip on Windows installs twisted/ folder otherwise
virtualenv:
	python -mvirtualenv --distribute --no-site-packages "$(VIRTUALENV)"
	cd $(VIRTUALENV); $(BIN)/pip -q install Twisted
	$(VIRTUAL)pip -q install paisley
	$(VIRTUAL)pip -q install pyopenssl
	$(VIRTUAL)pip -q install oauth
	$(VIRTUAL)pip -q install twittytwister
	$(VIRTUAL)pip -q install PyYAML
$(VIRTUALENV):
	make virtualenv
install: $(VIRTUALENV) $(SOURCES)
	$(VIRTUAL)python setup.py --quiet sdist
	$(VIRTUAL)python setup.py --quiet install

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf build/ dist/
	rm -f pip-log.txt MANIFEST twistd.pid
