test: flake8 pylint pytest

flake8:
	flake8 basicrules test

pylint:
	pylint basicrules -E

pytest:
	coverage run --source basicrules --branch -m pytest test
	coverage report --show-missing --fail-under=100
