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

.PHONY: dev
dev: venv install-hooks
	@true

test tests:
	tox -e py36

clean:
	@rm -rf .tox build dist docs/build *.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
