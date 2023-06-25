.PHONY: lint
# copied from the pipeline
lint:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# The GitHub editor is 127 chars wide
	flake8 . --count --max-complexity=10 --max-line-length=127 --statistics

.PHONY: freeze
freeze:
	pip list --format=freeze > requirements.txt