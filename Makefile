ifndef PORT
	PORT := 8080
endif

.git/hooks/pre-commit: venv .pre-commit-config.yaml
	./venv/bin/pre-commit install -f --install-hooks

.PHONY: install-hooks
install-hooks: .git/hooks/pre-commit
	@true

venv: requirements-dev.txt setup.py tox.ini
	@rm -rf venv
	tox -e venv

venv-pypy: requirements-dev.txt setup.py tox.ini
	@rm -rf venv-pypy
	tox -e venv-pypy

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
