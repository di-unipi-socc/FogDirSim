ifndef PORT
	PORT := 8080
endif
ifndef PYTHON
	PYTHON := $(shell which python3.7 || which python3.6)
endif

.git/hooks/pre-commit: venv .pre-commit-config.yaml
	./venv/bin/pre-commit install -f --install-hooks

.PHONY: install-hooks
install-hooks: .git/hooks/pre-commit
	@true

venv: requirements-dev.txt setup.py
	virtualenv venv --python ${PYTHON}
	./venv/bin/pip install -e .
	./venv/bin/pip install -r requirements-dev.txt

venv-pypy: requirements-dev.txt setup.py tox.ini
	virtualenv venv-pypy --python pypy3
	./venv-pypy/bin/pip install -e .
	./venv-pypy/bin/pip install -r requirements-dev.txt

.PHONY: dev
dev: venv install-hooks
	@true

.PHONY: test tests
test tests:
	tox -e py36

.PHONY: clean
clean:
	@rm -rf .tox build dist docs/build *.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

.PHONY: start-simulator-api
start-simulator-api:
	@which uwsgi
	uwsgi --http :${PORT} --wsgi-file ${CURDIR}/uwsgi/simulator_api.wsgi --master --processes 4

.PHONY: start-fake-fog-director
start-fake-fog-director:
	@which uwsgi
	uwsgi --http :${PORT} --wsgi-file ${CURDIR}/uwsgi/fake_fog_director.wsgi --master --processes 4
