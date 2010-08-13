VIRTUALENV = var
SOURCES = $(wildcard pyhkal/*.py) $(wildcard contrib/*.py) $(wildcard bin/*) \
		  setup.py pyhkal/service.tac

.PHONY: run test virtualenv yaml clean

run: install
	@echo "Running PyHKAL.."
	@cd "$(VIRTUALENV)"; \
	./bin/twistd -ny lib/python*/site-packages/pyhkal/service.tac; true

test: install
	cd "$(VIRTUALENV)"; ./bin/activate; trial pyhkal.test

check: install
	$(VIRTUALENV)/bin/python -m compile "$(VIRTUALENV)/lib/python*/site-packages/pyhkal/"

virtualenv:
	python -mvirtualenv --distribute --no-site-packages "$(VIRTUALENV)"
	$(VIRTUALENV)/bin/pip -q install Twisted
	$(VIRTUALENV)/bin/pip -q install paisley
yaml: virtualenv
	$(VIRTUALENV)/bin/pip -q install PyYAML
$(VIRTUALENV):
	make virtualenv
install: $(VIRTUALENV) $(SOURCES)
	$(VIRTUALENV)/bin/python setup.py --quiet install

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf "build/"
	rm -f pip-log.txt
