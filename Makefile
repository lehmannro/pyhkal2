VIRTUALENV = var
SOURCES = $(wildcard pyhkal/*.py) $(wildcard contrib/*.py) $(wildcard bin/*) \
		  setup.py
ifdef WIN32
	VIRTUAL = $(VIRTUALENV)/Scripts/activate.bat;
else
	VIRTUAL = . $(VIRTUALENV)/bin/activate;
endif

.PHONY: run test virtualenv clean

run: install
	@echo "Running PyHKAL.."
	$(VIRTUAL) twistd -n $(T) pyhkal config.yaml

test: install
	$(VIRTUAL) cd $(VIRTUALENV); trial pyhkal.test

check: install
	/bin/bash -c "cd '$(VIRTUALENV)'; bin/python -m compileall lib/python*/site-packages/pyhkal/"

pylint: install; SH='/bin/bash'
	cd "${VIRTUALENV}";\
	for version in `echo lib/python*/site-packages/`; do cd "$${version}"; pylint -E pyhkal; done

virtualenv:
	python -mvirtualenv --distribute --no-site-packages "$(VIRTUALENV)"
	$(VIRTUAL) pip -q install Twisted
	$(VIRTUAL) pip -q install paisley
	$(VIRTUAL) pip -q install pyopenssl
	$(VIRTUAL) pip -q install oauth
	$(VIRTUAL) pip -q install twittytwister
	$(VIRTUAL) pip -q install PyYAML
$(VIRTUALENV):
	make virtualenv
install: $(VIRTUALENV) $(SOURCES)
	$(VIRTUAL) python setup.py --quiet sdist
	$(VIRTUAL) python setup.py --quiet install

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf build/ dist/
	rm -f pip-log.txt MANIFEST twistd.pid
