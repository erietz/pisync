.PHONY: lint
# copied from the pipeline
lint:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --per-file-ignores="__init__.py:F401"
	# The GitHub editor is 127 chars wide
	flake8 . --count --max-complexity=10 --max-line-length=127 --statistics --per-file-ignores="__init__.py:F401"

.PHONY: test
test:
	pytest -s -vv

.PHONY: freeze
freeze:
	pip list --format=freeze > requirements.txt


dist:
	python3 -m pip install --upgrade build
	python3 -m build
	python3 -m pip install --upgrade twine
	echo "CHECK THIS VERSION NUMBER AND CHANGE IF NECESSARY!"
	cat ./src/pisync/__about__.py
	python3 -m twine upload dist/*
