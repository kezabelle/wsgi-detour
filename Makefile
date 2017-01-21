help:
	@echo "clean-build - get rid of build artifacts & metadata"
	@echo "clean-pyc - get rid of dross files"
	@echo "test - execute tests; calls clean-pyc for you"
	@echo "dist - build a distribution; calls test, clean-build and clean-pyc"
	@echo "check - check the quality of the built distribution; calls dist for you"

clean-build:
	rm -fr build/
	rm -fr htmlcov/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +


clean-pyc:
	find . -name '*.so' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

test: clean-pyc
	python -B -R -tt -W ignore setup.py test

dist: test clean-build clean-pyc
	python setup.py sdist bdist_wheel

check: dist
	pip install check-manifest pyroma restview
	check-manifest
	pyroma .
	restview --long-description
