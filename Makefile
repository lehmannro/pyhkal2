VIRTUALENV = var
SOURCES = $(wildcard pyhkal/*.py) $(wildcard contrib/*.py) $(wildcard bin/*) \
		  setup.py

.PHONY: run test virtualenv clean

run: install
	@echo "Running PyHKAL.."
	$(VIRTUALENV)/bin/twistd -n $(T) pyhkal config.yaml

test: install
	cd "$(VIRTUALENV)"; . bin/activate; trial pyhkal.test

check: install
	/bin/bash -c "cd '$(VIRTUALENV)'; bin/python -m compileall lib/python*/site-packages/pyhkal/"

pylint: install; SH='/bin/bash'
	cd "${VIRTUALENV}";\
	for version in `echo lib/python*/site-packages/`; do cd "$${version}"; pylint -E pyhkal; done

virtualenv:
	python -mvirtualenv --distribute --no-site-packages "$(VIRTUALENV)"
	$(VIRTUALENV)/bin/pip -q install Twisted
	$(VIRTUALENV)/bin/pip -q install paisley
	$(VIRTUALENV)/bin/pip -q install pyopenssl
	$(VIRTUALENV)/bin/pip -q install oauth
	$(VIRTUALENV)/bin/pip -q install twittytwister
	$(VIRTUALENV)/bin/pip -q install PyYAML
$(VIRTUALENV):
	make virtualenv
install: $(VIRTUALENV) $(SOURCES)
	$(VIRTUALENV)/bin/python setup.py --quiet sdist
	$(VIRTUALENV)/bin/python setup.py --quiet install

clean:
	rm -rf "$(VIRTUALENV)"
	rm -rf build/ dist/
	rm -f pip-log.txt MANIFEST twistd.pid
