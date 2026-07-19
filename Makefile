all: run

clean:
	rm -rf .mypy_cache
	rm -rf __pycache__
	rm -rf mazegen/__pycache__

lint:
	python3 -m flake8 . && python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	python3 -m flake8 . && python3 -m mypy . --strict

run: config.txt a_maze_ing.py
	@python3 a_maze_ing.py config.txt

debug: config.txt a_maze_ing.py
	python3 -m pdb a_maze_ing.py config.txt

install:
	pip install flake8 mypy build

build:
	python3 -m build --outdir .

.PHONY: all clean lint lint-strict run debug install build