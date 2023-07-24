.PHONY: test coverage dist lint fmt

test:
	# TODO: figure out why -s option is required for fabric remote connection
	hatch run test -s -vv

coverage:
	hatch run cov -s -vv

lint:
	hatch run lint:all

fmt:
	hatch run lint:fmt

# dist:
# 	# todo move all this to script in pyproject.toml
# 	python3 -m pip install --upgrade build
# 	python3 -m build
# 	python3 -m pip install --upgrade twine
# 	echo "CHECK THIS VERSION NUMBER AND CHANGE IF NECESSARY!"
# 	cat ./src/pisync/__about__.py
# 	python3 -m twine upload dist/*

dist:
	hatch build
	hatch publish
